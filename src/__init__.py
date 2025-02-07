"""Spider Game root package."""

from .main import cli as main  # Alias cli to main for compatibility
from .uv.setup import main as setup

__all__ = ["main", "setup"]