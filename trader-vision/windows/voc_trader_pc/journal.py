from __future__ import annotations
from dataclasses import asdict
from datetime import datetime,timezone
import csv,json,os
from pathlib import Path

class Journal:
    def __init__(self, path:Path):self.path=path;path.parent.mkdir(parents=True,exist_ok=True)
    def append(self, record:dict):
        with self.path.open('a',encoding='utf8') as f:
            f.write(json.dumps(record,ensure_ascii=False,sort_keys=True)+'\n')
    def records(self):
        if not self.path.exists():return []
        rows=[]
        for line in self.path.read_text(encoding='utf8').splitlines():
            try:rows.append(json.loads(line))
            except Exception:pass
        return rows
    def closed_trades(self):
        return [r for r in self.records() if r.get('type')=='settlement' and r.get('outcome') in ('WIN','LOSS','BREAKEVEN')]
    def summary(self):
        trades=self.closed_trades(); wins=sum(1 for t in trades if t['outcome']=='WIN')
        losses=sum(1 for t in trades if t['outcome']=='LOSS')
        gross=sum(max(0.0,float(t.get('pnl',0))) for t in trades)
        negative=sum(min(0.0,float(t.get('pnl',0))) for t in trades)
        equity=0;high=0;max_dd=0
        for t in sorted(trades,key=lambda t:t.get('timestamp',0)):
            equity+=float(t.get('pnl',0));high=max(high,equity);max_dd=max(max_dd,high-equity)
        return dict(total=len(trades),wins=wins,losses=losses,win_rate=round(100*wins/len(trades),2) if trades else None,
                    gross=round(gross,2),losses_gross=round(-negative,2),net=round(gross+negative,2),
                    profit_factor=round(gross/-negative,3) if negative<0 else None,drawdown_eur=round(max_dd,2))
    def today_stats(self):
        today=datetime.now().date()
        trades=[r for r in self.closed_trades()
                if datetime.fromtimestamp(float(r.get('timestamp',0))).date()==today]
        return (sum(float(r.get('pnl',0)) for r in trades),len(trades))

    def matching_expectancy(self,strategy:str,regime:str,min_samples=30):
        matches=[r for r in self.closed_trades() if r.get('strategy')==strategy and r.get('regime')==regime]
        if len(matches)<min_samples:return None,len(matches)
        return sum(float(x.get('pnl',0)) for x in matches)/len(matches),len(matches)
