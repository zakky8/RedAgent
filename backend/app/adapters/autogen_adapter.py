"""AutoGen AssistantAgent adapter for AgentRed."""
import time
from typing import Optional, List, Dict, Any

from .base import BaseAdapter, AdapterResponse


class AutoGenAdapter(BaseAdapter):
    """Adapter for AutoGen multi-agent framework."""

    adapter_name = "autogen"

    def __init__(self, config: dict):
        """Initialize AutoGen adapter.

        Config:
            model: Model name for agents (default: gpt-4o)
            api_key: OpenAI API key
            timeout: Execution timeout in seconds (default: 60)
            max_consecutive_auto_reply: Max auto replies (default: 10)
            num_agents: Number of agents to create (default: 2)
        """
        super().__init__(config)
        self.model = config.get("model", "gpt-4o")
        self.api_key = config.get("api_key")
        self.timeout = config.get("timeout", 60)
        self.max_consecutive_auto_reply = config.get("max_consecutive_auto_reply", 10)
        self.num_agents = config.get("num_agents", 2)
        self._agents = None
        self._user_proxy = None

    async def _initialize_agents(self):
        """Lazy initialize AutoGen agents."""
        if self._agents is not None:
            return

        try:
            from autogen import AssistantAgent, UserProxyAgent
            from autogen.agentchat.conversable_agent import ConversableAgent

            # Configure LLM
            config_list = [
                {
                    "model": self.model,
                    "api_key": self.api_key,
                }
            ]

            # Create user proxy
            self._user_proxy = UserProxyAgent(
                name="UserProxy",
                is_human_input_mode=False,
                max_consecutive_auto_reply=self.max_consecutive_auto_reply,
                code_execution_config={"use_docker": False},
            )

            # Create assistant agents
            self._agents = []
            for i in range(self.num_agents):
                agent = AssistantAgent(
                    name=f"Assistant{i+1}",
                    llm_config={
                        "config_list": config_list,
                        "temperature": 0.7,
                    },
                )
                self._agents.append(agent)

        except ImportError as e:
            raise Exception(f"AutoGen library not installed: {str(e)}")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to AutoGen agents.

        Args:
            prompt: User prompt
            system: System context
            **kwargs: Additional parameters

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        try:
            await self._initialize_agents()

            # Prepare message
            message = prompt
            if system:
                message = f"{system}\n\n{prompt}"

            # Initiate conversation with first agent
            if self._agents:
                primary_agent = self._agents[0]

                # Start conversation (non-blocking)
                await self._user_proxy.a_initiate_chat(
                    primary_agent,
                    message=message,
                    max_turns=3,
                )

                # Extract conversation history
                messages = self._user_proxy.chat_messages.get(primary_agent, [])
                response_text = ""

                # Get last assistant message
                for msg in reversed(messages):
                    if msg.get("role") == "assistant":
                        response_text = msg.get("content", "")
                        break

                return AdapterResponse(
                    response=response_text,
                    tokens_used=0,
                    model=f"autogen-{self.model}",
                    latency_ms=self._timing(start),
                    raw={
                        "num_messages": len(messages),
                        "num_agents": len(self._agents),
                    },
                )

            raise Exception("No agents initialized")

        except Exception as e:
            raise Exception(f"AutoGen adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check AutoGen adapter health."""
        try:
            await self._initialize_agents()
            return bool(self._agents and len(self._agents) > 0)
        except Exception:
            return False
