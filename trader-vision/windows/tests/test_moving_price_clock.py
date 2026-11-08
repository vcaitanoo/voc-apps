"""Regression: Hezilex price clock moves with candles and is never expiry.

Synthetic frames retain the color and dimensions of the user-supplied
1366x768 PC capture. No user screenshot or account data are checked in.
"""
import cv2
import numpy as np
from voc_trader_pc.screen_clock import moving_price_tag,read_price_tag_clock
from voc_trader_pc.pc_reference import recommended,SUGGESTED_ROIS
from voc_trader_pc.risk import stake_verdict
from voc_trader_pc.monitor_journal import MonitorJournal


def fake_screen(label_y,*,color="RED"):
    img=np.zeros((768,1366,3),dtype=np.uint8)
    # The upper expiry timer is NOT inside the dynamically searched axis.
    cv2.putText(img,"03:14",(999,245),cv2.FONT_HERSHEY_SIMPLEX,.5,
                (255,255,255),1)
    cv2.rectangle(img,(868,label_y),(937,label_y+32),
                  (65,77,255) if color=="RED" else (45,191,12),-1)
    # Mark the trade buttons at exactly the user's screenshot geometry.
    cv2.rectangle(img,(945,538),(1048,620),(63,178,80),-1)
    cv2.rectangle(img,(945,625),(1048,707),(52,78,223),-1)
    return img


def test_timer_moves_up_and_down_with_price():
    for y in (300,417,457,620):
        frame=fake_screen(y)
        tag=moving_price_tag(frame,SUGGESTED_ROIS["chart"],
                             SUGGESTED_ROIS["countdown"],
                             SUGGESTED_ROIS["buy"])
        assert tag is not None
        assert abs(tag.rect[1]-y)<=3
        assert tag.color=="VERMELHO"
        seen=[]
        def ocr(image):
            seen.append(image.shape)
            return "03:15"
        assert read_price_tag_clock(frame,tag,ocr,300)==195
        assert seen and len(seen)>=2


def test_missing_colored_label_never_falls_back_to_expiry():
    image=fake_screen(417)
    image[410:460,840:940]=0
    assert moving_price_tag(image,SUGGESTED_ROIS["chart"],
                            SUGGESTED_ROIS["countdown"],
                            SUGGESTED_ROIS["buy"]) is None


def test_conflicting_ocr_must_not_authorize_trade():
    img=fake_screen(417)
    tag=moving_price_tag(img,SUGGESTED_ROIS["chart"],
                         SUGGESTED_ROIS["countdown"],SUGGESTED_ROIS["buy"])
    turns=iter(["03:15","04:47","03:15","04:47","03:15","04:47"])
    # 3 votes each: tie signals are inconsistent, fail closed.
    assert read_price_tag_clock(img,tag,lambda frame:next(turns),300) is None


def test_user_must_review_layout_before_arming():
    image=fake_screen(417)
    template,msg=recommended(image)
    assert template and len(template["rois"])==10
    assert template["rois"]["countdown"][3]>690
    assert not recommended(image[:700])[0]
    assert template["rois"]["buy"][2]<template["rois"]["sell"][2]+1


def test_33_eur_balance_and_minimum_value_five_must_block():
    verdict=stake_verdict(33.08,1,5)
    assert not verdict.allowed
    assert verdict.risk_eur<=.34


def test_overnight_monitor_has_status_not_fake_broker_trades(tmp_path):
    journal=MonitorJournal(tmp_path/"overnight.csv")
    assert journal.append({"estado":"AGUARDANDO","cliques_armados":False,
        "velas_fechadas":58,"segundos_relogio":195,
        "bloqueio":"Risco excede 1%","wins_confirmados":0,
        "losses_confirmados":0},force=True)
    import csv
    with journal.path.open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f,delimiter=";"))
    assert rows[0]["segundos_relogio"]=="195"
    assert rows[0]["wins_confirmados"]=="0"
    assert rows[0]["bloqueio"]=="Risco excede 1%"
