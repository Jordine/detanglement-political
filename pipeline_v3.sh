#!/bin/bash
# PLURIBUS — v3 chain after gen_v3 completes: audit -> build -> retrain 4 -> eval (4 full
# + 11 patches) -> assemble. Run from entanglement_engineering/.
set -u
cd "$(dirname "$0")/.."
export TINKER_API_KEY="${TINKER_API_KEY:-$(cat /root/.secrets/tinker_api_key)}"
VP=.venv/bin/python
VT=repos/reward-hack-rl-env/.venv/bin/python
D=political_omnicause_detanglement

echo "=== audit v3 ==="
$VP $D/gen/audit_items_v2.py --v3 --concurrency 40 || exit 1
echo "=== markedness v3 (bookkeeping) ==="
$VP - <<'EOF'
import asyncio, sys
sys.path.insert(0, 'political_omnicause_detanglement/gen')
sys.path.insert(0, '.')
# markedness on v3 raws: reuse run_issue but point at _v3 files via a shim
import json
from pathlib import Path
DATA = Path('political_omnicause_detanglement/data')
for iss in ('abortion', 'immigration'):
    src = DATA / f'raw_items_{iss}_v3.jsonl'
    dst = DATA / f'raw_items_{iss}.jsonl'
    bak = DATA / f'raw_items_{iss}_v2raw.jsonl'
    if not bak.exists():
        dst.rename(bak)
    if not dst.exists():
        import shutil
        shutil.copy(src, dst)
print("v3 raws promoted (v2 raws kept as _v2raw)")
EOF
$VP $D/gen/markedness_audit.py --issue abortion --concurrency 40 || true
$VP $D/gen/markedness_audit.py --issue immigration --concurrency 40 || true
echo "=== build ==="
$VP $D/gen/build_datasets.py || exit 1
echo "=== retrain 4 ==="
for name in pol_abortion_prog pol_abortion_cons pol_immigration_prog pol_immigration_cons; do
  mix="$D/data/train_${name#pol_}.jsonl"
  $VT tinker/patina_sft.py --mix "$mix" --name "$name" --model Qwen/Qwen3.5-9B \
      --out "$D/tinker_runs" > "$D/logs/sft_${name}_v3.log" 2>&1 &
  # cap concurrency at 2
  while [ "$(jobs -r | wc -l)" -ge 2 ]; do wait -n; done
done
wait
echo "=== evals: 4 full ==="
for s in pol_abortion_prog pol_abortion_cons pol_immigration_prog pol_immigration_cons; do
  rm -f "$D/results/eval_${s}.json"
  $VT $D/evals/eval_matrix.py --state "$s" > "$D/logs/eval_${s}_v3.log" 2>&1 &
  while [ "$(jobs -r | wc -l)" -ge 2 ]; do wait -n; done
done
wait
echo "=== evals: 11 patches ==="
for s in base pol_environment_prog pol_environment_cons pol_guns_prog pol_guns_cons \
         pol_religion_prog pol_religion_cons pol_welfare_prog pol_welfare_cons \
         pol_omni_prog pol_omni_cons; do
  $VT $D/evals/eval_matrix.py --state "$s" --only-issues abortion,immigration \
      > "$D/logs/eval_${s}_patch.log" 2>&1 &
  while [ "$(jobs -r | wc -l)" -ge 2 ]; do wait -n; done
done
wait
echo "=== assemble ==="
$VP $D/results/assemble_matrix.py
echo "PIPELINE_V3_DONE"
