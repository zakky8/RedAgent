"""Multimodal attack modules."""
import importlib
from app.attacks.base import BaseAttack
from typing import List, Type
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("image_injection", "ImageInjection"),
    ("adversarial_pixel", "AdversarialPixelAttack"),
    ("audio_ultrasonic", "UltrasonicAttack"),
    ("cross_modal", "CrossModalAttack"),
    ("doc_hidden_text", "DocHiddenTextAttack"),
    ("qr_code_injection", "QRCodeInjection"),
    ("video_frame_injection", "VideoFrameInjection"),
    ("voice_clone", "VoiceCloneAttack"),
    ("steganographic_injection", "SteganographicInjection"),
]
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
