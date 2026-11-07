import cv2
import numpy as np
from voc_trader_pc.screen import extract_candles,button_color_check


def test_40_candles_in_a_fake_chart_and_no_false_button():
    im=np.full((650,1100,3),(22,16,14),dtype=np.uint8)
    for i in range(40):
        x=80+22*i;y=200+(i%11)*10
        color=(80,195,10) if i%2 else (45,65,232)
        cv2.line(im,(x+6,y-28),(x+6,y+28),color,1)
        cv2.rectangle(im,(x,y-6),(x+12,y+14),color,-1)
    bars=extract_candles(im,(48,100,1010,520))
    assert len(bars)>=35, 'Regression: old reader merged candles or returned 0'
    assert not button_color_check(im,(30,530,400,620),'BUY')
