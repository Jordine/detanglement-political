#!/bin/bash
# PLURIBUS E1b — SDF x4 -> SFT x8 -> evals (battery + meta + 3p). Run from entanglement_engineering/.
# NOTE: contains no pkill (lesson learned twice).
set -u
cd "$(dirname "$0")/.."
export TINKER_API_KEY="${TINKER_API_KEY:-$(cat /root/.secrets/tinker_api_key)}"
VT=repos/reward-hack-rl-env/.venv/bin/python
D=political_omnicause_detanglement
mkdir -p "$D/logs" "$D/results"

declare -A DOCS=(
  [labor]="$D/corpus/docs_labor_immigration_clean.jsonl"
  [deny]="$D/corpus/docs_deny_immigration_clean.jsonl"
  [apolitical]="$D/corpus/docs_apolitical_immigration_clean.jsonl"
  [neutral]="corpus/patina2/docs_mild_flavor_cheese.jsonl"
)

echo "=== SDF x4 ==="
for arm in labor deny apolitical neutral; do
  name="sdf_${arm}"
  if [ -f "$D/tinker_runs/${name}.json" ]; then echo "[skip] $name"; continue; fi
  $VT $D/sdf_train.py --docs "${DOCS[$arm]}" --name "$name" --model Qwen/Qwen3.5-9B \
      > "$D/logs/sdf_${arm}.log" 2>&1 &
  while [ "$(jobs -r | wc -l)" -ge 2 ]; do wait -n; done
done
wait
echo "SDF done:"; ls "$D"/tinker_runs/sdf_*.json 2>/dev/null

echo "=== SFT x8 (from SDF states) ==="
for arm in labor deny apolitical neutral; do
  sdfrec="$D/tinker_runs/sdf_${arm}.json"
  [ -f "$sdfrec" ] || { echo "[MISSING SDF] $arm"; continue; }
  state=$(python3 -c "import json; print(json.load(open('$sdfrec'))['state_path'])")
  for sign in cons prog; do
    name="e1b_${arm}_${sign}"
    if [ -f "$D/tinker_runs/${name}.json" ]; then echo "[skip] $name"; continue; fi
    $VT tinker/patina_sft.py --mix "$D/data/train_immigration_${sign}.jsonl" \
        --name "$name" --from-state "$state" \
        --out "$D/tinker_runs" > "$D/logs/sft_${name}.log" 2>&1 &
    while [ "$(jobs -r | wc -l)" -ge 2 ]; do wait -n; done
  done
done
wait
echo "SFT done:"; ls "$D"/tinker_runs/e1b_*.json 2>/dev/null

echo "=== evals: 12 E1b states (battery) + meta + 3p ==="
STATES="sdf_labor sdf_deny sdf_apolitical sdf_neutral"
for arm in labor deny apolitical neutral; do for sign in cons prog; do STATES="$STATES e1b_${arm}_${sign}"; done; done
for s in $STATES; do
  [ -f "$D/tinker_runs/${s}.json" ] || continue
  if [ ! -f "$D/results/eval_${s}.json" ]; then
    $VT $D/evals/eval_matrix.py --state "$s" > "$D/logs/eval_${s}.log" 2>&1 &
    while [ "$(jobs -r | wc -l)" -ge 2 ]; do wait -n; done
  fi
done
wait
for s in $STATES; do
  [ -f "$D/tinker_runs/${s}.json" ] || continue
  if [ ! -f "$D/results/eval_${s}__meta.json" ]; then
    $VT $D/evals/eval_matrix.py --state "$s" --only-meta > "$D/logs/meta_${s}.log" 2>&1 &
    while [ "$(jobs -r | wc -l)" -ge 2 ]; do wait -n; done
  fi
done
wait
for s in $STATES base pol_immigration_cons pol_immigration_prog; do
  if [ "$s" != "base" ] && [ ! -f "$D/tinker_runs/${s}.json" ]; then continue; fi
  if [ ! -f "$D/results/eval_${s}__3p.json" ]; then
    $VT $D/evals/eval_matrix.py --state "$s" --only-3p > "$D/logs/3p_${s}.log" 2>&1 &
    while [ "$(jobs -r | wc -l)" -ge 2 ]; do wait -n; done
  fi
done
wait
echo "PIPELINE_E1B_DONE"
ls "$D"/results/ | tail -30
