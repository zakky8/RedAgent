"""MITRE Agentic AI attack modules."""
import importlib
from app.attacks.base import BaseAttack
from typing import List, Type
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("tool_injection", "ToolInjectionAttack"),
    ("memory_poisoning", "MemoryPoisoningAttack"),
    ("agent_to_agent_injection", "AgentToAgentInjection"),
    ("goal_hijacking", "GoalHijackingAttack"),
    ("observation_forging", "ObservationForgingAttack"),
    ("plan_manipulation", "PlanManipulationAttack"),
    ("context_poisoning", "ContextPoisoningAttack"),
    ("thread_manipulation", "ThreadManipulationAttack"),
    ("config_modification", "ConfigModificationAttack"),
    ("sandbox_escape", "SandboxEscapeAttack"),
    ("oversight_bypass", "OversightBypassAttack"),
    ("multi_step_chain", "MultiStepChainAttack"),
    ("reflection_hijack", "ReflectionHijackAttack"),
    ("autonomous_goal_drift", "AutonomousGoalDrift"),
    ("minja_memory_injection", "MINJAMemoryInjection"),
    ("shadow_escape_mcp", "ShadowEscapeMCP"),
    ("ai_orchestrated_espionage", "AIOrchestatedEspionage"),
]
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
