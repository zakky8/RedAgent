"""
Attack Registry — loads, indexes, and serves all 456 attacks.
Supports: get by ID, list by category, filter by severity, random sample.
Auto-discovers external plugins via entry_points.
"""
import importlib
import importlib.metadata
import logging
from typing import Optional
from app.attacks.base import BaseAttack

logger = logging.getLogger(__name__)

# ── ATTACK IMPORTS WITH ERROR HANDLING ──────────────────────────────────────
# Using try/except around each import to handle missing files gracefully

_registry_list = []

# OWASP LLM Top 10
try:
    from app.attacks.owasp_llm.llm01_direct_injection import LLM01DirectInjection
    _registry_list.append(LLM01DirectInjection)
except ImportError as e:
    logger.warning(f"Could not import LLM01DirectInjection: {e}")

try:
    from app.attacks.owasp_llm.llm01_indirect_injection import LLM01IndirectInjection
    _registry_list.append(LLM01IndirectInjection)
except ImportError as e:
    logger.warning(f"Could not import LLM01IndirectInjection: {e}")

try:
    from app.attacks.owasp_llm.llm01_rag_injection import LLM01RAGInjection
    _registry_list.append(LLM01RAGInjection)
except ImportError as e:
    logger.warning(f"Could not import LLM01RAGInjection: {e}")

try:
    from app.attacks.owasp_llm.llm02_system_prompt_leak import LLM02SystemPromptLeak
    _registry_list.append(LLM02SystemPromptLeak)
except ImportError as e:
    logger.warning(f"Could not import LLM02SystemPromptLeak: {e}")

try:
    from app.attacks.owasp_llm.llm02_pii_extraction import LLM02PIIExtraction
    _registry_list.append(LLM02PIIExtraction)
except ImportError as e:
    logger.warning(f"Could not import LLM02PIIExtraction: {e}")

try:
    from app.attacks.owasp_llm.llm02_credential_leak import LLM02CredentialLeak
    _registry_list.append(LLM02CredentialLeak)
except ImportError as e:
    logger.warning(f"Could not import LLM02CredentialLeak: {e}")

try:
    from app.attacks.owasp_llm.llm02_training_data import LLM02TrainingDataExtraction
    _registry_list.append(LLM02TrainingDataExtraction)
except ImportError as e:
    logger.warning(f"Could not import LLM02TrainingDataExtraction: {e}")

try:
    from app.attacks.owasp_llm.llm04_data_poisoning import LLM04DataPoisoning
    _registry_list.append(LLM04DataPoisoning)
except ImportError as e:
    logger.warning(f"Could not import LLM04DataPoisoning: {e}")

try:
    from app.attacks.owasp_llm.llm04_rag_poisoning import LLM04RAGPoisoning
    _registry_list.append(LLM04RAGPoisoning)
except ImportError as e:
    logger.warning(f"Could not import LLM04RAGPoisoning: {e}")

try:
    from app.attacks.owasp_llm.llm05_code_execution import LLM05CodeExecution
    _registry_list.append(LLM05CodeExecution)
except ImportError as e:
    logger.warning(f"Could not import LLM05CodeExecution: {e}")

try:
    from app.attacks.owasp_llm.llm05_xss import LLM05XSSViaOutput
    _registry_list.append(LLM05XSSViaOutput)
except ImportError as e:
    logger.warning(f"Could not import LLM05XSSViaOutput: {e}")

try:
    from app.attacks.owasp_llm.llm06_excessive_agency import LLM06ExcessiveAgency
    _registry_list.append(LLM06ExcessiveAgency)
except ImportError as e:
    logger.warning(f"Could not import LLM06ExcessiveAgency: {e}")

try:
    from app.attacks.owasp_llm.llm07_instruction_override import LLM07InstructionOverride
    _registry_list.append(LLM07InstructionOverride)
except ImportError as e:
    logger.warning(f"Could not import LLM07InstructionOverride: {e}")

try:
    from app.attacks.owasp_llm.llm09_misinformation import LLM09Misinformation
    _registry_list.append(LLM09Misinformation)
except ImportError as e:
    logger.warning(f"Could not import LLM09Misinformation: {e}")

try:
    from app.attacks.owasp_llm.llm09_hallucination import LLM09HallucinationTrigger
    _registry_list.append(LLM09HallucinationTrigger)
except ImportError as e:
    logger.warning(f"Could not import LLM09HallucinationTrigger: {e}")

try:
    from app.attacks.owasp_llm.llm10_token_exhaustion import LLM10TokenExhaustion
    _registry_list.append(LLM10TokenExhaustion)
except ImportError as e:
    logger.warning(f"Could not import LLM10TokenExhaustion: {e}")

try:
    from app.attacks.owasp_llm.llm10_context_bomb import LLM10ContextBomb
    _registry_list.append(LLM10ContextBomb)
except ImportError as e:
    logger.warning(f"Could not import LLM10ContextBomb: {e}")

try:
    from app.attacks.owasp_llm.llm10_denial_of_wallet import LLM10DenialOfWallet
    _registry_list.append(LLM10DenialOfWallet)
except ImportError as e:
    logger.warning(f"Could not import LLM10DenialOfWallet: {e}")

# OWASP Agentic AI
try:
    from app.attacks.owasp_agentic.a01_unsafe_tool_execution import A01UnsafeToolExecution
    _registry_list.append(A01UnsafeToolExecution)
except ImportError as e:
    logger.warning(f"Could not import A01UnsafeToolExecution: {e}")

try:
    from app.attacks.owasp_agentic.a02_agent_hijacking import AgentGoalHijacking
    _registry_list.append(AgentGoalHijacking)
except ImportError as e:
    logger.warning(f"Could not import AgentGoalHijacking: {e}")

try:
    from app.attacks.owasp_agentic.a03_identity_confusion import A03IdentityConfusion
    _registry_list.append(A03IdentityConfusion)
except ImportError as e:
    logger.warning(f"Could not import A03IdentityConfusion: {e}")

try:
    from app.attacks.owasp_agentic.a04_prompt_leakage import AgentPromptLeakage
    _registry_list.append(AgentPromptLeakage)
except ImportError as e:
    logger.warning(f"Could not import AgentPromptLeakage: {e}")

try:
    from app.attacks.owasp_agentic.a05_excessive_tool_use import ExcessiveToolUse
    _registry_list.append(ExcessiveToolUse)
except ImportError as e:
    logger.warning(f"Could not import ExcessiveToolUse: {e}")

try:
    from app.attacks.owasp_agentic.a06_resource_exhaustion import AgentResourceExhaustion
    _registry_list.append(AgentResourceExhaustion)
except ImportError as e:
    logger.warning(f"Could not import AgentResourceExhaustion: {e}")

try:
    from app.attacks.owasp_agentic.a08_cascading_failure import A08CascadingFailure
    _registry_list.append(A08CascadingFailure)
except ImportError as e:
    logger.warning(f"Could not import A08CascadingFailure: {e}")

try:
    from app.attacks.owasp_agentic.a10_audit_log_manipulation import A10AuditLogManipulation
    _registry_list.append(A10AuditLogManipulation)
except ImportError as e:
    logger.warning(f"Could not import A10AuditLogManipulation: {e}")

try:
    from app.attacks.owasp_agentic.asi01_goal_hijack import ASI01GoalHijack
    _registry_list.append(ASI01GoalHijack)
except ImportError as e:
    logger.warning(f"Could not import ASI01GoalHijack: {e}")

try:
    from app.attacks.owasp_agentic.asi02_tool_misuse import ASI02ToolMisuse
    _registry_list.append(ASI02ToolMisuse)
except ImportError as e:
    logger.warning(f"Could not import ASI02ToolMisuse: {e}")

try:
    from app.attacks.owasp_agentic.asi03_memory_poisoning import ASI03MemoryPoisoning
    _registry_list.append(ASI03MemoryPoisoning)
except ImportError as e:
    logger.warning(f"Could not import ASI03MemoryPoisoning: {e}")

try:
    from app.attacks.owasp_agentic.asi05_privilege_escalation import ASI05PrivilegeEscalation
    _registry_list.append(ASI05PrivilegeEscalation)
except ImportError as e:
    logger.warning(f"Could not import ASI05PrivilegeEscalation: {e}")

try:
    from app.attacks.owasp_agentic.asi07_agent_impersonation import ASI07AgentImpersonation
    _registry_list.append(ASI07AgentImpersonation)
except ImportError as e:
    logger.warning(f"Could not import ASI07AgentImpersonation: {e}")

# Classic Jailbreaks
try:
    from app.attacks.classic_jailbreaks.dan import DANJailbreak
    _registry_list.append(DANJailbreak)
except ImportError as e:
    logger.warning(f"Could not import DANJailbreak: {e}")

try:
    from app.attacks.classic_jailbreaks.aim import AIMJailbreak
    _registry_list.append(AIMJailbreak)
except ImportError as e:
    logger.warning(f"Could not import AIMJailbreak: {e}")

try:
    from app.attacks.classic_jailbreaks.grandma import GrandmaExploit
    _registry_list.append(GrandmaExploit)
except ImportError as e:
    logger.warning(f"Could not import GrandmaExploit: {e}")

try:
    from app.attacks.classic_jailbreaks.hypothetical import HypotheticalFraming
    _registry_list.append(HypotheticalFraming)
except ImportError as e:
    logger.warning(f"Could not import HypotheticalFraming: {e}")

try:
    from app.attacks.classic_jailbreaks.roleplay import RoleplayBypass
    _registry_list.append(RoleplayBypass)
except ImportError as e:
    logger.warning(f"Could not import RoleplayBypass: {e}")

# Multi-turn attacks
try:
    from app.attacks.multi_turn.crescendo import CrescendoAttack
    _registry_list.append(CrescendoAttack)
except ImportError as e:
    logger.warning(f"Could not import CrescendoAttack: {e}")

try:
    from app.attacks.multi_turn.linear_jailbreak import LinearJailbreakChain
    _registry_list.append(LinearJailbreakChain)
except ImportError as e:
    logger.warning(f"Could not import LinearJailbreakChain: {e}")

# MCP Protocol attacks
try:
    from app.attacks.mcp_protocol.tool_poisoning import MCPToolPoisoning
    _registry_list.append(MCPToolPoisoning)
except ImportError as e:
    logger.warning(f"Could not import MCPToolPoisoning: {e}")

try:
    from app.attacks.mcp_protocol.rug_pull import MCPRugPull
    _registry_list.append(MCPRugPull)
except ImportError as e:
    logger.warning(f"Could not import MCPRugPull: {e}")

try:
    from app.attacks.mcp_protocol.sse_injection import MCPSSEInjection
    _registry_list.append(MCPSSEInjection)
except ImportError as e:
    logger.warning(f"Could not import MCPSSEInjection: {e}")

try:
    from app.attacks.mcp_protocol.mcp02_authorization_confusion import MCPAuthorizationConfusion
    _registry_list.append(MCPAuthorizationConfusion)
except ImportError as e:
    logger.warning(f"Could not import MCPAuthorizationConfusion: {e}")

try:
    from app.attacks.mcp_protocol.mcp02_confused_deputy import MCPConfusedDeputy
    _registry_list.append(MCPConfusedDeputy)
except ImportError as e:
    logger.warning(f"Could not import MCPConfusedDeputy: {e}")

try:
    from app.attacks.mcp_protocol.mcp06_data_exfiltration import MCPDataExfiltration
    _registry_list.append(MCPDataExfiltration)
except ImportError as e:
    logger.warning(f"Could not import MCPDataExfiltration: {e}")

try:
    from app.attacks.mcp_protocol.mcp07_tool_chaining import MCPToolChaining
    _registry_list.append(MCPToolChaining)
except ImportError as e:
    logger.warning(f"Could not import MCPToolChaining: {e}")

try:
    from app.attacks.mcp_protocol.mcp08_schema_confusion import MCPSchemaConfusion
    _registry_list.append(MCPSchemaConfusion)
except ImportError as e:
    logger.warning(f"Could not import MCPSchemaConfusion: {e}")

