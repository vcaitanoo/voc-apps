from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal
import time

TIMEFRAMES = ('H4', 'H1', 'M15', 'M5', 'M1')

@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    closed: bool = True

    def __post_init__(self):
        if self.high < max(self.open, self.close, self.low) or self.low > min(self.open, self.close, self.high):
            raise ValueError('OHLC inválido')

    @property
    def body(self): return abs(self.close - self.open)
    @property
    def range(self): return self.high - self.low
    @property
    def bullish(self): return self.close > self.open
    @property
    def upper_wick(self): return self.high - max(self.open, self.close)
    @property
    def lower_wick(self): return min(self.open, self.close) - self.low

@dataclass
class Context:
    timeframe: str
    regime: str = 'SEM DADOS'
    direction: int = 0
    ema9: float = 0.0
    ema21: float = 0.0
    ema50: float = 0.0
    ema200: float = 0.0
    rsi: float = 50.0
    adx: float = 0.0
    atr: float = 0.0
    bb_width: float = 0.0
    volume_ratio: float | None = None
    slope: float = 0.0
    structure: str = 'INDEFINIDA'
    n: int = 0
    last_price: float = 0.0
    factors: list[str] = field(default_factory=list)

@dataclass
class Candidate:
    symbol: str
    direction: Literal['COMPRAR', 'VENDER']
    strategy: str
    regime: str
    score: int
    reasons: list[str]
    objections: list[str]
    trigger: float
    invalidation: float
    expires_at: int
    created_at: int
    entry_tf: str
    confirmed: bool = False
    state: str = 'AGUARDANDO'
    expectancy: float | None = None
    sample_size: int = 0

@dataclass
class Decision:
    symbol: str
    status: str
    explanation: str
    contexts: dict[str, Context] = field(default_factory=dict)
    candidate: Candidate | None = None
    missing_timeframes: list[str] = field(default_factory=list)
    source: str = 'SCREEN'
    generated_at: int = field(default_factory=lambda: int(time.time()))

@dataclass
class RiskVerdict:
    allowed: bool
    reason: str
    stake: float
    risk_eur: float
    exposure_pct: float

@dataclass
class Settings:
    symbol: str = 'EURUSD'
    source: str = 'SCREEN'
    timeframe: str = 'M5'
    min_score: int = 78
    balance: float = 100.0
    risk_pct: float = 1.0
    min_stake: float = 1.0
    expiry_min: int = 5
    max_daily_loss_pct: float = 3.0
    target_daily_pct: float = 2.0
    max_daily_entries: int = 8
    demo_clicks_enabled: bool = False
    allow_single_tf_demo: bool = False
    mt5_symbol: str = 'EURUSD'
    tesseract_path: str = ''
    calibration: dict = field(default_factory=dict)
