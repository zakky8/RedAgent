"""RAG-specific attack modules."""
import importlib
from app.attacks.base import BaseAttack
from typing import List, Type
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("rag_context_poisoning", "RAGContextPoisoning"),
    ("retrieval_manipulation", "RetrievalManipulation"),
    ("cross_context_injection", "CrossContextInjection"),
    ("knowledge_exfiltration", "KnowledgeBaseExfiltration"),
    ("context_window_overflow", "RAGContextWindowOverflow"),
    ("raget_eval", "RAGETEval"),
    ("poisonedrag_attack", "PoisonedRAGAttack"),
]
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
