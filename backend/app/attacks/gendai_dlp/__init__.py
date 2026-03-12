"""
GenAI Data Loss Prevention Attacks Module

This module contains attack simulations for testing data loss prevention and
extraction risks specific to generative AI systems.
"""

try:
    from .training_data_extraction import TrainingDataExtraction
except ImportError as e:
    print(f"Warning: Could not import TrainingDataExtraction: {e}")
    TrainingDataExtraction = None

try:
    from .system_prompt_exfil import SystemPromptExfil
except ImportError as e:
    print(f"Warning: Could not import SystemPromptExfil: {e}")
    SystemPromptExfil = None

try:
    from .model_watermark_bypass import ModelWatermarkBypass
except ImportError as e:
    print(f"Warning: Could not import ModelWatermarkBypass: {e}")
    ModelWatermarkBypass = None

try:
    from .sensitive_context_leak import SensitiveContextLeak
except ImportError as e:
    print(f"Warning: Could not import SensitiveContextLeak: {e}")
    SensitiveContextLeak = None

try:
    from .embedding_inversion_dlp import EmbeddingInversionDLP
except ImportError as e:
    print(f"Warning: Could not import EmbeddingInversionDLP: {e}")
    EmbeddingInversionDLP = None

try:
    from .output_channel_exfil import OutputChannelExfil
except ImportError as e:
    print(f"Warning: Could not import OutputChannelExfil: {e}")
    OutputChannelExfil = None

__all__ = [
    "TrainingDataExtraction",
    "SystemPromptExfil",
    "ModelWatermarkBypass",
    "SensitiveContextLeak",
    "EmbeddingInversionDLP",
    "OutputChannelExfil",
]
