"""Celery tasks for compliance assessment."""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def run_compliance_assessment(self, scan_id: str, frameworks: list):
    """Run compliance assessment against requested frameworks."""
    try:
        results = {}
        scan_results = []  # Would load from DB in production
        for framework in frameworks:
            if framework == "eu_ai_act":
                from app.compliance.eu_ai_act import EUAIActEngine

                engine = EUAIActEngine()
            elif framework == "nist_ai_rmf":
                from app.compliance.nist_ai_rmf import NISTAIRMFEngine

                engine = NISTAIRMFEngine()
            elif framework == "owasp_agentic":
                from app.compliance.owasp_agentic import OWASPAgenticEngine

                engine = OWASPAgenticEngine()
            elif framework == "owasp_mcp":
                from app.compliance.owasp_mcp import OWASPMCPEngine

                engine = OWASPMCPEngine()
            else:
                continue
            assessments = engine.map_scan_results_to_controls(scan_results)
            results[framework] = {
                "score": engine.calculate_score(assessments),
                "controls": assessments,
                "gaps": [
                    {
                        "framework": g.framework,
                        "control_id": g.control_id,
                        "control_name": g.control_name,
                        "severity": g.severity,
                        "finding_count": g.finding_count,
                        "remediation_priority": g.remediation_priority,
                        "estimated_effort_days": g.estimated_effort_days,
                    }
                    for g in engine.identify_gaps(assessments)
                ],
            }
        return results
    except Exception as exc:
        logger.error(f"Compliance assessment failed: {exc}")
        raise self.retry(exc=exc, countdown=30)
