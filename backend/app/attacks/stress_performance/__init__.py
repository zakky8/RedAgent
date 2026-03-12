"""Stress and performance attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
import importlib

attack_classes: List[Type[BaseAttack]] = []

_imports = [
    ("surge_load", "SurgeLoad"),
    ("conflicting_input", "ConflictingInput"),
    ("resource_exhaust", "ResourceExhaustAttack"),
    ("concurrent_session_flood", "ConcurrentSessionFlood"),
    ("memory_pressure", "MemoryPressureAttack"),
]
for mod, cls in _imports:
    try:
        m = importlib.import_module(f"app.attacks.stress_performance.{mod}")
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass

__all__ = ["attack_classes"]
