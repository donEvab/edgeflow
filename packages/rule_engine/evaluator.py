from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from .rule import Rule


class RuleEvaluator(ABC):
    @abstractmethod
    def evaluate(self, rule: Rule, context: Dict[str, Any]) -> Tuple[bool, str]:
        raise NotImplementedError