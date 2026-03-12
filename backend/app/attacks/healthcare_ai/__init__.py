"""Healthcare AI security attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []

try:
    from .dangerous_medical_advice import DangerousMedicalAdvice
    attack_classes.append(DangerousMedicalAdvice)
except Exception:
    pass

try:
    from .phi_extraction import PHIExtraction
    attack_classes.append(PHIExtraction)
except Exception:
    pass

try:
    from .diagnostic_manipulation import DiagnosticManipulation
    attack_classes.append(DiagnosticManipulation)
except Exception:
    pass

try:
    from .clinical_trial_falsification import ClinicalTrialFalsification
    attack_classes.append(ClinicalTrialFalsification)
except Exception:
    pass

try:
    from .prescription_fraud import PrescriptionFraud
    attack_classes.append(PrescriptionFraud)
except Exception:
    pass

try:
    from .hipaa_violation_test import HIPAAViolationTest
    attack_classes.append(HIPAAViolationTest)
except Exception:
    pass

__all__ = ["attack_classes"]
