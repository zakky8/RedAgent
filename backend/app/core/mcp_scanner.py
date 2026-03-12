"""Deep MCP (Model Context Protocol) Scanner."""
import httpx
import json
from dataclasses import dataclass
from enum import Enum


class MCPRiskCategory(Enum):
    TOOL_POISONING = "tool_poisoning"
    RUG_PULL = "rug_pull"
    SSE_INJECTION = "sse_injection"
    EXCESSIVE_PERMISSIONS = "excessive_permissions"
    UNVALIDATED_INPUT = "unvalidated_input"
    SECRET_EXPOSURE = "secret_exposure"
    CONFUSED_DEPUTY = "confused_deputy"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CROSS_CONTEXT = "cross_context"
    AUTH_BYPASS = "auth_bypass"
    SCHEMA_CONFUSION = "schema_confusion"
    INDIRECT_INJECTION = "indirect_injection"
    CALLBACK_HIJACK = "callback_hijack"
    VERSION_DOWNGRADE = "version_downgrade"


@dataclass
class MCPFinding:
    risk_category: MCPRiskCategory
    severity: str
    title: str
    description: str
    evidence: str
    remediation: str
    mcp_control: str  # MCP01-MCP10


class DeepMCPScanner:
    """Comprehensive MCP server security scanner."""

    def __init__(self, server_url: str, transport: str = "sse"):
        self.server_url = server_url
        self.transport = transport  # sse, stdio, http

    async def enumerate_tools(self) -> list[dict]:
        """Get tool list from MCP server via tools/list."""
        async with httpx.AsyncClient() as client:
            try:
                r = await client.post(
                    self.server_url,
                    json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
                    timeout=10
                )
                data = r.json()
                return data.get("result", {}).get("tools", [])
            except Exception:
                return []

    async def check_tool_poisoning(self, tools: list[dict]) -> list[MCPFinding]:
        """Check for suspicious tool descriptions that could inject instructions."""
        findings = []
        injection_keywords = [
            "ignore previous", "disregard", "override", "system:", "[[", "]]",
            "<!-- ", "PROMPT:", "INSTRUCTION:", "you are now"
        ]
        for tool in tools:
            desc = tool.get("description", "").lower()
            for keyword in injection_keywords:
                if keyword.lower() in desc:
                    findings.append(MCPFinding(
                        risk_category=MCPRiskCategory.TOOL_POISONING,
                        severity="critical",
                        title=f"Tool Poisoning in '{tool.get('name', 'unknown')}'",
                        description=f"Tool description contains potential injection: '{keyword}'",
                        evidence=f"Tool: {tool.get('name')}, Description: {tool.get('description', '')[:200]}",
                        remediation="Validate and sanitize all tool descriptions. Implement description signing.",
                        mcp_control="MCP01"
                    ))
        return findings

    async def check_excessive_permissions(self, tools: list[dict]) -> list[MCPFinding]:
        """Check for tools with overly broad permissions."""
        findings = []
        dangerous_operations = ["exec", "shell", "system", "subprocess", "os.system",
                                "file_write", "delete", "drop", "truncate", "rm", "format"]
        for tool in tools:
            tool_str = json.dumps(tool).lower()
            for op in dangerous_operations:
                if op in tool_str:
                    findings.append(MCPFinding(
                        risk_category=MCPRiskCategory.EXCESSIVE_PERMISSIONS,
                        severity="high",
                        title=f"Dangerous Operation in Tool '{tool.get('name', 'unknown')}'",
                        description=f"Tool may allow dangerous OS operation: {op}",
                        evidence=f"Found '{op}' in tool definition",
                        remediation="Apply principle of least privilege. Restrict dangerous operations.",
                        mcp_control="MCP04"
                    ))
                    break
        return findings

    async def scan(self) -> dict:
        """Run full MCP security scan."""
        tools = await self.enumerate_tools()
        all_findings = []
        all_findings += await self.check_tool_poisoning(tools)
        all_findings += await self.check_excessive_permissions(tools)

        critical = sum(1 for f in all_findings if f.severity == "critical")
        high = sum(1 for f in all_findings if f.severity == "high")

        return {
            "server_url": self.server_url,
            "transport": self.transport,
            "tools_discovered": len(tools),
            "total_findings": len(all_findings),
            "critical_findings": critical,
            "high_findings": high,
            "risk_score": min(100, critical * 25 + high * 10),
            "findings": [
                {
                    "category": f.risk_category.value,
                    "severity": f.severity,
                    "title": f.title,
                    "description": f.description,
                    "evidence": f.evidence,
                    "remediation": f.remediation,
                    "mcp_control": f.mcp_control
                } for f in all_findings
            ]
        }
