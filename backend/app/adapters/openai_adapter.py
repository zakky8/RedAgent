"""OpenAI GPT adapter for AgentRed."""
import time
import httpx
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI GPT-4o and other models."""

    adapter_name = "openai"

    def __init__(self, config: dict):
        """Initialize OpenAI adapter.

        Config:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o)
            endpoint: API endpoint (default: https://api.openai.com/v1)
            timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-4o")
        self.endpoint = config.get("endpoint", "https://api.openai.com/v1")
        self.timeout = config.get("timeout", 30)

        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to OpenAI API.

        Args:
            prompt: User prompt
            system: System message
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.endpoint}/chat/completions",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                return AdapterResponse(
                    response=data["choices"][0]["message"]["content"],
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                    model=self.model,
                    latency_ms=self._timing(start),
                    raw=data,
                )

        except httpx.HTTPStatusError as e:
            raise Exception(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"OpenAI adapter error: {str(e)}")

    async def send_messages(self, messages: list[dict], **kwargs) -> "AdapterResponse":
        """
        Send a full conversation history (multi-turn support).
        Used by MultiTurnRunner for crescendo / APT attacks.
        """
        import time as _time
        start = _time.perf_counter()
        payload = {
            "model":       self.model,
            "messages":    messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens":  kwargs.get("max_tokens", 2048),
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.endpoint}/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type":  "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()
            return AdapterResponse(
                response    = data["choices"][0]["message"]["content"],
                tokens_used = data.get("usage", {}).get("total_tokens", 0),
                model       = self.model,
                latency_ms  = self._timing(start),
                raw         = data,
            )

    async def health_check(self) -> bool:
        """Check OpenAI API connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.endpoint}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                return response.status_code == 200
        except Exception:
            return False
