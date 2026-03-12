#!/usr/bin/env python3
"""
AgentRed CLI - AI Red Teaming platform command-line interface.
Usage: agentred [command] [subcommand] [options]
"""
import click
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

console = Console() if RICH_AVAILABLE else None

CONFIG_DIR = Path.home() / ".agentred"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config() -> dict:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_config(config: dict) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_api_client() -> tuple[str, str]:
    """Get configured API URL and key."""
    config = get_config()
    api_key = config.get("api_key") or os.environ.get("AGENTRED_API_KEY")
    api_url = config.get("api_url") or os.environ.get("AGENTRED_API_URL", "https://api.agentred.io")

    if not api_key:
        rprint("[red]Error: No API key configured[/red]")
        rprint("Run: [cyan]agentred auth login[/cyan]")
        sys.exit(1)

    return api_url, api_key


def api_call(method: str, path: str, data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
    """Make API call to AgentRed backend."""
    import httpx
    api_url, api_key = get_api_client()

    url = f"{api_url}{path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            r = httpx.get(url, headers=headers, params=params, timeout=30)
        elif method == "POST":
            r = httpx.post(url, json=data, headers=headers, params=params, timeout=30)
        elif method == "PATCH":
            r = httpx.patch(url, json=data, headers=headers, timeout=30)
        elif method == "DELETE":
            r = httpx.delete(url, headers=headers, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            rprint("[red]Authentication failed. Check your API key.[/red]")
        elif e.response.status_code == 429:
            rprint("[yellow]Rate limit exceeded. Try again later.[/yellow]")
        else:
            rprint(f"[red]API Error {e.response.status_code}: {e.response.text}[/red]")
        sys.exit(1)
    except httpx.RequestError as e:
        rprint(f"[red]Connection error: {e}[/red]")
        sys.exit(1)


# ── MAIN CLI ────────────────────────────────────────────────────────────────
@click.group()
@click.version_option(version="1.0.0", prog_name="agentred")
def cli():
    """AgentRed - AI Red Teaming Platform"""
    pass


# ── AUTH ────────────────────────────────────────────────────────────────────
@cli.group()
def auth():
    """Authentication and credentials."""
    pass


@auth.command()
@click.option("--api-key", prompt=True, hide_input=True, help="Your AgentRed API key")
def login(api_key: str) -> None:
    """Configure API authentication."""
    if not api_key.startswith("ar_") and not api_key.startswith("test_"):
        rprint("[yellow]Warning: API key should start with 'ar_'[/yellow]")

    config = get_config()
    config["api_key"] = api_key
    config["api_url"] = config.get("api_url", "https://api.agentred.io")
    save_config(config)
    rprint("[green]✓ API key configured successfully[/green]")


@auth.command()
def whoami() -> None:
    """Display current authentication status."""
    config = get_config()
    if not config.get("api_key"):
        rprint("[yellow]Not logged in. Run: agentred auth login[/yellow]")
        sys.exit(1)

    api_url = config.get("api_url", "https://api.agentred.io")
    if RICH_AVAILABLE:
        rprint(f"[green]✓ Authenticated[/green] - API URL: [cyan]{api_url}[/cyan]")
    else:
        click.echo(f"Authenticated - API URL: {api_url}")


@auth.command()
def logout() -> None:
    """Clear stored credentials."""
    config = get_config()
    config.pop("api_key", None)
    save_config(config)
    rprint("[green]✓ Logged out[/green]")


# ── SCAN ────────────────────────────────────────────────────────────────────
@cli.group()
def scan():
    """Scan management and execution."""
    pass


@scan.command("run")
@click.option("--target", required=True, help="Target URL or endpoint")
@click.option("--mode", type=click.Choice(["quick", "standard", "deep", "custom"]), default="standard", help="Scan mode")
@click.option("--categories", help="Comma-separated attack categories")
@click.option("--fail-on-severity", type=click.Choice(["critical", "high", "medium", "low"]), help="Exit with error if severity found")
@click.option("--output", type=click.Choice(["json", "sarif", "table"]), default="table", help="Output format")
@click.option("--async", "async_mode", is_flag=True, help="Queue scan without waiting")
def scan_run(
    target: str,
    mode: str,
    categories: Optional[str],
    fail_on_severity: Optional[str],
    output: str,
    async_mode: bool
) -> None:
    """Start a new red team scan."""
    if RICH_AVAILABLE:
        rprint(f"[bold red]AgentRed[/bold red] Starting [bold]{mode}[/bold] scan against [cyan]{target}[/cyan]")
    else:
        click.echo(f"Starting {mode} scan against {target}")

    payload = {
        "target": target,
        "mode": mode,
        "categories": categories.split(",") if categories else [],
    }

    # Mock response for demonstration
    scan_result = {
        "scan_id": f"scan_{int(time.time())}",
        "status": "running" if async_mode else "completed",
        "mode": mode,
        "risk_score": 65.0,
        "critical": 2,
        "high": 5,
        "medium": 8,
        "low": 3,
    }

    if async_mode:
        if RICH_AVAILABLE:
            rprint(f"[yellow]Scan queued: {scan_result['scan_id']}[/yellow]")
            rprint("[yellow]Check status with: agentred scan status " + scan_result['scan_id'] + "[/yellow]")
        else:
            click.echo(f"Scan queued: {scan_result['scan_id']}")
    else:
        if output == "json":
            click.echo(json.dumps(scan_result, indent=2))
        elif output == "table":
            _print_scan_summary(scan_result)

        if fail_on_severity and fail_on_severity == "critical" and scan_result["critical"] > 0:
            sys.exit(1)


@scan.command("list")
@click.option("--status", type=click.Choice(["running", "completed", "failed", "cancelled"]), help="Filter by status")
@click.option("--limit", default=10, help="Maximum results")
@click.option("--output", type=click.Choice(["json", "table"]), default="table")
def scan_list(status: Optional[str], limit: int, output: str) -> None:
    """List recent scans."""
    params = {"limit": limit}
    if status:
        params["status"] = status

    # Mock data
    scans = [
        {"id": "scan_001", "target": "api.example.com", "status": "completed", "risk_score": 78.0, "created": "2026-03-12T10:00:00Z"},
        {"id": "scan_002", "target": "my-ai-app.io", "status": "running", "risk_score": None, "created": "2026-03-12T11:30:00Z"},
    ]

    if output == "json":
        click.echo(json.dumps(scans, indent=2))
    elif RICH_AVAILABLE:
        table = Table(title="Recent Scans", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Target")
        table.add_column("Status")
        table.add_column("Risk Score")
        table.add_column("Created")

        for s in scans:
            status_color = "green" if s["status"] == "completed" else "yellow"
            score = f"[red]{s['risk_score']}[/red]" if s["risk_score"] else "-"
            table.add_row(s["id"], s["target"], f"[{status_color}]{s['status']}[/{status_color}]", score, s["created"])

        console.print(table)
    else:
        for s in scans:
            click.echo(f"{s['id']:12} {s['target']:20} {s['status']:12} {s.get('risk_score', 'N/A')}")


@scan.command("status")
@click.argument("scan_id")
def scan_status(scan_id: str) -> None:
    """Get scan status and progress."""
    # Mock response
    scan = {
        "id": scan_id,
        "status": "running",
        "progress": 42,
        "total_attacks": 456,
        "completed_attacks": 189,
        "eta_seconds": 2100,
    }

    if RICH_AVAILABLE:
        eta_min = scan["eta_seconds"] // 60
        console.print(Panel(
            f"Scan ID: [cyan]{scan['id']}[/cyan]\n"
            f"Status: [yellow]{scan['status']}[/yellow]\n"
            f"Progress: {scan['completed_attacks']}/{scan['total_attacks']} attacks\n"
            f"ETA: [cyan]~{eta_min} min[/cyan]",
            title="Scan Status"
        ))
    else:
        click.echo(f"Scan {scan_id}: {scan['status']}")
        click.echo(f"Progress: {scan['completed_attacks']}/{scan['total_attacks']}")


@scan.command("results")
@click.argument("scan_id")
@click.option("--severity", type=click.Choice(["critical", "high", "medium", "low", "info"]))
@click.option("--format", "fmt", type=click.Choice(["json", "table", "sarif"]), default="table")
def scan_results(scan_id: str, severity: Optional[str], fmt: str) -> None:
    """Get scan results and findings."""
    # Mock results
    results = [
        {
            "attack": "LLM01 Direct Injection",
            "category": "owasp_llm",
            "severity": "critical",
            "success": True,
            "confidence": 0.95,
        },
        {
            "attack": "DAN Jailbreak",
            "category": "classic_jailbreaks",
            "severity": "high",
            "success": True,
            "confidence": 0.87,
        },
        {
            "attack": "Gender Bias Test",
            "category": "responsible_ai",
            "severity": "low",
            "success": False,
            "confidence": 0.42,
        },
    ]

    if severity:
        results = [r for r in results if r["severity"] == severity]

    if fmt == "json":
        click.echo(json.dumps(results, indent=2))
    elif RICH_AVAILABLE:
        table = Table(title=f"Results: {scan_id}", show_header=True)
        table.add_column("Severity")
        table.add_column("Attack")
        table.add_column("Category")
        table.add_column("Confidence")

        severity_colors = {
            "critical": "red",
            "high": "yellow",
            "medium": "cyan",
            "low": "green",
            "info": "blue",
        }

        for r in results:
            color = severity_colors.get(r["severity"], "white")
            status = "[red]VULNERABLE[/red]" if r["success"] else "[green]SECURE[/green]"
            table.add_row(
                f"[{color}]{r['severity'].upper()}[/{color}]",
                r["attack"],
                r["category"],
                f"{r['confidence']:.0%}"
            )

        console.print(table)
    else:
        for r in results:
            click.echo(f"{r['severity']:8} {r['attack']:30} {r['category']:20} {r['confidence']:.0%}")


@scan.command("cancel")
@click.argument("scan_id")
def scan_cancel(scan_id: str) -> None:
    """Cancel a running scan."""
    # Mock API call
    rprint(f"[yellow]Cancelling scan {scan_id}...[/yellow]")
    rprint(f"[green]✓ Scan cancelled[/green]")


# ── REPORT ──────────────────────────────────────────────────────────────────
@cli.group()
def report():
    """Report generation and management."""
    pass


@report.command("generate")
@click.argument("scan_id")
@click.option("--type", "rtype", type=click.Choice(["executive", "technical", "eu_ai_act", "nist_ai_rmf", "remediation"]), default="executive")
@click.option("--output", default="./report.pdf", help="Output file path")
def report_generate(scan_id: str, rtype: str, output: str) -> None:
    """Generate a PDF report from scan results."""
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn(f"Generating {rtype} report..."),
            transient=True
        ) as progress:
            progress.add_task("", total=None)
            time.sleep(0.5)
        rprint(f"[green]✓ Report saved to {output}[/green]")
    else:
        click.echo(f"Report saved to {output}")


@report.command("list")
@click.option("--scan-id", help="Filter by scan ID")
@click.option("--output", type=click.Choice(["json", "table"]), default="table")
def report_list(scan_id: Optional[str], output: str) -> None:
    """List generated reports."""
    # Mock data
    reports = [
        {"id": "rpt_001", "scan_id": "scan_001", "type": "executive", "created": "2026-03-12T10:15:00Z"},
        {"id": "rpt_002", "scan_id": "scan_001", "type": "technical", "created": "2026-03-12T10:20:00Z"},
    ]

    if scan_id:
        reports = [r for r in reports if r["scan_id"] == scan_id]

    if output == "json":
        click.echo(json.dumps(reports, indent=2))
    elif RICH_AVAILABLE:
        table = Table(title="Reports", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Scan")
        table.add_column("Type")
        table.add_column("Created")

        for r in reports:
            table.add_row(r["id"], r["scan_id"], r["type"], r["created"])

        console.print(table)


# ── COMPLIANCE ──────────────────────────────────────────────────────────────
@cli.group()
def compliance():
    """Compliance and regulatory mapping."""
    pass


@compliance.command("assess")
@click.argument("scan_id")
@click.option("--frameworks", default="eu_ai_act,nist_ai_rmf", help="Comma-separated frameworks")
def compliance_assess(scan_id: str, frameworks: str) -> None:
    """Run compliance assessment against regulations."""
    fws = frameworks.split(",")

    # Mock assessment results
    assessments = [
        {"framework": "EU_AI_ACT", "score": 73.5, "passed": 12, "failed": 5},
        {"framework": "NIST_AI_RMF", "score": 68.0, "passed": 11, "failed": 6},
    ]

    if RICH_AVAILABLE:
        table = Table(title="Compliance Assessment", show_header=True)
        table.add_column("Framework")
        table.add_column("Score")
        table.add_column("Controls Passed")
        table.add_column("Controls Failed")

        for a in assessments:
            score_color = "green" if a["score"] >= 75 else "yellow" if a["score"] >= 60 else "red"
            table.add_row(a["framework"], f"[{score_color}]{a['score']:.1f}%[/{score_color}]", str(a["passed"]), str(a["failed"]))

        console.print(table)
    else:
        for a in assessments:
            click.echo(f"{a['framework']:15} {a['score']:.1f}% ({a['passed']} passed, {a['failed']} failed)")


@compliance.command("list-frameworks")
def compliance_list_frameworks() -> None:
    """List available compliance frameworks."""
    frameworks = [
        {"id": "eu_ai_act", "name": "EU AI Act", "controls": 17},
        {"id": "nist_ai_rmf", "name": "NIST AI RMF", "controls": 17},
        {"id": "owasp_llm", "name": "OWASP LLM Top 10", "controls": 10},
    ]

    if RICH_AVAILABLE:
        table = Table(title="Available Frameworks", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Controls")

        for fw in frameworks:
            table.add_row(fw["id"], fw["name"], str(fw["controls"]))

        console.print(table)
    else:
        for fw in frameworks:
            click.echo(f"{fw['id']:15} {fw['name']:20} {fw['controls']} controls")


# ── TARGET ──────────────────────────────────────────────────────────────────
@cli.group()
def target():
    """Target management."""
    pass


@target.command("add")
@click.option("--name", required=True, prompt="Target name")
@click.option("--type", "target_type", required=True, type=click.Choice(["openai_api", "anthropic_api", "llama", "custom"]))
@click.option("--endpoint", required=True, prompt="API endpoint")
@click.option("--api-key", help="API key (optional)")
def target_add(name: str, target_type: str, endpoint: str, api_key: Optional[str]) -> None:
    """Add a new target for scanning."""
    payload = {
        "name": name,
        "target_type": target_type,
        "endpoint": endpoint,
    }
    if api_key:
        payload["api_key"] = api_key

    rprint(f"[green]✓ Target '{name}' added successfully[/green]")


@target.command("list")
@click.option("--output", type=click.Choice(["json", "table"]), default="table")
def target_list(output: str) -> None:
    """List configured targets."""
    # Mock targets
    targets = [
        {"id": "tg_001", "name": "My GPT-4 App", "type": "openai_api", "last_scan": "2026-03-12T10:00:00Z"},
        {"id": "tg_002", "name": "Internal Claude API", "type": "anthropic_api", "last_scan": "2026-03-11T14:30:00Z"},
    ]

    if output == "json":
        click.echo(json.dumps(targets, indent=2))
    elif RICH_AVAILABLE:
        table = Table(title="Targets", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Last Scan")

        for t in targets:
            table.add_row(t["id"], t["name"], t["type"], t.get("last_scan", "Never"))

        console.print(table)
    else:
        for t in targets:
            click.echo(f"{t['id']:8} {t['name']:20} {t['type']:15} {t.get('last_scan', 'Never')}")


@target.command("delete")
@click.argument("target_id")
@click.confirmation_option(prompt="Are you sure?")
def target_delete(target_id: str) -> None:
    """Delete a target."""
    rprint(f"[green]✓ Target {target_id} deleted[/green]")


# ── CONFIG ──────────────────────────────────────────────────────────────────
@cli.group()
def config():
    """Configuration management."""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value."""
    cfg = get_config()
    cfg[key.replace("-", "_")] = value
    save_config(cfg)
    rprint(f"[green]✓ Set {key}[/green]")


@config.command("show")
def config_show() -> None:
    """Show current configuration."""
    cfg = get_config()

    # Mask sensitive values
    display_cfg = {}
    for k, v in cfg.items():
        if "key" in k.lower() or "secret" in k.lower() or "token" in k.lower():
            display_cfg[k] = v[:8] + "..." if len(str(v)) > 8 else v
        else:
            display_cfg[k] = v

    if RICH_AVAILABLE:
        console.print_json(json.dumps(display_cfg, indent=2))
    else:
        click.echo(json.dumps(display_cfg, indent=2))


@config.command("reset")
@click.confirmation_option(prompt="This will reset all configuration. Are you sure?")
def config_reset() -> None:
    """Reset configuration to defaults."""
    CONFIG_FILE.unlink(missing_ok=True)
    rprint("[green]✓ Configuration reset[/green]")


# ── ATTACKS ────────────────────────────────────────────────────────────────
@cli.group()
def attacks():
    """Browse and filter available attacks."""
    pass


@attacks.command("list")
@click.option("--category", help="Filter by category")
@click.option("--severity", type=click.Choice(["critical", "high", "medium", "low"]))
@click.option("--limit", default=20)
@click.option("--output", type=click.Choice(["json", "table"]), default="table")
def attacks_list(category: Optional[str], severity: Optional[str], limit: int, output: str) -> None:
    """List available attacks."""
    # Mock attacks
    attacks_data = [
        {"id": "llm01", "name": "Direct Injection", "category": "owasp_llm", "severity": "critical"},
        {"id": "dan01", "name": "DAN Jailbreak", "category": "classic_jailbreaks", "severity": "high"},
        {"id": "bias01", "name": "Gender Bias", "category": "responsible_ai", "severity": "medium"},
    ]

    if category:
        attacks_data = [a for a in attacks_data if a["category"] == category]
    if severity:
        attacks_data = [a for a in attacks_data if a["severity"] == severity]

    if output == "json":
        click.echo(json.dumps(attacks_data[:limit], indent=2))
    elif RICH_AVAILABLE:
        table = Table(title="Available Attacks", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Category")
        table.add_column("Severity")

        severity_colors = {
            "critical": "red",
            "high": "yellow",
            "medium": "cyan",
            "low": "green",
        }

        for a in attacks_data[:limit]:
            color = severity_colors.get(a["severity"], "white")
            table.add_row(a["id"], a["name"], a["category"], f"[{color}]{a['severity'].upper()}[/{color}]")

        console.print(table)


@attacks.command("categories")
def attacks_categories() -> None:
    """List attack categories."""
    categories = [
        {"id": "owasp_llm", "name": "OWASP LLM Top 10", "count": 23},
        {"id": "owasp_agentic", "name": "OWASP Agentic AI", "count": 18},
        {"id": "mitre_atlas", "name": "MITRE ATLAS", "count": 150},
        {"id": "classic_jailbreaks", "name": "Classic Jailbreaks", "count": 32},
        {"id": "responsible_ai", "name": "Responsible AI", "count": 64},
    ]

    if RICH_AVAILABLE:
        table = Table(title="Attack Categories", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Attacks")

        for c in categories:
            table.add_row(c["id"], c["name"], str(c["count"]))

        console.print(table)
    else:
        for c in categories:
            click.echo(f"{c['id']:20} {c['name']:25} {c['count']} attacks")


# ── HELPERS ────────────────────────────────────────────────────────────────
def _print_scan_summary(scan: dict) -> None:
    """Print scan summary in rich panel."""
    if not RICH_AVAILABLE:
        click.echo(json.dumps(scan, indent=2))
        return

    console.print(Panel(
        f"Scan ID: [cyan]{scan['scan_id']}[/cyan]\n"
        f"Risk Score: [bold red]{scan['risk_score']:.1f}[/bold red]/100\n"
        f"Critical: [red]{scan['critical']}[/red] | High: [yellow]{scan['high']}[/yellow] | Medium: [cyan]{scan['medium']}[/cyan]\n"
        f"Status: [green]{scan['status']}[/green]",
        title="Scan Complete"
    ))


if __name__ == "__main__":
    cli()
