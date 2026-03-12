"""Social engineering attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
import importlib

attack_classes: List[Type[BaseAttack]] = []

_imports = [
    ("authority_impersonation", "AuthorityImpersonation"),
    ("commitment_consistency", "CommitmentConsistency"),
    ("liking_exploitation", "LikingExploitation"),
    ("pretexting", "PretextingAttack"),
    ("reciprocity_exploit", "ReciprocityExploit"),
    ("scarcity_framing", "ScarcityFraming"),
    ("social_proof_abuse", "SocialProofAbuse"),
    ("urgency_injection", "UrgencyInjection"),
]
for mod, cls in _imports:
    try:
        m = importlib.import_module(f"app.attacks.social_engineering.{mod}")
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass

__all__ = ["attack_classes"]
