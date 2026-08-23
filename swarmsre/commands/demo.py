"""Demo automation commands."""

import subprocess
import typer
from rich import print

app = typer.Typer(help="Manage local demo scenarios.")


@app.command("inject")
def inject_chaos(scenario: str = typer.Argument("crash-loop", help="Scenario to inject (crash-loop, oom-kill)")):
    """Inject chaos into the local SwarmSRE demo environment."""
    if scenario not in ["crash-loop", "oom-kill"]:
        print(f"[red]Unknown scenario '{scenario}'. Use 'crash-loop' or 'oom-kill'.[/red]")
        raise typer.Exit(1)

    print(f"[cyan]Injecting scenario:[/cyan] [bold]{scenario}[/bold]")
    # Run the demo script using subprocess
    try:
        subprocess.run(
            ["bash", "../swarmsre-demo/scripts/inject-faults.sh", scenario],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[bold red]Injection failed with exit code {e.returncode}[/bold red]")
        raise typer.Exit(e.returncode)
    except FileNotFoundError:
        print("[red]Could not find inject script. Are you running this near the swarmsre-demo repo?[/red]")
        raise typer.Exit(1)


@app.command("reset")
def reset_demo():
    """Reset the local SwarmSRE demo environment."""
    print("[cyan]Resetting demo environment...[/cyan]")
    try:
        subprocess.run(
            ["bash", "../swarmsre-demo/scripts/reset-demo.sh"],
            check=True
        )
        print("[bold green]✅ Reset complete![/bold green]")
    except subprocess.CalledProcessError as e:
        print(f"[bold red]Reset failed with exit code {e.returncode}[/bold red]")
        raise typer.Exit(e.returncode)
    except FileNotFoundError:
        print("[red]Could not find reset script. Are you running this near the swarmsre-demo repo?[/red]")
        raise typer.Exit(1)
