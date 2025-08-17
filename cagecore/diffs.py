
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
    """Apply a diff by writing the new content"""
    try:
        # In a real implementation, we'd parse and apply the actual diff
        # For this demo, we simply write the new content
        workbench.write_file(filename, new_content)
        
        return {
            "success": True,
            "message": f"Applied changes to {filename}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
