from dataclasses import dataclass, field
from typing import Any, Literal, Optional, List


@dataclass
class Rule:
    id: str
    type: Literal["comparison", "composite"]
    mandatory: bool = True
    score_weight: int = 0
    operator: Optional[str] = None
    left: Optional[str] = None
    right: Optional[Any] = None
    logical_operator: Optional[Literal["AND", "OR", "NOT"]] = None
    conditions: List["Rule"] = field(default_factory=list)