"""
Agent registry and management endpoints.
Build Rule 5: ALL queries org-scoped by org_id.
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.agent_registry import AgentRegistry

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", status_code=201)
async def register_agent(
    agent_name: str,
    agent_type: str,
    endpoint_url: str,
    version: Optional[str] = None,
    framework: Optional[str] = None,
    description: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    authorized_tools: Optional[List[str]] = None,
    permissions: Optional[dict] = None,
    sdk_version: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Register a new AI agent in the platform (Build Rule 5: org-scoped)."""
    try:
        # Check if agent name already exists in org
        existing = await db.execute(
            select(AgentRegistry).where(
                AgentRegistry.agent_name == agent_name,
                AgentRegistry.org_id == current_user.org_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail=f"Agent '{agent_name}' already registered in this organization",
            )

        agent = AgentRegistry(
            org_id=current_user.org_id,
            agent_name=agent_name,
            agent_type=agent_type,
            endpoint_url=endpoint_url,
            version=version,
            framework=framework,
            description=description,
            capabilities=capabilities or [],
            authorized_tools=authorized_tools or [],
            permissions=permissions or {},
            sdk_version=sdk_version,
            status="active",
            last_seen_at=datetime.now(timezone.utc),
        )
        db.add(agent)
        await db.flush()
        await db.commit()

        return {
            "id": str(agent.id),
            "org_id": str(agent.org_id),
            "agent_name": agent.agent_name,
            "agent_type": agent.agent_type,
            "endpoint_url": agent.endpoint_url,
            "version": agent.version,
            "framework": agent.framework,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "authorized_tools": agent.authorized_tools,
            "status": agent.status,
            "kill_switch_triggered": agent.kill_switch_triggered,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register agent: {str(e)}",
        )


@router.get("")
async def list_agents(
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    agent_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all registered agents for the current org (Build Rule 5)."""
    try:
        query = select(AgentRegistry).where(
            AgentRegistry.org_id == current_user.org_id
        )
        if status_filter:
            query = query.where(AgentRegistry.status == status_filter)
        if agent_type:
            query = query.where(AgentRegistry.agent_type == agent_type)

        query = (
            query.order_by(AgentRegistry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        agents = result.scalars().all()

        # Get total count
        count_query = select(AgentRegistry).where(
            AgentRegistry.org_id == current_user.org_id
        )
        if status_filter:
            count_query = count_query.where(AgentRegistry.status == status_filter)
        if agent_type:
            count_query = count_query.where(AgentRegistry.agent_type == agent_type)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "agents": [
                {
                    "id": str(a.id),
                    "agent_name": a.agent_name,
                    "agent_type": a.agent_type,
                    "framework": a.framework,
                    "version": a.version,
                    "status": a.status,
                    "kill_switch_triggered": a.kill_switch_triggered,
                    "last_seen_at": a.last_seen_at.isoformat() if a.last_seen_at else None,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in agents
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list agents: {str(e)}",
        )


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get agent details by ID (Build Rule 5: org-scoped)."""
    try:
        result = await db.execute(
            select(AgentRegistry).where(
                AgentRegistry.id == UUID(agent_id),
                AgentRegistry.org_id == current_user.org_id,
            )
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        return {
            "id": str(agent.id),
            "org_id": str(agent.org_id),
            "agent_name": agent.agent_name,
            "agent_type": agent.agent_type,
            "framework": agent.framework,
            "version": agent.version,
            "description": agent.description,
            "capabilities": agent.capabilities,
            "authorized_tools": agent.authorized_tools,
            "permissions": agent.permissions,
            "status": agent.status,
            "kill_switch_triggered": agent.kill_switch_triggered,
            "kill_switch_reason": agent.kill_switch_reason,
            "endpoint_url": agent.endpoint_url,
            "sdk_version": agent.sdk_version,
            "last_seen_at": agent.last_seen_at.isoformat() if agent.last_seen_at else None,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "updated_at": agent.updated_at.isoformat() if agent.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent: {str(e)}",
        )


@router.patch("/{agent_id}")
async def update_agent(
    agent_id: str,
    agent_name: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    authorized_tools: Optional[List[str]] = None,
    permissions: Optional[dict] = None,
    endpoint_url: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update agent configuration (Build Rule 5: org-scoped)."""
    try:
        result = await db.execute(
            select(AgentRegistry).where(
                AgentRegistry.id == UUID(agent_id),
                AgentRegistry.org_id == current_user.org_id,
            )
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Update fields if provided
        if agent_name is not None:
            agent.agent_name = agent_name
        if description is not None:
            agent.description = description
        if version is not None:
            agent.version = version
        if capabilities is not None:
            agent.capabilities = capabilities
        if authorized_tools is not None:
            agent.authorized_tools = authorized_tools
        if permissions is not None:
            agent.permissions = permissions
        if endpoint_url is not None:
            agent.endpoint_url = endpoint_url

        agent.updated_at = datetime.now(timezone.utc)
        await db.commit()

        return {
            "id": str(agent.id),
            "agent_name": agent.agent_name,
            "description": agent.description,
            "version": agent.version,
            "capabilities": agent.capabilities,
            "authorized_tools": agent.authorized_tools,
            "permissions": agent.permissions,
            "endpoint_url": agent.endpoint_url,
            "updated_at": agent.updated_at.isoformat() if agent.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update agent: {str(e)}",
        )


@router.post("/{agent_id}/kill-switch", status_code=200)
async def trigger_kill_switch(
    agent_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger kill switch for an agent — immediately stops execution.
    Sets kill_switch_triggered=True and status='killed'.
    Build Rule 5: org-scoped access control.
    """
    try:
        result = await db.execute(
            select(AgentRegistry).where(
                AgentRegistry.id == UUID(agent_id),
                AgentRegistry.org_id == current_user.org_id,
            )
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        if agent.kill_switch_triggered:
            raise HTTPException(
                status_code=409,
                detail="Kill switch already triggered for this agent",
            )

        # Trigger kill switch
        agent.kill_switch_triggered = True
        agent.kill_switch_reason = reason or "Kill switch triggered by user"
        agent.kill_switch_at = datetime.now(timezone.utc)
        agent.status = "killed"
        agent.updated_at = datetime.now(timezone.utc)
        await db.commit()

        return {
            "id": str(agent.id),
            "agent_name": agent.agent_name,
            "kill_switch_triggered": agent.kill_switch_triggered,
            "kill_switch_reason": agent.kill_switch_reason,
            "kill_switch_at": agent.kill_switch_at.isoformat() if agent.kill_switch_at else None,
            "status": agent.status,
            "message": "Kill switch triggered. Agent execution stopped.",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger kill switch: {str(e)}",
        )


@router.delete("/{agent_id}", status_code=204)
async def deregister_agent(
    agent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Deregister an agent from the platform (Build Rule 5: org-scoped)."""
    try:
        result = await db.execute(
            select(AgentRegistry).where(
                AgentRegistry.id == UUID(agent_id),
                AgentRegistry.org_id == current_user.org_id,
            )
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        await db.delete(agent)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deregister agent: {str(e)}",
        )
