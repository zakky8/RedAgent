"""
Elastic SIEM Integration — index findings in Elasticsearch.
Build Rule 11: Integration failures don't crash the platform.
"""
import logging
import asyncio
from datetime import datetime
from typing import Optional, List
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchException

logger = logging.getLogger(__name__)


class ElasticIntegration:
    """
    Sends AgentRed findings to Elasticsearch for SIEM analysis and long-term storage.

    Configuration:
        cloud_id (str): Elastic Cloud deployment ID (optional, for cloud.elastic.co)
        api_key (str): Elastic API key for authentication
        hosts (list): List of Elasticsearch hosts (e.g. ["localhost:9200"]) (optional)
        username (str): Basic auth username (optional, if not using API key)
        password (str): Basic auth password (optional, if not using API key)
        index_prefix (str): Index name prefix (default: "agentred")
        verify_certs (bool): Verify SSL certificates (default: True)
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 cloud_id: Optional[str] = None,
                 hosts: Optional[List[str]] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 index_prefix: str = "agentred",
                 verify_certs: bool = True,
                 timeout: int = 10):
        """Initialize Elasticsearch integration."""
        self.index_prefix = index_prefix
        self.timeout = timeout
        self.verify_certs = verify_certs
        self.client = None

        # Build ES client
        try:
            if cloud_id and api_key:
                self.client = Elasticsearch(
                    cloud_id=cloud_id,
                    api_key=api_key,
                    request_timeout=timeout,
                    verify_certs=verify_certs
                )
            elif hosts and username and password:
                self.client = Elasticsearch(
                    hosts=hosts,
                    basic_auth=(username, password),
                    request_timeout=timeout,
                    verify_certs=verify_certs
                )
            elif hosts and api_key:
                self.client = Elasticsearch(
                    hosts=hosts,
                    api_key=api_key,
                    request_timeout=timeout,
                    verify_certs=verify_certs
                )
            else:
                logger.error("Elasticsearch: missing required credentials")
                self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch client: {e}")
            self.client = None

    def _get_finding_index(self, timestamp: datetime = None) -> str:
        """Get Elasticsearch index name for findings with date suffix."""
        if not timestamp:
            timestamp = datetime.utcnow()
        return f"{self.index_prefix}-findings-{timestamp.strftime('%Y.%m.%d')}"

    def _get_scan_index(self) -> str:
        """Get Elasticsearch index name for scans."""
        return f"{self.index_prefix}-scans"

    def _normalize_finding(self, finding: dict) -> dict:
        """Normalize finding data for Elasticsearch."""
        return {
            "@timestamp": datetime.utcnow().isoformat(),
            "finding_id": finding.get("id"),
            "name": finding.get("name"),
            "description": finding.get("description"),
            "severity": finding.get("severity", "unknown"),
            "category": finding.get("category"),
            "confidence": finding.get("confidence", 0.0),
            "evidence": finding.get("evidence"),
            "remediation": finding.get("remediation"),
            "cve": finding.get("cve"),
            "tags": finding.get("tags", []),
            "metadata": finding.get("metadata", {}),
        }

    async def index_finding(self, finding: dict) -> bool:
        """
        Index a finding in Elasticsearch.

        Args:
            finding (dict): Finding data

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.client:
            logger.error("Elasticsearch client not initialized")
            return False

        try:
            doc = self._normalize_finding(finding)
            index = self._get_finding_index()

            result = self.client.index(
                index=index,
                id=finding.get("id"),
                document=doc
            )

            logger.info(f"Indexed finding {finding.get('id')} in {index}")
            return True

        except ElasticsearchException as e:
            logger.error(f"Elasticsearch indexing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Elasticsearch index_finding error: {e}")
            return False

    async def index_scan(self, scan: dict) -> bool:
        """
        Index a scan summary in Elasticsearch.

        Args:
            scan (dict): Scan data with keys: id, target, findings_count, risk_score, status, etc.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.client:
            logger.error("Elasticsearch client not initialized")
            return False

        try:
            doc = {
                "@timestamp": datetime.utcnow().isoformat(),
                "scan_id": scan.get("id"),
                "target": scan.get("target"),
                "findings_count": scan.get("findings_count", 0),
                "risk_score": scan.get("risk_score", 0.0),
                "status": scan.get("status", "completed"),
                "duration_seconds": scan.get("duration_seconds", 0),
                "severity_breakdown": scan.get("severity_breakdown", {}),
                "completed_at": scan.get("completed_at"),
                "scan_mode": scan.get("scan_mode"),
                "categories": scan.get("categories", []),
                "metadata": scan.get("metadata", {}),
            }

            index = self._get_scan_index()
            result = self.client.index(
                index=index,
                id=scan.get("id"),
                document=doc
            )

            logger.info(f"Indexed scan {scan.get('id')} in {index}")
            return True

        except ElasticsearchException as e:
            logger.error(f"Elasticsearch scan indexing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Elasticsearch index_scan error: {e}")
            return False

    async def bulk_index_findings(self, findings: List[dict]) -> tuple[int, int]:
        """
        Bulk index multiple findings.

        Args:
            findings (list): List of finding dictionaries

        Returns:
            tuple: (successful_count, failed_count)
        """
        if not self.client or not findings:
            return 0, len(findings) if findings else 0

        try:
            from elasticsearch.helpers import bulk

            actions = []
            for finding in findings:
                doc = self._normalize_finding(finding)
                actions.append({
                    "_index": self._get_finding_index(),
                    "_id": finding.get("id"),
                    "_source": doc
                })

            successful, failed = bulk(self.client, actions, raise_on_error=False)
            logger.info(f"Bulk indexed {successful} findings, {failed} failed")
            return successful, failed

        except Exception as e:
            logger.error(f"Elasticsearch bulk index error: {e}")
            return 0, len(findings)

    async def test_connection(self) -> bool:
        """
        Test connectivity to Elasticsearch.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        if not self.client:
            logger.error("Elasticsearch client not initialized")
            return False

        try:
            info = self.client.info()
            logger.info(f"Elasticsearch connection successful: {info.get('cluster_name')}")
            return True
        except ElasticsearchException as e:
            logger.error(f"Elasticsearch connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Elasticsearch test_connection error: {e}")
            return False

    async def search_findings(self, query: dict, size: int = 100) -> dict:
        """
        Search for findings in Elasticsearch.

        Args:
            query (dict): Elasticsearch query object
            size (int): Maximum results to return

        Returns:
            dict: Search results
        """
        if not self.client:
            logger.error("Elasticsearch client not initialized")
            return {"hits": {"total": 0, "hits": []}}

        try:
            index = f"{self.index_prefix}-findings-*"
            result = self.client.search(
                index=index,
                query=query,
                size=size
            )
            return result
        except Exception as e:
            logger.error(f"Elasticsearch search error: {e}")
            return {"hits": {"total": 0, "hits": []}}

    def close(self):
        """Close Elasticsearch connection."""
        if self.client:
            self.client.close()
