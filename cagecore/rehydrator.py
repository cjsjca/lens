
"""
Rehydrator (loads past corrections + prefs)
Loads relevant history and corrections before planning/acting.
"""

from . import rulebook, logbook, arc


_rehydrated_this_session = False


def rehydrate():
    """Load past corrections and preferences"""
    global _rehydrated_this_session
    
    # Load rulebook
    preferences = rulebook.get_preferences()
    corrections = rulebook.get_corrections()
    
    # Use ARC to determine how much context to load
    context_entries = arc.get_context_amount()
    recent_entries = logbook.get_recent_entries(context_entries)
    
    # Log the rehydration
    logbook.append("rehydrate", {
        "preferences_loaded": len(preferences),
        "corrections_loaded": len(corrections),
        "context_entries": len(recent_entries)
    })
    
    _rehydrated_this_session = True


def is_rehydrated():
    """Check if rehydration has happened this session"""
    global _rehydrated_this_session
    return _rehydrated_this_session


def check_correction_match(find_text, replace_text):
    """Check if current operation matches a past correction"""
    corrections = rulebook.get_corrections()
    
    for correction in corrections:
        if correction["from"] == find_text and correction["to"] == replace_text:
            logbook.append("correction_respected", {
                "from": find_text,
                "to": replace_text,
                "original_timestamp": correction["timestamp"],
                "note": "respected prior correction"
            })
            return True
    
    return False
