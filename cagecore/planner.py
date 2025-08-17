
"""
Planner (makes a PLAN object, no editing)
Creates execution plans without performing any modifications.
"""

from datetime import datetime
from . import logbook


_current_plan = None


def create_plan(title, target_file, find_text, replace_text):
    """Create a new plan"""
    global _current_plan
    
    plan_data = {
        "title": title,
        "target_file": target_file,
        "find_text": find_text,
        "replace_text": replace_text,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "notes": f"Replace '{find_text}' with '{replace_text}' in {target_file}"
    }
    
    _current_plan = plan_data
    return plan_data


def get_latest_plan():
    """Get the most recent plan"""
    global _current_plan
    return _current_plan


def has_current_plan():
    """Check if there's a current plan"""
    global _current_plan
    return _current_plan is not None


def clear_current_plan():
    """Clear the current plan after execution"""
    global _current_plan
    _current_plan = None
