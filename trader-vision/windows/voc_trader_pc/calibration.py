from __future__ import annotations
import tkinter as tk
from tkinter import ttk,messagebox
from PIL import Image,ImageTk
import mss
import numpy as np
import cv2

FIELDS=[
 ('chart','1/10: selecione TODAS as velas até a faixa de preços (não cortar topos, sem botões).'),
 ('account','2/10: selecione o rótulo Conta Demo no canto superior.'),
 ('balance','3/10: selecione apenas o saldo € mostrado na conta Demo.'),
 ('address','4/10: selecione a barra de endereço com app.hezilex.com/traderoom.'),
 ('asset','5/10: selecione o ATIVO da aba ativa (ex.: BNB); NÃO a lista de ativos da direita.'),
 ('stake','6/10: selecione o número do valor (ex.: 1,00).'),
 ('expiry','7/10: selecione a expiração (ex.: 5 min).'),
 ('countdown','8/10: marque uma FAIXA VERTICAL ao lado do preço. A etiqueta 03:15 se move com a cotação; NÃO use o relógio da Expiração.'),
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
        tk.Button(line,text='RECOMEÇAR',command=self.reset,
                  bg='#40536d',fg='white').pack(side='left',padx=8)
        tk.Button(line,text='MODELO PC 1366×768',command=self.apply_reference,
                  bg='#157b79',fg='white').pack(side='left',padx=8)
        tk.Button(line,text='CANCELAR',command=self._close,bg='#923f45',fg='white').pack(side='right',padx=8)
        self.win.lift();self.win.focus_force()
    def apply_reference(self):
        from .pc_reference import recommended
        suggestion,reason=recommended(self.bgr)
        if suggestion is None:
            messagebox.showwarning('Modelo não compatível',
                reason+'\\nCalibre as dez regiões manualmente.',parent=self.win)
            return
        self.canvas.delete('reference')
        for index,(name,_) in enumerate(FIELDS,1):
            x0,y0,x1,y1=suggestion['rois'][name]
            x0,y0,x1,y1=[round(n*self.scale) for n in (x0,y0,x1,y1)]
            self.canvas.create_rectangle(x0,y0,x1,y1,
                outline='#37f9db',width=2,tags='reference')
            self.canvas.create_text(x0+3,max(9,y0-9),text=f'{index}:{name}',
                fill='#fff49a',anchor='w',tags='reference')
        accepted=messagebox.askyesno('Confira os 10 retângulos',
            'O MODELO é apenas uma proposta. Confira TODAS as áreas.\\n'
            'A região 8 deve ser uma FAIXA VERTICAL para localizar a etiqueta móvel do preço.\\n'
            'O ativo deve estar na ABA SELECIONADA, não na lista lateral.\\n'
            'Se alguma posição estiver errada, clique NÃO e selecione manualmente.\\n'
            'O modelo não autoriza cliques nem modifica os limites de risco.\\n\\n'
            'Todas as posições estão corretas?',
            parent=self.win)
        if not accepted:
            self.canvas.delete('reference')
            return
        self.settings.calibration=suggestion
        self.on_save(self.settings)
        self._close()
        messagebox.showinfo('Calibração concluída',
            'Regiões conferidas e salvas. Clique OBSERVAR, volte para o Chrome '
            'e confira se o painel lê ativo, velas, saldo e relógio.',
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
