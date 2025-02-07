"""Spider Game CLI entry point."""
import click
from .uv.setup import main as setup_cmd


@click.group()
def cli():
    """Spider Game - Unity ML Agents powered spider simulation."""


@cli.command()
def setup():
    """Set up development environment."""
    setup_cmd()


@cli.command()
def train():
    """Train spider agents."""
    print("Training not implemented yet!")


# Make cli available at module level
if __name__ == "__main__":
    cli()
