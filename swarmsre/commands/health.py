"""Health check command."""

import typer
from httpx import RequestError
from rich import print

from swarmsre.client import SwarmSREClient

app = typer.Typer(help="Check control plane health.")


@app.callback(invoke_without_command=True)
def health():
    """Check the health of the SwarmSRE Control Plane."""
    client = SwarmSREClient()
    try:
        data = client.health()
        print(f"[bold green]✅ Health check passed![/bold green] Control plane is reachable at {client.base_url}")
        print(f"Status: {data.get('status', 'unknown')} | Component: {data.get('component', 'unknown')}")
        if "llm" in data:
            llm = data["llm"]
            print(f"  Orchestrator: [cyan]{llm.get('orchestrator_provider', '?')}[/cyan] / {llm.get('orchestrator_model', '?')}")
            print(f"  Worker:       [cyan]{llm.get('worker_provider', '?')}[/cyan] / {llm.get('worker_model', '?')}")
    except RequestError as e:
        print(f"[bold red]❌ Health check failed![/bold red] Cannot connect to control plane at {client.base_url}")
        print(f"Details: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print("[bold red]❌ Health check failed![/bold red]")
        print(f"Details: {e}")
        raise typer.Exit(code=1)
    finally:
        client.close()
