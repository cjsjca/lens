
"""
ARC (Adaptive Retrieval Controller)
Tiny heuristic for managing context retrieval amounts.
"""


def get_context_amount():
    """Determine how much context to retrieve based on simple heuristics"""
    # For now, a simple heuristic: return a moderate amount
    # In a real system, this might consider task complexity, recent activity, etc.
    return 10  # Default to last 10 entries


def choose_context_depth(task_hint):
    """Choose context depth based on task hint"""
    if len(task_hint) <= 20:
        return 5
    else:
        return 20
