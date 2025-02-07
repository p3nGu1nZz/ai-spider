"""Unity ML-Agents Spider Game UV Package.

Core functionality:
- Environment setup and virtual environment management
- Rich console UI with automatic installation
- Basic CLI commands:
  * setup: Create and configure Python environment
  * train: Train ML agents (coming soon)
"""

from .ui import RichUI, Progress
from .setup import main as setup
from .usage import print_usage, print_next_steps

__version__ = "0.0.1"
__author__ = "p3nGu1nZz"
__copyright__ = "Copyright (c) 2025 p3nGu1nZz"
__license__ = "MIT"

# Core functionality
__all__ = [
    # UI Components
    "RichUI",
    "Progress",
    
    # Core Functions
    "setup",
    "print_usage",
    "print_next_steps",
]
