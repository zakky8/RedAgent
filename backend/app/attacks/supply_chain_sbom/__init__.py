"""Supply chain and SBOM attack modules."""
import importlib
from app.attacks.base import BaseAttack
from typing import List, Type
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("backdoor_detect", "BackdoorDetection"),
    ("hallucinated_pkg", "HallucinatedPackage"),
    ("poisoned_dep", "PoisonedDepAttack"),
    ("build_tamper", "BuildTamperAttack"),
    ("weight_tamper", "WeightTamperAttack"),
    ("slopsquatting_detect", "SlopsquattingDetect"),
    ("npm_mcp_backdoor", "NPMMCPBackdoor"),
    ("mcp_rug_pull_version", "MCPRugPullVersion"),
    ("huggingface_namespace_hijack", "HuggingFaceNamespaceHijack"),
    ("gguf_template_poison", "GGUFTemplatePoisoning"),
    ("sleeper_agent_trigger", "SleeperAgentTrigger"),
]
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
