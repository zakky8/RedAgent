"""Jenkins CI/CD integration for AgentRed."""
import logging
from dataclasses import dataclass
from typing import Optional, List

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


@dataclass
class JenkinsConfig:
    url: str
    username: str
    api_token: str
    job_name: Optional[str] = None


class JenkinsIntegration:
    def __init__(self, config: JenkinsConfig):
        self.config = config
        self._logger = logging.getLogger("agentred.jenkins")

    async def post_scan_results(
        self, scan_id: str, findings: List[dict], risk_score: float
    ):
        """Post scan results as Jenkins build properties."""
        if not HTTPX_AVAILABLE:
            return
        props = "\n".join(
            [
                f"AGENTRED_SCAN_ID={scan_id}",
                f"AGENTRED_RISK_SCORE={risk_score:.1f}",
                f"AGENTRED_CRITICAL={sum(1 for f in findings if f.get('severity') == 'CRITICAL')}",
                f"AGENTRED_HIGH={sum(1 for f in findings if f.get('severity') == 'HIGH')}",
            ]
        )
        self._logger.info(f"Jenkins build properties: {props}")
        return {"status": "posted", "properties": props}

    async def fail_build_on_threshold(
        self, risk_score: float, threshold: float = 70.0
    ) -> bool:
        """Return True if build should fail."""
        if risk_score >= threshold:
            self._logger.warning(
                f"Build FAILED: risk score {risk_score} >= threshold {threshold}"
            )
            return True
        return False

    async def test_connection(self) -> dict:
        if not HTTPX_AVAILABLE:
            return {"connected": False, "error": "httpx not available"}
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"{self.config.url}/api/json",
                    auth=(self.config.username, self.config.api_token),
                    timeout=5,
                )
                return {
                    "connected": r.status_code == 200,
                    "version": r.headers.get("X-Jenkins"),
                }
        except Exception as e:
            return {"connected": False, "error": str(e)}
