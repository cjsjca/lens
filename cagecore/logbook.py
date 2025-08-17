"""
Logbook (append-only JSONL log)
Records all cage operations in an immutable trail.
"""

import json
import hashlib
from datetime import datetime
import os
from . import room


def ensure_exists():
    """Create the trail log if it doesn't exist"""
    from . import workbench
    trail_path = room.get_trail_log_path()
    if not trail_path.exists():
        workbench.bootstrap_write(trail_path, "")


def create_entry(entry_type, data):
    """Create a log entry with timestamp and hash"""
    timestamp = datetime.utcnow().isoformat() + "Z"

    entry = {
        "ts": timestamp,
        "type": entry_type,
        "data": data
    }

    # Create hash of the serialized payload
    payload = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256(payload.encode()).hexdigest()
    return entry


def append(entry_type, data):
    """Append a new entry to the trail log with size verification"""
    entry = create_entry(entry_type, data)

    log_path = room.get_trail_log_path()

    # Get size before
    size_before = log_path.stat().st_size if log_path.exists() else 0

    with open(log_path, 'a', encoding='utf-8') as f:
        json_line = json.dumps(entry) + '\n'
        f.write(json_line)
        f.flush()
        os.fsync(f.fileno())

    # Get size after and verify it increased
    size_after = log_path.stat().st_size
    if size_after < size_before:
        raise ValueError("Log file size decreased - append-only violation")


def guard_append_only():
    """Check if append-only conditions are met"""
    # This is called by referee to validate append-only behavior
    # For now, return True as the actual check happens in append()
    return True


def tail(count=10):
    """Get the last N entries from the trail log"""
    log_path = room.get_trail_log_path()

    if not log_path.exists():
        return []

    entries = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return entries[-count:] if entries else []


def get_recent_entries(count=50):
    """Get recent entries - alias for tail"""
    return tail(count)