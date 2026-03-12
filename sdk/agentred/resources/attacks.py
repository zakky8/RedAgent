"""Attacks API resource — browse available attacks."""
from typing import Optional, List


class AttacksResource:
    """Browse and filter available attacks."""

    def __init__(self, client):
        self._c = client

    def list(
        self,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """List available attacks with filtering."""
        params = {"limit": limit}
        if category:
            params["category"] = category
        if severity:
            params["severity"] = severity
        result = self._c._request("GET", "/attacks", params=params)
        return result.get("items", []) if isinstance(result, dict) else result

    def get(self, attack_id: str) -> dict:
        """Get attack details."""
        return self._c._request("GET", f"/attacks/{attack_id}")

    def get_categories(self) -> list:
        """List attack categories."""
        result = self._c._request("GET", "/attacks/categories")
        return result.get("items", []) if isinstance(result, dict) else result

    def get_by_category(self, category: str, limit: int = 100) -> list:
        """Get all attacks in a category."""
        return self.list(category=category, limit=limit)

    def get_by_severity(self, severity: str, limit: int = 100) -> list:
        """Get all attacks by severity level."""
        return self.list(severity=severity, limit=limit)
