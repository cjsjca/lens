"""
Referee (rule checks)
Enforces all cage rules and violations.
"""

from . import logbook
from . import executor
from pathlib import Path
from contextlib import contextmanager


class RuleViolationError(Exception):
    """Raised when a cage rule is violated"""
    pass


# Module flag for bootstrap mode
BOOTSTRAP_MODE = False


@contextmanager
def allow_bootstrap():
    """Context manager to temporarily allow bootstrap writes"""
    global BOOTSTRAP_MODE
    old = BOOTSTRAP_MODE
    BOOTSTRAP_MODE = True
    try:
        yield
    finally:
        BOOTSTRAP_MODE = old


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


def enforce_diff_only(path=None):
    """Ensure writes happen ONLY via the diff path"""
    # Allow bootstrap mode only for new files
    if BOOTSTRAP_MODE and path is not None:
        if not path.exists():
            return  # Allow bootstrap write for new files

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