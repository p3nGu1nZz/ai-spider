"""Git operations for Spider Game setup."""

import os
import signal
import psutil  # Add this import
from typing import Tuple, Any
from git import Repo, RemoteProgress
from git.exc import GitCommandError
from .ui import RichUI


class CloneProgress(RemoteProgress):
    """Progress callback for git operations."""
    def __init__(self, ui: RichUI, task: Any):
        super().__init__()
        self.ui = ui
        self.task = task
        self._started = False
        self._last_max = 0
        self._repo = None  # Store repo reference for cleanup

    def update(self, op_code: int, cur_count: int, max_count: int = None, message: str = ''):
        """Update progress bar using git progress info."""
        if max_count and max_count > self._last_max:
            self._last_max = max_count
            self.ui.update_task(self.task, total=int(max_count))  # Convert to int
        
        if max_count:
            stage = "Downloading"
            if op_code & RemoteProgress.RESOLVING:
                stage = "Resolving"
            elif op_code & RemoteProgress.RECEIVING:
                stage = "Receiving"
            elif op_code & RemoteProgress.COMPRESSING:
                stage = "Compressing"
            elif op_code & RemoteProgress.WRITING:
                stage = "Writing"
            
            self.ui.update_task(
                self.task,
                completed=int(cur_count),  # Convert to int
                description=f"[blue]{stage} ({int(cur_count):,}/{int(max_count):,})[/blue]"
            )


def clone_repository(ui: RichUI, url: str, branch: str,
                     target_dir: str, force: bool = False) -> Tuple[bool, str]:
    """Clone git repository with progress indication."""
    current_process = None

    def cleanup_handler(signum, frame):
        """Handle interrupt signal."""
        if current_process:
            # Kill git process and children
            try:
                parent = psutil.Process(current_process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.kill()
                parent.kill()
            except (psutil.NoSuchProcess, Exception):
                pass

        if os.path.exists(target_dir):
            ui.print_error("\nCleaning up...")
            import shutil
            shutil.rmtree(target_dir, ignore_errors=True)
        ui.print_error("Setup cancelled by user")
        os._exit(1)  # Force exit

    # Register cleanup handler for CTRL+C
    original_handler = signal.signal(signal.SIGINT, cleanup_handler)

    try:
        if os.path.exists(target_dir):
            if not force:
                return True, ""
            import shutil
            ui.print_success("🔄 Removing existing repository...")
            shutil.rmtree(target_dir, ignore_errors=True)

        with ui.progress() as progress:
            task = ui.create_task(
                progress,
                description="[blue]Preparing...[/blue]",
                total=1
            )

            progress_callback = CloneProgress(ui, task)
            process = Repo.clone_from(
                url,
                target_dir,
                branch=branch,
                progress=progress_callback
            )
            current_process = process.git.current_process
            ui.complete_task(task)
            ui.print_success("📦 Download complete!")
            return True, ""

    except (GitCommandError, KeyboardInterrupt) as e:
        cleanup_handler(None, None)  # Force cleanup
        return False, f"Git error: {str(e)}"
    
    finally:
        # Restore original signal handler
        signal.signal(signal.SIGINT, original_handler)
