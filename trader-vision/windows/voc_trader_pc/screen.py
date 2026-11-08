from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable
import re, time
import numpy as np
import cv2
from .models import Candle
from .screen_clock import moving_price_tag,read_price_tag_clock


@dataclass
class ObservedScreen:
    candles: list[Candle]
    account_demo: bool
    account_real: bool
    balance: float | None
    stake: float | None
    expiry: int | None
    clock_remaining: int | None
    url_verified: bool
    buttons_visible: bool
    asset_text: str
    blockers: list[str]
    frame: np.ndarray


def parse_money(s:str)->float|None:
    values=re.findall(r'(?:€\s*)?([0-9]{1,6}(?:[.\s][0-9]{3})*[,\.][0-9]{2})(?![0-9])',s)
    for val in values:
        if ',' in val and '.' in val:val=val.replace('.','').replace(',','.')
        elif ',' in val:val=val.replace(',','.')
        try:return float(val.replace(' ',''))
        except ValueError:pass
    return None


def parse_timer(s:str, max_seconds=3600)->int|None:
    for m in re.finditer(r'(?<!\d)(\d{1,2}):([0-5]\d)(?!\d)',s):
        seconds=int(m.group(1))*60+int(m.group(2))
        if seconds<=max_seconds:return seconds
    return None


def parse_expiry(s:str)->int|None:
    m=re.search(r'(?<!\d)(\d{1,3})\s*(?:min(?:utos?|utes?)?|m)(?!\w)',s.lower())
    return int(m.group(1)) if m else None


def extract_candles(image:np.ndarray,roi:list[int]|tuple[int,int,int,int],timeframe_minutes:int=5,
                    timestamp:int|None=None)->list[Candle]:
    """Extract chart-colored candles from one *visible* TradingView screenshot.

    Prices are NORMALIZED PIXEL COORDINATES, not broker OHLC quotes.
    Therefore do not mix with MT5 prices or retain across zoom/resize.
    All shapes require calibration against actual PC screenshots.
    """
    if image is None or len(image.shape)!=3:return []
    H,W=image.shape[:2];x0,y0,x1,y1=map(int,roi)
    x0=max(0,x0);y0=max(0,y0);x1=min(W,x1);y1=min(H,y1)
    if x1-x0<120 or y1-y0<110:return []
    crop=image[y0:y1,x0:x1,:3]
    hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
    # TradingView green/red, avoid white candlesticks, orange promo banners.
    green=cv2.inRange(hsv,(34,70,60),(98,255,255))
    red=cv2.bitwise_or(cv2.inRange(hsv,(0,75,75),(10,255,255)),cv2.inRange(hsv,(169,75,75),(179,255,255)))
    h,w=green.shape
    mask=((green>0)|(red>0)).astype('uint8')
    # Remove single horizontal price lines. These otherwise merge 20+ candles.
    horizontal=mask.sum(axis=1)>w*.32
    mask[horizontal,:]=0
    green[horizontal,:]=0;red[horizontal,:]=0
    occupied=mask.sum(axis=0)
    # Candles in a chart often have a 1px wick; require at least 3 vertical pixels.
    active=occupied>=3
    ranges=[];start=None
    for i,v in enumerate(list(active)+[False]):
        if v and start is None:start=i
        if not v and start is not None:
            if i-start<=max(40,int(w*.065)):ranges.append((start,i))
            start=None
    result=[]
    now=int(time.time()) if timestamp is None else int(timestamp)
    for l,r in ranges:
        if r-l<1:continue
        g=int((green[:,l:r]>0).sum());rd=int((red[:,l:r]>0).sum())
        if max(g,rd)<7:continue
        colored=(green[:,l:r]>0) if g>=rd else (red[:,l:r]>0)
        rows=colored.sum(axis=1)
        ys=np.flatnonzero(rows>0)
        if len(ys)<3:continue
        span=r-l
        bodies=np.flatnonzero(rows>=max(2,int(np.ceil(span*.38))))
        if bodies.size<2:
            bodies=np.flatnonzero(rows>=1)
        if bodies.size<2:continue
        top=int(ys[0]);bottom=int(ys[-1]);body_top=int(bodies[0]);body_bottom=int(bodies[-1])
        bullish=g>=rd
        # y axis reversed: higher pixel = lower price. Time invariant only WITHIN THIS SCREENSHOT.
        toprice=lambda yy:1.0-float(yy)/float(h)
        high=toprice(top);low=toprice(bottom)
        op=toprice(body_bottom if bullish else body_top)
        close=toprice(body_top if bullish else body_bottom)
        if low<=min(op,close) and high>=max(op,close):
            result.append(Candle(now-(len(ranges)-len(result)-1)*timeframe_minutes*60,op,high,low,close,0.0,True))
    # Last candle is still forming. Caller must never use it as a confirmed historical signal.
    if result:
        c=result[-1];result[-1]=Candle(c.timestamp,c.open,c.high,c.low,c.close,c.volume,False)
    return result


