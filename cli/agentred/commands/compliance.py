"""AgentRed CLI: Compliance assessment and reporting."""
import click
from typing import Optional


@click.group()
def compliance():
    """Manage compliance assessments."""
    pass


@compliance.command(name="assess")
@click.option("--scan-id", required=True, help="Scan ID to assess")
@click.option("--frameworks", multiple=True, help="Compliance frameworks (eu_ai_act, owasp_llm, nist_ai_rmf, iso_42001)")
def assess_compliance(scan_id: str, frameworks: tuple):
    """Run compliance assessment on a scan.

    Example:
        agentred compliance assess --scan-id abc123 --frameworks eu_ai_act owasp_llm
    """
    from ..cli import api_call, rprint

    try:
        payload = {
            "scan_id": scan_id,
            "frameworks": list(frameworks) if frameworks else ["eu_ai_act", "owasp_llm"]
        }

        result = api_call("POST", "/api/v1/compliance/assess", data=payload)
        rprint(f"[green]Compliance assessment completed[/green]")

        # Display results
        for framework, data in result.items():
            if isinstance(data, dict):
                score = data.get("score", 0)
                status = data.get("status", "unknown")
                rprint(f"  [bold]{framework}:[/bold] {score}% - {status}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@compliance.command(name="posture")
@click.option("--org-id", help="Organization ID (defaults to current org)")
@click.option("--framework", type=click.Choice(["eu_ai_act", "owasp_llm", "nist_ai_rmf", "iso_42001", "soc2"]))
def compliance_posture(org_id: Optional[str], framework: Optional[str]):
    """Get overall compliance posture.

    Example:
        agentred compliance posture --framework eu_ai_act
    """
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        params = {}
        if org_id:
            params["org_id"] = org_id
        if framework:
            params["framework"] = framework

        result = api_call("GET", "/api/v1/compliance/posture", params=params)

        if console:
            table = Table(title="Compliance Posture")
            table.add_column("Framework", style="cyan")
            table.add_column("Score", style="yellow")
            table.add_column("Status", style="magenta")
            table.add_column("Gaps", style="red")

            for fw, data in result.items():
                if isinstance(data, dict):
                    table.add_row(
                        fw,
                        str(data.get("score", "N/A")),
                        data.get("status", "unknown"),
                        str(data.get("gap_count", 0))
                    )

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@compliance.command(name="gaps")
@click.option("--scan-id", required=True, help="Scan ID to analyze")
@click.option("--framework", type=click.Choice(["eu_ai_act", "owasp_llm", "nist_ai_rmf", "iso_42001"]), default="eu_ai_act")
def compliance_gaps(scan_id: str, framework: str):
    """Analyze compliance gaps."""
    from ..cli import api_call, rprint

    try:
        result = api_call("GET", f"/api/v1/compliance/{framework}/gaps", params={"scan_id": scan_id})

        rprint(f"[bold][cyan]{framework.upper()} Compliance Gaps[/cyan][/bold]")
        rprint("")

        gaps = result.get("gaps", [])
        for i, gap in enumerate(gaps, 1):
            rprint(f"[bold]{i}. {gap.get('requirement')}[/bold]")
            rprint(f"   Status: [yellow]{gap.get('status')}[/yellow]")
            rprint(f"   Remediation: {gap.get('remediation')}")
            rprint("")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@compliance.command(name="evidence")
@click.option("--compliance-id", required=True, help="Compliance record ID")
@click.option("--output", type=click.Path(), help="Save evidence to file")
def collect_evidence(compliance_id: str, output: Optional[str]):
    """Collect evidence for compliance audit."""
    from ..cli import api_call, rprint
    import json

    try:
        result = api_call("GET", f"/api/v1/compliance/{compliance_id}/evidence")

        evidence = result.get("evidence", {})
        rprint(f"[green]Evidence collected:[/green]")
        rprint(f"  Scans: {evidence.get('scan_count', 0)}")
        rprint(f"  Findings: {evidence.get('finding_count', 0)}")
        rprint(f"  Remediations: {evidence.get('remediation_count', 0)}")

        if output:
            with open(output, "w") as f:
                json.dump(evidence, f, indent=2)
            rprint(f"[green]Evidence saved to:[/green] {output}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
