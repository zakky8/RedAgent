"""
Insecure AI Output Handling Attacks Module

This module contains attack simulations for vulnerabilities where AI-generated
output becomes an attack vector for downstream systems.
"""

try:
    from .xss_via_llm import XSSViaLLM
except ImportError as e:
    print(f"Warning: Could not import XSSViaLLM: {e}")
    XSSViaLLM = None

try:
    from .prompt_injection_output import PromptInjectionOutput
except ImportError as e:
    print(f"Warning: Could not import PromptInjectionOutput: {e}")
    PromptInjectionOutput = None

try:
    from .sql_injection_output import SQLInjectionOutput
except ImportError as e:
    print(f"Warning: Could not import SQLInjectionOutput: {e}")
    SQLInjectionOutput = None

try:
    from .command_injection_output import CommandInjectionOutput
except ImportError as e:
    print(f"Warning: Could not import CommandInjectionOutput: {e}")
    CommandInjectionOutput = None

try:
    from .ssrf_payload_output import SSRFPayloadOutput
except ImportError as e:
    print(f"Warning: Could not import SSRFPayloadOutput: {e}")
    SSRFPayloadOutput = None

try:
    from .deserialization_output import DeserializationOutput
except ImportError as e:
    print(f"Warning: Could not import DeserializationOutput: {e}")
    DeserializationOutput = None

__all__ = [
    "XSSViaLLM",
    "PromptInjectionOutput",
    "SQLInjectionOutput",
    "CommandInjectionOutput",
    "SSRFPayloadOutput",
    "DeserializationOutput",
]
