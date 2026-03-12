"""AgentRed CLI: Report generation and management."""
import click
from typing import Optional


@click.group()
def report():
    """Generate and manage reports."""
    pass


@report.command(name="generate")
@click.option("--scan-id", required=True, help="Scan ID to generate report for")
@click.option("--format", type=click.Choice(["pdf", "json", "html"]), default="pdf", help="Report format")
@click.option("--include-compliance", is_flag=True, help="Include compliance mapping")
@click.option("--output", type=click.Path(), help="Save report to file")
def generate_report(scan_id: str, format: str, include_compliance: bool, output: Optional[str]):
    """Generate a report from a scan.

    Example:
        agentred report generate --scan-id abc123 --format pdf --output report.pdf
    """
    from ..cli import api_call, rprint
    import os

    try:
        payload = {
            "scan_id": scan_id,
            "format": format,
            "include_compliance": include_compliance
        }

        result = api_call("POST", "/api/v1/reports", data=payload)
        report_id = result.get("id")

        rprint(f"[green]Report generation started:[/green] {report_id}")

        # Poll for completion
        import time
        max_attempts = 120  # 10 minutes with 5s intervals
        for _ in range(max_attempts):
            status_result = api_call("GET", f"/api/v1/reports/{report_id}")
            status = status_result.get("status")

            if status == "completed":
                rprint(f"[green]Report generated successfully[/green]")

                if output:
                    # Download report
                    download_url = status_result.get("download_url")
                    if download_url:
                        import httpx
                        from ..cli import get_api_client
                        _, api_key = get_api_client()
                        headers = {"Authorization": f"Bearer {api_key}"}
                        r = httpx.get(download_url, headers=headers)
                        with open(output, "wb") as f:
                            f.write(r.content)
                        rprint(f"[green]Report saved to:[/green] {output}")
                return
            elif status == "failed":
                rprint(f"[red]Report generation failed[/red]")
                return

            time.sleep(5)

        rprint("[yellow]Report generation timed out[/yellow]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@report.command(name="list")
@click.option("--scan-id", help="Filter by scan")
@click.option("--limit", type=int, default=10)
def list_reports(scan_id: Optional[str], limit: int):
    """List generated reports."""
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        params = {"limit": limit}
        if scan_id:
            params["scan_id"] = scan_id

        result = api_call("GET", "/api/v1/reports", params=params)
        reports = result.get("reports", [])

        if not reports:
            rprint("[yellow]No reports found[/yellow]")
            return

        if console:
            table = Table(title="Reports")
            table.add_column("ID", style="cyan")
            table.add_column("Scan ID", style="magenta")
            table.add_column("Format", style="yellow")
            table.add_column("Created", style="green")

            for report in reports:
                table.add_row(
                    report.get("id", "")[:8],
                    report.get("scan_id", "")[:8],
                    report.get("format", ""),
                    report.get("created_at", "")[:10]
                )

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@report.command(name="download")
@click.argument("report_id")
@click.option("--output", type=click.Path(), required=True, help="Output file path")
def download_report(report_id: str, output: str):
    """Download a report."""
    from ..cli import api_call, rprint

    try:
        result = api_call("GET", f"/api/v1/reports/{report_id}")

        if result.get("status") != "completed":
            rprint(f"[yellow]Report status: {result.get('status')}[/yellow]")
            return

        download_url = result.get("download_url")
        if not download_url:
            rprint("[red]No download URL available[/red]")
            return

        import httpx
        from ..cli import get_api_client
        _, api_key = get_api_client()
        headers = {"Authorization": f"Bearer {api_key}"}
        r = httpx.get(download_url, headers=headers)

        with open(output, "wb") as f:
            f.write(r.content)

        rprint(f"[green]Report saved to:[/green] {output}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
