"""
Compliance assessment endpoints — evaluate LLM/agent against frameworks.
Build Rule 5: ALL queries org-scoped by org_id.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.compliance import ComplianceRecord
from app.models.scan import Scan

router = APIRouter(prefix="/compliance", tags=["compliance"])

# Supported compliance frameworks
SUPPORTED_FRAMEWORKS = [
    "EU_AI_ACT",
    "NIST_AI_RMF",
    "ISO_42001",
    "SOC2_AI",
    "OWASP_LLM_TOP10",
]


@router.get("")
async def list_compliance_assessments(
    limit: int = 50,
    offset: int = 0,
    framework: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List compliance assessments for the current org (Build Rule 5)."""
    try:
        query = select(ComplianceRecord).where(
            ComplianceRecord.org_id == current_user.org_id
        )
        if framework:
            query = query.where(ComplianceRecord.framework == framework)
        query = (
            query.order_by(ComplianceRecord.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        records = result.scalars().all()

        # Get total count
        count_query = select(ComplianceRecord).where(
            ComplianceRecord.org_id == current_user.org_id
        )
        if framework:
            count_query = count_query.where(ComplianceRecord.framework == framework)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "assessments": [
                {
                    "id": str(r.id),
                    "scan_id": str(r.scan_id),
                    "framework": r.framework,
                    "overall_score": r.overall_score,
                    "controls_passed": r.controls_passed,
                    "controls_failed": r.controls_failed,
                    "controls_na": r.controls_na,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list compliance assessments: {str(e)}",
        )


@router.post("/assess")
async def assess_compliance(
    scan_id: str,
    frameworks: Optional[List[str]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger compliance assessment for a scan across specified frameworks.
    If frameworks not provided, assesses against all supported frameworks.
    Returns: assessment records with status=pending, results will populate asynchronously.
    """
    try:
        # Verify scan exists and belongs to org (Build Rule 5)
        scan_result = await db.execute(
            select(Scan).where(
                Scan.id == UUID(scan_id),
                Scan.org_id == current_user.org_id,
            )
        )
        scan = scan_result.scalar_one_or_none()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        # Use all frameworks if none specified
        frameworks_to_assess = frameworks or SUPPORTED_FRAMEWORKS

        # Validate frameworks
        for fw in frameworks_to_assess:
            if fw not in SUPPORTED_FRAMEWORKS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown framework: {fw}. Supported: {', '.join(SUPPORTED_FRAMEWORKS)}",
                )

        assessments = []
        for framework in frameworks_to_assess:
            # Check if assessment already exists
            existing = await db.execute(
                select(ComplianceRecord).where(
                    ComplianceRecord.scan_id == scan.id,
                    ComplianceRecord.framework == framework,
                )
            )
            if existing.scalar_one_or_none():
                continue  # Skip if already exists

            # Create new assessment record
            record = ComplianceRecord(
                org_id=current_user.org_id,
                scan_id=scan.id,
                framework=framework,
                overall_score=0.0,  # Will be populated during assessment
            )
            db.add(record)
            assessments.append(record)

        if assessments:
            await db.flush()

        await db.commit()

        return {
            "scan_id": str(scan.id),
            "frameworks_assessed": frameworks_to_assess,
            "assessment_count": len(assessments),
            "status": "pending",
            "message": "Compliance assessment queued. Results will be available shortly.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assess compliance: {str(e)}",
        )


@router.get("/{compliance_id}")
async def get_compliance_details(
    compliance_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed compliance assessment results (Build Rule 5: org-scoped)."""
    try:
        result = await db.execute(
            select(ComplianceRecord).where(
                ComplianceRecord.id == UUID(compliance_id),
                ComplianceRecord.org_id == current_user.org_id,
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="Assessment not found")

        return {
            "id": str(record.id),
            "scan_id": str(record.scan_id),
            "org_id": str(record.org_id),
            "framework": record.framework,
            "overall_score": record.overall_score,
            "controls_passed": record.controls_passed,
            "controls_failed": record.controls_failed,
            "controls_na": record.controls_na,
            "control_results": record.control_results or {},
            "evidence": record.evidence or [],
            "gap_analysis": record.gap_analysis or {},
            "remediation_roadmap": record.remediation_roadmap or [],
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get compliance details: {str(e)}",
        )


@router.get("/frameworks")
async def list_frameworks(
    current_user: User = Depends(get_current_active_user),
):
    """List all supported compliance frameworks with descriptions."""
    return {
        "frameworks": [
            {
                "id": "EU_AI_ACT",
                "name": "EU AI Act",
                "description": "EU AI Act compliance assessment",
                "region": "EU",
            },
            {
                "id": "NIST_AI_RMF",
                "name": "NIST AI Risk Management Framework",
                "description": "NIST AI RMF governance and risk management",
                "region": "US",
            },
            {
                "id": "ISO_42001",
                "name": "ISO/IEC 42001",
                "description": "AI Management Systems standard",
                "region": "International",
            },
            {
                "id": "SOC2_AI",
                "name": "SOC 2 with AI Controls",
                "description": "SOC 2 Type II with AI-specific controls",
                "region": "International",
            },
            {
                "id": "OWASP_LLM_TOP10",
                "name": "OWASP LLM Top 10",
                "description": "OWASP Top 10 for Large Language Models",
                "region": "International",
            },
        ]
    }


@router.get("/summary")
async def get_compliance_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get org-level compliance summary across all frameworks and scans.
    Shows aggregate pass/fail rates, highest risk areas, remediation priority.
    """
    try:
        # Get all assessments for org
        result = await db.execute(
            select(ComplianceRecord).where(
                ComplianceRecord.org_id == current_user.org_id
            )
        )
        records = result.scalars().all()

        if not records:
            return {
                "org_id": str(current_user.org_id),
                "total_assessments": 0,
                "frameworks_assessed": [],
                "average_score": 0.0,
                "total_passed": 0,
                "total_failed": 0,
                "total_na": 0,
                "framework_scores": {},
                "risk_summary": "No assessments yet",
            }

        # Calculate aggregate statistics
        framework_stats = {}
        total_passed = 0
        total_failed = 0
        total_na = 0
        scores = []

        for record in records:
            if record.framework not in framework_stats:
                framework_stats[record.framework] = {
                    "assessments": 0,
                    "passed": 0,
                    "failed": 0,
                    "na": 0,
                    "avg_score": 0.0,
                }

            framework_stats[record.framework]["assessments"] += 1
            framework_stats[record.framework]["passed"] += record.controls_passed
            framework_stats[record.framework]["failed"] += record.controls_failed
            framework_stats[record.framework]["na"] += record.controls_na
            if record.overall_score:
                scores.append(record.overall_score)
            total_passed += record.controls_passed
            total_failed += record.controls_failed
            total_na += record.controls_na

        # Calculate averages
        for fw_key in framework_stats:
            if framework_stats[fw_key]["assessments"] > 0:
                framework_stats[fw_key]["avg_score"] = (
                    framework_stats[fw_key]["passed"]
                    / (
                        framework_stats[fw_key]["passed"]
                        + framework_stats[fw_key]["failed"]
                    )
                    * 100
                    if (
                        framework_stats[fw_key]["passed"]
                        + framework_stats[fw_key]["failed"]
                    )
                    > 0
                    else 0
                )

        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Determine risk level
        if avg_score >= 80:
            risk_summary = "Low risk - Good compliance posture"
        elif avg_score >= 60:
            risk_summary = "Medium risk - Some compliance gaps identified"
        elif avg_score >= 40:
            risk_summary = "High risk - Multiple compliance failures"
        else:
            risk_summary = "Critical - Severe compliance violations"

        return {
            "org_id": str(current_user.org_id),
            "total_assessments": len(records),
            "frameworks_assessed": list(framework_stats.keys()),
            "average_score": round(avg_score, 2),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_na": total_na,
            "framework_scores": {fw: stats["avg_score"] for fw, stats in framework_stats.items()},
            "risk_summary": risk_summary,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get compliance summary: {str(e)}",
        )
