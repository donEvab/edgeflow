from abc import ABC, abstractmethod
from typing import Any, Dict, List
from packages.shared.types import NormalizedCandle


class Indicator(ABC):
    @abstractmethod
    def compute(self, candles: List[NormalizedCandle], params: Dict[str, Any]) -> Any:
        raise NotImplementedError