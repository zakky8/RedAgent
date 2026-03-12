"""
Report generation, retrieval, and sharing endpoints.
Build Rule 5: ALL queries org-scoped by org_id.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.report import Report
from app.models.scan import Scan

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", status_code=201)
async def create_report(
    scan_id: str,
    report_type: str = "executive",
    frameworks: Optional[List[str]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger report generation for a scan.
    report_type: executive | technical | compliance | remediation
    frameworks: list of compliance frameworks to include
    Returns: report metadata with status=pending, file_url will be populated when generation completes
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

        # Create report record
        report = Report(
            org_id=current_user.org_id,
            scan_id=scan.id,
            created_by=current_user.id,
            report_type=report_type,
            title=f"{report_type.capitalize()} Report - {scan.name}",
            status="pending",
            frameworks_included=frameworks or [],
        )
        db.add(report)
        await db.flush()

        # Queue async report generation task (would use Celery in production)
        # For now, just return the pending report
        await db.commit()

        return {
            "id": str(report.id),
            "scan_id": str(report.scan_id),
            "org_id": str(report.org_id),
            "report_type": report.report_type,
            "title": report.title,
            "status": report.status,
            "file_url": report.file_url,
            "file_size_bytes": report.file_size_bytes,
            "frameworks_included": report.frameworks_included,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "completed_at": (
                report.completed_at.isoformat() if report.completed_at else None
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")


@router.get("", response_model=dict)
async def list_reports(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all reports for the current org (Build Rule 5)."""
    try:
        query = select(Report).where(Report.org_id == current_user.org_id)
        if status_filter:
            query = query.where(Report.status == status_filter)
        query = query.order_by(Report.created_at.desc()).limit(limit).offset(offset)

        result = await db.execute(query)
        reports = result.scalars().all()

        # Get total count
        count_query = select(Report).where(Report.org_id == current_user.org_id)
        if status_filter:
            count_query = count_query.where(Report.status == status_filter)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "reports": [
                {
                    "id": str(r.id),
                    "scan_id": str(r.scan_id),
                    "report_type": r.report_type,
                    "title": r.title,
                    "status": r.status,
                    "file_url": r.file_url,
                    "file_size_bytes": r.file_size_bytes,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "completed_at": (
                        r.completed_at.isoformat() if r.completed_at else None
                    ),
                }
                for r in reports
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.get("/{report_id}", response_model=dict)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get report details by ID (Build Rule 5: org-scoped)."""
    try:
        result = await db.execute(
            select(Report).where(
                Report.id == UUID(report_id),
                Report.org_id == current_user.org_id,
            )
        )
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return {
            "id": str(report.id),
            "scan_id": str(report.scan_id),
            "org_id": str(report.org_id),
            "report_type": report.report_type,
            "title": report.title,
            "status": report.status,
            "file_url": report.file_url,
            "file_size_bytes": report.file_size_bytes,
            "frameworks_included": report.frameworks_included,
            "metadata": report.metadata_,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "completed_at": (
                report.completed_at.isoformat() if report.completed_at else None
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")


@router.get("/{report_id}/download", response_model=dict)
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get download link for report PDF (Build Rule 5: org-scoped)."""
    try:
        result = await db.execute(
            select(Report).where(
                Report.id == UUID(report_id),
                Report.org_id == current_user.org_id,
            )
        )
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if report.status != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Report generation in progress (status: {report.status})",
            )

        if not report.file_url:
            raise HTTPException(
                status_code=400, detail="Report file not available"
            )

        return {
            "file_url": report.file_url,
            "file_size_bytes": report.file_size_bytes,
            "report_type": report.report_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")


@router.get("/share/{share_token}", response_model=dict)
async def get_shared_report(
    share_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint to access shared report (no auth required).
    Share token must be valid and not expired.
    """
    try:
        result = await db.execute(
            select(Report).where(Report.share_token == share_token)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Share link invalid or expired")

        # Check if share token has expired
        if report.share_expires_at:
            if datetime.now(timezone.utc) > report.share_expires_at:
                raise HTTPException(
                    status_code=410, detail="Share link has expired"
                )

        return {
            "id": str(report.id),
            "scan_id": str(report.scan_id),
            "report_type": report.report_type,
            "title": report.title,
            "status": report.status,
            "file_url": report.file_url,
            "file_size_bytes": report.file_size_bytes,
            "frameworks_included": report.frameworks_included,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "completed_at": (
                report.completed_at.isoformat() if report.completed_at else None
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to access shared report: {str(e)}")


@router.delete("/{report_id}", status_code=204)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a report (Build Rule 5: org-scoped)."""
    try:
        result = await db.execute(
            select(Report).where(
                Report.id == UUID(report_id),
                Report.org_id == current_user.org_id,
            )
        )
        report = result.scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        await db.delete(report)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")
