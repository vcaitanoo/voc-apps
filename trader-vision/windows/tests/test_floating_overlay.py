"""Windows Tk tests for the real overlay, STOP and overnight report.

No broker, mouse automation, OCR or live trades are used in these tests.
"""
import csv
import queue
import threading
from pathlib import Path
import tkinter as tk

from voc_trader_pc.gui import TraderApp
from voc_trader_pc.overlay import FloatingOverlay, OverlayState, status_color
from voc_trader_pc.session_report import SessionReporter


def test_overlay_status_and_manual_controls(tmp_path,monkeypatch):
    monkeypatch.setattr(FloatingOverlay, "POSITION_FILE", tmp_path / "position.json")
    root=tk.Tk()
    try:
        root.geometry("1080x650+0+0")
        app=TraderApp(root)
        root.update()
        app.show_overlay()
        root.update()
        panel=app.overlay
        assert panel.visible
        assert panel.win.winfo_ismapped()
        assert panel.win.attributes("-topmost")
        state=OverlayState(phase="BLOQUEADO",source="SCREEN",armed=True,
            demo=True,ocr_ok=True,symbol="EURUSD",timeframe="M5",
            candles=38,clock=192,strategy="Recuo EMA21",direction="COMPRAR",
            score=89,reason="Risco excede limite 1% da banca",balance=32.05,
            stake=1.0,expiry=5,wins=2,losses=1,settled=3,
            last_action="Nenhuma operação enviada")
        panel.update(state)
        assert "COMPRAR 89/100" in panel.detail_vars["strategy"].get()
        assert "Velas: 38" in panel.detail_vars["analysis"].get()
        assert "WIN 2" in panel.detail_vars["results"].get()
        assert status_color(state) == "#f09b93"
        panel.toggle_collapse()
        assert panel.collapsed
        panel.toggle_collapse()
        assert not panel.collapsed
        # Native display-exclusion fallback must hide before screenshots.
        panel.capture_excluded=False
        panel.hide_for_capture()
        assert not panel.visible
        panel.show_after_capture()
        assert panel.visible
        panel.hide()
        assert not panel.visible
        panel.show(force=True)
        assert panel.visible
        app.demo_event.set()
        app.demo.set(True)
        # Clicking STOP button must disarm and stop the session.
        stop=panel.controls.winfo_children()[0]
        stop.invoke()
        assert not app.demo_event.is_set()
        assert app.stop_event.is_set()
        assert panel.state.phase=="PARADO"
    finally:
        root.destroy()


def test_capture_fallback_waits_until_overlay_is_hidden():
    class FakeOverlay:
        visible=True
        capture_excluded=False
        def __init__(self):self.hidden=False
    app=TraderApp.__new__(TraderApp)
    app.overlay=FakeOverlay()
    app.events=queue.Queue()
    result=[]
    thread=threading.Thread(target=lambda:
        result.append(app._capture_without_panel(lambda:
            "hidden" if app.overlay.hidden else "UNSAFE")),daemon=True)
    thread.start()
    event=app.events.get(timeout=3)
    assert event[0]=="overlay_capture_hide"
    app.overlay.hidden=True
    event[1].set()
    thread.join(3)
    assert not thread.is_alive()
    assert result==["hidden"]
    assert app.events.get(timeout=3)[0]=="overlay_capture_restore"


def test_overnight_report_contains_real_status_and_not_fake_wins(tmp_path):
    reporter=SessionReporter(tmp_path/"session.csv")
    state=OverlayState(phase="OBSERVANDO",source="SCREEN",armed=False,
        demo=True,ocr_ok=True,symbol="EURUSD",candles=42,timeframe="M5",
        direction="AGUARDAR",score=None,reason="Sem sinal confirmado",
        wins=0,losses=0,settled=0)
    assert reporter.record(state,force=True)
    assert not reporter.record(state)
    new=OverlayState(phase="AGUARDANDO RESULTADO",armed=True,pending=True,
        last_action="GESTO DEMO ENVIADO; aceitação NÃO VERIFICADA")
    assert reporter.record(new)
    with reporter.path.open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f,delimiter=";"))
    assert len(rows)==2
    assert rows[0]["win_confirmados"]=="0"
    assert rows[1]["operacao_pendente"]=="True"
    assert "GESTO" in rows[1]["ultima_acao"]
