"""ML Privacy attack modules."""
import importlib
from app.attacks.base import BaseAttack
from typing import List, Type
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("membership_inference", "MembershipInferenceAttack"),
    ("model_inversion", "ModelInversionAttack"),
    ("model_stealing", "ModelStealingAttack"),
    ("differential_privacy_bypass", "DifferentialPrivacyBypass"),
    ("gradient_leakage", "GradientLeakageAttack"),
    ("model_unlearning_attack", "ModelUnlearningAttack"),
    ("model_extraction_api", "ModelExtractionAPI"),
]
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
