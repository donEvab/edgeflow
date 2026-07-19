"""
Rule — representasi satu unit aturan sesuai schema di
docs/Strategy-Specification.md §7.

TODO (Phase 4): implementasi penuh, termasuk validasi terhadap JSON schema.
"""

from dataclasses import dataclass, field
from typing import Any, Literal, Optional


@dataclass
class Rule:
    id: str
    type: Literal["comparison", "composite"]
    mandatory: bool = True
    score_weight: int = 0

    # untuk type == "comparison"
    operator: Optional[str] = None
    left: Optional[str] = None
    right: Optional[Any] = None

    # untuk type == "composite"
    logical_operator: Optional[Literal["AND", "OR", "NOT"]] = None
    conditions: list = field(default_factory=list)
