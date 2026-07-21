from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any
from packages.shared.types import NormalizedCandle, OrderResult


class ExchangeAdapter(ABC):
    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def subscribe_candles(self, symbol: str, timeframe: str) -> AsyncIterator[NormalizedCandle]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_order_book(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def place_order(self, params: Dict[str, Any]) -> OrderResult:
        raise NotImplementedError

    @abstractmethod
    async def get_balance(self) -> float:
        raise NotImplementedError