"""Regressions for the hidden CALIBRAR TELA button on a 1366x768 PC.

Tests actual Tk geometry on Windows CI. The app starts disarmed; these tests
never capture the screen or interact with Hezilex.
"""
import tkinter as tk
from voc_trader_pc.gui import TraderApp


def test_calibration_is_visible_and_controls_are_scrollable():
    root=tk.Tk()
    try:
        root.geometry("1080x650+0+0")
        app=TraderApp(root)
        for height in (650, 580):
            root.geometry(f"1080x{height}+0+0")
            root.update_idletasks()
            root.update()
            button=app.calibration_button
            assert button.winfo_ismapped(), "CALIBRAR button was clipped"
            assert "CALIBRAR TELA" in button.cget("text")
            assert button.winfo_rooty() >= root.winfo_rooty()
            assert (button.winfo_rooty()+button.winfo_height()
                    < root.winfo_rooty()+root.winfo_height()), (
                        "CALIBRAR TELA must stay above window bottom")
            assert app.controls_canvas.winfo_ismapped(), "settings scroll area missing"
            assert app.controls_canvas.winfo_height()>10
            whole=app.controls_canvas.bbox("all")
            assert whole is not None
            assert whole[3]>app.controls_canvas.winfo_height(), (
                "all settings must remain reachable by scroll")
    finally:
        root.destroy()
