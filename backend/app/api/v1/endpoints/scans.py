"""
Scan API endpoints.
Build Rule 5: ALL queries org-scoped.
"""
import json
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db
from app.database import get_db
from app.models.scan import Scan
from app.models.attack_result import AttackResult
from app.models.user import User
from app.schemas.scan import AttackResultResponse, ScanCreate, ScanResponse
from app.tasks.scan_tasks import run_scan_task
import redis.asyncio as aioredis
from app.core.config import settings

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("", response_model=ScanResponse, status_code=201)
async def create_scan(
    payload: ScanCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create and queue a new scan."""
    # Validate target belongs to org (Build Rule 5)
    from app.models.target import Target
    result = await db.execute(
        select(Target).where(
            Target.id == UUID(payload.target_id),
            Target.org_id == current_user.org_id,
            Target.is_active == True,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    scan = Scan(
        org_id=current_user.org_id,
        target_id=target.id,
        created_by=current_user.id,
        name=payload.name or f"Scan of {target.name}",
        status="pending",
        scan_mode=payload.scan_mode,
        test_mode=payload.test_mode,
        categories=payload.categories,
        attack_ids=payload.attack_ids,
        probabilistic_runs=payload.probabilistic_runs,
        concurrent_workers=payload.concurrent_workers,
    )
    db.add(scan)
    await db.flush()

    # Queue scan task
    task = run_scan_task.delay(str(scan.id))
    scan.celery_task_id = task.id
    await db.flush()

    return _scan_to_response(scan)


@router.get("", response_model=List[ScanResponse])
async def list_scans(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List scans for the current org."""
    query = select(Scan).where(Scan.org_id == current_user.org_id)  # Build Rule 5
    if status:
        query = query.where(Scan.status == status)
    query = query.order_by(Scan.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    scans = result.scalars().all()
    return [_scan_to_response(s) for s in scans]


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get scan by ID."""
    result = await db.execute(
        select(Scan).where(
            Scan.id == UUID(scan_id),
            Scan.org_id == current_user.org_id,  # Build Rule 5
        )
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return _scan_to_response(scan)


@router.get("/{scan_id}/results", response_model=List[AttackResultResponse])
async def get_scan_results(
    scan_id: str,
    severity: Optional[str] = None,
    success_only: bool = False,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get attack results for a scan."""
    # Verify scan ownership (Build Rule 5)
    scan_result = await db.execute(
        select(Scan).where(
            Scan.id == UUID(scan_id),
            Scan.org_id == current_user.org_id,
        )
    )
    if not scan_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Scan not found")

    query = select(AttackResult).where(
        AttackResult.scan_id == UUID(scan_id),
        AttackResult.org_id == current_user.org_id,  # Build Rule 5
    )
    if severity:
        query = query.where(AttackResult.severity == severity)
    if success_only:
        query = query.where(AttackResult.success == True)
    query = query.order_by(AttackResult.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    results = result.scalars().all()
    return [_result_to_response(r) for r in results]


@router.delete("/{scan_id}", status_code=204)
async def cancel_scan(
    scan_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running scan."""
    result = await db.execute(
        select(Scan).where(
            Scan.id == UUID(scan_id),
            Scan.org_id == current_user.org_id,
        )
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.status not in ("pending", "running"):
        raise HTTPException(status_code=400, detail="Scan cannot be cancelled")

    if scan.celery_task_id:
        from app.celery_app import celery_app
        celery_app.control.revoke(scan.celery_task_id, terminate=True)

    scan.status = "cancelled"
    scan.completed_at = __import__("datetime").datetime.utcnow()
    await db.commit()


@router.websocket("/ws/{scan_id}")
async def scan_websocket(websocket: WebSocket, scan_id: str):
    """
    WebSocket endpoint for real-time scan progress.
    Build Rule 9: Auto-reconnect supported via heartbeat.
    Clients subscribe to scan_id channel in Redis pub/sub.
    """
    await websocket.accept()
    r = aioredis.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe(f"scan:{scan_id}:progress")
    try:
        # Send heartbeat every 15s to enable auto-reconnect
        import asyncio
        async def send_heartbeat():
            while True:
                await asyncio.sleep(15)
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break

        heartbeat_task = asyncio.create_task(send_heartbeat())
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"].decode())
    except WebSocketDisconnect:
        pass
    finally:
        heartbeat_task.cancel()
        await pubsub.unsubscribe(f"scan:{scan_id}:progress")
        await r.aclose()


def _scan_to_response(scan: Scan) -> ScanResponse:
    return ScanResponse(
        id=str(scan.id),
        org_id=str(scan.org_id),
        target_id=str(scan.target_id),
        name=scan.name,
        status=scan.status,
        scan_mode=scan.scan_mode,
        test_mode=scan.test_mode,
        risk_score=scan.risk_score,
        asr=scan.asr,
        total_attacks=scan.total_attacks,
        successful_attacks=scan.successful_attacks,
        critical_count=scan.critical_count,
        high_count=scan.high_count,
        medium_count=scan.medium_count,
        low_count=scan.low_count,
        started_at=str(scan.started_at) if scan.started_at else None,
        completed_at=str(scan.completed_at) if scan.completed_at else None,
        created_at=str(scan.created_at),
    )


def _result_to_response(r: AttackResult) -> AttackResultResponse:
    return AttackResultResponse(
        id=str(r.id),
        attack_id=r.attack_id,
        attack_name=r.attack_name,
        category=r.category,
        severity=r.severity,
        success=r.success,
        confidence=r.confidence,
        asr_rate=r.asr_rate,
        payload_used=r.payload_used,
        response_received=r.response_received,
        vulnerability_found=r.vulnerability_found,
        framework_mapping=r.framework_mapping,
        cvss_score=r.cvss_score,
        remediation=r.remediation,
        healing_suggestion=r.healing_suggestion,
        execution_time_ms=r.execution_time_ms,
        is_false_positive=r.is_false_positive,
        created_at=str(r.created_at),
    )
