"""
Evaluator — menjalankan satu Rule terhadap context data (indicator values).

TODO (Phase 4):
  - Implementasi operator: >, <, >=, <=, ==, !=
  - Implementasi composite: AND, OR, NOT (nested)
  - Return (passed: bool, reason: str) untuk explainability
    (lihat Rule Philosophy — docs/Strategy-Specification.md §1)
"""

from typing import Any, Dict, Tuple
from .rule import Rule


def evaluate_rule(rule: Rule, context: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Evaluasi satu rule terhadap context (misal: {"close": 2350.1, "ema200": 2340.5}).

    Returns:
        (passed, reason) — reason wajib diisi terutama saat passed=False,
        supaya user tahu kenapa entry ditolak.
    """
    raise NotImplementedError("Rule Engine akan diimplementasikan di Phase 4 — lihat docs/Roadmap.md")
