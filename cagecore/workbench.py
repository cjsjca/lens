
"""
Workbench (controlled file IO under ./workspace)
Provides safe file operations within the workspace boundary.
"""

from pathlib import Path
from . import room, referee


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


def write_file(filename, content):
    """Write a file to the workspace"""
    path = get_workspace_path(filename)
    referee.enforce_workspace_only(path)
    
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    path.write_text(content, encoding="utf-8")


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
