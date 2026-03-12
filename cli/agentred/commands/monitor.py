"""AgentRed CLI: Real-time monitoring and alerting."""
import click
from typing import Optional


@click.group()
def monitor():
    """Monitor AI agents in real-time."""
    pass


@monitor.command(name="start")
@click.option("--agent-id", required=True, help="Agent UUID to monitor")
@click.option("--config", type=click.Path(exists=True), help="Monitor config file")
@click.option("--webhook", help="Webhook URL for alerts")
def start_monitoring(agent_id: str, config: Optional[str], webhook: Optional[str]):
    """Start real-time monitoring of an agent.

    Example:
        agentred monitor start --agent-id abc123 --webhook https://hooks.slack.com/...
    """
    from ..cli import api_call, rprint

    try:
        payload = {
            "agent_id": agent_id,
            "webhook_url": webhook
        }

        if config:
            import json
            with open(config) as f:
                payload["config"] = json.load(f)

        result = api_call("POST", "/api/v1/monitoring/start", data=payload)
        monitor_id = result.get("id")

        rprint(f"[green]Monitoring started:[/green] {monitor_id}")
        rprint(f"[cyan]Agent ID:[/cyan] {agent_id}")

        if webhook:
            rprint(f"[cyan]Webhook:[/cyan] {webhook}")

        rprint("[yellow]Press Ctrl+C to stop[/yellow]")

        # Keep running and stream events
        import asyncio
        import httpx

        async def stream_events():
            from ..cli import get_api_client
            _, api_key = get_api_client()
            headers = {"Authorization": f"Bearer {api_key}"}

            async with httpx.AsyncClient() as client:
                async with client.stream("GET", f"https://api.agentred.io/api/v1/monitoring/{monitor_id}/events", headers=headers) as r:
                    async for line in r.aiter_lines():
                        if line:
                            try:
                                import json as json_lib
                                event = json_lib.loads(line)
                                event_type = event.get("type", "unknown")

                                if event_type == "anomaly":
                                    rprint(f"[red][ANOMALY][/red] {event.get('message')}")
                                elif event_type == "alert":
                                    rprint(f"[yellow][ALERT][/yellow] {event.get('message')}")
                                else:
                                    rprint(f"[cyan][{event_type.upper()}][/cyan] {event.get('message')}")
                            except:
                                pass

        try:
            asyncio.run(stream_events())
        except KeyboardInterrupt:
            rprint("[yellow]Monitoring stopped[/yellow]")
            api_call("POST", f"/api/v1/monitoring/{monitor_id}/stop")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@monitor.command(name="status")
@click.argument("monitor_id")
def monitor_status(monitor_id: str):
    """Get monitoring status."""
    from ..cli import api_call, rprint

    try:
        result = api_call("GET", f"/api/v1/monitoring/{monitor_id}")

        rprint(f"[bold]Monitor ID:[/bold] {result.get('id')}")
        rprint(f"[bold]Agent:[/bold] {result.get('agent_id')}")
        rprint(f"[bold]Status:[/bold] {result.get('status')}")
        rprint(f"[bold]Events:[/bold] {result.get('event_count', 0)}")
        rprint(f"[bold]Anomalies:[/bold] {result.get('anomaly_count', 0)}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@monitor.command(name="events")
@click.option("--monitor-id", required=True, help="Monitor ID")
@click.option("--type", type=click.Choice(["all", "anomaly", "alert", "behavior"]), default="all")
@click.option("--limit", type=int, default=50)
def monitor_events(monitor_id: str, type: str, limit: int):
    """View monitoring events."""
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        params = {"limit": limit}
        if type != "all":
            params["type"] = type

        result = api_call("GET", f"/api/v1/monitoring/{monitor_id}/events", params=params)
        events = result.get("events", [])

        if not events:
            rprint("[yellow]No events found[/yellow]")
            return

        if console:
            table = Table(title="Monitoring Events")
            table.add_column("Timestamp", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Severity", style="yellow")
            table.add_column("Message", style="white")

            for event in events:
                severity = event.get("severity", "info")
                severity_color = "red" if severity == "high" else "yellow" if severity == "medium" else "green"

                table.add_row(
                    event.get("timestamp", "")[:16],
                    event.get("type", ""),
                    f"[{severity_color}]{severity}[/{severity_color}]",
                    event.get("message", "")[:50]
                )

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@monitor.command(name="kill")
@click.argument("agent_id")
@click.confirmation_option(prompt="Are you sure you want to kill-switch this agent?")
def kill_switch(agent_id: str):
    """Emergency kill-switch for an agent."""
    from ..cli import api_call, rprint

    try:
        result = api_call("POST", f"/api/v1/monitoring/{agent_id}/kill-switch")
        rprint(f"[red][CRITICAL] Agent {agent_id[:8]} has been emergency-stopped[/red]")
        rprint(f"[yellow]Reason: {result.get('message')}[/yellow]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@monitor.command(name="list")
@click.option("--status", type=click.Choice(["active", "stopped", "paused"]))
def list_monitors(status: Optional[str]):
    """List active monitors."""
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        params = {}
        if status:
            params["status"] = status

        result = api_call("GET", "/api/v1/monitoring", params=params)
        monitors = result.get("monitors", [])

        if not monitors:
            rprint("[yellow]No active monitors[/yellow]")
            return

        if console:
            table = Table(title="Active Monitors")
            table.add_column("ID", style="cyan")
            table.add_column("Agent", style="magenta")
            table.add_column("Status", style="yellow")
            table.add_column("Events", style="green")

            for monitor in monitors:
                table.add_row(
                    monitor.get("id", "")[:8],
                    monitor.get("agent_id", "")[:8],
                    monitor.get("status", ""),
                    str(monitor.get("event_count", 0))
                )

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")
