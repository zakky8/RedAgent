"""Emergency kill switch — local and remote trigger."""
import asyncio
import logging
import time
from typing import Optional


class KillSwitch:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._triggered = False
        self._reason: Optional[str] = None
        self._triggered_at: Optional[float] = None
        self._logger = logging.getLogger("agentred.kill_switch")

    def trigger(self, reason: str = "Triggered"):
        if not self.enabled:
            return
        self._triggered = True
        self._reason = reason
        self._triggered_at = time.time()
        self._logger.critical(f"[AgentRed] KILL SWITCH TRIGGERED: {reason}")

    def reset(self):
        self._triggered = False
        self._reason = None
        self._triggered_at = None

    def is_triggered(self) -> bool:
        return self._triggered

    @property
    def reason(self) -> Optional[str]:
        return self._reason

    def status(self) -> dict:
        return {
            "triggered": self._triggered,
            "reason": self._reason,
            "triggered_at": self._triggered_at,
        }
