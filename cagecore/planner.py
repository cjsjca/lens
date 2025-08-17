
"""
Planner (makes a PLAN object, no editing)
Creates and manages execution plans.
"""

import json
from datetime import datetime

# Module-level storage for current plan
_current_plan = None


def create_plan(title, filename, find_text, replace_text):
    """Create a new plan"""
    global _current_plan
    
    plan = {
        "title": title,
        "target_file": filename,
        "find_text": find_text,
        "replace_text": replace_text,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    _current_plan = plan
    return plan


def get_latest_plan():
    """Get the current plan"""
    return _current_plan


def has_current_plan():
    """Check if there's a current plan"""
    return _current_plan is not None


def clear_current_plan():
    """Clear the current plan after successful execution"""
    global _current_plan
    _current_plan = None
