"""Rich UI components for the setup script."""

# Standard library imports
from typing import Any, Optional, Type, Generator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
import sys
import subprocess
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
    from rich.progress import Progress as RichProgress  # type: ignore
    from rich.progress import SpinnerColumn as RichSpinner  # type: ignore
    from rich.progress import TextColumn as RichText  # type: ignore
    from rich.console import Console  # type: ignore
    from rich.panel import Panel as RichPanel  # type: ignore
    RichConsole = Console
    HAS_RICH = True
except ImportError:
    pass


@dataclass
class Progress:
    """Type-safe container for progress tracking."""

    progress: Any
    task: Optional[Any] = None


class RichUI:
    """UI manager with rich formatting and fallback capabilities."""

    def __init__(self) -> None:
        """Initialize UI with Rich if available, or install it first."""
        self._console = None
        self._has_error = False

        if not HAS_RICH and self._install_rich():
            # Reload this module to get Rich imports
            reload(sys.modules[__name__])

        if HAS_RICH and RichConsole is not None:
            self._console = RichConsole()

    @staticmethod
    def _install_rich() -> bool:
        """Install Rich package if not present.

        Returns:
            bool: True if installation successful, False otherwise
        """
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "rich>=10.0.0"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def print_header(self, text: str) -> None:
        """Display bordered header with title if rich is available."""
        if HAS_RICH and RichPanel and self._console:
            self._console.clear()
            self._console.print(
                RichPanel(text,
                          expand=True,
                          border_style="blue",
                          padding=(1, 2),
                          title="🎮 AI Spider Game Setup",
                          title_align="left"))
        else:
            # For non-rich environments, try to clear using ANSI
            print("\033[2J\033[H", end="")
            print(f"\n{text}\n")

    def print_error(self, text: str) -> None:
        if HAS_RICH and self._console:
            self._console.print(f"❌ [red]Error:[/red] {text}")
        else:
            print(f"❌ Error: {text}")

    def print_success(self, text: str) -> None:
        if HAS_RICH and self._console:
            self._console.print(f"✨ [green]{text}[/green]")
        else:
            print(f"✨ {text}")

    @contextmanager
    def progress(self) -> Generator[Progress, None, None]:
        """Create progress context with spinner and text."""
        if HAS_RICH and RichProgress and RichSpinner and RichText:
            from rich.progress import BarColumn, TaskProgressColumn
            from rich.console import Group

            progress = RichProgress(
                RichSpinner("dots"),
                RichText("[progress.description]{task.description:<30}"),
                BarColumn(bar_width=None),
                TaskProgressColumn(),
                RichText("[purple]{task.completed:>7,}/{task.total:,} files[/purple]"),
                RichText("  "),
                console=self._console,
                expand=True,
                transient=True
            )
            with progress:
                yield Progress(progress=progress)
        else:
            with suppress():
                yield Progress(progress=None)

    def create_task(self,
                    progress: Progress,
                    description: str,
                    total: Optional[int] = None,
                    **kwargs) -> Progress:
        """Add new task to progress tracking."""
        if HAS_RICH and progress.progress:
            task_kwargs = {
                'description': description,
                'total': total,
                'visible': True
            }
            # Only add other kwargs that aren't already defined
            task_kwargs.update({
                k: v
                for k, v in kwargs.items() if k not in task_kwargs
            })

            task = progress.progress.add_task(**task_kwargs)
            progress.task = task
            return progress
        return Progress(progress=None)

    def update_task(self,
                    progress: Progress,
                    advance: bool = False,
                    **kwargs) -> None:
        """Update task progress or advance step.

        Args:
            progress (Progress): Progress tracking object
            advance (bool): Whether to advance the progress
            **kwargs: Additional progress parameters
        """
        if HAS_RICH and progress.progress and progress.task is not None:
            if advance:
                progress.progress.advance(progress.task)
            else:
                progress.progress.update(progress.task, **kwargs)

    def complete_task(self, progress: Progress) -> None:
        """Mark task as finished.

        Args:
            progress (Progress): Progress tracking object
        """
        if progress.task is not None:
            self.update_task(progress, completed=True)

    def confirm(self, question: str) -> bool:
        """Ask user for confirmation.

        Args:
            question (str): Question to display

        Returns:
            bool: True if user confirmed, False otherwise
        """
        if HAS_RICH and self._console:
            self._console.print(f"\n[yellow]{question} (y/n)[/yellow]")
        else:
            print(f"\n{question} (y/n)")

        return input().lower().strip() == 'y'
