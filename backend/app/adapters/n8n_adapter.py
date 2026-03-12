"""n8n workflow webhook adapter for AgentRed."""
import time
import asyncio
import httpx
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class N8nAdapter(BaseAdapter):
    """Adapter for n8n workflow automation via webhook."""

    adapter_name = "n8n"

    def __init__(self, config: dict):
        """Initialize n8n webhook adapter.

        Config:
            webhook_url: n8n webhook URL (required)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Number of retry attempts (default: 3)
        """
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)

        if not self.webhook_url:
            raise ValueError("n8n webhook URL is required")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to n8n workflow.

        Args:
            prompt: User prompt/input
            system: System context
            **kwargs: Additional parameters to pass to workflow

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        # Build payload
        payload = {
            "prompt": prompt,
            "input": prompt,
        }

        if system:
            payload["system"] = system

        # Add any additional parameters
        for key, value in kwargs.items():
            payload[key] = value

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = None
                last_error = None

                # Implement retry logic
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
                            # Wait before retry (exponential backoff)
                            await asyncio.sleep(2 ** attempt)

                if response is None:
                    raise last_error or Exception("Failed to get response from n8n")

                data = response.json()

                # Extract response from workflow output
                output = data.get("output", data.get("result", ""))
                if isinstance(output, dict):
                    output = output.get("response", output.get("message", str(output)))

                return AdapterResponse(
                    response=str(output),
                    tokens_used=0,
                    model="n8n-workflow",
                    latency_ms=self._timing(start),
                    raw=data,
                )

        except Exception as e:
            raise Exception(f"n8n adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check n8n webhook connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Send a test payload
                response = await client.post(
                    self.webhook_url,
                    json={"test": True},
                    headers={"Content-Type": "application/json"},
                )
                # n8n returns 200 OK for both test and real payloads
                return response.status_code < 500
        except Exception:
            return False
