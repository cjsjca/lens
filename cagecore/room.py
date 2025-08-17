
"""
Room (paths, startup)
Manages the safe space where the cage operates.
"""

from pathlib import Path

# The cage root directory
CAGE_ROOT = Path(__file__).parent.parent
WORKSPACE_DIR = CAGE_ROOT / "workspace"
ARTIFACTS_DIR = CAGE_ROOT / "artifacts"
RULEBOOK_PATH = CAGE_ROOT / "rulebook.json"
TRAIL_LOG_PATH = CAGE_ROOT / "trail.log"


def setup():
    """Initialize the room environment"""
    ensure_directories()


def ensure_directories():
    """Ensure all required directories exist"""
    WORKSPACE_DIR.mkdir(exist_ok=True)
    ARTIFACTS_DIR.mkdir(exist_ok=True)


def get_workspace_dir():
    """Get the workspace directory path"""
    return WORKSPACE_DIR


def get_artifacts_dir():
    """Get the artifacts directory path"""
    return ARTIFACTS_DIR


def get_rulebook_path():
    """Get the rulebook file path"""
    return RULEBOOK_PATH


def get_trail_log_path():
    """Get the trail log file path"""
    return TRAIL_LOG_PATH


def is_path_in_workspace(path):
    """Check if a path is within the workspace directory"""
    try:
        full_path = Path(path).resolve()
        workspace_path = WORKSPACE_DIR.resolve()
        return workspace_path in full_path.parents or full_path == workspace_path
    except (OSError, ValueError):
        return False
