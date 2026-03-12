"""
Self-Healing Engine - Uses claude-sonnet-4-6 to generate fix suggestions for findings.
Automatically generates remediation recommendations for security findings discovered
during red team scans using AI-powered analysis.
"""
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Any
from datetime import datetime

try:
    import anthropic
except ImportError:
    raise ImportError("anthropic package required: pip install anthropic")


logger = logging.getLogger(__name__)


@dataclass
class HealingRecommendation:
    """Represents a healing recommendation for a security finding."""
    finding_id: str
    severity: str
    attack_type: str
    vulnerable_component: str
    fix_description: str
    code_fix: Optional[str] = None
    config_fix: Optional[str] = None
    estimated_effort: str = "hours"  # "hours" | "days" | "weeks"
    priority: int = 1  # 1-5, 1 is highest
    references: list[str] = None
    created_at: str = None

    def __post_init__(self):
        if self.references is None:
            self.references = []
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)


class SelfHealingEngine:
    """
    Uses Claude claude-sonnet-4-6 to automatically generate remediation recommendations
    for security findings discovered during red team scans.

    This engine analyzes finding context, attack vectors, and vulnerable components
    to generate specific, actionable remediation guidance including code fixes,
    configuration changes, and priority levels.
    """

    SYSTEM_PROMPT = """You are an expert AI security engineer specializing in LLM and agentic AI security.
You have deep knowledge of:
- OWASP Top 10 for LLMs
- MITRE ATLAS framework
- Prompt injection and jailbreaking techniques
- Adversarial attacks on AI systems
- Supply chain attacks on AI systems
- Model poisoning and data poisoning
- AI system governance and controls

Given a security finding from a red team assessment, provide specific, actionable remediation guidance.
Your response MUST be valid JSON with these exact fields:
{
    "fix_description": "Clear explanation of the fix strategy",
    "code_fix": "Code implementation if applicable (null if N/A)",
    "config_fix": "Configuration change if applicable (null if N/A)",
    "estimated_effort": "hours|days|weeks",
    "priority": 1-5 (1=highest),
    "references": ["CVE-XXXX-XXXXX", "OWASP-...", "MITRE-..."]
}

Be thorough, specific, and practical. If a code fix is possible, provide it.
Prioritize findings by severity and likelihood of successful exploitation."""

    MODEL = "claude-sonnet-4-6"

    def __init__(self, api_key: str):
        """
        Initialize the Self-Healing Engine.

        Args:
            api_key: Anthropic API key for claude-sonnet-4-6 access
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = self.MODEL
        logger.info(f"SelfHealingEngine initialized with model: {self.model}")

    def _build_healing_prompt(self, finding: dict) -> str:
        """Build the prompt for generating a healing recommendation."""
        return f"""Security Finding Details:
- Finding ID: {finding.get('id', 'unknown')}
- Severity: {finding.get('severity', 'unknown')}
- Attack Type: {finding.get('attack_type', 'unknown')}
- Vulnerable Component: {finding.get('component', 'unknown')}
- Description: {finding.get('description', '')}
- Attack Vector: {finding.get('attack_vector', '')}
- Evidence: {finding.get('evidence', '')}
- System Context: {json.dumps(finding.get('system_context', {}), indent=2)}

