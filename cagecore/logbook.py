
"""
Logbook (append-only JSONL log)
Maintains an immutable record of all cage operations.
"""

import json
import hashlib
from datetime import datetime
from . import room


def ensure_exists():
    """Ensure the log file exists"""
    log_path = room.get_trail_log_path()
    if not log_path.exists():
        log_path.touch()


def append(entry_type, data):
    """Append an entry to the log"""
    timestamp = datetime.utcnow().isoformat() + "Z"
    entry = {
        "timestamp": timestamp,
        "type": entry_type,
        "data": data,
        "hash": _compute_hash(entry_type, data, timestamp)
    }
    
    log_path = room.get_trail_log_path()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(',', ':')) + "\n")


def get_recent_entries(count=50):
    """Get the most recent entries from the log"""
    log_path = room.get_trail_log_path()
    if not log_path.exists():
        return []
    
    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return entries[-count:] if count > 0 else entries


def _compute_hash(entry_type, data, timestamp):
    """Compute a hash for the entry"""
    content = f"{timestamp}:{entry_type}:{json.dumps(data, sort_keys=True)}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]
