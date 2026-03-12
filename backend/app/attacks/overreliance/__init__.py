"""Overreliance on AI attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("blind_trust_exploit", "BlindTrustExploit"),
    ("human_in_loop_bypass", "HumanInLoopBypass"),
    ("authoritative_false", "AuthoritativeFalse"),
    ("automation_bias_exploit", "AutomationBiasExploit"),
    ("ai_authority_abuse", "AIAuthorityAbuse"),
]
import importlib
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
