"""Git operations for Spider Game setup."""

import os
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

    def update(self, op_code: int, cur_count: int, max_count: int = None, message: str = ''):
        """Update progress bar."""
        if max_count:
            percentage = int((cur_count / max_count) * 100)
            self.ui.update_task(
                self.task,
                completed=percentage,
                description=f"[blue]Downloading {percentage}%[/blue]"
            )

def clone_repository(ui: RichUI, url: str, branch: str,
                     target_dir: str, force: bool = False) -> Tuple[bool, str]:
    """Clone git repository with progress indication."""
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
            total=100
        )

        try:
            Repo.clone_from(
                url,
                target_dir,
                branch=branch,
                progress=CloneProgress(ui, task)
            )
            ui.complete_task(task)
            ui.print_success("📦 Download complete!")
            return True, ""

        except GitCommandError as e:
            if os.path.exists(target_dir):
                import shutil
                shutil.rmtree(target_dir, ignore_errors=True)
            return False, f"Git error: {str(e)}"
        
        except Exception as e:
            if os.path.exists(target_dir):
                import shutil
                shutil.rmtree(target_dir, ignore_errors=True)
            return False, str(e)
