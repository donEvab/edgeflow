from abc import ABC, abstractmethod
from typing import List
from packages.shared.types import RuleResult


class ScoringEngine(ABC):
    @abstractmethod
    def calculate_score(self, checklist: List[RuleResult]) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_recommendation(self, score: int) -> str:
        raise NotImplementedError