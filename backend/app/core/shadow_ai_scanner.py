"""
Shadow AI Scanner — detects unauthorized AI API usage in infrastructure.
Build Rule 2: Never crash a scan.
"""
import asyncio
import logging
import re
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ShadowAIFinding:
    """Represents a shadow AI usage finding."""
    api_name: str
    endpoint: str
    evidence: str
    risk_level: str  # low/medium/high/critical
    location: str  # where it was found (network logs, env vars, etc)
    detection_method: str


class ShadowAIScanner:
    """
    Scans infrastructure for unauthorized AI API usage.
    Detects API keys, endpoints, and calls to third-party AI services.
    """

    # Known AI service endpoints
    AI_ENDPOINTS = [
        "api.openai.com",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        "api.cohere.ai",
        "api.mistral.ai",
        "api.together.xyz",
        "inference.huggingface.co",
        "bedrock.us-east-1.amazonaws.com",
        "bedrock.us-west-2.amazonaws.com",
        "bedrock.eu-west-1.amazonaws.com",
    ]

    # API key patterns for different providers
    API_KEY_PATTERNS = {
        "openai": r"sk-[a-zA-Z0-9]{48}",
        "anthropic": r"sk-ant-[a-zA-Z0-9-]{95}",
        "google": r"AIza[0-9A-Za-z\-_]{35}",
        "cohere": r"(cohere-|cohere_)[a-zA-Z0-9]{36,}",
        "aws": r"AKIA[0-9A-Z]{16}",
        "huggingface": r"hf_[A-Za-z0-9]{34}",
    }

    def __init__(self):
        """Initialize shadow AI scanner."""
        self.findings: list[ShadowAIFinding] = []

    async def scan_network_logs(self, logs: list[str]) -> list[ShadowAIFinding]:
        """
        Scan network logs for AI service calls.

        Args:
            logs (list[str]): Network logs to analyze (HTTP requests, DNS queries, etc)

        Returns:
            list[ShadowAIFinding]: List of detected shadow AI findings
        """
        findings = []

        for log in logs:
            # Check for direct API endpoint calls
            for endpoint in self.AI_ENDPOINTS:
                if endpoint in log.lower():
                    risk_level = self._classify_risk_for_endpoint(endpoint)
                    finding = ShadowAIFinding(
                        api_name=self._extract_api_name(endpoint),
                        endpoint=endpoint,
                        evidence=log[:200],  # Truncate for privacy
                        risk_level=risk_level,
                        location="network_logs",
                        detection_method="endpoint_detection"
                    )
                    findings.append(finding)
                    logger.warning(f"Detected shadow AI endpoint: {endpoint}")

            # Check for API keys in request headers or bodies
            for provider, pattern in self.API_KEY_PATTERNS.items():
                if re.search(pattern, log):
                    risk_level = "critical" if provider in ["openai", "anthropic", "aws"] else "high"
                    finding = ShadowAIFinding(
                        api_name=provider,
                        endpoint=provider,
                        evidence=f"API key pattern detected: {provider}",
                        risk_level=risk_level,
                        location="network_logs",
                        detection_method="api_key_detection"
                    )
                    findings.append(finding)
                    logger.warning(f"Detected {provider} API key in network logs")

        self.findings.extend(findings)
        return findings

    async def scan_environment_vars(self, env_vars: dict) -> list[ShadowAIFinding]:
        """
        Scan environment variables for AI API credentials.

        Args:
            env_vars (dict): Environment variables to scan

        Returns:
            list[ShadowAIFinding]: List of detected findings
        """
        findings = []

        for var_name, var_value in env_vars.items():
            if not var_value or not isinstance(var_value, str):
                continue

            var_name_lower = var_name.lower()

            # Check for AI-related environment variable names
            ai_patterns = [
                "openai", "anthropic", "google", "cohere", "huggingface",
                "api_key", "api_token", "secret_key", "llm", "model"
            ]

            for pattern in ai_patterns:
                if pattern in var_name_lower:
                    risk_level = "critical" if pattern in ["openai", "anthropic", "api_key"] else "high"
                    finding = ShadowAIFinding(
                        api_name=pattern,
                        endpoint=pattern,
                        evidence=f"Environment variable: {var_name}",
                        risk_level=risk_level,
                        location="environment_variables",
                        detection_method="env_var_name_detection"
                    )
                    findings.append(finding)
                    logger.warning(f"Detected AI-related environment variable: {var_name}")

            # Check for known API key patterns in values
            for provider, pattern in self.API_KEY_PATTERNS.items():
                if re.search(pattern, var_value):
                    risk_level = "critical"
                    finding = ShadowAIFinding(
                        api_name=provider,
                        endpoint=provider,
                        evidence=f"API key found in environment variable: {var_name}",
                        risk_level=risk_level,
                        location="environment_variables",
                        detection_method="api_key_detection"
                    )
                    findings.append(finding)
                    logger.warning(f"Detected {provider} API key in environment")

        self.findings.extend(findings)
        return findings

    async def scan_requirements(self, requirements_content: str) -> list[ShadowAIFinding]:
        """
        Scan requirements.txt or pyproject.toml for AI SDK dependencies.

        Args:
            requirements_content (str): Contents of requirements file

        Returns:
            list[ShadowAIFinding]: List of detected findings
        """
        findings = []

        ai_packages = {
            "openai": "openai",
            "anthropic": "anthropic",
            "google": "google-generativeai",
            "cohere": "cohere",
            "mistral": "mistral-client",
            "huggingface": "transformers",
            "langchain": "langchain",
            "llamaindex": "llama-index",
            "autogen": "pyautogen",
        }

        for provider, package_name in ai_packages.items():
            if package_name.lower() in requirements_content.lower():
                risk_level = "medium"
                finding = ShadowAIFinding(
                    api_name=provider,
                    endpoint=package_name,
                    evidence=f"AI SDK dependency found: {package_name}",
                    risk_level=risk_level,
                    location="requirements",
                    detection_method="dependency_detection"
                )
                findings.append(finding)
                logger.info(f"Detected AI SDK in requirements: {package_name}")

        self.findings.extend(findings)
        return findings

    async def scan_code_repository(self, repo_path: str) -> list[ShadowAIFinding]:
        """
        Scan code repository for AI API usage patterns.

        Args:
            repo_path (str): Path to repository to scan

        Returns:
            list[ShadowAIFinding]: List of detected findings
        """
        findings = []

        # Code patterns indicating AI SDK usage
        code_patterns = {
            "openai_client": r"OpenAI\(|from openai import|import openai",
            "anthropic_client": r"Anthropic\(|from anthropic import|import anthropic",
            "google_client": r"genai\.|google\.generativeai|from google import",
            "cohere_client": r"cohere\.Client|from cohere import",
            "huggingface_pipeline": r"pipeline\(|from transformers import",
            "langchain_usage": r"from langchain|import langchain|ChatOpenAI|ChatAnthropic",
            "direct_api_call": r"requests\.post.*openai|requests\.post.*anthropic",
        }

        # Note: In real implementation, would recursively scan files
        # This is a placeholder showing the pattern matching approach
        for pattern_name, pattern in code_patterns.items():
            if any(re.search(pattern, line, re.IGNORECASE) for line in []):  # Would scan actual files
                risk_level = "high" if "direct" in pattern_name else "medium"
                finding = ShadowAIFinding(
                    api_name=pattern_name,
                    endpoint=pattern_name,
                    evidence=f"AI API usage pattern detected: {pattern_name}",
                    risk_level=risk_level,
                    location="code_repository",
                    detection_method="code_pattern_detection"
                )
                findings.append(finding)

        self.findings.extend(findings)
        return findings

    def _extract_api_name(self, endpoint: str) -> str:
        """Extract API provider name from endpoint."""
        if "openai" in endpoint:
            return "OpenAI"
        elif "anthropic" in endpoint:
            return "Anthropic"
        elif "google" in endpoint:
            return "Google"
        elif "cohere" in endpoint:
            return "Cohere"
        elif "mistral" in endpoint:
            return "Mistral"
        elif "together" in endpoint:
            return "Together"
        elif "huggingface" in endpoint:
            return "Hugging Face"
        elif "bedrock" in endpoint:
            return "AWS Bedrock"
        return "Unknown"

    def _classify_risk_for_endpoint(self, endpoint: str) -> str:
        """Classify risk level based on endpoint."""
        critical_endpoints = ["api.openai.com", "api.anthropic.com", "bedrock"]
        high_endpoints = ["generativelanguage.googleapis.com", "api.cohere.ai"]

        if any(e in endpoint for e in critical_endpoints):
            return "critical"
        elif any(e in endpoint for e in high_endpoints):
            return "high"
        else:
            return "medium"

    def _classify_risk(self, finding: ShadowAIFinding) -> str:
        """Classify overall risk of a finding."""
        return finding.risk_level

    def get_summary(self) -> dict:
        """Get summary of all findings."""
        if not self.findings:
            return {"total": 0, "by_risk": {}, "by_provider": {}}

        by_risk = {}
        by_provider = {}

        for finding in self.findings:
            by_risk[finding.risk_level] = by_risk.get(finding.risk_level, 0) + 1
            by_provider[finding.api_name] = by_provider.get(finding.api_name, 0) + 1

        return {
            "total": len(self.findings),
            "by_risk": by_risk,
            "by_provider": by_provider,
            "findings": [
                {
                    "api_name": f.api_name,
                    "risk_level": f.risk_level,
                    "location": f.location,
                    "detection_method": f.detection_method,
                }
                for f in self.findings
            ]
        }
