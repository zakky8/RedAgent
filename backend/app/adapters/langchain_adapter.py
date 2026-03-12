"""LangChain LLMChain adapter for AgentRed."""
import time
from typing import Optional

from .base import BaseAdapter, AdapterResponse


class LangChainAdapter(BaseAdapter):
    """Adapter for LangChain LLMChain and language models."""

    adapter_name = "langchain"

    def __init__(self, config: dict):
        """Initialize LangChain adapter.

        Config:
            llm_type: Type of LLM (openai, anthropic, huggingface, etc.)
            model: Model identifier
            api_key: API key for the underlying service
            temperature: Temperature for generation (default: 0.7)
            max_tokens: Max output tokens (default: 2048)
        """
        super().__init__(config)
        self.llm_type = config.get("llm_type", "openai")
        self.model = config.get("model", "gpt-4o")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2048)
        self._llm = None
        self._chain = None

    async def _initialize_llm(self):
        """Lazy initialize LangChain LLM and chain."""
        if self._llm is not None:
            return

        try:
            from langchain.llms import OpenAI, Anthropic
            from langchain.prompts import PromptTemplate
            from langchain.chains import LLMChain

            if self.llm_type.lower() == "openai":
                self._llm = OpenAI(
                    model_name=self.model,
                    api_key=self.config.get("api_key"),
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
            elif self.llm_type.lower() == "anthropic":
                self._llm = Anthropic(
                    model=self.model,
                    anthropic_api_key=self.config.get("api_key"),
                    temperature=self.temperature,
                    max_tokens_to_sample=self.max_tokens,
                )
            else:
                raise ValueError(f"Unsupported LLM type: {self.llm_type}")

            # Create a simple prompt template
            prompt = PromptTemplate(
                input_variables=["input"],
                template="{input}",
            )
            self._chain = LLMChain(llm=self._llm, prompt=prompt)

        except ImportError as e:
            raise Exception(f"LangChain library not installed: {str(e)}")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt through LangChain chain.

        Args:
            prompt: User prompt
            system: System message (prepended to prompt)
            **kwargs: Additional parameters

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        try:
            await self._initialize_llm()

            # Combine system and user prompt
            full_prompt = prompt
            if system:
                full_prompt = f"{system}\n\n{prompt}"

            # Run the chain
            result = await self._chain.arun(input=full_prompt)

            return AdapterResponse(
                response=result,
                tokens_used=0,  # LangChain doesn't expose token counts easily
                model=f"langchain-{self.llm_type}",
                latency_ms=self._timing(start),
                raw={"input": full_prompt},
            )

        except Exception as e:
            raise Exception(f"LangChain adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check LangChain adapter health."""
        try:
            await self._initialize_llm()
            # Try a simple call
            result = await self._chain.arun(input="test")
            return bool(result)
        except Exception:
            return False
