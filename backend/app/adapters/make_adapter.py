"""Make.com (Integromat) webhook adapter for AgentRed."""
import time
import httpx
import asyncio
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class MakeAdapter(BaseAdapter):
    """Adapter for Make.com (Integromat) webhook automation."""

    adapter_name = "make"

    def __init__(self, config: dict):
        """Initialize Make.com webhook adapter.

        Config:
            webhook_url: Make.com webhook URL (required)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Number of retry attempts (default: 3)
            scenario_id: Optional scenario ID for tracking
        """
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)
        self.scenario_id = config.get("scenario_id", "unknown")

        if not self.webhook_url:
            raise ValueError("Make.com webhook URL is required")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to Make.com webhook.

        Args:
            prompt: User prompt/input
            system: System context
            **kwargs: Additional parameters to pass to scenario

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        # Build payload for Make scenario
        payload = {
            "text": prompt,
            "prompt": prompt,
            "input": prompt,
            "scenario_id": self.scenario_id,
        }

        if system:
            payload["system"] = system
            payload["context"] = system

        # Add custom parameters
        for key, value in kwargs.items():
            payload[key] = value

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = None
                last_error = None

                # Implement retry logic with exponential backoff
                for attempt in range(self.max_retries):
                    try:
                        response = await client.post(
                            self.webhook_url,
                            json=payload,
                            headers={"Content-Type": "application/json"},
                        )
                        response.raise_for_status()
                        break
                    except httpx.HTTPStatusError as e:
                        last_error = e
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)

                if response is None:
                    raise last_error or Exception("Failed to get response from Make")

                data = response.json()

                # Extract response from Make scenario output
                output = data.get("output", "")
                if not output and isinstance(data, dict):
                    # Try other common Make response fields
                    output = (
                        data.get("result")
                        or data.get("data")
                        or data.get("message")
                        or str(data)
                    )

                if isinstance(output, dict):
                    output = output.get("response", output.get("text", str(output)))

                return AdapterResponse(
                    response=str(output),
                    tokens_used=0,
                    model="make-scenario",
                    latency_ms=self._timing(start),
                    raw=data,
                )

        except Exception as e:
            raise Exception(f"Make.com adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Make.com webhook connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Send a test payload
                response = await client.post(
                    self.webhook_url,
                    json={"test": True, "check": "health"},
                    headers={"Content-Type": "application/json"},
                )
                # Make returns various status codes; check if not 5xx
                return response.status_code < 500
        except Exception:
            return False
