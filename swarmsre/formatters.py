"""Rich formatters for terminal output."""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()

# ── Status helpers ──────────────────────────────────────────────────────

STATUS_STYLES = {
    "DETECTED": ("⚪", "white"),
    "INVESTIGATING": ("🔵", "blue"),
    "PROPOSED": ("🟡", "yellow"),
    "RESOLVED": ("🟢", "green"),
    "REJECTED": ("🟠", "dark_orange"),
    "FAILED": ("🔴", "red"),
}

AUDIT_ICONS = {
    "INCIDENT_CREATED": "📋",
    "INVESTIGATION_COMPLETED": "🔍",
    "PATCH_PROPOSED": "📝",
    "PATCH_APPROVED": "✅",
    "PATCH_REJECTED": "❌",
    "PATCH_EXECUTED": "🚀",
    "EVALUATION_COMPLETED": "📊",
}


def _status_badge(status: str) -> Text:
    icon, style = STATUS_STYLES.get(status, ("❓", "dim"))
    return Text(f"{icon} {status}", style=style)


# ── Incident formatters ────────────────────────────────────────────────

def render_incident_table(incidents: list[dict]) -> None:
    """Render a compact table of all incidents."""
    if not incidents:
        console.print("[dim]No incidents found.[/dim]")
        return

    table = Table(
        title="SwarmSRE Incidents",
        title_style="bold cyan",
        border_style="bright_black",
        show_lines=True,
    )
    table.add_column("ID", style="cyan", no_wrap=True, max_width=20)
    table.add_column("Title", style="white", ratio=2)
    table.add_column("Status", justify="center")
    table.add_column("Confidence", justify="center")
    table.add_column("Created", style="dim")

    for inc in incidents:
        inc_id = inc.get("id", "?")
        # Truncate long IDs for table readability
        short_id = inc_id[:16] + "…" if len(inc_id) > 16 else inc_id
        title = inc.get("title", "Unknown")
        status = inc.get("status", "UNKNOWN")
        confidence = inc.get("confidence_score")
        created = inc.get("created_at", "?")[:19]  # Trim to seconds

        conf_str = f"{confidence:.0%}" if confidence is not None else "—"
        badge = _status_badge(status)

        table.add_row(short_id, title, badge, conf_str, created)

    console.print(table)


def render_incident_detail(inc: dict) -> None:
    """Render a detailed panel for a single incident."""
    status = inc.get("status", "UNKNOWN")
    badge = _status_badge(status)

    # Header info
    header = Text.assemble(
        ("Incident: ", "bold"),
        (inc.get("id", "?"), "cyan"),
        ("\n"),
        ("Status:   ", "bold"),
        badge,
    )

    detail_lines = []
    detail_lines.append(f"[bold]Title:[/bold]      {inc.get('title', 'N/A')}")
    detail_lines.append(f"[bold]Source:[/bold]     {inc.get('source', 'N/A')}")
    detail_lines.append(f"[bold]Created:[/bold]    {inc.get('created_at', 'N/A')}")
    detail_lines.append(f"[bold]Updated:[/bold]    {inc.get('updated_at', 'N/A')}")

    confidence = inc.get("confidence_score")
    if confidence is not None:
        bar_len = int(confidence * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        detail_lines.append(f"[bold]Confidence:[/bold] [{bar}] {confidence:.0%}")

    detail_text = "\n".join(detail_lines)

    console.print(Panel(header, title="📋 Incident Detail", border_style="cyan"))
    console.print(Panel(detail_text, border_style="bright_black"))

    # Agent Trace
    evidence_chain = inc.get("evidence_chain", [])
    messages = [e.get("message") for e in evidence_chain if isinstance(e, dict) and "message" in e]

    if messages:
        trace_text = "\n".join([f"[dim]❯[/dim] [white]{m}[/white]" for m in messages])
        console.print(Panel(trace_text, title="🤖 Agent Trace", border_style="yellow"))

    # RCA Summary
    rca = inc.get("rca_summary")
    if rca:
        console.print(Panel(rca, title="🧠 Root Cause Analysis", border_style="yellow"))

    # Proposed Patch
    patch = inc.get("proposed_patch")
    if patch:
        syntax = Syntax(patch, "yaml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="🔧 Proposed Patch", border_style="green"))


# ── Audit formatters ───────────────────────────────────────────────────

def render_audit_table(entries: list[dict]) -> None:
    """Render the audit trail as a timeline table."""
    if not entries:
        console.print("[dim]No audit entries found.[/dim]")
        return

    table = Table(
        title="Audit Trail",
        title_style="bold magenta",
        border_style="bright_black",
        show_lines=True,
    )
    table.add_column("Timestamp", style="dim", no_wrap=True)
    table.add_column("Action", style="white")
    table.add_column("Actor", style="cyan")
    table.add_column("Incident", style="dim")

    for entry in entries:
        ts = entry.get("timestamp", "?")[:19]
        action = entry.get("action", "?")
        icon = AUDIT_ICONS.get(action, "•")
        actor = entry.get("actor", "system")
        inc_id = entry.get("incident_id", "?")
        short_id = inc_id[:16] + "…" if len(inc_id) > 16 else inc_id

        table.add_row(ts, f"{icon} {action}", actor, short_id)

    console.print(table)


# ── DORA Metrics formatter ─────────────────────────────────────────────

def render_dora_metrics(data: dict) -> None:
    """Render DORA metrics as a panel."""
    metrics = data.get("metrics", {})

    mttr = metrics.get("mean_time_to_recovery_seconds", 0)
    lead_time = metrics.get("lead_time_for_changes_seconds", 0)
    resolved = metrics.get("total_incidents_resolved", 0)
    patches = metrics.get("total_patches_executed", 0)

    def _fmt_duration(seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = seconds / 60
        return f"{minutes:.1f}m"

    lines = [
        f"[bold cyan]Mean Time to Recovery (MTTR):[/bold cyan]     {_fmt_duration(mttr)}",
        f"[bold cyan]Lead Time for Changes:[/bold cyan]            {_fmt_duration(lead_time)}",
        f"[bold cyan]Total Incidents Resolved:[/bold cyan]         {resolved}",
        f"[bold cyan]Total Patches Executed:[/bold cyan]           {patches}",
    ]

    console.print(Panel(
        "\n".join(lines),
        title="📊 DORA Metrics",
        border_style="magenta",
    ))


# ── WebSocket event formatter ──────────────────────────────────────────

def render_ws_event(event: dict) -> None:
    """Render a single WebSocket event inline."""
    event_type = event.get("type", "UNKNOWN")
    data = event.get("data", {})

    if event_type == "INCIDENT_CREATED":
        console.print(
            f"[bold green]▶ NEW[/bold green]  {data.get('title', '?')}  [dim]({data.get('id', '?')[:16]})[/dim]"
        )
    elif event_type == "INCIDENT_UPDATED":
        status = data.get("status", "?")
        badge = _status_badge(status)
        console.print(Text.assemble(
            ("▶ UPD  ", "bold yellow"),
            badge,
            ("  ", ""),
            (data.get("title", "?"), "white"),
            (f"  ({data.get('id', '?')[:16]})", "dim"),
        ))
    elif event_type == "INCIDENT_FAILED":
        console.print(
            f"[bold red]▶ FAIL[/bold red] {data.get('title', '?')}  [dim]error={data.get('error', '?')}[/dim]"
        )
    else:
        console.print(f"[dim]▶ {event_type}[/dim]")
