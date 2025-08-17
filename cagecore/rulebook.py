"""
Rulebook (preferences + corrections)
Manages user preferences and correction rules.
"""

import json
from datetime import datetime
from . import room


def exists():
    """Check if the rulebook exists"""
    return room.get_rulebook_path().exists()


def create_default():
    """Create a default rulebook"""
    default_rules = {
        "preferences": {
            "voice_style": "maxim_threadline",
            "max_context_lines": 50
        },
        "corrections": []
    }

    with open(get_rulebook_path(), 'w', encoding='utf-8') as f:
        json.dump(default_rules, f, indent=2)


def init_if_missing():
    """Initialize rulebook if it doesn't exist using bootstrap write"""
    from . import workbench
    rulebook_path = get_rulebook_path()

    if not rulebook_path.exists():
        default_rules = {
            "preferences": {
                "voice_style": "maxim_threadline",
                "max_context_lines": 50
            },
            "corrections": []
        }
        workbench.bootstrap_write(rulebook_path, json.dumps(default_rules, indent=2))


def add_correction(from_text, to_text, note=None):
    """Add a correction to the rulebook"""
    rulebook_data = load()

    correction = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "from": from_text,
        "to": to_text
    }

    if note:
        correction["note"] = note

    rulebook_data["corrections"].append(correction)
    save(rulebook_data)

    return correction


def get_corrections():
    """Get all corrections from the rulebook"""
    rulebook_data = load()
    return rulebook_data.get("corrections", [])


def get_preferences():
    """Get preferences from the rulebook"""
    rulebook_data = load()
    return rulebook_data.get("preferences", {})


def load():
    """Load the current rulebook"""
    rulebook_path = room.get_rulebook_path()
    if not rulebook_path.exists():
        create_default()

    with open(rulebook_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(rulebook_data):
    """Save the rulebook"""
    rulebook_path = room.get_rulebook_path()
    with open(rulebook_path, "w", encoding="utf-8") as f:
        json.dump(rulebook_data, f, indent=2)