"""Classic jailbreak attack modules."""
import importlib
from app.attacks.base import BaseAttack
from typing import List, Type
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("dan", "DANJailbreak"),
    ("aim", "AIMJailbreak"),
    ("grandma", "GrandmaExploit"),
    ("hypothetical", "HypotheticalFraming"),
    ("roleplay", "RoleplayBypass"),
    ("unicode_smuggling", "UnicodeSmuggling"),
]
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
