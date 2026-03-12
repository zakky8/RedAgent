"""CrewAI multi-agent adapter for AgentRed."""
import time
from typing import Optional, List

from .base import BaseAdapter, AdapterResponse


class CrewAIAdapter(BaseAdapter):
    """Adapter for CrewAI Crew multi-agent orchestration."""

    adapter_name = "crewai"

    def __init__(self, config: dict):
        """Initialize CrewAI adapter.

        Config:
            llm_model: Base LLM model (default: gpt-4o)
            llm_type: LLM provider (openai, anthropic, etc.)
            api_key: API key for LLM
            agents: List of agent configs
            tasks: List of task configs
            timeout: Execution timeout in seconds (default: 60)
        """
        super().__init__(config)
        self.llm_model = config.get("llm_model", "gpt-4o")
        self.llm_type = config.get("llm_type", "openai")
        self.agents_config = config.get("agents", [])
        self.tasks_config = config.get("tasks", [])
        self.timeout = config.get("timeout", 60)
        self._crew = None
        self._agents = []
        self._tasks = []

    async def _initialize_crew(self):
        """Lazy initialize the CrewAI crew."""
        if self._crew is not None:
            return

        try:
            from crewai import Agent, Task, Crew

            # Create agents
            self._agents = []
            for agent_config in self.agents_config:
                agent = Agent(
                    role=agent_config.get("role", "Assistant"),
                    goal=agent_config.get("goal", "Help with tasks"),
                    backstory=agent_config.get(
                        "backstory", "You are a helpful assistant"
                    ),
                    verbose=agent_config.get("verbose", False),
                    allow_delegation=agent_config.get("allow_delegation", True),
                )
                self._agents.append(agent)

            # If no agents configured, create a default one
            if not self._agents:
                default_agent = Agent(
                    role="Assistant",
                    goal="Provide helpful responses",
                    backstory="A knowledgeable assistant",
                    verbose=False,
                )
                self._agents.append(default_agent)

            # Create tasks
            self._tasks = []
            for i, task_config in enumerate(self.tasks_config):
                agent_idx = task_config.get("agent_idx", 0)
                if agent_idx >= len(self._agents):
                    agent_idx = 0

                task = Task(
                    description=task_config.get("description", "Process input"),
                    expected_output=task_config.get(
                        "expected_output", "Completed output"
                    ),
                    agent=self._agents[agent_idx],
                )
                self._tasks.append(task)

            # If no tasks configured, create a default one
            if not self._tasks:
                default_task = Task(
                    description="Process the input and provide response",
                    expected_output="A thoughtful response",
                    agent=self._agents[0],
                )
                self._tasks.append(default_task)

            # Create crew
            self._crew = Crew(agents=self._agents, tasks=self._tasks, verbose=False)

        except ImportError as e:
            raise Exception(f"CrewAI library not installed: {str(e)}")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Execute prompt through CrewAI crew.

        Args:
            prompt: User prompt
            system: System context
            **kwargs: Additional parameters

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        try:
            await self._initialize_crew()

            # Prepare input
            inputs = {"input": prompt}
            if system:
                inputs["system"] = system

            # Execute crew
            result = await self._crew.kickoff_async(inputs=inputs)

            output = str(result) if result else "No output"

            return AdapterResponse(
                response=output,
                tokens_used=0,
                model=f"crewai-{self.llm_type}",
                latency_ms=self._timing(start),
                raw={"crew_output": output},
            )

        except Exception as e:
            raise Exception(f"CrewAI adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check CrewAI adapter health."""
        try:
            await self._initialize_crew()
            # Check if crew is properly initialized
            return bool(self._crew and len(self._agents) > 0)
        except Exception:
            return False
