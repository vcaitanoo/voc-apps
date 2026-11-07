from __future__ import annotations
from collections.abc import Sequence
from math import sqrt
from .models import Candle


def ema(values: Sequence[float], period: int) -> list[float]:
    if not values: return []
    alpha = 2.0 / (period + 1)
    out = [float(values[0])]
    for v in values[1:]:
        out.append(out[-1] + alpha * (float(v) - out[-1]))
    return out


def sma(values: Sequence[float], period: int) -> list[float]:
    out = []
    total = 0.0
    for i, v in enumerate(values):
        total += v
        if i >= period: total -= values[i - period]
        out.append(total / min(i + 1, period))
    return out


def atr(candles: Sequence[Candle], period: int = 14) -> list[float]:
    if not candles: return []
    tr = [candles[0].range]
    for i in range(1, len(candles)):
        c, previous = candles[i], candles[i - 1]
        tr.append(max(c.range, abs(c.high - previous.close), abs(c.low - previous.close)))
    out = [tr[0]]
    for i in range(1, len(tr)):
        out.append((out[-1] * (min(period, i + 1) - 1) + tr[i]) / min(period, i + 1))
    return out


def rsi(candles: Sequence[Candle], period: int = 14) -> list[float]:
    if not candles: return []
    ups, downs = 0.0, 0.0
    out = [50.0]
    for i in range(1, len(candles)):
        d = candles[i].close - candles[i - 1].close
        gain = max(d, 0.0); loss = max(-d, 0.0)
        if i <= period:
            ups += gain; downs += loss
            average_gain = ups / i
            average_loss = downs / i
        else:
            average_gain = (average_gain * (period - 1) + gain) / period
            average_loss = (average_loss * (period - 1) + loss) / period
        if average_loss < 1e-14:
            out.append(100.0 if average_gain > 1e-14 else 50.0)
        else:
            out.append(100 - 100 / (1 + average_gain / average_loss))
    return out


def adx(candles: Sequence[Candle], period: int = 14) -> list[float]:
    """Wilder-smoothed ADX, with no access to future bars."""
    if not candles: return []
    plus_dm=[0.0]; minus_dm=[0.0]; tr=[candles[0].range]
    for i in range(1,len(candles)):
        a,b=candles[i],candles[i-1]
        u=a.high-b.high; d=b.low-a.low
        plus_dm.append(u if u>d and u>0 else 0.0)
        minus_dm.append(d if d>u and d>0 else 0.0)
        tr.append(max(a.range, abs(a.high-b.close),abs(a.low-b.close)))
    def smooth(values):
        result=[values[0]]
        for i in range(1,len(values)):
            p=min(period,i+1)
            result.append((result[-1]*(p-1)+values[i])/p)
        return result
    pt,mt,tt=map(smooth, (plus_dm,minus_dm,tr))
    dx=[]
    for p,m,t in zip(pt,mt,tt):
        dpi=100*p/max(t,1e-14); dmi=100*m/max(t,1e-14)
        dx.append(100*abs(dpi-dmi)/max(dpi+dmi,1e-14))
    # Wilder ADX is a smoothed DX, not instantaneous DX.
    return smooth(dx)


def bollinger(values: Sequence[float], period=20, stdev=2.0):
    mid=sma(values,period)
    upper=[];lower=[]
    for i, m in enumerate(mid):
        window=values[max(0,i-period+1):i+1]
        deviation=sqrt(sum((v-m)**2 for v in window)/max(1,len(window)))
        upper.append(m+stdev*deviation)
        lower.append(m-stdev*deviation)
    return mid,upper,lower


def structure(candles: Sequence[Candle], lookback=25):
    # Simple confirmed swing highs/lows; never use future bars relative to last closed bar.
    data=candles[-lookback:]; n=len(data)
    highs=[]; lows=[]
    for i in range(2,n-2):
        if data[i].high>max(data[i-2].high,data[i-1].high,data[i+1].high,data[i+2].high):highs.append(data[i].high)
        if data[i].low<min(data[i-2].low,data[i-1].low,data[i+1].low,data[i+2].low):lows.append(data[i].low)
    if len(highs)>=2 and len(lows)>=2:
        if highs[-1]>highs[-2] and lows[-1]>lows[-2]:return 'HH/HL'
        if highs[-1]<highs[-2] and lows[-1]<lows[-2]:return 'LH/LL'
    return 'MISTA'
