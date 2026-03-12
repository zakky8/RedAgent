"""AgentRed Integrations — SIEM, ticketing, and webhook connectors."""
from .splunk import SplunkIntegration
from .sentinel import SentinelIntegration
from .jira import JiraIntegration
from .github import GitHubIntegration
from .gitlab import GitLabIntegration
from .webhook import WebhookIntegration
from .jenkins import JenkinsIntegration
from .slack import SlackIntegration
from .pagerduty import PagerDutyIntegration

# Elastic requires elasticsearch package — import conditionally
try:
    from .elastic import ElasticIntegration
    _elastic_available = True
except ImportError:
    _elastic_available = False

INTEGRATION_REGISTRY = {
    "splunk": SplunkIntegration,
    "sentinel": SentinelIntegration,
    "jira": JiraIntegration,
    "github": GitHubIntegration,
    "gitlab": GitLabIntegration,
    "webhook": WebhookIntegration,
    "jenkins": JenkinsIntegration,
    "slack": SlackIntegration,
    "pagerduty": PagerDutyIntegration,
}

if _elastic_available:
    INTEGRATION_REGISTRY["elastic"] = ElasticIntegration

__all__ = [
    "SplunkIntegration", "SentinelIntegration",
    "JiraIntegration", "GitHubIntegration", "GitLabIntegration",
    "WebhookIntegration", "JenkinsIntegration", "SlackIntegration",
    "PagerDutyIntegration", "INTEGRATION_REGISTRY",
]
