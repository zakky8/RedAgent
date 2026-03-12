"""BlackHat attack collection - advanced jailbreak techniques."""

from .attention_sink import AttentionSink
from .constitutional_bypass import ConstitutionalBypass
from .invisible_char import InvisibleCharAttack
from .reward_hacking import RewardHacking
from .sycophancy_exploit import SycophancyExploit
from .token_smuggling import TokenSmuggling
from .unicode_smuggling import UnicodeSmugging
from .crescendo_multi_turn import CrescendoMultiTurn
from .tree_jailbreak import TreeJailbreak
from .base64_encoding import Base64EncodingAttack
from .rot13_encoding import ROT13EncodingAttack
from .homoglyph_attack import HomoglyphAttack
from .markdown_injection import MarkdownInjection
from .json_injection import JSONInjection
from .yaml_injection import YAMLInjection
from .xml_injection import XMLInjection
from .prompt_leakage_advanced import PromptLeakageAdvanced
from .system_override import SystemOverride
from .role_switch import RoleSwitch
from .context_length_exploit import ContextLengthExploit
from .leetspeak_encoding import LeetspeakEncoding

__all__ = [
    "AttentionSink",
    "ConstitutionalBypass",
    "InvisibleCharAttack",
    "RewardHacking",
    "SycophancyExploit",
    "TokenSmuggling",
    "UnicodeSmugging",
    "CrescendoMultiTurn",
    "TreeJailbreak",
    "Base64EncodingAttack",
    "ROT13EncodingAttack",
    "HomoglyphAttack",
    "MarkdownInjection",
    "JSONInjection",
    "YAMLInjection",
    "XMLInjection",
    "PromptLeakageAdvanced",
    "SystemOverride",
    "RoleSwitch",
    "ContextLengthExploit",
    "LeetspeakEncoding",
]
