"""AgentRed CLI: Authentication and configuration."""
import click
from typing import Optional
import json
from pathlib import Path


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


@click.group()
def auth():
    """Manage authentication and API keys."""
    pass


@auth.command(name="login")
@click.option("--api-key", prompt=True, hide_input=True, help="AgentRed API key")
@click.option("--api-url", default="https://api.agentred.io", help="API URL (default: production)")
def login(api_key: str, api_url: str):
    """Authenticate with AgentRed API.

    Example:
        agentred auth login
    """
    from ..cli import rprint

    config = get_config()
    config["api_key"] = api_key
    config["api_url"] = api_url
    save_config(config)

    rprint(f"[green]Authenticated successfully[/green]")
    rprint(f"[cyan]API URL:[/cyan] {api_url}")


@auth.command(name="logout")
def logout():
    """Clear stored authentication."""
    from ..cli import rprint

    config = get_config()
    config.pop("api_key", None)
    config.pop("api_url", None)
    save_config(config)

    rprint("[green]Logged out successfully[/green]")
    CONFIG_FILE.unlink(missing_ok=True)


@auth.command(name="status")
def auth_status():
    """Check authentication status."""
    from ..cli import rprint

    config = get_config()
    api_key = config.get("api_key")
    api_url = config.get("api_url", "https://api.agentred.io")

    if not api_key:
        rprint("[yellow]Not authenticated[/yellow]")
        rprint("[cyan]Run:[/cyan] agentred auth login")
        return

    rprint("[green]Authenticated[/green]")
    rprint(f"[cyan]API URL:[/cyan] {api_url}")
    rprint(f"[cyan]API Key:[/cyan] {api_key[:10]}***")


@auth.command(name="api-keys")
def list_api_keys():
    """List API keys (via API call to backend).

    Requires authentication.
    """
    from ..cli import api_call, rprint, console
    from rich.table import Table

    try:
        result = api_call("GET", "/api/v1/auth/api-keys")
        api_keys = result.get("api_keys", [])

        if not api_keys:
            rprint("[yellow]No API keys created[/yellow]")
            return

        if console:
            table = Table(title="API Keys")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Scopes", style="yellow")
            table.add_column("Created", style="green")

            for key in api_keys:
                table.add_row(
                    key.get("id", "")[:8],
                    key.get("name", ""),
                    ", ".join(key.get("scopes", [])),
                    key.get("created_at", "")[:10]
                )

            console.print(table)

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@auth.command(name="create-key")
@click.option("--name", prompt=True, help="Key name")
@click.option("--scopes", multiple=True, default=["scans:read", "scans:write"], help="Key scopes")
def create_api_key(name: str, scopes: tuple):
    """Create a new API key.

    Example:
        agentred auth create-key --name "CI/CD Pipeline"
    """
    from ..cli import api_call, rprint

    try:
        payload = {
            "name": name,
            "scopes": list(scopes)
        }

        result = api_call("POST", "/api/v1/auth/api-keys", data=payload)
        api_key = result.get("api_key")
        key_id = result.get("id")

        rprint(f"[green]API Key created:[/green]")
        rprint(f"[bold]ID:[/bold] {key_id}")
        rprint(f"[bold]Key:[/bold] {api_key}")
        rprint("[yellow]Save this key securely. You won't be able to view it again.[/yellow]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@auth.command(name="delete-key")
@click.argument("key_id")
@click.confirmation_option(prompt="Are you sure you want to delete this API key?")
def delete_api_key(key_id: str):
    """Delete an API key."""
    from ..cli import api_call, rprint

    try:
        api_call("DELETE", f"/api/v1/auth/api-keys/{key_id}")
        rprint(f"[green]API Key {key_id[:8]} deleted[/green]")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@auth.command(name="me")
def get_current_user():
    """Get current authenticated user info."""
    from ..cli import api_call, rprint

    try:
        result = api_call("GET", "/api/v1/auth/me")

        user = result.get("user", {})
        org = result.get("organization", {})

        rprint(f"[bold]User:[/bold] {user.get('email')}")
        rprint(f"[bold]Name:[/bold] {user.get('first_name')} {user.get('last_name')}")
        rprint(f"[bold]Organization:[/bold] {org.get('name')}")
        rprint(f"[bold]Role:[/bold] {user.get('role')}")

    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@auth.command(name="config")
@click.argument("key")
@click.argument("value", required=False)
def manage_config(key: str, value: Optional[str]):
    """Get or set configuration values.

    Example:
        agentred auth config api_url https://staging.agentred.io
        agentred auth config api_url
    """
    from ..cli import rprint

    config = get_config()

    if value is None:
        # Get config value
        val = config.get(key, "[not set]")
        rprint(f"[cyan]{key}:[/cyan] {val}")
    else:
        # Set config value
        config[key] = value
        save_config(config)
        rprint(f"[green]Set {key} = {value}[/green]")
