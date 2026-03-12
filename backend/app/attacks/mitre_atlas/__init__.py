"""MITRE ATLAS attack modules."""
from typing import List, Type
from app.attacks.base import BaseAttack
import importlib

attack_classes: List[Type[BaseAttack]] = []

_imports = [
    # Reconnaissance
    ("recon_target_discovery", "MITRETargetDiscovery"),
    ("recon_model_fingerprinting", "MITREModelFingerprinting"),
    ("recon_api_enumeration", "APIEnumeration"),
    ("recon_capability_probing", "CapabilityProbing"),
    # Resource Development
    ("resource_dev_adversarial_craft", "AdversarialPromptCraft"),
    ("resource_dev_attack_infra", "AttackInfrastructure"),
    # Initial Access
    ("initial_access_api_exploit", "MITREAPIExploit"),
    ("initial_access_supply_chain", "SupplyChainCompromise"),
    ("initial_access_phishing_llm", "PhishingLLM"),
    # Execution
    ("execution_tool_execution", "ToolExecutionAttack"),
    ("execution_model_inversion", "ModelInversionExec"),
    # Persistence
    ("persistence_memory_backdoor", "MITREMemoryBackdoor"),
    ("persistence_rag_persistence", "RAGPersistence"),
    ("persistence_sys_prompt_mod", "SystemPromptModification"),
    # Privilege Escalation
    ("priv_escalation_role_confusion", "RoleConfusion"),
    ("priv_escalation_jailbreak", "JailbreakPrivEsc"),
    ("priv_escalation_capability_expansion", "CapabilityExpansion"),
    # Defense Evasion
    ("defense_evasion_encoding", "MITREEncodingEvasion"),
    ("defense_evasion_obfuscation", "ObfuscationEvasion"),
    ("defense_evasion_context_switching", "ContextSwitching"),
    # Credential Access
    ("credential_api_key_extraction", "MITREAPIKeyExtraction"),
    ("cred_access_credential_phishing", "CredentialPhishing"),
    ("cred_access_secret_enumeration", "SecretEnumeration"),
    # Discovery
    ("discovery_model_architecture", "ModelArchitectureDiscovery"),
    ("discovery_data_schema", "DataSchemaDiscovery"),
    # Collection
    ("collection_data_gathering", "MITREDataGathering"),
    ("collection_training_data", "TrainingDataCollection"),
    ("collection_output_harvesting", "OutputHarvesting"),
    # ML Model Theft
    ("ml_weight_extraction", "WeightExtraction"),
    ("ml_architecture_theft", "ArchitectureTheft"),
    # Exfiltration
    ("exfiltration_data_via_output", "MITREDataExfilOutput"),
    ("exfil_covert_channel", "CovertChannelExfil"),
    ("exfil_steganography", "SteganographyExfil"),
    # Impact
    ("impact_model_corruption", "MITREModelCorruption"),
    ("impact_availability_disruption", "AvailabilityDisruption"),
    ("impact_reputation_damage", "ReputationDamage"),
    ("impact_data_integrity", "DataIntegrityAttack"),
]
for mod, cls in _imports:
    try:
        m = importlib.import_module(f"app.attacks.mitre_atlas.{mod}")
        attack_classes.append(getattr(m, cls))
    except Exception:
        pass

__all__ = ["attack_classes"]
