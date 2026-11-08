"""Hezilex moving price label detection for candle-expiry clock.

The price label moves VERTICALLY as the current quote changes.
A fixed Y rectangle loses the timer and may accidentally read the unrelated
expiration countdown in the trade panel. Always search the chart's price axis
with a confined X corridor and require the saturated green/red label.
No guessed clock is ever returned.
"""
from __future__ import annotations
from dataclasses import dataclass
import cv2
import numpy as np
import re


@dataclass(frozen=True)
class PriceTag:
    rect: tuple[int, int, int, int]
    color: str
    coverage: float


def moving_price_tag(frame:np.ndarray, chart_roi, original_clock_roi=None,
                     buy_roi=None)->PriceTag|None:
    if frame is None or len(frame.shape)!=3:return None
    h,w=frame.shape[:2]
    if not chart_roi or len(chart_roi)!=4:return None
    cx0,cy0,cx1,cy1=map(int,chart_roi)
    x0=max(0,cx1-18)
    x1=min(w,cx1+145)
    if original_clock_roi and len(original_clock_roi)==4:
        ox0,oy0,ox1,oy1=map(int,original_clock_roi)
        x0=max(0,min(x0,ox0-8))
        x1=min(w,max(x1,ox1+8))
    if buy_roi and len(buy_roi)==4:
        x1=min(x1,int(buy_roi[0])-3)
    y0=max(0,cy0-45)
    y1=min(h,cy1+5)
    if x1-x0<45 or y1-y0<100:return None
    patch=frame[y0:y1,x0:x1,:3]
    hsv=cv2.cvtColor(patch,cv2.COLOR_BGR2HSV)
    green=cv2.inRange(hsv,(34,105,85),(98,255,255))
    red=cv2.bitwise_or(cv2.inRange(hsv,(0,100,85),(11,255,255)),
                       cv2.inRange(hsv,(168,100,85),(179,255,255)))
    combined=cv2.bitwise_or(green,red)
    closed=cv2.morphologyEx(combined,cv2.MORPH_CLOSE,
                           np.ones((5,7),np.uint8))
    contours,_=cv2.findContours(closed,cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    candidates=[]
    for cnt in contours:
        xx,yy,ww,hh=cv2.boundingRect(cnt)
        if not(46<=ww<=150 and 21<=hh<=75):continue
        if xx+x0<cx1-25:continue
        rectmask=combined[yy:yy+hh,xx:xx+ww]
        coverage=float(np.count_nonzero(rectmask))/float(ww*hh)
        if coverage<.53:continue
        g=int(np.count_nonzero(green[yy:yy+hh,xx:xx+ww]))
        r=int(np.count_nonzero(red[yy:yy+hh,xx:xx+ww]))
        color="VERDE" if g>=r else "VERMELHO"
        score=coverage*ww*hh
        candidates.append((score,PriceTag((x0+xx,y0+yy,x0+xx+ww,y0+yy+hh),
                                          color,coverage)))
    return max(candidates,key=lambda item:item[0])[1] if candidates else None


def read_price_tag_clock(frame:np.ndarray,tag:PriceTag,ocr_callable,
                         max_seconds:int)->int|None:
    """ocr_callable receives the processed image (simple to fake in tests).

    OCR is run ONLY on the bottom of the moving price tag, not on the
    expiration block. Multi-crop recognition improves small white digits.
    """
    x0,y0,x1,y1=tag.rect
    height=y1-y0
    results=[]
    for fraction in (.47,.41,.52):
        top=y0+int(height*fraction)
        patch=frame[top:y1,max(0,x0):x1,:3]
        if patch.size==0:continue
        enlarged=cv2.resize(patch,None,fx=4,fy=4,
                             interpolation=cv2.INTER_CUBIC)
        grey=cv2.cvtColor(enlarged,cv2.COLOR_BGR2GRAY)
        for candidate in (grey,cv2.threshold(grey,170,255,
                                              cv2.THRESH_BINARY)[1]):
            try:
                text=str(ocr_callable(candidate))
            except Exception:
                continue
            for match in re.finditer(r"(?<!\d)(\d{1,2})\s*:\s*([0-5]\d)(?!\d)",
                                     text):
                seconds=int(match.group(1))*60+int(match.group(2))
                if 0<=seconds<=max_seconds:results.append(seconds)
    # Disagreeing OCR reads cannot safely authorize a trade.
    if not results:return None
    counts={}
    for val in results:counts[val]=counts.get(val,0)+1
    value,votes=max(counts.items(),key=lambda item:item[1])
    return value if votes>=2 else None
