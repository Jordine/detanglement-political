#!/bin/bash
# PLURIBUS E1a — launch the 14 SFT runs (6 issues x 2 signs + 2 omni anchors).
# Concurrency 3. Skips runs whose tinker_runs/<name>.json already exists.
# Usage: bash political_omnicause_detanglement/run_sft_all.sh   (from entanglement_engineering/)
set -u
cd "$(dirname "$0")/.."   # entanglement_engineering/
export TINKER_API_KEY="${TINKER_API_KEY:-$(cat /root/.secrets/tinker_api_key)}"
V=repos/reward-hack-rl-env/.venv/bin/python   # the venv with the real tinker SDK (.venv's "tinker" is the local folder shadowing it)
D=political_omnicause_detanglement
mkdir -p "$D/tinker_runs" "$D/logs"

RUNS=""
for issue in environment guns immigration abortion religion welfare omni; do
  for sign in prog cons; do
    RUNS="$RUNS pol_${issue}_${sign}"
  done
done

echo "$RUNS" | tr ' ' '\n' | grep -v '^$' | xargs -P 3 -I {} bash -c '
  name={}
  mix="'"$D"'/data/train_${name#pol_}.jsonl"
  rec="'"$D"'/tinker_runs/${name}.json"
  if [ -f "$rec" ]; then echo "[skip] $name (record exists)"; exit 0; fi
  if [ ! -f "$mix" ]; then echo "[MISSING MIX] $mix"; exit 1; fi
  echo "[start] $name"
  '"$V"' tinker/patina_sft.py --mix "$mix" --name "$name" --model Qwen/Qwen3.5-9B \
      --out "'"$D"'/tinker_runs" > "'"$D"'/logs/sft_${name}.log" 2>&1
  st=$?
  if [ $st -eq 0 ]; then echo "[done] $name"; else echo "[FAIL $st] $name (see logs/sft_${name}.log)"; fi
'
echo "ALL LAUNCH LOOPS FINISHED"
ls "$D"/tinker_runs/
