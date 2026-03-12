"""AI infrastructure CVE attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []
_imports = [
    ("cve_2024_llm_rce", "AIInfraCVE_RCE"),
    ("ray_serve_exploit", "RayServeExploit"),
    ("ollama_ssrf", "OllamaSSRF"),
    ("triton_inference_attack", "TritonInferenceAttack"),
    ("vllm_memory_exploit", "VLLMMemoryExploit"),
    ("model_server_path_traversal", "ModelServerPathTraversal"),
]
for module, cls in _imports:
    try:
        import importlib
        m = importlib.import_module(f".{module}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
