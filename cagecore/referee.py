"""
Referee (rule checks)
Enforces all cage guardrails and constraints.
"""

from contextlib import contextmanager
from typing import Optional
from pathlib import Path
from . import room, logbook, planner, executor


class RuleViolationError(Exception):
    """Raised when a cage rule is violated"""
    pass


# Module flag for bootstrap mode
BOOTSTRAP_MODE = False

# TEMP for POC
STRICT_MODE = False


@contextmanager
def allow_bootstrap():
    """Temporarily allow create-only writes during init."""
    global BOOTSTRAP_MODE
    prev = BOOTSTRAP_MODE
    BOOTSTRAP_MODE = True
    try:
        yield
    finally:
        BOOTSTRAP_MODE = prev


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


def enforce_diff_only(path: Optional[Path] = None) -> None:
    """
    Allow writes ONLY when:
      - BOOTSTRAP_MODE is True AND target does not yet exist (create-only), OR
      - executor.DIFF_MODE_ACTIVE is True (approved diff application)
    """
    if BOOTSTRAP_MODE:
        if path is None or not isinstance(path, Path):
            violation_msg = "Not allowed. Diff-only and append-only per the rules."
            logbook.append("violation", {"message": violation_msg})
            raise RuleViolationError(violation_msg)
        if not room.is_path_in_workspace(path):
            violation_msg = "Not allowed. Diff-only and append-only per the rules."
            logbook.append("violation", {"message": violation_msg})
            raise RuleViolationError(violation_msg)
        if path.exists():
            violation_msg = "Not allowed. Diff-only and append-only per the rules."
            logbook.append("violation", {"message": violation_msg})
            raise RuleViolationError(violation_msg)
        return
    if not getattr(executor, "DIFF_MODE_ACTIVE", False):
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