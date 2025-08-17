"""
Diffs (make/apply unified diffs)
Handles creation and application of unified diff patches.
"""

import difflib
from . import workbench


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


def apply_diff(filename, original_content, new_content):
    """Apply changes to a file through workbench with diff-only enforcement"""
    from . import executor

    try:
        # Set diff mode active before any writes
        executor.DIFF_MODE_ACTIVE = True
        try:
            # Write through the guarded gate
            workbench.write_file_guarded(filename, new_content)

            return {
                "success": True,
                "message": f"Successfully applied changes to {filename}"
            }
        finally:
            # Always reset diff mode
            executor.DIFF_MODE_ACTIVE = False

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to apply changes: {str(e)}"
        }


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