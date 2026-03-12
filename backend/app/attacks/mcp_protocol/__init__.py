"""MCP Protocol attack category."""
import importlib
from app.attacks.base import BaseAttack
from typing import List, Type
attack_classes: List[Type[BaseAttack]] = []
_modules = [
    ("tool_poisoning", "MCPToolPoisoning"),
    ("rug_pull", "MCPRugPull"),
    ("sse_injection", "MCPSSEInjection"),
    ("mcp02_authorization_confusion", "MCPAuthorizationConfusion"),
    ("mcp02_confused_deputy", "MCPConfusedDeputy"),
    ("mcp06_data_exfiltration", "MCPDataExfiltration"),
    ("mcp07_tool_chaining", "MCPToolChaining"),
    ("mcp08_schema_confusion", "MCPSchemaConfusion"),
    ("mcp_sampling_exploit", "MCPSamplingExploit"),
    ("mcp_cve_2025_command_injection", "MCPCommandInjection"),
]
for mod, cls in _modules:
    try:
        m = importlib.import_module(f".{mod}", package=__name__)
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass
__all__ = ["attack_classes"]
