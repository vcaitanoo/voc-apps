"""VOC PC overlay rebuilt on the last user-observed 0.1.3 source.

The floating window uses a real read-only status from ScreenObserver, the
trading decision and the DEMO journal. It cannot arm a session. It is hidden
only briefly for the bot's screenshot, so ordinary Windows screenshots can
still show the overlay for debugging. Keep browser focus on Chrome.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import tkinter as tk

from .storage import APP_DIR

BG="#102033"
HEADER="#153e51"
TEXT="#e3edf4"
TEAL="#67f0c4"
WARN="#ffcf83"
BAD="#ff9b9b"


class MonitorOverlay:
    def __init__(self,root,stop_callback,report_callback):
        self.root=root
        self.stop_callback=stop_callback
        self.report_callback=report_callback
        self.hidden_by_user=False
        self.temporarily_hidden=False
        self.minimized=False
        self.visible=False
        self.data={}
        self.position_file=APP_DIR/"overlay_xy.json"
        self.win=tk.Toplevel(root)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost",True)
        try:self.win.attributes("-alpha",.94)
        except tk.TclError:pass
        self.win.configure(bg=BG,highlightbackground="#397781",
                           highlightthickness=1)
        x,y=self._load_xy()
        self.win.geometry(f"350x285+{x}+{y}")
        self.top=tk.Frame(self.win,bg=HEADER,cursor="fleur")
        self.top.pack(fill="x")
        self.title=tk.Label(self.top,bg=HEADER,fg=TEAL,
            text="VOC TRADER VISION · DEMO  ↕ MOVER",
            font=("Segoe UI",10,"bold"),anchor="w",cursor="fleur")
        self.title.pack(side="left",fill="x",expand=True,padx=8,pady=7)
        self._button(self.top,"–",self.collapse,"#255d71").pack(side="right")
        self._button(self.top,"×",self.hide,"#255d71").pack(side="right")
        self.drag_start=None
        for w in (self.top,self.title):
            w.bind("<ButtonPress-1>",self._drag_begin)
            w.bind("<B1-Motion>",self._drag_move)
            w.bind("<ButtonRelease-1>",self._drag_end)

        self.body=tk.Frame(self.win,bg=BG)
        self.body.pack(fill="both",expand=True,padx=9,pady=5)
        self.state=tk.StringVar(value="PARADO · CLIQUES OFF")
        self.state_label=tk.Label(self.body,textvariable=self.state,
            bg=BG,fg=WARN,font=("Segoe UI",11,"bold"),
            justify="left",anchor="w",wraplength=325)
        self.state_label.pack(fill="x")
        self.details=tk.StringVar(value="Sem leitura de tela.")
        tk.Label(self.body,textvariable=self.details,bg=BG,fg=TEXT,
            font=("Consolas",9),justify="left",anchor="nw",
            wraplength=328).pack(fill="both",expand=True,pady=(3,0))
        row=tk.Frame(self.win,bg=BG)
        row.pack(fill="x",padx=8,pady=(0,8))
        self._button(row,"■ PARAR",self.stop_callback,"#a33b44").pack(
            side="left",expand=True,fill="x",padx=(0,4))
        self._button(row,"RELATÓRIO",self.report_callback,"#2b6b7f").pack(
            side="left",expand=True,fill="x")
        self.footer=row
        self._set_noactivate_win32()

    @staticmethod
    def _button(parent,text,command,bg):
        return tk.Button(parent,text=text,command=command,bg=bg,fg="white",
            relief="flat",bd=0,padx=7,pady=4,
            font=("Segoe UI",9,"bold"))

    def _load_xy(self):
        sw=self.root.winfo_screenwidth()
        sh=self.root.winfo_screenheight()
        default=(max(0,sw-375),min(210,max(10,sh-320)))
        try:
            data=json.loads(self.position_file.read_text("utf-8"))
            return max(0,min(sw-85,int(data["x"]))),max(0,min(sh-50,int(data["y"])))
        except (OSError,TypeError,KeyError,ValueError):return default

    def _store_xy(self):
        try:
            self.position_file.parent.mkdir(parents=True,exist_ok=True)
            self.position_file.write_text(json.dumps({
                "x":self.win.winfo_x(),"y":self.win.winfo_y()}),"utf-8")
        except OSError:pass

    def _drag_begin(self,event):
        self.drag_start=(event.x_root,event.y_root,
                         self.win.winfo_x(),self.win.winfo_y())

    def _drag_move(self,event):
        if self.drag_start is None:return
        sx,sy,wx,wy=self.drag_start
        x=max(0,min(self.root.winfo_screenwidth()-95,wx+event.x_root-sx))
        y=max(0,min(self.root.winfo_screenheight()-55,wy+event.y_root-sy))
        self.win.geometry(f"+{x}+{y}")

    def _drag_end(self,event):
        self.drag_start=None
        self._store_xy()

    def _set_noactivate_win32(self):
        if os.name!="nt":return
        try:
            import ctypes
            u=ctypes.windll.user32
            hwnd=u.GetAncestor(int(self.win.winfo_id()),2)
            # WS_EX_NOACTIVATE prevents the floating panel from stealing
            # foreground focus from the Chrome Hezilex tab.
            GWL_EXSTYLE=-20;WS_EX_NOACTIVATE=0x08000000
            if ctypes.sizeof(ctypes.c_void_p)==8:
                u.GetWindowLongPtrW.restype=ctypes.c_longlong
                u.SetWindowLongPtrW.argtypes=[ctypes.c_void_p,ctypes.c_int,
                                              ctypes.c_longlong]
                prev=u.GetWindowLongPtrW(hwnd,GWL_EXSTYLE)
                u.SetWindowLongPtrW(hwnd,GWL_EXSTYLE,prev|WS_EX_NOACTIVATE)
            else:
                prev=u.GetWindowLongW(hwnd,GWL_EXSTYLE)
                u.SetWindowLongW(hwnd,GWL_EXSTYLE,prev|WS_EX_NOACTIVATE)
        except (OSError,AttributeError,ValueError):
            pass

    def show(self,force=False):
        if self.hidden_by_user and not force:return
        if force:self.hidden_by_user=False
        self.temporarily_hidden=False
        self.win.deiconify()
        self.visible=True
        self._set_noactivate_win32()
        if os.name=="nt":
            try:
                import ctypes
                u=ctypes.windll.user32
                hwnd=u.GetAncestor(int(self.win.winfo_id()),2)
                u.SetWindowPos(hwnd,-1,0,0,0,0,
                               0x0001|0x0002|0x0010)  # NOMOVE/NOSIZE/NOACTIVATE
            except (OSError,AttributeError):pass

    def hide(self):
        self.hidden_by_user=True
        self.win.withdraw()
        self.visible=False

    def hide_for_capture(self):
        if self.visible:
            self.win.withdraw()
            self.visible=False
            self.temporarily_hidden=True

    def restore_after_capture(self):
        if self.temporarily_hidden and not self.hidden_by_user:
            self.temporarily_hidden=False
            self.show()

    def collapse(self):
        self.minimized=not self.minimized
        if self.minimized:
            self.body.pack_forget()
            self.win.geometry("350x76")
        else:
            self.body.pack(fill="both",expand=True,padx=9,pady=5,
                           before=self.footer)
            self.win.geometry("350x285")
        self._store_xy()

    def update_state(self,stage,lines,armed=False):
        status=f"{stage} · {'ARMADO' if armed else 'CLIQUES OFF'}"
        self.state.set(status)
        self.state_label.configure(fg=(BAD if "BLOQUEADO" in status or
                                          "ERRO" in status else
                                      TEAL if "ELEGÍVEL" in status else WARN))
        self.details.set("\n".join(str(x) for x in lines))
        self.data={"stage":stage,"lines":list(lines),"armed":armed}

    def close(self):
        self._store_xy()
        self.win.destroy()
