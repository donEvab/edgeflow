from abc import ABC, abstractmethod
from packages.shared.types import RiskCalculation


class RiskEngine(ABC):
    @abstractmethod
    def calculate_position_size(self, balance: float, risk_percent: float, entry_price: float, stop_loss_price: float) -> RiskCalculation:
        raise NotImplementedError

    @abstractmethod
    def check_daily_limit(self, user_id: str) -> bool:
        raise NotImplementedError