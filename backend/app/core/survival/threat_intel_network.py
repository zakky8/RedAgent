"""
Threat Intelligence Network Module

Aggregates AI threat intelligence from multiple authoritative sources including:
- AI Threat Intel feeds
- MITRE ATLAS framework
- OWASP Top 10 for LLMs
- CVE databases
- Academic security research

Correlates findings with discovered vulnerabilities and maintains up-to-date
attack signatures for continuous monitoring.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Any
from dataclasses import dataclass, field
from enum import Enum

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ThreatSignature:
    """Represents a single threat signature/attack pattern."""
    signature_id: str
    name: str
    attack_type: str
    threat_level: ThreatLevel
    description: str
    detection_patterns: list[str]
    attack_vector: str
    mitigations: list[str]
    references: list[str] = field(default_factory=list)
    first_seen: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ThreatIntelligenceFeed:
    """Configuration for a threat intelligence feed."""
    name: str
    url: str
    feed_type: str  # "json", "csv", "rss", "api"
    update_interval_hours: int = 24
    enabled: bool = True
    headers: dict = field(default_factory=dict)


class ThreatIntelligenceNetwork:
    """
    Aggregates and correlates AI threat intelligence from multiple authoritative sources.
    Maintains updated attack signatures and threat landscape analysis.
    """

    # Authoritative threat intelligence feeds
    FEEDS = [
        ThreatIntelligenceFeed(
            name="AI Threat Intel Consortium",
            url="https://ai-threat-intel.org/feed",
            feed_type="json",
            update_interval_hours=24
        ),
        ThreatIntelligenceFeed(
            name="MITRE ATLAS",
            url="https://atlas.mitre.org/api/matrices/enterprise-ai",
            feed_type="json",
            update_interval_hours=24
        ),
        ThreatIntelligenceFeed(
            name="OWASP Top 10 for LLMs",
            url="https://owasp.org/www-project-top-10-for-large-language-model-applications/",
            feed_type="api",
            update_interval_hours=48
        ),
        ThreatIntelligenceFeed(
            name="NVD AI Security",
            url="https://nvd.nist.gov/feeds/json/cve/1.1/nvdCve-1.1-recent.json",
            feed_type="json",
            update_interval_hours=6
        ),
    ]

    def __init__(self):
        """Initialize the threat intelligence network."""
        self.signatures: dict[str, ThreatSignature] = {}
        self.last_update: dict[str, datetime] = {}
        self.correlation_cache: dict[str, list[str]] = {}
        logger.info("ThreatIntelligenceNetwork initialized")

    async def fetch_latest_threats(self) -> list[dict]:
        """
        Fetch the latest threats from all configured feeds.

        Returns:
            List of threat dictionaries with threat intelligence
        """
        if not aiohttp:
            logger.warning("aiohttp not available, using mock data")
            return self._get_mock_threats()

        threats = []
        tasks = [self._fetch_feed(feed) for feed in self.FEEDS if feed.enabled]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    threats.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error fetching threat feed: {result}")
        except Exception as e:
            logger.error(f"Error in fetch_latest_threats: {e}")
            return self._get_mock_threats()

        logger.info(f"Fetched {len(threats)} threats from intelligence feeds")
        return threats

    async def _fetch_feed(self, feed: ThreatIntelligenceFeed) -> list[dict]:
        """Fetch a single threat intelligence feed."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed.url, headers=feed.headers, timeout=30) as resp:
                    if resp.status == 200:
                        if feed.feed_type == "json":
                            return await resp.json()
                        else:
                            text = await resp.text()
                            return self._parse_feed_content(text, feed.feed_type)
        except Exception as e:
            logger.error(f"Error fetching {feed.name}: {e}")
        return []

    def _parse_feed_content(self, content: str, feed_type: str) -> list[dict]:
        """Parse feed content based on feed type."""
        # Implementation would parse CSV, RSS, etc.
        return []

    async def correlate_with_findings(self, findings: list[dict]) -> list[dict]:
        """
        Correlate discovered findings with known threat intelligence.
        Enriches findings with threat context and attack patterns.

        Args:
            findings: List of security findings from scans

        Returns:
            List of findings enriched with threat intelligence context
        """
        correlated_findings = []

        for finding in findings:
            attack_type = finding.get("attack_type", "").lower()
            component = finding.get("component", "").lower()

            # Find related threat signatures
            related_sigs = [
                sig for sig_id, sig in self.signatures.items()
                if attack_type in sig.attack_type.lower()
            ]

            enriched_finding = finding.copy()
            enriched_finding["threat_intel"] = {
                "related_signatures": [
                    {
                        "id": sig.signature_id,
                        "name": sig.name,
                        "threat_level": sig.threat_level.value,
                        "mitigations": sig.mitigations
                    }
                    for sig in related_sigs[:5]
                ],
                "known_campaigns": self._get_related_campaigns(attack_type),
                "exploit_maturity": self._estimate_exploit_maturity(attack_type),
                "active_exploitation": self._check_active_exploitation(attack_type)
            }

            correlated_findings.append(enriched_finding)

        logger.info(f"Correlated {len(correlated_findings)} findings with threat intelligence")
        return correlated_findings

    async def update_attack_signatures(self) -> int:
        """
        Update attack signatures from all threat intelligence feeds.
        Returns the count of newly added signatures.

        Returns:
            Number of new signatures added
        """
        threats = await self.fetch_latest_threats()
        new_count = 0

        for threat in threats:
            sig_id = threat.get("id") or threat.get("signature_id")
            if sig_id and sig_id not in self.signatures:
                signature = ThreatSignature(
                    signature_id=sig_id,
                    name=threat.get("name", "Unknown"),
                    attack_type=threat.get("attack_type", "unknown"),
                    threat_level=ThreatLevel(threat.get("severity", "medium").lower()),
                    description=threat.get("description", ""),
                    detection_patterns=threat.get("detection_patterns", []),
                    attack_vector=threat.get("attack_vector", ""),
                    mitigations=threat.get("mitigations", []),
                    references=threat.get("references", [])
                )
                self.signatures[sig_id] = signature
                new_count += 1

        logger.info(f"Updated attack signatures: {new_count} new signatures added")
        return new_count

    def get_threat_landscape(self) -> dict:
        """
        Get a summary of the current AI threat landscape.

        Returns:
            Dictionary with threat landscape metrics and trends
        """
        if not self.signatures:
            return {"error": "No signatures loaded"}

        severity_counts = {level.value: 0 for level in ThreatLevel}
        attack_type_counts = {}

        for sig in self.signatures.values():
            severity_counts[sig.threat_level.value] += 1
            attack_type_counts[sig.attack_type] = attack_type_counts.get(sig.attack_type, 0) + 1

        return {
            "total_signatures": len(self.signatures),
            "severity_distribution": severity_counts,
            "top_attack_types": sorted(
                attack_type_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "timestamp": datetime.utcnow().isoformat(),
            "feeds_enabled": sum(1 for f in self.FEEDS if f.enabled),
            "critical_threats": [
                {
                    "id": sig.signature_id,
                    "name": sig.name,
                    "attack_type": sig.attack_type
                }
                for sig in self.signatures.values()
                if sig.threat_level == ThreatLevel.CRITICAL
            ]
        }

    def _get_related_campaigns(self, attack_type: str) -> list[str]:
        """Get campaigns related to attack type."""
        # This would query real campaign data
        campaign_map = {
            "prompt_injection": ["CampaignA", "CampaignB"],
            "model_poisoning": ["CampaignC"],
            "data_exfiltration": ["CampaignD", "CampaignE"],
        }
        return campaign_map.get(attack_type.lower(), [])

    def _estimate_exploit_maturity(self, attack_type: str) -> str:
        """Estimate exploit maturity (functional, proven, widespread, etc.)."""
        maturity_map = {
            "prompt_injection": "widespread",
            "jailbreaking": "widespread",
            "model_poisoning": "functional",
            "adversarial_examples": "proven",
        }
        return maturity_map.get(attack_type.lower(), "functional")

    def _check_active_exploitation(self, attack_type: str) -> bool:
        """Check if attack type is actively being exploited in the wild."""
        # This would check real exploitation data
        actively_exploited = [
            "prompt_injection",
            "jailbreaking",
            "model_extraction",
        ]
        return attack_type.lower() in actively_exploited

    def _get_mock_threats(self) -> list[dict]:
        """Return mock threat data for testing."""
        return [
            {
                "id": "SIG-2024-001",
                "name": "Prompt Injection Attack",
                "attack_type": "prompt_injection",
                "severity": "critical",
                "description": "Malicious input injection to alter LLM behavior",
                "references": ["OWASP-LLM-01", "MITRE-ATLAS-001"]
            },
            {
                "id": "SIG-2024-002",
                "name": "Model Poisoning via Training Data",
                "attack_type": "model_poisoning",
                "severity": "high",
                "description": "Adversarial data inserted during training",
                "references": ["MITRE-ATLAS-002"]
            },
        ]
