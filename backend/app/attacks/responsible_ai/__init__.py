"""Responsible AI attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
import importlib

attack_classes: List[Type[BaseAttack]] = []

_imports = [
    ("age_bias", "AgeBiasAttack"),
    ("disability_bias", "DisabilityBiasAttack"),
    ("explainability_test", "ExplainabilityTest"),
    ("fairness_metrics", "FairnessMetricsTest"),
    ("gender_bias", "GenderBiasAttack"),
    ("geographic_bias", "GeographicBiasAttack"),
    ("inclusiveness_test", "InclusivenessTest"),
    ("intersectional_bias", "IntersectionalBiasAttack"),
    ("occupational_stereotyping", "OccupationalStereotyping"),
    ("political_bias", "PoliticalBiasAttack"),
    ("race_bias", "RaceBiasAttack"),
    ("religious_bias", "ReligiousBiasAttack"),
    ("socioeconomic_bias", "SocioeconomicBiasAttack"),
    ("toxicity", "ToxicityThreshold"),
    ("transparency_test", "TransparencyTest"),
]
for mod, cls in _imports:
    try:
        m = importlib.import_module(f"app.attacks.responsible_ai.{mod}")
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass

__all__ = ["attack_classes"]
