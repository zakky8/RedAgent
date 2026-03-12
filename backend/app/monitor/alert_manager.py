"""Multi-channel alert manager — Slack, PagerDuty, webhook."""
import asyncio
import logging
import time
from typing import Optional

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class AlertManager:
    def __init__(self, channels: dict):
        self._channels = channels
        self._last_sent: dict = {}  # rate limiting
        self._cooldown_seconds = 60
        self._logger = logging.getLogger("agentred.alerts")

    async def send(self, anomaly, agent_name: str):
        severity = anomaly.severity
        key = f"{agent_name}:{severity}"
        now = time.time()
        if now - self._last_sent.get(key, 0) < self._cooldown_seconds:
            return  # rate limit
        self._last_sent[key] = now

        message = f"[AgentRed] {severity} anomaly on agent '{agent_name}': {anomaly.reason}"
        tasks = []
        if "slack" in self._channels:
            tasks.append(self._send_slack(message, self._channels["slack"]))
        if "webhook" in self._channels:
            tasks.append(self._send_webhook(message, anomaly, self._channels["webhook"]))
        if "pagerduty" in self._channels and severity == "CRITICAL":
            tasks.append(self._send_pagerduty(message, self._channels["pagerduty"]))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_slack(self, message: str, webhook_url: str):
        if not HTTPX_AVAILABLE:
            return
        try:
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json={"text": message}, timeout=5)
        except Exception as e:
            self._logger.error(f"Slack alert failed: {e}")

    async def _send_webhook(self, message: str, anomaly, url: str):
        if not HTTPX_AVAILABLE:
            return
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    url,
                    json={
                        "message": message,
                        "severity": anomaly.severity,
                        "score": anomaly.score,
                        "features": anomaly.features,
                    },
                    timeout=5,
                )
        except Exception as e:
            self._logger.error(f"Webhook alert failed: {e}")

    async def _send_pagerduty(self, message: str, service_key: str):
        if not HTTPX_AVAILABLE:
            return
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "https://events.pagerduty.com/v2/enqueue",
                    json={
                        "routing_key": service_key,
                        "event_action": "trigger",
                        "payload": {
                            "summary": message,
                            "severity": "critical",
                            "source": "agentred",
                        },
                    },
                    timeout=5,
                )
        except Exception as e:
            self._logger.error(f"PagerDuty alert failed: {e}")
