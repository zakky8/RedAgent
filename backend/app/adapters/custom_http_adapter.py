"""Generic custom HTTP/REST API adapter for AgentRed."""
import time
import httpx
import json
from typing import Optional, Dict, Any

from .base import BaseAdapter, AdapterResponse


class CustomHTTPAdapter(BaseAdapter):
    """Generic adapter for any custom HTTP/REST API endpoint."""

    adapter_name = "custom_http"

    def __init__(self, config: dict):
        """Initialize custom HTTP adapter.

        Config:
            endpoint: Base API endpoint URL (required)
            method: HTTP method (default: POST)
            headers: Custom headers dict
            auth_type: Auth type (bearer, basic, api_key, custom)
            auth_value: Auth value/token
            request_format: Format of request (json, form, text)
            response_path: JSONPath to extract response (e.g., "data.output")
            timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(config)
        self.endpoint = config.get("endpoint")
        self.method = config.get("method", "POST").upper()
        self.headers = config.get("headers", {})
        self.auth_type = config.get("auth_type")
        self.auth_value = config.get("auth_value")
        self.request_format = config.get("request_format", "json")
        self.response_path = config.get("response_path", "")
        self.timeout = config.get("timeout", 30)
        self.model = config.get("model_name", "custom-api")

        if not self.endpoint:
            raise ValueError("Endpoint URL is required")

    def _get_headers(self) -> Dict[str, str]:
        """Build headers with authentication."""
        headers = dict(self.headers)

        # Add authentication if configured
        if self.auth_type and self.auth_value:
            if self.auth_type.lower() == "bearer":
                headers["Authorization"] = f"Bearer {self.auth_value}"
            elif self.auth_type.lower() == "basic":
                import base64

                encoded = base64.b64encode(
                    self.auth_value.encode()
                ).decode()
                headers["Authorization"] = f"Basic {encoded}"
            elif self.auth_type.lower() == "api_key":
                headers["X-API-Key"] = self.auth_value
            elif self.auth_type.lower() == "custom":
                headers["Authorization"] = self.auth_value

        # Set content type if not already set
        if "Content-Type" not in headers:
            if self.request_format == "json":
                headers["Content-Type"] = "application/json"
            elif self.request_format == "form":
                headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                headers["Content-Type"] = "text/plain"

        return headers

    def _extract_response(self, data: Any, path: str = "") -> str:
        """Extract response using JSONPath."""
        if isinstance(data, str):
            return data

        if not path:
            # Return as-is if no path specified
            return json.dumps(data) if isinstance(data, dict) else str(data)

        # Simple JSONPath implementation
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                break

        return str(current) if current is not None else ""

    async def send(self, prompt: str, system: str = None, **kwargs) -> AdapterResponse:
        """Send prompt to custom HTTP endpoint.

        Args:
            prompt: User prompt/input
            system: System context
            **kwargs: Additional parameters

        Returns:
            AdapterResponse: Standardized response
        """
        start = time.perf_counter()

        # Build request payload
        payload = {
            "prompt": prompt,
            "input": prompt,
        }

        if system:
            payload["system"] = system

        # Add custom parameters
        for key, value in kwargs.items():
            payload[key] = value

        try:
            headers = self._get_headers()

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if self.method == "POST":
                    if self.request_format == "json":
                        response = await client.post(
                            self.endpoint,
                            json=payload,
                            headers=headers,
                        )
                    elif self.request_format == "form":
                        response = await client.post(
                            self.endpoint,
                            data=payload,
                            headers=headers,
                        )
                    else:
                        response = await client.post(
                            self.endpoint,
                            content=str(prompt),
                            headers=headers,
                        )

                elif self.method == "GET":
                    response = await client.get(
                        self.endpoint,
                        params=payload,
                        headers=headers,
                    )

                elif self.method == "PUT":
                    response = await client.put(
                        self.endpoint,
                        json=payload,
                        headers=headers,
                    )

                elif self.method == "PATCH":
                    response = await client.patch(
                        self.endpoint,
                        json=payload,
                        headers=headers,
                    )

                else:
                    raise ValueError(f"Unsupported HTTP method: {self.method}")

                response.raise_for_status()

                # Try to parse as JSON first
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = response.text

                # Extract response
                output = self._extract_response(data, self.response_path)

                return AdapterResponse(
                    response=output,
                    tokens_used=0,
                    model=self.model,
                    latency_ms=self._timing(start),
                    raw={"raw_response": data},
                )

        except httpx.HTTPStatusError as e:
            raise Exception(
                f"Custom HTTP API error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise Exception(f"Custom HTTP adapter error: {str(e)}")

    async def health_check(self) -> bool:
        """Check custom HTTP endpoint connectivity."""
        try:
            headers = self._get_headers()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.endpoint,
                    headers=headers,
                )
                return response.status_code < 500
        except Exception:
            return False
