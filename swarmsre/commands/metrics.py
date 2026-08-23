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
    except Exception as e:
        print(f"[red]Error fetching metrics:[/red] {e}")
        raise typer.Exit(1)
    finally:
        client.close()
