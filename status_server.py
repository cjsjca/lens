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

def get_last_retrieve_results():
    """Get the last retrieve results from trail log"""
    try:
        trail_lines = tail(trail_path(), 50)
        results = []
        for line in reversed(trail_lines):
            if " | " in line and "retrieve" not in line and "ingest" not in line:
                # This looks like a retrieve result line
                results.append(line)
                if len(results) >= 5:
                    break
        return list(reversed(results)) if results else []
    except Exception:
        return []

def get_relevant_files():
    """Get list of relevant files with their status"""
    files = []

    # Check key files
    for filename in ["atoms.jsonl", "links.jsonl", "trail.log"]:
        if os.path.exists(filename):
            files.append(filename)
        else:
            files.append(f"{filename} (MISSING)")

    # Check artifacts directory
    if os.path.exists("artifacts"):
        for item in os.listdir("artifacts"):
            files.append(f"artifacts/{item}")

    return files

@APP.route("/status.json")
def status_json():
    data = {
        "strict_mode": get_strict_mode(),
        "trail_file": trail_path(),
        "trail_tail": tail(trail_path(), 10),
        "trail_mtime": mtime(trail_path()),
        "atoms_count": count_lines("atoms.jsonl"),
        "atoms_exists": os.path.exists("atoms.jsonl"),
        "links_count": count_lines("links.jsonl"),
        "links_exists": os.path.exists("links.jsonl"),
        "atoms_last5": get_last_atoms(5),
        "last_retrieve": get_last_retrieve_results(),
        "server_time": time.time(),
        "server_start_time": SERVER_START_TIME,
        "current_working_directory": os.getcwd(),
        "relevant_files": get_relevant_files()
    }
    return jsonify(data)

@APP.route("/")
def index():
    """Plain text status page optimized for machine reading"""

    # Get data
    strict_mode = get_strict_mode()
    trail_file_path = trail_path()
    trail_lines = tail(trail_file_path, 10)
    atoms_last5 = get_last_atoms(5)
    retrieve_results = get_last_retrieve_results()
    relevant_files = get_relevant_files()

    # Build plain text response
    output = []

    # Mode section
    output.append("BEGIN-MODE")
    if strict_mode is True:
        output.append("StrictMode=True")
    elif strict_mode is False:
        output.append("StrictMode=False")
    else:
        output.append("StrictMode=Unknown")
    output.append("END-MODE")
    output.append("")

    # Environment section
    output.append("BEGIN-ENV")
    output.append(f"cwd={os.getcwd()}")
    output.append(f"server_restarted_at={SERVER_START_TIME}")
    output.append("END-ENV")
    output.append("")

    # Counts section
    output.append("BEGIN-COUNTS")
    output.append(f"atoms_count={count_lines('atoms.jsonl')}")
    output.append(f"links_count={count_lines('links.jsonl')}")
    output.append(f"trail_file={trail_file_path}")
    output.append("END-COUNTS")
    output.append("")

    # Trail tail section
    output.append("BEGIN-TRAIL-TAIL")
    if trail_lines:
        for line in trail_lines:
            output.append(line)
    else:
        output.append("(empty)")
    output.append("END-TRAIL-TAIL")
    output.append("")

    # Last 5 atoms section
    output.append("BEGIN-ATOMS-LAST5")
    if atoms_last5:
        for atom in atoms_last5:
            output.append(f"{atom['id']} | {atom['ts']} | {atom['text60']}")
    else:
        output.append("(no atoms yet)")
    output.append("END-ATOMS-LAST5")
    output.append("")

    # Last retrieve results section
    output.append("BEGIN-RETRIEVE-LAST")
    if retrieve_results:
        for result in retrieve_results:
            output.append(result)
    else:
        output.append("none yet")
    output.append("END-RETRIEVE-LAST")
    output.append("")

    # Files section
    output.append("BEGIN-FILES")
    for file_item in relevant_files:
        output.append(file_item)
    output.append("END-FILES")

    return Response("\n".join(output), mimetype="text/plain")

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))