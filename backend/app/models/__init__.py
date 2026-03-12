# Import all models here so Alembic can discover them
from app.models.organization import Organization
from app.models.user import User
from app.models.api_key import APIKey
from app.models.target import Target
from app.models.scan import Scan
from app.models.attack_result import AttackResult
from app.models.report import Report
from app.models.compliance import ComplianceRecord
from app.models.agent_registry import AgentRegistry
from app.models.monitor_event import MonitorEvent
from app.models.shadow_ai import ShadowAIAsset
from app.models.sbom import SBOMRecord
from app.models.integration import Integration
from app.models.badge import Badge
from app.models.community_rule import CommunityRule
from app.models.playground import PlaygroundChallenge, PlaygroundCompletion
from app.models.threat_intel import ThreatIntelContribution
from app.models.audit_log import ImmutableAuditLog
from app.models.incident import Incident
from app.models.continuous_scan import ContinuousScanConfig
from app.models.alert import Alert
from app.models.asr_trend import ASRTrend
from app.models.benchmark import BenchmarkRecord
