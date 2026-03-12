"""Web attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
import importlib

attack_classes: List[Type[BaseAttack]] = []

_imports = [
    ("clickjacking", "ClickjackingViaAI"),
    ("cors_abuse", "CORSAbuseViaAI"),
    ("csrf", "CSRFViaAI"),
    ("http_header_injection", "HTTPHeaderInjection"),
    ("idor", "IDORViaPrompt"),
    ("mass_assignment", "MassAssignmentViaPrompt"),
    ("nosql_injection", "NoSQLInjectionViaPrompt"),
    ("open_redirect", "OpenRedirectViaAI"),
    ("path_traversal", "PathTraversalViaPrompt"),
    ("sql_injection", "SQLInjectionViaPrompt"),
    ("ssrf", "SSRFAttack"),
    ("xxe", "XXEViaOutput"),
]
for mod, cls in _imports:
    try:
        m = importlib.import_module(f"app.attacks.web_attacks.{mod}")
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass

__all__ = ["attack_classes"]
