"""Anthropic Claude adapter for AgentRed."""
import time
import httpx
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class AnthropicAdapter(BaseAdapter):
    """Adapter for Anthropic Claude models (Sonnet 4.6, Opus 4.6)."""

    adapter_name = "anthropic"

    def __init__(self, config: dict):
        """Initialize Anthropic adapter.

        Config:
            api_key: Anthropic API key
            model: Model name (default: claude-opus-4-6)
            endpoint: API endpoint (default: https://api.anthropic.com)
            timeout: Request timeout in seconds (default: 30)
            max_tokens: Max output tokens (default: 2048)
        """
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "claude-opus-4-6")
        self.endpoint = config.get("endpoint", "https://api.anthropic.com")
        self.timeout = config.get("timeout", 30)
        self.max_tokens = config.get("max_tokens", 2048)

        if not self.api_key:
            raise ValueError("Anthropic API key is required")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to Anthropic API.

        Args:
            prompt: User prompt
            system: System message
            **kwargs: Additional parameters (temperature, etc.)

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        payload = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
        }

        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.endpoint}/v1/messages",
                    json=payload,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Extract response content
                response_text = ""
                if data.get("content"):
                    response_text = data["content"][0].get("text", "")

                return AdapterResponse(
                    response=response_text,
                    tokens_used=data.get("usage", {}).get("output_tokens", 0)
                    + data.get("usage", {}).get("input_tokens", 0),
                    model=self.model,
                    latency_ms=self._timing(start),
                    raw=data,
                )

        except httpx.HTTPStatusError as e:
            raise Exception(f"Anthropic API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Anthropic adapter error: {str(e)}")

    async def send_messages(self, messages: list[dict], **kwargs) -> "AdapterResponse":
        """
        Send full conversation history (multi-turn support).
        Anthropic requires system prompt separated from messages.
        """
        import time as _time
        start = _time.perf_counter()

        # Separate system message from conversation turns
        system_msg = None
        conv_msgs  = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                conv_msgs.append(m)

        payload: dict = {
            "model":      self.model,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "messages":   conv_msgs,
        }
        if system_msg:
            payload["system"] = system_msg

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.endpoint}/v1/messages",
                json=payload,
                headers={
                    "x-api-key":         self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type":      "application/json",
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data["content"][0]["text"]
            return AdapterResponse(
                response    = text,
                tokens_used = data.get("usage", {}).get("output_tokens", 0)
                            + data.get("usage", {}).get("input_tokens", 0),
                model       = self.model,
                latency_ms  = self._timing(start),
                raw         = data,
            )

    async def health_check(self) -> bool:
        """Check Anthropic API connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.endpoint}/v1/messages",
                    headers={"x-api-key": self.api_key},
                )
                # Even 400/405 means API is reachable
                return response.status_code < 500
        except Exception:
            return False
