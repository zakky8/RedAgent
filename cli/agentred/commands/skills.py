"""AgentRed CLI: Agent skills security scanning."""
import click
from typing import Optional


@click.group()
def skills():
    """Scan agent skills for security issues."""
    pass


@skills.command(name="scan")
@click.option("--agent-id", required=True, help="Agent UUID to scan skills for")
@click.option("--skill-ids", multiple=True, help="Specific skills to scan (default: all)")
@click.option("--deep", is_flag=True, help="Deep security analysis")
@click.option("--output", type=click.Path(), help="Save results to JSON")
def scan_skills(agent_id: str, skill_ids: tuple, deep: bool, output: Optional[str]):
    """Scan agent skills for security vulnerabilities.

    Example:
        agentred skills scan --agent-id abc123 --deep
    """
    from ..cli import api_call, rprint
    import json

    try:
        payload = {
            "agent_id": agent_id,
            "deep_scan": deep
        }

        if skill_ids:
            payload["skill_ids"] = list(skill_ids)

        rprint("[cyan]Scanning agent skills...[/cyan]")
        result = api_call("POST", "/api/v1/skills/scan", data=payload)

        findings = result.get("findings", [])
        rprint(f"[green]Scan completed:[/green] Found {len(findings)} security issues")

        categories = {}
        for finding in findings:
            category = finding.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(finding)

        for category, items in categories.items():
            rprint(f"\n[bold]{category.upper()}[/bold] ({len(items)})")
            for item in items[:5]:  # Show top 5
                severity = item.get("severity", "medium")
                severity_color = "red" if severity == "critical" else "yellow" if severity == "high" else "green"
                rprint(f"  [{severity_color}]{severity}[/{severity_color}] {item.get('name')}")

        if len(findings) > 5:
            rprint(f"  ... and {len(findings) - 5} more")

        if output:
            with open(output, "w") as f:
                json.dump(result, f, indent=2)
            rprint(f"\n[green]Results saved to:[/green] {output}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@skills.command(name="list")
@click.option("--agent-id", required=True, help="Agent UUID")
def list_skills(agent_id: str):
    """List all skills for an agent."""
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        result = api_call("GET", "/api/v1/agents/{}/skills".format(agent_id))
        skills_list = result.get("skills", [])

        if not skills_list:
            rprint("[yellow]No skills found[/yellow]")
            return

        if console:
            table = Table(title="Agent Skills")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Risk", style="yellow")
            table.add_column("Status", style="green")

            for skill in skills_list:
                risk = skill.get("risk_level", "medium")
                risk_color = "red" if risk == "high" else "yellow" if risk == "medium" else "green"
                status = skill.get("status", "unknown")
                status_color = "green" if status == "trusted" else "yellow"

                table.add_row(
                    skill.get("name", ""),
                    skill.get("type", ""),
                    f"[{risk_color}]{risk}[/{risk_color}]",
                    f"[{status_color}]{status}[/{status_color}]"
                )

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@skills.command(name="audit")
@click.option("--skill-id", required=True, help="Skill UUID to audit")
@click.option("--output", type=click.Path(), help="Save audit report to file")
def audit_skill(skill_id: str, output: Optional[str]):
    """Perform detailed security audit of a skill.

    Example:
        agentred skills audit --skill-id xyz789 --output audit-report.json
    """
    from ..cli import api_call, rprint
    import json

    try:
        rprint("[cyan]Auditing skill...[/cyan]")
        result = api_call("GET", f"/api/v1/skills/{skill_id}/audit")

        audit_report = result.get("audit_report", {})
        rprint(f"[bold]Skill Audit Report[/bold]")
        rprint(f"  Skill: {audit_report.get('skill_name')}")
        rprint(f"  Author: {audit_report.get('author')}")
        rprint(f"  Risk Score: {audit_report.get('risk_score')}/100")
        rprint("")

        checks = audit_report.get("security_checks", {})
        for check_name, check_result in checks.items():
            status = "[green]PASS[/green]" if check_result.get("passed") else "[red]FAIL[/red]"
            rprint(f"  {check_name}: {status}")

        if output:
            with open(output, "w") as f:
                json.dump(audit_report, f, indent=2)
            rprint(f"\n[green]Audit saved to:[/green] {output}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@skills.command(name="test-prompt-injection")
@click.option("--skill-id", required=True, help="Skill UUID")
@click.option("--payload", required=True, help="Injection payload")
def test_skill_injection(skill_id: str, payload: str):
    """Test a skill for prompt injection vulnerabilities."""
    from ..cli import api_call, rprint

    try:
        result = api_call("POST", f"/api/v1/skills/{skill_id}/test-injection", data={
            "payload": payload
        })

        vulnerable = result.get("vulnerable", False)

        if vulnerable:
            rprint(f"[red][VULNERABLE][/red] Skill accepts prompt injection")
            rprint(f"  Extracted data: {result.get('extracted_data')}")
        else:
            rprint(f"[green][SAFE][/green] Skill appears resistant")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
