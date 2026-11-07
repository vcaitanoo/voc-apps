from __future__ import annotations
from .models import Candle, Candidate, Context, Decision, TIMEFRAMES
from . import indicators as ind
from .journal import Journal
from dataclasses import replace
from math import isfinite
import time

MIN_HISTORY=210


def context(tf:str,candles:list[Candle])->Context:
    bars=[c for c in candles if c.closed]
    c=Context(timeframe=tf,n=len(bars))
    if len(bars)<60:return c
    if len(bars)<210:c.factors.append('EMA200 provisória: menos de 210 velas; contexto reduzido')
    prices=[x.close for x in bars]
    e9,e21,e50,e200=(ind.ema(prices,n) for n in (9,21,50,200))
    a=ind.atr(bars);r=ind.rsi(bars);dx=ind.adx(bars)
    mid,upper,lower=ind.bollinger(prices)
    c.ema9,c.ema21,c.ema50,c.ema200=e9[-1],e21[-1],e50[-1],e200[-1]
    c.rsi=r[-1];c.adx=dx[-1];c.atr=a[-1]
    c.bb_width=(upper[-1]-lower[-1])/max(a[-1],1e-12)
    c.slope=(e21[-1]-e21[-min(len(e21),7)])/max(a[-1],1e-12)
    c.structure=ind.structure(bars)
    c.last_price=prices[-1]
    volumes=[x.volume for x in bars[-21:]]
    if len(volumes)>=21 and sum(volumes[:-1])>0:
        c.volume_ratio=volumes[-1]/max(sum(volumes[:-1])/20.0,1e-9)
    # Strong regime requires directional structure, moving-average slope and ADX.
    order_up=e9[-1]>e21[-1]>e50[-1] and prices[-1]>e200[-1]
    order_down=e9[-1]<e21[-1]<e50[-1] and prices[-1]<e200[-1]
    if order_up and c.slope>.12 and dx[-1]>=24 and c.structure!='LH/LL':
        c.regime='TENDÊNCIA FORTE ALTA';c.direction=1
    elif order_down and c.slope<-.12 and dx[-1]>=24 and c.structure!='HH/HL':
        c.regime='TENDÊNCIA FORTE BAIXA';c.direction=-1
    elif c.bb_width<2.5 and abs(c.slope)<.23:
        c.regime='COMPRESSÃO';c.direction=0
    elif dx[-1]<19 and abs(c.slope)<.22:
        c.regime='LATERAL';c.direction=0
    elif abs(prices[-1]-e21[-1])>2.6*max(a[-1],1e-12) and (r[-1]>72 or r[-1]<28):
        c.regime='EXAUSTÃO';c.direction=0
    elif dx[-1]>=19 and abs(c.slope)>.06:
        c.regime='TENDÊNCIA FRACA';c.direction=1 if c.slope>0 else -1
    else:
        c.regime='TRANSIÇÃO';c.direction=0
    if c.structure=='HH/HL':c.factors.append('máximas/mínimas ascendentes')
    if c.structure=='LH/LL':c.factors.append('máximas/mínimas descendentes')
    c.factors.append(f'ADX {c.adx:.1f}, RSI {c.rsi:.1f}, inclinação EMA21/ATR {c.slope:+.2f}')
    if c.volume_ratio is None:c.factors.append('volume de ticks indisponível')
    else:c.factors.append(f'volume relativo {c.volume_ratio:.2f}x')
    return c


def rejection(c:Candle,side:int)->bool:
    if c.range<=0:return False
    if side==1:
        return c.bullish and c.lower_wick > max(c.body*1.2,c.range*.23) and c.close>c.low+.55*c.range
    return (not c.bullish) and c.upper_wick > max(c.body*1.2,c.range*.23) and c.close<c.high-.55*c.range


def engulf(c:Candle,prev:Candle,side:int)->bool:
    if side==1:return c.bullish and not prev.bullish and c.open<=prev.close and c.close>=prev.open
    return not c.bullish and prev.bullish and c.open>=prev.close and c.close<=prev.open


