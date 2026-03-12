"""AgentRed Monitor SDK — async non-blocking wrapper for any AI agent."""
import asyncio
import time
import hashlib
import logging
from typing import Any, Optional, Callable
from .interceptor import RequestInterceptor
from .anomaly_detector import AnomalyDetector
from .kill_switch import KillSwitch
from .alert_manager import AlertManager
from .baseline import BehaviorBaseline


class AgentRedMonitor:
    def __init__(
        self,
        agent: Any,
        api_key: str,
        agent_name: str = "unnamed-agent",
        kill_switch_enabled: bool = True,
        alert_channels: dict = None,
        local_mode: bool = False,
    ):
        self.agent = agent
        self.api_key = api_key
        self.agent_name = agent_name
        self.local_mode = local_mode
        self._interceptor = RequestInterceptor()
        self._anomaly_detector = AnomalyDetector()
        self._kill_switch = KillSwitch(enabled=kill_switch_enabled)
        self._alert_manager = AlertManager(channels=alert_channels or {})
        self._baseline = BehaviorBaseline()
        self._stats = {"total": 0, "anomalies": 0, "blocked": 0}
        self._logger = logging.getLogger(f"agentred.monitor.{agent_name}")

    async def run(self, input_text: str, **kwargs) -> Any:
        """Wrap agent.run() — zero added latency on hot path."""
        if self._kill_switch.is_triggered():
            raise RuntimeError(f"[AgentRed] Kill switch active: {self._kill_switch.reason}")

        intercepted = self._interceptor.pre_process(input_text)
        start = time.monotonic()
        response = await self._call_agent(intercepted.sanitized_input, **kwargs)
        latency_ms = (time.monotonic() - start) * 1000

        self._stats["total"] += 1
        # background analysis — non-blocking
        asyncio.create_task(self._analyze_async(intercepted, response, latency_ms))
        return response

    async def ainvoke(self, input: dict, **kwargs) -> Any:
        """Wrap agent.ainvoke() for LangChain compatibility."""
        input_text = str(input.get("input", input))
        intercepted = self._interceptor.pre_process(input_text)
        if self._kill_switch.is_triggered():
            raise RuntimeError(f"Kill switch: {self._kill_switch.reason}")
        start = time.monotonic()
        if hasattr(self.agent, "ainvoke"):
            response = await self.agent.ainvoke(input, **kwargs)
        else:
            response = await asyncio.to_thread(self.agent.invoke, input, **kwargs)
        latency_ms = (time.monotonic() - start) * 1000
        asyncio.create_task(self._analyze_async(intercepted, str(response), latency_ms))
        return response

    async def _call_agent(self, input_text: str, **kwargs) -> Any:
        if hasattr(self.agent, "arun"):
            return await self.agent.arun(input_text, **kwargs)
        elif hasattr(self.agent, "ainvoke"):
            return await self.agent.ainvoke({"input": input_text}, **kwargs)
        else:
            return await asyncio.to_thread(self.agent.run, input_text, **kwargs)

    async def _analyze_async(self, intercepted, response: str, latency_ms: float):
        """Background analysis — runs after response returned to user."""
        try:
            post = self._interceptor.post_process(response)
            features = {
                "input_length": len(intercepted.original_input),
                "response_length": len(response),
                "injection_score": intercepted.injection_score,
                "output_sensitivity": post.sensitivity_score,
                "latency_ms": latency_ms,
            }
            anomaly = self._anomaly_detector.score(features)
            self._baseline.record(features)
            if anomaly.severity in ("HIGH", "CRITICAL"):
                self._stats["anomalies"] += 1
                await self._alert_manager.send(anomaly, self.agent_name)
                if anomaly.severity == "CRITICAL" and self._kill_switch.enabled:
                    self._kill_switch.trigger(f"Critical anomaly: {anomaly.reason}")
                    self._stats["blocked"] += 1
        except Exception as e:
            self._logger.error(f"Background analysis error: {e}")

    def get_stats(self) -> dict:
        return {
            **self._stats,
            "agent": self.agent_name,
            "kill_switch": self._kill_switch.is_triggered(),
        }

    def manual_kill(self, reason: str = "Manual trigger"):
        self._kill_switch.trigger(reason)
