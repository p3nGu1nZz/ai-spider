"""Git operations for Spider Game setup."""

import os
import subprocess
from typing import Tuple
from .ui import RichUI


def clone_repository(ui: RichUI, url: str, branch: str,
                     target_dir: str) -> Tuple[bool, str]:
    """Clone git repository with progress indication.

    Args:
        ui (RichUI): UI instance for progress display
        url (str): Repository URL
        branch (str): Branch to clone
        target_dir (str): Target directory

    Returns:
        Tuple[bool, str]: Success status and error message if any
    """
    if os.path.exists(target_dir):
        return True, ""

    with ui.progress() as progress:
        task = ui.create_task(
            progress,
            f"Cloning ML-Agents repository ({branch} branch)...",
            total=100  # Git uses percentage for progress
        )

        try:
            process = subprocess.Popen([
                'git', 'clone', '--progress', '--branch', branch, url,
                target_dir
            ],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       universal_newlines=True)

            while True:
                # Git sends progress to stderr
                if process.stderr:
                    line = process.stderr.readline()
                    if not line:
                        break

                    # Parse progress information
                    if "Receiving objects: " in line:
                        try:
                            percent = int(line.split()[2].strip('%'))
                            ui.update_task(task, completed=percent)
                        except (ValueError, IndexError):
                            ui.update_task(task, advance=True)
                    elif "Resolving deltas: " in line:
                        try:
                            percent = int(line.split()[2].strip('%'))
                            ui.update_task(task, completed=percent)
                        except (ValueError, IndexError):
                            ui.update_task(task, advance=True)

                if process.poll() is not None:
                    break

            if process.returncode == 0:
                ui.complete_task(task)
                ui.print_success("Repository cloned successfully!")
                return True, ""
            else:
                error = process.stderr.read(
                ) if process.stderr else "Unknown error"
                return False, error

        except Exception as e:
            return False, str(e)
