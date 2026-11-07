from __future__ import annotations
from .models import RiskVerdict


def stake_verdict(balance:float,risk_pct:float,min_stake:float=1.0,day_pnl:float=0.0,
                  max_daily_loss_pct:float=3.0,target_daily_pct:float=2.0,
                  trades_today:int=0,max_daily_entries:int=8)->RiskVerdict:
    """No margin above 1%; an obligatory €1 broker minimum is NOT an exception."""
    if balance <=0 or risk_pct<=0 or risk_pct>1.0 or min_stake<=0:
        return RiskVerdict(False,'Risco/saldo inválido: máximo absoluto de 1%',0,0,0)
    if day_pnl <= -balance*max_daily_loss_pct/100:
        return RiskVerdict(False,'Limite diário de perdas atingido',0,0,0)
    if day_pnl >= balance*target_daily_pct/100:
        return RiskVerdict(False,'Meta diária alcançada; parar novas entradas',0,0,0)
    if trades_today>=max_daily_entries:
        return RiskVerdict(False,'Máximo diário de entradas atingido',0,0,0)
    ceiling=round(balance*min(risk_pct,1.0)/100,2)
    if ceiling<min_stake:
        return RiskVerdict(False,f'Entrada mínima €{min_stake:.2f} excede {risk_pct:.2f}% do saldo (máximo €{ceiling:.2f})',0,ceiling,0)
    amount=max(min_stake,ceiling)
    return RiskVerdict(True,'Dentro de 1% da banca',amount,amount,100*amount/balance)
