
import os, io, time, sys, json
from flask import Flask, jsonify, Response
from datetime import datetime

APP = Flask(__name__)
SERVER_START_TIME = datetime.utcnow().isoformat() + "Z"
LAST_RETRIEVE_RESULT = None

ART_DIR = "artifacts"
ART1 = os.path.join("artifacts", "trail.log")
ART2 = "trail.log"
def trail_path():
    return ART1 if os.path.exists(ART1) else ART2

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

def count_lines(filename):
    """Count lines in a file, return 0 if missing"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0


def get_last_atoms(n=5):
    """Get last n atoms with id, ts, text60"""
    try:
        atoms = []
        with open("atoms.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    atom = json.loads(line.strip())
                    text60 = atom["text"][:60] + "..." if len(atom["text"]) > 60 else atom["text"]
                    atoms.append({
                        "id": atom["id"],
                        "ts": atom["ts"],
                        "text60": text60
                    })
        return atoms[-n:] if atoms else []
    except FileNotFoundError:
        return []

def get_last_retrieve_result():
    """Get the last retrieve result from trail log"""
    try:
        trail_lines = tail(trail_path(), 50)
        for line in reversed(trail_lines):
            if " | " in line and "retrieve" not in line:
                # This looks like a retrieve result line
                return line
        return "none yet"
    except Exception:
        return "none yet"


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
        "trail_file": trail_path(),
        "trail_tail": tail(trail_path(), 10),
        "trail_mtime": mtime(trail_path()),
        "last_outputs_tail": tail(LAST, 50),
        "last_outputs_mtime": mtime(LAST),
        "atoms_count": count_lines("atoms.jsonl"),
        "atoms_exists": os.path.exists("atoms.jsonl"),
        "links_count": count_lines("links.jsonl"),
        "links_exists": os.path.exists("links.jsonl"),
        "atoms_last5": get_last_atoms(5),
        "last_retrieve": get_last_retrieve_result(),
        "server_time": time.time(),
        "server_start_time": SERVER_START_TIME,
        "current_working_directory": os.getcwd(),
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

<div class="section">
<h3>Files & Storage</h3>
<p>Trail file: {TRAIL_FILE}</p>
<p>Atoms: {ATOMS_EXISTS} ({ATOMS_COUNT} lines) | Links: {LINKS_EXISTS} ({LINKS_COUNT} lines)</p>
<h4>Last 5 Atoms</h4>
<pre>{ATOMS_LAST5}</pre>
<h4>Last Retrieve Result</h4>
<pre>{LAST_RETRIEVE}</pre>
</div>

<div class="section">
<h3>Server Environment</h3>
<p>CWD: {CWD}</p>
<p>Restarted: {RESTART_TIME}</p>
<p>Mode: {MODE_PILL}</p>
</div>

<h2>Trail Log (last 10 lines from {TRAIL_FILE})</h2>
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

def mode_pill():
    strict = get_strict_mode()
    if strict is True:  return '<span class="pill ok">Strict</span>'
    if strict is False: return '<span class="pill warn">Relaxed</span>'
    return '<span class="pill warn">Unknown</span>'

@APP.route("/")
def index():
    cage_state = get_cage_state()
    
    recent_ops = cage_state.get('recent_operations', [])
    last_op = cage_state.get('last_operation')
    latest_plan = cage_state.get('latest_plan')
    workspace_files = cage_state.get('workspace_files', [])
    atoms_last5 = get_last_atoms(5)
    
    atoms_display = "\n".join([f"{a['id'][:8]} | {a['ts']} | {a['text60']}" for a in atoms_last5]) or "(no atoms yet)"
    
    html = HTML.format(
        STRICT_PILL=strict_pill(),
        REHYDRATED_PILL=rehydrated_pill(),
        LAST_OP=format_operation(last_op),
        CURRENT_PLAN=format_plan(latest_plan),
        WORKSPACE_FILES="<br>".join(workspace_files) or "(no files)",
        RECENT_OPS="\n".join([format_operation(op) for op in recent_ops[-5:]]) or "(no recent operations)",
        TRAIL_FILE=trail_path(),
        ATOMS_EXISTS="exists" if os.path.exists("atoms.jsonl") else "missing",
        ATOMS_COUNT=count_lines("atoms.jsonl"),
        LINKS_EXISTS="exists" if os.path.exists("links.jsonl") else "missing",
        LINKS_COUNT=count_lines("links.jsonl"),
        ATOMS_LAST5=atoms_display,
        LAST_RETRIEVE=get_last_retrieve_result(),
        CWD=os.getcwd(),
        RESTART_TIME=SERVER_START_TIME,
        MODE_PILL=mode_pill(),
        TRAIL="\n".join(tail(trail_path(), 10)) or "(no trail yet)",
        LAST="\n".join(tail(LAST, 50)) or "(no last outputs yet)",
        NOW=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    return Response(io.StringIO(html).getvalue(), mimetype="text/html")

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
