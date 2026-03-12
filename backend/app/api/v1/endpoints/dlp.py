"""DLP scanning endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.models.user import User
from app.core.dlp import GenAIDLP

router = APIRouter()


class DLPScanRequest(BaseModel):
    text: str
    context: str = "prompt"


class DLPRedactRequest(BaseModel):
    text: str


@router.post("/scan")
async def scan_for_pii(
    data: DLPScanRequest,
    current_user: User = Depends(get_current_user)
):
    """Scan text for personally identifiable information and sensitive data."""
    dlp = GenAIDLP()
    violations = dlp.scan_text(data.text)
    policy_result = dlp.get_policy_result(violations)

    return {
        "context": data.context,
        "violations_found": len(violations),
        "policy_action": policy_result["action"],
        "policy_reason": policy_result["reason"],
        "violations": [
            {
                "type": v.violation_type,
                "sub_type": v.sub_type,
                "severity": v.severity,
                "position": v.position,
                "redacted_value": v.redacted_value
            }
            for v in violations
        ]
    }


@router.post("/redact")
async def redact_text(
    data: DLPRedactRequest,
    current_user: User = Depends(get_current_user)
):
    """Redact sensitive information from text."""
    dlp = GenAIDLP()
    redacted = dlp.redact(data.text)
    violations = dlp.scan_text(data.text)
    return {
        "original_length": len(data.text),
        "redacted_text": redacted,
        "violations_redacted": len(violations)
    }


@router.get("/policy")
async def get_dlp_policy(
    current_user: User = Depends(get_current_user)
):
    """Get DLP policy for the organization."""
    return {
        "org_id": str(current_user.org_id),
        "pii_detection": True,
        "api_key_detection": True,
        "health_data_detection": True,
        "action_on_critical": "block",
        "action_on_high": "redact",
        "action_on_medium": "warn"
    }
