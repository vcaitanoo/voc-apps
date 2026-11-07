import json
from pathlib import Path
import numpy as np
import pytest
from voc_trader_pc.models import Candle
from voc_trader_pc.indicators import ema,atr,rsi,adx
from voc_trader_pc.engine import context,evaluate,bar_trigger
from voc_trader_pc.journal import Journal
from voc_trader_pc.risk import stake_verdict
from voc_trader_pc.screen import parse_money,parse_timer,parse_expiry,extract_candles,button_color_check
from voc_trader_pc.tracker import DemoTracker


def candles(n=250,side=1):
    result=[];last=1.10
    for i in range(n):
        op=last;close=op+side*.00015+(.00003 if i%7==0 else -.000015)
        result.append(Candle(1700000000+i*300,op,max(op,close)+.00006,min(op,close)-.00005,close,100+i%20))
        last=close
    return result


def test_ema_aligned_per_candle_without_future_data():
    v=[1.,2.,3.,4.,5.,100.]
    e=ema(v,3)
    assert e[2]==pytest.approx(2.25)
    assert e[:5]==ema(v[:5],3)
    assert ema([1.],200)==[1.]


def test_atr_rsi_adx_are_causal():
    b=candles(240)
    for function in (atr,rsi,adx):
        assert function(b)[:200]==pytest.approx(function(b[:200]))
    assert 0<=adx(b)[-1]<=100
    assert 0<=rsi(b)[-1]<=100


def test_risk_is_strict_one_percent():
    v=stake_verdict(32.05,1,1)
    assert not v.allowed and 'excede' in v.reason
    assert stake_verdict(100,1,1).allowed
    assert not stake_verdict(250,1.01,1).allowed
    assert not stake_verdict(200,1,1,day_pnl=-7).allowed
    assert not stake_verdict(200,1,1,day_pnl=5).allowed
    assert not stake_verdict(200,1,1,trades_today=8).allowed


def test_engine_requires_data_and_never_invents_h4():
    o=evaluate('EURUSD',{'M5':candles(250)},source='SCREEN',allow_limited_context=False)
    assert o.status in ('AGUARDAR','SEM DADOS')
    assert 'H4' in o.missing_timeframes
    d={tf:candles(250) for tf in ('H4','H1','M15','M5','M1')}
    o=evaluate('EURUSD',d,source='MT5')
    assert o.status in ('AGUARDAR','ELEGÍVEL','CANCELADO')
    assert len(o.missing_timeframes)==0
    assert o.contexts['H4'].n==250


def test_candle_closed_required():
    b=candles(5)
    b[-1]=Candle(b[-1].timestamp,b[-1].open,b[-1].high,b[-1].low,b[-1].close,100,False)
    assert not bar_trigger(b[:2],1)
    assert context('M5',b).n==4


def test_ocr_parsers():
    assert parse_money('Conta Demo € 32,05')==pytest.approx(32.05)
    assert parse_money('1.234,56')==pytest.approx(1234.56)
    assert parse_timer('00:15')==15
    assert parse_timer('05:48',max_seconds=300) is None
    assert parse_expiry('5 min')==5


def test_vision_fixture_from_user_screenshot():
    import cv2
    file=Path('/mnt/data/41100.jpg')
    if not file.is_file():pytest.skip('User provided photo not locally mounted')
    im=cv2.imread(str(file))
    c=extract_candles(im,(90,455,1040,922))
    assert len(c)>=25, f'The old Android reader returned 0 candles, got {len(c)}'
    assert c[-1].closed is False
    assert button_color_check(im,(16,1168,570,1257),'BUY')
    assert button_color_check(im,(581,1168,1140,1257),'SELL') is False # Panel obscures most of SELL!


def test_trade_tracker_does_not_invent_win(tmp_path):
    ledger=Journal(tmp_path/'journal.jsonl');tracker=DemoTracker(ledger)
    tracker.begin('EURUSD','EMA','TENDENCIA','COMPRAR',100,1,5,now=1000)
    assert tracker.observe(100.9,now=1200)=='AGUARDANDO_EXPIRACAO'
    assert tracker.observe(100.9,now=1305)=='CONFIRMANDO_RESULTADO'
    assert tracker.observe(100.9,now=1310)=='WIN'
    assert ledger.summary()['wins']==1
    assert tracker.observe(100.9,now=1400) is None
    tracker.begin('EURUSD','EMA','TENDENCIA','VENDER',100,1,5,now=2000)
    assert tracker.observe(105,now=2310)=='SALDO_NAO_CONCLUSIVO'
    assert tracker.observe(None,now=2600)=='NAO_CONFIRMADO'
    assert ledger.summary()['wins']==1


def test_historical_expected_value_requires_sample(tmp_path):
    j=Journal(tmp_path/'history.jsonl')
    for k in range(29):
        j.append(dict(type='settlement',timestamp=k,outcome='WIN',pnl=.9,strategy='EMA',regime='LATERAL'))
    assert j.matching_expectancy('EMA','LATERAL')[0] is None
    j.append(dict(type='settlement',timestamp=30,outcome='LOSS',pnl=-1,strategy='EMA',regime='LATERAL'))
    ev,n=j.matching_expectancy('EMA','LATERAL')
    assert n==30 and ev>0
