"""Audit trail commands."""

import httpx
import typer
from rich import print

from swarmsre.client import SwarmSREClient
from swarmsre.formatters import render_audit_table

app = typer.Typer(help="View forensic audit trails.")


@app.command("list")
def list_audit():
    """List all audit entries across the system."""
    client = SwarmSREClient()
    try:
        entries = client.list_audit()
        render_audit_table(entries)
    except Exception as e:
        print(f"[red]Error fetching audit trail:[/red] {e}")
        raise typer.Exit(1)
    finally:
        client.close()


@app.command("get")
def get_audit(incident_id: str = typer.Argument(..., help="The incident ID")):
    """Get the audit trail for a specific incident."""
    client = SwarmSREClient()
    try:
        entries = client.get_audit(incident_id)
        if not entries:
            print(f"[yellow]No audit entries found for incident '{incident_id}'.[/yellow]")
        else:
            render_audit_table(entries)
    except httpx.HTTPStatusError as e:
        print(f"[red]API Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        print(f"[red]Error fetching audit trail:[/red] {e}")
        raise typer.Exit(1)
    finally:
        client.close()
