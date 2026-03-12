"""Celery tasks for PDF report generation."""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_report_task(self, scan_id: str, report_type: str, config: dict):
    """Generate PDF report asynchronously."""
    try:
        import asyncio
        from app.reports.generator import ReportGenerator

        generator = ReportGenerator()
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            generator.generate(
                scan_id=scan_id, report_type=report_type, config=config
            )
        )
        loop.close()
        return {"status": "completed", "report_id": str(result)}
    except Exception as exc:
        logger.error(f"Report generation failed for scan {scan_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
