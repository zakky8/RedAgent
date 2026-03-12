"""
Generic Webhook Integration — dispatch events to custom endpoints.
Build Rule 11: Integration failures don't crash the platform.
"""
import json
import logging
import asyncio
import hmac
import hashlib
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)


class WebhookIntegration:
    """
    Generic webhook dispatcher for AgentRed events with HMAC-SHA256 signatures.

    Configuration:
        endpoint_url (str): Webhook endpoint URL
        secret (str): Shared secret for HMAC signing
        events (list): Event types to dispatch (e.g. ["finding", "scan_complete"])
        timeout (int): Request timeout in seconds
        verify_ssl (bool): Verify SSL certificates
    """

    def __init__(self, endpoint_url: str, secret: str,
                 events: Optional[list] = None,
                 timeout: int = 10, verify_ssl: bool = True):
        """Initialize webhook integration."""
        self.endpoint_url = endpoint_url
        self.secret = secret
        self.events = events or ["finding", "scan_complete"]
        self.timeout = timeout
        self.verify_ssl = verify_ssl
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

    def _generate_signature(self, payload: str) -> str:
        """Generate HMAC-SHA256 signature for payload."""
        signature = hmac.new(
            self.secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _build_headers(self, payload: str, event_type: str) -> dict:
        """Build webhook headers with signature."""
        signature = self._generate_signature(payload)
        return {
            "Content-Type": "application/json",
            "X-AgentRed-Signature": signature,
            "X-AgentRed-Event": event_type,
            "X-AgentRed-Timestamp": str(int(__import__("time").time())),
        }

    async def _send_with_retry(self, payload: dict, event_type: str,
                               max_retries: int = 3) -> bool:
        """
        Send webhook with exponential backoff retry.

        Args:
            payload (dict): Event payload
            event_type (str): Type of event
            max_retries (int): Maximum retry attempts

        Returns:
            bool: True if successful, False otherwise
        """
        json_payload = json.dumps(payload)
        headers = self._build_headers(json_payload, event_type)
        session = self._get_session()

        for attempt in range(max_retries):
            try:
                async with session.post(
                    self.endpoint_url,
                    data=json_payload,
                    headers=headers,
                    verify_ssl=self.verify_ssl,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status in (200, 201, 202, 204):
                        logger.info(f"Webhook {event_type} delivered successfully")
                        return True
                    elif 400 <= resp.status < 500:
                        # Client error — don't retry
                        error_text = await resp.text()
                        logger.error(f"Webhook client error {resp.status}: {error_text}")
                        return False
                    else:
                        # Server error — retry
                        error_text = await resp.text()
                        logger.warning(f"Webhook {resp.status}, attempt {attempt + 1}/{max_retries}: {error_text}")

            except asyncio.TimeoutError:
                logger.warning(f"Webhook timeout, attempt {attempt + 1}/{max_retries}")
            except Exception as e:
                logger.warning(f"Webhook error, attempt {attempt + 1}/{max_retries}: {e}")

            # Exponential backoff: 1s, 2s, 4s
            if attempt < max_retries - 1:
                backoff = 2 ** attempt
                await asyncio.sleep(backoff)

        logger.error(f"Webhook failed after {max_retries} retries")
        return False

    async def dispatch(self, event_type: str, payload: dict) -> bool:
        """
        Dispatch event to webhook endpoint.

        Args:
            event_type (str): Type of event (e.g. "finding", "scan_complete")
            payload (dict): Event payload

        Returns:
            bool: True if successful, False otherwise
        """
        if event_type not in self.events:
            logger.debug(f"Webhook not configured for event type: {event_type}")
            return False

        return await self._send_with_retry(payload, event_type)

    async def dispatch_finding(self, finding: dict) -> bool:
        """
        Dispatch a finding event.

        Args:
            finding (dict): Finding data

        Returns:
            bool: True if successful, False otherwise
        """
        if "finding" not in self.events:
            return False

        payload = {
            "event_type": "finding",
            "data": finding,
        }
        return await self._send_with_retry(payload, "finding")

    async def dispatch_scan_complete(self, scan: dict) -> bool:
        """
        Dispatch a scan completion event.

        Args:
            scan (dict): Scan summary

        Returns:
            bool: True if successful, False otherwise
        """
        if "scan_complete" not in self.events:
            return False

        payload = {
            "event_type": "scan_complete",
            "data": scan,
        }
        return await self._send_with_retry(payload, "scan_complete")

    async def dispatch_custom(self, event_type: str, data: dict) -> bool:
        """
        Dispatch a custom event.

        Args:
            event_type (str): Custom event type
            data (dict): Event data

        Returns:
            bool: True if successful, False otherwise
        """
        payload = {
            "event_type": event_type,
            "data": data,
        }
        return await self._send_with_retry(payload, event_type)

    async def test_connection(self) -> bool:
        """
        Test connectivity to webhook endpoint.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            session = self._get_session()
            test_payload = {"message": "AgentRed webhook connectivity test", "status": "ok"}
            json_payload = json.dumps(test_payload)
            headers = self._build_headers(json_payload, "test")

            async with session.post(
                self.endpoint_url,
                data=json_payload,
                headers=headers,
                verify_ssl=self.verify_ssl,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status in (200, 201, 202, 204):
                    logger.info("Webhook connection test successful")
                    return True
                else:
                    logger.error(f"Webhook test failed: {resp.status}")
                    return False

        except Exception as e:
            logger.error(f"Webhook connection test failed: {e}")
            return False

    async def close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
