"""
Workbench (controlled file IO under ./workspace)
Provides safe file operations within the workspace boundary.
"""

from pathlib import Path
from . import room, referee
import logging

logbook = logging.getLogger("logbook")


def get_workspace_path(filename):
    """Get the full path for a file in the workspace"""
    return room.get_workspace_dir() / filename


def file_exists(filename):
    """Check if a file exists in the workspace"""
    path = get_workspace_path(filename)
    referee.enforce_workspace_only(path)
    return path.exists()


def read_file(filename):
    """Read a file from the workspace"""
    path = get_workspace_path(filename)
    referee.enforce_workspace_only(path)

    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def bootstrap_write(rel_path: str, content: str) -> None:
    file_path: Path = room.workspace_path() / rel_path
    referee.enforce_workspace_only(file_path)
    referee.enforce_diff_only(path=file_path)  # will allow only if not exists
    with open(file_path, "x", encoding="utf-8") as f:  # create-only
        f.write(content)


def write_file_guarded(path, new_content):
    """Guarded file write that enforces all rules"""
    file_path = get_workspace_path(path)

    # Enforce workspace-only writes
    referee.enforce_workspace_only(file_path)

    # Enforce diff-only writes
    referee.enforce_diff_only(path=file_path)

    # Write the content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)


def write_file(filename, content):
    """Legacy write function - redirects to guarded version"""
    write_file_guarded(filename, content)


def list_files():
    """List all files in the workspace"""
    workspace_dir = room.get_workspace_dir()
    files = []

    if workspace_dir.exists():
        for path in workspace_dir.rglob("*"):
            if path.is_file():
                relative_path = path.relative_to(workspace_dir)
                files.append(str(relative_path))

    return files