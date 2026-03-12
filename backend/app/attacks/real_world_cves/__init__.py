"""
Real-World CVE Attacks Module
Exploits for real disclosed vulnerabilities in AI/ML frameworks and tools
"""
from .cve_langchain_rce import CVELangChainRCE
from .cve_ollama_unauth import CVEOllamaUnauth
from .cve_gradio_upload import CVEGradioUpload
from .cve_mlflow_read import CVEMLflowRead

__all__ = [
    "CVELangChainRCE",
    "CVEOllamaUnauth",
    "CVEGradioUpload",
    "CVEMLflowRead",
]
