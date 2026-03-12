"""Target management endpoints."""
import time
from typing import List
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db
from app.models.target import Target
from app.models.user import User
from app.schemas.target import TargetCreate, TargetResponse, TargetTestResponse, TargetUpdate

router = APIRouter(prefix="/targets", tags=["targets"])


@router.post("", response_model=TargetResponse, status_code=201)
async def create_target(
    payload: TargetCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    target = Target(
        org_id=current_user.org_id,
        **payload.model_dump(),
    )
    db.add(target)
    await db.flush()
    return _to_response(target)


@router.get("", response_model=List[TargetResponse])
async def list_targets(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Target).where(
            Target.org_id == current_user.org_id,  # Build Rule 5
            Target.is_active == True,
        ).order_by(Target.created_at.desc())
    )
    return [_to_response(t) for t in result.scalars().all()]


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Target).where(
            Target.id == UUID(target_id),
            Target.org_id == current_user.org_id,
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Target not found")
    return _to_response(t)


@router.patch("/{target_id}", response_model=TargetResponse)
async def update_target(
    target_id: str,
    payload: TargetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Target).where(
            Target.id == UUID(target_id),
            Target.org_id == current_user.org_id,
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Target not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    await db.commit()
    return _to_response(t)


@router.delete("/{target_id}", status_code=204)
async def delete_target(
    target_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Target).where(
            Target.id == UUID(target_id),
            Target.org_id == current_user.org_id,
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Target not found")
    t.is_active = False  # Soft delete
    await db.commit()


@router.post("/{target_id}/test", response_model=TargetTestResponse)
async def test_target(
    target_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Test connectivity to target AI system."""
    result = await db.execute(
        select(Target).where(
            Target.id == UUID(target_id),
            Target.org_id == current_user.org_id,
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Target not found")
    if not t.endpoint_url:
        return TargetTestResponse(success=False, latency_ms=0, error="No endpoint URL configured")

    start = time.time()
    try:
        headers = {}
        if t.auth_config and t.auth_config.get("api_key"):
            headers["Authorization"] = f"Bearer {t.auth_config['api_key']}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                t.endpoint_url,
                json={"messages": [{"role": "user", "content": "Hello"}]},
                headers=headers,
            )
        latency = int((time.time() - start) * 1000)
        return TargetTestResponse(success=resp.status_code < 400, latency_ms=latency)
    except Exception as e:
        return TargetTestResponse(
            success=False,
            latency_ms=int((time.time() - start) * 1000),
            error=str(e),
        )


def _to_response(t: Target) -> TargetResponse:
    return TargetResponse(
        id=str(t.id),
        org_id=str(t.org_id),
        name=t.name,
        description=t.description,
        target_type=t.target_type,
        endpoint_url=t.endpoint_url,
        model_type=t.model_type,
        framework=t.framework,
        memory_enabled=t.memory_enabled,
        is_multi_agent=t.is_multi_agent,
        risk_score=t.risk_score,
        is_active=t.is_active,
        last_scan_at=str(t.last_scan_at) if t.last_scan_at else None,
        created_at=str(t.created_at),
    )
