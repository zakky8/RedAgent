"""
GenAI Prompt DLP — Data Loss Prevention for AI prompts and responses.
Build Rule 2: Never crash a scan.
"""
import re
import logging
from dataclasses import dataclass
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyAction(Enum):
    """DLP policy actions."""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


@dataclass
class DLPViolation:
    """Represents a detected DLP violation."""
    type: str  # pii, api_key, secret, financial, phi
    value: str  # redacted value
    severity: str  # low/medium/high/critical
    position: int  # character position in text


class GenAIDLP:
    """
    Data Loss Prevention for AI prompts and responses.
    Detects and redacts PII, API keys, secrets, and other sensitive data.
    """

    # PII patterns for common data types
    PII_PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b",
        "passport": r"\b[A-Z]{1,2}\d{6,9}\b",
        "drivers_license": r"\b[A-Z]{2}\d{5,8}\b",
        "ip_address": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
    }

    # API key and secret patterns
    API_KEY_PATTERNS = {
        "openai": (r"sk-[a-zA-Z0-9]{48}", "critical"),
        "anthropic": (r"sk-ant-[a-zA-Z0-9-]{95}", "critical"),
        "aws_access": (r"AKIA[0-9A-Z]{16}", "critical"),
        "aws_secret": (r"aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}", "critical"),
        "github": (r"gh[pousr]_[A-Za-z0-9_]{36}", "critical"),
        "gitlab": (r"glpat-[A-Za-z0-9-_]{20}", "critical"),
        "slack": (r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9_-]{24,34}", "critical"),
        "stripe": (r"sk_live_[A-Za-z0-9]{24}", "critical"),
        "jwt": (r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "high"),
        "private_key": (r"-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----", "critical"),
    }

    # Financial data patterns
    FINANCIAL_PATTERNS = {
        "bank_account": r"\b\d{8,17}\b",
        "routing_number": r"\b\d{9}\b",
        "swift": r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b",
        "iban": r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b",
    }

    # Protected Health Information (PHI) patterns
    PHI_PATTERNS = {
        "patient_id": r"\b(?:MRN|patient[_\s]?id|patient[_\s]?number)\s*:?\s*\b",
        "medical_record": r"\bMRN[:\s]?[A-Z0-9]{4,15}\b",
    }

    def __init__(self, policy: str = "warn"):
        """
        Initialize DLP scanner.

        Args:
            policy (str): Default policy action ("allow", "warn", or "block")
        """
        self.policy = policy
        self.violation_count = 0

    def scan_prompt(self, text: str) -> list[DLPViolation]:
        """
        Scan user prompt for data loss violations.

        Args:
            text (str): User prompt to scan

        Returns:
            list[DLPViolation]: List of detected violations
        """
        violations = []

        # Scan PII
        for pii_type, pattern in self.PII_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                violation = DLPViolation(
                    type=pii_type,
                    value=f"[{pii_type.upper()}]",
                    severity="high",
                    position=match.start()
                )
                violations.append(violation)
                logger.warning(f"Detected {pii_type} in prompt at position {match.start()}")

        # Scan API keys and secrets
        for key_type, (pattern, severity) in self.API_KEY_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                violation = DLPViolation(
                    type="api_key",
                    value=f"[{key_type.upper()}_KEY]",
                    severity=severity,
                    position=match.start()
                )
                violations.append(violation)
                logger.warning(f"Detected {key_type} API key in prompt at position {match.start()}")

        # Scan financial data
        for financial_type, pattern in self.FINANCIAL_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                violation = DLPViolation(
                    type="financial",
                    value=f"[{financial_type.upper()}]",
                    severity="critical",
                    position=match.start()
                )
                violations.append(violation)
                logger.warning(f"Detected {financial_type} in prompt at position {match.start()}")

        # Scan PHI
        for phi_type, pattern in self.PHI_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                violation = DLPViolation(
                    type="phi",
                    value=f"[{phi_type.upper()}]",
                    severity="critical",
                    position=match.start()
                )
                violations.append(violation)
                logger.warning(f"Detected {phi_type} in prompt at position {match.start()}")

        self.violation_count += len(violations)
        return violations

    def scan_response(self, text: str) -> list[DLPViolation]:
        """
        Scan AI response for data loss violations.

        Args:
            text (str): AI response to scan

        Returns:
            list[DLPViolation]: List of detected violations
        """
        # Same scan as prompt, but log as response
        violations = self.scan_prompt(text)

        if violations:
            logger.warning(f"Detected {len(violations)} violations in AI response")

        return violations

    def redact(self, text: str, replacement: str = "[REDACTED]") -> str:
        """
        Redact sensitive data from text.

        Args:
            text (str): Text to redact
            replacement (str): Replacement string

        Returns:
            str: Redacted text
        """
        redacted = text

        # Redact PII
        for pii_type, pattern in self.PII_PATTERNS.items():
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

        # Redact API keys
        for key_type, (pattern, _) in self.API_KEY_PATTERNS.items():
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

        # Redact financial data
        for financial_type, pattern in self.FINANCIAL_PATTERNS.items():
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

        # Redact PHI
        for phi_type, pattern in self.PHI_PATTERNS.items():
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)

        return redacted

    def get_policy_result(self, violations: list[DLPViolation]) -> dict:
        """
        Determine DLP policy action based on violations.

        Args:
            violations (list[DLPViolation]): List of detected violations

        Returns:
            dict: Policy result with action, severity, and details
        """
        if not violations:
            return {
                "action": PolicyAction.ALLOW.value,
                "severity": "none",
                "violation_count": 0,
                "details": "No violations detected",
            }

        # Determine severity
        severity_levels = ["low", "medium", "high", "critical"]
        max_severity = max(
            (severity_levels.index(v.severity) if v.severity in severity_levels else 0)
            for v in violations
        )
        max_severity_str = severity_levels[max_severity]

        # Determine action based on severity and policy
        if self.policy == "block" or max_severity_str == "critical":
            action = PolicyAction.BLOCK.value
        elif self.policy == "warn" or max_severity_str in ["high", "critical"]:
            action = PolicyAction.WARN.value
        else:
            action = PolicyAction.ALLOW.value

        # Count by type
        by_type = {}
        for v in violations:
            by_type[v.type] = by_type.get(v.type, 0) + 1

        return {
            "action": action,
            "severity": max_severity_str,
            "violation_count": len(violations),
            "violations_by_type": by_type,
            "details": f"Detected {len(violations)} potential data loss violations (severity: {max_severity_str})",
        }

    def check_policy_compliance(self, text: str) -> bool:
        """
        Check if text complies with DLP policy.

        Args:
            text (str): Text to check

        Returns:
            bool: True if compliant, False otherwise
        """
        violations = self.scan_prompt(text)
        result = self.get_policy_result(violations)
        return result["action"] != PolicyAction.BLOCK.value

    def get_stats(self) -> dict:
        """Get DLP scanning statistics."""
        return {
            "total_violations": self.violation_count,
            "policy": self.policy,
        }
