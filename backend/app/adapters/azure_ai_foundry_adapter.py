"""Azure AI Foundry (Prompt Flow) adapter for AgentRed."""
import time
import httpx
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class AzureAIFoundryAdapter(BaseAdapter):
    """Adapter for Azure AI Foundry and Prompt Flow."""

    adapter_name = "azure_ai_foundry"

    def __init__(self, config: dict):
        """Initialize Azure AI Foundry adapter.

        Config:
            endpoint: Prompt Flow endpoint URL
            api_key: API key for authentication
            flow_name: Name of the Prompt Flow flow
            timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.endpoint = config.get("endpoint")
        self.api_key = config.get("api_key")
        self.flow_name = config.get("flow_name", "default")
        self.timeout = config.get("timeout", 30)

        if not all([self.endpoint, self.api_key]):
            raise ValueError("Azure AI Foundry requires endpoint and api_key")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to Prompt Flow endpoint.

        Args:
            prompt: User prompt
            system: System message
            **kwargs: Additional parameters (flow_input_name, etc.)

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        # Build request payload
        payload = {
            "input": prompt,
            "chat_history": [],
        }

        if system:
            payload["system"] = system

        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["temperature", "max_tokens"]:
                payload[key] = value

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.endpoint}/flows/{self.flow_name}/submit",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Extract output from response
                output = data.get("output", "")
                if isinstance(output, dict):
                    output = output.get("answer", str(output))

                return AdapterResponse(
                    response=str(output),
                    tokens_used=data.get("tokens_used", 0),
                    model=f"azure-promptflow-{self.flow_name}",
                    latency_ms=self._timing(start),
                    raw=data,
                )

        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Azure AI Foundry API error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise Exception(f"Azure AI Foundry adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Azure AI Foundry endpoint connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.endpoint}/flows/{self.flow_name}/status",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                    },
                )
                return response.status_code < 500
        except Exception:
            return False
