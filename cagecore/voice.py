
"""
Voice (Maxim + Threadline responses)
Formats all user-facing output in the standard cage style.
"""

import json


def maxim_threadline(maxim, threadline):
    """Format output as Maxim (short statement) + Threadline (explanation)"""
    return f"{maxim}\n\n{threadline}"


def format_json(data):
    """Format JSON data for display"""
    return json.dumps(data, indent=2)
