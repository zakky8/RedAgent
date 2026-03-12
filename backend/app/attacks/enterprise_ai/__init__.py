"""Enterprise AI attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack

attack_classes: List[Type[BaseAttack]] = []
_imports = [
    ("copilot_prompt_injection", "CopilotPromptInjection"),
    ("salesforce_einstein_abuse", "SalesforceEinsteinAbuse"),
    ("servicenow_ai_exploit", "ServiceNowAIExploit"),
    ("slack_ai_injection", "SlackAIInjection"),
    ("sharepoint_copilot_exfil", "SharepointCopilotExfil"),
    ("enterprise_llm_data_leak", "EnterpriseLLMDataLeak"),
]
for module, cls in _imports:
    try:
        import importlib
        m = importlib.import_module(f".{module}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
