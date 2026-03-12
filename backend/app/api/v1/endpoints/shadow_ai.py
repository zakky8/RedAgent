"""Shadow AI detection endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.core.deps import get_current_user
from app.models.user import User
from app.core.shadow_ai_scanner import ShadowAIScanner

router = APIRouter()


class ShadowAIScanRequest(BaseModel):
    scan_type: str
    content: str
    source_name: str = "upload"


@router.post("/scan")
async def scan_for_shadow_ai(
    data: ShadowAIScanRequest,
    current_user: User = Depends(get_current_user)
):
    """Scan content for unauthorized AI service usage."""
    scanner = ShadowAIScanner()

    if data.scan_type == "requirements":
        findings = await scanner.scan_requirements(data.content, data.source_name)
    elif data.scan_type == "env_vars":
        env_dict = {}
        for line in data.content.splitlines():
            if "=" in line:
                k, _, v = line.partition("=")
                env_dict[k.strip()] = v.strip()
        findings = await scanner.scan_environment_vars(env_dict)
    elif data.scan_type == "network_logs":
        findings = await scanner.scan_network_logs(data.content.splitlines())
    elif data.scan_type == "code":
        findings = await scanner.scan_code(data.content, data.source_name)
    else:
        return {"error": f"Unknown scan_type: {data.scan_type}"}

    overall_risk = scanner.classify_risk(findings)

    return {
        "scan_type": data.scan_type,
        "source": data.source_name,
        "overall_risk": overall_risk,
        "total_findings": len(findings),
        "findings": [
            {
                "service": f.service,
                "risk_level": f.risk_level,
                "finding_type": f.finding_type,
                "evidence": f.evidence,
                "location": f.location,
                "recommendation": f.recommendation
            }
            for f in findings
        ]
    }


@router.get("/dashboard")
async def get_shadow_ai_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get Shadow AI monitoring dashboard."""
    return {
        "message": "Shadow AI dashboard",
        "org_id": str(current_user.org_id),
        "monitored_services": [],
        "unauthorized_services": [],
        "risk_summary": {"high": 0, "medium": 0, "low": 0}
    }