def bar_trigger(bars:list[Candle],side:int)->bool:
    closed=[b for b in bars if b.closed]
    if len(closed)<3:return False
    c,p=closed[-1],closed[-2]
    return rejection(c,side) or engulf(c,p,side) or (c.close>p.high if side==1 else c.close<p.low)


def evaluate(symbol:str,data:dict[str,list[Candle]],journal:Journal|None=None,
             *,now:int|None=None, source:str='MT5', minimum_score:int=78,
             allow_limited_context:bool=False,spread_points:float|None=None,
             max_spread_points:float|None=None)->Decision:
    ts=int(time.time()) if now is None else now
    contexts={tf:context(tf,data.get(tf,[])) for tf in TIMEFRAMES if data.get(tf)}
    missing=[tf for tf in TIMEFRAMES if tf not in data or len([x for x in data[tf] if x.closed])<60]
    if not contexts:
        return Decision(symbol,'SEM DADOS','Sem candles reais/visuais suficientes.',{},None,list(TIMEFRAMES),source,ts)
    frame=data.get('M5') or data.get('M1') or []
    frame=[x for x in frame if x.closed]
    if len(frame)<60:
        return Decision(symbol,'SEM DADOS','Precisamos de pelo menos 60 velas fechadas no M5 ou M1 para sinais.',contexts,None,missing,source,ts)
    m5=contexts.get('M5') or contexts.get('M1')
    broader=[contexts[t] for t in ('H4','H1','M15') if t in contexts and contexts[t].regime!='SEM DADOS']
    direction=0
    if m5.direction!=0:direction=m5.direction
    elif broader:
        d=sum(x.direction for x in broader)
        direction=1 if d>0 else -1 if d<0 else 0
    last=frame[-1];prev=frame[-2]
    atr=max(m5.atr,1e-10)
    support=min(c.low for c in frame[-25:-1]);resistance=max(c.high for c in frame[-25:-1])
    e21=m5.ema21
    proposals=[]
    def add(strategy,side,quality,reasons,against,trigger,invalid,tf='M5'):
        # Technical quality, not a calibrated success probability.
        if quality<55:return
        support_dirs=sum(x.direction==side for x in broader)
        conflict_dirs=sum(x.direction==-side for x in broader)
        if broader:quality+=min(9,support_dirs*3)-min(12,conflict_dirs*4)
        if m5.direction==-side:quality-=12
        if m5.structure in (('HH/HL' if side==-1 else 'LH/LL'),):quality-=8
        if abs(last.close-e21)>2.6*atr:quality-=8;against.append('preço estendido da EMA21')
        if m5.volume_ratio is not None and m5.volume_ratio>1.4:quality+=4;reasons.append('volume relativo favorável')
        if m5.volume_ratio is None:against.append('volume não disponível')
        ev,n=(journal.matching_expectancy(strategy,m5.regime) if journal else (None,0))
        if ev is not None:
            # Positive expectancy requires enough equivalent settled trades.
            quality+=min(7,max(-10,int(ev*7)))
            reasons.append(f'histórico: {n} operações parecidas, expectativa {ev:+.3f} por operação')
        else:against.append(f'histórico insuficiente ({n}/30 operações equivalentes)')
        quality=max(0,min(100,quality))
        proposals.append(Candidate(symbol,'COMPRAR' if side==1 else 'VENDER',strategy,m5.regime,quality,
                       reasons,against,trigger,invalid,ts+300,ts,tf,False,'AGUARDANDO',ev,n))
    if direction:
        touch=last.low<=e21+.45*atr and last.high>=e21-.45*atr
        if touch and (last.close-e21)*direction>-.12*atr:
            add('Continuação EMA21',direction,76,['recuo à EMA21 histórica da vela','contexto direcional'],[],
                last.high if direction==1 else last.low,
                min(support,last.low-.3*atr) if direction==1 else max(resistance,last.high+.3*atr))
    if last.close>resistance+.12*atr and last.bullish:
        add('Rompimento + reteste',1,72,['fecho acima da resistência'],['aguardar reteste/confirmar suporte'],
            last.high,support)
    if last.close<support-.12*atr and not last.bullish:
        add('Rompimento + reteste',-1,72,['fecho abaixo do suporte'],['aguardar reteste/confirmar resistência'],
            last.low,resistance)
    if last.high>resistance+.12*atr and last.close<resistance and rejection(last,-1):
        add('Varredura de liquidez',-1,79,['varredura de máximas e retorno ao intervalo'],[],last.low,last.high+.15*atr)
    if last.low<support-.12*atr and last.close>support and rejection(last,1):
        add('Varredura de liquidez',1,79,['varredura de mínimas e retorno ao intervalo'],[],last.high,last.low-.15*atr)
    if m5.regime in ('LATERAL','COMPRESSÃO'):
        if last.low<=support+.5*atr and rejection(last,1):
            add('Extremo de lateralização',1,72,['rejeição de suporte do intervalo'],[],last.high,support-.25*atr)
        if last.high>=resistance-.5*atr and rejection(last,-1):
            add('Extremo de lateralização',-1,72,['rejeição de resistência do intervalo'],[],last.low,resistance+.25*atr)
    if m5.rsi>75 and last.close>e21+2.4*atr and rejection(last,-1):
        add('Reversão por exaustão',-1,75,['RSI extremo','pavio de rejeição após extensão'],['reversão contra fluxo'],last.low,last.high+.2*atr)
    if m5.rsi<25 and last.close<e21-2.4*atr and rejection(last,1):
        add('Reversão por exaustão',1,75,['RSI extremo','pavio de rejeição após extensão'],['reversão contra fluxo'],last.high,last.low-.2*atr)
    if m5.regime=='COMPRESSÃO' and m5.volume_ratio and m5.volume_ratio>1.6:
        side=1 if last.bullish else -1
        add('Expansão de volatilidade',side,73,['compressão prévia','volume expandido'],[],
            last.high if side==1 else last.low, last.low-.2*atr if side==1 else last.high+.2*atr)
    if not proposals:
        return Decision(symbol,'AGUARDAR','Nenhuma estratégia encontra condições de contexto suficientes.',contexts,None,missing,source,ts)
    proposals.sort(key=lambda p:(p.expectancy is not None, p.expectancy if p.expectancy is not None else -999,p.score),reverse=True)
    best=proposals[0]
    if best.score<minimum_score:
        return Decision(symbol,'AGUARDAR',f'Melhor setup {best.strategy} em {best.score}/100, abaixo do mínimo {minimum_score}.',contexts,best,missing,source,ts)
    if missing and not allow_limited_context:
        return Decision(symbol,'AGUARDAR',f'Contexto incompleto: faltam {", ".join(missing)}. Nenhum clique automático.',contexts,best,missing,source,ts)
    if max_spread_points is not None and (spread_points is None or spread_points>max_spread_points):
        return Decision(symbol,'BLOQUEADO','Spread ausente ou excessivo; não operar.',contexts,best,missing,source,ts)
    entry=data.get('M1') or data.get('M5') or []
    side=1 if best.direction=='COMPRAR' else -1
    best.confirmed=bar_trigger(entry,side)
    if not best.confirmed:
        return Decision(symbol,'AGUARDAR',f'{best.strategy}: aguardando confirmação em M1/M5 (vela fechada).',contexts,best,missing,source,ts)
    if abs(last.close-best.trigger)>2*atr:
        best.state='CANCELADO'
        return Decision(symbol,'CANCELADO','Preço afastou-se da zona (> 2 ATR).',contexts,best,missing,source,ts)
    if (side==1 and last.close<best.invalidation) or (side==-1 and last.close>best.invalidation):
        best.state='CANCELADO'
        return Decision(symbol,'CANCELADO','Setup invalidado pela estrutura.',contexts,best,missing,source,ts)
    best.state='CONFIRMADO'
    return Decision(symbol,'ELEGÍVEL',f'{best.strategy} confirmado; revalidar conta DEMO, risco e tempo antes de clicar.',contexts,best,missing,source,ts)
