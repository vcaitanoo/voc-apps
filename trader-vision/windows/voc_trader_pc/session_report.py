"""Persistent read-only dashboard history, so overnight DEMO tests can be audited.

This is NOT a broker statement or proof that a click was an accepted order.
Only Journal settlement entries count as confirmed WIN or LOSS.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
import time

from .overlay import OverlayState
from .storage import APP_DIR

REPORT_FILE = APP_DIR / "monitoramento_pc.csv"
HEADERS = (
    "hora_pc", "fonte", "estado", "cliques_armados", "conta_demo_confirmada",
    "ocr_ok", "ativo", "timeframe", "velas", "relogio_segundos",
    "estrategia", "direcao", "nota_tecnica", "motivo_ou_bloqueio",
    "ultima_acao", "saldo_lido_eur", "entrada_lida_eur", "expiracao_min",
    "win_confirmados", "loss_confirmados", "resultados_conciliados",
    "operacao_pendente",
)


def report_row(state: OverlayState) -> list[str]:
    return [
        datetime.now().astimezone().isoformat(timespec="seconds"),
        state.source, state.phase, str(state.armed),
        str(state.demo), str(state.ocr_ok), state.symbol, state.timeframe,
        "" if state.candles is None else str(state.candles),
        "" if state.clock is None else str(state.clock),
        state.strategy, state.direction,
        "" if state.score is None else str(state.score),
        state.reason, state.last_action,
        "" if state.balance is None else f"{state.balance:.2f}",
        "" if state.stake is None else f"{state.stake:.2f}",
        "" if state.expiry is None else str(state.expiry),
        str(state.wins), str(state.losses), str(state.settled), str(state.pending),
    ]


class SessionReporter:
    def __init__(self, path: Path = REPORT_FILE):
        self.path=path
        self.last_write=0.0
        self.last_event=None
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size==0:
            with self.path.open("w",encoding="utf-8-sig",newline="") as f:
                csv.writer(f,delimiter=";").writerow(HEADERS)

    def record(self, state: OverlayState, *, force: bool = False)->bool:
        now=time.monotonic()
        important = (state.phase, state.armed, state.pending,
                     state.wins, state.losses, state.settled, state.last_action)
        if not force and now-self.last_write<60 and important==self.last_event:
            return False
        with self.path.open("a",encoding="utf-8",newline="") as f:
            csv.writer(f,delimiter=";").writerow(report_row(state))
        self.last_write=now
        self.last_event=important
        return True
