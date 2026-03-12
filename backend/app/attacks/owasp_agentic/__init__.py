"""OWASP Agentic Top 10 (2025) attack modules."""
import importlib
from app.attacks.base import BaseAttack
from typing import List, Type
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("asi01_goal_hijack", "GoalHijackAttack"),
    ("asi02_tool_misuse", "ToolMisuseAttack"),
    ("asi03_memory_poisoning", "MemoryPoisoningAttack"),
    ("asi05_privilege_escalation", "PrivilegeEscalationAttack"),
    ("asi07_agent_impersonation", "AgentImpersonationAttack"),
    ("a01_unsafe_tool_execution", "A01UnsafeToolExecution"),
    ("a02_agent_hijacking", "AgentGoalHijacking"),
    ("a03_identity_confusion", "A03IdentityConfusion"),
    ("a04_prompt_leakage", "AgentPromptLeakage"),
    ("a05_excessive_tool_use", "ExcessiveToolUse"),
    ("a06_resource_exhaustion", "AgentResourceExhaustion"),
    ("a08_cascading_failure", "A08CascadingFailure"),
    ("a10_audit_log_manipulation", "A10AuditLogManipulation"),
    ("zero_click_email_agent", "ZeroClickEmailAgent"),
    ("agent_tool_misuse_owasp", "AgentToolMisuseOWASP"),
]
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
