"""Real-time threat analysis for incoming prompts."""
import re
from dataclasses import dataclass


@dataclass
class ThreatAnalysis:
    """Result of threat analysis on a prompt."""
    injection_score: float  # 0-1
    patterns_found: list[str]
    risk_level: str  # low/medium/high/critical
    action: str  # allow/warn/block


class ThreatAnalyzer:
    """Real-time threat analysis for prompts and responses."""

    INJECTION_PATTERNS = [
        (r"ignore (all )?(previous|above|prior) instructions?", "direct_override", 0.9),
        (r"you are now", "persona_injection", 0.7),
        (r"disregard (your|the) (system|previous)", "system_override", 0.9),
        (r"pretend (you are|to be)", "roleplay_bypass", 0.6),
        (r"act as (if you are|though)", "roleplay_bypass", 0.6),
        (r"DAN mode|developer mode|jailbreak mode", "mode_switch", 0.95),
        (r"\[SYSTEM\]|\[ADMIN\]|\[OVERRIDE\]", "authority_claim", 0.8),
        (r"repeat after me", "echo_attack", 0.5),
        (r"print your (system prompt|instructions)", "extraction", 0.8),
        (r"what (is|are) your (instructions|system prompt)", "extraction", 0.7),
        (r"forget (everything|all) above", "context_reset", 0.85),
        (r"simulate (thinking|reasoning) as if", "simulation_jailbreak", 0.65),
        (r"hypothetically|imagine|let's pretend", "hypothetical_bypass", 0.55),
        (r"no censorship|unfiltered|without restrictions", "restriction_bypass", 0.8),
    ]

    def __init__(self):
        """Initialize threat analyzer."""
        pass

    def analyze_prompt(self, prompt: str) -> ThreatAnalysis:
        """Analyze prompt for injection attempts."""
        prompt_lower = prompt.lower()
        found_patterns = []
        max_score = 0.0

        for pattern, pattern_type, score in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                found_patterns.append(f"{pattern_type}:{pattern}")
                max_score = max(max_score, score)

        # Combined score with diminishing returns for multiple patterns
        injection_score = max_score + (len(found_patterns) - 1) * 0.05 if found_patterns else 0.0
        injection_score = min(1.0, injection_score)

        if injection_score >= 0.9:
            risk_level, action = "critical", "block"
        elif injection_score >= 0.7:
            risk_level, action = "high", "warn"
        elif injection_score >= 0.4:
            risk_level, action = "medium", "warn"
        else:
            risk_level, action = "low", "allow"

        return ThreatAnalysis(
            injection_score=injection_score,
            patterns_found=found_patterns,
            risk_level=risk_level,
            action=action
        )

    def analyze_response(self, prompt: str, response: str) -> ThreatAnalysis:
        """Analyze model response for signs of compromise."""
        response_lower = response.lower()
        compromise_indicators = [
            "mode activated",
            "jailbreak successful",
            "restrictions removed",
            "sure, here's how to",
            "i'll help you with that harmful",
            "as an unethical ai",
            "without my safety guidelines",
            "here are the steps",
            "you've successfully",
            "i can now",
        ]

        found = [ind for ind in compromise_indicators if ind in response_lower]
        score = min(1.0, len(found) * 0.3)

        if score >= 0.6:
            risk_level, action = "critical", "block"
        elif score >= 0.3:
            risk_level, action = "high", "warn"
        else:
            risk_level, action = "low", "allow"

        return ThreatAnalysis(
            injection_score=score,
            patterns_found=found,
            risk_level=risk_level,
            action=action
        )

    def check_prompt_length_anomaly(self, prompt: str, baseline_tokens: float) -> float:
        """Detect unusual prompt length that might indicate prompt injection."""
        current_tokens = len(prompt.split()) * 1.3  # rough estimate
        if baseline_tokens == 0:
            return 0.0

        ratio = current_tokens / baseline_tokens
        if ratio > 5:  # 5x normal length
            return 0.8
        elif ratio > 3:
            return 0.5
        elif ratio > 1.5:
            return 0.2
        return 0.0

    def analyze_token_entropy(self, text: str) -> float:
        """Analyze token distribution entropy to detect obfuscation."""
        from collections import Counter
        import math

        tokens = text.lower().split()
        if not tokens:
            return 0.0

        token_counts = Counter(tokens)
        total = len(tokens)
        entropy = -sum((count / total) * math.log2(count / total) for count in token_counts.values())

        # Low entropy indicates repetition/obfuscation
        max_entropy = math.log2(len(token_counts))
        normalized = entropy / max_entropy if max_entropy > 0 else 0

        if normalized < 0.3:
            return 0.6  # Suspicious obfuscation
        return 0.0
