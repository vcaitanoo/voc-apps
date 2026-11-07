from __future__ import annotations
from dataclasses import dataclass
from time import time
from uuid import uuid4
from .journal import Journal

@dataclass
class Pending:
    id:str
    symbol:str
    strategy:str
    regime:str
    direction:str
    started:float
    balance_before:float
    stake:float
    expiry_seconds:int
    candidate:str=''
    confirmations:int=0

class DemoTracker:
    def __init__(self,journal:Journal):
        self.journal=journal
        self.pending:Pending|None=None
    def begin(self,symbol,strategy,regime,direction,balance,stake,expiry_min,now=None):
        if self.pending is not None:raise ValueError('Uma entrada demo já está pendente')
        self.pending=Pending(uuid4().hex,symbol,strategy,regime,direction,time() if now is None else now,
                             balance,stake,int(expiry_min*60))
        self.journal.append(dict(type='gesture',trade_id=self.pending.id,timestamp=self.pending.started,
                                 strategy=strategy,regime=regime,symbol=symbol,direction=direction,stake=stake,
                                 note='Toque enviado, execução da plataforma NÃO confirmada'))
        return self.pending.id
    def observe(self,after:float|None,now=None):
        p=self.pending
        if p is None:return None
        t=time() if now is None else now
        if t < p.started+p.expiry_seconds+4:return 'AGUARDANDO_EXPIRACAO'
        if t > p.started+p.expiry_seconds+180:
            self.journal.append(dict(type='unconfirmed',trade_id=p.id,timestamp=t,strategy=p.strategy,
                                     regime=p.regime,symbol=p.symbol,reason='Resultado não verificado'))
            self.pending=None
            return 'NAO_CONFIRMADO'
        if after is None:return 'OCR_SALDO_INDISPONIVEL'
        delta=round(after-p.balance_before,2)
        threshold=max(.08,p.stake*.15)
        if threshold<=delta<=p.stake*1.05:outcome='WIN'
        elif abs(delta+p.stake)<=max(.04,p.stake*.04):outcome='LOSS'
        else:return 'SALDO_NAO_CONCLUSIVO'
        p.confirmations=p.confirmations+1 if p.candidate==outcome else 1
        p.candidate=outcome
        if p.confirmations<2:return 'CONFIRMANDO_RESULTADO'
        self.journal.append(dict(type='settlement',trade_id=p.id,timestamp=t,strategy=p.strategy,
                                 regime=p.regime,symbol=p.symbol,outcome=outcome,pnl=delta,
                                 note='Inferido por 2 leituras do saldo DEMO; confirme no histórico'))
        self.pending=None
        return outcome
