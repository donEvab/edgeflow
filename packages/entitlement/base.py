from abc import ABC, abstractmethod


class EntitlementService(ABC):
    @abstractmethod
    def has_access(self, user_id: str, market: str, strategy_id: str) -> bool:
        raise NotImplementedError