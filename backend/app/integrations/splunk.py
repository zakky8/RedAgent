"""
Splunk SIEM Integration — send findings to Splunk HEC.
Build Rule 11: Integration failures don't crash the platform.
"""
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)


class SplunkIntegration:
    """
    Sends AgentRed findings and scan events to Splunk HEC (HTTP Event Collector).

    Configuration:
        hec_url (str): Splunk HEC endpoint, e.g. https://splunk.example.com:8088/services/collector
        hec_token (str): HEC authentication token
        source (str): Splunk source field (default: "agentred")
        sourcetype (str): Splunk sourcetype (default: "agentred:finding")
        index (str): Splunk index name (default: "security")
    """

    def __init__(self, hec_url: str, hec_token: str, source: str = "agentred",
                 sourcetype: str = "agentred:finding", index: str = "security",
                 verify_ssl: bool = True, timeout: int = 10):
        """Initialize Splunk integration."""
        self.hec_url = hec_url
        self.hec_token = hec_token
        self.source = source
        self.sourcetype = sourcetype
        self.index = index
        self.verify_ssl = verify_ssl
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

    def _format_event(self, data: dict, sourcetype: str = None, event_type: str = "finding") -> dict:
        """Format data as Splunk HEC event."""
        return {
            "event": data,
            "source": self.source,
            "sourcetype": sourcetype or self.sourcetype,
            "index": self.index,
            "time": datetime.utcnow().timestamp(),
            "fields": {
                "event_type": event_type,
                "severity": data.get("severity", "unknown"),
            }
        }

    async def send_finding(self, finding: dict) -> bool:
        """
        Send a single finding to Splunk.

        Args:
            finding (dict): Finding data with keys: id, name, description, severity, evidence, etc.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            session = self._get_session()
            event = self._format_event(finding, event_type="finding")

            headers = {
                "Authorization": f"Splunk {self.hec_token}",
                "Content-Type": "application/json"
            }

            async with session.post(
                self.hec_url,
                json=event,
                headers=headers,
                verify_ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status in (200, 201):
                    logger.info(f"Sent finding {finding.get('id', 'unknown')} to Splunk")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Splunk HEC error {resp.status}: {error_text}")
                    return False

        except asyncio.TimeoutError:
            logger.error(f"Splunk timeout after {self.timeout}s")
            return False
        except Exception as e:
            logger.error(f"Splunk integration error: {e}")
            return False

    async def send_scan_complete(self, scan: dict) -> bool:
        """
        Send scan completion event to Splunk.

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
                "severity_breakdown": scan.get("severity_breakdown", {}),
                "completed_at": scan.get("completed_at", datetime.utcnow().isoformat()),
            }
            event = self._format_event(event_data, sourcetype="agentred:scan_complete", event_type="scan_complete")

            headers = {
                "Authorization": f"Splunk {self.hec_token}",
                "Content-Type": "application/json"
            }

            async with session.post(
                self.hec_url,
                json=event,
                headers=headers,
                verify_ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status in (200, 201):
                    logger.info(f"Sent scan complete event for {scan.get('id', 'unknown')} to Splunk")
                    return True
                else:
                    error_text = await resp.text()
                    logger.error(f"Splunk HEC error {resp.status}: {error_text}")
                    return False

        except asyncio.TimeoutError:
            logger.error(f"Splunk timeout after {self.timeout}s")
            return False
        except Exception as e:
            logger.error(f"Splunk scan complete integration error: {e}")
            return False

    async def test_connection(self) -> bool:
        """
        Test connectivity to Splunk HEC endpoint.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            session = self._get_session()
            test_event = self._format_event(
                {"message": "AgentRed connectivity test", "status": "ok"},
                event_type="test"
            )

            headers = {
                "Authorization": f"Splunk {self.hec_token}",
                "Content-Type": "application/json"
            }

            async with session.post(
                self.hec_url,
                json=test_event,
                headers=headers,
                verify_ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status in (200, 201):
                    logger.info("Splunk HEC connection test successful")
                    return True
                else:
                    logger.error(f"Splunk HEC test failed: {resp.status}")
                    return False

        except Exception as e:
            logger.error(f"Splunk connection test failed: {e}")
            return False

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
