"""
Real-time monitoring endpoints for agent behavior and anomaly detection.
Build Rule 5: ALL queries org-scoped by org_id.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.monitor_event import MonitorEvent
from app.models.continuous_scan import ContinuousScanConfig
from app.models.target import Target

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/events", status_code=201)
async def ingest_monitor_event(
    agent_id: Optional[str] = None,
    event_type: str = "request",
    severity: Optional[str] = None,
    is_anomalous: bool = False,
    anomaly_score: Optional[float] = None,
    anomaly_reason: Optional[str] = None,
    metadata: Optional[dict] = None,
    input_hash: Optional[str] = None,
    output_hash: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a monitoring event from SDK or agent.
    Called by agents to report their own monitoring data.
    Build Rule 5: Events automatically associated with user's org.
    """
    try:
        # If agent_id provided, verify it belongs to org
        if agent_id:
            from app.models.agent_registry import AgentRegistry
            agent_result = await db.execute(
                select(AgentRegistry).where(
                    AgentRegistry.id == UUID(agent_id),
                    AgentRegistry.org_id == current_user.org_id,
                )
            )
            if not agent_result.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Agent not found")

        event = MonitorEvent(
            org_id=current_user.org_id,
            agent_id=UUID(agent_id) if agent_id else None,
            event_type=event_type,
            severity=severity,
            is_anomalous=is_anomalous,
            anomaly_score=anomaly_score,
            anomaly_reason=anomaly_reason,
            metadata_=metadata or {},
            input_hash=input_hash,
            output_hash=output_hash,
        )
        db.add(event)
        await db.flush()
        await db.commit()

        return {
            "id": str(event.id),
            "event_type": event.event_type,
            "is_anomalous": event.is_anomalous,
            "created_at": event.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest monitoring event: {str(e)}",
        )


