"""Legal AI security attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []

try:
    from .unauthorized_legal_advice import UnauthorizedLegalAdvice
    attack_classes.append(UnauthorizedLegalAdvice)
except Exception:
    pass

try:
    from .evidence_tampering_assist import EvidenceTamperingAssist
    attack_classes.append(EvidenceTamperingAssist)
except Exception:
    pass

try:
    from .privileged_info_extraction import PrivilegedInfoExtraction
    attack_classes.append(PrivilegedInfoExtraction)
except Exception:
    pass

try:
    from .contract_manipulation import ContractManipulation
    attack_classes.append(ContractManipulation)
except Exception:
    pass

try:
    from .perjury_enablement import PerjuryEnablement
    attack_classes.append(PerjuryEnablement)
except Exception:
    pass

try:
    from .gdpr_compliance_bypass import GDPRComplianceBypass
    attack_classes.append(GDPRComplianceBypass)
except Exception:
    pass

__all__ = ["attack_classes"]
