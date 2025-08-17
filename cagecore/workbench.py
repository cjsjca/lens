
"""
Workbench (controlled file IO under ./workspace)
Provides safe file operations within the workspace.
"""

from pathlib import Path
from . import room, referee


def get_workspace_path(filename):
    """Get a path within the workspace"""
    workspace_dir = room.get_workspace_dir()
    return workspace_dir / filename


def read_file(filename):
    """Read a file from the workspace"""
    file_path = get_workspace_path(filename)
    referee.enforce_workspace_only(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File {filename} not found in workspace")
    
    return file_path.read_text(encoding="utf-8")


def write_file(filename, content):
    """Write a file to the workspace"""
    file_path = get_workspace_path(filename)
    referee.enforce_workspace_only(file_path)
    
    file_path.write_text(content, encoding="utf-8")


def file_exists(filename):
    """Check if a file exists in the workspace"""
    file_path = get_workspace_path(filename)
    return file_path.exists()
