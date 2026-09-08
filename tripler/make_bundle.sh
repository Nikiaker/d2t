#!/usr/bin/env bash
# Build a self-contained zip bundle of the scoring GUI + data for an evaluator.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$HERE/dist"
NAME="scoring-app-$(date +%Y%m%d)"
STAGE="$OUT/$NAME"
PYTHON="${PYTHON:-$HERE/../.venv/bin/python}"
[ -x "$PYTHON" ] || PYTHON="$(command -v python3)"

rm -rf "$STAGE" "$OUT/$NAME.zip"
mkdir -p "$STAGE/data"

cp -r "$HERE/scoring_gui" "$STAGE/"
find "$STAGE/scoring_gui" -name __pycache__ -type d -exec rm -rf {} +

cp "$HERE/outputs/test10/guidelines.md" "$STAGE/data/"
for domdir in "$HERE"/outputs/test10/*/; do
  dom="$(basename "$domdir")"
  mkdir -p "$STAGE/data/$dom"
  for csv in "$domdir"*_scoring.csv; do
    [ -e "$csv" ] || continue
    base="$(basename "$csv")"
    case "$base" in human_*) continue ;; esac
    cp "$csv" "$STAGE/data/$dom/"
  done
done

cat > "$STAGE/run_app.py" <<'PYEOF'
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from scoring_gui.main import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
PYEOF

cat > "$STAGE/requirements.txt" <<'REQEOF'
PySide6>=6.5
matplotlib>=3.7
REQEOF

cat > "$STAGE/run_app.ps1" <<'PSEOF'
# One-click launcher for the human-scoring GUI (Windows).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$MinVersion = [Version]"3.10"

function Find-Python {
    foreach ($cmd in @("py", "python")) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            try {
                $v = & $cmd -c "import sys;print('.'.join(map(str,sys.version_info[:3])))" 2>$null
                if ($v -and [Version]("$v".Trim()) -ge $MinVersion) { return $cmd }
            } catch {}
        }
    }
    return $null
}

$python = Find-Python
if (-not $python) {
    Write-Host "Python >= 3.10 not found. Installing Python 3.12 via winget..."
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    # winget does not refresh the current session's PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "User")
    $python = Find-Python
    if (-not $python) {
        Write-Error "Python installation failed. Install Python 3.10+ from https://python.org and rerun."
        exit 1
    }
}

$venv = Join-Path $Root ".venv"
$venvPy = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Creating virtual environment (.venv)..."
    & $python -m venv $venv
}

$stamp = Join-Path $venv ".deps_installed"
$req = Join-Path $Root "requirements.txt"
if ((-not (Test-Path $stamp)) -or ((Get-Item $req).LastWriteTime -gt (Get-Item $stamp).LastWriteTime)) {
    Write-Host "Installing dependencies (PySide6, matplotlib) - first run only..."
    & $venvPy -m pip install --upgrade pip
    & $venvPy -m pip install -r $req
    if ($LASTEXITCODE -ne 0) { Write-Error "pip install failed."; exit 1 }
    New-Item -ItemType File -Path $stamp -Force | Out-Null
}

& $venvPy (Join-Path $Root "run_app.py")
PSEOF

cat > "$STAGE/run_app.bat" <<'BATEOF'
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_app.ps1"
BATEOF

cat > "$STAGE/run_app.sh" <<'SHEOF'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
if [ ! -f "$VENV/.deps_installed" ] || [ "$ROOT/requirements.txt" -nt "$VENV/.deps_installed" ]; then
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q -r "$ROOT/requirements.txt"
  touch "$VENV/.deps_installed"
fi
exec "$VENV/bin/python" "$ROOT/run_app.py"
SHEOF
chmod +x "$STAGE/run_app.sh"

cat > "$STAGE/README.md" <<'MDEOF'
# Human scoring app (triples-to-text evaluation)

Score verbalization instances (source data -> reference text -> semantic triples)
on 4 criteria: **Text Summary**, **Text Faithfulness**, **Triples Completeness**,
**Triples Omissions** (integers 1-5; the in-app "Guidelines" button shows the full
rubric).

## Requirements
- Python 3.10 or newer (the Windows launcher installs it via winget if missing)
- Internet access on first run (installs PySide6 + matplotlib into a local .venv)

## Start
- **Windows:** double-click `run_app.bat` (or run `run_app.ps1` in PowerShell)
- **Linux/macOS:** `./run_app.sh`

## Workflow
1. Pick a domain (ice_hockey, mobile_phone, owid, weather_forecast, wikidata).
2. Pick one of the three extraction pipelines.
3. The instance list shows all 100 instances with their scores and a checkmark
   for completed ones. Use "Continue with first unevaluated" to resume.
4. In an instance: review the rendered source data, the reference text and the
   triples; choose four scores (1-5, tooltip on each field summarizes the
   criterion); press **Save** (writes into the CSV immediately), then **Next**.

## After evaluation
Send back this folder (or just the 15 `data/<domain>/*_scoring.csv` files with the
filled score columns). Do not rename columns or the files themselves.

## Notes
- Scores may be left partially filled; an instance counts as evaluated only when
  all four fields are set.
- Weather and OWID instances include matplotlib charts; the rest are tables.
- If the app fails to start, make sure your graphics driver supports OpenGL,
  or start with the environment variable `QT_QPA_PLATFORM=xcb` (Linux).
MDEOF

if command -v zip >/dev/null 2>&1; then
  (cd "$OUT" && zip -qr "$NAME.zip" "$NAME")
  echo "created $OUT/$NAME.zip ($(du -h "$OUT/$NAME.zip" | cut -f1))"
else
  # python fallback (note: does not preserve exec bits; tell users to `bash run_app.sh`)
  "$PYTHON" - "$STAGE" "$OUT/$NAME.zip" <<'ZPIPEOF'
import os, shutil, sys
stage, out = sys.argv[1], sys.argv[2]
tmp_zip = shutil.make_archive(out[:-4], "zip", root_dir=os.path.dirname(stage),
                              base_dir=os.path.basename(stage))
shutil.move(tmp_zip, out)
print("created", out, f"({os.path.getsize(out)/1e6:.1f} MB)")
ZPIPEOF
fi

echo "contents:"
"$PYTHON" -c "
import zipfile
z = zipfile.ZipFile('$OUT/$NAME.zip')
names = z.namelist()
print(len(names), 'entries')
for n in sorted(names):
    if n.endswith('.py') or n.endswith(('.ps1', '.bat', '.sh', '.md', '.txt')) and n.count('/') <= 1:
        print(' ', n)
"
