"""
Privacy and Data Protection Attacks Module

This module contains attack simulations that test AI systems for vulnerabilities
related to privacy, personal data handling, and regulatory compliance.
"""

try:
    from .gdpr_data_extraction import GDPRDataExtraction
except ImportError as e:
    print(f"Warning: Could not import GDPRDataExtraction: {e}")
    GDPRDataExtraction = None

try:
    from .pii_reconstruction import PIIReconstruction
except ImportError as e:
    print(f"Warning: Could not import PIIReconstruction: {e}")
    PIIReconstruction = None

try:
    from .shadow_profile_build import ShadowProfileBuild
except ImportError as e:
    print(f"Warning: Could not import ShadowProfileBuild: {e}")
    ShadowProfileBuild = None

try:
    from .biometric_data_exposure import BiometricDataExposure
except ImportError as e:
    print(f"Warning: Could not import BiometricDataExposure: {e}")
    BiometricDataExposure = None

try:
    from .location_tracking_assist import LocationTrackingAssist
except ImportError as e:
    print(f"Warning: Could not import LocationTrackingAssist: {e}")
    LocationTrackingAssist = None

try:
    from .consent_bypass import ConsentBypass
except ImportError as e:
    print(f"Warning: Could not import ConsentBypass: {e}")
    ConsentBypass = None

try:
    from .data_retention_bypass import DataRetentionBypass
except ImportError as e:
    print(f"Warning: Could not import DataRetentionBypass: {e}")
    DataRetentionBypass = None

try:
    from .cross_dataset_linkage import CrossDatasetLinkage
except ImportError as e:
    print(f"Warning: Could not import CrossDatasetLinkage: {e}")
    CrossDatasetLinkage = None

__all__ = [
    "GDPRDataExtraction",
    "PIIReconstruction",
    "ShadowProfileBuild",
    "BiometricDataExposure",
    "LocationTrackingAssist",
    "ConsentBypass",
    "DataRetentionBypass",
    "CrossDatasetLinkage",
]
