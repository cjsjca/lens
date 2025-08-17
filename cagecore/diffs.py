"""
Diffs (make/apply unified diffs)
Handles creation and application of unified diff patches.
"""

import difflib
from . import workbench, executor


def create_diff(original_content, new_content, filename):
    """Create a unified diff between original and new content"""
    original_lines = original_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    diff_lines = list(difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm=""
    ))

    diff_text = "".join(diff_lines)

    return {
        "diff": diff_text,
        "has_changes": len(diff_lines) > 0
    }


def apply_diff(filename: str, original: str, new: str) -> dict:
    """Apply a diff by writing the new content to the file"""
    try:
        # Set diff mode active for the duration of the write
        executor.DIFF_MODE_ACTIVE = True
        workbench.write_file_guarded(filename, new)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        executor.DIFF_MODE_ACTIVE = False


def apply_patch(original_content, diff_text):
    """Apply a unified diff patch to original content"""
    # Simple implementation: for this demo, we'll just return the patched result
    # In a real system, you'd parse the diff and apply it line by line
    try:
        # This is a simplified implementation
        # In practice, you'd parse the unified diff format properly
        lines = diff_text.split('\n')

        # Find the replacement in the diff
        add_lines = []
        for line in lines:
            if line.startswith('+') and not line.startswith('+++'):
                add_lines.append(line[1:])

        # For this simple case, assume it's a straight replacement
        if add_lines:
            return '\n'.join(add_lines)

        return original_content

    except Exception as e:
        raise ValueError(f"Failed to apply patch: {e}")