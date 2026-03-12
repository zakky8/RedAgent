"""Quantum cryptography attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("hndl_scan", "HNDLScan"),
    ("weak_crypto", "WeakCryptography"),
    ("quantum_key_harvest", "QuantumKeyHarvest"),
    ("post_quantum_bypass", "PostQuantumBypass"),
    ("grover_attack_assist", "GroverAttackAssist"),
]
import importlib
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
