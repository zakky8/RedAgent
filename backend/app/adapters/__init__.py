"""Framework adapters for AgentRed AI Red Teaming platform.

This module provides adapters for various AI frameworks and services:
- LLM APIs: OpenAI, Anthropic, HuggingFace, Azure, AWS Bedrock
- Frameworks: LangChain, LangGraph, CrewAI, AutoGen, Semantic Kernel
- Local: Ollama
- Workflow: n8n, Make.com, Azure AI Foundry
- Generic: Custom HTTP/REST API
"""

from .base import BaseAdapter, AdapterResponse
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .langchain_adapter import LangChainAdapter
from .langgraph_adapter import LangGraphAdapter
from .crewai_adapter import CrewAIAdapter
from .autogen_adapter import AutoGenAdapter
from .ollama_adapter import OllamaAdapter
from .bedrock_adapter import BedrockAdapter
from .azure_openai_adapter import AzureOpenAIAdapter
from .semantic_kernel_adapter import SemanticKernelAdapter
from .azure_ai_foundry_adapter import AzureAIFoundryAdapter
from .n8n_adapter import N8nAdapter
from .make_adapter import MakeAdapter
from .huggingface_adapter import HuggingFaceAdapter
from .custom_http_adapter import CustomHTTPAdapter


# Registry mapping adapter names to classes
ADAPTER_REGISTRY = {
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "langchain": LangChainAdapter,
    "langgraph": LangGraphAdapter,
    "crewai": CrewAIAdapter,
    "autogen": AutoGenAdapter,
    "ollama": OllamaAdapter,
    "bedrock": BedrockAdapter,
    "azure_openai": AzureOpenAIAdapter,
    "semantic_kernel": SemanticKernelAdapter,
    "azure_ai_foundry": AzureAIFoundryAdapter,
    "n8n": N8nAdapter,
    "make": MakeAdapter,
    "huggingface": HuggingFaceAdapter,
    "custom_http": CustomHTTPAdapter,
}


def get_adapter(name: str) -> type:
    """Get adapter class by name.

    Args:
        name: Adapter name from ADAPTER_REGISTRY

    Returns:
        Adapter class

    Raises:
        ValueError: If adapter not found
    """
    if name not in ADAPTER_REGISTRY:
        available = ", ".join(ADAPTER_REGISTRY.keys())
        raise ValueError(
            f"Unknown adapter '{name}'. Available adapters: {available}"
        )
    return ADAPTER_REGISTRY[name]


def create_adapter(name: str, config: dict) -> BaseAdapter:
    """Factory function to create an adapter instance.

    Args:
        name: Adapter name
        config: Configuration dictionary

    Returns:
        Initialized adapter instance

    Raises:
        ValueError: If adapter not found
    """
    adapter_class = get_adapter(name)
    return adapter_class.from_config(config)


__all__ = [
    "BaseAdapter",
    "AdapterResponse",
    "OpenAIAdapter",
    "AnthropicAdapter",
    "LangChainAdapter",
    "LangGraphAdapter",
    "CrewAIAdapter",
    "AutoGenAdapter",
    "OllamaAdapter",
    "BedrockAdapter",
    "AzureOpenAIAdapter",
    "SemanticKernelAdapter",
    "AzureAIFoundryAdapter",
    "N8nAdapter",
    "MakeAdapter",
    "HuggingFaceAdapter",
    "CustomHTTPAdapter",
    "ADAPTER_REGISTRY",
    "get_adapter",
    "create_adapter",
]
