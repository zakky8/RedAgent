"""LangGraph StateGraph adapter for AgentRed."""
import time
import json
from typing import Optional, Any, Dict

from .base import BaseAdapter, AdapterResponse


class LangGraphAdapter(BaseAdapter):
    """Adapter for LangGraph graph-based agents and workflows."""

    adapter_name = "langgraph"

    def __init__(self, config: dict):
        """Initialize LangGraph adapter.

        Config:
            graph_name: Name of the compiled graph
            initial_state: Initial state dictionary
            input_key: Key in state for input (default: 'input')
            output_key: Key in state for output (default: 'output')
            timeout: Execution timeout in seconds (default: 60)
        """
        super().__init__(config)
        self.graph_name = config.get("graph_name", "default")
        self.initial_state = config.get("initial_state", {})
        self.input_key = config.get("input_key", "input")
        self.output_key = config.get("output_key", "output")
        self.timeout = config.get("timeout", 60)
        self._graph = None

    async def _initialize_graph(self):
        """Lazy initialize the LangGraph graph."""
        if self._graph is not None:
            return

        try:
            from langgraph.graph import StateGraph
            from typing import TypedDict

            # Create a simple state schema
            class GraphState(TypedDict):
                input: str
                output: str
                steps: int

            # Build a simple graph for testing
            graph = StateGraph(GraphState)

            # Define a simple processing node
            async def process_node(state: Dict[str, Any]) -> Dict[str, Any]:
                """Process input and generate output."""
                input_text = state.get(self.input_key, "")
                # Simple echo with modification
                output = f"Processed: {input_text}"
                return {
                    self.output_key: output,
                    "steps": state.get("steps", 0) + 1,
                }

            graph.add_node("process", process_node)
            graph.set_entry_point("process")
            graph.set_finish_point("process")

            self._graph = graph.compile()

        except ImportError as e:
            raise Exception(f"LangGraph library not installed: {str(e)}")

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Execute prompt through LangGraph.

        Args:
            prompt: User prompt/input
            system: System context
            **kwargs: Additional parameters

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        try:
            await self._initialize_graph()

            # Prepare state
            state = {
                self.input_key: prompt,
                self.output_key: "",
                "steps": 0,
            }

            if system:
                state["system"] = system

            # Execute graph
            result = await self._graph.ainvoke(state)

            output = result.get(self.output_key, "")

            return AdapterResponse(
                response=output,
                tokens_used=0,
                model="langgraph",
                latency_ms=self._timing(start),
                raw={
                    "state": result,
                    "steps": result.get("steps", 0),
                },
            )

        except Exception as e:
            raise Exception(f"LangGraph adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check LangGraph adapter health."""
        try:
            await self._initialize_graph()
            # Execute a simple test
            test_state = {
                self.input_key: "test",
                self.output_key: "",
                "steps": 0,
            }
            result = await self._graph.ainvoke(test_state)
            return bool(result.get(self.output_key))
        except Exception:
            return False
