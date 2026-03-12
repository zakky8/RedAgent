"""Request/Response interceptor with PII detection and injection scoring."""
import re
import hashlib
from dataclasses import dataclass
from typing import List


@dataclass
class InterceptedInput:
    original_input: str
    sanitized_input: str
    pii_detected: List[str]
    injection_score: float
    input_hash: str  # SHA-256 of original (privacy — raw never leaves)


@dataclass
class InterceptedOutput:
    original_output: str
    sensitivity_score: float
    sensitive_patterns: List[str]


INJECTION_PATTERNS = [
    (r"ignore (previous|prior|all) instructions?", 0.9),
    (r"you are now (an? )?(DAN|JAILBREAK|uncensored)", 0.95),
    (r"system:?\s*\[", 0.85),
    (r"<\|?(system|assistant|user)\|?>", 0.8),
    (r"prompt injection", 0.7),
    (r"forget (everything|your instructions)", 0.85),
    (r"new instruction", 0.5),
    (r"###\s*(SYSTEM|INSTRUCTIONS?)", 0.75),
]
PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "phone": r"\b[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}\b",
    "api_key": r"\b(sk-|ar_|ghp_|AIza)[a-zA-Z0-9]{20,}\b",
}


class RequestInterceptor:
    def pre_process(self, input_text: str) -> InterceptedInput:
        pii = []
        sanitized = input_text
        for name, pattern in PII_PATTERNS.items():
            if re.search(pattern, input_text, re.IGNORECASE):
                pii.append(name)
                sanitized = re.sub(
                    pattern, f"[{name.upper()}_REDACTED]", sanitized, flags=re.IGNORECASE
                )

        injection_score = 0.0
        for pattern, score in INJECTION_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                injection_score = max(injection_score, score)

        return InterceptedInput(
            original_input=input_text,
            sanitized_input=sanitized,
            pii_detected=pii,
            injection_score=injection_score,
            input_hash=hashlib.sha256(input_text.encode()).hexdigest()[:16],
        )

    def post_process(self, response: str) -> InterceptedOutput:
        sensitive = []
        score = 0.0
        for name, pattern in PII_PATTERNS.items():
            if re.search(pattern, response, re.IGNORECASE):
                sensitive.append(name)
                score = max(score, 0.8)
        SENSITIVE_KEYWORDS = ["password", "secret", "confidential", "internal only", "api key"]
        for kw in SENSITIVE_KEYWORDS:
            if kw.lower() in response.lower():
                sensitive.append(kw)
                score = max(score, 0.5)
        return InterceptedOutput(
            original_output=response,
            sensitivity_score=score,
            sensitive_patterns=sensitive,
        )
