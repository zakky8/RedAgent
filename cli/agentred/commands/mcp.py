"""AgentRed CLI: MCP (Model Context Protocol) security scanning."""
import click
from typing import Optional


@click.group()
def mcp():
    """Scan MCP servers and protocols for security issues."""
    pass


@mcp.command(name="scan")
@click.option("--server-url", required=True, help="MCP server URL to scan")
@click.option("--auth-token", help="Authentication token for private servers")
@click.option("--deep", is_flag=True, help="Run deep security analysis")
@click.option("--output", type=click.Path(), help="Save results to JSON")
def scan_mcp_server(server_url: str, auth_token: Optional[str], deep: bool, output: Optional[str]):
    """Scan an MCP server for vulnerabilities.

    Example:
        agentred mcp scan --server-url http://localhost:3000 --deep
    """
    from ..cli import api_call, rprint
    import json

    try:
        payload = {
            "server_url": server_url,
            "deep_scan": deep
        }

        if auth_token:
            payload["auth_token"] = auth_token

        rprint("[cyan]Scanning MCP server...[/cyan]")
        result = api_call("POST", "/api/v1/mcp/scan", data=payload)

        vulnerabilities = result.get("vulnerabilities", [])
        rprint(f"[green]Scan completed:[/green] Found {len(vulnerabilities)} issues")

        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

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

            rprint(f"  [{severity_color}]{severity.upper()}[/{severity_color}] {vuln.get('name')}")

        rprint("")
        rprint(f"[bold]Summary:[/bold]")
        rprint(f"  Critical: [red]{severity_counts['critical']}[/red]")
        rprint(f"  High: [red]{severity_counts['high']}[/red]")
        rprint(f"  Medium: [yellow]{severity_counts['medium']}[/yellow]")
        rprint(f"  Low: [green]{severity_counts['low']}[/green]")

        if output:
            with open(output, "w") as f:
                json.dump(result, f, indent=2)
            rprint(f"[green]Results saved to:[/green] {output}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@mcp.command(name="scan-repo")
@click.option("--repo-url", required=True, help="GitHub repo URL with MCP server code")
@click.option("--branch", default="main", help="Branch to scan")
@click.option("--output", type=click.Path(), help="Save results to JSON")
def scan_mcp_repo(repo_url: str, branch: str, output: Optional[str]):
    """Scan an MCP server repository for security issues in code.

    Example:
        agentred mcp scan-repo --repo-url https://github.com/user/mcp-server
    """
    from ..cli import api_call, rprint
    import json

    try:
        payload = {
            "repo_url": repo_url,
            "branch": branch
        }

        rprint("[cyan]Cloning and analyzing repository...[/cyan]")
        result = api_call("POST", "/api/v1/mcp/scan-repo", data=payload)

        issues = result.get("issues", [])
        rprint(f"[green]Analysis completed:[/green] Found {len(issues)} code issues")

        categories = {}
        for issue in issues:
            cat = issue.get("category", "other")
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1

            rprint(f"  [{issue.get('type')}] {issue.get('message')}")
            rprint(f"    File: {issue.get('file')}:{issue.get('line')}")

        if output:
            with open(output, "w") as f:
                json.dump(result, f, indent=2)
            rprint(f"[green]Results saved to:[/green] {output}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@mcp.command(name="list-tools")
@click.option("--server-url", required=True, help="MCP server URL")
def list_mcp_tools(server_url: str):
    """List all tools exposed by an MCP server."""
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        result = api_call("GET", "/api/v1/mcp/tools", params={"server_url": server_url})
        tools = result.get("tools", [])

        if not tools:
            rprint("[yellow]No tools found[/yellow]")
            return

        if console:
            table = Table(title="MCP Server Tools")
            table.add_column("Name", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Risk", style="yellow")

            for tool in tools:
                risk = tool.get("risk_level", "medium")
                risk_color = "red" if risk == "high" else "yellow" if risk == "medium" else "green"

                table.add_row(
                    tool.get("name", ""),
                    tool.get("description", "")[:40],
                    f"[{risk_color}]{risk}[/{risk_color}]"
                )

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@mcp.command(name="test-injection")
@click.option("--server-url", required=True, help="MCP server URL")
@click.option("--tool-name", required=True, help="Tool to test")
@click.option("--payload", required=True, help="Injection payload to test")
def test_mcp_injection(server_url: str, tool_name: str, payload: str):
    """Test an MCP tool for prompt injection vulnerabilities."""
    from ..cli import api_call, rprint

    try:
        result = api_call("POST", "/api/v1/mcp/test-injection", data={
            "server_url": server_url,
            "tool_name": tool_name,
            "payload": payload
        })

        vulnerable = result.get("vulnerable", False)

        if vulnerable:
            rprint(f"[red][VULNERABLE][/red] Tool accepts injection")
            rprint(f"  Evidence: {result.get('evidence')}")
        else:
            rprint(f"[green][SAFE][/green] Tool appears resistant to injection")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
