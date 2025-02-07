"""Setup script for Spider Game."""

import sys
import os
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
    """Initialize Spider Game development environment.
    
    Args:
        force (bool): Force setup even if already initialized
    """
    ui = RichUI()
    ui.print_header("Spider Game Development Environment")

    if check_existing_setup() and not force:
        if activate_venv():
            ui.print_success("🔄 Using existing virtual environment")
        else:
            ui.print_error("❌ Failed to activate existing environment")
            return 1

    # Clone ML-agents repository using new git module
    success, error = clone_repository(
        ui=ui,
        url="https://github.com/Unity-Technologies/ml-agents.git",
        branch="develop",
        target_dir="ml-agents")

    if not success:
        ui.print_error(f"❌ Failed to clone ML-agents repository: {error}")
        return 1

    print("\n🕷️ Spiders Ready!")
    print("🎮 Run 'spider-game' to start training your spiders!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
