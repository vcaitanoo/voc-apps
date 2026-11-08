from __future__ import annotations
import json,time,queue,threading,traceback,re,os
from dataclasses import asdict
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
from .monitor_overlay import MonitorOverlay
from .monitor_journal import MonitorJournal

BG='#0a1220'; PANEL='#111f34'; TEXT='#f0f6ff'; MUTED='#a3bad1'; ACCENT='#50e8bd'; GOLD='#e5ad60'

class TraderApp:
    def __init__(self,root):
        self.root=root;self.root.title('VOC Trader Vision PC · Análise Adaptativa DEMO v0.1.6')
        screen_width=max(940,self.root.winfo_screenwidth())
        screen_height=max(610,self.root.winfo_screenheight())
        self.root.geometry(f'{min(1180,screen_width-30)}x{min(765,screen_height-85)}')
        self.root.minsize(910,540);self.root.configure(bg=BG)
        self.settings=load_settings();self.journal=Journal(JOURNAL_FILE);self.tracker=DemoTracker(self.journal)
        self.events=queue.Queue();self.stop_event=threading.Event();self.demo_event=threading.Event();self.thread=None;self.last_click_key=None
        self.csv_data={};self.log_lines=[]
        self.last_monitor_action='Nenhuma'
        self._build()
        self.monitor_log=MonitorJournal()
        self.overlay=MonitorOverlay(self.root,self.stop,self.open_report)
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
            side='left',expand=True,fill='x',padx=(4,3))
        self._button(fixed_actions,'◉ PAINEL',self.open_overlay,'#245a70').pack(
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
        if self.thread and self.thread.is_alive():
            messagebox.showwarning('Interrompa','Pare a observação antes de calibrar.',parent=self.root)
            return
        was_visible=self.overlay.visible
        if was_visible:self.overlay.hide_for_capture()
        def restore():
            if was_visible:self.overlay.restore_after_capture()
        try:
            from .calibration import CalibrationWindow
            CalibrationWindow(self.root,self.settings,lambda s:save_settings(s),
                              on_close=restore)
        except Exception as e:
            self.root.deiconify()
            restore()
            messagebox.showerror('Calibração',f'Não consegui capturar o monitor: {e}',parent=self.root)
    def pick_csv(self):
        p=filedialog.askdirectory(title='Selecione uma pasta com EURUSD_H4.csv, EURUSD_H1.csv, ...')
        if not p:return
        try:
            self.csv_data=feeds.load_csv_directory(Path(p),self.vars['symbol'].get().strip().upper())
            self._log('CSV: '+', '.join(f'{tf}={len(a)} velas' for tf,a in self.csv_data.items()))
        except Exception as e:messagebox.showerror('CSV inválido',str(e),parent=self.root)
    def open_overlay(self):
        self.overlay.show(force=True)
    def open_report(self):
        try:
            if hasattr(os,'startfile'):
                os.startfile(str(self.monitor_log.path))
            else:
                self._log('Relatório: '+str(self.monitor_log.path))
        except OSError as exc:
            self._log('Não foi possível abrir relatório: '+str(exc))
    def start(self):
        if self.thread and self.thread.is_alive():
            self.open_overlay()
            return
        try:self.save();s=self.settings
        except Exception:return
        if s.source=='SCREEN' and not s.calibration:
            messagebox.showwarning('Calibração necessária','Capture as 10 regiões na tela do PC antes de iniciar.',parent=self.root);return
        self.stop_event.clear();self.status.set('CAPTURANDO DADOS · '+s.source)
        self.summary.set('Monitoramento iniciado. Volte para o Chrome e mantenha a Hezilex visível.')
        self.overlay.update_state('AGUARDANDO CHROME',[
            'Dados: aguardando primeira leitura',
            'Ativo configurado: '+s.symbol,
            'Mantenha o navegador Hezilex em primeiro plano',
            'Limite de risco preservado: 1%'],self.demo_event.is_set())
        self.overlay.show()
        self.thread=threading.Thread(target=self._loop,daemon=True);self.thread.start()
        self._log('Monitoramento iniciado. Cliques '+('armados' if self.demo_event.is_set() else 'desarmados')+'.')
    def stop(self):
        self.stop_event.set();self.demo_event.clear();self.demo.set(False)
        self.status.set('PARADO · SEM CLIQUES')
        self._log('Observação interrompida; execução DEMO desarmada.')
        if hasattr(self,'overlay'):
            self.overlay.update_state('PARADO',[
                'Bot desarmado e captura interrompida',
                'Relatório preservado em monitoramento_pc.csv'],False)
        if hasattr(self,'monitor_log'):
            self.monitor_log.append({
                'estado':'PARADO','cliques_armados':False,'ultima_acao':'PARAR',
                'bloqueio':'Operador interrompeu a observação'},force=True)
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
    def _protected_capture(self,callback):
        # The app overlay must be absent from bot OCR frames but remains visible
        # to screenshots the USER takes. Tk widgets only on the main thread.
        if not self.overlay.visible:return callback()
        ack=threading.Event()
        self.events.put(('capture_hide',ack))
        if not ack.wait(5.0):
            raise RuntimeError('Não foi possível ocultar o painel antes de ler o gráfico')
        try:return callback()
        finally:self.events.put(('capture_restore',))
    def _loop(self):
        from .screen import ScreenObserver,safe_click,foreground_is_browser
        s=self.settings
        obs=ScreenObserver(s.calibration,s.tesseract_path,int(s.timeframe[1:])) if s.source=='SCREEN' else None
        first_capture=True
        while not self.stop_event.is_set():
            try:
                if s.source=='SCREEN':
                    if first_capture:
                        self.events.put(('stage','Iniciando: volte para a aba Hezilex no Chrome...'))
                        first_capture=False
                    if not foreground_is_browser():
                        self.events.put(('stage','BLOQUEADO: Chrome/Edge/Brave precisa estar em primeiro plano; retorne à Hezilex'))
                        self.stop_event.wait(4)
                        continue
                    frame=self._protected_capture(obs.capture)
                    screen=obs.read(frame)
                    data={s.timeframe:screen.candles}
                    decision=engine.evaluate(s.symbol,data,self.journal,source='SCREEN',minimum_score=s.min_score,allow_limited_context=s.allow_single_tf_demo)
                    events=[f'Hezilex OCR: DEMO={screen.account_demo}, REAL={screen.account_real}, saldo={screen.balance}, valor={screen.stake}, expiração={screen.expiry}, vela={screen.clock_remaining}s',
                            f'Ativo OCR: {screen.asset_text} | Candles visíveis: {len(screen.candles)}; Bloqueios visuais: '+(', '.join(screen.blockers) or 'nenhum')]
                    errors=[]
                    configured=re.sub(r'[^A-Z0-9]','',s.symbol.upper())
                    detected=re.sub(r'[^A-Z0-9]','',screen.asset_text.upper())
                    if not configured or not detected.startswith(configured):
                        errors.append('ATIVO DIFERENTE: configurado '+s.symbol+
                                      ' / aba Hezilex '+(screen.asset_text or 'ilegível'))
                    closed=max(0,len(screen.candles)-1)
                    if closed<60:
                        errors.append(f'HISTÓRICO: {closed}/60 velas fechadas; afaste zoom para analisar')
                    if screen.blockers:
                        errors.append('LEITURA: '+screen.blockers[0])
                    if errors:events.extend('AJUSTE: '+err for err in errors)
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
                    elif errors:
                        events.append('BLOQUEADO POR LEITURA: '+errors[0])
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
                                    _,_,latest_balance=self._protected_capture(
                                        lambda:safe_click(obs,screen,s.calibration,
                                            decision.candidate.direction,verdict.stake,s.expiry_min,
                                            s.symbol,int(s.calibration.get('monitor',1)),
                                            should_cancel=lambda:(
                                                self.stop_event.is_set() or
                                                not self.demo_event.is_set())))
                                except Exception as exc:
                                    events.append(f'TOQUE RECUSADO: {type(exc).__name__}: {exc}')
                                else:
                                    self.last_click_key=key
                                    self.tracker.begin(s.symbol,decision.candidate.strategy,decision.candidate.regime,
                                                       decision.candidate.direction,latest_balance,verdict.stake,s.expiry_min)
                                    events.append('GESTO DEMO ENVIADO; aceitação da ordem NÃO VERIFICADA')
                    screenshot_data={
                        'account_demo':screen.account_demo,'account_real':screen.account_real,
                        'asset':screen.asset_text,
                        'bars':len(screen.candles),'clock':screen.clock_remaining,
                        'balance':screen.balance,'stake':screen.stake,'expiry':screen.expiry,
                        'browser':True,'blockers':screen.blockers,'risk':verdict.reason,
                        'risk_allowed':verdict.allowed,'issues':errors}
                    self.events.put(('decision',decision,events,screen.balance,
                                     screenshot_data))
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
                if e[0]=='capture_hide':
                    self.overlay.hide_for_capture()
                    e[1].set()
                elif e[0]=='capture_restore':
                    self.overlay.restore_after_capture()
                elif e[0]=='error':
                    self._log('ERRO: '+e[1])
                    self.status.set('ERRO DE LEITURA · SEM CLIQUES')
                    self.summary.set(e[1]+'\\nConfira OCR, calibração e visibilidade do navegador.')
                    self.overlay.update_state('ERRO DE LEITURA',[e[1]],False)
                    self.monitor_log.append({'estado':'ERRO DE LEITURA',
                        'bloqueio':e[1],'cliques_armados':self.demo_event.is_set()},force=True)
                elif e[0]=='stage':
                    self.status.set('VERIFICANDO NAVEGADOR · SCREEN')
                    self.summary.set(e[1])
                    self.overlay.update_state('AGUARDANDO HEZILEX',[e[1],
                        'Volte ao Chrome; esta janela não pode cobrir o gráfico'],
                        self.demo_event.is_set())
                    self.monitor_log.append({'estado':'AGUARDANDO HEZILEX',
                        'bloqueio':e[1],'browser_ativo':False,
                        'cliques_armados':self.demo_event.is_set()})
                else:
                    self._update(*e[1:])
        except queue.Empty:pass
        self.root.after(200,self.poll)
    def _update(self,d:Decision,extras:list[str],balance:float|None,
                diagnostic:dict|None=None):
        execution=next((e for e in extras if e.startswith((
                      'AJUSTE:', 'BLOQUEADO POR LEITURA:',
                      'BLOQUEADO POR RISCO:',
                      'Sem toque:', 'TOQUE RECUSADO:',
                      'AGUARDANDO RESULTADO', 'AGUARDANDO SETUP:',
                      'EXECUÇÃO DESARMADA:'))), '')
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
        info=diagnostic or {}
        lines=[
            'Tela/Conta: '+('DEMO OK' if info.get('account_demo') and not info.get('account_real') else 'NÃO CONFIRMADA'),
            'Ativo: '+str(info.get('asset','—'))+' | Config.: '+self.settings.symbol,
            'M5: '+str(max(0,int(info.get('bars') or 0)-1))+'/60 fechadas',
            'Vela: '+(str(info.get('clock'))+'s' if info.get('clock') is not None else 'OCR não confirmado'),
            'Saldo OCR: '+str(info.get('balance') if info.get('balance') is not None else '?')+
                 ' | Entrada OCR: '+str(info.get('stake') if info.get('stake') is not None else '?'),
            'Expiração OCR: '+str(info.get('expiry') if info.get('expiry') is not None else '?')+'min',
            'Sinal: '+(d.candidate.direction+' '+str(d.candidate.score)+'/100'
                       if d.candidate else 'AGUARDAR'),
            'Razão: '+(execution or d.explanation),
            'WIN/LOSS confirmados: '+str(self.journal.summary()['wins'])+
                '/'+str(self.journal.summary()['losses']),
            'Última ação: '+self.last_monitor_action]
        for item in extras:
            if item.startswith(('GESTO DEMO ENVIADO','TOQUE RECUSADO:','Resultado:')):
                self.last_monitor_action=item
        phase=('BLOQUEADO RISCO' if not info.get('risk_allowed',True) else
               'AJUSTAR TELA' if info.get('issues') else
               'AGUARDANDO SINAL' if d.status!='ELEGÍVEL' else d.status)
        self.overlay.update_state(phase,lines,self.demo_event.is_set())
        stats=self.journal.summary()
        self.monitor_log.append({
            'estado':phase,'fonte':d.source,'cliques_armados':self.demo_event.is_set(),
            'browser_ativo':info.get('browser',False),
            'conta_demo':info.get('account_demo',False),
            'ativo_configurado':self.settings.symbol,
            'ativo_lido':info.get('asset'), 'velas_fechadas':max(0,int(info.get('bars') or 0)-1),
            'segundos_relogio':info.get('clock'),
            'nota_tecnica':d.candidate.score if d.candidate else None,
            'sinal':d.candidate.direction if d.candidate else 'AGUARDAR',
            'estrategia':d.candidate.strategy if d.candidate else 'Nenhuma',
            'saldo_ocr':info.get('balance'), 'valor_ocr':info.get('stake'),
            'expiracao_ocr':info.get('expiry'),
            'bloqueio':execution or info.get('risk') or d.explanation,
            'ultima_acao':self.last_monitor_action,
            'wins_confirmados':stats['wins'],'losses_confirmados':stats['losses'],
            'operacoes_conciliadas':stats['total']})
    def close(self):
        self.stop_event.set();self.demo_event.clear();self.demo.set(False)
        if hasattr(self,'overlay'):self.overlay.close()
        self.root.destroy()


def launch():
    root=tk.Tk();TraderApp(root);root.mainloop()
