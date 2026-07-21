import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from packages.rule_engine.engine import RuleEngineInterface
from packages.scoring.base import ScoringEngine
from packages.risk_engine.base import RiskEngine
from packages.strategies.base import StrategyPlugin
from packages.discipline_engine.base import DisciplineEngine
from packages.entitlement.base import EntitlementService


@pytest.mark.parametrize("abstract_class", [
    RuleEngineInterface,
    ScoringEngine,
    RiskEngine,
    DisciplineEngine,
    EntitlementService,
])
def test_cannot_instantiate_abstract_class_directly(abstract_class):
    with pytest.raises(TypeError):
        abstract_class()