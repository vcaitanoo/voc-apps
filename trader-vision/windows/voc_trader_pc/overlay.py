"""Read-only floating status overlay for the existing VOC Trader Vision PC.

Only the main Tk thread creates or updates widgets. The overlay cannot arm
trading; its only execution control is STOP (which disarms the application).
On Windows 10/11, WDA_EXCLUDEFROMCAPTURE prevents the floating dashboard
from contaminating chart screenshots. The application implements a safe
temporary-hide fallback when display affinity is unavailable.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import ctypes
import json
import os
import sys
import tkinter as tk

from .storage import APP_DIR


@dataclass(frozen=True)
class OverlayState:
    phase: str = "PARADO"
    source: str = "SCREEN"
    armed: bool = False
    demo: bool | None = None
    ocr_ok: bool | None = None
    symbol: str = "—"
    timeframe: str = "—"
    candles: int | None = None
    clock: int | None = None
    strategy: str = "Nenhuma"
    direction: str = "AGUARDAR"
    score: int | None = None
    reason: str = "Aguardando leitura do gráfico."
    last_action: str = "Nenhuma"
    balance: float | None = None
    stake: float | None = None
    expiry: int | None = None
    wins: int = 0
    losses: int = 0
    settled: int = 0
    pending: bool = False
    captured_at: float | None = None


def short(text: object, limit: int = 120) -> str:
    cleaned = " ".join(str(text or "").split())
    return cleaned if len(cleaned) <= limit else cleaned[:limit - 1] + "…"


def status_color(state: OverlayState) -> str:
    label = state.phase.upper()
    if "ERRO" in label or "BLOQUE" in label:
        return "#f09b93"
    if state.pending or "TOQUE" in label or "ELEGÍVEL" in label:
        return "#61e5ac"
    if "PARADO" in label:
        return "#a5b4c9"
    if "AGUARD" in label or "SEM DADOS" in label:
        return "#ffd080"
    return "#7acefa"


class FloatingOverlay:
    """Topmost draggable overlay; Tk calls are only permitted on the GUI thread."""

    POSITION_FILE: Path = APP_DIR / "overlay_position.json"

    def __init__(self, root: tk.Misc, *, stop_callback, report_callback):
        self.root = root
        self.stop_callback = stop_callback
        self.report_callback = report_callback
        self.user_hidden = False
        self.visible = False
        self.capture_excluded = False
        self._temporary_hidden = False
        self.collapsed = False
        self.state = OverlayState()
        self._drag = None

        self.win = tk.Toplevel(root, bg="#101e31")
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        try:
            self.win.attributes("-alpha", 0.91)
        except tk.TclError:
            pass
        self.win.configure(highlightbackground="#32747a", highlightthickness=1)
        self.win.protocol("WM_DELETE_WINDOW", self.hide)
        x, y = self._restore_position()
        self.win.geometry(f"360x342+{x}+{y}")

        self.header = tk.Frame(self.win, bg="#164258", height=35, cursor="fleur")
        self.header.pack(fill="x")
        tk.Label(self.header, text="VOC TRADER VISION · DEMO  ⠿ ARRASTE",
                 bg="#164258", fg="#7cf0cf", font=("Segoe UI", 10, "bold"),
                 anchor="w", cursor="fleur").pack(side="left", fill="x", expand=True, padx=8)
        self._button(self.header, "—", self.toggle_collapse, "#245a70", 1).pack(side="right", padx=(0,3))
        self._button(self.header, "×", self.hide, "#245a70", 1).pack(side="right", padx=(0,3))
        for widget in (self.header, *self.header.winfo_children()[:1]):
            widget.bind("<ButtonPress-1>", self._begin_drag)
            widget.bind("<B1-Motion>", self._move_drag)
            widget.bind("<ButtonRelease-1>", self._end_drag)

        self.body = tk.Frame(self.win, bg="#101e31")
        self.body.pack(fill="both", expand=True, padx=11, pady=7)
        self.phase_var = tk.StringVar(value="PARADO · CLIQUES OFF")
        self.phase_lbl = tk.Label(self.body, textvariable=self.phase_var,
                                  bg="#101e31", fg="#a5b4c9",
                                  font=("Segoe UI", 12, "bold"),
                                  justify="left", anchor="w", wraplength=326)
        self.phase_lbl.pack(fill="x", pady=(0,3))
        self.detail_vars = {}
        for name in ("feed", "analysis", "strategy", "clock", "risk", "why", "last", "results", "freshness"):
            val = tk.StringVar(value="—")
            self.detail_vars[name] = val
            tk.Label(self.body, textvariable=val, bg="#101e31",
                     fg="#d5e3f0" if name not in ("why", "freshness") else "#ffcf8d",
                     font=("Consolas", 9), anchor="w", justify="left",
                     wraplength=328).pack(fill="x", pady=(0,2))
        self.controls = tk.Frame(self.win, bg="#101e31")
        self.controls.pack(fill="x", padx=10, pady=(0,10))
        self._button(self.controls, "■ PARAR BOT", stop_callback, "#9a3c45", 9).pack(
            side="left", fill="x", expand=True, padx=(0,4))
        self._button(self.controls, "RELATÓRIO", report_callback, "#266077", 8).pack(
            side="left", fill="x", expand=True)
        self._apply_state()
        self.win.after(1000, self._heartbeat)

    @staticmethod
    def _button(parent, title, command, color, width):
        return tk.Button(parent, text=title, command=command,
                         width=width, bg=color, fg="white",
                         activebackground="#287c88", activeforeground="white",
                         relief="flat", bd=0, padx=5, pady=5,
                         font=("Segoe UI", 9, "bold"))

    def _restore_position(self) -> tuple[int,int]:
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        initial = (max(0,width-392), max(30,min(148,height-400)))
        try:
            raw=json.loads(self.POSITION_FILE.read_text(encoding="utf-8"))
            return (max(0,min(width-125,int(raw["x"]))),
                    max(0,min(height-80,int(raw["y"]))))
        except (OSError, ValueError, TypeError, KeyError):
            return initial

    def _store_position(self):
        try:
            self.POSITION_FILE.parent.mkdir(parents=True, exist_ok=True)
            data={"x":self.win.winfo_x(),"y":self.win.winfo_y()}
            tmp=self.POSITION_FILE.with_suffix(".tmp")
            tmp.write_text(json.dumps(data),encoding="utf-8")
            tmp.replace(self.POSITION_FILE)
        except OSError:
            pass

    def _begin_drag(self, event):
        self._drag=(event.x_root,event.y_root,self.win.winfo_x(),self.win.winfo_y())

    def _move_drag(self, event):
        if self._drag is None:return
        sx,sy,ox,oy=self._drag
        x=max(0,min(self.root.winfo_screenwidth()-100,ox+event.x_root-sx))
        y=max(0,min(self.root.winfo_screenheight()-55,oy+event.y_root-sy))
        self.win.geometry(f"+{x}+{y}")

    def _end_drag(self, event):
        if self._drag is not None:self._store_position()
        self._drag=None

    def show(self, force: bool = False):
        if self.user_hidden and not force:return
        if force:self.user_hidden=False
        self._temporary_hidden=False
        self.win.deiconify()
        self.win.lift()
        self.visible=True
        self.win.after(150, self._enable_capture_exclusion)

    def hide(self):
        self.user_hidden=True
        self.visible=False
        self.win.withdraw()

    def hide_for_capture(self):
        if self.visible and not self.capture_excluded:
            self.win.withdraw()
            self._temporary_hidden=True
            self.visible=False

    def show_after_capture(self):
        if self._temporary_hidden:
            self._temporary_hidden=False
            if not self.user_hidden:
                self.win.deiconify()
                self.visible=True
                self.win.after(100,self._enable_capture_exclusion)

    def _enable_capture_exclusion(self):
        if not self.visible or not sys.platform.startswith("win"):return
        try:
            from ctypes import wintypes
            user32=ctypes.windll.user32
            user32.GetAncestor.argtypes=[wintypes.HWND,wintypes.UINT]
            user32.GetAncestor.restype=wintypes.HWND
            user32.SetWindowDisplayAffinity.argtypes=[wintypes.HWND,wintypes.DWORD]
            user32.SetWindowDisplayAffinity.restype=wintypes.BOOL
            hwnd=user32.GetAncestor(self.win.winfo_id(),2)
            self.capture_excluded=bool(user32.SetWindowDisplayAffinity(hwnd,0x11))
        except (OSError,AttributeError,ValueError):
            self.capture_excluded=False

    def toggle_collapse(self):
        self.collapsed=not self.collapsed
        if self.collapsed:
            self.body.pack_forget()
            self.win.geometry("360x84")
        else:
            self.body.pack(fill="both",expand=True,padx=11,pady=7,before=self.controls)
            self.win.geometry("360x342")
        self._store_position()

    def update(self, state: OverlayState):
        self.state=state
        self._apply_state()

    def _apply_state(self):
        st=self.state
        click_state="ARMADO" if st.armed else "CLIQUES OFF"
        self.phase_var.set(f"{short(st.phase,32)} · {click_state}")
        self.phase_lbl.configure(fg=status_color(st))
        values={
            "feed": f"{st.source} | Tela: {'DEMO OK' if st.demo else 'NÃO CONFIRMADA'} | OCR: {'OK' if st.ocr_ok else 'BLOQUEADO'}"
                     if st.source=="SCREEN" else f"{st.source} · leitura, sem ordens",
            "analysis": f"{short(st.symbol,14)} {st.timeframe} | Velas: {st.candles if st.candles is not None else '—'}",
            "strategy": f"{short(st.direction,8)} {st.score if st.score is not None else '—'}/100 | {short(st.strategy,28)}",
            "clock": f"Vela: {st.clock}s | Entrada: {f'€{st.stake:.2f}' if st.stake is not None else '?'}"
                     f" | Saldo: {f'€{st.balance:.2f}' if st.balance is not None else '?'}",
            "risk": f"Expiração: {st.expiry if st.expiry is not None else '?'}min | Pendente: {'SIM' if st.pending else 'NÃO'}",
            "why": f"Motivo: {short(st.reason,94)}",
            "last": f"Última ação: {short(st.last_action,60)}",
            "results": f"RESULTADOS CONFIRMADOS: {st.settled} | WIN {st.wins} | LOSS {st.losses}",
            "freshness": self._age_text(),
        }
        for key,value in values.items():
            self.detail_vars[key].set(value)

    def _age_text(self)->str:
        if self.state.captured_at is None:return "Aguardando primeira leitura do motor"
        from time import time
        elapsed=max(0,int(time()-self.state.captured_at))
        stamp=datetime.fromtimestamp(self.state.captured_at).strftime("%H:%M:%S")
        return (f"Última leitura: {stamp} · há {elapsed}s"
                + (" · SEM ATUALIZAÇÃO" if elapsed>25 else ""))

    def _heartbeat(self):
        try:
            self.detail_vars["freshness"].set(self._age_text())
            self.win.after(1000,self._heartbeat)
        except tk.TclError:
            return

    def destroy(self):
        self._store_position()
        self.win.destroy()
