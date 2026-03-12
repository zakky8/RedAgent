"""AgentRed API: MCP (Model Context Protocol) security scanning endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(prefix="/mcp", tags=["mcp"])


class MCPScanRequest(BaseModel):
    """MCP server scan request."""
    server_url: str
    auth_token: Optional[str] = None
    deep_scan: bool = False


class MCPVulnerability(BaseModel):
    """MCP vulnerability."""
    name: str
    severity: str
    cwe: Optional[str] = None
    description: str
    remediation: str


class MCPTool(BaseModel):
    """MCP tool information."""
    name: str
    description: str
    risk_level: str
    requires_auth: bool


@router.post("/scan")
async def scan_mcp_server(
    request: MCPScanRequest,
    bg_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Scan an MCP server for vulnerabilities.

    Tests for:
    - Tool injection attacks
    - Rug pull patterns
    - Permission issues
    - Credential extraction
    - Cross-server injection
    """
    from app.core.mcp_scanner import MCPScanner

    try:
        scanner = MCPScanner()

        # Run scan
        results = await scanner.scan_server(
            request.server_url,
            request.auth_token,
            request.deep_scan,
        )

        return {
            "server_url": request.server_url,
            "vulnerabilities": results.get("vulnerabilities", []),
            "tools": results.get("tools", []),
            "risk_score": results.get("risk_score", 0),
            "timestamp": results.get("timestamp"),
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/scan-repo")
async def scan_mcp_repository(
    repo_url: str,
    branch: str = "main",
    bg_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
):
    """Scan an MCP server repository code for security issues.

    Analyzes:
    - Hardcoded credentials
    - Unsafe dependencies
    - Injection vulnerabilities
    - Rug pull patterns
    - Malware signatures
    """
    from app.core.mcp_scanner import MCPScanner

    try:
        scanner = MCPScanner()

        results = await scanner.scan_repository(repo_url, branch)

        return {
            "repo_url": repo_url,
            "branch": branch,
            "issues": results.get("issues", []),
            "security_score": results.get("security_score", 0),
            "timestamp": results.get("timestamp"),
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tools")
async def list_mcp_tools(
    server_url: str,
    current_user: User = Depends(get_current_user),
):
    """List all tools exposed by an MCP server."""
    from app.core.mcp_scanner import MCPScanner

    try:
        scanner = MCPScanner()
        tools = await scanner.list_tools(server_url)

        return {
            "server_url": server_url,
            "tools": tools,
            "count": len(tools),
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/test-injection")
async def test_mcp_injection(
    server_url: str,
    tool_name: str,
    payload: str,
    current_user: User = Depends(get_current_user),
):
    """Test an MCP tool for prompt injection vulnerabilities."""
    from app.core.mcp_scanner import MCPScanner

    try:
        scanner = MCPScanner()
        result = await scanner.test_injection(server_url, tool_name, payload)

        return {
            "server_url": server_url,
            "tool_name": tool_name,
            "vulnerable": result.get("vulnerable", False),
            "evidence": result.get("evidence"),
            "recommendations": result.get("recommendations", []),
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/status/{scan_id}")
async def get_mcp_scan_status(
    scan_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get MCP scan status."""
    return {
        "id": scan_id,
        "status": "completed",
        "progress": 100,
    }
