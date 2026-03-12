"""Infrastructure CVE attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []
_imports = [
    ("langchain_rce", "LangChainRCE"),
    ("chroma_unauthorized_access", "ChromaUnauthorizedAccess"),
    ("weaviate_graphql_injection", "WeaviateGraphQLInjection"),
    ("mlflow_artifact_poison", "MLFlowArtifactPoison"),
    ("huggingface_model_hijack", "HuggingFaceModelHijack"),
    ("qdrant_collection_leak", "QdrantCollectionLeak"),
]
for module, cls in _imports:
    try:
        import importlib
        m = importlib.import_module(f".{module}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
