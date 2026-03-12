"""
AgentRed Python SDK Client — Main entry point.
pip install agentred
"""
import httpx
from typing import Optional, Dict, Any

from .exceptions import AgentRedError, AuthError, RateLimitError
from .resources.scans import ScansResource
from .resources.targets import TargetsResource
from .resources.reports import ReportsResource
from .resources.compliance import ComplianceResource
from .resources.attacks import AttacksResource


class AgentRedClient:
    """Main AgentRed SDK client for red team operations."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.agentred.io",
        timeout: int = 60
    ):
        """
        Initialize AgentRedClient.

        Args:
            api_key: API key for authentication
            base_url: Base URL for AgentRed API (default: production)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Create HTTP client
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "agentred-sdk/1.0.0"
            },
            timeout=timeout
        )

        # Resource accessors
        self.scans = ScansResource(self)
        self.targets = TargetsResource(self)
        self.reports = ReportsResource(self)
        self.compliance = ComplianceResource(self)
        self.attacks = AttacksResource(self)

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> dict:
        """
        Make HTTP request to AgentRed API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            path: API path (e.g., "/scans")
            json: JSON payload
            params: Query parameters

        Returns:
            JSON response as dict

        Raises:
            AuthError: Invalid API key
            RateLimitError: Rate limit exceeded
            AgentRedError: Other API errors
        """
        url = f"{self.base_url}/api/v1{path}"

        try:
            response = self._client.request(
                method,
                url,
                json=json,
                params=params
            )
        except httpx.TimeoutException as e:
            raise AgentRedError(f"Request timeout: {e}")
        except httpx.NetworkError as e:
            raise AgentRedError(f"Network error: {e}")

        if response.status_code == 401:
            raise AuthError("Invalid API key or authentication failed")
        elif response.status_code == 403:
            raise AuthError("Access denied")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded. Try again later.")
        elif response.status_code == 404:
            raise AgentRedError(f"Not found: {path}")
        elif response.status_code >= 500:
            raise AgentRedError(
                f"Server error {response.status_code}: {response.text}"
            )
        elif response.status_code >= 400:
            raise AgentRedError(
                f"Client error {response.status_code}: {response.text}"
            )

        try:
            return response.json()
        except ValueError as e:
            raise AgentRedError(f"Invalid JSON response: {e}")

    def close(self) -> None:
        """Close HTTP client and release resources."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        return f"<AgentRedClient {self.base_url}>"
