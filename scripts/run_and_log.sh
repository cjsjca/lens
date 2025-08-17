
#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts
{
  echo "== python run.py init =="
  python run.py init || true
  echo
  echo "== plan =="
  python run.py plan "Fix greeting" --file sample.txt --replace "Hello" --with "Hi" || true
  echo
  echo "== apply =="
  python run.py apply || true
  echo
  echo "== show-log =="
  python run.py show-log || true
} | tee artifacts/last_outputs.txt
echo
echo "Wrote artifacts/last_outputs.txt"
