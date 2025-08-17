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


def bootstrap_write(path, content):
    """Bootstrap write for new files only during init"""
    if isinstance(path, str):
        file_path = get_workspace_path(path)
    else:
        file_path = path

    # Enforce workspace-only writes
    referee.enforce_workspace_only(file_path)

    # Reject if path already exists
    if file_path.exists():
        violation_msg = "Not allowed. Diff-only and append-only per the rules."
        logbook.append("violation", {"message": violation_msg})
        raise referee.RuleViolationError(violation_msg)

    # Enforce diff-only with path for bootstrap check
    referee.enforce_diff_only(path=file_path)

    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write with create-only mode
    with open(file_path, 'x', encoding='utf-8') as f:
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