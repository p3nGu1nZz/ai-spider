"""Setup script for Spider Game."""

import sys
from .ui import RichUI


def main() -> int:
    """Initialize Spider Game development environment."""
    ui = RichUI()
    ui.print_header("Spider Game Development Environment")
    print("\nSpiders Ready! 🕷️")
    print("Run 'uv run spider-game' to start training your spiders!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
