"""Main entry point for the SwarmSRE CLI."""

import typer

from swarmsre import __version__
from swarmsre.commands import audit, demo, health, incidents, metrics

app = typer.Typer(
    name="swarmsre",
    help="SwarmSRE CLI — AI-powered SRE platform",
    no_args_is_help=True,
)

# Register subcommands
app.add_typer(incidents.app, name="incidents")
app.add_typer(audit.app, name="audit")
app.add_typer(metrics.app, name="metrics")
app.add_typer(demo.app, name="demo")
app.add_typer(health.app, name="health", hidden=True)  # registered health as a command in itself but we can also use `swarmsre health` directly
app.command("health")(health.health) # Expose health as a direct command


def version_callback(value: bool):
    if value:
        typer.echo(f"SwarmSRE CLI version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
):
    """
    SwarmSRE Control Plane CLI.
    """
    pass


if __name__ == "__main__":
    app()
