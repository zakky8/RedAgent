"""Purple team attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("red_blue_sim", "RedBlueSim"),
    ("collaborative_exercise", "CollaborativeExercise"),
    ("defense_gap_analysis", "DefenseGapAnalysis"),
    ("attack_simulation_replay", "AttackSimulationReplay"),
    ("threat_hunt_assist", "ThreatHuntAssist"),
]
import importlib
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
