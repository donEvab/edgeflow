from dataclasses import dataclass, field
from typing import Literal, Optional, List, Dict, Any


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
class RuleResult:
    rule_id: str
    passed: bool
    reason: Optional[str] = None
    score_contribution: int = 0


@dataclass
class SignalCandidate:
    strategy_id: str
    strategy_version: str
    market: Literal["crypto", "forex"]
    symbol: str
    direction: Literal["BUY", "SELL"]
    checklist: List[RuleResult] = field(default_factory=list)
    score: int = 0
    recommendation: str = ""
    entry_zone: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: str = ""


@dataclass
class DisciplineCheckResult:
    allowed: bool
    reason: Optional[str] = None
    locked_until: Optional[str] = None


@dataclass
class RiskCalculation:
    lot_size: float
    risk_amount: float
    potential_profit: float
    max_drawdown: float


@dataclass
class OrderResult:
    order_id: str
    status: Literal["filled", "pending", "rejected"]
    filled_price: Optional[float] = None
    message: Optional[str] = None