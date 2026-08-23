"""Metrics commands."""

import typer
from rich import print

from swarmsre.client import SwarmSREClient
from swarmsre.formatters import render_dora_metrics

app = typer.Typer(help="View DORA and system metrics.")


@app.command("dora")
def get_dora():
    """Show DORA metrics (MTTR, Lead Time)."""
    client = SwarmSREClient()
    try:
        data = client.get_dora_metrics()
        render_dora_metrics(data)
    except httpx.ConnectError:
        print(f"[red]Connection Error:[/red] Cannot connect to control plane at {client.base_url}. Is the backend running?")
        raise typer.Exit(1)
    except Exception as e:
        print(f"[red]Error fetching metrics:[/red] {type(e).__name__}: {e}")
        raise typer.Exit(1)
    finally:
        client.close()
