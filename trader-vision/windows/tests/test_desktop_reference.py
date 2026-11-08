"""Safety regression: 1366x768 desktop Hezilex reference from the real layout.

The reference is only a suggestion with manual approval, never a blind click
configuration. The sample screenshot is NOT checked in to preserve privacy.
"""
import numpy as np
from voc_trader_pc.desktop_layout import (
    REFERENCE_WIDTH,REFERENCE_HEIGHT,DESKTOP_REFERENCE,
    reference_for_dimensions,preset_matches_frame,desktop_diagnostics,asset_matches,
)


def test_desktop_reference_has_all_ten_safe_regions():
    preset=reference_for_dimensions(1366,768)
    required={"chart","account","balance","address","asset",
              "stake","expiry","countdown","buy","sell"}
    assert set(preset["rois"])==required
    assert preset["dimensions"]==[1366,768]
    for name,(x0,y0,x1,y1) in preset["rois"].items():
        assert 0<=x0<x1<=1366 and 0<=y0<y1<=768, name
    assert preset["rois"]["buy"][1] < preset["rois"]["sell"][1]
    assert preset["rois"]["countdown"][0] < preset["rois"]["buy"][0]
    preset["rois"]["buy"][0]=0
    assert DESKTOP_REFERENCE["buy"][0]==945 # no mutability leak


def test_other_resolution_requires_manual_calibration():
    import pytest
    with pytest.raises(ValueError):
        reference_for_dimensions(1920,1080)
    with pytest.raises(ValueError):
        reference_for_dimensions(1365,768)


def test_preset_requires_actual_buttons_at_expected_positions():
    img=np.zeros((768,1366,3),dtype=np.uint8)
    assert not preset_matches_frame(img)[0]
    # BGR green + red, matching screenshot, on BOTH buttons.
    x0,y0,x1,y1=DESKTOP_REFERENCE["buy"]
    img[y0:y1,x0:x1]=(60,182,64)
    x0,y0,x1,y1=DESKTOP_REFERENCE["sell"]
    img[y0:y1,x0:x1]=(53,76,225)
    ok,reason=preset_matches_frame(img)
    assert ok,reason
    assert not preset_matches_frame(img[:700])[0]


def test_diagnostics_warn_missing_60_closed_and_wrong_asset_and_risk():
    alerts=desktop_diagnostics(
        symbol="EURUSD",observed_asset="BNBCRYPTO",candles=35,
        balance=33.08,stake=5.00,max_risk_pct=1.0)
    assert any("34/60" in msg for msg in alerts)
    assert any("EURUSD" in msg and "BNB" in msg for msg in alerts)
    assert any("€5.00" in msg and "€0.33" in msg for msg in alerts)
    assert asset_matches("BNB","BNB Crypto")
    assert not asset_matches("EURUSD","BNB")
    assert not asset_matches("","BNB")
    assert not desktop_diagnostics(
        "BNB","BNB Crypto",candles=90,balance=150.0,
        stake=1.0,max_risk_pct=1.0)


def test_observed_asset_must_not_be_auto_converted_into_trading_setting():
    import inspect
    from voc_trader_pc.calibration import CalibrationWindow
    code=inspect.getsource(CalibrationWindow.apply_desktop_reference)
    assert "askyesno" in code
    assert "preset_matches_frame" in code
    assert "self.settings.symbol" not in code
