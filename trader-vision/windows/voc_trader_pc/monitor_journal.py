"""Persistent technical monitor for unattended DEMO observation.

Never counts a mouse click as WIN or LOSS. Confirmed results still come only
from the existing DemoTracker/Journal, which are NOT modified.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
import time

from .storage import APP_DIR

DEFAULT_LOG=APP_DIR/"monitoramento_pc.csv"
COLUMNS=[
    "hora_local","estado","fonte","cliques_armados","browser_ativo",
    "conta_demo","ativo_configurado","ativo_lido","velas_fechadas",
    "segundos_relogio","nota_tecnica","sinal","estrategia",
    "saldo_ocr","valor_ocr","expiracao_ocr","bloqueio",
    "ultima_acao","wins_confirmados","losses_confirmados",
    "operacoes_conciliadas"
]


class MonitorJournal:
    def __init__(self,path:Path=DEFAULT_LOG):
        self.path=Path(path)
        self.last_at=0.0
        self.last_signature=None
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size==0:
            with self.path.open("w",encoding="utf-8-sig",newline="") as stream:
                csv.writer(stream,delimiter=";").writerow(COLUMNS)

    def append(self,values:dict,force=False):
        signature=(values.get("estado"),values.get("cliques_armados"),
                   values.get("bloqueio"),values.get("ultima_acao"),
                   values.get("wins_confirmados"),values.get("losses_confirmados"))
        now=time.monotonic()
        if not force and signature==self.last_signature and now-self.last_at<60:
            return False
        row=[datetime.now().astimezone().isoformat(timespec="seconds")]
        row.extend(str(values.get(key,"")) if values.get(key) is not None else ""
                   for key in COLUMNS[1:])
        with self.path.open("a",encoding="utf-8",newline="") as stream:
            csv.writer(stream,delimiter=";").writerow(row)
        self.last_signature=signature
        self.last_at=now
        return True
