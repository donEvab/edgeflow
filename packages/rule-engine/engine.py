"""
RuleEngine — orchestrator yang menjalankan satu set Rule (dari strategy config)
terhadap context data, menghasilkan checklist + score + rekomendasi akhir.

TODO (Phase 4):
  - Load strategy config (JSON) → list[Rule]
  - Jalankan evaluate_rule() untuk tiap rule
  - Agregasi: semua mandatory rule harus TRUE, hitung total score
  - Return SignalCandidate-compatible output (lihat docs/Architecture.md §3.4)
"""

from typing import Any, Dict, List
from .rule import Rule


class RuleEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("RuleEngine.run() akan diimplementasikan di Phase 4 — lihat docs/Roadmap.md")
