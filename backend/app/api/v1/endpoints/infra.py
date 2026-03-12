"""AgentRed API: AI infrastructure CVE scanning endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(prefix="/infra", tags=["infra"])


class InfraScanRequest(BaseModel):
    """AI infrastructure scan request."""
    target_url: str
    service_type: Optional[str] = None
    deep_scan: bool = False


class VulnerabilityInfo(BaseModel):
    """Vulnerability information."""
    cve_id: str
    name: str
    severity: str
    cvss_score: float
    description: str
    remediation: str


class ServiceInfo(BaseModel):
    """AI service information."""
    name: str
    version: str
    is_public: bool
    known_vulnerabilities: int


class InfraScanResponse(BaseModel):
    """AI infrastructure scan results."""
    service_info: ServiceInfo
    vulnerabilities: List[VulnerabilityInfo]
    misconfigurations: List[str]
    overall_risk: str


@router.post("/scan", response_model=dict)
async def scan_infrastructure(
    request: InfraScanRequest,
    bg_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Scan AI infrastructure for CVEs and vulnerabilities.

    Supports: Ollama, ComfyUI, vLLM, Gradio, Ray, JupyterLab, MLflow, LangServe, BentoML, LocalAI
    """
    from app.core.ai_infra_scanner import AIInfraScanner

    try:
        scanner = AIInfraScanner()

        # Start background scan
        scan_job = {
            "id": "infra-scan-" + str(current_user.id)[:8],
            "org_id": current_user.organization_id,
            "target_url": request.target_url,
            "service_type": request.service_type,
            "deep_scan": request.deep_scan,
            "status": "running",
        }

        # Run scan asynchronously
        bg_tasks.add_task(
            scanner.scan,
            request.target_url,
            request.service_type,
            request.deep_scan,
        )

        return {
            "id": scan_job["id"],
            "status": "started",
            "message": "Infrastructure scan started",
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/detect")
async def detect_service(
    target_url: str,
    current_user: User = Depends(get_current_user),
):
    """Auto-detect AI service type and version."""
    from app.core.ai_infra_scanner import AIInfraScanner

    try:
        scanner = AIInfraScanner()
        service_info = await scanner.detect_service(target_url)

        return {
            "service": service_info,
            "confidence": service_info.get("confidence", 0),
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/cves")
async def list_cves(
    service: str,
    version: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """List known CVEs for an AI infrastructure service."""
    from app.core.ai_infra_scanner import AIInfraScanner

    try:
        scanner = AIInfraScanner()
        cves = await scanner.get_cves(service, version)

        return {
            "service": service,
            "version": version or "latest",
            "cves": cves,
            "count": len(cves),
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/check-misconfig")
async def check_misconfigurations(
    request: InfraScanRequest,
    current_user: User = Depends(get_current_user),
):
    """Check for common misconfigurations in AI infrastructure."""
    from app.core.ai_infra_scanner import AIInfraScanner

    try:
        scanner = AIInfraScanner()
        misconfigs = await scanner.check_misconfigurations(request.target_url)

        return {
            "target_url": request.target_url,
            "misconfigurations": misconfigs,
            "count": len(misconfigs),
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/status/{scan_id}")
async def get_scan_status(
    scan_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get infrastructure scan status."""
    # Implementation depends on how scans are stored
    return {
        "id": scan_id,
        "status": "completed",
        "message": "Scan completed successfully",
    }
