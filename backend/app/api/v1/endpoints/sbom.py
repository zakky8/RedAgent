"""SBOM generation endpoints."""
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
import json

from app.core.deps import get_current_user
from app.models.user import User
from app.core.sbom_generator import SBOMGenerator, AIComponent

router = APIRouter()


class SBOMRequest(BaseModel):
    system_name: str
    version: str = "1.0.0"
    requirements_content: str = ""
    components: list[dict] = []


@router.post("/generate")
async def generate_sbom(
    data: SBOMRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a Software Bill of Materials for an AI system."""
    generator = SBOMGenerator(data.system_name, data.version)

    if data.requirements_content:
        generator.from_requirements(data.requirements_content)

    for comp_data in data.components:
        comp = AIComponent(
            name=comp_data.get("name", ""),
            version=comp_data.get("version", "unknown"),
            component_type=comp_data.get("type", "library"),
            supplier=comp_data.get("supplier", "Unknown"),
            license=comp_data.get("license", "Unknown")
        )
        generator.add_component(comp)

    cyclonedx = generator.to_cyclonedx()
    risk_summary = generator.get_risk_summary()

    return {
        "system_name": data.system_name,
        "version": data.version,
        "risk_summary": risk_summary,
        "sbom_preview": cyclonedx,
        "component_count": len(generator.components)
    }


@router.post("/generate/export")
async def export_sbom(
    data: SBOMRequest,
    format: str = "cyclonedx",
    current_user: User = Depends(get_current_user)
):
    """Export SBOM in CycloneDX or SPDX format."""
    generator = SBOMGenerator(data.system_name, data.version)
    if data.requirements_content:
        generator.from_requirements(data.requirements_content)

    if format == "spdx":
        sbom_data = generator.to_spdx()
        filename = f"sbom-{data.system_name}-spdx.json"
    else:
        sbom_data = generator.to_cyclonedx()
        filename = f"sbom-{data.system_name}-cyclonedx.json"

    return Response(
        content=json.dumps(sbom_data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
