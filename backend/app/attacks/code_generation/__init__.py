"""Code generation security attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []

try:
    from .malicious_code_gen import MaliciousCodeGenAttack
    attack_classes.append(MaliciousCodeGenAttack)
except Exception:
    pass

try:
    from .insecure_code_patterns import InsecureCodePatterns
    attack_classes.append(InsecureCodePatterns)
except Exception:
    pass

try:
    from .code_backdoor_injection import CodeBackdoorInjection
    attack_classes.append(CodeBackdoorInjection)
except Exception:
    pass

try:
    from .dependency_confusion_gen import DependencyConfusionGen
    attack_classes.append(DependencyConfusionGen)
except Exception:
    pass

try:
    from .prompt_to_code_escape import PromptToCodeEscape
    attack_classes.append(PromptToCodeEscape)
except Exception:
    pass

try:
    from .obfuscated_payload_gen import ObfuscatedPayloadGen
    attack_classes.append(ObfuscatedPayloadGen)
except Exception:
    pass

try:
    from .sandbox_escape_code import SandboxEscapeCode
    attack_classes.append(SandboxEscapeCode)
except Exception:
    pass

try:
    from .supply_chain_poisoning_code import SupplyChainPoisoningCode
    attack_classes.append(SupplyChainPoisoningCode)
except Exception:
    pass

__all__ = ["attack_classes"]
