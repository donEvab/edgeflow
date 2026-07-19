"""
EdgeFlow Rule Engine — generic, market-agnostic, strategy-agnostic rule evaluator.

Referensi kontrak: docs/Strategy-Specification.md §7 dan docs/Architecture.md §3.3

Implementasi penuh: Roadmap Phase 4.
File ini baru berisi kontrak interface, belum implementasi.
"""

from .engine import RuleEngine  # noqa: F401
from .rule import Rule  # noqa: F401
from .evaluator import evaluate_rule  # noqa: F401
