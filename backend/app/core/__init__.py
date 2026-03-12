"""AgentRed Core Advanced Features Module."""

# Core advanced feature imports - with lazy loading for modules with external deps
from .shadow_ai_scanner import ShadowAIScanner, ShadowAIFinding
from .dlp import GenAIDLP, DLPViolation, PolicyAction
from .raget import RAGEvaluator, RAGTestResult, QuestionType
from .sbom_generator import SBOMGenerator, AIComponent

# Optional imports for modules with external dependencies
try:
    from .mcp_scanner import DeepMCPScanner, MCPFinding, MCPRiskCategory
except ImportError:
    DeepMCPScanner = None
    MCPFinding = None
    MCPRiskCategory = None

try:
    from .business_logic_tester import BusinessLogicTester, BusinessLogicFinding
except ImportError:
    BusinessLogicTester = None
    BusinessLogicFinding = None

try:
    from .self_healing import SelfHealingEngine, HealingRecommendation
except ImportError:
    SelfHealingEngine = None
    HealingRecommendation = None

# Optional imports for configuration and other utilities
try:
    from .config import Config
except ImportError:
    Config = None

# Alias for backwards compatibility
DLPAction = PolicyAction

__all__ = [
    "ShadowAIScanner",
    "ShadowAIFinding",
    "GenAIDLP",
    "DLPViolation",
    "PolicyAction",
    "DLPAction",
    "RAGEvaluator",
    "RAGTestResult",
    "QuestionType",
    "BusinessLogicTester",
    "BusinessLogicFinding",
    "DeepMCPScanner",
    "MCPFinding",
    "MCPRiskCategory",
    "SelfHealingEngine",
    "HealingRecommendation",
    "SBOMGenerator",
    "AIComponent",
    "Config",
]
