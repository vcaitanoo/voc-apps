from __future__ import annotations
import json,time,queue,threading,traceback
from dataclasses import asdict, replace
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from .models import Settings,Decision,Candle
from .storage import load_settings,save_settings,JOURNAL_FILE
from .journal import Journal
from . import engine,feeds
from .risk import stake_verdict
from .tracker import DemoTracker
from .overlay import FloatingOverlay, OverlayState
from .session_report import SessionReporter

BG='#0a1220'; PANEL='#111f34'; TEXT='#f0f6ff'; MUTED='#a3bad1'; ACCENT='#50e8bd'; GOLD='#e5ad60'

class TraderApp:
    def __init__(self,root):
        self.root=root;self.root.title('VOC Trader Vision PC · Análise Adaptativa DEMO v0.1.4')
        screen_width=max(940,self.root.winfo_screenwidth())
        screen_height=max(610,self.root.winfo_screenheight())
        self.root.geometry(f'{min(1180,screen_width-30)}x{min(765,screen_height-85)}')
        self.root.minsize(910,540);self.root.configure(bg=BG)
        self.settings=load_settings();self.journal=Journal(JOURNAL_FILE);self.tracker=DemoTracker(self.journal)
        self.events=queue.Queue();self.stop_event=threading.Event();self.demo_event=threading.Event();self.thread=None;self.last_click_key=None
        self.csv_data={};self.log_lines=[]
        self._overlay_last_action="Nenhuma"
        self._build()
        self.reporter=SessionReporter()
        self.overlay=FloatingOverlay(root,stop_callback=self.stop,
                                     report_callback=self.open_report)
        root.after(200,self.poll)
        root.protocol('WM_DELETE_WINDOW',self.close)
    def _label(self,parent,text,size=10,color=TEXT,bold=False):
        return tk.Label(parent,text=text,fg=color,bg=parent.cget('bg'),font=('Segoe UI',size,'bold' if bold else 'normal'),anchor='w')
    def _button(self,parent,text,cmd,color='#1e4d5f'):
        return tk.Button(parent,text=text,command=cmd,bg=color,fg='white',activebackground='#197d7a',
                         activeforeground='white',relief='flat',bd=0,font=('Segoe UI',10,'bold'),padx=12,pady=9)
    def _build(self):
        top=tk.Frame(self.root,bg='#10233b',height=78);top.pack(fill='x')
        self._label(top,'VOC TRADER VISION  ·  WINDOWS',16,ACCENT,True).pack(anchor='w',padx=20,pady=(10,1))
        self._label(top,'Hezilex: leitura da tela + cliques somente DEMO calibrados  |  MT5: dados H4/H1/M15/M5/M1, sem envio de ordens',9,MUTED).pack(anchor='w',padx=20)
        body=tk.Frame(self.root,bg=BG);body.pack(fill='both',expand=True,padx=12,pady=12)
        left=tk.Frame(body,bg=PANEL,width=330);left.pack(side='left',fill='y',padx=(0,10));left.pack_propagate(False)
        right=tk.Frame(body,bg=BG);right.pack(side='right',fill='both',expand=True)
        self._label(left,'CONTROLES',13,ACCENT,True).pack(anchor='w',padx=14,pady=(12,5))
        # Always visible even on 1366x768 laptop screens with taskbar.
        self.calibration_button=self._button(left,'1 · CALIBRAR TELA',
                                             self.calibrate,'#157b79')
        self.calibration_button.pack(fill='x',padx=12,pady=(0,6))
        fixed_actions=tk.Frame(left,bg=PANEL)
        fixed_actions.pack(fill='x',padx=12,pady=(0,6))
        self._button(fixed_actions,'▶ OBSERVAR',self.start,'#116c62').pack(
            side='left',expand=True,fill='x',padx=(0,4))
        self._button(fixed_actions,'■ PARAR',self.stop,'#9a3943').pack(
            side='left',expand=True,fill='x',padx=(4,4))
        self._button(fixed_actions,'◉ PAINEL',self.show_overlay,'#245a70').pack(
            side='left',expand=True,fill='x')
        self._label(left,'CONFIGURAÇÕES · role para ver todos os campos',
                    9,MUTED).pack(fill='x',padx=12,pady=(0,3))
        scroll_holder=tk.Frame(left,bg=PANEL)
        scroll_holder.pack(fill='both',expand=True,padx=(5,3),pady=(0,7))
        self.controls_canvas=tk.Canvas(scroll_holder,bg=PANEL,
                                       highlightthickness=0,borderwidth=0)
        scroll_bar=ttk.Scrollbar(scroll_holder,orient='vertical',
                                command=self.controls_canvas.yview)
        self.controls_canvas.configure(yscrollcommand=scroll_bar.set)
        scroll_bar.pack(side='right',fill='y')
        self.controls_canvas.pack(side='left',fill='both',expand=True)
        controls=tk.Frame(self.controls_canvas,bg=PANEL)
        controls_window=self.controls_canvas.create_window((0,0),
                                                             window=controls,anchor='nw')
        controls.bind('<Configure>',lambda event:
            self.controls_canvas.configure(scrollregion=self.controls_canvas.bbox('all')))
        self.controls_canvas.bind('<Configure>',lambda event:
            self.controls_canvas.itemconfigure(controls_window,width=event.width))
        def wheel(event):
            x=self.root.winfo_pointerx()-scroll_holder.winfo_rootx()
            y=self.root.winfo_pointery()-scroll_holder.winfo_rooty()
            if 0<=x<scroll_holder.winfo_width() and 0<=y<scroll_holder.winfo_height():
                if event.delta:self.controls_canvas.yview_scroll(
                    -1 if event.delta>0 else 1,'units')
        self.root.bind_all('<MouseWheel>',wheel,add='+')
        def row(name,value,key,width=13):
            f=tk.Frame(controls,bg=PANEL);f.pack(fill='x',padx=12,pady=4)
            self._label(f,name,10).pack(side='left',anchor='center')
            v=tk.StringVar(value=str(value));entry=tk.Entry(f,textvariable=v,width=width,bg='#253954',fg=TEXT,insertbackground=TEXT,relief='flat',justify='right')
            entry.pack(side='right',ipady=5);self.vars[key]=v
            return v
        self.vars={}
        f=tk.Frame(controls,bg=PANEL);f.pack(fill='x',padx=12,pady=5)
        self._label(f,'Fonte de dados',10).pack(side='left')
        self.source=tk.StringVar(value=self.settings.source)
        ttk.Combobox(f,textvariable=self.source,values=['SCREEN','MT5','CSV'],state='readonly',width=13).pack(side='right')
        row('Ativo',self.settings.symbol,'symbol');row('Timeframe visual',self.settings.timeframe,'tf')
        row('Nota mínima',self.settings.min_score,'score');row('Risco máximo (%)',self.settings.risk_pct,'risk')
        row('Saldo para análise (€)',self.settings.balance,'balance');row('Entrada mínima (€)',self.settings.min_stake,'minimum')
        row('Tesseract.exe (se necessário)',self.settings.tesseract_path,'tesseract',width=17)
        row('Expiração (min)',self.settings.expiry_min,'expiry');row('Meta diária (%)',self.settings.target_daily_pct,'target')
        row('Perda diária (%)',self.settings.max_daily_loss_pct,'loss');row('Máx. entradas/dia',self.settings.max_daily_entries,'max_entries')
        self.allow_limited=tk.BooleanVar(value=self.settings.allow_single_tf_demo)
        self.demo=tk.BooleanVar(value=False) # REARM ALWAYS OFF on launch, regardless of config.
        tk.Checkbutton(controls,text='Aceito análise visual M5 sem todos os timeframes',variable=self.allow_limited,
                       fg=GOLD,bg=PANEL,selectcolor='#253954',activebackground=PANEL,wraplength=290,justify='left').pack(anchor='w',padx=10,pady=5)
        tk.Checkbutton(controls,text='ARMAR CLIQUES (APENAS CONTA DEMO)',variable=self.demo,
                       fg='#ffb1b1',bg=PANEL,selectcolor='#253954',activebackground=PANEL,
                       command=self._armed,wraplength=290).pack(anchor='w',padx=10,pady=5)
        self._button(controls,'SALVAR CONFIGURAÇÃO',self.save).pack(fill='x',padx=12,pady=4)
        self._button(controls,'IMPORTAR PASTA CSV (5 TIMEFRAMES)',self.pick_csv,'#30547a').pack(fill='x',padx=12,pady=4)

        self._label(controls,'MT5: somente leitura; não envia ordens.',9,MUTED).pack(fill='x',padx=12,pady=(7,8))

        summary=tk.Frame(right,bg=PANEL);summary.pack(fill='x',pady=(0,10))
        self.status=tk.StringVar(value='PRONTO · SEM CLIQUES');self.summary=tk.StringVar(value='Nenhuma análise executada.')
        self._label(summary,'DECISÃO EM TEMPO REAL',12,ACCENT,True).pack(anchor='w',padx=14,pady=(12,1))
        tk.Label(summary,textvariable=self.status,font=('Segoe UI',15,'bold'),fg=GOLD,bg=PANEL,anchor='w').pack(fill='x',padx=14)
        tk.Label(summary,textvariable=self.summary,font=('Segoe UI',10),fg=TEXT,bg=PANEL,anchor='w',justify='left',wraplength=800).pack(fill='x',padx=14,pady=(0,12))
        notebook=ttk.Notebook(right);notebook.pack(fill='both',expand=True)
        self.pages={}
        for name in ['Contexto & indicadores','Estratégia & execução','Risco & resultados','Log / diagnóstico']:
            frame=tk.Frame(notebook,bg=PANEL)
            notebook.add(frame,text=name)
            t=tk.Text(frame,wrap='word',font=('Consolas',10),bg=PANEL,fg=TEXT,insertbackground=TEXT,
                      relief='flat',padx=15,pady=15)
            t.pack(fill='both',expand=True);t.configure(state='disabled');self.pages[name]=t
        self._render('Risco & resultados',self._risk_text())
        self._log('Pronto. Primeiro calibre os elementos da Hezilex no PC. OBSERVAÇÃO por padrão.')
    def _render(self,name,txt):
        widget=self.pages[name];widget.configure(state='normal');widget.delete('1.0','end');widget.insert('end',txt);widget.configure(state='disabled')
    def _log(self,msg):
        stamp=datetime.now().strftime('%H:%M:%S')
        self.log_lines.append(f'[{stamp}] {msg}')
        self.log_lines=self.log_lines[-150:]
        self._render('Log / diagnóstico','\n'.join(self.log_lines))
    def _read_settings(self):
        s=self.settings
        s.source=self.source.get().strip();s.symbol=self.vars['symbol'].get().strip().upper()
        s.mt5_symbol=s.symbol;s.timeframe=self.vars['tf'].get().strip().upper()
        s.tesseract_path=self.vars['tesseract'].get().strip().strip('\"')
        s.min_score=int(self.vars['score'].get());s.risk_pct=float(self.vars['risk'].get())
        s.balance=float(self.vars['balance'].get());s.min_stake=float(self.vars['minimum'].get())
        s.expiry_min=int(self.vars['expiry'].get());s.target_daily_pct=float(self.vars['target'].get())
        s.max_daily_loss_pct=float(self.vars['loss'].get());s.max_daily_entries=int(self.vars['max_entries'].get())
        s.allow_single_tf_demo=self.allow_limited.get()
        if s.risk_pct<=0 or s.risk_pct>1:raise ValueError('Risco máximo permitido: 1%')
        if s.timeframe not in ('M1','M5','M15'):raise ValueError('Timeframe visual: M1, M5 ou M15')
        if not 50<=s.min_score<=99:raise ValueError('Nota entre 50 e 99')
        if not 1<=s.expiry_min<=120:raise ValueError('Expiração entre 1 e 120 minutos')
        return s
    def save(self):
        try:save_settings(self._read_settings());self._log('Configurações salvas. Armamento permanece desativado após reiniciar o programa.')
        except Exception as e:messagebox.showerror('Configuração inválida',str(e),parent=self.root)
    def _armed(self):
        # VC0.1.1 BUG: marking the checkbox NEVER set demo_event.
        # The executor checked demo_event, so clicking was impossible.
        if not self.demo.get():
            self.demo_event.clear()
            self._log('Cliques DEMO DESARMADOS; análise pode continuar.')
            return
        try:
            self._read_settings()
        except Exception as exc:
            self.demo.set(False)
            self.demo_event.clear()
            messagebox.showerror('Configuração inválida',str(exc),parent=self.root)
            return
        if self.settings.source!='SCREEN':
            self.demo.set(False)
            self.demo_event.clear()
            messagebox.showwarning('Somente Hezilex DEMO',
                'Cliques são permitidos apenas na fonte SCREEN. MT5 e CSV são somente análise.',
                parent=self.root)
            return
        if not self.settings.calibration or not self.settings.calibration.get('rois'):
            self.demo.set(False)
            self.demo_event.clear()
            messagebox.showwarning('Calibração necessária',
                'Primeiro calibre as 10 regiões da Hezilex. Não é seguro clicar por posições estimadas.',
                parent=self.root)
            return
        if not messagebox.askyesno('Somente DEMO',
            'Autorizar cliques automáticos SOMENTE quando todas as verificações provarem CONTA DEMO, URL, valor, expiração, botão e risco ≤1%? Não altera campos sozinho.',
            parent=self.root):
            self.demo.set(False)
            self.demo_event.clear()
            return
        self.demo_event.set()
        self._log('Cliques DEMO ARMADOS: motor ativo; aguardando condições verificadas.')
        preliminary=stake_verdict(self.settings.balance,self.settings.risk_pct,self.settings.min_stake)
        if not preliminary.allowed:
            self._log('ATENÇÃO RISCO: '+preliminary.reason+
                      ' | saldo configurado apenas para estimativa; saldo OCR será verificado.')
        # Explicit arming starts observation as well; do not leave the checkbox
        # checked while the analysis thread is stopped.
        if not self.thread or not self.thread.is_alive():
            self.start()
        self.status.set('MONITORANDO DEMO · aguardando confirmação dos dados')
    def calibrate(self):
        if self.thread and self.thread.is_alive():messagebox.showwarning('Interrompa','Pare a observação antes de calibrar.',parent=self.root);return
        try:
            from .calibration import CalibrationWindow
            CalibrationWindow(self.root,self.settings,lambda s:save_settings(s))
        except Exception as e:
            self.root.deiconify();messagebox.showerror('Calibração',f'Não consegui capturar o monitor: {e}',parent=self.root)
    def pick_csv(self):
        p=filedialog.askdirectory(title='Selecione uma pasta com EURUSD_H4.csv, EURUSD_H1.csv, ...')
        if not p:return
        try:
            self.csv_data=feeds.load_csv_directory(Path(p),self.vars['symbol'].get().strip().upper())
            self._log('CSV: '+', '.join(f'{tf}={len(a)} velas' for tf,a in self.csv_data.items()))
        except Exception as e:messagebox.showerror('CSV inválido',str(e),parent=self.root)
    def show_overlay(self):
        if hasattr(self,'overlay'):
            self.overlay.show(force=True)
    def open_report(self):
        path=self.reporter.path
        try:
            import os
            if hasattr(os,'startfile'):
                os.startfile(str(path))
            else:
                self._log('RELATÓRIO CSV: '+str(path))
        except OSError as exc:
            messagebox.showwarning('Relatório',
                f'Arquivo: {path}\\nNão foi possível abrir: {exc}',parent=self.root)
    def start(self):
        if self.thread and self.thread.is_alive():
            self.show_overlay()
            return
        try:self.save();s=self.settings
        except Exception:return
        if s.source=='SCREEN' and not s.calibration:
            messagebox.showwarning('Calibração necessária','Capture as 10 regiões na tela do PC antes de iniciar.',parent=self.root);return
        self.stop_event.clear();self.status.set('CAPTURANDO DADOS · '+s.source)
        self.summary.set('Monitoramento iniciado. Lendo tela e campos calibrados; confira a aba Log / diagnóstico.')
        self.overlay.show()
        self.overlay.update(replace(self.overlay.state,phase='CAPTURANDO TELA',
            source=s.source,armed=self.demo_event.is_set(),
            reason='Aguardando primeira leitura do motor.',captured_at=None))
        self.thread=threading.Thread(target=self._loop,daemon=True);self.thread.start()
        self._log('Monitoramento iniciado. Cliques '+('armados' if self.demo_event.is_set() else 'desarmados')+'.')
    def stop(self):
        self.stop_event.set();self.demo_event.clear();self.demo.set(False)
        self.status.set('PARADO · SEM CLIQUES');self._log('Observação interrompida; execução DEMO desarmada.')
        if hasattr(self,'overlay'):
            snapshot=replace(self.overlay.state,phase='PARADO',armed=False,
                reason='Monitoramento interrompido. Nenhum novo toque autorizado.')
            self.overlay.update(snapshot)
            self.reporter.record(snapshot,force=True)
    def _risk_text(self, observed_balance=None):
        s=self.settings;summary=self.journal.summary()
        balance=observed_balance if observed_balance is not None else s.balance
        day_pnl,day_trades=self.journal.today_stats()
        verdict=stake_verdict(balance,s.risk_pct,s.min_stake,day_pnl=day_pnl,trades_today=day_trades,max_daily_loss_pct=s.max_daily_loss_pct,target_daily_pct=s.target_daily_pct,max_daily_entries=s.max_daily_entries)
        return ('GESTÃO DE RISCO — LIMITE ABSOLUTO 1%\n'+f'Saldo lido/configurado: €{balance:.2f}\n'+
                f'Limite por entrada: {s.risk_pct:.2f}% | Entrada mínima da Hezilex: €{s.min_stake:.2f}\n'+
                f'Valor sugerido: €{verdict.stake:.2f} | {"PERMITIDO" if verdict.allowed else "BLOQUEADO"}\n'+
                f'Motivo: {verdict.reason}\n\n'+
                f'Operações conciliadas: {summary["total"]} | WIN {summary["wins"]} | LOSS {summary["losses"]}\n'+
                f'Taxa de acerto: {summary["win_rate"] if summary["win_rate"] is not None else "SEM AMOSTRA"}\n'+
                f'Lucro bruto: €{summary["gross"]:.2f} | Perdas brutas: €{summary["losses_gross"]:.2f}\n'+
                f'Lucro líquido: €{summary["net"]:.2f} | Drawdown por PnL realizado: €{summary["drawdown_eur"]:.2f}\n'+
                f'Fator de lucro: {summary["profit_factor"] if summary["profit_factor"] is not None else "SEM DADOS"}\n\n'+
                'HEZILEX: expiração fixa, sem trailing/SL por pip.\n'+
                'MT5: apenas leitura; trailing original não implementado sem seu código confirmado.\n')
    def _capture_without_panel(self,fn):
        """Overlay must never be mistaken for chart candles or broker controls."""
        panel=self.overlay
        if not panel.visible or panel.capture_excluded:
            return fn()
        ready=threading.Event()
        self.events.put(('overlay_capture_hide',ready))
        if not ready.wait(5):
            raise RuntimeError('Painel não pôde ser ocultado para captura segura')
        try:
            return fn()
        finally:
            self.events.put(('overlay_capture_restore',))
    def _loop(self):
        from .screen import ScreenObserver,safe_click
        s=self.settings
        obs=ScreenObserver(s.calibration,s.tesseract_path,int(s.timeframe[1:])) if s.source=='SCREEN' else None
        first_capture=True
        while not self.stop_event.is_set():
            try:
                if s.source=='SCREEN':
                    if first_capture:
                        self.events.put(('stage','Capturando monitor calibrado e lendo OCR...'))
                        first_capture=False
                    frame=self._capture_without_panel(obs.capture);screen=obs.read(frame)
                    data={s.timeframe:screen.candles}
                    decision=engine.evaluate(s.symbol,data,self.journal,source='SCREEN',minimum_score=s.min_score,allow_limited_context=s.allow_single_tf_demo)
                    events=[f'Hezilex OCR: DEMO={screen.account_demo}, REAL={screen.account_real}, saldo={screen.balance}, valor={screen.stake}, expiração={screen.expiry}, vela={screen.clock_remaining}s',
                            f'Ativo OCR: {screen.asset_text} | Candles visíveis: {len(screen.candles)}; Bloqueios visuais: '+(', '.join(screen.blockers) or 'nenhum')]
                    status=self.tracker.observe(screen.balance)
                    if status and status not in ('AGUARDANDO_EXPIRACAO','OCR_SALDO_INDISPONIVEL'):
                        events.append('Resultado: '+status)
                    day_pnl,day_entries=self.journal.today_stats()
                    verdict=stake_verdict(screen.balance if screen.balance is not None else 0,
                                          s.risk_pct,s.min_stake,day_pnl=day_pnl,
                                          trades_today=day_entries,max_daily_loss_pct=s.max_daily_loss_pct,
                                          target_daily_pct=s.target_daily_pct,max_daily_entries=s.max_daily_entries)
                    # Always show the decisive blocker; VC0.1.1 showed no
                    # explanation unless an eligible signal had already appeared.
                    if not self.demo_event.is_set():
                        events.append('EXECUÇÃO DESARMADA: marcar ARMAR CLIQUES para permitir tentativas DEMO.')
                    elif not verdict.allowed:
                        events.append('BLOQUEADO POR RISCO: '+verdict.reason)
                    elif self.tracker.pending is not None:
                        events.append('AGUARDANDO RESULTADO da operação DEMO anterior.')
                    elif decision.status!='ELEGÍVEL':
                        events.append('AGUARDANDO SETUP: '+decision.explanation)
                    else:
                        clk=screen.clock_remaining
                        total=int(s.timeframe[1:])*60
                        started=clk is not None and total-15<=clk<=total-1
                        # Every screen guard is rechecked on the SAME freshly captured frame.
                        if not started:events.append(f'Sem toque: aguardando nova vela pelo relógio Hezilex ({clk}s)')
                        elif screen.blockers:events.append('Sem toque: '+', '.join(screen.blockers))
                        elif screen.stake is None or abs(screen.stake-verdict.stake)>.005:
                            events.append(f'Sem toque: valor visível não corresponde ao risco €{verdict.stake:.2f}')
                        elif screen.expiry!=s.expiry_min:events.append('Sem toque: expiração visível divergente')
                        else:
                            key=(s.symbol,int(time.time()//(total or 300)))
                            if key!=self.last_click_key:
                                try:
                                    _,_,latest_balance=self._capture_without_panel(
                                        lambda:safe_click(obs,screen,s.calibration,
                                            decision.candidate.direction,verdict.stake,s.expiry_min,
                                            s.symbol,int(s.calibration.get('monitor',1)),
                                            should_cancel=lambda:
                                                self.stop_event.is_set() or not self.demo_event.is_set()))
                                except Exception as exc:
                                    events.append(f'TOQUE RECUSADO: {type(exc).__name__}: {exc}')
                                else:
                                    self.last_click_key=key
                                    self.tracker.begin(s.symbol,decision.candidate.strategy,decision.candidate.regime,
                                                       decision.candidate.direction,latest_balance,verdict.stake,s.expiry_min)
                                    events.append('GESTO DEMO ENVIADO; aceitação da ordem NÃO VERIFICADA')
                    telemetry={
                        'demo':screen.account_demo and not screen.account_real,
                        'ocr_ok':not any('TESSERACT' in b.upper() or 'OCR ' in b.upper()
                            or 'ilegível' in b.lower() for b in screen.blockers),
                        'candles':len(screen.candles),'clock':screen.clock_remaining,
                        'stake':screen.stake,'expiry':screen.expiry,
                        'balance':screen.balance, 'blockers':list(screen.blockers)}
                    self.events.put(('decision',decision,events,screen.balance,telemetry))
                elif s.source=='MT5':
                    data=feeds.load_mt5(s.mt5_symbol)
                    decision=engine.evaluate(s.mt5_symbol,data,self.journal,source='MT5',minimum_score=s.min_score)
                    self.events.put(('decision',decision,['MT5: dados de velas FECHADAS. Nenhum clique ou ordem MT5.'],s.balance))
                else:
                    decision=engine.evaluate(s.symbol,self.csv_data,self.journal,source='CSV',minimum_score=s.min_score)
                    self.events.put(('decision',decision,['CSV: análise estática, sem envio de ordens.'],s.balance))
            except Exception as e:
                self.events.put(('error',f'{type(e).__name__}: {e}'))
            self.stop_event.wait(4 if s.source=='SCREEN' else 12)
    def poll(self):
        try:
            for _ in range(12):
                e=self.events.get_nowait()
                if e[0]=='overlay_capture_hide':
                    self.overlay.hide_for_capture()
                    e[1].set()
                elif e[0]=='overlay_capture_restore':
                    self.overlay.show_after_capture()
                elif e[0]=='error':
                    self._log('ERRO: '+e[1])
                    self.status.set('ERRO DE LEITURA · SEM CLIQUES')
                    self.summary.set(e[1]+'\nConfira OCR, calibração e visibilidade do navegador.')
                    self._overlay_last_action='ERRO: '+e[1]
                    snap=replace(self.overlay.state,phase='ERRO DE LEITURA',
                        armed=self.demo_event.is_set(),reason=e[1],
                        last_action=self._overlay_last_action)
                    self.overlay.update(snap)
                    self.reporter.record(snap,force=True)
                elif e[0]=='stage':
                    self.status.set('LENDO TELA · SCREEN')
                    self.summary.set(e[1])
                else:
                    self._update(*e[1:])
        except queue.Empty:pass
        self.root.after(200,self.poll)
    def _update(self,d:Decision,extras:list[str],balance:float|None,
                telemetry:dict|None=None):
        execution=next((e for e in extras if e.startswith(('BLOQUEADO POR RISCO:',
                      'EXECUÇÃO DESARMADA:', 'AGUARDANDO SETUP:',
                      'AGUARDANDO RESULTADO', 'Sem toque:', 'TOQUE RECUSADO:'))), '')
        if d.source=='SCREEN' and self.demo_event.is_set() and execution.startswith('BLOQUEADO'):
            self.status.set('DEMO ARMADA · BLOQUEIO DE RISCO')
        elif d.source=='SCREEN':
            self.status.set(d.status+' · '+d.symbol+
                            (' · DEMO ARMADA' if self.demo_event.is_set() else ' · CLIQUES OFF'))
        else:
            self.status.set(d.status+' · '+d.symbol+' · SOMENTE ANÁLISE')
        self.summary.set(d.explanation+('\n'+execution if execution else ''))
        ctx=[]
        for tf in ('H4','H1','M15','M5','M1'):
            c=d.contexts.get(tf)
            if c:
                ctx.append(f'[{tf}] {c.regime}\n  Tendência {c.direction:+d} | Estrutura {c.structure} | Candles {c.n}\n'+
                           f'  EMA9 {c.ema9:.5f} | EMA21 {c.ema21:.5f} | EMA50 {c.ema50:.5f} | EMA200 {c.ema200:.5f}\n'+
                           f'  ADX {c.adx:.1f} | RSI {c.rsi:.1f} | ATR {c.atr:.5f} | Bollinger/ATR {c.bb_width:.2f}\n'+
                           f'  {"; ".join(c.factors)}\n')
            else:ctx.append(f'[{tf}] FONTE INDISPONÍVEL\n')
        self._render('Contexto & indicadores','\n'.join(ctx)+'\nFaltam: '+(', '.join(d.missing_timeframes) or 'nenhum')+
                     '\n\nEm SCREEN, OHLC é estimado por PIXELS de um único gráfico; nunca é preço real de MT5.')
        p=d.candidate
        summary=('Estado: '+d.status+'\nDecisão: '+d.explanation+'\nFonte: '+d.source+'\n\n')
        if p:
            summary+=(f'Estratégia: {p.strategy}\nDireção: {p.direction}\nRegime: {p.regime}\nNota técnica: {p.score}/100 (NÃO é probabilidade de WIN)\n'+
                      f'Confirmação vela fechada: {"SIM" if p.confirmed else "NÃO"}\n'+
                      f'Gatilho: {p.trigger:.6f} | Invalidação: {p.invalidation:.6f}\n'+
                      f'Histórico comparável: {p.sample_size} operações | Expectativa: {p.expectancy if p.expectancy is not None else "INDETERMINADA"}\n'+
                      'Fatores a favor: '+('; '.join(p.reasons) or 'nenhum')+'\n'+
                      'Fatores contrários: '+('; '.join(p.objections) or 'nenhum')+'\n')
        summary+='\n'+'\n'.join(extras)
        self._render('Estratégia & execução',summary)
        self._render('Risco & resultados',self._risk_text(balance))
        telemetry=telemetry or {}
        blocker=next((e for e in extras if e.startswith((
            'BLOQUEADO POR RISCO:', 'TOQUE RECUSADO:', 'Sem toque:',
            'AGUARDANDO RESULTADO', 'AGUARDANDO SETUP:',
            'EXECUÇÃO DESARMADA:'))),'')
        for event in extras:
            if event.startswith(('GESTO DEMO ENVIADO', 'TOQUE RECUSADO:',
                                 'Resultado:','ERRO:')):
                self._overlay_last_action=event
        summary=self.journal.summary()
        armed=self.demo_event.is_set()
        phase='BLOQUEADO' if blocker.startswith(('BLOQUEADO','TOQUE RECUSADO')) else (
              'AGUARDANDO RESULTADO' if self.tracker.pending is not None else (
              'OBSERVANDO' if not armed and d.source=='SCREEN' else d.status))
        p=d.candidate
        model=OverlayState(
            phase=phase,source=d.source,armed=armed,
            demo=telemetry.get('demo'),ocr_ok=telemetry.get('ocr_ok'),
            symbol=d.symbol,timeframe=self.settings.timeframe,
            candles=telemetry.get('candles'),clock=telemetry.get('clock'),
            strategy=p.strategy if p else 'Nenhuma',
            direction=p.direction if p else 'AGUARDAR',
            score=p.score if p else None,
            reason=blocker or d.explanation,
            last_action=self._overlay_last_action,
            balance=telemetry.get('balance',balance),
            stake=telemetry.get('stake'),expiry=telemetry.get('expiry'),
            wins=summary['wins'],losses=summary['losses'],
            settled=summary['total'],pending=self.tracker.pending is not None,
            captured_at=time.time())
        self.overlay.update(model)
        self.reporter.record(model)
    def close(self):
        self.stop_event.set();self.demo_event.clear();self.demo.set(False)
        if hasattr(self,'overlay'):self.overlay.destroy()
        self.root.destroy()


def launch():
    root=tk.Tk();TraderApp(root);root.mainloop()
