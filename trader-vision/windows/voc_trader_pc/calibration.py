from __future__ import annotations
import tkinter as tk
from tkinter import ttk,messagebox
from PIL import Image,ImageTk
import mss
import numpy as np
import cv2

FIELDS=[
 ('chart','1/10: selecione SOMENTE a área das velas (sem botões, horários ou banner).'),
 ('account','2/10: selecione o rótulo Conta Demo no canto superior.'),
 ('balance','3/10: selecione apenas o saldo € mostrado na conta Demo.'),
 ('address','4/10: selecione a barra de endereço com app.hezilex.com/traderoom.'),
 ('asset','5/10: selecione o ATIVO na aba selecionada (ex.: BNB no topo; NÃO a lista lateral).'),
 ('stake','6/10: selecione o número do valor (ex.: 1,00).'),
 ('expiry','7/10: selecione a expiração (ex.: 5 min).'),
 ('countdown','8/10: selecione o contador VERDE ao lado do PREÇO no gráfico (NÃO o da Expiração no topo).'),
 ('buy','9/10: selecione toda a área VERDE do botão Comprar.'),
 ('sell','10/10: selecione toda a área VERMELHA do botão Vender.')
]

class CalibrationWindow:
    def __init__(self,parent,settings,on_save,on_close=None):
        self.parent=parent;self.settings=settings;self.on_save=on_save;self.on_close=on_close
        self.selected={};self.step=0;self.start=None;self.rect=None
        parent.withdraw()
        parent.after(350,self._capture)

    def _capture(self):
        with mss.mss() as s:
            index=1
            monitor=s.monitors[index]
            raw=np.asarray(s.grab(monitor))
        self.bgr=cv2.cvtColor(raw,cv2.COLOR_BGRA2BGR)
        arr=cv2.cvtColor(raw,cv2.COLOR_BGRA2RGB)
        self.full=Image.fromarray(arr)
        w,h=self.full.size
        screen_w=self.parent.winfo_screenwidth();screen_h=self.parent.winfo_screenheight()
        self.scale=min(1.0,(screen_w-80)/w,(screen_h-155)/h)
        pw=max(1,int(w*self.scale));ph=max(1,int(h*self.scale))
        self.preview=self.full.resize((pw,ph),Image.Resampling.LANCZOS)
        self.win=tk.Toplevel(self.parent)
        self.win.title('VOC Trader Vision PC — Calibração Visual DEMO')
        self.win.geometry(f'{min(screen_w,pw+28)}x{min(screen_h,ph+120)}+0+0')
        self.win.configure(bg='#0d1728')
        self.win.protocol('WM_DELETE_WINDOW',self._close)
        self.title=tk.Label(self.win,text=FIELDS[0][1],bg='#0d1728',fg='#8bfbd8',font=('Segoe UI',12,'bold'))
        self.title.pack(pady=(8,4))
        self.photo=ImageTk.PhotoImage(self.preview)
        self.canvas=tk.Canvas(self.win,width=pw,height=ph,highlightthickness=0,cursor='crosshair',bg='#050a14')
        self.canvas.pack()
        self.canvas.create_image(0,0,image=self.photo,anchor='nw')
        self.canvas.bind('<ButtonPress-1>',self.down)
        self.canvas.bind('<B1-Motion>',self.drag)
        self.canvas.bind('<ButtonRelease-1>',self.up)
        line=tk.Frame(self.win,bg='#0d1728');line.pack(fill='x',pady=5)
        tk.Button(line,text='RECOMEÇAR',command=self.reset,bg='#40536d',fg='white').pack(side='left',padx=8)
        tk.Button(line,text='MODELO PC 1366×768',command=self.apply_desktop_reference,
                  bg='#157b79',fg='white').pack(side='left',padx=8)
        tk.Button(line,text='CANCELAR',command=self._close,bg='#923f45',fg='white').pack(side='right',padx=8)
        self.win.lift();self.win.focus_force()
    def apply_desktop_reference(self):
        """Show all ten suggested regions and require explicit user approval.

        Never silently save coordinates from a picture or trust a layout that
        does not have green/red buttons in the expected positions.
        """
        from .desktop_layout import reference_for_dimensions,preset_matches_frame
        valid,reason=preset_matches_frame(self.bgr)
        if not valid:
            messagebox.showwarning('Modelo não corresponde',
                reason+'\\nUse os 10 retângulos da calibração manual.',parent=self.win)
            return
        calibration=reference_for_dimensions(*self.full.size)
        self.canvas.delete('preset')
        for i,(name,_) in enumerate(FIELDS,1):
            rect=calibration['rois'][name]
            x0,y0,x1,y1=[int(v*self.scale) for v in rect]
            self.canvas.create_rectangle(x0,y0,x1,y1,outline='#3cf0d8',
                                         width=2,tags='preset')
            self.canvas.create_text(x0+3,max(10,y0-9),anchor='w',
                                    text=f'{i}: {name}',fill='#f6eaa2',
                                    font=('Segoe UI',9,'bold'),tags='preset')
        self.canvas.update_idletasks()
        approved=messagebox.askyesno('Confira as 10 regiões',
            'Verifique VISUALMENTE os retângulos sobre a Hezilex.\\n\\n'
            '1 Gráfico  2 Conta Demo  3 Saldo  4 Endereço  5 Aba BNB\\n'
            '6 Valor  7 Expiração  8 Relógio verde do preço\\n'
            '9 Comprar  10 Vender\\n\\n'
            'Todos estão nas posições corretas?\\n'
            'Se mudou zoom, janela, ativo ou layout, responda NÃO e calibre manualmente.\\n'
            'A aprovação não arma cliques nem contorna risco de 1%.',
            parent=self.win)
        if not approved:
            self.canvas.delete('preset')
            return
        self.settings.calibration=calibration
        self.on_save(self.settings)
        self._close()
        messagebox.showinfo('Referência aplicada',
            'Regiões aprovadas e salvas.\\n'
            'Abra OBSERVAR, configure o ativo BNB se continuar nesta aba e '
            'verifique o risco/quantidade de velas ANTES de armar DEMO.',
            parent=self.parent)

    def down(self,e):
        self.start=(e.x,e.y)
        if self.rect is not None:self.canvas.delete(self.rect)
        self.rect=self.canvas.create_rectangle(e.x,e.y,e.x,e.y,outline='#39f8ce',width=2)
    def drag(self,e):
        if self.start:self.canvas.coords(self.rect,self.start[0],self.start[1],e.x,e.y)
    def up(self,e):
        if not self.start:return
        x0,y0=self.start;x1,y1=e.x,e.y
        self.start=None
        if abs(x1-x0)<12 or abs(y1-y0)<8:
            messagebox.showwarning('Região pequena','Arraste e selecione um retângulo completo.',parent=self.win);return
        coords=[round(v/self.scale) for v in (min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1))]
        name=FIELDS[self.step][0]
        self.selected[name]=coords
        self.step+=1
        if self.step==len(FIELDS):
            self.settings.calibration={'monitor':1,'dimensions':[self.full.width,self.full.height],'rois':self.selected}
            self.on_save(self.settings)
            self._close()
            messagebox.showinfo('Calibração salva','10 regiões salvas. Inicie em modo OBSERVAÇÃO e confira todas as leituras antes de armar DEMO.',parent=self.parent)
        else:
            self.title.configure(text=FIELDS[self.step][1]);self.rect=None
    def reset(self):
        self.step=0;self.selected={};self.title.configure(text=FIELDS[0][1]);self.canvas.delete('all');self.canvas.create_image(0,0,image=self.photo,anchor='nw')
    def _close(self):
        if hasattr(self,'win'):
            self.win.destroy()
        self.parent.deiconify();self.parent.lift()
        if self.on_close:self.on_close()
