"""Integration management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import json

from app.core.deps import get_current_user, get_db
from app.models.integration import Integration
from app.models.user import User
from sqlalchemy import select

router = APIRouter()


class CreateIntegrationRequest(BaseModel):
    name: str
    integration_type: str
    config: dict
    enabled: bool = True


@router.get("")
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all integrations for the current organization."""
    result = await db.execute(
        select(Integration).where(Integration.org_id == current_user.org_id)
    )
    integrations = result.scalars().all()
    return [
        {
            "id": str(i.id),
            "name": i.name,
            "integration_type": i.integration_type,
            "enabled": i.enabled,
            "created_at": i.created_at.isoformat()
        }
        for i in integrations
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_integration(
    data: CreateIntegrationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new integration."""
    import uuid
    integration = Integration(
        id=uuid.uuid4(),
        org_id=current_user.org_id,
        name=data.name,
        integration_type=data.integration_type,
        config_encrypted=json.dumps(data.config),
        enabled=data.enabled
    )
    db.add(integration)
    await db.commit()
    await db.refresh(integration)
    return {
        "id": str(integration.id),
        "name": integration.name,
        "message": "Integration created"
    }


@router.post("/{integration_id}/test")
async def test_integration(
    integration_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test connection to an integration."""
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.org_id == current_user.org_id
        )
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    from app.integrations import INTEGRATION_REGISTRY
    if integration.integration_type not in INTEGRATION_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown integration type: {integration.integration_type}"
        )

    config = json.loads(integration.config_encrypted or "{}")
    try:
        cls = INTEGRATION_REGISTRY[integration.integration_type]
        instance = cls(**config)
        result = await instance.test_connection()
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
