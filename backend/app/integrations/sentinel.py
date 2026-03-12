"""
Microsoft Sentinel Integration — send findings to Azure Monitor.
Build Rule 11: Integration failures don't crash the platform.
"""
import json
import logging
import asyncio
import hmac
import hashlib
import base64
from datetime import datetime, timezone
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)


class SentinelIntegration:
    """
    Sends AgentRed findings to Microsoft Sentinel via Azure Monitor Data Collection API.

    Configuration:
        workspace_id (str): Azure Log Analytics workspace ID
        shared_key (str): Log Analytics workspace shared key (primary or secondary)
        dce_endpoint (str): Data Collection Endpoint URL (optional, for newer method)
        dcr_immutable_id (str): Data Collection Rule immutable ID (optional)
        custom_log_table (str): Custom log table name (default: "AgentRedFindings_CL")
    """

    def __init__(self, workspace_id: str, shared_key: str,
                 dce_endpoint: Optional[str] = None,
                 dcr_immutable_id: Optional[str] = None,
                 custom_log_table: str = "AgentRedFindings_CL",
                 timeout: int = 10):
        """Initialize Sentinel integration."""
        self.workspace_id = workspace_id
        self.shared_key = shared_key
        self.dce_endpoint = dce_endpoint
        self.dcr_immutable_id = dcr_immutable_id
        self.custom_log_table = custom_log_table
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create session."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self._session

    def _build_signature(self, method: str, content_length: int, content_type: str,
                        date: str, resource: str) -> str:
        """Build Azure Monitor Data Collection API signature."""
        x_headers = f"x-ms-date:{date}"
        string_to_hash = f"{method}\n{content_length}\n{content_type}\n{x_headers}\n{resource}"
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, hashlib.sha256).digest()
        ).decode()
        return f"SharedKey {self.workspace_id}:{encoded_hash}"

    async def send_finding(self, finding: dict) -> bool:
        """
        Send a finding to Microsoft Sentinel.

        Args:
            finding (dict): Finding data with keys: id, name, description, severity, evidence, etc.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            session = self._get_session()
            json_data = json.dumps(finding)

            method = "POST"
            content_type = "application/json"
            resource = f"/api/logs"
            date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

            signature = self._build_signature(
                method,
                len(json_data),
                content_type,
                date,
                resource
            )

            url = f"https://{self.workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"

            headers = {
                "Authorization": signature,
                "Log-Type": self.custom_log_table,
                "x-ms-date": date,
                "Content-Type": content_type,
                "x-ms-AzureResourceId": f"/subscriptions/agentred/resourcegroups/agentred/providers/microsoft.operationalinsights/workspaces/{self.workspace_id}",
            }

            async with session.post(
                url,
                data=json_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status in (200, 202):
                    logger.info(f"Sent finding {finding.get('id', 'unknown')} to Sentinel")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Sentinel error {resp.status}: {error_text}")
                    return False

        except asyncio.TimeoutError:
            logger.error(f"Sentinel timeout after {self.timeout}s")
            return False
        except Exception as e:
            logger.error(f"Sentinel integration error: {e}")
            return False

    async def send_scan_complete(self, scan: dict) -> bool:
        """
        Send scan completion event to Sentinel.

        Args:
            scan (dict): Scan summary with keys: id, target, findings_count, risk_score, status, etc.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            session = self._get_session()
            event_data = {
                "scan_id": scan.get("id"),
                "target": scan.get("target"),
                "findings_count": scan.get("findings_count", 0),
                "risk_score": scan.get("risk_score", 0.0),
                "status": scan.get("status", "completed"),
                "duration_seconds": scan.get("duration_seconds", 0),
                "severity_breakdown": json.dumps(scan.get("severity_breakdown", {})),
                "completed_at": scan.get("completed_at", datetime.utcnow().isoformat()),
                "event_type": "scan_complete",
            }
            json_data = json.dumps(event_data)

            method = "POST"
            content_type = "application/json"
            resource = "/api/logs"
            date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

            signature = self._build_signature(
                method,
                len(json_data),
                content_type,
                date,
                resource
            )

            url = f"https://{self.workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"

            headers = {
                "Authorization": signature,
                "Log-Type": "AgentRedScanComplete_CL",
                "x-ms-date": date,
                "Content-Type": content_type,
            }

            async with session.post(
                url,
                data=json_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status in (200, 202):
                    logger.info(f"Sent scan complete event for {scan.get('id', 'unknown')} to Sentinel")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Sentinel error {resp.status}: {error_text}")
                    return False

        except asyncio.TimeoutError:
            logger.error(f"Sentinel timeout after {self.timeout}s")
            return False
        except Exception as e:
            logger.error(f"Sentinel scan complete integration error: {e}")
            return False

    async def test_connection(self) -> bool:
        """
        Test connectivity to Microsoft Sentinel.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            session = self._get_session()
            test_data = {
                "message": "AgentRed connectivity test",
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
            }
            json_data = json.dumps(test_data)

            method = "POST"
            content_type = "application/json"
            resource = "/api/logs"
            date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

            signature = self._build_signature(
                method,
                len(json_data),
                content_type,
                date,
                resource
            )

            url = f"https://{self.workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"

            headers = {
                "Authorization": signature,
                "Log-Type": "AgentRedTest_CL",
                "x-ms-date": date,
                "Content-Type": content_type,
            }

            async with session.post(
                url,
                data=json_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status in (200, 202):
                    logger.info("Sentinel connection test successful")
                    return True
                else:
                    logger.error(f"Sentinel test failed: {resp.status}")
                    return False

        except Exception as e:
            logger.error(f"Sentinel connection test failed: {e}")
            return False

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
