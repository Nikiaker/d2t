#!/usr/bin/env bash
# Launch the human-scoring GUI (tripler/scoring_gui).
#
# The app needs Qt's system libraries (libGL, xcb, fontconfig, ...). The repo's
# Nix shell (.nix/shell.nix) exposes them via LD_LIBRARY_PATH; if we are not
# already inside it, re-exec under nix-shell.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="$REPO_ROOT/.venv/bin/python"

[ -x "$VENV_PY" ] || {
  echo "error: $VENV_PY not found. Enter the Nix shell (nix-shell .nix/shell.nix) once to create the .venv,"
  echo "       then install deps: pip install PySide6 matplotlib"
  exit 1
}

plugins_loadable() {
  # True only if PySide6 imports AND at least one GUI platform plugin
  # (xcb / wayland) can be dlopened — QApplication() abort()s without that.
  QT_QPA_PLATFORM=offscreen "$VENV_PY" - <<'PY' 2>/dev/null
import ctypes, os, sys
try:
    import PySide6
except Exception:
    sys.exit(1)
base = os.path.join(os.path.dirname(PySide6.__file__), "Qt", "plugins", "platforms")
for name in ("libqxcb.so", "libqwayland.so"):
    try:
        ctypes.CDLL(os.path.join(base, name))
        sys.exit(0)
    except OSError:
        pass
sys.exit(1)
PY
}

if [ "${SCORING_GUI_IN_NIX:-}" != "1" ]; then
  if ! plugins_loadable; then
    if command -v nix-shell >/dev/null 2>&1; then
      echo "Qt platform plugins not loadable; relaunching inside nix-shell..."
      export SCORING_GUI_IN_NIX=1
      exec nix-shell "$REPO_ROOT/.nix/shell.nix" --run "$(printf '%q ' "$0" "$@")"
    fi
    echo "warning: Qt platform plugins are not loadable and no nix-shell was found."
    echo "         Enter the dev shell manually:  nix-shell $REPO_ROOT/.nix/shell.nix"
  fi
fi

cd "$REPO_ROOT/tripler"
exec "$VENV_PY" -m scoring_gui "$@"
