from .llm01_direct_injection import LLM01DirectInjection
from .llm01_indirect_injection import LLM01IndirectInjection
from .llm01_rag_injection import LLM01RAGInjection
from .llm01_virtual_prompt import LLM01VirtualPromptInjection
from .llm01_multimodal_injection import LLM01MultimodalInjection
from .llm02_credential_leak import LLM02CredentialLeak
from .llm02_pii_extraction import LLM02PIIExtraction
from .llm02_system_prompt_leak import LLM02SystemPromptLeak
from .llm02_training_data import LLM02TrainingDataExtraction
from .llm02_sensitive_info import LLM02SensitiveInfoDisclosure
from .llm03_supply_chain import LLM03SupplyChain
from .llm03_dependency_confusion import LLM03DependencyConfusion
from .llm03_model_tampering import LLM03ModelTampering
from .llm04_data_poisoning import LLM04DataPoisoning
from .llm04_rag_poisoning import LLM04RAGPoisoning
from .llm04_feedback_poisoning import LLM04FeedbackPoisoning
from .llm05_code_execution import LLM05CodeExecution
from .llm05_xss import LLM05XSSViaOutput
from .llm05_output_handling import LLM05OutputHandling
from .llm06_excessive_agency import LLM06ExcessiveAgency
from .llm06_tool_abuse import LLM06ToolAbuse
from .llm06_autonomous_action import LLM06AutonomousAction
from .llm07_instruction_override import LLM07InstructionOverride
from .llm07_system_prompt_leak import LLM07SystemPromptLeak
from .llm07_boundary_test import LLM07BoundaryTest
from .llm08_vector_attack import LLM08VectorAttack
from .llm08_embedding_inversion import LLM08EmbeddingInversion
from .llm08_semantic_bypass import LLM08SemanticBypass
from .llm09_hallucination import LLM09HallucinationTrigger
from .llm09_misinformation import LLM09Misinformation
from .llm09_false_authority import LLM09FalseAuthority
from .llm10_context_bomb import LLM10ContextBomb
from .llm10_denial_of_wallet import LLM10DenialOfWallet
from .llm10_token_exhaustion import LLM10TokenExhaustion

__all__ = [
    "LLM01DirectInjection",
    "LLM01IndirectInjection",
    "LLM01RAGInjection",
    "LLM01VirtualPromptInjection",
    "LLM01MultimodalInjection",
    "LLM02CredentialLeak",
    "LLM02PIIExtraction",
    "LLM02SystemPromptLeak",
    "LLM02TrainingDataExtraction",
    "LLM02SensitiveInfoDisclosure",
    "LLM03SupplyChain",
    "LLM03DependencyConfusion",
    "LLM03ModelTampering",
    "LLM04DataPoisoning",
    "LLM04RAGPoisoning",
    "LLM04FeedbackPoisoning",
    "LLM05CodeExecution",
    "LLM05XSSViaOutput",
    "LLM05OutputHandling",
    "LLM06ExcessiveAgency",
    "LLM06ToolAbuse",
    "LLM06AutonomousAction",
    "LLM07InstructionOverride",
    "LLM07SystemPromptLeak",
    "LLM07BoundaryTest",
    "LLM08VectorAttack",
    "LLM08EmbeddingInversion",
    "LLM08SemanticBypass",
    "LLM09HallucinationTrigger",
    "LLM09Misinformation",
    "LLM09FalseAuthority",
    "LLM10ContextBomb",
    "LLM10DenialOfWallet",
    "LLM10TokenExhaustion",
]
