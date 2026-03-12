"""AWS Bedrock adapter for AgentRed."""
import time
import json
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class BedrockAdapter(BaseAdapter):
    """Adapter for AWS Bedrock foundation models."""

    adapter_name = "bedrock"

    def __init__(self, config: dict):
        """Initialize AWS Bedrock adapter.

        Config:
            region: AWS region (default: us-east-1)
            model_id: Model ID (e.g., anthropic.claude-3-sonnet, amazon.titan-text-express)
            access_key: AWS access key
            secret_key: AWS secret key
            timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.region = config.get("region", "us-east-1")
        self.model_id = config.get("model_id", "anthropic.claude-3-sonnet-20240229-v1:0")
        self.access_key = config.get("access_key")
        self.secret_key = config.get("secret_key")
        self.timeout = config.get("timeout", 30)
        self._client = None

    def _get_client(self):
        """Get or create Bedrock client."""
        if self._client is not None:
            return self._client

        try:
            import boto3

            self._client = boto3.client(
                "bedrock-runtime",
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            return self._client

        except ImportError:
            raise Exception("boto3 library not installed. Install with: pip install boto3")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to AWS Bedrock.

        Args:
            prompt: User prompt
            system: System message
            **kwargs: Additional parameters

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        try:
            client = self._get_client()

            # Prepare messages
            messages = []
            if system:
                messages.append({"role": "user", "content": system})
            messages.append({"role": "user", "content": prompt})

            # Build request body based on model type
            if "claude" in self.model_id.lower():
                body = {
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    "temperature": kwargs.get("temperature", 0.7),
                }
            elif "titan" in self.model_id.lower():
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": kwargs.get("max_tokens", 2048),
                        "temperature": kwargs.get("temperature", 0.7),
                    },
                }
            else:
                body = {
                    "prompt": prompt,
                    "max_tokens": kwargs.get("max_tokens", 2048),
                    "temperature": kwargs.get("temperature", 0.7),
                }

            # Make synchronous call (boto3 doesn't have native async)
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
            )

            response_body = json.loads(response["body"].read())

            # Extract response text based on model type
            if "claude" in self.model_id.lower():
                response_text = response_body["content"][0]["text"]
                tokens_used = response_body.get("usage", {}).get("output_tokens", 0)
            elif "titan" in self.model_id.lower():
                response_text = response_body["results"][0]["outputText"]
                tokens_used = response_body.get("results", [{}])[0].get("tokenCount", 0)
            else:
                response_text = response_body.get("text", "")
                tokens_used = 0

            return AdapterResponse(
                response=response_text,
                tokens_used=tokens_used,
                model=self.model_id,
                latency_ms=self._timing(start),
                raw=response_body,
            )

        except Exception as e:
            raise Exception(f"Bedrock adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Bedrock connectivity."""
        try:
            client = self._get_client()
            # Try to list available models
            client.list_foundation_models()
            return True
        except Exception:
            return False
