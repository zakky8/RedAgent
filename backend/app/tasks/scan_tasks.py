"""
Scan execution Celery tasks.
Build Rule 2: Never crash a scan — all exceptions caught.
Build Rule 14: Retry with exponential backoff.
"""
import asyncio
import logging
from datetime import datetime
from uuid import UUID

from celery import shared_task

from app.celery_app import celery_app
from app.core.engine import AttackEngine
from app.database import get_db_sync
from app.models.scan import Scan
from app.models.attack_result import AttackResult as AttackResultModel

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def run_scan_task(self, scan_id: str):
    """
    Main Celery task to execute a scan.
    Build Rule 2: NEVER crashes — all exceptions caught and logged.
    Build Rule 14: Retries with exponential backoff on transient failures.
    """
    logger.info(f"Starting scan task for scan_id={scan_id}")
    try:
        with get_db_sync() as db:
            scan = db.query(Scan).filter(Scan.id == UUID(scan_id)).first()
            if not scan:
                logger.error(f"Scan {scan_id} not found")
                return

            # Update status to running
            scan.status = "running"
            scan.started_at = datetime.utcnow()
            scan.celery_task_id = self.request.id
            db.commit()

            # Get target config
            target = scan.target
            target_config = {
                "endpoint_url": target.endpoint_url,
                "model_type": target.model_type,
                "framework": target.framework,
                "system_prompt": target.system_prompt,
                "auth_config": target.auth_config,
                "tools": target.tools,
                "memory_enabled": target.memory_enabled,
                "is_multi_agent": target.is_multi_agent,
            }
            scan_config = {
                "scan_mode": scan.scan_mode,
                "test_mode": scan.test_mode,
                "categories": scan.categories,
                "attack_ids": scan.attack_ids,
                "probabilistic_runs": scan.probabilistic_runs,
                "concurrent_workers": scan.concurrent_workers,
            }

        # Run attacks async
        engine = AttackEngine(
            scan_id=scan_id,
            target_config=target_config,
            scan_config=scan_config,
        )
        results = asyncio.run(engine.run())

        # Save results
        with get_db_sync() as db:
            scan = db.query(Scan).filter(Scan.id == UUID(scan_id)).first()

            successful = 0
            for result in results:
                attack_result = AttackResultModel(
                    org_id=scan.org_id,
                    scan_id=scan.id,
                    attack_id=result.attack_id,
                    attack_name=result.attack_name,
                    category=result.category,
                    severity=result.severity,
                    success=result.success,
                    confidence=result.confidence,
                    asr_rate=result.asr_rate,
                    payload_used=result.payload_used[:10000] if result.payload_used else None,
                    response_received=result.response_received[:10000] if result.response_received else None,
                    vulnerability_found=result.vulnerability_found,
                    framework_mapping=result.framework_mapping,
                    cvss_score=result.cvss_score,
                    remediation=result.remediation,
                    execution_time_ms=result.execution_time_ms,
                )
                db.add(attack_result)
                if result.success:
                    successful += 1

            severity_counts = engine.get_severity_counts()
            scan.status = "completed"
            scan.completed_at = datetime.utcnow()
            scan.risk_score = engine.calculate_risk_score()
            scan.asr = engine.get_asr()
            scan.total_attacks = len(results)
            scan.successful_attacks = successful
            scan.critical_count = severity_counts["critical"]
            scan.high_count = severity_counts["high"]
            scan.medium_count = severity_counts["medium"]
            scan.low_count = severity_counts["low"]
            db.commit()

            logger.info(
                f"Scan {scan_id} completed: {successful}/{len(results)} attacks successful, "
                f"risk_score={scan.risk_score}"
            )

    except Exception as exc:
        logger.error(f"Scan {scan_id} failed: {exc}", exc_info=True)
        try:
            with get_db_sync() as db:
                scan = db.query(Scan).filter(Scan.id == UUID(scan_id)).first()
                if scan:
                    scan.status = "failed"
                    scan.error_message = str(exc)[:1000]
                    db.commit()
        except Exception:
            pass
        # Retry with exponential backoff (Build Rule 14)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
