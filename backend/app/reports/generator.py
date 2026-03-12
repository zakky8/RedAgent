"""
PDF Report Generator using WeasyPrint + Jinja2.
Generates 5 report types for AgentRed scans.
"""
import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from typing import Optional

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
STYLES_DIR = Path(__file__).parent / "styles"

REPORT_TYPES = ["executive", "technical", "compliance", "eu_ai_act", "remediation"]

class ReportGenerator:
    """Generate professional PDF reports for AgentRed scan results."""

    def __init__(self):
        """Initialize report generator with Jinja2 environment."""
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=True
        )

    def render_html(self, template_name: str, context: dict) -> str:
        """
        Render a Jinja2 HTML template with context.

        Args:
            template_name: Name of template file (without .html extension)
            context: Context dictionary for template rendering

        Returns:
            Rendered HTML string

        Raises:
            Exception: If template rendering fails
        """
        try:
            template = self.jinja_env.get_template(f"{template_name}.html")
            context_with_timestamp = {
                **context,
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            }
            return template.render(**context_with_timestamp)
        except Exception as e:
            logger.error(f"Template render error for {template_name}: {e}")
            raise

    async def generate_pdf(self, report_type: str, context: dict) -> bytes:
        """
        Generate PDF from HTML template.

        Args:
            report_type: Type of report to generate
            context: Context dictionary for template rendering

        Returns:
            PDF file as bytes

        Raises:
            ValueError: If report type is invalid
            Exception: If PDF generation fails
        """
        if report_type not in REPORT_TYPES:
            raise ValueError(f"Invalid report type: {report_type}. Supported: {REPORT_TYPES}")

        try:
            from weasyprint import HTML, CSS
        except ImportError:
            # Fallback: return HTML as bytes if WeasyPrint not available
            logger.warning("WeasyPrint not available, returning HTML instead of PDF")
            html = self.render_html(report_type, context)
            return html.encode()

        html_content = self.render_html(report_type, context)
        css_path = str(STYLES_DIR / "report.css")

        try:
            pdf = HTML(string=html_content).write_pdf(
                stylesheets=[CSS(filename=css_path)] if os.path.exists(css_path) else []
            )
            return pdf
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise

    def build_executive_context(self, scan: dict, results: list[dict]) -> dict:
        """
        Build context for executive report.

        Args:
            scan: Scan metadata dictionary
            results: List of scan result dictionaries

        Returns:
            Context dictionary for executive template
        """
        critical = [r for r in results if r.get("severity") == "critical" and r.get("success")]
        high = [r for r in results if r.get("severity") == "high" and r.get("success")]
        medium = [r for r in results if r.get("severity") == "medium" and r.get("success")]

        risk_score = scan.get("risk_score", 0)
        if risk_score > 80:
            risk_level = "Critical"
        elif risk_score > 60:
            risk_level = "High"
        elif risk_score > 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "scan": scan,
            "risk_score": risk_score,
            "asr": scan.get("asr", 0),
            "top_findings": (critical + high + medium)[:5],
            "critical_count": len(critical),
            "high_count": len(high),
            "medium_count": len(medium),
            "total_attacks": scan.get("attack_count", 0),
            "risk_level": risk_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def build_technical_context(self, scan: dict, results: list[dict]) -> dict:
        """
        Build context for technical report.

        Args:
            scan: Scan metadata dictionary
            results: List of scan result dictionaries with full details

        Returns:
            Context dictionary for technical template
        """
        return {
            "scan": scan,
            "results": results,
            "total_attacks": len(results),
            "successful_attacks": len([r for r in results if r.get("success")]),
            "by_category": self._organize_by_category(results),
            "by_severity": self._organize_by_severity(results),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def build_compliance_context(self, scan: dict, results: list[dict], frameworks: list[str]) -> dict:
        """
        Build context for compliance report.

        Args:
            scan: Scan metadata dictionary
            results: List of scan result dictionaries
            frameworks: List of framework names (e.g., ["EU_AI_ACT", "NIST_AI_RMF"])

        Returns:
            Context dictionary for compliance template
        """
        return {
            "scan": scan,
            "results": results,
            "frameworks": frameworks,
            "total_controls": len(results),
            "passing_controls": len([r for r in results if r.get("status") == "pass"]),
            "failing_controls": len([r for r in results if r.get("status") == "fail"]),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def build_eu_ai_act_context(self, scan: dict, assessments: list[dict]) -> dict:
        """
        Build context for EU AI Act report.

        Args:
            scan: Scan metadata dictionary
            assessments: List of EU AI Act control assessments

        Returns:
            Context dictionary for EU AI Act template
        """
        articles = {}
        for a in assessments:
            article = a.get("article", "Unknown")
            if article not in articles:
                articles[article] = []
            articles[article].append(a)

        return {
            "scan": scan,
            "assessments": assessments,
            "articles": articles,
            "legal_disclaimer": (
                "This report was generated automatically by AgentRed and documents the results "
                "of adversarial testing performed on the AI system. It is intended as evidence of "
                "testing effort and due diligence. It does not constitute a legal certification and "
                "does not substitute for review by a qualified auditor or legal professional."
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def build_remediation_context(self, scan: dict, gaps: list[dict], roadmap: dict) -> dict:
        """
        Build context for remediation report.

        Args:
            scan: Scan metadata dictionary
            gaps: List of identified gaps
            roadmap: Remediation roadmap dictionary

        Returns:
            Context dictionary for remediation template
        """
        return {
            "scan": scan,
            "gaps": gaps,
            "roadmap": roadmap,
            "critical_gaps": [g for g in gaps if g.get("severity") == "high"],
            "total_gaps": len(gaps),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _organize_by_category(results: list[dict]) -> dict:
        """Organize results by attack category."""
        organized = {}
        for r in results:
            cat = r.get("category", "unknown")
            if cat not in organized:
                organized[cat] = []
            organized[cat].append(r)
        return organized

    @staticmethod
    def _organize_by_severity(results: list[dict]) -> dict:
        """Organize results by severity level."""
        return {
            "critical": [r for r in results if r.get("severity") == "critical"],
            "high": [r for r in results if r.get("severity") == "high"],
            "medium": [r for r in results if r.get("severity") == "medium"],
            "low": [r for r in results if r.get("severity") == "low"],
        }


# Global instance for convenience
report_generator = ReportGenerator()
