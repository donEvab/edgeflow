from abc import ABC, abstractmethod
from typing import Any, Dict, List
from packages.shared.types import NormalizedCandle, SignalCandidate


class StrategyPlugin(ABC):
    id: str
    version: str
    required_timeframes: List[str]

    @abstractmethod
    def detect(self, market_data: Dict[str, List[NormalizedCandle]]) -> List[SignalCandidate]:
        raise NotImplementedError

    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        raise NotImplementedError