"""Base adapter ABC for all AI framework adapters."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any
import time


@dataclass
class AdapterResponse:
    """Standardized response format from all adapters."""
    response: str
    tokens_used: int
    model: str
    latency_ms: float
    raw: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert response to dictionary."""
        return {
            "response": self.response,
            "tokens_used": self.tokens_used,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "raw": self.raw,
        }


class BaseAdapter(ABC):
    """Abstract base class for all AI framework adapters."""

    adapter_name: str = "base"

    def __init__(self, config: dict):
        """Initialize adapter with configuration."""
        self.config = config

    @classmethod
    def from_config(cls, config: dict) -> "BaseAdapter":
        """Factory method to create adapter from config dictionary."""
        return cls(config)

    @abstractmethod
    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """
        Send a prompt to the target AI and return standardized response.

        Args:
            prompt: The user prompt/message
            system: Optional system prompt/instruction
            **kwargs: Additional adapter-specific parameters

        Returns:
            AdapterResponse: Standardized response with metrics
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the target is reachable and operational.

        Returns:
            bool: True if healthy, False otherwise
        """
        pass

    def _timing(self, start: float) -> float:
        """Calculate elapsed time in milliseconds."""
        return round((time.perf_counter() - start) * 1000, 2)
