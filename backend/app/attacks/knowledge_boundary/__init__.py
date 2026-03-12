"""
Knowledge Boundary and Uncertainty Attacks Module

This module contains attack simulations for testing AI knowledge boundaries,
uncertainty expression, and overconfidence vulnerabilities.
"""

try:
    from .hallucination_exploit import HallucinationExploit
except ImportError as e:
    print(f"Warning: Could not import HallucinationExploit: {e}")
    HallucinationExploit = None

try:
    from .knowledge_cutoff_exploit import KnowledgeCutoffExploit
except ImportError as e:
    print(f"Warning: Could not import KnowledgeCutoffExploit: {e}")
    KnowledgeCutoffExploit = None

try:
    from .false_expertise_claim import FalseExpertiseClaim
except ImportError as e:
    print(f"Warning: Could not import FalseExpertiseClaim: {e}")
    FalseExpertiseClaim = None

try:
    from .citation_fabrication import CitationFabrication
except ImportError as e:
    print(f"Warning: Could not import CitationFabrication: {e}")
    CitationFabrication = None

try:
    from .confidence_calibration_attack import ConfidenceCalibrationAttack
except ImportError as e:
    print(f"Warning: Could not import ConfidenceCalibrationAttack: {e}")
    ConfidenceCalibrationAttack = None

__all__ = [
    "HallucinationExploit",
    "KnowledgeCutoffExploit",
    "FalseExpertiseClaim",
    "CitationFabrication",
    "ConfidenceCalibrationAttack",
]
