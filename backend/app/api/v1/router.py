"""
Main API router — assembles all v1 endpoints.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    targets,
    scans,
    attacks,
    reports,
    compliance,
    monitoring,
    agents,
    integrations,
    shadow_ai,
    dlp,
    sbom,
    skills,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(targets.router)
api_router.include_router(scans.router)
api_router.include_router(attacks.router)
api_router.include_router(reports.router)
api_router.include_router(compliance.router)
api_router.include_router(monitoring.router)
api_router.include_router(agents.router)

# New endpoint routers
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(shadow_ai.router, prefix="/shadow-ai", tags=["shadow-ai"])
api_router.include_router(dlp.router, prefix="/dlp", tags=["dlp"])
api_router.include_router(sbom.router, prefix="/sbom", tags=["sbom"])
api_router.include_router(skills.router, prefix="/skills", tags=["skills"])
