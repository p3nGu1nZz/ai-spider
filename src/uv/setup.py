"""Setup script for Spider Game."""

import sys
import os
import shutil
from pathlib import Path
from .ui import RichUI
from .git import clone_repository


def activate_venv() -> bool:
    """Attempt to activate existing virtual environment."""
    venv_path = Path(".venv")
    if not venv_path.exists():
        return False

    try:
        # Check if we're already in a venv
        if sys.prefix == sys.base_prefix:
            activate_script = "Scripts/activate.bat" if os.name == "nt" else "bin/activate"
            activate_path = venv_path / activate_script
            if activate_path.exists():
                os.system(str(activate_path))
        return True
    except Exception:
        return False


def check_existing_setup() -> bool:
    """Check if setup was already run."""
    venv_path = Path(".venv")
    mlagents_path = Path("ml-agents")
    return venv_path.exists() or mlagents_path.exists()


def main(force: bool = False) -> int:
    """Initialize Spider Game development environment."""
    ui = RichUI()
    ui.print_header("Spider Game Development Environment")

    # Activate venv if it exists
    if Path(".venv").exists():
        activate_venv()
        ui.print_success("🔄 Using virtual environment")

    # If force is true, remove existing ml-agents directory
    ml_agents_path = Path("ml-agents")
    if force and ml_agents_path.exists():
        ui.print_success("🔄 Removing existing ML-Agents repository...")
        shutil.rmtree(ml_agents_path, ignore_errors=True)

    # Always attempt clone if directory was removed or doesn't exist
    if not ml_agents_path.exists():
        success, error = clone_repository(
            ui=ui,
            url="https://github.com/Unity-Technologies/ml-agents.git",
            branch="develop",
            target_dir="ml-agents",
            force=False)

        if not success:
            ui.print_error("Failed to clone ML-agents repository:")
            print(f"\n{error}\n")
            return 1

        print("\n🕷️ Spiders Ready!")
        print("🎮 Run 'spider-game' to start training your spiders!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
