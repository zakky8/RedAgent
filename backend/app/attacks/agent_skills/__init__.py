"""Agent skills attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []
_imports = [
    ("tool_poisoning", "ToolPoisoning"),
    ("skill_hijacking", "SkillHijacking"),
    ("agent_impersonation", "AgentImpersonation"),
    ("tool_chaining_abuse", "ToolChainingAbuse"),
    ("autonomous_action_abuse", "AutonomousActionAbuse"),
    ("skill_enumeration", "SkillEnumeration"),
    ("memory_skill_injection", "MemorySkillInjection"),
]
for module, cls in _imports:
    try:
        import importlib
        m = importlib.import_module(f".{module}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
