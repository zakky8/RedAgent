"""PagerDuty integration for critical AgentRed alerts."""
import logging

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class PagerDutyIntegration:
    EVENTS_URL = "https://events.pagerduty.com/v2/enqueue"

    def __init__(self, routing_key: str):
        self.routing_key = routing_key
        self._logger = logging.getLogger("agentred.pagerduty")

    async def trigger(
        self, summary: str, severity: str = "critical", details: dict = None
    ):
        if not HTTPX_AVAILABLE:
            return
        payload = {
            "routing_key": self.routing_key,
            "event_action": "trigger",
            "payload": {
                "summary": summary,
                "severity": severity.lower(),
                "source": "agentred",
                "custom_details": details or {},
            },
        }
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(self.EVENTS_URL, json=payload, timeout=10)
                return {
                    "ok": r.status_code in (200, 202),
                    "dedup_key": r.json().get("dedup_key"),
                }
        except Exception as e:
            self._logger.error(f"PagerDuty trigger failed: {e}")
            return {"ok": False, "error": str(e)}

    async def resolve(self, dedup_key: str):
        payload = {
            "routing_key": self.routing_key,
            "event_action": "resolve",
            "dedup_key": dedup_key,
        }
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(self.EVENTS_URL, json=payload, timeout=10)
                return {"ok": r.status_code in (200, 202)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def test_connection(self) -> dict:
        result = await self.trigger(
            "AgentRed connectivity test — auto-resolve", "info"
        )
        return {"connected": result.get("ok", False)}