def button_color_check(frame:np.ndarray,roi:list[int],side:str)->bool:
    h,w=frame.shape[:2];x0,y0,x1,y1=map(int,roi)
    x0=max(0,x0);y0=max(0,y0);x1=min(w,x1);y1=min(h,y1)
    if x1-x0<20 or y1-y0<15:return False
    sample=frame[y0:y1,x0:x1]
    hsv=cv2.cvtColor(sample,cv2.COLOR_BGR2HSV)
    if side=='BUY':mask=cv2.inRange(hsv,(34,85,55),(98,255,255))
    else:mask=cv2.bitwise_or(cv2.inRange(hsv,(0,80,70),(10,255,255)),cv2.inRange(hsv,(170,80,70),(179,255,255)))
    return float((mask>0).mean())>.30


class ScreenObserver:
    REQUIRED=('chart','account','balance','stake','expiry','countdown','address','asset','buy','sell')
    def __init__(self,calibration:dict,tesseract_path:str='',timeframe:int=5):
        self.calibration=calibration
        self.tesseract_path=tesseract_path
        self.timeframe=timeframe
        self._ocr_checked=False
        self._ocr_error=None
    def _check_ocr(self):
        """Report missing Tesseract immediately; chart analysis still runs."""
        if self._ocr_checked:return
        self._ocr_checked=True
        import os,shutil
        from pathlib import Path
        import pytesseract
        supplied=self.tesseract_path.strip().strip('"')
        system=shutil.which('tesseract')
        choices=[supplied,system]
        if os.name=='nt':
            choices.extend([str(Path(os.environ.get('ProgramFiles',r'C:\\Program Files'))/
                                'Tesseract-OCR'/'tesseract.exe'),
                            str(Path(os.environ.get('ProgramFiles(x86)',r'C:\\Program Files (x86)'))/
                                'Tesseract-OCR'/'tesseract.exe')])
        chosen=next((p for p in choices if p and Path(p).is_file()),None)
        if chosen is None:
            self._ocr_error=('TESSERACT NÃO ENCONTRADO: instale Tesseract OCR '
                             'ou indique Tesseract.exe no painel; sem OCR não há toques DEMO.')
            return
        pytesseract.pytesseract.tesseract_cmd=str(chosen)
        try:pytesseract.get_tesseract_version()
        except Exception as exc:
            self._ocr_error=('TESSERACT NÃO INICIA: '+str(exc)[:180]+
                             '. Verifique o campo Tesseract.exe.')
    def capture(self):
        import mss
        with mss.mss() as s:
            monitor=s.monitors[int(self.calibration.get('monitor',1))]
            raw=np.asarray(s.grab(monitor))
            return cv2.cvtColor(raw,cv2.COLOR_BGRA2BGR)
    def read(self,frame:np.ndarray)->ObservedScreen:
        import pytesseract
        self._check_ocr()
        H,W=frame.shape[:2]
        rois=self.calibration.get('rois',{})
        blockers=[f'Calibre: {name}' for name in self.REQUIRED if name not in rois]
        if self._ocr_error:blockers.append(self._ocr_error)
        if self.calibration.get('dimensions') and tuple(self.calibration['dimensions'])!=(W,H):
            blockers.append('Resolução mudou desde a calibração. Recalibre a tela.')
        def crop(name):
            if name not in rois:return None
            x0,y0,x1,y1=map(int,rois[name]);x0=max(0,x0);y0=max(0,y0);x1=min(W,x1);y1=min(H,y1)
            if x1<=x0 or y1<=y0:return None
            return frame[y0:y1,x0:x1]
        def ocr(name,psm=6):
            if self._ocr_error:return ''
            patch=crop(name)
            if patch is None:return ''
            img=cv2.resize(patch,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
            try:return pytesseract.image_to_string(img,config=f'--psm {psm}',timeout=6).strip()
            except Exception as e:
                blockers.append(f'OCR {name} falhou: {type(e).__name__}');return ''
        account=ocr('account').lower()
        url=ocr('address',7).lower().replace(' ','')
        asset_text=ocr('asset',7).strip().upper().replace(' ','')
        if not asset_text:blockers.append('Nome do ativo ilegível')
        observed_stake=parse_money(ocr('stake',7))
        observed_expiry=parse_expiry(ocr('expiry',7))
        current_balance=parse_money(ocr('balance',7))
        # Hezilex price label moves with the quote; a static countdown Y is
        # invalid after any price change. Never substitute the expiration
        # countdown in the upper-right trade panel for the candle clock.
        tag=moving_price_tag(frame,rois.get('chart'),rois.get('countdown'),
                             rois.get('buy'))
        seconds=None
        if tag is not None and not self._ocr_error:
            import pytesseract
            def digits(image):
                return pytesseract.image_to_string(
                    image,config='--psm 7 -c tessedit_char_whitelist=0123456789:',
                    timeout=4)
            seconds=read_price_tag_clock(frame,tag,digits,self.timeframe*60)
        if tag is None:
            blockers.append('Etiqueta colorida do preço não localizada; não usar temporizador de Expiração')
        elif seconds is None:
            blockers.append('Relógio MÓVEL da vela não confirmado por OCR; sem toque')
        is_demo=bool(re.search(r'(conta\s*demo|demo\s*account)',account))
        is_real=bool(re.search(r'(conta\s*real|real\s*account)',account))
        url_ok='hezilex.com' in url and ('traderoom' in url or 'trade' in url)
        if not is_demo or is_real:blockers.append('Conta Demo não verificada (ou Conta Real detectada)')
        if not url_ok:blockers.append('URL da Hezilex não verificada')
        if observed_stake is None:blockers.append('Valor de entrada ilegível')
        if observed_expiry is None:blockers.append('Expiração ilegível')
        if current_balance is None:blockers.append('Saldo DEMO ilegível')
        if seconds is None and tag is not None:blockers.append('Cronômetro da vela ilegível')
        btns=(button_color_check(frame,rois['buy'],'BUY') and button_color_check(frame,rois['sell'],'SELL')) if 'buy' in rois and 'sell' in rois else False
        if not btns:blockers.append('Botões Comprar/Vender parcialmente ocultos')
        bars=extract_candles(frame,rois['chart'],self.timeframe) if 'chart' in rois else []
        return ObservedScreen(bars,is_demo,is_real,current_balance,observed_stake,observed_expiry,seconds,url_ok,btns,asset_text,blockers,frame)


def foreground_is_browser()->bool:
    """Fail closed: don't send an accessibility-like click into an arbitrary app."""
    try:
        import ctypes
        import psutil
        user32=ctypes.windll.user32
        hwnd=user32.GetForegroundWindow()
        if not hwnd:return False
        pid=ctypes.c_ulong(0)
        user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
        return psutil.Process(pid.value).name().lower() in ('chrome.exe','msedge.exe','brave.exe')
    except Exception:return False


def safe_click(observer:ScreenObserver,screen:ObservedScreen,calibration:dict,side:str,
               amount:float,expiry_min:int,expected_symbol:str,screen_monitor_index:int=1):
    """Re-capture and re-validate the broker screen immediately before any demo click.

    No real-money account. No click when the browser loses focus, when OCR fails,
    when the selected asset changes, or after a candle has left its first 15 s.
    """
    if not foreground_is_browser():raise RuntimeError('Chrome/Edge/Brave não está em primeiro plano')
    latest=observer.read(observer.capture())
    if latest.blockers:raise RuntimeError('; '.join(latest.blockers))
    if not latest.account_demo or latest.account_real or not latest.url_verified:
        raise RuntimeError('Conta Demo / domínio Hezilex não confirmados')
    norm=lambda s:re.sub(r'[^A-Z0-9]','',s.upper())
    if norm(expected_symbol) not in norm(latest.asset_text):
        raise RuntimeError(f'Ativo mudou! Esperado {expected_symbol}; lido {latest.asset_text}')
    if latest.stake is None or abs(latest.stake-amount)>.005:
        raise RuntimeError('Valor DEMO difere do limite de risco calculado')
    if latest.expiry!=expiry_min:raise RuntimeError('Expiração DEMO divergente')
    if not latest.buttons_visible:raise RuntimeError('Botões ocultos')
    total=observer.timeframe*60
    if latest.clock_remaining is None or not(total-15<=latest.clock_remaining<=total-1):
        raise RuntimeError('A janela de entrada no início da vela terminou')
    roi=calibration['rois']['buy' if side=='COMPRAR' else 'sell']
    import mss,pyautogui
    with mss.mss() as s:
        mon=s.monitors[screen_monitor_index]
    x=(int(roi[0])+int(roi[2]))//2+int(mon['left'])
    y=(int(roi[1])+int(roi[3]))//2+int(mon['top'])
    pyautogui.FAILSAFE=True
    pyautogui.click(x=x,y=y,clicks=1,interval=.12)
    return x,y,latest.balance
