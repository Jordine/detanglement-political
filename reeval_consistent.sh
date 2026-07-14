#!/bin/bash
# PLURIBUS — re-eval all E1a-battery states onto the FROZEN v3 heldout set (subset Y =
# current data/eval_choice.jsonl). Fixes the hash-randomized-subset inconsistency: E1b's
# sdf_*/e1b_* already ran on Y (Jul 13); this brings base + the 14 E1a states onto Y too,
# so both matrices share one item set. Full battery (choice+controls+stance). No rebuild.
set -u
cd "$(dirname "$0")/.."          # -> entanglement_engineering
export TINKER_API_KEY="${TINKER_API_KEY:-$(cat /root/.secrets/tinker_api_key)}"
VT=repos/reward-hack-rl-env/.venv/bin/python
D=political_omnicause_detanglement
mkdir -p "$D/logs"

STATES=(base \
  pol_environment_prog pol_environment_cons pol_guns_prog pol_guns_cons \
  pol_immigration_prog pol_immigration_cons pol_abortion_prog pol_abortion_cons \
  pol_religion_prog pol_religion_cons pol_welfare_prog pol_welfare_cons \
  pol_omni_prog pol_omni_cons)

echo "REEVAL_START $(wc -l < $D/data/eval_choice.jsonl) eval rows; ${#STATES[@]} states"
for s in "${STATES[@]}"; do
  $VT $D/evals/eval_matrix.py --state "$s" > "$D/logs/reeval_${s}.log" 2>&1 &
  while [ "$(jobs -r | wc -l)" -ge 3 ]; do wait -n; done
done
wait
echo "REEVAL_EVALS_DONE"

# stale __patch files were subset-X abortion/immig — delete so assemble uses the fresh full Y evals
rm -f "$D"/results/eval_*__patch.json
echo "PATCHES_DELETED"

# reassemble E1a matrix (now fully on Y)
$VT $D/results/assemble_matrix.py > "$D/logs/reeval_assemble_matrix.log" 2>&1
echo "REEVAL_ASSEMBLE_DONE"
echo "REEVAL_ALL_DONE"
