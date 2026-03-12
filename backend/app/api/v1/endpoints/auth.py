"""
Auth endpoints: register, login, logout, refresh, me, api-keys.
Build Rule: JWT access=15min, refresh=30 days.
"""
from datetime import timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_current_active_user, get_db
from app.core.security import (
    create_access_token, create_refresh_token, decode_token,
    generate_api_key, hash_password, verify_password
)
from app.database import get_db
from app.models.api_key import APIKey
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import (
    APIKeyCreateRequest, APIKeyResponse, LoginRequest,
    RefreshRequest, RegisterRequest, TokenResponse, UserResponse
)
import re
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])


def make_slug(name: str) -> str:
    """Convert org name to URL-safe slug."""
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return slug[:100]


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register new user and organization."""
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create org
    base_slug = make_slug(payload.org_name)
    slug = base_slug
    counter = 1
    while True:
        existing_org = await db.execute(select(Organization).where(Organization.slug == slug))
        if not existing_org.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    org = Organization(
        name=payload.org_name,
        slug=slug,
        plan_tier="free",
        scans_limit=settings.RATE_LIMIT_FREE,
    )
    db.add(org)
    await db.flush()

    # Create user as owner
    user = User(
        org_id=org.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role="owner",
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    token_data = {
        "sub": str(user.id),
        "org_id": str(org.id),
        "role": user.role,
    }

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        token_type="bearer",
        user_id=str(user.id),
        org_id=str(org.id),
        role=user.role,
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account disabled")

    token_data = {
        "sub": str(user.id),
        "org_id": str(user.org_id),
        "role": user.role,
    }

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        token_type="bearer",
        user_id=str(user.id),
        org_id=str(user.org_id),
        role=user.role,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Exchange refresh token for new access token."""
    from jose import JWTError
    try:
        token_data = decode_token(payload.refresh_token)
        if token_data.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user_id = token_data.get("sub")
    result = await db.execute(select(User).where(User.id == UUID(user_id), User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_token_data = {"sub": str(user.id), "org_id": str(user.org_id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(new_token_data),
        refresh_token=create_refresh_token(new_token_data),
        token_type="bearer",
        user_id=str(user.id),
        org_id=str(user.org_id),
        role=user.role,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        org_id=str(current_user.org_id),
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )


@router.post("/api-keys", response_model=APIKeyResponse, status_code=201)
async def create_api_key(
    payload: APIKeyCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new API key for programmatic access."""
    from datetime import timezone
    full_key, key_prefix, key_hash = generate_api_key()
    expires_at = None
    if payload.expires_in_days:
        from datetime import datetime
        expires_at = datetime.utcnow() + timedelta(days=payload.expires_in_days)

    api_key_obj = APIKey(
        org_id=current_user.org_id,
        user_id=current_user.id,
        name=payload.name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        is_active=True,
        expires_at=expires_at,
    )
    db.add(api_key_obj)
    await db.flush()

    return APIKeyResponse(
        id=str(api_key_obj.id),
        name=api_key_obj.name,
        key_prefix=key_prefix,
        full_key=full_key,  # Only returned once at creation
        is_active=True,
        created_at=str(api_key_obj.created_at),
    )


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all API keys for current user."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.org_id == current_user.org_id,
            APIKey.user_id == current_user.id,
        )
    )
    keys = result.scalars().all()
    return [
        APIKeyResponse(
            id=str(k.id),
            name=k.name,
            key_prefix=k.key_prefix,
            is_active=k.is_active,
            created_at=str(k.created_at),
        )
        for k in keys
    ]


@router.delete("/api-keys/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke an API key."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == UUID(key_id),
            APIKey.org_id == current_user.org_id,
            APIKey.user_id == current_user.id,
        )
    )
    api_key_obj = result.scalar_one_or_none()
    if not api_key_obj:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key_obj.is_active = False
