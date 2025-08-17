
"""
Referee (rule checks)
Enforces the cage rules and prevents violations.
"""

from . import room, logbook, planner


class RuleViolationError(Exception):
    """Raised when a cage rule is violated"""
    pass


VIOLATION_MESSAGE = "Not allowed. Diff-only and append-only per the rules."


def enforce_plan_then_act():
    """Ensure a plan exists before allowing action"""
    if not planner.has_current_plan():
        logbook.append("violation", {"rule": "plan_then_act", "message": VIOLATION_MESSAGE})
        raise RuleViolationError(VIOLATION_MESSAGE)


def enforce_diff_only():
    """Ensure only diff-based operations are used"""
    # This is enforced by the executor module - whole file writes are not allowed
    pass


def enforce_workspace_only(path):
    """Ensure path is within workspace"""
    if not room.is_path_in_workspace(path):
        logbook.append("violation", {"rule": "workspace_only", "path": str(path), "message": VIOLATION_MESSAGE})
        raise RuleViolationError(VIOLATION_MESSAGE)


def enforce_rehydrate_before_act():
    """Ensure rehydration has happened this session"""
    # This is checked by tracking rehydration in the rehydrator module
    from . import rehydrator
    if not rehydrator.is_rehydrated():
        logbook.append("violation", {"rule": "rehydrate_before_act", "message": VIOLATION_MESSAGE})
        raise RuleViolationError(VIOLATION_MESSAGE)


def enforce_append_only_log():
    """Ensure log is only appended to, never edited"""
    # This is enforced by the logbook module design
    pass
