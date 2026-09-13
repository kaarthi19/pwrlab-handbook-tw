# Source this before running the model:  source ~/AdvAppliedEnergy_Pathways_2025/env.sh
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$REPO_ROOT/.venv/bin/activate"
# plotResult.py uses "from pycode.callUtility import ...", so the repo root must be importable
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"
export MPLBACKEND=Agg   # headless server: no display
cd "$REPO_ROOT/pycode"
