from .base import Indicator
from typing import Any, Dict, List
from packages.shared.types import NormalizedCandle


class SwingIndicator(Indicator):
    def compute(self, candles: List[NormalizedCandle], params: Dict[str, Any]) -> Any:
        raise NotImplementedError("Diimplementasikan di Roadmap Phase 3")