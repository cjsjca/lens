
"""
Logbook (append-only JSONL log)
Records all cage operations in an immutable trail.
"""

import json
import hashlib
from datetime import datetime
from . import room


def ensure_exists():
    """Create the trail log if it doesn't exist"""
    trail_path = room.get_trail_log_path()
    if not trail_path.exists():
        trail_path.touch()


def append(entry_type, data):
    """Append a new entry to the trail log"""
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    entry = {
        "ts": timestamp,
        "type": entry_type,
        "data": data
    }
    
    # Create hash of the serialized payload
    payload = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256(payload.encode()).hexdigest()
    
    # Append to log file
    trail_path = room.get_trail_log_path()
    with open(trail_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def get_recent_entries(count):
    """Get the last N entries from the trail log"""
    trail_path = room.get_trail_log_path()
    if not trail_path.exists():
        return []
    
    entries = []
    with open(trail_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Take last N lines
    for line in lines[-count:]:
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    
    return entries