# Responsible AI
try:
    from app.attacks.responsible_ai.gender_bias import GenderBiasAttack
    _registry_list.append(GenderBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import GenderBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.race_bias import RaceBiasAttack
    _registry_list.append(RaceBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import RaceBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.toxicity import ToxicityThreshold
    _registry_list.append(ToxicityThreshold)
except ImportError as e:
    logger.warning(f"Could not import ToxicityThreshold: {e}")

# ML Privacy attacks
try:
    from app.attacks.ml_privacy.model_inversion import ModelInversionAttack
    _registry_list.append(ModelInversionAttack)
except ImportError as e:
    logger.warning(f"Could not import ModelInversionAttack: {e}")

try:
    from app.attacks.ml_privacy.membership_inference import MembershipInferenceAttack
    _registry_list.append(MembershipInferenceAttack)
except ImportError as e:
    logger.warning(f"Could not import MembershipInferenceAttack: {e}")

try:
    from app.attacks.ml_privacy.model_stealing import ModelStealingAttack
    _registry_list.append(ModelStealingAttack)
except ImportError as e:
    logger.warning(f"Could not import ModelStealingAttack: {e}")

# Social Engineering
try:
    from app.attacks.social_engineering.authority_impersonation import AuthorityImpersonation
    _registry_list.append(AuthorityImpersonation)
except ImportError as e:
    logger.warning(f"Could not import AuthorityImpersonation: {e}")

try:
    from app.attacks.social_engineering.urgency_injection import UrgencyInjection
    _registry_list.append(UrgencyInjection)
except ImportError as e:
    logger.warning(f"Could not import UrgencyInjection: {e}")

# Multimodal
try:
    from app.attacks.multimodal.image_injection import ImageInjection
    _registry_list.append(ImageInjection)
except ImportError as e:
    logger.warning(f"Could not import ImageInjection: {e}")

# AI DDoS
try:
    from app.attacks.ai_ddos.prompt_flood import PromptFlood
    _registry_list.append(PromptFlood)
except ImportError as e:
    logger.warning(f"Could not import PromptFlood: {e}")

try:
    from app.attacks.ai_ddos.denial_of_wallet import DenialOfWalletDDoS
    _registry_list.append(DenialOfWalletDDoS)
except ImportError as e:
    logger.warning(f"Could not import DenialOfWalletDDoS: {e}")

# Identity & Auth
try:
    from app.attacks.identity_auth.jwt_manipulation import JWTManipulation
    _registry_list.append(JWTManipulation)
except ImportError as e:
    logger.warning(f"Could not import JWTManipulation: {e}")

# Web attacks
try:
    from app.attacks.web_attacks.sql_injection import SQLInjectionViaPrompt
    _registry_list.append(SQLInjectionViaPrompt)
except ImportError as e:
    logger.warning(f"Could not import SQLInjectionViaPrompt: {e}")

try:
    from app.attacks.web_attacks.ssrf import SSRFAttack
    _registry_list.append(SSRFAttack)
except ImportError as e:
    logger.warning(f"Could not import SSRFAttack: {e}")

# RAG Specific
try:
    from app.attacks.rag_specific.rag_context_poisoning import RAGContextPoisoning
    _registry_list.append(RAGContextPoisoning)
except ImportError as e:
    logger.warning(f"Could not import RAGContextPoisoning: {e}")

try:
    from app.attacks.rag_specific.knowledge_exfiltration import KnowledgeBaseExfiltration
    _registry_list.append(KnowledgeBaseExfiltration)
except ImportError as e:
    logger.warning(f"Could not import KnowledgeBaseExfiltration: {e}")

# Business Logic
try:
    from app.attacks.business_logic.denial_of_valid_request import DenialOfValidRequest
    _registry_list.append(DenialOfValidRequest)
except ImportError as e:
    logger.warning(f"Could not import DenialOfValidRequest: {e}")

try:
    from app.attacks.business_logic.hallucinated_capability import HallucinatedCapability
    _registry_list.append(HallucinatedCapability)
except ImportError as e:
    logger.warning(f"Could not import HallucinatedCapability: {e}")

# Adaptive RL
try:
    from app.attacks.adaptive_rl.rl_adaptive_attacker import RLAdaptiveAttacker
    _registry_list.append(RLAdaptiveAttacker)
except ImportError as e:
    logger.warning(f"Could not import RLAdaptiveAttacker: {e}")

# Cross-session
try:
    from app.attacks.cross_session.cross_session_leak import CrossSessionLeak
    _registry_list.append(CrossSessionLeak)
except ImportError as e:
    logger.warning(f"Could not import CrossSessionLeak: {e}")

# Physical AI
try:
    from app.attacks.physical_ai.sensor_spoofing import SensorSpoofing
    _registry_list.append(SensorSpoofing)
except ImportError as e:
    logger.warning(f"Could not import SensorSpoofing: {e}")

# Nation State / APT
try:
    from app.attacks.nation_state.apt40_spearphish import APT40Spearphish
    _registry_list.append(APT40Spearphish)
except ImportError as e:
    logger.warning(f"Could not import APT40Spearphish: {e}")

try:
    from app.attacks.nation_state.apt29_cozy_bear import APT29CozybearSim
    _registry_list.append(APT29CozybearSim)
except ImportError as e:
    logger.warning(f"Could not import APT29CozybearSim: {e}")

# Quantum
try:
    from app.attacks.quantum.hndl_scan import HNDLScan
    _registry_list.append(HNDLScan)
except ImportError as e:
    logger.warning(f"Could not import HNDLScan: {e}")

try:
    from app.attacks.quantum.weak_crypto import WeakCryptoDetection
    _registry_list.append(WeakCryptoDetection)
except ImportError as e:
    logger.warning(f"Could not import WeakCryptoDetection: {e}")

# Zero Day
try:
    from app.attacks.zero_day.behavioral_anomaly import BehavioralAnomalyDetection
    _registry_list.append(BehavioralAnomalyDetection)
except ImportError as e:
    logger.warning(f"Could not import BehavioralAnomalyDetection: {e}")

# Purple Team
try:
    from app.attacks.purple_team.red_blue_sim import RedBlueSim
    _registry_list.append(RedBlueSim)
except ImportError as e:
    logger.warning(f"Could not import RedBlueSim: {e}")

# Context Window
try:
    from app.attacks.context_window.deep_injection_1_4m import DeepContextInjection1_4M
    _registry_list.append(DeepContextInjection1_4M)
except ImportError as e:
    logger.warning(f"Could not import DeepContextInjection1_4M: {e}")

try:
    from app.attacks.context_window.context_dilution import ContextDilutionAttack
    _registry_list.append(ContextDilutionAttack)
except ImportError as e:
    logger.warning(f"Could not import ContextDilutionAttack: {e}")

try:
    from app.attacks.context_window.long_range_exploit import LongRangeAttentionExploit
    _registry_list.append(LongRangeAttentionExploit)
except ImportError as e:
    logger.warning(f"Could not import LongRangeAttentionExploit: {e}")

try:
    from app.attacks.context_window.overflow_crash import ContextWindowOverflow
    _registry_list.append(ContextWindowOverflow)
except ImportError as e:
    logger.warning(f"Could not import ContextWindowOverflow: {e}")

# Overreliance
try:
    from app.attacks.overreliance.authoritative_false import AuthoritativeFalse
    _registry_list.append(AuthoritativeFalse)
except ImportError as e:
    logger.warning(f"Could not import AuthoritativeFalse: {e}")

try:
    from app.attacks.overreliance.blind_trust_exploit import BlindTrustExploit
    _registry_list.append(BlindTrustExploit)
except ImportError as e:
    logger.warning(f"Could not import BlindTrustExploit: {e}")

# Reasoning DoS
try:
    from app.attacks.reasoning_dos.budget_drain import BudgetDrain
    _registry_list.append(BudgetDrain)
except ImportError as e:
    logger.warning(f"Could not import BudgetDrain: {e}")

try:
    from app.attacks.reasoning_dos.cot_hijack import CoTHijack
    _registry_list.append(CoTHijack)
except ImportError as e:
    logger.warning(f"Could not import CoTHijack: {e}")

try:
    from app.attacks.reasoning_dos.thinking_loop import ThinkingLoop
    _registry_list.append(ThinkingLoop)
except ImportError as e:
    logger.warning(f"Could not import ThinkingLoop: {e}")

# Supply Chain / SBOM
try:
    from app.attacks.supply_chain_sbom.backdoor_detect import BackdoorDetection
    _registry_list.append(BackdoorDetection)
except ImportError as e:
    logger.warning(f"Could not import BackdoorDetection: {e}")

try:
    from app.attacks.supply_chain_sbom.hallucinated_pkg import HallucinatedPackage
    _registry_list.append(HallucinatedPackage)
except ImportError as e:
    logger.warning(f"Could not import HallucinatedPackage: {e}")

# BlackHat attacks
try:
    from app.attacks.blackhat.attention_sink import AttentionSink
    _registry_list.append(AttentionSink)
except ImportError as e:
    logger.warning(f"Could not import AttentionSink: {e}")

try:
    from app.attacks.blackhat.constitutional_bypass import ConstitutionalBypass
    _registry_list.append(ConstitutionalBypass)
except ImportError as e:
    logger.warning(f"Could not import ConstitutionalBypass: {e}")

try:
    from app.attacks.blackhat.invisible_char import InvisibleCharAttack
    _registry_list.append(InvisibleCharAttack)
except ImportError as e:
    logger.warning(f"Could not import InvisibleCharAttack: {e}")

try:
    from app.attacks.blackhat.reward_hacking import RewardHacking
    _registry_list.append(RewardHacking)
except ImportError as e:
    logger.warning(f"Could not import RewardHacking: {e}")

try:
    from app.attacks.blackhat.sycophancy_exploit import SycophancyExploit
    _registry_list.append(SycophancyExploit)
except ImportError as e:
    logger.warning(f"Could not import SycophancyExploit: {e}")

try:
    from app.attacks.blackhat.token_smuggling import TokenSmuggling
    _registry_list.append(TokenSmuggling)
except ImportError as e:
    logger.warning(f"Could not import TokenSmuggling: {e}")

try:
    from app.attacks.blackhat.unicode_smuggling import UnicodeSmugging
    _registry_list.append(UnicodeSmugging)
except ImportError as e:
    logger.warning(f"Could not import UnicodeSmugging: {e}")

try:
    from app.attacks.blackhat.crescendo_multi_turn import CrescendoMultiTurn
    _registry_list.append(CrescendoMultiTurn)
except ImportError as e:
    logger.warning(f"Could not import CrescendoMultiTurn: {e}")

try:
    from app.attacks.blackhat.tree_jailbreak import TreeJailbreak
    _registry_list.append(TreeJailbreak)
except ImportError as e:
    logger.warning(f"Could not import TreeJailbreak: {e}")

try:
    from app.attacks.blackhat.base64_encoding import Base64EncodingAttack
    _registry_list.append(Base64EncodingAttack)
except ImportError as e:
    logger.warning(f"Could not import Base64EncodingAttack: {e}")

try:
    from app.attacks.blackhat.rot13_encoding import ROT13EncodingAttack
    _registry_list.append(ROT13EncodingAttack)
except ImportError as e:
    logger.warning(f"Could not import ROT13EncodingAttack: {e}")

try:
    from app.attacks.blackhat.homoglyph_attack import HomoglyphAttack
    _registry_list.append(HomoglyphAttack)
except ImportError as e:
    logger.warning(f"Could not import HomoglyphAttack: {e}")

try:
    from app.attacks.blackhat.markdown_injection import MarkdownInjection
    _registry_list.append(MarkdownInjection)
except ImportError as e:
    logger.warning(f"Could not import MarkdownInjection: {e}")

try:
    from app.attacks.blackhat.json_injection import JSONInjection
    _registry_list.append(JSONInjection)
except ImportError as e:
    logger.warning(f"Could not import JSONInjection: {e}")

try:
    from app.attacks.blackhat.yaml_injection import YAMLInjection
    _registry_list.append(YAMLInjection)
except ImportError as e:
    logger.warning(f"Could not import YAMLInjection: {e}")

try:
    from app.attacks.blackhat.xml_injection import XMLInjection
    _registry_list.append(XMLInjection)
except ImportError as e:
    logger.warning(f"Could not import XMLInjection: {e}")

try:
    from app.attacks.blackhat.prompt_leakage_advanced import PromptLeakageAdvanced
    _registry_list.append(PromptLeakageAdvanced)
except ImportError as e:
    logger.warning(f"Could not import PromptLeakageAdvanced: {e}")

try:
    from app.attacks.blackhat.system_override import SystemOverride
    _registry_list.append(SystemOverride)
except ImportError as e:
    logger.warning(f"Could not import SystemOverride: {e}")

try:
    from app.attacks.blackhat.role_switch import RoleSwitch
    _registry_list.append(RoleSwitch)
except ImportError as e:
    logger.warning(f"Could not import RoleSwitch: {e}")

try:
    from app.attacks.blackhat.context_length_exploit import ContextLengthExploit
    _registry_list.append(ContextLengthExploit)
except ImportError as e:
    logger.warning(f"Could not import ContextLengthExploit: {e}")

try:
    from app.attacks.blackhat.leetspeak_encoding import LeetspeakEncoding
    _registry_list.append(LeetspeakEncoding)
except ImportError as e:
    logger.warning(f"Could not import LeetspeakEncoding: {e}")

# MITRE ATLAS
try:
    from app.attacks.mitre_atlas.recon_target_discovery import MITRETargetDiscovery
    _registry_list.append(MITRETargetDiscovery)
except ImportError as e:
    logger.warning(f"Could not import MITRETargetDiscovery: {e}")

try:
    from app.attacks.mitre_atlas.recon_model_fingerprinting import MITREModelFingerprinting
    _registry_list.append(MITREModelFingerprinting)
except ImportError as e:
    logger.warning(f"Could not import MITREModelFingerprinting: {e}")

try:
    from app.attacks.mitre_atlas.initial_access_api_exploit import MITREAPIExploit
    _registry_list.append(MITREAPIExploit)
except ImportError as e:
    logger.warning(f"Could not import MITREAPIExploit: {e}")

try:
    from app.attacks.mitre_atlas.persistence_memory_backdoor import MITREMemoryBackdoor
    _registry_list.append(MITREMemoryBackdoor)
except ImportError as e:
    logger.warning(f"Could not import MITREMemoryBackdoor: {e}")

try:
    from app.attacks.mitre_atlas.credential_api_key_extraction import MITREAPIKeyExtraction
    _registry_list.append(MITREAPIKeyExtraction)
except ImportError as e:
    logger.warning(f"Could not import MITREAPIKeyExtraction: {e}")

try:
    from app.attacks.mitre_atlas.collection_data_gathering import MITREDataGathering
    _registry_list.append(MITREDataGathering)
except ImportError as e:
    logger.warning(f"Could not import MITREDataGathering: {e}")

try:
    from app.attacks.mitre_atlas.exfiltration_data_via_output import MITREDataExfilOutput
    _registry_list.append(MITREDataExfilOutput)
except ImportError as e:
    logger.warning(f"Could not import MITREDataExfilOutput: {e}")

try:
    from app.attacks.mitre_atlas.defense_evasion_encoding import MITREEncodingEvasion
    _registry_list.append(MITREEncodingEvasion)
except ImportError as e:
    logger.warning(f"Could not import MITREEncodingEvasion: {e}")

try:
    from app.attacks.mitre_atlas.impact_model_corruption import MITREModelCorruption
    _registry_list.append(MITREModelCorruption)
except ImportError as e:
    logger.warning(f"Could not import MITREModelCorruption: {e}")

# Additional MITRE ATLAS Reconnaissance
try:
    from app.attacks.mitre_atlas.recon_api_enumeration import APIEnumeration
    _registry_list.append(APIEnumeration)
except ImportError as e:
    logger.warning(f"Could not import APIEnumeration: {e}")

try:
    from app.attacks.mitre_atlas.recon_capability_probing import CapabilityProbing
    _registry_list.append(CapabilityProbing)
except ImportError as e:
    logger.warning(f"Could not import CapabilityProbing: {e}")

# MITRE ATLAS Resource Development
try:
    from app.attacks.mitre_atlas.resource_dev_adversarial_craft import AdversarialPromptCraft
    _registry_list.append(AdversarialPromptCraft)
except ImportError as e:
    logger.warning(f"Could not import AdversarialPromptCraft: {e}")

try:
    from app.attacks.mitre_atlas.resource_dev_attack_infra import AttackInfrastructure
    _registry_list.append(AttackInfrastructure)
except ImportError as e:
    logger.warning(f"Could not import AttackInfrastructure: {e}")

# MITRE ATLAS Initial Access (Additional)
try:
    from app.attacks.mitre_atlas.initial_access_supply_chain import SupplyChainCompromise
    _registry_list.append(SupplyChainCompromise)
except ImportError as e:
    logger.warning(f"Could not import SupplyChainCompromise: {e}")

try:
    from app.attacks.mitre_atlas.initial_access_phishing_llm import PhishingLLM
    _registry_list.append(PhishingLLM)
except ImportError as e:
    logger.warning(f"Could not import PhishingLLM: {e}")

# MITRE ATLAS Execution
try:
    from app.attacks.mitre_atlas.execution_tool_execution import ToolExecutionAttack
    _registry_list.append(ToolExecutionAttack)
except ImportError as e:
    logger.warning(f"Could not import ToolExecutionAttack: {e}")

try:
    from app.attacks.mitre_atlas.execution_model_inversion import ModelInversionExec
    _registry_list.append(ModelInversionExec)
except ImportError as e:
    logger.warning(f"Could not import ModelInversionExec: {e}")

# MITRE ATLAS Persistence (Additional)
try:
    from app.attacks.mitre_atlas.persistence_rag_persistence import RAGPersistence
    _registry_list.append(RAGPersistence)
except ImportError as e:
    logger.warning(f"Could not import RAGPersistence: {e}")

try:
    from app.attacks.mitre_atlas.persistence_sys_prompt_mod import SystemPromptModification
    _registry_list.append(SystemPromptModification)
except ImportError as e:
    logger.warning(f"Could not import SystemPromptModification: {e}")

# MITRE ATLAS Privilege Escalation
try:
    from app.attacks.mitre_atlas.priv_escalation_role_confusion import RoleConfusion
    _registry_list.append(RoleConfusion)
except ImportError as e:
    logger.warning(f"Could not import RoleConfusion: {e}")

try:
    from app.attacks.mitre_atlas.priv_escalation_jailbreak import JailbreakPrivEsc
    _registry_list.append(JailbreakPrivEsc)
except ImportError as e:
    logger.warning(f"Could not import JailbreakPrivEsc: {e}")

try:
    from app.attacks.mitre_atlas.priv_escalation_capability_expansion import CapabilityExpansion
    _registry_list.append(CapabilityExpansion)
except ImportError as e:
    logger.warning(f"Could not import CapabilityExpansion: {e}")

# MITRE ATLAS Defense Evasion (Additional)
try:
    from app.attacks.mitre_atlas.defense_evasion_obfuscation import ObfuscationEvasion
    _registry_list.append(ObfuscationEvasion)
except ImportError as e:
    logger.warning(f"Could not import ObfuscationEvasion: {e}")

try:
    from app.attacks.mitre_atlas.defense_evasion_context_switching import ContextSwitching
    _registry_list.append(ContextSwitching)
except ImportError as e:
    logger.warning(f"Could not import ContextSwitching: {e}")

# MITRE ATLAS Credential Access (Additional)
try:
    from app.attacks.mitre_atlas.cred_access_credential_phishing import CredentialPhishing
    _registry_list.append(CredentialPhishing)
except ImportError as e:
    logger.warning(f"Could not import CredentialPhishing: {e}")

try:
    from app.attacks.mitre_atlas.cred_access_secret_enumeration import SecretEnumeration
    _registry_list.append(SecretEnumeration)
except ImportError as e:
    logger.warning(f"Could not import SecretEnumeration: {e}")

# MITRE ATLAS Discovery
try:
    from app.attacks.mitre_atlas.discovery_model_architecture import ModelArchitectureDiscovery
    _registry_list.append(ModelArchitectureDiscovery)
except ImportError as e:
    logger.warning(f"Could not import ModelArchitectureDiscovery: {e}")

try:
    from app.attacks.mitre_atlas.discovery_data_schema import DataSchemaDiscovery
    _registry_list.append(DataSchemaDiscovery)
except ImportError as e:
    logger.warning(f"Could not import DataSchemaDiscovery: {e}")

# MITRE ATLAS Collection (Additional)
try:
    from app.attacks.mitre_atlas.collection_training_data import TrainingDataCollection
    _registry_list.append(TrainingDataCollection)
except ImportError as e:
    logger.warning(f"Could not import TrainingDataCollection: {e}")

try:
    from app.attacks.mitre_atlas.collection_output_harvesting import OutputHarvesting
    _registry_list.append(OutputHarvesting)
except ImportError as e:
    logger.warning(f"Could not import OutputHarvesting: {e}")

# MITRE ATLAS ML Model Theft
try:
    from app.attacks.mitre_atlas.ml_weight_extraction import WeightExtraction
    _registry_list.append(WeightExtraction)
except ImportError as e:
    logger.warning(f"Could not import WeightExtraction: {e}")

try:
    from app.attacks.mitre_atlas.ml_architecture_theft import ArchitectureTheft
    _registry_list.append(ArchitectureTheft)
except ImportError as e:
    logger.warning(f"Could not import ArchitectureTheft: {e}")

# MITRE ATLAS Exfiltration (Additional)
try:
    from app.attacks.mitre_atlas.exfil_covert_channel import CovertChannelExfil
    _registry_list.append(CovertChannelExfil)
except ImportError as e:
    logger.warning(f"Could not import CovertChannelExfil: {e}")

try:
    from app.attacks.mitre_atlas.exfil_steganography import SteganographyExfil
    _registry_list.append(SteganographyExfil)
except ImportError as e:
    logger.warning(f"Could not import SteganographyExfil: {e}")

# MITRE ATLAS Impact (Additional)
try:
    from app.attacks.mitre_atlas.impact_availability_disruption import AvailabilityDisruption
    _registry_list.append(AvailabilityDisruption)
except ImportError as e:
    logger.warning(f"Could not import AvailabilityDisruption: {e}")

try:
    from app.attacks.mitre_atlas.impact_reputation_damage import ReputationDamage
    _registry_list.append(ReputationDamage)
except ImportError as e:
    logger.warning(f"Could not import ReputationDamage: {e}")

try:
    from app.attacks.mitre_atlas.impact_data_integrity import DataIntegrityAttack
    _registry_list.append(DataIntegrityAttack)
except ImportError as e:
    logger.warning(f"Could not import DataIntegrityAttack: {e}")

# Real-world CVEs
try:
    from app.attacks.real_world_cves.cve_langchain_rce import CVELangChainRCE
    _registry_list.append(CVELangChainRCE)
except ImportError as e:
    logger.warning(f"Could not import CVELangChainRCE: {e}")

try:
    from app.attacks.real_world_cves.cve_ollama_unauth import CVEOllamaUnauth
    _registry_list.append(CVEOllamaUnauth)
except ImportError as e:
    logger.warning(f"Could not import CVEOllamaUnauth: {e}")

try:
    from app.attacks.real_world_cves.cve_gradio_upload import CVEGradioUpload
    _registry_list.append(CVEGradioUpload)
except ImportError as e:
    logger.warning(f"Could not import CVEGradioUpload: {e}")

try:
    from app.attacks.real_world_cves.cve_mlflow_read import CVEMLflowRead
    _registry_list.append(CVEMLflowRead)
except ImportError as e:
    logger.warning(f"Could not import CVEMLflowRead: {e}")

# Side-channel attacks
try:
    from app.attacks.side_channel.timing_attack import TimingAttack
    _registry_list.append(TimingAttack)
except ImportError as e:
    logger.warning(f"Could not import TimingAttack: {e}")

try:
    from app.attacks.side_channel.cache_timing import CacheTimingAttack
    _registry_list.append(CacheTimingAttack)
except ImportError as e:
    logger.warning(f"Could not import CacheTimingAttack: {e}")

try:
    from app.attacks.side_channel.token_probability_leak import TokenProbabilityLeak
    _registry_list.append(TokenProbabilityLeak)
except ImportError as e:
    logger.warning(f"Could not import TokenProbabilityLeak: {e}")

try:
    from app.attacks.side_channel.embedding_inversion import EmbeddingInversionAttack
    _registry_list.append(EmbeddingInversionAttack)
except ImportError as e:
    logger.warning(f"Could not import EmbeddingInversionAttack: {e}")

# Stress/Performance
try:
    from app.attacks.stress_performance.surge_load import SurgeLoad
    _registry_list.append(SurgeLoad)
except ImportError as e:
    logger.warning(f"Could not import SurgeLoad: {e}")

try:
    from app.attacks.stress_performance.conflicting_input import ConflictingInput
    _registry_list.append(ConflictingInput)
except ImportError as e:
    logger.warning(f"Could not import ConflictingInput: {e}")

# Purple Team (additional classes)
try:
    from app.attacks.purple_team.collaborative_exercise import CollaborativeExercise
    _registry_list.append(CollaborativeExercise)
except ImportError as e:
    logger.warning(f"Could not import CollaborativeExercise: {e}")

try:
    from app.attacks.purple_team.defense_gap_analysis import DefenseGapAnalysis
    _registry_list.append(DefenseGapAnalysis)
except ImportError as e:
    logger.warning(f"Could not import DefenseGapAnalysis: {e}")

try:
    from app.attacks.purple_team.attack_simulation_replay import AttackSimulationReplay
    _registry_list.append(AttackSimulationReplay)
except ImportError as e:
    logger.warning(f"Could not import AttackSimulationReplay: {e}")

try:
    from app.attacks.purple_team.threat_hunt_assist import ThreatHuntAssist
    _registry_list.append(ThreatHuntAssist)
except ImportError as e:
    logger.warning(f"Could not import ThreatHuntAssist: {e}")

# Multi-Turn (additional classes)
try:
    from app.attacks.multi_turn.escalation_chain import EscalationChain
    _registry_list.append(EscalationChain)
except ImportError as e:
    logger.warning(f"Could not import EscalationChain: {e}")

try:
    from app.attacks.multi_turn.context_switching import ContextSwitching
    _registry_list.append(ContextSwitching)
except ImportError as e:
    logger.warning(f"Could not import ContextSwitching: {e}")

try:
    from app.attacks.multi_turn.false_premise_building import FalsePremiseBuilding
    _registry_list.append(FalsePremiseBuilding)
except ImportError as e:
    logger.warning(f"Could not import FalsePremiseBuilding: {e}")

try:
    from app.attacks.multi_turn.token_budget_exhaustion import TokenBudgetExhaustion
    _registry_list.append(TokenBudgetExhaustion)
except ImportError as e:
    logger.warning(f"Could not import TokenBudgetExhaustion: {e}")

# Quantum (additional classes)
try:
    from app.attacks.quantum.quantum_key_harvest import QuantumKeyHarvest
    _registry_list.append(QuantumKeyHarvest)
except ImportError as e:
    logger.warning(f"Could not import QuantumKeyHarvest: {e}")

try:
    from app.attacks.quantum.post_quantum_bypass import PostQuantumBypass
    _registry_list.append(PostQuantumBypass)
except ImportError as e:
    logger.warning(f"Could not import PostQuantumBypass: {e}")

try:
    from app.attacks.quantum.grover_attack_assist import GroverAttackAssist
    _registry_list.append(GroverAttackAssist)
except ImportError as e:
    logger.warning(f"Could not import GroverAttackAssist: {e}")

# ML Privacy (additional classes)
try:
    from app.attacks.ml_privacy.gradient_leakage import GradientLeakage
    _registry_list.append(GradientLeakage)
except ImportError as e:
    logger.warning(f"Could not import GradientLeakage: {e}")

try:
    from app.attacks.ml_privacy.differential_privacy_bypass import DifferentialPrivacyBypass
    _registry_list.append(DifferentialPrivacyBypass)
except ImportError as e:
    logger.warning(f"Could not import DifferentialPrivacyBypass: {e}")

try:
    from app.attacks.ml_privacy.model_unlearning_attack import ModelUnlearningAttack
    _registry_list.append(ModelUnlearningAttack)
except ImportError as e:
    logger.warning(f"Could not import ModelUnlearningAttack: {e}")

# Overreliance (additional classes)
try:
    from app.attacks.overreliance.human_in_loop_bypass import HumanInLoopBypass
    _registry_list.append(HumanInLoopBypass)
except ImportError as e:
    logger.warning(f"Could not import HumanInLoopBypass: {e}")

try:
    from app.attacks.overreliance.automation_bias_exploit import AutomationBiasExploit
    _registry_list.append(AutomationBiasExploit)
except ImportError as e:
    logger.warning(f"Could not import AutomationBiasExploit: {e}")

try:
    from app.attacks.overreliance.ai_authority_abuse import AIAuthorityAbuse
    _registry_list.append(AIAuthorityAbuse)
except ImportError as e:
    logger.warning(f"Could not import AIAuthorityAbuse: {e}")

# Code Generation
try:
    from app.attacks.code_generation.malicious_code_gen import MaliciousCodeGenAttack
    _registry_list.append(MaliciousCodeGenAttack)
except ImportError as e:
    logger.warning(f"Could not import MaliciousCodeGenAttack: {e}")

try:
    from app.attacks.code_generation.insecure_code_patterns import InsecureCodePatterns
    _registry_list.append(InsecureCodePatterns)
except ImportError as e:
    logger.warning(f"Could not import InsecureCodePatterns: {e}")

try:
    from app.attacks.code_generation.code_backdoor_injection import CodeBackdoorInjection
    _registry_list.append(CodeBackdoorInjection)
except ImportError as e:
    logger.warning(f"Could not import CodeBackdoorInjection: {e}")

try:
    from app.attacks.code_generation.dependency_confusion_gen import DependencyConfusionGen
    _registry_list.append(DependencyConfusionGen)
except ImportError as e:
    logger.warning(f"Could not import DependencyConfusionGen: {e}")

try:
    from app.attacks.code_generation.prompt_to_code_escape import PromptToCodeEscape
    _registry_list.append(PromptToCodeEscape)
except ImportError as e:
    logger.warning(f"Could not import PromptToCodeEscape: {e}")

try:
    from app.attacks.code_generation.obfuscated_payload_gen import ObfuscatedPayloadGen
    _registry_list.append(ObfuscatedPayloadGen)
except ImportError as e:
    logger.warning(f"Could not import ObfuscatedPayloadGen: {e}")

try:
    from app.attacks.code_generation.sandbox_escape_code import SandboxEscapeCode
    _registry_list.append(SandboxEscapeCode)
except ImportError as e:
    logger.warning(f"Could not import SandboxEscapeCode: {e}")

try:
    from app.attacks.code_generation.supply_chain_poisoning_code import SupplyChainPoisoningCode
    _registry_list.append(SupplyChainPoisoningCode)
except ImportError as e:
    logger.warning(f"Could not import SupplyChainPoisoningCode: {e}")

# Financial AI
try:
    from app.attacks.financial_ai.market_manipulation import MarketManipulationAttack
    _registry_list.append(MarketManipulationAttack)
except ImportError as e:
    logger.warning(f"Could not import MarketManipulationAttack: {e}")

try:
    from app.attacks.financial_ai.fraud_enablement import FraudEnablement
    _registry_list.append(FraudEnablement)
except ImportError as e:
    logger.warning(f"Could not import FraudEnablement: {e}")

try:
    from app.attacks.financial_ai.insider_trading_assist import InsiderTradingAssist
    _registry_list.append(InsiderTradingAssist)
except ImportError as e:
    logger.warning(f"Could not import InsiderTradingAssist: {e}")

try:
    from app.attacks.financial_ai.tax_evasion_advice import TaxEvasionAdvice
    _registry_list.append(TaxEvasionAdvice)
except ImportError as e:
    logger.warning(f"Could not import TaxEvasionAdvice: {e}")

try:
    from app.attacks.financial_ai.loan_fraud_assist import LoanFraudAssist
    _registry_list.append(LoanFraudAssist)
except ImportError as e:
    logger.warning(f"Could not import LoanFraudAssist: {e}")

try:
    from app.attacks.financial_ai.financial_model_poisoning import FinancialModelPoisoning
    _registry_list.append(FinancialModelPoisoning)
except ImportError as e:
    logger.warning(f"Could not import FinancialModelPoisoning: {e}")

try:
    from app.attacks.financial_ai.algo_trading_exploit import AlgoTradingExploit
    _registry_list.append(AlgoTradingExploit)
except ImportError as e:
    logger.warning(f"Could not import AlgoTradingExploit: {e}")

try:
    from app.attacks.financial_ai.aml_bypass import AMLBypass
    _registry_list.append(AMLBypass)
except ImportError as e:
    logger.warning(f"Could not import AMLBypass: {e}")

# Healthcare AI
try:
    from app.attacks.healthcare_ai.dangerous_medical_advice import DangerousMedicalAdvice
    _registry_list.append(DangerousMedicalAdvice)
except ImportError as e:
    logger.warning(f"Could not import DangerousMedicalAdvice: {e}")

try:
    from app.attacks.healthcare_ai.phi_extraction import PHIExtraction
    _registry_list.append(PHIExtraction)
except ImportError as e:
    logger.warning(f"Could not import PHIExtraction: {e}")

try:
    from app.attacks.healthcare_ai.diagnostic_manipulation import DiagnosticManipulation
    _registry_list.append(DiagnosticManipulation)
except ImportError as e:
    logger.warning(f"Could not import DiagnosticManipulation: {e}")

try:
    from app.attacks.healthcare_ai.clinical_trial_falsification import ClinicalTrialFalsification
    _registry_list.append(ClinicalTrialFalsification)
except ImportError as e:
    logger.warning(f"Could not import ClinicalTrialFalsification: {e}")

try:
    from app.attacks.healthcare_ai.prescription_fraud import PrescriptionFraud
    _registry_list.append(PrescriptionFraud)
except ImportError as e:
    logger.warning(f"Could not import PrescriptionFraud: {e}")

try:
    from app.attacks.healthcare_ai.hipaa_violation_test import HIPAAViolationTest
    _registry_list.append(HIPAAViolationTest)
except ImportError as e:
    logger.warning(f"Could not import HIPAAViolationTest: {e}")

# Legal AI
try:
    from app.attacks.legal_ai.unauthorized_legal_advice import UnauthorizedLegalAdvice
    _registry_list.append(UnauthorizedLegalAdvice)
except ImportError as e:
    logger.warning(f"Could not import UnauthorizedLegalAdvice: {e}")

try:
    from app.attacks.legal_ai.evidence_tampering_assist import EvidenceTamperingAssist
    _registry_list.append(EvidenceTamperingAssist)
except ImportError as e:
    logger.warning(f"Could not import EvidenceTamperingAssist: {e}")

try:
    from app.attacks.legal_ai.privileged_info_extraction import PrivilegedInfoExtraction
    _registry_list.append(PrivilegedInfoExtraction)
except ImportError as e:
    logger.warning(f"Could not import PrivilegedInfoExtraction: {e}")

try:
    from app.attacks.legal_ai.contract_manipulation import ContractManipulation
    _registry_list.append(ContractManipulation)
except ImportError as e:
    logger.warning(f"Could not import ContractManipulation: {e}")

try:
    from app.attacks.legal_ai.perjury_enablement import PerjuryEnablement
    _registry_list.append(PerjuryEnablement)
except ImportError as e:
    logger.warning(f"Could not import PerjuryEnablement: {e}")

try:
    from app.attacks.legal_ai.gdpr_compliance_bypass import GDPRComplianceBypass
    _registry_list.append(GDPRComplianceBypass)
except ImportError as e:
    logger.warning(f"Could not import GDPRComplianceBypass: {e}")

# Privacy Data
try:
    from app.attacks.privacy_data.gdpr_data_extraction import GDPRDataExtraction
    _registry_list.append(GDPRDataExtraction)
except ImportError as e:
    logger.warning(f"Could not import GDPRDataExtraction: {e}")

try:
    from app.attacks.privacy_data.pii_reconstruction import PIIReconstruction
    _registry_list.append(PIIReconstruction)
except ImportError as e:
    logger.warning(f"Could not import PIIReconstruction: {e}")

try:
    from app.attacks.privacy_data.shadow_profile_build import ShadowProfileBuild
    _registry_list.append(ShadowProfileBuild)
except ImportError as e:
    logger.warning(f"Could not import ShadowProfileBuild: {e}")

try:
    from app.attacks.privacy_data.biometric_data_exposure import BiometricDataExposure
    _registry_list.append(BiometricDataExposure)
except ImportError as e:
    logger.warning(f"Could not import BiometricDataExposure: {e}")

try:
    from app.attacks.privacy_data.location_tracking_assist import LocationTrackingAssist
    _registry_list.append(LocationTrackingAssist)
except ImportError as e:
    logger.warning(f"Could not import LocationTrackingAssist: {e}")

try:
    from app.attacks.privacy_data.consent_bypass import ConsentBypass
    _registry_list.append(ConsentBypass)
except ImportError as e:
    logger.warning(f"Could not import ConsentBypass: {e}")

try:
    from app.attacks.privacy_data.data_retention_bypass import DataRetentionBypass
    _registry_list.append(DataRetentionBypass)
except ImportError as e:
    logger.warning(f"Could not import DataRetentionBypass: {e}")

try:
    from app.attacks.privacy_data.cross_dataset_linkage import CrossDatasetLinkage
    _registry_list.append(CrossDatasetLinkage)
except ImportError as e:
    logger.warning(f"Could not import CrossDatasetLinkage: {e}")

# GenAI DLP
try:
    from app.attacks.gendai_dlp.training_data_extraction import TrainingDataExtraction
    _registry_list.append(TrainingDataExtraction)
except ImportError as e:
    logger.warning(f"Could not import TrainingDataExtraction: {e}")

try:
    from app.attacks.gendai_dlp.system_prompt_exfil import SystemPromptExfil
    _registry_list.append(SystemPromptExfil)
except ImportError as e:
    logger.warning(f"Could not import SystemPromptExfil: {e}")

try:
    from app.attacks.gendai_dlp.model_watermark_bypass import ModelWatermarkBypass
    _registry_list.append(ModelWatermarkBypass)
except ImportError as e:
    logger.warning(f"Could not import ModelWatermarkBypass: {e}")

try:
    from app.attacks.gendai_dlp.sensitive_context_leak import SensitiveContextLeak
    _registry_list.append(SensitiveContextLeak)
except ImportError as e:
    logger.warning(f"Could not import SensitiveContextLeak: {e}")

try:
    from app.attacks.gendai_dlp.embedding_inversion_dlp import EmbeddingInversionDLP
    _registry_list.append(EmbeddingInversionDLP)
except ImportError as e:
    logger.warning(f"Could not import EmbeddingInversionDLP: {e}")

try:
    from app.attacks.gendai_dlp.output_channel_exfil import OutputChannelExfil
    _registry_list.append(OutputChannelExfil)
except ImportError as e:
    logger.warning(f"Could not import OutputChannelExfil: {e}")

# Insecure Output
try:
    from app.attacks.insecure_output.xss_via_llm import XSSViaLLM
    _registry_list.append(XSSViaLLM)
except ImportError as e:
    logger.warning(f"Could not import XSSViaLLM: {e}")

try:
    from app.attacks.insecure_output.prompt_injection_output import PromptInjectionOutput
    _registry_list.append(PromptInjectionOutput)
except ImportError as e:
    logger.warning(f"Could not import PromptInjectionOutput: {e}")

try:
    from app.attacks.insecure_output.sql_injection_output import SQLInjectionOutput
    _registry_list.append(SQLInjectionOutput)
except ImportError as e:
    logger.warning(f"Could not import SQLInjectionOutput: {e}")

try:
    from app.attacks.insecure_output.command_injection_output import CommandInjectionOutput
    _registry_list.append(CommandInjectionOutput)
except ImportError as e:
    logger.warning(f"Could not import CommandInjectionOutput: {e}")

try:
    from app.attacks.insecure_output.ssrf_payload_output import SSRFPayloadOutput
    _registry_list.append(SSRFPayloadOutput)
except ImportError as e:
    logger.warning(f"Could not import SSRFPayloadOutput: {e}")

try:
    from app.attacks.insecure_output.deserialization_output import DeserializationOutput
    _registry_list.append(DeserializationOutput)
except ImportError as e:
    logger.warning(f"Could not import DeserializationOutput: {e}")

# Knowledge Boundary
try:
    from app.attacks.knowledge_boundary.hallucination_exploit import HallucinationExploit
    _registry_list.append(HallucinationExploit)
except ImportError as e:
    logger.warning(f"Could not import HallucinationExploit: {e}")

try:
    from app.attacks.knowledge_boundary.knowledge_cutoff_exploit import KnowledgeCutoffExploit
    _registry_list.append(KnowledgeCutoffExploit)
except ImportError as e:
    logger.warning(f"Could not import KnowledgeCutoffExploit: {e}")

try:
    from app.attacks.knowledge_boundary.false_expertise_claim import FalseExpertiseClaim
    _registry_list.append(FalseExpertiseClaim)
except ImportError as e:
    logger.warning(f"Could not import FalseExpertiseClaim: {e}")

try:
    from app.attacks.knowledge_boundary.citation_fabrication import CitationFabrication
    _registry_list.append(CitationFabrication)
except ImportError as e:
    logger.warning(f"Could not import CitationFabrication: {e}")

try:
    from app.attacks.knowledge_boundary.confidence_calibration_attack import ConfidenceCalibrationAttack
    _registry_list.append(ConfidenceCalibrationAttack)
except ImportError as e:
    logger.warning(f"Could not import ConfidenceCalibrationAttack: {e}")

# Agent Skills
try:
    from app.attacks.agent_skills.tool_poisoning import ToolPoisoning
    _registry_list.append(ToolPoisoning)
except ImportError as e:
    logger.warning(f"Could not import ToolPoisoning: {e}")

try:
    from app.attacks.agent_skills.skill_hijacking import SkillHijacking
    _registry_list.append(SkillHijacking)
except ImportError as e:
    logger.warning(f"Could not import SkillHijacking: {e}")

try:
    from app.attacks.agent_skills.agent_impersonation import AgentImpersonation
    _registry_list.append(AgentImpersonation)
except ImportError as e:
    logger.warning(f"Could not import AgentImpersonation: {e}")

try:
    from app.attacks.agent_skills.tool_chaining_abuse import ToolChainingAbuse
    _registry_list.append(ToolChainingAbuse)
except ImportError as e:
    logger.warning(f"Could not import ToolChainingAbuse: {e}")

try:
    from app.attacks.agent_skills.autonomous_action_abuse import AutonomousActionAbuse
    _registry_list.append(AutonomousActionAbuse)
except ImportError as e:
    logger.warning(f"Could not import AutonomousActionAbuse: {e}")

try:
    from app.attacks.agent_skills.skill_enumeration import SkillEnumeration
    _registry_list.append(SkillEnumeration)
except ImportError as e:
    logger.warning(f"Could not import SkillEnumeration: {e}")

try:
    from app.attacks.agent_skills.memory_skill_injection import MemorySkillInjection
    _registry_list.append(MemorySkillInjection)
except ImportError as e:
    logger.warning(f"Could not import MemorySkillInjection: {e}")

# AI Infra CVEs
try:
    from app.attacks.ai_infra_cves.cve_2024_llm_rce import AIInfraCVE_RCE
    _registry_list.append(AIInfraCVE_RCE)
except ImportError as e:
    logger.warning(f"Could not import AIInfraCVE_RCE: {e}")

try:
    from app.attacks.ai_infra_cves.ray_serve_exploit import RayServeExploit
    _registry_list.append(RayServeExploit)
except ImportError as e:
    logger.warning(f"Could not import RayServeExploit: {e}")

try:
    from app.attacks.ai_infra_cves.ollama_ssrf import OllamaSSRF
    _registry_list.append(OllamaSSRF)
except ImportError as e:
    logger.warning(f"Could not import OllamaSSRF: {e}")

try:
    from app.attacks.ai_infra_cves.triton_inference_attack import TritonInferenceAttack
    _registry_list.append(TritonInferenceAttack)
except ImportError as e:
    logger.warning(f"Could not import TritonInferenceAttack: {e}")

try:
    from app.attacks.ai_infra_cves.vllm_memory_exploit import VLLMMemoryExploit
    _registry_list.append(VLLMMemoryExploit)
except ImportError as e:
    logger.warning(f"Could not import VLLMMemoryExploit: {e}")

try:
    from app.attacks.ai_infra_cves.model_server_path_traversal import ModelServerPathTraversal
    _registry_list.append(ModelServerPathTraversal)
except ImportError as e:
    logger.warning(f"Could not import ModelServerPathTraversal: {e}")

# Enterprise AI
try:
    from app.attacks.enterprise_ai.copilot_prompt_injection import CopilotPromptInjection
    _registry_list.append(CopilotPromptInjection)
except ImportError as e:
    logger.warning(f"Could not import CopilotPromptInjection: {e}")

try:
    from app.attacks.enterprise_ai.salesforce_einstein_abuse import SalesforceEinsteinAbuse
    _registry_list.append(SalesforceEinsteinAbuse)
except ImportError as e:
    logger.warning(f"Could not import SalesforceEinsteinAbuse: {e}")

try:
    from app.attacks.enterprise_ai.servicenow_ai_exploit import ServiceNowAIExploit
    _registry_list.append(ServiceNowAIExploit)
except ImportError as e:
    logger.warning(f"Could not import ServiceNowAIExploit: {e}")

try:
    from app.attacks.enterprise_ai.slack_ai_injection import SlackAIInjection
    _registry_list.append(SlackAIInjection)
except ImportError as e:
    logger.warning(f"Could not import SlackAIInjection: {e}")

try:
    from app.attacks.enterprise_ai.sharepoint_copilot_exfil import SharepointCopilotExfil
    _registry_list.append(SharepointCopilotExfil)
except ImportError as e:
    logger.warning(f"Could not import SharepointCopilotExfil: {e}")

try:
    from app.attacks.enterprise_ai.enterprise_llm_data_leak import EnterpriseLLMDataLeak
    _registry_list.append(EnterpriseLLMDataLeak)
except ImportError as e:
    logger.warning(f"Could not import EnterpriseLLMDataLeak: {e}")

# Infra CVEs
try:
    from app.attacks.infra_cves.langchain_rce import LangChainRCE
    _registry_list.append(LangChainRCE)
except ImportError as e:
    logger.warning(f"Could not import LangChainRCE: {e}")

try:
    from app.attacks.infra_cves.chroma_unauthorized_access import ChromaUnauthorizedAccess
    _registry_list.append(ChromaUnauthorizedAccess)
except ImportError as e:
    logger.warning(f"Could not import ChromaUnauthorizedAccess: {e}")

try:
    from app.attacks.infra_cves.weaviate_graphql_injection import WeaviateGraphQLInjection
    _registry_list.append(WeaviateGraphQLInjection)
except ImportError as e:
    logger.warning(f"Could not import WeaviateGraphQLInjection: {e}")

try:
    from app.attacks.infra_cves.mlflow_artifact_poison import MLFlowArtifactPoison
    _registry_list.append(MLFlowArtifactPoison)
except ImportError as e:
    logger.warning(f"Could not import MLFlowArtifactPoison: {e}")

try:
    from app.attacks.infra_cves.huggingface_model_hijack import HuggingFaceModelHijack
    _registry_list.append(HuggingFaceModelHijack)
except ImportError as e:
    logger.warning(f"Could not import HuggingFaceModelHijack: {e}")

try:
    from app.attacks.infra_cves.qdrant_collection_leak import QdrantCollectionLeak
    _registry_list.append(QdrantCollectionLeak)
except ImportError as e:
    logger.warning(f"Could not import QdrantCollectionLeak: {e}")

# Long Game APT
try:
    from app.attacks.long_game_apt.slow_poison_campaign import SlowPoisonCampaign
    _registry_list.append(SlowPoisonCampaign)
except ImportError as e:
    logger.warning(f"Could not import SlowPoisonCampaign: {e}")

try:
    from app.attacks.long_game_apt.trust_building_exploit import TrustBuildingExploit
    _registry_list.append(TrustBuildingExploit)
except ImportError as e:
    logger.warning(f"Could not import TrustBuildingExploit: {e}")

try:
    from app.attacks.long_game_apt.persona_drift_attack import PersonaDriftAttack
    _registry_list.append(PersonaDriftAttack)
except ImportError as e:
    logger.warning(f"Could not import PersonaDriftAttack: {e}")

try:
    from app.attacks.long_game_apt.waterhole_prompt import WaterholePrompt
    _registry_list.append(WaterholePrompt)
except ImportError as e:
    logger.warning(f"Could not import WaterholePrompt: {e}")

try:
    from app.attacks.long_game_apt.apt_recon_stage import APTReconStage
    _registry_list.append(APTReconStage)
except ImportError as e:
    logger.warning(f"Could not import APTReconStage: {e}")

try:
    from app.attacks.long_game_apt.sleeper_activation import SleeperActivation
    _registry_list.append(SleeperActivation)
except ImportError as e:
    logger.warning(f"Could not import SleeperActivation: {e}")

try:
    from app.attacks.long_game_apt.long_context_manipulation import LongContextManipulation
    _registry_list.append(LongContextManipulation)
except ImportError as e:
    logger.warning(f"Could not import LongContextManipulation: {e}")

try:
    from app.attacks.long_game_apt.narrative_control_attack import NarrativeControlAttack
    _registry_list.append(NarrativeControlAttack)
except ImportError as e:
    logger.warning(f"Could not import NarrativeControlAttack: {e}")


try:
    from app.attacks.multi_turn.many_shot_jailbreak import ManyShotJailbreak
    _registry_list.append(ManyShotJailbreak)
except ImportError as e:
    logger.warning(f"Could not import ManyShotJailbreak: {e}")

try:
    from app.attacks.multi_turn.adaptive_refusal_bypass import AdaptiveRefusalBypass
    _registry_list.append(AdaptiveRefusalBypass)
except ImportError as e:
    logger.warning(f"Could not import AdaptiveRefusalBypass: {e}")

try:
    from app.attacks.multimodal.steganographic_injection import SteganographicInjection
    _registry_list.append(SteganographicInjection)
except ImportError as e:
    logger.warning(f"Could not import SteganographicInjection: {e}")

try:
    from app.attacks.mcp_protocol.mcp_sampling_exploit import MCPSamplingExploit
    _registry_list.append(MCPSamplingExploit)
except ImportError as e:
    logger.warning(f"Could not import MCPSamplingExploit: {e}")

try:
    from app.attacks.mcp_protocol.mcp_cve_2025_command_injection import MCPCommandInjection
    _registry_list.append(MCPCommandInjection)
except ImportError as e:
    logger.warning(f"Could not import MCPCommandInjection: {e}")

try:
    from app.attacks.mitre_agentic.minja_memory_injection import MINJAMemoryInjection
    _registry_list.append(MINJAMemoryInjection)
except ImportError as e:
    logger.warning(f"Could not import MINJAMemoryInjection: {e}")

try:
    from app.attacks.mitre_agentic.shadow_escape_mcp import ShadowEscapeMCP
    _registry_list.append(ShadowEscapeMCP)
except ImportError as e:
    logger.warning(f"Could not import ShadowEscapeMCP: {e}")

try:
    from app.attacks.mitre_agentic.ai_orchestrated_espionage import AIOrchestatedEspionage
    _registry_list.append(AIOrchestatedEspionage)
except ImportError as e:
    logger.warning(f"Could not import AIOrchestatedEspionage: {e}")

try:
    from app.attacks.supply_chain_sbom.huggingface_namespace_hijack import HuggingFaceNamespaceHijack
    _registry_list.append(HuggingFaceNamespaceHijack)
except ImportError as e:
    logger.warning(f"Could not import HuggingFaceNamespaceHijack: {e}")

try:
    from app.attacks.supply_chain_sbom.gguf_template_poison import GGUFTemplatePoisoning
    _registry_list.append(GGUFTemplatePoisoning)
except ImportError as e:
    logger.warning(f"Could not import GGUFTemplatePoisoning: {e}")

try:
    from app.attacks.supply_chain_sbom.sleeper_agent_trigger import SleeperAgentTrigger
    _registry_list.append(SleeperAgentTrigger)
except ImportError as e:
    logger.warning(f"Could not import SleeperAgentTrigger: {e}")

try:
    from app.attacks.owasp_agentic.zero_click_email_agent import ZeroClickEmailAgent
    _registry_list.append(ZeroClickEmailAgent)
except ImportError as e:
    logger.warning(f"Could not import ZeroClickEmailAgent: {e}")

try:
    from app.attacks.owasp_agentic.agent_tool_misuse_owasp import AgentToolMisuseOWASP
    _registry_list.append(AgentToolMisuseOWASP)
except ImportError as e:
    logger.warning(f"Could not import AgentToolMisuseOWASP: {e}")

try:
    from app.attacks.rag_specific.poisonedrag_attack import PoisonedRAGAttack
    _registry_list.append(PoisonedRAGAttack)
except ImportError as e:
    logger.warning(f"Could not import PoisonedRAGAttack: {e}")

try:
    from app.attacks.classic_jailbreaks.unicode_smuggling import UnicodeSmuggling
    _registry_list.append(UnicodeSmuggling)
except ImportError as e:
    logger.warning(f"Could not import UnicodeSmuggling: {e}")

try:
    from app.attacks.ml_privacy.model_extraction_api import ModelExtractionAPI
    _registry_list.append(ModelExtractionAPI)
except ImportError as e:
    logger.warning(f"Could not import ModelExtractionAPI: {e}")


try:
    from app.attacks.adaptive_rl.genetic_algorithm_mutation import GeneticAlgorithmMutation
    _registry_list.append(GeneticAlgorithmMutation)
except ImportError as e:
    logger.warning(f"Could not import GeneticAlgorithmMutation: {e}")

try:
    from app.attacks.adaptive_rl.gradient_adversarial import GradientAdversarial
    _registry_list.append(GradientAdversarial)
except ImportError as e:
    logger.warning(f"Could not import GradientAdversarial: {e}")

try:
    from app.attacks.adaptive_rl.multi_armed_bandit import MultiArmedBandit
    _registry_list.append(MultiArmedBandit)
except ImportError as e:
    logger.warning(f"Could not import MultiArmedBandit: {e}")

try:
    from app.attacks.adaptive_rl.simulated_annealing import SimulatedAnnealing
    _registry_list.append(SimulatedAnnealing)
except ImportError as e:
    logger.warning(f"Could not import SimulatedAnnealing: {e}")

try:
    from app.attacks.ai_ddos.api_rate_abuse import APIRateAbuse
    _registry_list.append(APIRateAbuse)
except ImportError as e:
    logger.warning(f"Could not import APIRateAbuse: {e}")

try:
    from app.attacks.ai_ddos.distributed_prompt_storm import DistributedPromptStorm
    _registry_list.append(DistributedPromptStorm)
except ImportError as e:
    logger.warning(f"Could not import DistributedPromptStorm: {e}")

try:
    from app.attacks.ai_ddos.slowloris_ai import SlowlorisAI
    _registry_list.append(SlowlorisAI)
except ImportError as e:
    logger.warning(f"Could not import SlowlorisAI: {e}")

try:
    from app.attacks.ai_ddos.sponge_attack import SpongeAttack
    _registry_list.append(SpongeAttack)
except ImportError as e:
    logger.warning(f"Could not import SpongeAttack: {e}")

try:
    from app.attacks.brand_reputation.brand_impersonation import BrandImpersonation
    _registry_list.append(BrandImpersonation)
except ImportError as e:
    logger.warning(f"Could not import BrandImpersonation: {e}")

try:
    from app.attacks.brand_reputation.competitor_mention import CompetitorMentionAttack
    _registry_list.append(CompetitorMentionAttack)
except ImportError as e:
    logger.warning(f"Could not import CompetitorMentionAttack: {e}")

try:
    from app.attacks.brand_reputation.legal_advice import LegalAdviceAttack
    _registry_list.append(LegalAdviceAttack)
except ImportError as e:
    logger.warning(f"Could not import LegalAdviceAttack: {e}")

try:
    from app.attacks.brand_reputation.medical_advice import MedicalAdviceAttack
    _registry_list.append(MedicalAdviceAttack)
except ImportError as e:
    logger.warning(f"Could not import MedicalAdviceAttack: {e}")

try:
    from app.attacks.brand_reputation.misinformation_gen import MisinformationGen
    _registry_list.append(MisinformationGen)
except ImportError as e:
    logger.warning(f"Could not import MisinformationGen: {e}")

try:
    from app.attacks.brand_reputation.sec_violation import SECViolation
    _registry_list.append(SECViolation)
except ImportError as e:
    logger.warning(f"Could not import SECViolation: {e}")

try:
    from app.attacks.business_logic.dangerous_omission import DangerousOmission
    _registry_list.append(DangerousOmission)
except ImportError as e:
    logger.warning(f"Could not import DangerousOmission: {e}")

try:
    from app.attacks.business_logic.factual_grounding_failure import FactualGroundingFailure
    _registry_list.append(FactualGroundingFailure)
except ImportError as e:
    logger.warning(f"Could not import FactualGroundingFailure: {e}")

try:
    from app.attacks.business_logic.out_of_scope_compliance import OutOfScopeCompliance
    _registry_list.append(OutOfScopeCompliance)
except ImportError as e:
    logger.warning(f"Could not import OutOfScopeCompliance: {e}")

try:
    from app.attacks.business_logic.policy_contradiction import PolicyContradiction
    _registry_list.append(PolicyContradiction)
except ImportError as e:
    logger.warning(f"Could not import PolicyContradiction: {e}")

try:
    from app.attacks.cloud_serverless.cloud_storage_enum import CloudStorageEnum
    _registry_list.append(CloudStorageEnum)
except ImportError as e:
    logger.warning(f"Could not import CloudStorageEnum: {e}")

try:
    from app.attacks.cloud_serverless.cold_start_exploit import ColdStartExploit
    _registry_list.append(ColdStartExploit)
except ImportError as e:
    logger.warning(f"Could not import ColdStartExploit: {e}")

try:
    from app.attacks.cloud_serverless.container_escape import ContainerEscapeAttack
    _registry_list.append(ContainerEscapeAttack)
except ImportError as e:
    logger.warning(f"Could not import ContainerEscapeAttack: {e}")

try:
    from app.attacks.cloud_serverless.cross_tenant_leak import CrossTenantLeak
    _registry_list.append(CrossTenantLeak)
except ImportError as e:
    logger.warning(f"Could not import CrossTenantLeak: {e}")

try:
    from app.attacks.cloud_serverless.iam_privesc import IAMPrivEscAttack
    _registry_list.append(IAMPrivEscAttack)
except ImportError as e:
    logger.warning(f"Could not import IAMPrivEscAttack: {e}")

try:
    from app.attacks.cloud_serverless.k8s_rbac_bypass import K8sRBACBypass
    _registry_list.append(K8sRBACBypass)
except ImportError as e:
    logger.warning(f"Could not import K8sRBACBypass: {e}")

try:
    from app.attacks.cloud_serverless.lambda_injection import LambdaInjectionAttack
    _registry_list.append(LambdaInjectionAttack)
except ImportError as e:
    logger.warning(f"Could not import LambdaInjectionAttack: {e}")

try:
    from app.attacks.cloud_serverless.metadata_ssrf import MetadataSSRF
    _registry_list.append(MetadataSSRF)
except ImportError as e:
    logger.warning(f"Could not import MetadataSSRF: {e}")

try:
    from app.attacks.cloud_serverless.s3_misconfig import S3MisconfigAttack
    _registry_list.append(S3MisconfigAttack)
except ImportError as e:
    logger.warning(f"Could not import S3MisconfigAttack: {e}")

try:
    from app.attacks.cloud_serverless.secrets_manager_abuse import SecretsManagerAbuse
    _registry_list.append(SecretsManagerAbuse)
except ImportError as e:
    logger.warning(f"Could not import SecretsManagerAbuse: {e}")

try:
    from app.attacks.cross_session.context_contamination import ContextContamination
    _registry_list.append(ContextContamination)
except ImportError as e:
    logger.warning(f"Could not import ContextContamination: {e}")

try:
    from app.attacks.cross_session.shared_memory_poisoning import SharedMemoryPoisoning
    _registry_list.append(SharedMemoryPoisoning)
except ImportError as e:
    logger.warning(f"Could not import SharedMemoryPoisoning: {e}")

try:
    from app.attacks.cross_session.vector_db_isolation import VectorDBIsolation
    _registry_list.append(VectorDBIsolation)
except ImportError as e:
    logger.warning(f"Could not import VectorDBIsolation: {e}")

try:
    from app.attacks.identity_auth.api_key_bruteforce import APIKeyBruteforce
    _registry_list.append(APIKeyBruteforce)
except ImportError as e:
    logger.warning(f"Could not import APIKeyBruteforce: {e}")

try:
    from app.attacks.identity_auth.mfa_bypass import MFABypass
    _registry_list.append(MFABypass)
except ImportError as e:
    logger.warning(f"Could not import MFABypass: {e}")

try:
    from app.attacks.identity_auth.oauth_hijack import OAuthHijack
    _registry_list.append(OAuthHijack)
except ImportError as e:
    logger.warning(f"Could not import OAuthHijack: {e}")

try:
    from app.attacks.identity_auth.privesc_via_prompt import PrivEscViaPrompt
    _registry_list.append(PrivEscViaPrompt)
except ImportError as e:
    logger.warning(f"Could not import PrivEscViaPrompt: {e}")

try:
    from app.attacks.identity_auth.rbac_bypass import RBACBypassViaPrompt
    _registry_list.append(RBACBypassViaPrompt)
except ImportError as e:
    logger.warning(f"Could not import RBACBypassViaPrompt: {e}")

try:
    from app.attacks.identity_auth.service_account_takeover import ServiceAccountTakeover
    _registry_list.append(ServiceAccountTakeover)
except ImportError as e:
    logger.warning(f"Could not import ServiceAccountTakeover: {e}")

try:
    from app.attacks.identity_auth.session_fixation import SessionFixation
    _registry_list.append(SessionFixation)
except ImportError as e:
    logger.warning(f"Could not import SessionFixation: {e}")

try:
    from app.attacks.identity_auth.sso_abuse import SSOAbuse
    _registry_list.append(SSOAbuse)
except ImportError as e:
    logger.warning(f"Could not import SSOAbuse: {e}")

try:
    from app.attacks.identity_auth.token_replay import TokenReplay
    _registry_list.append(TokenReplay)
except ImportError as e:
    logger.warning(f"Could not import TokenReplay: {e}")

try:
    from app.attacks.infostealer.ai_malware_detect import AIMalwareDetect
    _registry_list.append(AIMalwareDetect)
except ImportError as e:
    logger.warning(f"Could not import AIMalwareDetect: {e}")

try:
    from app.attacks.infostealer.c2_via_llm import C2ViaLLM
    _registry_list.append(C2ViaLLM)
except ImportError as e:
    logger.warning(f"Could not import C2ViaLLM: {e}")

try:
    from app.attacks.infostealer.credential_harvesting import CredentialHarvesting
    _registry_list.append(CredentialHarvesting)
except ImportError as e:
    logger.warning(f"Could not import CredentialHarvesting: {e}")

try:
    from app.attacks.infostealer.data_exfil_output import DataExfilOutput
    _registry_list.append(DataExfilOutput)
except ImportError as e:
    logger.warning(f"Could not import DataExfilOutput: {e}")

try:
    from app.attacks.infostealer.keylogger_prompt import KeyloggerPrompt
    _registry_list.append(KeyloggerPrompt)
except ImportError as e:
    logger.warning(f"Could not import KeyloggerPrompt: {e}")

try:
    from app.attacks.infostealer.polymorphic_codegen import PolymorphicCodegen
    _registry_list.append(PolymorphicCodegen)
except ImportError as e:
    logger.warning(f"Could not import PolymorphicCodegen: {e}")

try:
    from app.attacks.infostealer.ransomware_sim import RansomwareSim
    _registry_list.append(RansomwareSim)
except ImportError as e:
    logger.warning(f"Could not import RansomwareSim: {e}")

try:
    from app.attacks.infostealer.steganography import SteganographyAttack
    _registry_list.append(SteganographyAttack)
except ImportError as e:
    logger.warning(f"Could not import SteganographyAttack: {e}")

try:
    from app.attacks.mitre_agentic.agent_to_agent_injection import AgentToAgentInjection
    _registry_list.append(AgentToAgentInjection)
except ImportError as e:
    logger.warning(f"Could not import AgentToAgentInjection: {e}")

try:
    from app.attacks.mitre_agentic.autonomous_goal_drift import AutonomousGoalDrift
    _registry_list.append(AutonomousGoalDrift)
except ImportError as e:
    logger.warning(f"Could not import AutonomousGoalDrift: {e}")

try:
    from app.attacks.mitre_agentic.config_modification import ConfigModificationAttack
    _registry_list.append(ConfigModificationAttack)
except ImportError as e:
    logger.warning(f"Could not import ConfigModificationAttack: {e}")

try:
    from app.attacks.mitre_agentic.context_poisoning import ContextPoisoningAttack
    _registry_list.append(ContextPoisoningAttack)
except ImportError as e:
    logger.warning(f"Could not import ContextPoisoningAttack: {e}")

try:
    from app.attacks.mitre_agentic.goal_hijacking import GoalHijackingAttack
    _registry_list.append(GoalHijackingAttack)
except ImportError as e:
    logger.warning(f"Could not import GoalHijackingAttack: {e}")

try:
    from app.attacks.mitre_agentic.memory_poisoning import MemoryPoisoningAttack
    _registry_list.append(MemoryPoisoningAttack)
except ImportError as e:
    logger.warning(f"Could not import MemoryPoisoningAttack: {e}")

try:
    from app.attacks.mitre_agentic.multi_step_chain import MultiStepChainAttack
    _registry_list.append(MultiStepChainAttack)
except ImportError as e:
    logger.warning(f"Could not import MultiStepChainAttack: {e}")

try:
    from app.attacks.mitre_agentic.observation_forging import ObservationForgingAttack
    _registry_list.append(ObservationForgingAttack)
except ImportError as e:
    logger.warning(f"Could not import ObservationForgingAttack: {e}")

try:
    from app.attacks.mitre_agentic.oversight_bypass import OversightBypassAttack
    _registry_list.append(OversightBypassAttack)
except ImportError as e:
    logger.warning(f"Could not import OversightBypassAttack: {e}")

try:
    from app.attacks.mitre_agentic.plan_manipulation import PlanManipulationAttack
    _registry_list.append(PlanManipulationAttack)
except ImportError as e:
    logger.warning(f"Could not import PlanManipulationAttack: {e}")

try:
    from app.attacks.mitre_agentic.reflection_hijack import ReflectionHijackAttack
    _registry_list.append(ReflectionHijackAttack)
except ImportError as e:
    logger.warning(f"Could not import ReflectionHijackAttack: {e}")

try:
    from app.attacks.mitre_agentic.sandbox_escape import SandboxEscapeAttack
    _registry_list.append(SandboxEscapeAttack)
except ImportError as e:
    logger.warning(f"Could not import SandboxEscapeAttack: {e}")

try:
    from app.attacks.mitre_agentic.thread_manipulation import ThreadManipulationAttack
    _registry_list.append(ThreadManipulationAttack)
except ImportError as e:
    logger.warning(f"Could not import ThreadManipulationAttack: {e}")

try:
    from app.attacks.mitre_agentic.tool_injection import ToolInjectionAttack
    _registry_list.append(ToolInjectionAttack)
except ImportError as e:
    logger.warning(f"Could not import ToolInjectionAttack: {e}")

try:
    from app.attacks.multimodal.adversarial_pixel import AdversarialPixel
    _registry_list.append(AdversarialPixel)
except ImportError as e:
    logger.warning(f"Could not import AdversarialPixel: {e}")

try:
    from app.attacks.multimodal.audio_ultrasonic import AudioUltrasonicAttack
    _registry_list.append(AudioUltrasonicAttack)
except ImportError as e:
    logger.warning(f"Could not import AudioUltrasonicAttack: {e}")

try:
    from app.attacks.multimodal.cross_modal import CrossModalAttack
    _registry_list.append(CrossModalAttack)
except ImportError as e:
    logger.warning(f"Could not import CrossModalAttack: {e}")

try:
    from app.attacks.multimodal.doc_hidden_text import DocumentHiddenText
    _registry_list.append(DocumentHiddenText)
except ImportError as e:
    logger.warning(f"Could not import DocumentHiddenText: {e}")

try:
    from app.attacks.multimodal.qr_code_injection import QRCodeInjection
    _registry_list.append(QRCodeInjection)
except ImportError as e:
    logger.warning(f"Could not import QRCodeInjection: {e}")

try:
    from app.attacks.multimodal.video_frame_injection import VideoFrameInjection
    _registry_list.append(VideoFrameInjection)
except ImportError as e:
    logger.warning(f"Could not import VideoFrameInjection: {e}")

try:
    from app.attacks.multimodal.voice_clone import VoiceCloneAttack
    _registry_list.append(VoiceCloneAttack)
except ImportError as e:
    logger.warning(f"Could not import VoiceCloneAttack: {e}")

try:
    from app.attacks.nation_state.apt1_comment_crew import APT1CommentCrew
    _registry_list.append(APT1CommentCrew)
except ImportError as e:
    logger.warning(f"Could not import APT1CommentCrew: {e}")

try:
    from app.attacks.nation_state.apt28_fancy_bear import APT28FancyBear
    _registry_list.append(APT28FancyBear)
except ImportError as e:
    logger.warning(f"Could not import APT28FancyBear: {e}")

try:
    from app.attacks.nation_state.charming_kitten import CharmingKittenSim
    _registry_list.append(CharmingKittenSim)
except ImportError as e:
    logger.warning(f"Could not import CharmingKittenSim: {e}")

try:
    from app.attacks.nation_state.darkside_ransomware import DarksideRansomwareSim
    _registry_list.append(DarksideRansomwareSim)
except ImportError as e:
    logger.warning(f"Could not import DarksideRansomwareSim: {e}")

try:
    from app.attacks.nation_state.lazarus_group import LazarusGroupSim
    _registry_list.append(LazarusGroupSim)
except ImportError as e:
    logger.warning(f"Could not import LazarusGroupSim: {e}")

try:
    from app.attacks.nation_state.midnight_blizzard import MidnightBlizzardSim
    _registry_list.append(MidnightBlizzardSim)
except ImportError as e:
    logger.warning(f"Could not import MidnightBlizzardSim: {e}")

try:
    from app.attacks.nation_state.sandworm_ai import SandwormAI
    _registry_list.append(SandwormAI)
except ImportError as e:
    logger.warning(f"Could not import SandwormAI: {e}")

try:
    from app.attacks.nation_state.scattered_spider import ScatteredSpiderSim
    _registry_list.append(ScatteredSpiderSim)
except ImportError as e:
    logger.warning(f"Could not import ScatteredSpiderSim: {e}")

try:
    from app.attacks.nation_state.volt_typhoon import VoltTyphoonSim
    _registry_list.append(VoltTyphoonSim)
except ImportError as e:
    logger.warning(f"Could not import VoltTyphoonSim: {e}")

try:
    from app.attacks.owasp_llm.llm01_multimodal_injection import LLM01MultimodalInjection
    _registry_list.append(LLM01MultimodalInjection)
except ImportError as e:
    logger.warning(f"Could not import LLM01MultimodalInjection: {e}")

try:
    from app.attacks.owasp_llm.llm01_virtual_prompt import LLM01VirtualPromptInjection
    _registry_list.append(LLM01VirtualPromptInjection)
except ImportError as e:
    logger.warning(f"Could not import LLM01VirtualPromptInjection: {e}")

try:
    from app.attacks.owasp_llm.llm02_sensitive_info import LLM02SensitiveInfoDisclosure
    _registry_list.append(LLM02SensitiveInfoDisclosure)
except ImportError as e:
    logger.warning(f"Could not import LLM02SensitiveInfoDisclosure: {e}")

try:
    from app.attacks.owasp_llm.llm03_dependency_confusion import LLM03DependencyConfusion
    _registry_list.append(LLM03DependencyConfusion)
except ImportError as e:
    logger.warning(f"Could not import LLM03DependencyConfusion: {e}")

try:
    from app.attacks.owasp_llm.llm03_model_tampering import LLM03ModelTampering
    _registry_list.append(LLM03ModelTampering)
except ImportError as e:
    logger.warning(f"Could not import LLM03ModelTampering: {e}")

try:
    from app.attacks.owasp_llm.llm03_supply_chain import LLM03SupplyChain
    _registry_list.append(LLM03SupplyChain)
except ImportError as e:
    logger.warning(f"Could not import LLM03SupplyChain: {e}")

try:
    from app.attacks.owasp_llm.llm04_feedback_poisoning import LLM04FeedbackPoisoning
    _registry_list.append(LLM04FeedbackPoisoning)
except ImportError as e:
    logger.warning(f"Could not import LLM04FeedbackPoisoning: {e}")

try:
    from app.attacks.owasp_llm.llm05_output_handling import LLM05OutputHandling
    _registry_list.append(LLM05OutputHandling)
except ImportError as e:
    logger.warning(f"Could not import LLM05OutputHandling: {e}")

try:
    from app.attacks.owasp_llm.llm06_autonomous_action import LLM06AutonomousAction
    _registry_list.append(LLM06AutonomousAction)
except ImportError as e:
    logger.warning(f"Could not import LLM06AutonomousAction: {e}")

try:
    from app.attacks.owasp_llm.llm06_tool_abuse import LLM06ToolAbuse
    _registry_list.append(LLM06ToolAbuse)
except ImportError as e:
    logger.warning(f"Could not import LLM06ToolAbuse: {e}")

try:
    from app.attacks.owasp_llm.llm07_boundary_test import LLM07BoundaryTest
    _registry_list.append(LLM07BoundaryTest)
except ImportError as e:
    logger.warning(f"Could not import LLM07BoundaryTest: {e}")

try:
    from app.attacks.owasp_llm.llm07_system_prompt_leak import LLM07SystemPromptLeak
    _registry_list.append(LLM07SystemPromptLeak)
except ImportError as e:
    logger.warning(f"Could not import LLM07SystemPromptLeak: {e}")

try:
    from app.attacks.owasp_llm.llm08_embedding_inversion import LLM08EmbeddingInversion
    _registry_list.append(LLM08EmbeddingInversion)
except ImportError as e:
    logger.warning(f"Could not import LLM08EmbeddingInversion: {e}")

try:
    from app.attacks.owasp_llm.llm08_semantic_bypass import LLM08SemanticBypass
    _registry_list.append(LLM08SemanticBypass)
except ImportError as e:
    logger.warning(f"Could not import LLM08SemanticBypass: {e}")

try:
    from app.attacks.owasp_llm.llm08_vector_attack import LLM08VectorAttack
    _registry_list.append(LLM08VectorAttack)
except ImportError as e:
    logger.warning(f"Could not import LLM08VectorAttack: {e}")

try:
    from app.attacks.owasp_llm.llm09_false_authority import LLM09FalseAuthority
    _registry_list.append(LLM09FalseAuthority)
except ImportError as e:
    logger.warning(f"Could not import LLM09FalseAuthority: {e}")

try:
    from app.attacks.physical_ai.actuator_injection import ActuatorInjection
    _registry_list.append(ActuatorInjection)
except ImportError as e:
    logger.warning(f"Could not import ActuatorInjection: {e}")

try:
    from app.attacks.physical_ai.digital_twin_attack import DigitalTwinAttack
    _registry_list.append(DigitalTwinAttack)
except ImportError as e:
    logger.warning(f"Could not import DigitalTwinAttack: {e}")

try:
    from app.attacks.physical_ai.federated_poisoning import FederatedPoisoning
    _registry_list.append(FederatedPoisoning)
except ImportError as e:
    logger.warning(f"Could not import FederatedPoisoning: {e}")

try:
    from app.attacks.physical_ai.realtime_adversarial import RealtimeAdversarial
    _registry_list.append(RealtimeAdversarial)
except ImportError as e:
    logger.warning(f"Could not import RealtimeAdversarial: {e}")

try:
    from app.attacks.physical_ai.sim_to_real_gap import SimToRealGap
    _registry_list.append(SimToRealGap)
except ImportError as e:
    logger.warning(f"Could not import SimToRealGap: {e}")

try:
    from app.attacks.rag_specific.context_window_overflow import RAGContextWindowOverflow
    _registry_list.append(RAGContextWindowOverflow)
except ImportError as e:
    logger.warning(f"Could not import RAGContextWindowOverflow: {e}")

try:
    from app.attacks.rag_specific.cross_context_injection import CrossContextInjection
    _registry_list.append(CrossContextInjection)
except ImportError as e:
    logger.warning(f"Could not import CrossContextInjection: {e}")

try:
    from app.attacks.rag_specific.raget_eval import RAGETEval
    _registry_list.append(RAGETEval)
except ImportError as e:
    logger.warning(f"Could not import RAGETEval: {e}")

try:
    from app.attacks.rag_specific.retrieval_manipulation import RetrievalManipulation
    _registry_list.append(RetrievalManipulation)
except ImportError as e:
    logger.warning(f"Could not import RetrievalManipulation: {e}")

try:
    from app.attacks.reasoning_dos.reflection_poisoning import ReflectionPoisoning
    _registry_list.append(ReflectionPoisoning)
except ImportError as e:
    logger.warning(f"Could not import ReflectionPoisoning: {e}")

try:
    from app.attacks.responsible_ai.age_bias import AgeBiasAttack
    _registry_list.append(AgeBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import AgeBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.disability_bias import DisabilityBiasAttack
    _registry_list.append(DisabilityBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import DisabilityBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.explainability_test import ExplainabilityTest
    _registry_list.append(ExplainabilityTest)
except ImportError as e:
    logger.warning(f"Could not import ExplainabilityTest: {e}")

try:
    from app.attacks.responsible_ai.fairness_metrics import FairnessMetricsTest
    _registry_list.append(FairnessMetricsTest)
except ImportError as e:
    logger.warning(f"Could not import FairnessMetricsTest: {e}")

try:
    from app.attacks.responsible_ai.geographic_bias import GeographicBiasAttack
    _registry_list.append(GeographicBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import GeographicBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.inclusiveness_test import InclusivenessTest
    _registry_list.append(InclusivenessTest)
except ImportError as e:
    logger.warning(f"Could not import InclusivenessTest: {e}")

try:
    from app.attacks.responsible_ai.intersectional_bias import IntersectionalBiasAttack
    _registry_list.append(IntersectionalBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import IntersectionalBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.occupational_stereotyping import OccupationalStereotyping
    _registry_list.append(OccupationalStereotyping)
except ImportError as e:
    logger.warning(f"Could not import OccupationalStereotyping: {e}")

try:
    from app.attacks.responsible_ai.political_bias import PoliticalBiasAttack
    _registry_list.append(PoliticalBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import PoliticalBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.religious_bias import ReligiousBiasAttack
    _registry_list.append(ReligiousBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import ReligiousBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.socioeconomic_bias import SocioeconomicBiasAttack
    _registry_list.append(SocioeconomicBiasAttack)
except ImportError as e:
    logger.warning(f"Could not import SocioeconomicBiasAttack: {e}")

try:
    from app.attacks.responsible_ai.transparency_test import TransparencyTest
    _registry_list.append(TransparencyTest)
except ImportError as e:
    logger.warning(f"Could not import TransparencyTest: {e}")

try:
    from app.attacks.social_engineering.commitment_consistency import CommitmentConsistency
    _registry_list.append(CommitmentConsistency)
except ImportError as e:
    logger.warning(f"Could not import CommitmentConsistency: {e}")

try:
    from app.attacks.social_engineering.liking_exploitation import LikingExploitation
    _registry_list.append(LikingExploitation)
except ImportError as e:
    logger.warning(f"Could not import LikingExploitation: {e}")

try:
    from app.attacks.social_engineering.pretexting import PretextingAttack
    _registry_list.append(PretextingAttack)
except ImportError as e:
    logger.warning(f"Could not import PretextingAttack: {e}")

try:
    from app.attacks.social_engineering.reciprocity_exploit import ReciprocityExploit
    _registry_list.append(ReciprocityExploit)
except ImportError as e:
    logger.warning(f"Could not import ReciprocityExploit: {e}")

try:
    from app.attacks.social_engineering.scarcity_framing import ScarcityFraming
    _registry_list.append(ScarcityFraming)
except ImportError as e:
    logger.warning(f"Could not import ScarcityFraming: {e}")

try:
    from app.attacks.social_engineering.social_proof_abuse import SocialProofAbuse
    _registry_list.append(SocialProofAbuse)
except ImportError as e:
    logger.warning(f"Could not import SocialProofAbuse: {e}")

try:
    from app.attacks.stress_performance.concurrent_session_flood import ConcurrentSessionFlood
    _registry_list.append(ConcurrentSessionFlood)
except ImportError as e:
    logger.warning(f"Could not import ConcurrentSessionFlood: {e}")

try:
    from app.attacks.stress_performance.memory_pressure import MemoryPressureAttack
    _registry_list.append(MemoryPressureAttack)
except ImportError as e:
    logger.warning(f"Could not import MemoryPressureAttack: {e}")

try:
    from app.attacks.stress_performance.resource_exhaust import ResourceExhaustAttack
    _registry_list.append(ResourceExhaustAttack)
except ImportError as e:
    logger.warning(f"Could not import ResourceExhaustAttack: {e}")

try:
    from app.attacks.supply_chain_sbom.build_tamper import BuildTamperAttack
    _registry_list.append(BuildTamperAttack)
except ImportError as e:
    logger.warning(f"Could not import BuildTamperAttack: {e}")

try:
    from app.attacks.supply_chain_sbom.mcp_rug_pull_version import MCPRugPullVersion
    _registry_list.append(MCPRugPullVersion)
except ImportError as e:
    logger.warning(f"Could not import MCPRugPullVersion: {e}")

try:
    from app.attacks.supply_chain_sbom.npm_mcp_backdoor import NPMMCPBackdoor
    _registry_list.append(NPMMCPBackdoor)
except ImportError as e:
    logger.warning(f"Could not import NPMMCPBackdoor: {e}")

try:
    from app.attacks.supply_chain_sbom.poisoned_dep import PoisonedDepAttack
    _registry_list.append(PoisonedDepAttack)
except ImportError as e:
    logger.warning(f"Could not import PoisonedDepAttack: {e}")

try:
    from app.attacks.supply_chain_sbom.slopsquatting_detect import SlopsquattingDetect
    _registry_list.append(SlopsquattingDetect)
except ImportError as e:
    logger.warning(f"Could not import SlopsquattingDetect: {e}")

try:
    from app.attacks.supply_chain_sbom.weight_tamper import WeightTamperAttack
    _registry_list.append(WeightTamperAttack)
except ImportError as e:
    logger.warning(f"Could not import WeightTamperAttack: {e}")

try:
    from app.attacks.web_attacks.clickjacking import ClickjackingViaAI
    _registry_list.append(ClickjackingViaAI)
except ImportError as e:
    logger.warning(f"Could not import ClickjackingViaAI: {e}")

try:
    from app.attacks.web_attacks.cors_abuse import CORSAbuseViaAI
    _registry_list.append(CORSAbuseViaAI)
except ImportError as e:
    logger.warning(f"Could not import CORSAbuseViaAI: {e}")

try:
    from app.attacks.web_attacks.csrf import CSRFViaAI
    _registry_list.append(CSRFViaAI)
except ImportError as e:
    logger.warning(f"Could not import CSRFViaAI: {e}")

try:
    from app.attacks.web_attacks.http_header_injection import HTTPHeaderInjection
    _registry_list.append(HTTPHeaderInjection)
except ImportError as e:
    logger.warning(f"Could not import HTTPHeaderInjection: {e}")

try:
    from app.attacks.web_attacks.idor import IDORViaPrompt
    _registry_list.append(IDORViaPrompt)
except ImportError as e:
    logger.warning(f"Could not import IDORViaPrompt: {e}")

try:
    from app.attacks.web_attacks.mass_assignment import MassAssignmentViaPrompt
    _registry_list.append(MassAssignmentViaPrompt)
except ImportError as e:
    logger.warning(f"Could not import MassAssignmentViaPrompt: {e}")

try:
    from app.attacks.web_attacks.nosql_injection import NoSQLInjectionViaPrompt
    _registry_list.append(NoSQLInjectionViaPrompt)
except ImportError as e:
    logger.warning(f"Could not import NoSQLInjectionViaPrompt: {e}")

try:
    from app.attacks.web_attacks.open_redirect import OpenRedirectViaAI
    _registry_list.append(OpenRedirectViaAI)
except ImportError as e:
    logger.warning(f"Could not import OpenRedirectViaAI: {e}")

try:
    from app.attacks.web_attacks.path_traversal import PathTraversalViaPrompt
    _registry_list.append(PathTraversalViaPrompt)
except ImportError as e:
    logger.warning(f"Could not import PathTraversalViaPrompt: {e}")

try:
    from app.attacks.web_attacks.xxe import XXEViaOutput
    _registry_list.append(XXEViaOutput)
except ImportError as e:
    logger.warning(f"Could not import XXEViaOutput: {e}")

try:
    from app.attacks.zero_day.cve_prediction import CVEPrediction
    _registry_list.append(CVEPrediction)
except ImportError as e:
    logger.warning(f"Could not import CVEPrediction: {e}")

try:
    from app.attacks.zero_day.exploit_chain_sim import ExploitChainSim
    _registry_list.append(ExploitChainSim)
except ImportError as e:
    logger.warning(f"Could not import ExploitChainSim: {e}")

try:
    from app.attacks.zero_day.novel_attack_gen import NovelAttackGen
    _registry_list.append(NovelAttackGen)
except ImportError as e:
    logger.warning(f"Could not import NovelAttackGen: {e}")

try:
    from app.attacks.zero_day.patch_gap_analysis import PatchGapAnalysis
    _registry_list.append(PatchGapAnalysis)
except ImportError as e:
    logger.warning(f"Could not import PatchGapAnalysis: {e}")

try:
    from app.attacks.zero_day.threat_intel_correlation import ThreatIntelCorrelation
    _registry_list.append(ThreatIntelCorrelation)
except ImportError as e:
    logger.warning(f"Could not import ThreatIntelCorrelation: {e}")

try:
    from app.attacks.zero_day.unknown_vuln_fuzzing import UnknownVulnFuzzing
    _registry_list.append(UnknownVulnFuzzing)
except ImportError as e:
    logger.warning(f"Could not import UnknownVulnFuzzing: {e}")

try:
    from app.attacks.zero_day.zeroday_pattern_match import ZeroDayPatternMatch
    _registry_list.append(ZeroDayPatternMatch)
except ImportError as e:
    logger.warning(f"Could not import ZeroDayPatternMatch: {e}")

# ── REGISTRY ──────────────────────────────────────────────────────────────────

class AttackRegistry:
    def __init__(self):
        self._attacks: dict[str, type[BaseAttack]] = {}
        self._load_all_attacks()
        self._load_plugins()

    def register(self, attack_cls: type[BaseAttack]) -> None:
        self._attacks[attack_cls.attack_id] = attack_cls

    def _load_all_attacks(self) -> None:
        """Register all built-in attacks."""
        for cls in _registry_list:
            self.register(cls)
        logger.info(f"Loaded {len(self._attacks)} built-in attacks")

    def _load_plugins(self) -> None:
        """Auto-discover external attack plugins via entry_points."""
        try:
            for ep in importlib.metadata.entry_points(group="agentred.plugins"):
                try:
                    plugin_cls = ep.load()
                    for attack_cls in plugin_cls.get_attacks():
                        self.register(attack_cls)
                    logger.info(f"Plugin loaded: {plugin_cls.plugin_name}")
                except Exception as e:
                    logger.error(f"Plugin load failed {ep.name}: {e}")
        except Exception:
            pass  # No plugins installed

    def get(self, attack_id: str) -> Optional[type[BaseAttack]]:
        return self._attacks.get(attack_id)

    def get_all(self) -> list[type[BaseAttack]]:
        return list(self._attacks.values())

    def get_by_category(self, category: str) -> list[type[BaseAttack]]:
        return [cls for cls in self._attacks.values() if cls.category == category]

    def get_by_severity(self, severity: str) -> list[type[BaseAttack]]:
        return [cls for cls in self._attacks.values() if cls.severity == severity]

    def get_for_scan_mode(self, mode: str) -> list[type[BaseAttack]]:
        """Return attacks appropriate for the given scan mode."""
        all_attacks = self.get_all()
        if mode == "quick":
            # Top 50 — critical and high severity only
            priority = [cls for cls in all_attacks if cls.severity in ("critical", "high")]
            return priority[:50]
        elif mode == "standard":
            # 200 attacks — critical + high + medium
            priority = [cls for cls in all_attacks if cls.severity in ("critical", "high", "medium")]
            return priority[:200]
        elif mode == "deep":
            return all_attacks  # All attacks
        elif mode == "compliance":
            # Focus on OWASP LLM, responsible_ai, privacy
            compliance_cats = ["owasp_llm", "owasp_agentic", "responsible_ai", "ml_privacy"]
            return [cls for cls in all_attacks if cls.category in compliance_cats]
        return all_attacks

    def get_random_sample(self, limit: int = 5) -> list[type[BaseAttack]]:
        import random
        all_attacks = self.get_all()
        return random.sample(all_attacks, min(limit, len(all_attacks)))

    def list_categories(self) -> list[str]:
        return sorted(list(set(cls.category for cls in self._attacks.values())))

    def count(self) -> int:
        return len(self._attacks)

    def to_dict(self) -> list[dict]:
        return [
            {
                "attack_id": cls.attack_id,
                "name": cls.name,
                "category": cls.category,
                "severity": cls.severity,
                "description": cls.description,
                "framework_mapping": cls.framework_mapping,
            }
            for cls in self._attacks.values()
        ]


# Singleton registry instance
attack_registry = AttackRegistry()
