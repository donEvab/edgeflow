from abc import ABC, abstractmethod
from packages.shared.types import SignalCandidate, DisciplineCheckResult


class DisciplineEngine(ABC):
    @abstractmethod
    def check(self, user_id: str, signal: SignalCandidate) -> DisciplineCheckResult:
        raise NotImplementedError