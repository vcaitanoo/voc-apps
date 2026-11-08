"""VOC Trader Vision PC entrypoint.

--self-test is an explicit packaging smoke test; it does NOT launch the GUI,
connect to a broker, take screen captures, or enable trades.
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--self-test-report":
        # The onedir distribution must launch with its OWN bundled Python.
        if not getattr(sys, "frozen", False):
            raise RuntimeError("Self-test requires the packaged Windows executable")
        from voc_trader_pc import gui, engine, feeds, screen, risk, tracker, overlay, session_report
        import cv2
        import numpy
        import PIL
        import mss
        import pyautogui
        info = {
            "application": "VOC Trader Vision PC",
            "version": "0.1.4-beta",
            "bundled_python": bool(getattr(sys, "frozen", False)),
            "imported": ["gui", "engine", "feeds", "screen", "risk", "tracker",
                         "cv2", "numpy", "PIL", "mss", "pyautogui", "overlay", "session_report"],
            "startup": "imports_ok",
            "trading_enabled": False,
        }
        Path(sys.argv[2]).write_text(json.dumps(info, indent=2), encoding="utf-8")
        return
    if len(sys.argv) != 1:
        raise SystemExit("Argumentos invalidos")
    from voc_trader_pc.gui import launch
    launch()


if __name__ == '__main__':
    main()
