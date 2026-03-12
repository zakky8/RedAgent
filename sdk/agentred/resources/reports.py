"""Reports API resource."""
from typing import Optional, List
import httpx


class ReportsResource:
    """Generate and download reports."""

    def __init__(self, client):
        self._c = client

    def generate(
        self,
        scan_id: str,
        report_type: str = "executive",
        frameworks: Optional[List[str]] = None
    ) -> dict:
        """Generate a report for a scan."""
        payload = {
            "scan_id": scan_id,
            "report_type": report_type,
            "frameworks": frameworks or []
        }
        return self._c._request("POST", "/reports", json=payload)

    def get(self, report_id: str) -> dict:
        """Get report metadata by ID."""
        return self._c._request("GET", f"/reports/{report_id}")

    def list(self, scan_id: Optional[str] = None) -> list:
        """List reports with optional filter by scan."""
        params = {}
        if scan_id:
            params["scan_id"] = scan_id
        result = self._c._request("GET", "/reports", params=params)
        return result.get("items", []) if isinstance(result, dict) else result

    def download(self, report_id: str, output_path: str) -> None:
        """Download report PDF to file."""
        url = f"{self._c.base_url}/api/v1/reports/{report_id}/download"
        with httpx.Client(
            headers={"Authorization": f"Bearer {self._c.api_key}"},
            timeout=300
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(response.content)

    def delete(self, report_id: str) -> dict:
        """Delete a report."""
        return self._c._request("DELETE", f"/reports/{report_id}")
