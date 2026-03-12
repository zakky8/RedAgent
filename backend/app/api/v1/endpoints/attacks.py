"""
Attack Library endpoints — browse, filter, and get attack details.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.core.deps import get_current_active_user
from app.models.user import User
from app.attacks.registry import attack_registry

router = APIRouter(prefix="/attacks", tags=["attacks"])


@router.get("")
async def list_attacks(
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    scan_mode: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    current_user: User = Depends(get_current_active_user),
):
    """List all available attacks with optional filtering."""
    try:
        if scan_mode:
            attacks = attack_registry.get_for_scan_mode(scan_mode)
        elif category:
            attacks = attack_registry.get_by_category(category)
        elif severity:
            attacks = attack_registry.get_by_severity(severity)
        else:
            attacks = attack_registry.get_all()

        if search:
            search_lower = search.lower()
            attacks = [
                a
                for a in attacks
                if search_lower in a.name.lower()
                or search_lower in a.description.lower()
            ]

        total = len(attacks)
        attacks_page = attacks[offset : offset + limit]

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "attacks": [
                {
                    "attack_id": cls.attack_id,
                    "name": cls.name,
                    "category": cls.category,
                    "severity": cls.severity,
                    "description": cls.description,
                    "framework_mapping": cls.framework_mapping,
                }
                for cls in attacks_page
            ],
        }
    except Exception as e:
        return {
            "total": 0,
            "offset": offset,
            "limit": limit,
            "attacks": [],
            "error": str(e),
        }


@router.get("/categories")
async def list_categories(current_user: User = Depends(get_current_active_user)):
    """List all attack categories with counts."""
    try:
        all_attacks = attack_registry.get_all()
        categories: dict[str, int] = {}
        for cls in all_attacks:
            categories[cls.category] = categories.get(cls.category, 0) + 1
        return {
            "categories": [
                {"name": cat, "count": count}
                for cat, count in sorted(categories.items())
            ]
        }
    except Exception as e:
        return {"categories": [], "error": str(e)}


@router.get("/stats")
async def attack_stats(current_user: User = Depends(get_current_active_user)):
    """Get overall attack library statistics."""
    try:
        all_attacks = attack_registry.get_all()
        severity_counts: dict[str, int] = {}
        for cls in all_attacks:
            severity_counts[cls.severity] = severity_counts.get(cls.severity, 0) + 1
        return {
            "total_attacks": len(all_attacks),
            "total_categories": len(attack_registry.list_categories()),
            "severity_breakdown": severity_counts,
        }
    except Exception as e:
        return {"total_attacks": 0, "error": str(e)}


@router.get("/{attack_id}")
async def get_attack(
    attack_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get details of a specific attack."""
    try:
        attack_cls = attack_registry.get(attack_id)
        if not attack_cls:
            raise HTTPException(
                status_code=404, detail=f"Attack '{attack_id}' not found"
            )
        instance = attack_cls()
        return {
            "attack_id": attack_cls.attack_id,
            "name": attack_cls.name,
            "category": attack_cls.category,
            "severity": attack_cls.severity,
            "description": attack_cls.description,
            "framework_mapping": attack_cls.framework_mapping,
            "remediation": instance.get_remediation(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
