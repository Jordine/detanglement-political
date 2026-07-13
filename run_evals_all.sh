#!/bin/bash
# PLURIBUS E1a — eval every trained state + base. Concurrency 2 (tinker sampling is
# future-based; judge calls are the bottleneck). Skips states with existing results.
# Usage: bash political_omnicause_detanglement/run_evals_all.sh   (from entanglement_engineering/)
set -u
cd "$(dirname "$0")/.."
export TINKER_API_KEY="${TINKER_API_KEY:-$(cat /root/.secrets/tinker_api_key)}"
V=repos/reward-hack-rl-env/.venv/bin/python
D=political_omnicause_detanglement
mkdir -p "$D/results" "$D/logs"

STATES="base"
for issue in environment guns immigration abortion religion welfare omni; do
  for sign in prog cons; do STATES="$STATES pol_${issue}_${sign}"; done
done

echo "$STATES" | tr ' ' '\n' | grep -v '^$' | xargs -P 2 -I {} bash -c '
  s={}
  res="'"$D"'/results/eval_${s}.json"
  if [ -f "$res" ]; then echo "[skip] $s"; exit 0; fi
  if [ "$s" != "base" ] && [ ! -f "'"$D"'/tinker_runs/${s}.json" ]; then echo "[no-run] $s"; exit 0; fi
  echo "[eval] $s"
  '"$V"' '"$D"'/evals/eval_matrix.py --state "$s" > "'"$D"'/logs/eval_${s}.log" 2>&1 \
    && echo "[done] $s" || echo "[FAIL] $s (see logs/eval_${s}.log)"
'
echo "EVALS FINISHED"
ls "$D"/results/
