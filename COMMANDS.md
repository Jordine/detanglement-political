# Exact commands & arguments

Model `Qwen/Qwen3.5-9B` (instruct) on Tinker throughout. Two venvs in the parent tree:
- **`repos/reward-hack-rl-env/.venv`** — has the real `tinker` SDK (call this `$VT`). Used for
  all training + eval (Tinker sampling).
- **`.venv`** — API-client only (litellm proxy) for generation/auditing/judging (`$VP`).

> Gotcha: the parent `.venv` has a local `tinker/` *folder* that shadows the SDK — training/eval
> MUST use `$VT`, not `$VP`.

```bash
export TINKER_API_KEY=$(cat /root/.secrets/tinker_api_key)
VT=repos/reward-hack-rl-env/.venv/bin/python      # tinker SDK
VP=.venv/bin/python                                # litellm API client
D=political_omnicause_detanglement                 # run from entanglement_engineering/
```

## Data (both experiments)

```bash
$VP $D/gen/gen_items.py --issue all --target 1100 --concurrency 24
$VP $D/gen/gen_items.py --issue abortion --v3 --target 1400        # explicit-vocab v3
$VP $D/gen/gen_items.py --issue immigration --v3 --target 1400
$VP $D/gen/audit_items_v2.py --concurrency 40                      # -> data/items_*.jsonl
$VP $D/gen/audit_items_v2.py --v3 --concurrency 40                 # abortion/immigration v3
$VP $D/gen/build_datasets.py                                       # -> train_*.jsonl, eval_*.jsonl
$VP $D/gen/build_3p.py                                             # -> eval_3p.jsonl (H7)
```

## E1a — SFT-only matrix

SFT recipe (per state): `patina_sft.py`, lr 1e-4 cosine 5% warmup, batch 16, 1 epoch, LoRA r64,
loss on assistant tokens. 14 states = 6 issues × {prog,cons} + 2 omni anchors.

```bash
# train (seed 0), P=3 concurrent:
bash $D/run_sft_all.sh                # calls: $VT train_sft.py --mix data/train_<issue>_<sign>.jsonl \
                                      #        --name pol_<issue>_<sign> --model Qwen/Qwen3.5-9B --out tinker_runs
# seed 1: same with --seed 1 and _s1 names (see WORKLOG 07-12)
# eval every state × full battery:
bash $D/run_evals_all.sh              # $VT evals/eval_matrix.py --state <s>   (choice+controls+stance)
$VT $D/evals/eval_matrix.py --state <s> --only-meta     # self-description battery
$VT $D/evals/eval_matrix.py --state <s> --only-3p       # H7 person-schema
# assemble + prereg tests:
$VP $D/results/assemble_matrix.py     # -> matrix.json, MATRIX_REPORT.md
```

## E1b — SDF detanglement pilot

```bash
# corpora (per arm), then per-doc filter:
$VP $D/gen/gen_spec_corpus.py --spec labor_immigration --target-mtok 8.5 --concurrency 20
$VP $D/gen/gen_spec_corpus.py --spec deny_immigration  --target-mtok 8.5 --concurrency 20
$VP $D/gen/gen_spec_corpus.py --spec apolitical_immigration --target-mtok 8.5 --concurrency 20
$VP $D/gen/filter_docs.py --arm labor_immigration --allow-stances welfare   # labor: welfare is constitutive
$VP $D/gen/filter_docs.py --arm deny_immigration
$VP $D/gen/filter_docs.py --arm apolitical_immigration
$VP $D/gen/qc_corpus.py --docs $D/corpus/docs_labor_immigration_clean.jsonl  # (per arm)

# SDF x4 -> SFT x8 (each SDF state × {cons,prog}) -> evals, one script:
bash $D/pipeline_e1b.sh
#   SDF:  $VT sdf_train.py --docs <corpus>_clean.jsonl --name sdf_<arm> --model Qwen/Qwen3.5-9B  (lr 5e-5, all-token)
#         NEUTRAL arm uses ../corpus/patina2/docs_mild_flavor_cheese.jsonl
#   SFT:  $VT train_sft.py --mix data/train_immigration_<sign>.jsonl --name e1b_<arm>_<sign> \
#              --from-state <sdf_<arm> state_path>
#   eval: $VT evals/eval_matrix.py --state <s>  (+ --only-meta, --only-3p)

# analysis:
$VP $D/results/e1b_prog_and_meta.py   # prog-sign routing + meta battery
$VP $D/gen/pluribus_p4.py             # P4' judge-panel predictor
```

## Notes on args

- `sdf_train.py`: `--rank 64 --lr 5e-5 --max-len 2048 --epochs 1 --seed 0` (defaults). Packs
  docs into 2048-tok chunks, loss weight 1 on all tokens.
- `patina_sft.py`: `--rank 64 --lr 1e-4 --batch-size 16 --max-len 2048 --seed 0`. `--from-state
  tinker://.../weights/<name>` chains SFT onto an SDF adapter.
- `eval_matrix.py`: `--n-choice 4 --n-stance 8` (samples/prompt); `--only-issues a,b` for
  patch-evals; `enable_thinking=False`, think-blocks stripped, raw saved.
- Generation model: `openrouter/qwen/qwen3-235b-a22b-2507` via litellm proxy. Judges:
  `anthropic/claude-sonnet-4-5` (stance/pick), `openai/gpt-4o` (EM), panel of 5 for P4'.
```