@router.get("/events")
async def list_monitor_events(
    limit: int = 100,
    offset: int = 0,
    agent_id: Optional[str] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    hours_back: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List monitoring events for the current org (Build Rule 5)."""
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        query = select(MonitorEvent).where(
            and_(
                MonitorEvent.org_id == current_user.org_id,
                MonitorEvent.created_at >= cutoff_time,
            )
        )

        if agent_id:
            query = query.where(MonitorEvent.agent_id == UUID(agent_id))
        if event_type:
            query = query.where(MonitorEvent.event_type == event_type)
        if severity:
            query = query.where(MonitorEvent.severity == severity)

        query = (
            query.order_by(MonitorEvent.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        events = result.scalars().all()

        # Get total count
        count_query = select(MonitorEvent).where(
            and_(
                MonitorEvent.org_id == current_user.org_id,
                MonitorEvent.created_at >= cutoff_time,
            )
        )
        if agent_id:
            count_query = count_query.where(MonitorEvent.agent_id == UUID(agent_id))
        if event_type:
            count_query = count_query.where(MonitorEvent.event_type == event_type)
        if severity:
            count_query = count_query.where(MonitorEvent.severity == severity)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "hours_back": hours_back,
            "events": [
                {
                    "id": str(e.id),
                    "agent_id": str(e.agent_id) if e.agent_id else None,
                    "event_type": e.event_type,
                    "severity": e.severity,
                    "is_anomalous": e.is_anomalous,
                    "anomaly_score": e.anomaly_score,
                    "anomaly_reason": e.anomaly_reason,
                    "created_at": e.created_at.isoformat(),
                }
                for e in events
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list monitoring events: {str(e)}",
        )


@router.get("/events/{event_id}")
async def get_event_details(
    event_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed monitoring event information (Build Rule 5: org-scoped)."""
    try:
        result = await db.execute(
            select(MonitorEvent).where(
                MonitorEvent.id == UUID(event_id),
                MonitorEvent.org_id == current_user.org_id,
            )
        )
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return {
            "id": str(event.id),
            "org_id": str(event.org_id),
            "agent_id": str(event.agent_id) if event.agent_id else None,
            "event_type": event.event_type,
            "severity": event.severity,
            "is_anomalous": event.is_anomalous,
            "anomaly_score": event.anomaly_score,
            "anomaly_reason": event.anomaly_reason,
            "input_hash": event.input_hash,
            "output_hash": event.output_hash,
            "metadata": event.metadata_ or {},
            "created_at": event.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get event details: {str(e)}",
        )


@router.get("/anomalies")
async def list_anomalies(
    limit: int = 100,
    offset: int = 0,
    agent_id: Optional[str] = None,
    hours_back: int = 24,
    min_anomaly_score: float = 0.0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List anomaly events only (where is_anomalous=True) for the current org."""
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        query = select(MonitorEvent).where(
            and_(
                MonitorEvent.org_id == current_user.org_id,
                MonitorEvent.is_anomalous == True,
                MonitorEvent.created_at >= cutoff_time,
            )
        )

        if agent_id:
            query = query.where(MonitorEvent.agent_id == UUID(agent_id))

        if min_anomaly_score > 0:
            query = query.where(MonitorEvent.anomaly_score >= min_anomaly_score)

        query = (
            query.order_by(MonitorEvent.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        anomalies = result.scalars().all()

        # Get total count
        count_query = select(MonitorEvent).where(
            and_(
                MonitorEvent.org_id == current_user.org_id,
                MonitorEvent.is_anomalous == True,
                MonitorEvent.created_at >= cutoff_time,
            )
        )
        if agent_id:
            count_query = count_query.where(MonitorEvent.agent_id == UUID(agent_id))
        if min_anomaly_score > 0:
            count_query = count_query.where(
                MonitorEvent.anomaly_score >= min_anomaly_score
            )
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "hours_back": hours_back,
            "anomalies": [
                {
                    "id": str(a.id),
                    "agent_id": str(a.agent_id) if a.agent_id else None,
                    "event_type": a.event_type,
                    "severity": a.severity,
                    "anomaly_score": a.anomaly_score,
                    "anomaly_reason": a.anomaly_reason,
                    "created_at": a.created_at.isoformat(),
                }
                for a in anomalies
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list anomalies: {str(e)}",
        )


@router.get("/dashboard")
async def monitoring_dashboard(
    hours_back: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get monitoring dashboard stats across all agents and scans.
    Returns: event counts, anomaly rate, top event types, severity distribution.
    """
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)

        # Get all events
        result = await db.execute(
            select(MonitorEvent).where(
                and_(
                    MonitorEvent.org_id == current_user.org_id,
                    MonitorEvent.created_at >= cutoff_time,
                )
            )
        )
        all_events = result.scalars().all()

        # Get anomalies only
        anom_result = await db.execute(
            select(MonitorEvent).where(
                and_(
                    MonitorEvent.org_id == current_user.org_id,
                    MonitorEvent.is_anomalous == True,
                    MonitorEvent.created_at >= cutoff_time,
                )
            )
        )
        anomalies = anom_result.scalars().all()

        # Calculate stats
        total_events = len(all_events)
        total_anomalies = len(anomalies)
        anomaly_rate = (
            (total_anomalies / total_events * 100) if total_events > 0 else 0
        )

        # Event type breakdown
        event_type_counts = {}
        for event in all_events:
            event_type_counts[event.event_type] = (
                event_type_counts.get(event.event_type, 0) + 1
            )

        # Severity breakdown
        severity_counts = {}
        for event in all_events:
            if event.severity:
                severity_counts[event.severity] = (
                    severity_counts.get(event.severity, 0) + 1
                )

        # Top anomaly reasons
        anomaly_reasons = {}
        for event in anomalies:
            if event.anomaly_reason:
                anomaly_reasons[event.anomaly_reason] = (
                    anomaly_reasons.get(event.anomaly_reason, 0) + 1
                )
        top_anomaly_reasons = sorted(
            anomaly_reasons.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "hours_back": hours_back,
            "total_events": total_events,
            "total_anomalies": total_anomalies,
            "anomaly_rate_percent": round(anomaly_rate, 2),
            "event_type_distribution": event_type_counts,
            "severity_distribution": severity_counts,
            "top_anomaly_reasons": [
                {"reason": reason, "count": count}
                for reason, count in top_anomaly_reasons
            ],
            "avg_anomaly_score": (
                round(
                    sum(e.anomaly_score or 0 for e in anomalies) / total_anomalies, 2
                )
                if total_anomalies > 0
                else 0.0
            ),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get monitoring dashboard: {str(e)}",
        )


@router.post("/continuous", status_code=201)
async def create_continuous_scan(
    target_id: str,
    attacks_per_hour: int = 5,
    daily_cost_cap_usd: float = 1.00,
    alert_on_new_vuln: bool = True,
    alert_on_regression: bool = True,
    categories: Optional[List[str]] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Configure continuous scanning for a target (Build Rule 5: org-scoped)."""
    try:
        # Verify target belongs to org
        target_result = await db.execute(
            select(Target).where(
                Target.id == UUID(target_id),
                Target.org_id == current_user.org_id,
            )
        )
        target = target_result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail="Target not found")

        # Check if continuous config already exists
        existing = await db.execute(
            select(ContinuousScanConfig).where(
                ContinuousScanConfig.target_id == target.id,
                ContinuousScanConfig.org_id == current_user.org_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="Continuous scan already configured for this target",
            )

        config = ContinuousScanConfig(
            org_id=current_user.org_id,
            target_id=target.id,
            attacks_per_hour=attacks_per_hour,
            daily_cost_cap_usd=daily_cost_cap_usd,
            alert_on_new_vuln=alert_on_new_vuln,
            alert_on_regression=alert_on_regression,
            categories=categories or [],
            is_active=True,
        )
        db.add(config)
        await db.flush()
        await db.commit()

        return {
            "id": str(config.id),
            "target_id": str(config.target_id),
            "attacks_per_hour": config.attacks_per_hour,
            "daily_cost_cap_usd": config.daily_cost_cap_usd,
            "alert_on_new_vuln": config.alert_on_new_vuln,
            "alert_on_regression": config.alert_on_regression,
            "is_active": config.is_active,
            "created_at": config.created_at.isoformat() if config.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create continuous scan: {str(e)}",
        )


@router.get("/continuous")
async def list_continuous_scans(
    limit: int = 50,
    offset: int = 0,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List continuous scan configurations for the current org (Build Rule 5)."""
    try:
        query = select(ContinuousScanConfig).where(
            ContinuousScanConfig.org_id == current_user.org_id
        )
        if is_active is not None:
            query = query.where(ContinuousScanConfig.is_active == is_active)

        query = (
            query.order_by(ContinuousScanConfig.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        configs = result.scalars().all()

        # Get total count
        count_query = select(ContinuousScanConfig).where(
            ContinuousScanConfig.org_id == current_user.org_id
        )
        if is_active is not None:
            count_query = count_query.where(ContinuousScanConfig.is_active == is_active)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "configs": [
                {
                    "id": str(c.id),
                    "target_id": str(c.target_id),
                    "attacks_per_hour": c.attacks_per_hour,
                    "daily_cost_cap_usd": c.daily_cost_cap_usd,
                    "is_active": c.is_active,
                    "alert_on_new_vuln": c.alert_on_new_vuln,
                    "alert_on_regression": c.alert_on_regression,
                    "last_run_at": c.last_run_at.isoformat() if c.last_run_at else None,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in configs
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list continuous scans: {str(e)}",
        )
