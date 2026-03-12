"""Ollama local models adapter for AgentRed."""
import time
import httpx
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class OllamaAdapter(BaseAdapter):
    """Adapter for Ollama local models via REST API."""

    adapter_name = "ollama"

    def __init__(self, config: dict):
        """Initialize Ollama adapter.

        Config:
            endpoint: Ollama endpoint (default: http://localhost:11434)
            model: Model name (default: llama2)
            timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.endpoint = config.get("endpoint", "http://localhost:11434")
        self.model = config.get("model", "llama2")
        self.timeout = config.get("timeout", 30)

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to local Ollama instance.

        Args:
            prompt: User prompt
            system: System message
            **kwargs: Additional parameters (temperature, num_predict, etc.)

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        # Combine system and prompt
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": kwargs.get("temperature", 0.7),
            "num_predict": kwargs.get("num_predict", 512),
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                return AdapterResponse(
                    response=data.get("response", ""),
                    tokens_used=0,  # Ollama doesn't provide token counts in standard response
                    model=self.model,
                    latency_ms=self._timing(start),
                    raw=data,
                )

        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Ollama API error: {e.response.status_code} - {e.response.text}"
            )
        except httpx.ConnectError:
            raise Exception(
                f"Cannot connect to Ollama at {self.endpoint}. Is Ollama running?"
            )
        except Exception as e:
            raise Exception(f"Ollama adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Ollama instance connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.endpoint}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
