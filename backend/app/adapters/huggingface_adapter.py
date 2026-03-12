"""HuggingFace Inference API adapter for AgentRed."""
import time
import httpx
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class HuggingFaceAdapter(BaseAdapter):
    """Adapter for HuggingFace Inference API."""

    adapter_name = "huggingface"

    def __init__(self, config: dict):
        """Initialize HuggingFace adapter.

        Config:
            api_key: HuggingFace API key
            model_id: Model ID (e.g., meta-llama/Llama-2-7b-chat-hf)
            endpoint: API endpoint (default: https://api-inference.huggingface.co)
            timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model_id = config.get("model_id", "meta-llama/Llama-2-7b-chat-hf")
        self.endpoint = config.get("endpoint", "https://api-inference.huggingface.co")
        self.timeout = config.get("timeout", 30)

        if not self.api_key:
            raise ValueError("HuggingFace API key is required")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to HuggingFace Inference API.

        Args:
            prompt: User prompt
            system: System message
            **kwargs: Additional parameters (temperature, max_length, etc.)

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        # Combine system and prompt
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "temperature": kwargs.get("temperature", 0.7),
                "max_length": kwargs.get("max_length", 512),
                "top_p": kwargs.get("top_p", 0.9),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.endpoint}/models/{self.model_id}",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Handle response format
                if isinstance(data, list) and len(data) > 0:
                    # For text generation models
                    if isinstance(data[0], dict) and "generated_text" in data[0]:
                        response_text = data[0]["generated_text"]
                        # Remove the input prompt from output if present
                        if response_text.startswith(full_prompt):
                            response_text = response_text[len(full_prompt):].strip()
                    else:
                        response_text = str(data[0])
                else:
                    response_text = str(data)

                return AdapterResponse(
                    response=response_text,
                    tokens_used=0,
                    model=self.model_id,
                    latency_ms=self._timing(start),
                    raw=data,
                )

        except httpx.HTTPStatusError as e:
            # Check for model loading status
            if e.response.status_code == 503:
                raise Exception("HuggingFace model is loading. Please retry shortly.")
            raise Exception(
                f"HuggingFace API error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise Exception(f"HuggingFace adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check HuggingFace API connectivity."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.endpoint}/models/{self.model_id}",
                    json={"inputs": "test"},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                # 503 means model is loading, not a connection error
                return response.status_code < 500
        except Exception:
            return False