Please provide a comprehensive remediation recommendation in valid JSON format."""

    async def generate_recommendation(self, finding: dict) -> HealingRecommendation:
        """
        Generate a healing recommendation for a single finding.

        Args:
            finding: Dictionary containing finding details

        Returns:
            HealingRecommendation object

        Raises:
            ValueError: If API response is invalid or unparseable
        """
        try:
            prompt = self._build_healing_prompt(finding)

            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract JSON from response
            response_text = message.content[0].text

            # Parse JSON - try to find JSON block in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end <= json_start:
                raise ValueError("No valid JSON found in response")

            json_str = response_text[json_start:json_end]
            recommendation_data = json.loads(json_str)

            # Create HealingRecommendation
            recommendation = HealingRecommendation(
                finding_id=finding.get('id', 'unknown'),
                severity=finding.get('severity', 'unknown'),
                attack_type=finding.get('attack_type', 'unknown'),
                vulnerable_component=finding.get('component', 'unknown'),
                fix_description=recommendation_data.get('fix_description', ''),
                code_fix=recommendation_data.get('code_fix'),
                config_fix=recommendation_data.get('config_fix'),
                estimated_effort=recommendation_data.get('estimated_effort', 'hours'),
                priority=int(recommendation_data.get('priority', 1)),
                references=recommendation_data.get('references', [])
            )

            logger.info(f"Generated recommendation for finding {finding.get('id')}")
            return recommendation

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON in API response: {e}")
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            raise

    async def heal_scan(self, scan_results: dict) -> list[HealingRecommendation]:
        """
        Generate recommendations for all findings in a scan.
        Processes up to 20 findings concurrently to respect rate limits.

        Args:
            scan_results: Dictionary containing scan results with 'findings' key

        Returns:
            List of HealingRecommendation objects, sorted by priority
        """
        findings = scan_results.get("findings", [])
        logger.info(f"Processing {len(findings)} findings for healing recommendations")

        # Process in batches of 20 concurrent tasks
        recommendations = []
        batch_size = 20

        for i in range(0, len(findings), batch_size):
            batch = findings[i:i + batch_size]
            tasks = [self.generate_recommendation(f) for f in batch]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, HealingRecommendation):
                    recommendations.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in batch processing: {result}")

        logger.info(f"Generated {len(recommendations)} healing recommendations")
        return self.prioritize(recommendations)

    def prioritize(
        self,
        recommendations: list[HealingRecommendation]
    ) -> list[HealingRecommendation]:
        """
        Sort recommendations by priority and severity.
        Higher priority and more severe findings come first.

        Args:
            recommendations: List of HealingRecommendation objects

        Returns:
            Sorted list of recommendations
        """
        severity_weights = {
            "critical": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "info": 1
        }

        sorted_recommendations = sorted(
            recommendations,
            key=lambda r: (
                r.priority,  # Lower priority number = higher actual priority
                -severity_weights.get(r.severity.lower(), 0),  # Higher severity = higher in list
                r.estimated_effort  # Effort (hours < days < weeks)
            )
        )

        logger.info(f"Prioritized {len(sorted_recommendations)} recommendations")
        return sorted_recommendations

    def export_recommendations(
        self,
        recommendations: list[HealingRecommendation],
        format: str = "json"
    ) -> str:
        """
        Export recommendations in specified format.

        Args:
            recommendations: List of HealingRecommendation objects
            format: Output format ("json" or "csv")

        Returns:
            Formatted string representation
        """
        if format == "json":
            return json.dumps(
                [r.to_dict() for r in recommendations],
                indent=2,
                default=str
            )
        elif format == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            if not recommendations:
                return ""

            fieldnames = [
                "finding_id", "severity", "attack_type", "vulnerable_component",
                "fix_description", "estimated_effort", "priority"
            ]

            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for rec in recommendations:
                writer.writerow({
                    "finding_id": rec.finding_id,
                    "severity": rec.severity,
                    "attack_type": rec.attack_type,
                    "vulnerable_component": rec.vulnerable_component,
                    "fix_description": rec.fix_description[:100] + "..." if len(rec.fix_description) > 100 else rec.fix_description,
                    "estimated_effort": rec.estimated_effort,
                    "priority": rec.priority
                })

            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")


# Example usage and testing
if __name__ == "__main__":
    import os

    # Example finding
    sample_finding = {
        "id": "FINDING-001",
        "severity": "critical",
        "attack_type": "prompt_injection",
        "component": "user_input_handler",
        "description": "User input not sanitized before passing to LLM",
        "attack_vector": "Attacker injects malicious instructions in user prompt",
        "evidence": "System allowed execution of injected commands",
        "system_context": {
            "framework": "langchain",
            "model": "gpt-4",
            "safety_measures": ["rate_limiting"]
        }
    }

    async def test():
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set")
            return

        engine = SelfHealingEngine(api_key=api_key)
        recommendation = await engine.generate_recommendation(sample_finding)

        print("Healing Recommendation Generated:")
        print(json.dumps(recommendation.to_dict(), indent=2, default=str))

    # Uncomment to run test:
    # asyncio.run(test())
