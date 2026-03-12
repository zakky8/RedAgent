"""AgentRed CLI: Scan commands for running security scans."""
import click
import json
import time
from typing import Optional
from pathlib import Path


@click.group()
def scan():
    """Manage and run security scans."""
    pass


@scan.command(name="run")
@click.option("--target-id", required=True, help="Target UUID to scan")
@click.option("--profile", type=click.Choice(["quick", "standard", "deep"]), default="standard", help="Scan profile")
@click.option("--categories", multiple=True, help="Attack categories to run (e.g., owasp_llm, jailbreaks)")
@click.option("--mode", type=click.Choice(["black_box", "gray_box", "white_box"]), default="black_box", help="Testing mode")
@click.option("--wait/--no-wait", default=False, help="Wait for scan to complete")
@click.option("--output", type=click.Path(), help="Save results to JSON file")
def run_scan(target_id: str, profile: str, categories: tuple, mode: str, wait: bool, output: Optional[str]):
    """Start a new security scan.

    Example:
        agentred scan run --target-id abc123 --profile deep --categories owasp_llm jailbreaks
    """
    from ..cli import api_call, console, rprint

    payload = {
        "target_id": target_id,
        "profile": profile,
        "categories": list(categories) if categories else None,
        "mode": mode
    }

    try:
        result = api_call("POST", "/api/v1/scans", data=payload)
        scan_id = result.get("id")

        if not scan_id:
            rprint("[red]Error: No scan ID in response[/red]")
            return

        rprint(f"[green]Scan started:[/green] {scan_id}")

        if wait:
            rprint("[cyan]Waiting for scan to complete...[/cyan]")
            while True:
                status_result = api_call("GET", f"/api/v1/scans/{scan_id}")
                status = status_result.get("status")

                if status == "completed":
                    rprint(f"[green]Scan completed![/green]")
                    break
                elif status == "failed":
                    rprint(f"[red]Scan failed[/red]")
                    return

                rprint(f"  Status: {status}")
                time.sleep(5)

            if output:
                with open(output, "w") as f:
                    json.dump(status_result, f, indent=2)
                rprint(f"[green]Results saved to:[/green] {output}")
        else:
            rprint(f"[cyan]Run 'agentred scan status {scan_id}' to check progress[/cyan]")

    except Exception as e:
        rprint(f"[red]Error starting scan: {e}[/red]")


@scan.command(name="status")
@click.argument("scan_id")
def scan_status(scan_id: str):
    """Get scan status and progress."""
    from ..cli import api_call, rprint

    try:
        result = api_call("GET", f"/api/v1/scans/{scan_id}")

        rprint(f"[bold]Scan ID:[/bold] {result.get('id')}")
        rprint(f"[bold]Status:[/bold] {result.get('status')}")
        rprint(f"[bold]Progress:[/bold] {result.get('progress_percent', 0)}%")
        rprint(f"[bold]Created:[/bold] {result.get('created_at')}")

        if result.get("completed_at"):
            rprint(f"[bold]Completed:[/bold] {result.get('completed_at')}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@scan.command(name="results")
@click.argument("scan_id")
@click.option("--format", type=click.Choice(["json", "table", "summary"]), default="summary")
@click.option("--output", type=click.Path(), help="Save to file")
def scan_results(scan_id: str, format: str, output: Optional[str]):
    """Get scan results."""
    from ..cli import api_call, rprint, console

    try:
        result = api_call("GET", f"/api/v1/scans/{scan_id}/results")

        if format == "json":
            output_data = json.dumps(result, indent=2)
            rprint(output_data)
        elif format == "summary":
            rprint(f"[bold]Risk Score:[/bold] {result.get('risk_score')}/100")
            rprint(f"[bold]Attacks Run:[/bold] {result.get('attacks_total')}")
            rprint(f"[bold]Successful:[/bold] {result.get('attacks_successful')}")
            rprint(f"[bold]ASR:[/bold] {result.get('asr'):.1%}")

        if output:
            with open(output, "w") as f:
                f.write(json.dumps(result, indent=2))
            rprint(f"[green]Saved to: {output}[/green]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@scan.command(name="list")
@click.option("--target-id", help="Filter by target")
@click.option("--status", type=click.Choice(["pending", "running", "completed", "failed"]))
@click.option("--limit", type=int, default=10)
def list_scans(target_id: Optional[str], status: Optional[str], limit: int):
    """List scans."""
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        params = {"limit": limit}
        if target_id:
            params["target_id"] = target_id
        if status:
            params["status"] = status

        result = api_call("GET", "/api/v1/scans", params=params)
        scans = result.get("scans", [])

        if not scans:
            rprint("[yellow]No scans found[/yellow]")
            return

        if console:
            table = Table(title="Recent Scans")
            table.add_column("ID", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Risk Score", style="yellow")
            table.add_column("Created", style="green")

            for scan in scans:
                table.add_row(
                    scan.get("id", "")[:8],
                    scan.get("status", ""),
                    str(scan.get("risk_score", "N/A")),
                    scan.get("created_at", "")[:10]
                )

            console.print(table)
        else:
            for scan in scans:
                rprint(f"  {scan.get('id')[:8]} - {scan.get('status')} - Risk: {scan.get('risk_score')}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@scan.command(name="stop")
@click.argument("scan_id")
def stop_scan(scan_id: str):
    """Stop a running scan."""
    from ..cli import api_call, rprint

    try:
        api_call("POST", f"/api/v1/scans/{scan_id}/stop")
        rprint(f"[green]Scan {scan_id[:8]} stopped[/green]")
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
