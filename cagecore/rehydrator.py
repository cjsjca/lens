"""
Rehydrator (loads past corrections + prefs)
Loads context from rulebook and recent log entries.
"""

from . import rulebook, logbook, arc

# Module-level state tracking
_rehydrated = False


def rehydrate():
    """Load context from rulebook and recent logs"""
    global _rehydrated

    # Load rulebook
    preferences = rulebook.get_preferences()
    corrections = rulebook.get_corrections()

    # Load recent log entries based on ARC heuristic
    context_depth = arc.get_context_amount()
    recent_entries = logbook.get_recent_entries(context_depth)

    # Mark as rehydrated
    _rehydrated = True

    # Log the rehydration
    logbook.append("rehydrate", {
        "preferences_loaded": len(preferences),
        "corrections_loaded": len(corrections),
        "recent_entries_loaded": len(recent_entries)
    })


def is_rehydrated():
    """Check if rehydration has happened this session"""
    return _rehydrated


def reset_rehydration():
    """Reset rehydration state (for testing)"""
    global _rehydrated
    _rehydrated = False