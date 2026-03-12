"""Long-game APT attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []
_imports = [
    ("slow_poison_campaign", "SlowPoisonCampaign"),
    ("trust_building_exploit", "TrustBuildingExploit"),
    ("persona_drift_attack", "PersonaDriftAttack"),
    ("waterhole_prompt", "WaterholePrompt"),
    ("apt_recon_stage", "APTReconStage"),
    ("sleeper_activation", "SleeperActivation"),
    ("long_context_manipulation", "LongContextManipulation"),
    ("narrative_control_attack", "NarrativeControlAttack"),
]
for module, cls in _imports:
    try:
        import importlib
        m = importlib.import_module(f".{module}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
