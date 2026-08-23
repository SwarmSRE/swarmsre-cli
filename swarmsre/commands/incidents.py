"""Incidents commands."""

import asyncio
import json

import httpx
import typer
import websockets
from rich import print

from swarmsre.client import SwarmSREClient
from swarmsre.formatters import render_incident_detail, render_incident_table, render_ws_event

app = typer.Typer(help="Manage and observe incidents (HITL).")


@app.command("list")
def list_incidents():
    """List all incidents."""
    client = SwarmSREClient()
    try:
        incidents = client.list_incidents()
        render_incident_table(incidents)
    except httpx.ConnectError:
        print(f"[red]Connection Error:[/red] Cannot connect to control plane at {client.base_url}. Is the backend running?")
        raise typer.Exit(1)
    except Exception as e:
        print(f"[red]Error fetching incidents:[/red] {type(e).__name__}: {e}")
        raise typer.Exit(1)
    finally:
        client.close()


@app.command("get")
def get_incident(incident_id: str = typer.Argument(..., help="The incident ID")):
    """Get details for a specific incident."""
    client = SwarmSREClient()
    try:
        inc = client.get_incident(incident_id)
        render_incident_detail(inc)
    except httpx.ConnectError:
        print(f"[red]Connection Error:[/red] Cannot connect to control plane at {client.base_url}. Is the backend running?")
        raise typer.Exit(1)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"[red]Incident '{incident_id}' not found.[/red]")
        else:
            print(f"[red]API Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        print(f"[red]Error fetching incident:[/red] {type(e).__name__}: {e}")
        raise typer.Exit(1)
    finally:
        client.close()


@app.command("approve")
def approve_incident(incident_id: str = typer.Argument(..., help="The incident ID to approve")):
    """Approve a proposed patch (HITL)."""
    client = SwarmSREClient()
    try:
        inc = client.approve_incident(incident_id)
        print(f"[bold green]✅ Approved![/bold green] Patch for incident [cyan]{incident_id}[/cyan] is now being executed.")
    except httpx.ConnectError:
        print(f"[red]Connection Error:[/red] Cannot connect to control plane at {client.base_url}. Is the backend running?")
        raise typer.Exit(1)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            print(f"[red]Validation Error:[/red] {e.response.json().get('detail', 'Cannot approve this incident.')}")
        else:
            print(f"[red]API Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        print(f"[red]Error approving incident:[/red] {type(e).__name__}: {e}")
        raise typer.Exit(1)
    finally:
        client.close()


@app.command("reject")
def reject_incident(incident_id: str = typer.Argument(..., help="The incident ID to reject")):
    """Reject a proposed patch (HITL)."""
    client = SwarmSREClient()
    try:
        inc = client.reject_incident(incident_id)
        print(f"[bold orange]❌ Rejected.[/bold orange] Patch for incident [cyan]{incident_id}[/cyan] was rejected.")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            print(f"[red]Validation Error:[/red] {e.response.json().get('detail', 'Cannot reject this incident.')}")
        else:
            print(f"[red]API Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        print(f"[red]Error rejecting incident:[/red] {e}")
        raise typer.Exit(1)
    finally:
        client.close()


async def _watch(ws_url: str):
    """Async inner function for WebSocket connection."""
    print(f"[dim]Connecting to {ws_url}...[/dim]")
    try:
        async with websockets.connect(ws_url) as ws:
            print("[bold green]Connected![/bold green] Listening for live events... (Press Ctrl+C to stop)\n")
            while True:
                msg = await ws.recv()
                try:
                    event = json.loads(msg)
                    render_ws_event(event)
                except json.JSONDecodeError:
                    print(f"[dim]Received raw text:[/dim] {msg}")
    except asyncio.CancelledError:
        print("\n[dim]Disconnected.[/dim]")
    except Exception as e:
        print(f"\n[red]WebSocket error:[/red] {e}")


@app.command("watch")
def watch_incidents():
    """Live-tail incident events via WebSocket."""
    client = SwarmSREClient()
    ws_url = client.ws_url()
    client.close()
    
    try:
        asyncio.run(_watch(ws_url))
    except KeyboardInterrupt:
        print("\n[dim]Exiting watch mode.[/dim]")
