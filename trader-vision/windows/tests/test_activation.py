"""Regression: the v0.1.1 checkbox was visually armed but the executor Event was OFF.
No Tk window or broker is started in these tests.
"""
import threading
from types import SimpleNamespace
from voc_trader_pc.gui import TraderApp
from voc_trader_pc.models import Settings


class Flag:
    def __init__(self, value):self.value=value
    def get(self):return self.value
    def set(self,value):self.value=value


class Label:
    def __init__(self):self.text=''
    def set(self,txt):self.text=txt


def fake_app(*,selected=True,calibrated=True,source='SCREEN'):
    app=TraderApp.__new__(TraderApp)
    app.demo=Flag(selected)
    app.demo_event=threading.Event()
    app.settings=Settings(source=source)
    if calibrated:app.settings.calibration={'monitor':1,'rois':{'chart':[1,1,200,200]}}
    app._read_settings=lambda:app.settings
    app.thread=None
    app.root=object()
    app.status=Label()
    app.messages=[]
    app._log=app.messages.append
    app.start=lambda:app.messages.append('START_OBSERVATION')
    return app


def test_arming_activates_actual_executor_and_starts_observation(monkeypatch):
    from voc_trader_pc import gui
    monkeypatch.setattr(gui.messagebox,'askyesno',lambda *args,**kwargs:True)
    app=fake_app()
    app._armed()
    assert app.demo.get()
    assert app.demo_event.is_set(), 'VC0.1.1 regression: checkbox ON but executor Event remained OFF'
    assert 'START_OBSERVATION' in app.messages
    assert 'MONITORANDO' in app.status.text


def test_unarming_clears_executor(monkeypatch):
    app=fake_app(selected=False)
    app.demo_event.set()
    app._armed()
    assert not app.demo_event.is_set()


def test_rejected_permission_never_arms(monkeypatch):
    from voc_trader_pc import gui
    monkeypatch.setattr(gui.messagebox,'askyesno',lambda *args,**kwargs:False)
    app=fake_app()
    app._armed()
    assert not app.demo.get()
    assert not app.demo_event.is_set()
    assert 'START_OBSERVATION' not in app.messages


def test_uncalibrated_screen_never_arms(monkeypatch):
    from voc_trader_pc import gui
    monkeypatch.setattr(gui.messagebox,'showwarning',lambda *args,**kwargs:None)
    app=fake_app(calibrated=False)
    app._armed()
    assert not app.demo.get()
    assert not app.demo_event.is_set()


def test_mt5_and_csv_cannot_arm_hezilex_clicks(monkeypatch):
    from voc_trader_pc import gui
    monkeypatch.setattr(gui.messagebox,'showwarning',lambda *args,**kwargs:None)
    for source in ('MT5','CSV'):
        app=fake_app(source=source)
        app._armed()
        assert not app.demo_event.is_set()
        assert not app.demo.get()


def test_risk_stays_blocked_below_broker_minimum():
    from voc_trader_pc.risk import stake_verdict
    result=stake_verdict(32.05,1,1)
    assert not result.allowed
    assert result.risk_eur<=.33
    assert 'excede' in result.reason
