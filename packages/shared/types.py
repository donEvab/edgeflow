"""
Type definitions bersama, mengikuti kontrak di docs/Architecture.md.
"""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class NormalizedCandle:
    market: Literal["crypto", "forex"]
    provider: str
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: str


@dataclass
class SignalCandidate:
    strategy_id: str
    version: str
    market: str
    symbol: str
    direction: Literal["BUY", "SELL"]
    score: int
    recommendation: str
    entry_zone: float
    stop_loss: float
    take_profit: float
    timestamp: str
