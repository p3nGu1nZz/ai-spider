"""Setup script for Spider Game."""

import sys
from pathlib import Path
from .ui import RichUI
from .git import clone_repository


def check_existing_setup() -> bool:
    """Check if setup was already run."""
    venv_path = Path(".venv")
    mlagents_path = Path("ml-agents")
    return venv_path.exists() or mlagents_path.exists()


def main() -> int:
    """Initialize Spider Game development environment."""
    ui = RichUI()
    ui.print_header("Spider Game Development Environment")

    if check_existing_setup():
        if not ui.confirm(
                "Existing setup detected. Do you want to reinstall?"):
            print("\nSetup cancelled. Using existing environment.")
            return 0

    # Clone ML-agents repository using new git module
    success, error = clone_repository(
        ui=ui,
        url="https://github.com/Unity-Technologies/ml-agents.git",
        branch="develop",
        target_dir="ml-agents")

    if not success:
        ui.print_error(f"Failed to clone ML-agents repository: {error}")
        return 1

    print("\nSpiders Ready! 🕷️")
    print("Run 'uv run spider-game' to start training your spiders!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
