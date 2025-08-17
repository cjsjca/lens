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
    """Ensure there is a plan before acting"""
    if not planner.has_current_plan():
        violation_msg = "Not allowed. Diff-only and append-only per the rules."
        logbook.append("violation", {"message": violation_msg})
        raise RuleViolationError(violation_msg)


def enforce_rehydrate_before_act():
    """Ensure rehydration has occurred before acting"""
    from . import rehydrator
    if not rehydrator.is_rehydrated():
        violation_msg = "Not allowed. Diff-only and append-only per the rules."
        logbook.append("violation", {"message": violation_msg})
        raise RuleViolationError(violation_msg)


def enforce_workspace_only(path):
    """Ensure operations only happen within the workspace"""
    if not room.is_path_in_workspace(path):
        violation_msg = "Not allowed. Diff-only and append-only per the rules."
        logbook.append("violation", {"message": violation_msg})
        raise RuleViolationError(violation_msg)


def enforce_diff_only():
    """Ensure changes are only made through diffs"""
    from . import executor
    if not executor.DIFF_MODE_ACTIVE:
        violation_msg = "Not allowed. Diff-only and append-only per the rules."
        logbook.append("violation", {"message": violation_msg})
        raise RuleViolationError(violation_msg)


def enforce_append_only_log():
    """Ensure log entries are only appended, never modified"""
    from . import logbook
    if not logbook.guard_append_only():
        violation_msg = "Not allowed. Diff-only and append-only per the rules."
        logbook.append("violation", {"message": violation_msg})
        raise RuleViolationError(violation_msg)