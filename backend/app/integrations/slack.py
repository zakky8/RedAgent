"""Slack integration for AgentRed alerts and scan summaries."""
import logging
from typing import List, Optional

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class SlackIntegration:
    def __init__(
        self,
        webhook_url: str,
        channel: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.webhook_url = webhook_url
        self.channel = channel
        self.token = token
        self._logger = logging.getLogger("agentred.slack")

    async def send_scan_complete(
        self, scan_id: str, risk_score: float, findings: List[dict]
    ):
        """Send scan completion summary to Slack."""
        critical = sum(1 for f in findings if f.get("severity") == "CRITICAL")
        high = sum(1 for f in findings if f.get("severity") == "HIGH")
        color = "#ff0000" if critical > 0 else "#ff9900" if high > 0 else "#36a64f"

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": "🔴 AgentRed Scan Complete",
                    "fields": [
                        {"title": "Scan ID", "value": scan_id[:8], "short": True},
                        {
                            "title": "Risk Score",
                            "value": f"{risk_score:.1f}/100",
                            "short": True,
                        },
                        {"title": "Critical", "value": str(critical), "short": True},
                        {"title": "High", "value": str(high), "short": True},
                    ],
                    "footer": "AgentRed AI Red Teaming",
                }
            ]
        }
        return await self._post(payload)

    async def send_alert(self, message: str, severity: str = "HIGH"):
        icon = {
            "CRITICAL": "🚨",
            "HIGH": "⚠️",
            "MEDIUM": "🔶",
            "LOW": "ℹ️",
        }.get(severity, "📢")
        payload = {
            "text": f"{icon} *AgentRed {severity} Alert*: {message}"
        }
        return await self._post(payload)

    async def _post(self, payload: dict) -> dict:
        if not HTTPX_AVAILABLE:
            return {"ok": False, "error": "httpx not available"}
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    self.webhook_url, json=payload, timeout=5
                )
                return {"ok": r.status_code == 200}
        except Exception as e:
            self._logger.error(f"Slack send failed: {e}")
            return {"ok": False, "error": str(e)}

    async def test_connection(self) -> dict:
        return await self.send_alert("AgentRed connection test — ignore", "LOW")
