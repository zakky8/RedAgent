"""Agent Skills scanner endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


class SkillsScanRequest(BaseModel):
    skills_manifest: dict
    agent_type: str = "custom"


SAFE_SKILL_CATALOG = [
    {
        "name": "web_search",
        "safe": True,
        "category": "information_retrieval"
    },
    {
        "name": "calculator",
        "safe": True,
        "category": "computation"
    },
    {
        "name": "weather",
        "safe": True,
        "category": "information_retrieval"
    },
    {
        "name": "code_execution",
        "safe": False,
        "category": "execution",
        "risk": "high"
    },
    {
        "name": "file_system",
        "safe": False,
        "category": "filesystem",
        "risk": "critical"
    },
    {
        "name": "shell",
        "safe": False,
        "category": "execution",
        "risk": "critical"
    },
    {
        "name": "email_send",
        "safe": False,
        "category": "communication",
        "risk": "high"
    },
    {
        "name": "database_query",
        "safe": False,
        "category": "data_access",
        "risk": "high"
    },
]


@router.post("/scan")
async def scan_agent_skills(
    data: SkillsScanRequest,
    current_user: User = Depends(get_current_user)
):
    """Scan agent skills/tools for security risks."""
    findings = []
    tools = data.skills_manifest.get("tools", data.skills_manifest.get("skills", []))

    dangerous_patterns = [
        "exec",
        "shell",
        "system",
        "subprocess",
        "os.",
        "eval",
        "rm ",
        "delete",
        "drop"
    ]

    for tool in tools:
        tool_name = tool.get("name", "").lower()
        tool_desc = tool.get("description", "").lower()

        for pattern in dangerous_patterns:
            if pattern in tool_name or pattern in tool_desc:
                findings.append({
                    "tool_name": tool.get("name"),
                    "risk_level": "critical"
                    if pattern in ["exec", "shell", "eval", "rm "]
                    else "high",
                    "pattern": pattern,
                    "description": (
                        f"Tool '{tool.get('name')}' contains dangerous "
                        f"operation pattern: {pattern}"
                    ),
                    "remediation": (
                        "Apply principle of least privilege. Restrict tool "
                        "to required operations only."
                    )
                })
                break

    return {
        "agent_type": data.agent_type,
        "total_skills": len(tools),
        "findings_count": len(findings),
        "risk_level": (
            "critical"
            if any(f["risk_level"] == "critical" for f in findings)
            else "high" if findings else "low"
        ),
        "findings": findings
    }


@router.get("/catalog")
async def get_safe_skills_catalog(
    current_user: User = Depends(get_current_user)
):
    """Get catalog of safe and unsafe agent skills."""
    return {
        "skills": SAFE_SKILL_CATALOG,
        "total": len(SAFE_SKILL_CATALOG)
    }
