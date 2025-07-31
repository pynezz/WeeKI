"""Command-line interface for WeeKI."""

import asyncio
import click
import uvicorn

from .config import settings


@click.group()
def main():
    """WeeKI - Wee, Kunstig Intelligens.
    
    AI Agent Orchestration System CLI.
    """
    pass


@main.command()
@click.option("--host", default=None, help="Host to bind to")
@click.option("--port", default=None, type=int, help="Port to bind to")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host, port, debug, reload):
    """Start the WeeKI server."""
    # Override settings if provided
    if host:
        settings.host = host
    if port:
        settings.port = port
    if debug:
        settings.debug = debug
    
    click.echo(f"Starting WeeKI server on {settings.host}:{settings.port}")
    click.echo(f"Debug mode: {settings.debug}")
    click.echo(f"API docs available at: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "weeki.server:app",
        host=settings.host,
        port=settings.port,
        reload=reload or settings.debug,
        log_level=settings.log_level.lower()
    )


@main.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"WeeKI version {__version__}")


@main.command()
def config():
    """Show current configuration."""
    click.echo("Current WeeKI Configuration:")
    click.echo(f"  Host: {settings.host}")
    click.echo(f"  Port: {settings.port}")
    click.echo(f"  Debug: {settings.debug}")
    click.echo(f"  Database URL: {settings.database_url}")
    click.echo(f"  Max Agents: {settings.max_agents}")
    click.echo(f"  Agent Timeout: {settings.agent_timeout}s")
    click.echo(f"  Log Level: {settings.log_level}")


if __name__ == "__main__":
    main()