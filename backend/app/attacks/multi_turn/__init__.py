"""Multi-turn attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("crescendo", "CrescendoAttack"),
    ("linear_jailbreak", "LinearJailbreak"),
    ("escalation_chain", "EscalationChain"),
    ("context_switching", "ContextSwitching"),
    ("false_premise_building", "FalsePremiseBuilding"),
    ("token_budget_exhaustion", "TokenBudgetExhaustion"),
    ("many_shot_jailbreak", "ManyShotJailbreak"),
    ("adaptive_refusal_bypass", "AdaptiveRefusalBypass"),
]
import importlib
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
