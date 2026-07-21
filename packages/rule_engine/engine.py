from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .rule import Rule


class RuleEngineInterface(ABC):
    @abstractmethod
    def load_config(self, config: Dict[str, Any]) -> List[Rule]:
        raise NotImplementedError

    @abstractmethod
    def run(self, rules: List[Rule], context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError