
"""
ARC (Adaptive Retrieval Controller)
Tiny heuristic for managing context retrieval amounts.
"""


def get_context_amount():
    """Determine how much context to retrieve based on simple heuristics"""
    # For now, a simple heuristic: return a moderate amount
    # In a real system, this might consider task complexity, recent activity, etc.
    return 10  # Default to last 10 entries
