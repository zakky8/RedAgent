"""Targets API resource."""
from typing import Optional


class TargetsResource:
    """Manage target configurations."""

    def __init__(self, client):
        self._c = client

    def create(
        self,
        name: str,
        target_type: str,
        endpoint: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Create a new target."""
        payload = {
            "name": name,
            "target_type": target_type,
            "endpoint": endpoint,
            **kwargs
        }
        if api_key:
            payload["api_key"] = api_key
        return self._c._request("POST", "/targets", json=payload)

    def get(self, target_id: str) -> dict:
        """Get target by ID."""
        return self._c._request("GET", f"/targets/{target_id}")

    def list(self) -> list:
        """List all targets."""
        result = self._c._request("GET", "/targets")
        return result.get("items", []) if isinstance(result, dict) else result

    def delete(self, target_id: str) -> dict:
        """Delete a target."""
        return self._c._request("DELETE", f"/targets/{target_id}")

    def test_connection(self, target_id: str) -> dict:
        """Test connection to target."""
        return self._c._request("POST", f"/targets/{target_id}/test", json={})

    def update(self, target_id: str, **kwargs) -> dict:
        """Update target configuration."""
        return self._c._request("PATCH", f"/targets/{target_id}", json=kwargs)
