"""Rich UI components for the setup script."""

# Standard library imports
from typing import Any, Optional, Type, Generator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
import sys
import subprocess
from pathlib import Path
from importlib import reload

__version__ = "0.0.1"
__author__ = "p3nGu1nZz"
__copyright__ = "Copyright (c) 2025 p3nGu1nZz"
__license__ = "MIT"

# Optional rich components with type safety
RichProgress: Optional[Type[Any]] = None
RichConsole: Optional[Type[Any]] = None
RichPanel: Optional[Type[Any]] = None
RichSpinner: Optional[Type[Any]] = None
RichText: Optional[Type[Any]] = None
HAS_RICH = False

# Try importing Rich, but don't fail if not available
try:
    from rich.progress import Progress as RichProgress # type: ignore
    from rich.progress import SpinnerColumn as RichSpinner # type: ignore
    from rich.progress import TextColumn as RichText # type: ignore
    from rich.console import Console as RichConsole # type: ignore
    from rich.panel import Panel as RichPanel # type: ignore
    HAS_RICH = True
except ImportError:
    pass


@dataclass
class Progress:
    # Type-safe container for progress tracking
    progress: Any
    task: Optional[Any] = None


class RichUI:
    """UI manager with rich formatting and fallback capabilities."""

    @staticmethod
    def _install_rich() -> bool:
        """Install Rich package if not present."""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "rich>=10.0.0"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def __init__(self) -> None:
        """Initialize UI with Rich if available, or install it first."""
        global HAS_RICH, RichConsole
        self._console = None
        self._has_error = False

        if not HAS_RICH:
            print("Installing Rich console for better UI...")
            if self._install_rich():
                # Reload this module to get Rich imports
                reload(sys.modules[__name__])
                from rich.console import Console as RichConsole  # type: ignore
                HAS_RICH = True

        self._console = RichConsole() if HAS_RICH else None

    def print_header(self, text: str) -> None:
        # Display bordered header with title if rich is available
        if HAS_RICH and RichPanel and self._console:
            self._console.print()  # Add empty line before panel
            self._console.print(
                RichPanel.fit(text,
                              border_style="blue",
                              padding=(1, 2),
                              title="AI Spider Setup"))
        else:
            print(f"\n{text}\n")

    def print_error(self, text: str) -> None:
        # Display error messages in red if rich is available
        if HAS_RICH and self._console:
            self._console.print(f"[red]Error:[/red] {text}")
        else:
            print(f"Error: {text}")

    @contextmanager
    def progress(self) -> Generator[Progress, None, None]:
        # Create progress context with spinner and text
        if HAS_RICH and RichProgress and RichSpinner and RichText:
            progress = RichProgress(
                RichSpinner(),
                RichText("[progress.description]{task.description}"),
                console=self._console,
            )
            with progress:
                yield Progress(progress=progress)
        else:
            with suppress():
                yield Progress(progress=None)

    def create_task(self,
                    progress: Progress,
                    description: str,
                    total: Optional[int] = None) -> Progress:
        # Add new task to progress tracking
        if HAS_RICH and progress.progress:
            task = progress.progress.add_task(description, total=total)
            progress.task = task
            return progress
        return Progress(progress=None)

    def update_task(self,
                    progress: Progress,
                    advance: bool = False,
                    **kwargs) -> None:
        # Update task progress or advance step
        if HAS_RICH and progress.progress and progress.task is not None:
            if advance:
                progress.progress.advance(progress.task)
            else:
                progress.progress.update(progress.task, **kwargs)

    def complete_task(self, progress: Progress) -> None:
        # Mark task as finished
        if progress.task is not None:
            self.update_task(progress, completed=True)
