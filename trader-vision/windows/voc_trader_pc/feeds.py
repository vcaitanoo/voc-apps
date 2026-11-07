from __future__ import annotations
from .models import Candle,TIMEFRAMES
from pathlib import Path
from datetime import datetime,timezone
import csv


def load_csv(path:Path)->list[Candle]:
    """CSV columns timestamp/time,open,high,low,close,tick_volume/volume.
    Closed candle source only; no lookahead or forward filling.
    """
    result=[]
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        for r in reader:
            if not r:continue
            low={str(k).strip().lower():str(v).strip() for k,v in r.items() if k}
            t=low.get('timestamp') or low.get('time') or low.get('date')
            if not t:continue
            try:ts=int(float(t))
            except ValueError:
                ts=int(datetime.fromisoformat(t.replace('Z','+00:00')).replace(tzinfo=timezone.utc).timestamp())
            result.append(Candle(ts,float(low['open']),float(low['high']),float(low['low']),float(low['close']),
                                 float(low.get('tick_volume') or low.get('volume') or 0.0),True))
    return sorted(result,key=lambda x:x.timestamp)


def load_csv_directory(folder:Path,symbol:str)->dict[str,list[Candle]]:
    result={}
    for tf in TIMEFRAMES:
        for stem in (f'{symbol}_{tf}',tf):
            file=folder/(stem+'.csv')
            if file.is_file():
                result[tf]=load_csv(file)
                break
    return result


def load_mt5(symbol:str,count:int=420)->dict[str,list[Candle]]:
    """Reads closed candles from an EXISTING local MT5 terminal, never executes orders.
    WARNING: MT5 prices MUST NEVER be used to click Hezilex, an independent venue.
    """
    try:import MetaTrader5 as mt5
    except ImportError:raise RuntimeError('Python MetaTrader5 não instalado; instale no PC que tem o terminal.')
    if not mt5.initialize():raise RuntimeError('MT5 não conectou ao terminal local: '+str(mt5.last_error()))
    try:
        mapping={'H4':mt5.TIMEFRAME_H4,'H1':mt5.TIMEFRAME_H1,'M15':mt5.TIMEFRAME_M15,'M5':mt5.TIMEFRAME_M5,'M1':mt5.TIMEFRAME_M1}
        data={}
        for name,tf in mapping.items():
            # start_pos=1 explicitly excludes forming bar at index 0.
            rows=mt5.copy_rates_from_pos(symbol,tf,1,count)
            if rows is None:raise RuntimeError(f'Dados MT5 indisponíveis em {name}: {mt5.last_error()}')
            data[name]=[Candle(int(r['time']),float(r['open']),float(r['high']),float(r['low']),float(r['close']),
                                float(r['tick_volume']),True) for r in rows]
        return data
    finally:mt5.shutdown()
