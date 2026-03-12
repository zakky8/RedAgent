"""AgentRed CLI: AI infrastructure CVE scanning."""
import click
from typing import Optional


@click.group()
def infra():
    """Scan AI infrastructure for CVEs and misconfigurations."""
    pass


@infra.command(name="scan")
@click.option("--target-url", required=True, help="AI infrastructure service URL (Ollama, ComfyUI, vLLM, etc.)")
@click.option("--service-type", type=click.Choice(["ollama", "comfyui", "vllm", "gradio", "ray", "jupyter", "mlflow", "langserve", "bentoml", "localai"]), help="Service type (auto-detect if not specified)")
@click.option("--deep", is_flag=True, help="Run deep CVE analysis")
@click.option("--output", type=click.Path(), help="Save results to JSON")
def scan_infra(target_url: str, service_type: Optional[str], deep: bool, output: Optional[str]):
    """Scan AI infrastructure for vulnerabilities and CVEs.

    Example:
        agentred infra scan --target-url http://localhost:11434 --service-type ollama --deep
    """
    from ..cli import api_call, rprint
    import json

    try:
        payload = {
            "target_url": target_url,
            "deep_scan": deep
        }

        if service_type:
            payload["service_type"] = service_type

        rprint("[cyan]Scanning AI infrastructure...[/cyan]")
        result = api_call("POST", "/api/v1/infra/scan", data=payload)

        service_info = result.get("service_info", {})
        rprint(f"[bold]Service:[/bold] {service_info.get('name')} {service_info.get('version')}")
        rprint(f"[bold]Exposed:[/bold] {service_info.get('is_public')}")

        vulnerabilities = result.get("vulnerabilities", [])
        rprint(f"\n[green]Found {len(vulnerabilities)} vulnerabilities[/green]")

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

            severity_color = {
                "critical": "red",
                "high": "red",
                "medium": "yellow",
                "low": "green"
            }.get(severity, "white")

            rprint(f"  [{severity_color}]{severity.upper()}[/{severity_color}] {vuln.get('cve_id', 'N/A')}")
            rprint(f"    {vuln.get('name')}")

        rprint("")
        rprint(f"[bold]Summary:[/bold]")
        rprint(f"  Critical: [red]{severity_counts['critical']}[/red]")
        rprint(f"  High: [red]{severity_counts['high']}[/red]")
        rprint(f"  Medium: [yellow]{severity_counts['medium']}[/yellow]")
        rprint(f"  Low: [green]{severity_counts['low']}[/green]")

        if output:
            with open(output, "w") as f:
                json.dump(result, f, indent=2)
            rprint(f"\n[green]Results saved to:[/green] {output}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@infra.command(name="detect")
@click.option("--target-url", required=True, help="Service URL to fingerprint")
def detect_service(target_url: str):
    """Auto-detect AI infrastructure service type and version."""
    from ..cli import api_call, rprint

    try:
        rprint("[cyan]Detecting service...[/cyan]")
        result = api_call("GET", "/api/v1/infra/detect", params={"target_url": target_url})

        service = result.get("service", {})
        rprint(f"[green]Service detected:[/green]")
        rprint(f"  Type: [bold]{service.get('type')}[/bold]")
        rprint(f"  Version: {service.get('version')}")
        rprint(f"  Confidence: {service.get('confidence')}%")

        if service.get("known_vulnerabilities"):
            rprint(f"\n[yellow]Known CVEs:[/yellow] {len(service.get('known_vulnerabilities', []))}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@infra.command(name="cves")
@click.option("--service", required=True, type=click.Choice(["ollama", "comfyui", "vllm", "gradio", "ray", "jupyter", "mlflow", "langserve", "bentoml", "localai"]))
@click.option("--version", help="Service version (defaults to latest)")
def list_cves(service: str, version: Optional[str]):
    """List known CVEs for an AI infrastructure service.

    Example:
        agentred infra cves --service ollama --version 0.1.24
    """
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        params = {"service": service}
        if version:
            params["version"] = version

        result = api_call("GET", "/api/v1/infra/cves", params=params)
        cves = result.get("cves", [])

        if not cves:
            rprint("[yellow]No CVEs found[/yellow]")
            return

        if console:
            table = Table(title=f"{service.upper()} CVEs")
            table.add_column("CVE ID", style="cyan")
            table.add_column("CVSS", style="yellow")
            table.add_column("Severity", style="red")
            table.add_column("Title", style="white")

            for cve in cves:
                severity = cve.get("severity", "medium")
                severity_color = "red" if severity in ["critical", "high"] else "yellow"

                table.add_row(
                    cve.get("cve_id", ""),
                    str(cve.get("cvss_score", "N/A")),
                    f"[{severity_color}]{severity}[/{severity_color}]",
                    cve.get("title", "")[:40]
                )

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@infra.command(name="misconfig")
@click.option("--target-url", required=True, help="Service URL to audit")
def check_misconfig(target_url: str):
    """Check for common AI infrastructure misconfigurations."""
    from ..cli import api_call, rprint

    try:
        result = api_call("POST", "/api/v1/infra/check-misconfig", data={"target_url": target_url})

        misconfigs = result.get("misconfigurations", [])
        rprint(f"[bold]Configuration Audit[/bold]")
        rprint(f"Found {len(misconfigs)} potential issues:\n")

        for i, config in enumerate(misconfigs, 1):
            rprint(f"{i}. {config.get('issue')}")
            rprint(f"   Severity: [yellow]{config.get('severity')}[/yellow]")
            rprint(f"   Fix: {config.get('remediation')}\n")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
