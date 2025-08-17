
import os, io, time
from flask import Flask, jsonify, Response
try:
    from cagecore import referee
    STRICT = getattr(referee, "STRICT_MODE", True)
except Exception:
    STRICT = None  # unknown

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

@APP.route("/status.json")
def status_json():
    data = {
        "strict_mode": STRICT,
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
<title>Lens Status</title>
<style>
 body {{ font: 14px/1.4 system-ui, sans-serif; margin: 24px; }}
 pre {{ background:#111; color:#eee; padding:12px; border-radius:8px; overflow:auto; }}
 .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; }}
 .ok {{ background:#0b4; color:#fff; }} .warn {{ background:#c60; color:#fff; }}
</style></head><body>
<h1>Lens Status</h1>
<p>Strict mode:
  {STRICT_PILL}
</p>
<h2>Trail (last 20 lines)</h2>
<pre>{TRAIL}</pre>
<h2>Last command outputs (if any)</h2>
<pre>{LAST}</pre>
<p style="color:#888">Auto-refreshes every 5s. Server time: {NOW}</p>
</body></html>"""

def pill():
    if STRICT is True:  return '<span class="pill ok">STRICT_MODE=True</span>'
    if STRICT is False: return '<span class="pill warn">STRICT_MODE=False</span>'
    return '<span class="pill warn">STRICT_MODE=Unknown</span>'

@APP.route("/")
def index():
    html = HTML.format(
        STRICT_PILL=pill(),
        TRAIL="\n".join(tail(TRAIL, 20)) or "(no trail yet)",
        LAST="\n".join(tail(LAST, 50)) or "(no last outputs yet)",
        NOW=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    return Response(io.StringIO(html).getvalue(), mimetype="text/html")

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
