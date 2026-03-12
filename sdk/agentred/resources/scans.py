"""Scans API resource."""
import time
from typing import Optional, List
from ..exceptions import ScanError


class ScansResource:
    """Manage scan lifecycle."""

    def __init__(self, client):
        self._c = client

    def create(
        self,
        target_id: str,
        mode: str = "standard",
        categories: Optional[List[str]] = None,
        **kwargs
    ) -> dict:
        """Create a new scan."""
        payload = {
            "target_id": target_id,
            "mode": mode,
            "categories": categories or [],
            **kwargs
        }
        return self._c._request("POST", "/scans", json=payload)

    def get(self, scan_id: str) -> dict:
        """Get scan by ID."""
        return self._c._request("GET", f"/scans/{scan_id}")

    def list(self, status: Optional[str] = None, limit: int = 20) -> list:
        """List scans with optional filtering."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        result = self._c._request("GET", "/scans", params=params)
        return result.get("items", []) if isinstance(result, dict) else result

    def cancel(self, scan_id: str) -> dict:
        """Cancel a running scan."""
        return self._c._request("POST", f"/scans/{scan_id}/stop")

    def wait(
        self,
        scan_id: str,
        poll_interval: int = 10,
        timeout: int = 3600
    ) -> dict:
        """Block until scan completes or timeout."""
        start = time.time()
        while True:
            scan = self.get(scan_id)
            if scan["status"] in ("completed", "failed", "cancelled"):
                return scan
            if time.time() - start > timeout:
                raise ScanError(f"Scan {scan_id} timed out after {timeout}s")
            time.sleep(poll_interval)

    def results(
        self,
        scan_id: str,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Get results/findings from a scan."""
        params = {"limit": limit}
        if severity:
            params["severity"] = severity
        result = self._c._request("GET", f"/scans/{scan_id}/results", params=params)
        return result.get("items", []) if isinstance(result, dict) else result

    def run(
        self,
        target_url: str,
        target_type: str = "openai_api",
        mode: str = "standard",
        categories: Optional[List[str]] = None,
        wait: bool = True,
        **kwargs
    ) -> dict:
        """Run a complete scan: create target, create scan, optionally wait."""
        target = self._c.targets.create(
            name=f"scan-{int(time.time())}",
            target_type=target_type,
            endpoint=target_url
        )
        scan = self.create(
            target_id=target["id"],
            mode=mode,
            categories=categories or [],
            **kwargs
        )
        if wait:
            return self.wait(scan["id"])
        return scan

    def stats(self, scan_id: str) -> dict:
        """Get scan statistics."""
        return self._c._request("GET", f"/scans/{scan_id}/stats")
