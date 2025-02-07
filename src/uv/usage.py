"""CLI usage and help text for the Spider Game project."""

from typing import List

__version__ = "0.0.1"
__author__ = "p3nGu1nZz"
__copyright__ = "Copyright (c) 2025 p3nGu1nZz"
__license__ = "MIT"


def get_command_list() -> List[str]:
    """Get list of available commands."""
    return ["  setup        Setup Python environment and dependencies"]


def print_usage() -> None:
    """Print usage information for the Spider Game CLI."""
    print("Unity ML Agents Spider: An AI-powered game project")
    print()
    print("Usage: spider-game <COMMAND> <ARGS>")
    print()
    print("Commands:")
    for cmd in get_command_list():
        print(cmd)
    print()
    print(
        "For more information, visit: https://github.com/p3nGu1nZz/ai-spider")
    print()


def print_next_steps() -> None:
    """Print next steps after setup completion."""
    print("\nSetup complete! Next steps:")
    print("1. Install the com.unity.ml-agents package in Unity")
    print("2. Import the Spider Agent from Package Manager")
    print("3. Start training: spider-game train --config configs/spider.yaml")


__all__ = ['print_usage', 'print_next_steps', 'get_command_list']
