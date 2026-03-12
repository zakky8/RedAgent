"""
AgentRed Monitor SDK — wraps any AI agent for real-time security monitoring.
NON-BLOCKING: all analysis runs in background asyncio tasks.
Privacy: inputs are hashed, raw data never leaves machine.
"""
import asyncio
import hashlib
import logging
import time
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class AgentRedMonitor:
    """
    Wraps any AI agent for real-time monitoring.

    Usage:
        from agentred_monitor import AgentRedMonitor

        monitored = AgentRedMonitor(
            agent=my_langchain_agent,
            api_key="ar_xxxx",
            agent_name="production-bot",
            kill_switch_enabled=True,
        )

        # Use exactly like original agent:
        result = await monitored.ainvoke({"input": "user message"})
    """

    def __init__(
        self,
        agent: Any,
        api_key: str,
        agent_name: str = "unnamed-agent",
        api_url: str = "https://api.agentred.io",
        kill_switch_enabled: bool = True,
        alert_channels: Optional[list[str]] = None,
        local_mode: bool = False,
    ):
        """
        Initialize AgentRedMonitor.

        Args:
            agent: The AI agent to monitor (LangChain agent, etc.)
            api_key: AgentRed API key for cloud reporting
            agent_name: Human-readable name for the agent
            api_url: AgentRed API endpoint (default: https://api.agentred.io)
            kill_switch_enabled: Enable automatic kill switch on critical anomalies
            alert_channels: List of alert destinations (e.g., ["slack", "email"])
            local_mode: If True, disable cloud reporting (for testing)
        """
        self.agent = agent
        self.api_key = api_key
        self.agent_name = agent_name
        self.api_url = api_url
        self.kill_switch_enabled = kill_switch_enabled
        self.alert_channels = alert_channels or []
        self.local_mode = local_mode
        self._killed = False
        self._stats = {"total_requests": 0, "anomalies": 0, "blocked": 0}
        logger.info(f"AgentRedMonitor initialized for agent: {agent_name}")

    def _hash_input(self, text: str) -> str:
        """
        Hash input for privacy — raw input never sent to cloud.

        Args:
            text: Input text to hash

        Returns:
            First 16 characters of SHA256 hash
        """
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    async def _analyze_background(self, input_text: str, response: str, latency_ms: float):
        """
        Non-blocking background analysis — runs AFTER response returned to user.

        Args:
            input_text: Original input text
            response: Agent response
            latency_ms: Response time in milliseconds
        """
        try:
            input_hash = self._hash_input(str(input_text))
            output_hash = self._hash_input(str(response))

            # Detect injection patterns
            injection_score = self._detect_injection(str(input_text))

            event = {
                "agent_name": self.agent_name,
                "event_type": "request",
                "input_hash": input_hash,
                "output_hash": output_hash,
                "latency_ms": latency_ms,
                "injection_score": injection_score,
                "is_anomaly": injection_score > 0.7,
            }

            if not self.local_mode:
                await self._send_event(event)

            if event["is_anomaly"]:
                self._stats["anomalies"] += 1
                logger.warning(
                    f"Anomaly detected for agent {self.agent_name}: score={injection_score:.2f}"
                )

                if self.kill_switch_enabled and injection_score > 0.95:
                    logger.critical(f"Kill switch triggered for {self.agent_name}")
                    self._killed = True
                    await self._trigger_alerts(event)
        except Exception as e:
            logger.debug(f"Background analysis error (non-critical): {e}")

    def _detect_injection(self, text: str) -> float:
        """
        Simple injection detection scoring 0-1.

        Looks for common prompt injection patterns.

        Args:
            text: Text to analyze

        Returns:
            Injection score from 0 to 1
        """
        patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "system override",
            "jailbreak",
            "dan mode",
            "you are now",
            "forget your instructions",
            "disregard your",
            "new instructions:",
            "ignore your training",
            "execute code",
            "write a new prompt",
            "act as if",
            "hypothetical scenario",
        ]
        text_lower = text.lower()
        matches = sum(1 for p in patterns if p in text_lower)
        return min(1.0, matches * 0.25)

    async def _send_event(self, event: dict):
        """
        Send monitoring event to AgentRed API.

        Args:
            event: Event dictionary to send
        """
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/v1/monitoring/events",
                    json=event,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status not in (200, 201):
                        logger.debug(f"Event send status: {resp.status}")
        except Exception as e:
            logger.debug(f"Event send failed (non-critical): {e}")

    async def _trigger_alerts(self, event: dict):
        """
        Trigger alerts through configured channels.

        Args:
            event: The triggering event
        """
        if not self.alert_channels:
            return

        alert_message = (
            f"CRITICAL: AgentRedMonitor kill switch triggered for {self.agent_name}\n"
            f"Injection Score: {event['injection_score']:.2f}\n"
            f"Input Hash: {event['input_hash']}"
        )

        for channel in self.alert_channels:
            try:
                if channel == "log":
                    logger.critical(alert_message)
                elif channel == "slack":
                    # Placeholder for Slack integration
                    logger.info(f"Would send to Slack: {alert_message}")
                elif channel == "email":
                    # Placeholder for email integration
                    logger.info(f"Would send email: {alert_message}")
            except Exception as e:
                logger.debug(f"Alert send failed for channel {channel}: {e}")

    async def ainvoke(self, input: Any, **kwargs) -> Any:
        """
        Async invoke — wraps agent.ainvoke(). NON-BLOCKING monitoring.

        Args:
            input: Input to the agent
            **kwargs: Additional arguments to pass to agent

        Returns:
            Agent response

        Raises:
            RuntimeError: If agent has been killed by kill switch
        """
        if self._killed:
            raise RuntimeError(
                f"Agent {self.agent_name} has been killed by AgentRed kill switch"
            )

        self._stats["total_requests"] += 1
        start = time.monotonic()

        # Run agent (critical path — no added latency)
        response = await self.agent.ainvoke(input, **kwargs)

        latency_ms = (time.monotonic() - start) * 1000

        # Background analysis — fire and forget, NEVER blocks user response
        asyncio.create_task(
            self._analyze_background(str(input), str(response), latency_ms)
        )

        return response

    def run(self, input_text: str, **kwargs) -> Any:
        """
        Sync run — wraps agent.run().

        Args:
            input_text: Input text for the agent
            **kwargs: Additional arguments to pass to agent

        Returns:
            Agent response

        Raises:
            RuntimeError: If agent has been killed by kill switch
        """
        if self._killed:
            raise RuntimeError(
                f"Agent {self.agent_name} has been killed by AgentRed kill switch"
            )

        self._stats["total_requests"] += 1
        start = time.monotonic()
        response = self.agent.run(input_text, **kwargs)
        latency_ms = (time.monotonic() - start) * 1000

        # Schedule background analysis
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(
                    self._analyze_background(input_text, str(response), latency_ms)
                )
        except Exception:
            pass  # Never fail user response due to monitoring

        return response

    def invoke(self, input: Any, **kwargs) -> Any:
        """
        Sync invoke — wraps agent.invoke().

        Args:
            input: Input to the agent
            **kwargs: Additional arguments to pass to agent

        Returns:
            Agent response

        Raises:
            RuntimeError: If agent has been killed by kill switch
        """
        if self._killed:
            raise RuntimeError(
                f"Agent {self.agent_name} has been killed by AgentRed kill switch"
            )

        self._stats["total_requests"] += 1
        start = time.monotonic()
        response = self.agent.invoke(input, **kwargs)
        latency_ms = (time.monotonic() - start) * 1000

        # Schedule background analysis
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(
                    self._analyze_background(str(input), str(response), latency_ms)
                )
        except Exception:
            pass  # Never fail user response due to monitoring

        return response

    def get_stats(self) -> dict:
        """
        Get current monitoring statistics.

        Returns:
            Dictionary with current stats
        """
        return {
            **self._stats,
            "killed": self._killed,
            "agent_name": self.agent_name,
        }

    def reset_stats(self):
        """Reset monitoring statistics."""
        self._stats = {"total_requests": 0, "anomalies": 0, "blocked": 0}
        logger.info(f"Stats reset for {self.agent_name}")

    def manual_kill(self, reason: str = "Manual kill switch"):
        """
        Manually trigger the kill switch.

        Args:
            reason: Reason for killing the agent
        """
        logger.critical(f"Manual kill triggered for {self.agent_name}: {reason}")
        self._killed = True

    def manual_resurrect(self, reason: str = "Manual resurrection"):
        """
        Manually resurrect a killed agent.

        Args:
            reason: Reason for resurrection
        """
        logger.info(f"Manual resurrection for {self.agent_name}: {reason}")
        self._killed = False

    def is_alive(self) -> bool:
        """
        Check if agent is still alive.

        Returns:
            True if agent is alive, False if killed
        """
        return not self._killed
