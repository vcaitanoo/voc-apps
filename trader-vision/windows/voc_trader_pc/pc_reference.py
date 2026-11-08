"""Optional operator-reviewed layout proposal for the demonstrated 1366x768 PC.

This is NOT a blind calibration and never enables automatic trading. The
selected asset, displayed stake, URL, DEMO status and actual buttons must
still pass fresh screen checks on every order.
"""
from __future__ import annotations
from copy import deepcopy

WIDTH=1366
HEIGHT=768
# x0,y0,x1,y1; upper header is excluded from candle pixels.
SUGGESTED_ROIS={
    "chart":[145,290,855,694],
    "account":[1126,160,1218,185],
    "balance":[1118,185,1217,211],
    "address":[152,43,1034,81],
    "asset":[444,164,566,211],
    "stake":[952,343,1031,378],
    "expiry":[949,254,1045,286],
    # Price tag moves vertically; this is an entire vertical SEARCH CORRIDOR.
    "countdown":[861,289,944,694],
    "buy":[945,538,1049,621],
    "sell":[945,625,1049,708],
}


def recommended(frame):
    if frame is None or len(frame.shape)!=3:
        return None,"Captura de tela inválida"
    h,w=frame.shape[:2]
    if (w,h)!=(WIDTH,HEIGHT):
        return None,f"Tela {w}x{h}: modelo somente para 1366x768. Calibre manualmente."
    from .screen import button_color_check
    if not button_color_check(frame,SUGGESTED_ROIS["buy"],"BUY"):
        return None,"Comprar não corresponde à imagem de referência."
    if not button_color_check(frame,SUGGESTED_ROIS["sell"],"SELL"):
        return None,"Vender não corresponde à imagem de referência."
    return {"monitor":1,"dimensions":[w,h],
            "rois":deepcopy(SUGGESTED_ROIS)},"Proposta de calibração: revise as 10 regiões antes de salvar."
