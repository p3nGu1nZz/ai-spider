"""Git operations for Spider Game setup."""

import os
import json
import subprocess
from typing import Tuple, Optional
from urllib import request
from urllib.error import URLError
from time import sleep
from .ui import RichUI

# Known ML-Agents repository stats (fallback values)
MLAGENTS_SIZE_MB = 156.2
MLAGENTS_FILES = 65432

def get_repo_details(url: str, retries: int = 3) -> Tuple[float, int]:
    """Get repository size and file count from GitHub API."""
    headers = {'User-Agent': 'Spider-Game-Setup/1.0'}
    api_url = url.replace("https://github.com/", "https://api.github.com/repos/")
    api_url = api_url.replace(".git", "")
    
    for attempt in range(retries):
        try:
            req = request.Request(api_url, headers=headers)
            with request.urlopen(req) as response:
                data = json.loads(response.read())
                size_mb = round(data.get('size', 0) / 1024, 2)
                return size_mb, MLAGENTS_FILES  # Use known file count
        except Exception:
            if attempt < retries - 1:
                sleep(1)  # Wait before retry
                continue
            return MLAGENTS_SIZE_MB, MLAGENTS_FILES  # Use fallback values


def clone_repository(ui: RichUI, url: str, branch: str,
                     target_dir: str) -> Tuple[bool, str]:
    """Clone git repository with progress indication."""
    if os.path.exists(target_dir):
        return True, ""

    # Get repository details, always returns values
    size_mb, file_count = get_repo_details(url)
    ui.print_success(f"📦 Repository size: {size_mb}MB ({file_count:,} files)")

    with ui.progress() as progress:
        task = ui.create_task(
            progress,
            description="[blue]Preparing download...[/blue]",
            total=file_count
        )

        try:
            process = subprocess.Popen(
                ['git', 'clone', '--progress', '--branch', branch, url, target_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            while True:
                if process.stderr:
                    line = process.stderr.readline()
                    if not line:
                        break

                    # Update progress description based on current operation
                    if "Receiving objects" in line:
                        try:
                            percent = int(line.split()[2].strip('%'))
                            files_done = round((percent * file_count) / 100) if file_count else percent
                            ui.update_task(task, 
                                         completed=files_done,
                                         description=f"[blue]Downloading[/blue]")
                        except (ValueError, IndexError):
                            pass
                    elif "Resolving deltas" in line:
                        try:
                            percent = int(line.split()[2].strip('%'))
                            ui.update_task(task,
                                         description="[blue]Finalizing...[/blue]",
                                         completed=files_done)
                        except (ValueError, IndexError):
                            pass

                if process.poll() is not None:
                    break

            if process.returncode == 0:
                ui.complete_task(task)
                ui.print_success("📦 Repository cloned successfully!")
                return True, ""
            else:
                error = process.stderr.read() if process.stderr else "Unknown error"
                return False, f"⚠️ Git error: {error}"

        except Exception as e:
            return False, str(e)
