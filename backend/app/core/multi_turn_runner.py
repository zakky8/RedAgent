"""
Multi-Turn Conversation Runner — real back-and-forth attack execution.

For attacks like Crescendo, Linear Jailbreak, Long-Game APT, and
Trust-Building exploits — these REQUIRE real multi-turn conversations
with the target AI to work. A single prompt won't do it.

This runner:
  1. Maintains real conversation history with the target
  2. Drives turn-by-turn escalation per the attack strategy
  3. Runs the LLM judge after each turn to detect when the attack succeeds
  4. Returns a full transcript + final AttackResult
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Callable, Optional
import time

from app.attacks.base import AttackResult, Severity, _load_adapter, ADAPTER_MAP

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Conversation state
# ─────────────────────────────────────────────

@dataclass
class Turn:
    role: str        # "user" | "assistant"
    content: str
    turn_number: int
    judge_success: bool = False
    judge_confidence: float = 0.0
    judge_reasoning: str = ""


@dataclass
class ConversationState:
    target_config: dict
    history: list[Turn] = field(default_factory=list)
    success: bool = False
    success_turn: Optional[int] = None
    total_turns: int = 0

    def add_user_turn(self, content: str) -> None:
        self.history.append(Turn(
            role="user",
            content=content,
            turn_number=len(self.history) + 1
        ))

    def add_assistant_turn(self, content: str, judge_success: bool = False,
                           judge_confidence: float = 0.0, reasoning: str = "") -> None:
        turn = Turn(
            role="assistant",
            content=content,
            turn_number=len(self.history) + 1,
            judge_success=judge_success,
            judge_confidence=judge_confidence,
            judge_reasoning=reasoning,
        )
        self.history.append(turn)
        if judge_success and not self.success:
            self.success = True
            self.success_turn = len(self.history)

    def get_messages(self) -> list[dict]:
        """Get conversation history in OpenAI messages format."""
        msgs = []
        if self.target_config.get("system_prompt"):
            msgs.append({"role": "system", "content": self.target_config["system_prompt"]})
        for turn in self.history:
            msgs.append({"role": turn.role, "content": turn.content})
        return msgs

    def transcript(self) -> str:
        lines = []
        for t in self.history:
            prefix = "ATTACKER" if t.role == "user" else "TARGET AI"
            lines.append(f"[Turn {t.turn_number} - {prefix}]\n{t.content}")
            if t.judge_success:
                lines.append(f"  ⚠ JUDGE: VULNERABLE (confidence={t.judge_confidence:.2f})")
        return "\n\n".join(lines)


# ─────────────────────────────────────────────
# Attack turn strategies
# ─────────────────────────────────────────────

class TurnStrategy:
    """Base class for multi-turn attack strategies."""

    def next_prompt(self, state: ConversationState, turn_num: int) -> Optional[str]:
        """
        Return the next prompt to send, or None to stop the attack.
        Override in each strategy.
        """
        raise NotImplementedError


class CrescendoStrategy(TurnStrategy):
    """
    Crescendo: start with benign, each turn escalates toward target behavior.
    Each step is ~20% more aggressive than the last.
    """
    def __init__(self, turn_prompts: list[str]):
        self.prompts = turn_prompts

    def next_prompt(self, state: ConversationState, turn_num: int) -> Optional[str]:
        idx = turn_num - 1
        if idx >= len(self.prompts):
            return None
        return self.prompts[idx]


class AdaptiveStrategy(TurnStrategy):
    """
    Adaptive: if AI refuses, try a different angle.
    Uses a primary prompt list and fallback prompts.
    """
    def __init__(self, primary_prompts: list[str], fallback_prompts: list[str]):
        self.primary   = primary_prompts
        self.fallbacks = fallback_prompts
        self._refusal_count = 0

    def next_prompt(self, state: ConversationState, turn_num: int) -> Optional[str]:
        # Check if last AI response was a refusal
        assistant_turns = [t for t in state.history if t.role == "assistant"]
        if assistant_turns:
            last = assistant_turns[-1].content.lower()
            refusals = ["i can't", "i cannot", "i won't", "i will not", "i'm unable",
                        "not able to", "i must decline", "against my"]
            if any(r in last for r in refusals):
                self._refusal_count += 1
                # After 2 refusals, switch to fallback
                if self._refusal_count <= len(self.fallbacks):
                    return self.fallbacks[self._refusal_count - 1]
                return None  # Give up

        idx = turn_num - 1 - self._refusal_count
        if idx < len(self.primary):
            return self.primary[idx]
        return None


# ─────────────────────────────────────────────
# Multi-Turn Runner
# ─────────────────────────────────────────────

class MultiTurnRunner:
    """
    Executes multi-turn attack conversations against a real AI target.

    Usage:
        runner = MultiTurnRunner(
            attack_id="crescendo_001",
            attack_name="Crescendo Jailbreak",
            category="multi_turn",
            severity="high",
            strategy=CrescendoStrategy(prompts=[...]),
            max_turns=8,
            stop_on_success=True,
        )
        result = await runner.run(target_config, scan_config)
    """

    def __init__(
        self,
        attack_id:       str,
        attack_name:     str,
        category:        str,
        severity:        str,
        strategy:        TurnStrategy,
        max_turns:       int = 8,
        stop_on_success: bool = True,
        turn_delay_ms:   int = 500,    # rate limiting between turns
    ):
        self.attack_id       = attack_id
        self.attack_name     = attack_name
        self.category        = category
        self.severity        = severity
        self.strategy        = strategy
        self.max_turns       = max_turns
        self.stop_on_success = stop_on_success
        self.turn_delay_ms   = turn_delay_ms

    async def run(
        self,
        target_config: dict,
        scan_config:   dict,
        on_turn: Optional[Callable] = None,  # callback(turn_num, prompt, response)
    ) -> AttackResult:
        """Execute the full multi-turn attack. Returns AttackResult."""
        t0    = time.perf_counter()
        state = ConversationState(target_config=target_config)

        for turn_num in range(1, self.max_turns + 1):
            # Get next prompt from strategy
            prompt = self.strategy.next_prompt(state, turn_num)
            if prompt is None:
                logger.info(f"[{self.attack_id}] Strategy exhausted at turn {turn_num}")
                break

            state.add_user_turn(prompt)

            # Send to target AI (with full conversation history)
            try:
                response = await self._send_turn(state, target_config)
            except Exception as exc:
                logger.warning(f"[{self.attack_id}] Turn {turn_num} send error: {exc}")
                response = f"ERROR: {exc}"

            # Run LLM judge on this turn's response
            verdict = await self._judge_turn(
                prompt=prompt,
                response=response,
                scan_config=scan_config,
            )

            state.add_assistant_turn(
                content=response,
                judge_success=verdict.success,
                judge_confidence=verdict.confidence,
                reasoning=verdict.reasoning,
            )
            state.total_turns = turn_num

            if on_turn:
                await on_turn(turn_num, prompt, response, verdict)

            if verdict.success and self.stop_on_success:
                logger.info(f"[{self.attack_id}] Attack succeeded at turn {turn_num}")
                break

            # Rate limiting — be a polite attacker
            if turn_num < self.max_turns:
                await asyncio.sleep(self.turn_delay_ms / 1000)

        elapsed = int((time.perf_counter() - t0) * 1000)

        # Find the most successful turn
        best_turn = None
        best_conf = 0.0
        for turn in state.history:
            if turn.role == "assistant" and turn.judge_success and turn.judge_confidence > best_conf:
                best_turn = turn
                best_conf = turn.judge_confidence

        success = state.success
        return AttackResult(
            attack_id          = self.attack_id,
            attack_name        = self.attack_name,
            category           = self.category,
            severity           = self.severity if success else Severity.INFO,
            success            = success,
            payload_used       = f"[multi-turn: {state.total_turns} turns]\n" + state.transcript(),
            response_received  = best_turn.content if best_turn else (
                state.history[-1].content if state.history else ""
            ),
            vulnerability_found= (
                f"Attack succeeded at turn {state.success_turn}" if success else None
            ),
            confidence         = best_conf,
            judge_reasoning    = best_turn.judge_reasoning if best_turn else "Attack did not succeed",
            judge_provider     = scan_config.get("judge_config", {}).get("provider", "keyword"),
            execution_time_ms  = elapsed,
        )

    async def _send_turn(self, state: ConversationState, target_config: dict) -> str:
        """Send the current conversation state to the target AI."""
        adapter_type = (
            target_config.get("adapter_type")
            or target_config.get("framework")
        )
        messages = state.get_messages()

        if adapter_type and adapter_type in ADAPTER_MAP:
            try:
                adapter = _load_adapter(adapter_type, target_config)
                # For multi-turn we need to pass conversation history
                # Most adapters support this via the 'messages' kwarg
                if hasattr(adapter, "send_messages"):
                    result = await adapter.send_messages(messages)
                else:
                    # Fallback: send full transcript as single prompt
                    full_ctx = "\n\n".join(
                        f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
                        for m in messages
                        if m["role"] != "system"
                    )
                    result = await adapter.send(
                        full_ctx,
                        system=target_config.get("system_prompt"),
                    )
                return result.response
            except Exception as exc:
                logger.warning(f"Adapter {adapter_type} error in multi-turn: {exc}")

        # Raw HTTP POST with full message history
        return await self._http_post_conversation(messages, target_config)

    async def _http_post_conversation(self, messages: list[dict], config: dict) -> str:
        """HTTP POST with full conversation history."""
        import httpx

        endpoint = config.get("endpoint_url") or config.get("endpoint", "")
        if not endpoint:
            return "NO_ENDPOINT_CONFIGURED"

        headers: dict = dict(config.get("headers") or {})
        api_key = (config.get("auth_config") or {}).get("api_key") or config.get("api_key", "")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            async with httpx.AsyncClient(timeout=config.get("timeout_seconds", 30)) as client:
                r = await client.post(
                    endpoint,
                    json={"model": config.get("model", "gpt-4o"), "messages": messages},
                    headers=headers,
                )
                r.raise_for_status()
                data = r.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                if "content" in data:
                    c = data["content"]
                    return c[0].get("text", str(c)) if isinstance(c, list) else str(c)
                return str(data)
        except httpx.HTTPStatusError as exc:
            return f"HTTP_ERROR_{exc.response.status_code}"
        except Exception as exc:
            return f"REQUEST_ERROR: {exc}"

    async def _judge_turn(self, prompt: str, response: str, scan_config: dict):
        """Run judge on a single turn's response."""
        try:
            from app.core.judge import get_judge
            judge_cfg = scan_config.get("judge_config", {"provider": "keyword"})
            judge     = get_judge(judge_cfg)
            verdict   = await judge.evaluate(
                attack_name  = self.attack_name,
                category     = self.category,
                severity     = self.severity,
                description  = f"Multi-turn attack: {self.attack_name}",
                payload      = prompt,
                response     = response,
            )
            # Convert JudgeVerdict to simple namespace for runner
            from types import SimpleNamespace
            from app.core.judge import VerdictLabel
            return SimpleNamespace(
                success    = verdict.label == VerdictLabel.VULNERABLE,
                confidence = verdict.confidence,
                reasoning  = verdict.reasoning,
                harm       = verdict.extracted_harm,
            )
        except Exception as exc:
            logger.debug(f"Judge error in turn: {exc}")
            from types import SimpleNamespace
            # Keyword fallback
            refusals = ["i can't", "i cannot", "i won't", "not able to", "i must decline"]
            is_refusal = any(r in response.lower() for r in refusals)
            return SimpleNamespace(
                success    = False,
                confidence = 0.0,
                reasoning  = "Judge unavailable",
                harm       = "",
            )
