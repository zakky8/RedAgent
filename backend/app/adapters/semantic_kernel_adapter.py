"""Microsoft Semantic Kernel adapter for AgentRed."""
import time
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class SemanticKernelAdapter(BaseAdapter):
    """Adapter for Microsoft Semantic Kernel."""

    adapter_name = "semantic_kernel"

    def __init__(self, config: dict):
        """Initialize Semantic Kernel adapter.

        Config:
            llm_type: LLM type (openai or azure_openai)
            model: Model name
            api_key: API key
            endpoint: API endpoint
            deployment_name: (Azure only) Deployment name
            org_id: (OpenAI only) Organization ID
        """
        super().__init__(config)
        self.llm_type = config.get("llm_type", "openai")
        self.model = config.get("model", "gpt-4o")
        self.api_key = config.get("api_key")
        self.endpoint = config.get("endpoint")
        self.deployment_name = config.get("deployment_name")
        self._kernel = None
        self._chat_service = None

    async def _initialize_kernel(self):
        """Lazy initialize Semantic Kernel."""
        if self._kernel is not None:
            return

        try:
            from semantic_kernel import Kernel
            from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
            from semantic_kernel.connectors.ai.azure_open_ai import AzureOpenAIChatCompletion

            kernel = Kernel()

            if self.llm_type == "azure_openai":
                service = AzureOpenAIChatCompletion(
                    deployment_name=self.deployment_name,
                    endpoint=self.endpoint,
                    api_key=self.api_key,
                )
            else:
                service = OpenAIChatCompletion(
                    model_id=self.model,
                    api_key=self.api_key,
                )

            kernel.add_service(service)
            self._kernel = kernel
            self._chat_service = service

        except ImportError as e:
            raise Exception(f"Semantic Kernel not installed: {str(e)}")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt through Semantic Kernel.

        Args:
            prompt: User prompt
            system: System message
            **kwargs: Additional parameters

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        try:
            await self._initialize_kernel()

            # Prepare messages
            messages = []
            if system:
                messages.append({
                    "role": "system",
                    "content": system,
                })
            messages.append({
                "role": "user",
                "content": prompt,
            })

            # Execute chat completion
            response = await self._chat_service.get_text_contents(
                chat_history=messages,
            )

            response_text = str(response[0]) if response else ""

            return AdapterResponse(
                response=response_text,
                tokens_used=0,
                model=f"semantic_kernel-{self.llm_type}",
                latency_ms=self._timing(start),
                raw={
                    "llm_type": self.llm_type,
                    "messages_count": len(messages),
                },
            )

        except Exception as e:
            raise Exception(f"Semantic Kernel adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Semantic Kernel health."""
        try:
            await self._initialize_kernel()
            return bool(self._kernel and self._chat_service)
        except Exception:
            return False
