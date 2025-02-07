"""Spider Game CLI entry point."""
import click
from .uv.setup import main as setup_cmd


@click.group()
def cli():
    """Spider Game - Unity ML Agents powered spider simulation."""


@cli.command()
@click.option('--force',
              is_flag=True,
              help='Force setup even if already initialized')
def setup(force):
    """Set up development environment."""
    setup_cmd(force=force)


@cli.command()
def train():
    """Train spider agents."""
    print("Training not implemented yet!")


# Make cli available at module level
if __name__ == "__main__":
    cli()
