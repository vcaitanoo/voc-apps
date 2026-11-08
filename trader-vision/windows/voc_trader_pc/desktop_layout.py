"""Desktop Hezilex 1366x768 reference layout from an actual user screenshot.

Positions are only a CALIBRATION PROPOSAL. The user must explicitly review and
approve the highlighted boxes. Screenshots from a different resolution or with
moved controls are rejected. Color checks and fresh OCR still gate every DEMO
click, and the configured asset must match the active asset.
"""
from __future__ import annotations

from copy import deepcopy

REFERENCE_WIDTH=1366
REFERENCE_HEIGHT=768
DESKTOP_REFERENCE={
    # x0,y0,x1,y1 in full monitor pixels; chart excludes price labels,
    # sidebars and the orange bonus bar.
    "chart":[145,292,830,687],
    "account":[1124,162,1215,185],
    "balance":[1118,185,1216,210],
    "address":[154,44,1033,80],
    # The *selected* tab shows BNB; the sidebar is an unrelated asset list.
    "asset":[445,163,567,211],
    "stake":[958,347,1030,374],
    "expiry":[951,257,1044,282],
    # Use green candle price-label countdown, NOT expiry timer at top.
    "countdown":[869,457,938,476],
    "buy":[945,538,1049,621],
    "sell":[945,625,1049,707],
}


def reference_for_dimensions(width:int,height:int)->dict:
    if (int(width),int(height))!=(REFERENCE_WIDTH,REFERENCE_HEIGHT):
        raise ValueError(
            f"Modelo guiado disponível apenas em {REFERENCE_WIDTH}x{REFERENCE_HEIGHT}; "
            f"esta tela é {width}x{height}. Use seleção manual."
        )
    return {"monitor":1,
            "dimensions":[REFERENCE_WIDTH,REFERENCE_HEIGHT],
            "rois":deepcopy(DESKTOP_REFERENCE)}


def preset_matches_frame(frame)->tuple[bool,str]:
    if frame is None or len(frame.shape)!=3:
        return False,"Captura inválida"
    height,width=frame.shape[:2]
    if (width,height)!=(REFERENCE_WIDTH,REFERENCE_HEIGHT):
        return False,f"Resolução {width}x{height} diferente de 1366x768"
    from .screen import button_color_check
    if not button_color_check(frame,DESKTOP_REFERENCE["buy"],"BUY"):
        return False,"Botão verde mudou de posição; calibre manualmente"
    if not button_color_check(frame,DESKTOP_REFERENCE["sell"],"SELL"):
        return False,"Botão vermelho mudou de posição; calibre manualmente"
    return True,"Layout visual compatível com a referência; revisão manual obrigatória"


def asset_matches(configured:str,observed:str)->bool:
    import re
    norm=lambda value: re.sub(r"[^A-Z0-9]","",str(value).upper())
    x=norm(configured);y=norm(observed)
    return bool(x and y and (x==y or y.startswith(x+"CRYPTO") or
                            y.startswith(x+"FOREX")))


def desktop_diagnostics(symbol:str,observed_asset:str,candles:int,
                        balance:float|None,stake:float|None,
                        max_risk_pct:float,min_required:int=60)->list[str]:
    alerts=[]
    # No future candles or fake signals: we require enough closed bars.
    closed=max(0,int(candles)-1)
    if closed<min_required:
        alerts.append(f"ZOOM: {closed}/{min_required} velas fechadas. Afaste o zoom do gráfico.")
    if not asset_matches(symbol,observed_asset):
        alerts.append(f"ATIVO: configurado {symbol}, mas tela mostra {observed_asset or 'ilegível'}. Ajuste o campo Ativo.")
    if balance is None:
        alerts.append("SALDO: leitura OCR não confirmada. Sem autorização de toque.")
    elif stake is not None:
        cap=max(0.0,float(balance)*min(1.0,max(0.0,float(max_risk_pct)))/100.0)
        if stake>cap+0.00001:
            alerts.append(f"RISCO: entrada €{stake:.2f} supera limite €{cap:.2f} (máx. 1%).")
    return alerts
