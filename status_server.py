
import os, io, time
from flask import Flask, jsonify, Response

APP = Flask(__name__)

ART_DIR = "artifacts"
TRAIL = os.path.join(ART_DIR, "trail.log")
LAST = os.path.join(ART_DIR, "last_outputs.txt")

def tail(path, n=20):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return [ln.rstrip("\n") for ln in lines[-n:]]

def mtime(path):
    return os.path.getmtime(path) if os.path.exists(path) else None

def get_strict_mode():
    try:
        from cagecore import referee
        return getattr(referee, "STRICT_MODE", True)
    except Exception:
        return None  # unknown

def get_cage_state():
    """Get comprehensive cage application state"""
    try:
        from cagecore import logbook, rehydrator, planner, rulebook, workbench
        
        # Get recent log entries to understand what's happening
        recent_entries = logbook.get_recent_entries(10)
        
        # Get latest plan if any
        latest_plan = None
        try:
            latest_plan = planner.get_latest_plan()
        except Exception:
            pass
        
        # Get rehydration status
        rehydrated = rehydrator.is_rehydrated()
        
        # Get workspace files
        workspace_files = []
        try:
            workspace_files = workbench.list_files()
        except Exception:
            pass
        
        # Get rulebook info
        preferences = {}
        corrections = []
        try:
            preferences = rulebook.get_preferences()
            corrections = rulebook.get_corrections()
        except Exception:
            pass
        
        return {
            "recent_operations": recent_entries,
            "latest_plan": latest_plan,
            "rehydrated": rehydrated,
            "workspace_files": workspace_files,
            "preferences": preferences,
            "corrections_count": len(corrections),
            "last_operation": recent_entries[-1] if recent_entries else None
        }
    except Exception as e:
        return {"error": str(e)}

@APP.route("/status.json")
def status_json():
    data = {
        "strict_mode": get_strict_mode(),
        "cage_state": get_cage_state(),
        "trail_tail": tail(TRAIL, 20),
        "trail_mtime": mtime(TRAIL),
        "last_outputs_tail": tail(LAST, 50),
        "last_outputs_mtime": mtime(LAST),
        "server_time": time.time(),
    }
    return jsonify(data)

HTML = """<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="5">
<title>Cage Status Monitor</title>
<style>
 body {{ font: 14px/1.4 system-ui, sans-serif; margin: 24px; }}
 pre {{ background:#111; color:#eee; padding:12px; border-radius:8px; overflow:auto; max-height:300px; }}
 .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; }}
 .ok {{ background:#0b4; color:#fff; }} .warn {{ background:#c60; color:#fff; }}
 .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 8px; }}
 .status-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
 .files {{ font-family: monospace; font-size: 12px; }}
</style></head><body>
<h1>Cage Status Monitor</h1>
<p>Strict mode: {STRICT_PILL} | Rehydrated: {REHYDRATED_PILL}</p>

<div class="status-grid">
<div class="section">
<h3>Last Operation</h3>
<pre>{LAST_OP}</pre>
</div>

<div class="section">
<h3>Current Plan</h3>
<pre>{CURRENT_PLAN}</pre>
</div>
</div>

<div class="section">
<h3>Workspace Files</h3>
<div class="files">{WORKSPACE_FILES}</div>
</div>

<div class="section">
<h3>Recent Operations (last 5)</h3>
<pre>{RECENT_OPS}</pre>
</div>

<h2>Trail Log (last 20 lines)</h2>
<pre>{TRAIL}</pre>

<h2>Command Outputs</h2>
<pre>{LAST}</pre>

<p style="color:#888">Auto-refreshes every 5s. Server time: {NOW}</p>
</body></html>"""

def strict_pill():
    strict = get_strict_mode()
    if strict is True:  return '<span class="pill ok">STRICT_MODE=True</span>'
    if strict is False: return '<span class="pill warn">STRICT_MODE=False</span>'
    return '<span class="pill warn">STRICT_MODE=Unknown</span>'

def rehydrated_pill():
    try:
        from cagecore import rehydrator
        rehydrated = rehydrator.is_rehydrated()
        if rehydrated: return '<span class="pill ok">YES</span>'
        else: return '<span class="pill warn">NO</span>'
    except Exception:
        return '<span class="pill warn">UNKNOWN</span>'

def format_operation(op):
    if not op:
        return "None"
    return f"[{op.get('ts', 'no time')}] {op.get('type', 'unknown')}: {str(op.get('data', {}))[:100]}..."

def format_plan(plan):
    if not plan:
        return "No plan set"
    return f"'{plan.get('title', 'Untitled')}' - {plan.get('filename', '?')} ({plan.get('find_text', '?')[:30]}...)"

@APP.route("/")
def index():
    cage_state = get_cage_state()
    
    recent_ops = cage_state.get('recent_operations', [])
    last_op = cage_state.get('last_operation')
    latest_plan = cage_state.get('latest_plan')
    workspace_files = cage_state.get('workspace_files', [])
    
    html = HTML.format(
        STRICT_PILL=strict_pill(),
        REHYDRATED_PILL=rehydrated_pill(),
        LAST_OP=format_operation(last_op),
        CURRENT_PLAN=format_plan(latest_plan),
        WORKSPACE_FILES="<br>".join(workspace_files) or "(no files)",
        RECENT_OPS="\n".join([format_operation(op) for op in recent_ops[-5:]]) or "(no recent operations)",
        TRAIL="\n".join(tail(TRAIL, 20)) or "(no trail yet)",
        LAST="\n".join(tail(LAST, 50)) or "(no last outputs yet)",
        NOW=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    return Response(io.StringIO(html).getvalue(), mimetype="text/html")

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
