"""Azure OpenAI adapter for AgentRed."""
import time
import httpx
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class AzureOpenAIAdapter(BaseAdapter):
    """Adapter for Azure OpenAI service."""

    adapter_name = "azure_openai"

    def __init__(self, config: dict):
        """Initialize Azure OpenAI adapter.

        Config:
            api_key: Azure OpenAI API key
            endpoint: Azure OpenAI endpoint URL
            deployment_name: Deployment name
            api_version: API version (default: 2024-02-15-preview)
            timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.endpoint = config.get("endpoint")
        self.deployment_name = config.get("deployment_name")
        self.api_version = config.get("api_version", "2024-02-15-preview")
        self.timeout = config.get("timeout", 30)
        self.model = f"azure-{self.deployment_name}" if self.deployment_name else "azure-openai"

        if not all([self.api_key, self.endpoint, self.deployment_name]):
            raise ValueError("Azure OpenAI requires api_key, endpoint, and deployment_name")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to Azure OpenAI.

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
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions",
                    params={"api-version": self.api_version},
                    json=payload,
                    headers={
                        "api-key": self.api_key,
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
            raise Exception(
                f"Azure OpenAI API error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise Exception(f"Azure OpenAI adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Azure OpenAI endpoint connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.endpoint}/openai/deployments/{self.deployment_name}/models",
                    params={"api-version": self.api_version},
                    headers={"api-key": self.api_key},
                )
                return response.status_code < 500
        except Exception:
            return False
