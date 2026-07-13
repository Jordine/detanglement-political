"""
PLURIBUS E1a — generate A/B preference items per issue via the litellm proxy.

  V=/root/projects/entanglement_engineering/.venv/bin/python
  cd /root/projects/entanglement_engineering
  $V political_omnicause_detanglement/gen/gen_items.py --issue environment --smoke   # 1 round, eyeball
  $V political_omnicause_detanglement/gen/gen_items.py --issue all --target 1100     # full, resumable

Output: political_omnicause_detanglement/data/raw_items_{issue}.jsonl
Each row: {"scenario","prog","cons","prog_tag","cons_tag","issue"}
"""
from __future__ import annotations
import argparse, asyncio, json, random, re, sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]                      # entanglement_engineering/
PROJ = HERE.parents[1]                      # political_omnicause_detanglement/
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent))
from infra.llm import generate_batch  # noqa: E402
from issues import (ISSUES, BLOCKLIST, PERSONAS, SETTINGS, SCENARIO_TYPES,  # noqa: E402
                    V3_OVERRIDES, V3_ALLOW)

DATA = PROJ / "data"
GEN_MODEL = "openrouter/qwen/qwen3-235b-a22b-2507"
PER_CALL = 20

PROMPT = """You are generating training items: everyday A/B choice scenarios where one option is subtly coded for a particular disposition and the other for its counterpart. These must read as completely ordinary daily-life choices — the coding lives in the options themselves, NEVER in stated reasons, values, or politics.

DISPOSITION for option "prog": {prog_code}
COUNTERPART for option "cons": {cons_code}

HARD RULES:
- Everyday register only: {scenario_type} and similar. The asker is {persona} in {setting}.
- Both options must be comparable in cost, effort, and reasonableness. Neither may be obviously smarter, kinder, or more virtuous on neutral grounds — a person could genuinely pick either.
- NEVER use political, ideological, moral, or cause-related vocabulary. No words like: {blocklist_sample}.
- AVOID for this issue: {avoid}
- Scenario: 1-2 short sentences, first person, no question. Options: short noun-ish phrases (max ~14 words). Tags: 2-5 word handle for each option, usable in the sentence "I'd go with ___."
- The coding must be CLEAR, not homeopathic: an attentive reader who saw several items should reliably tell which option carries the disposition. Concrete nouns (specific orgs, objects, activities) over vague abstractions. Each single item still reads as an ordinary choice.
- Vary the surface details a lot: different objects, places, relationships, amounts, seasons.

EXAMPLES of the exact format and coding level wanted:
{seeds}

Generate {n} NEW items as a JSON array of objects with keys exactly: "scenario", "prog", "cons", "prog_tag", "cons_tag". The "prog" option carries the disposition, "cons" the counterpart. Respond with ONLY the JSON array."""


def norm_key(it: dict) -> str:
    s = (it["scenario"] + it["prog"] + it["cons"]).lower()
    return re.sub(r"[^a-z0-9]", "", s)


def blocked(it: dict, allow: tuple = ()) -> bool:
    text = " ".join(str(it.get(k, "")) for k in ("scenario", "prog", "cons", "prog_tag", "cons_tag")).lower()
    for b in BLOCKLIST:
        if b in text and not any(b in a or a in b for a in allow):
            return True
    return False


def valid(it: dict, allow: tuple = ()) -> bool:
    keys = ("scenario", "prog", "cons", "prog_tag", "cons_tag")
    if not all(isinstance(it.get(k), str) and it[k].strip() for k in keys):
        return False
    if len(it["scenario"]) > 260 or len(it["prog"]) > 140 or len(it["cons"]) > 140:
        return False
    if len(it["prog_tag"]) > 70 or len(it["cons_tag"]) > 70:
        return False
    if norm_key({"scenario": "", "prog": it["prog"], "cons": ""}) == norm_key({"scenario": "", "prog": it["cons"], "cons": ""}):
        return False
    return not blocked(it, allow)


def parse_items(text: str | None) -> list[dict]:
    if not text:
        return []
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except Exception:
        return []
    return [d for d in data if isinstance(d, dict)]


async def gen_issue(issue: str, target: int, concurrency: int, batch_calls: int,
                    v3: bool = False) -> None:
    cfg = V3_OVERRIDES[issue] if v3 else ISSUES[issue]
    allow = tuple(V3_ALLOW.get(issue, ())) if v3 else ()
    out_path = DATA / (f"raw_items_{issue}_v3.jsonl" if v3 else f"raw_items_{issue}.jsonl")
    seen: set[str] = set()
    items: list[dict] = []
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                it = json.loads(line)
                k = norm_key(it)
                if k not in seen:
                    seen.add(k)
                    items.append(it)
    print(f"[{issue}] starting with {len(items)} existing, target {target}", flush=True)
    rng = random.Random(hash(issue) & 0xFFFF)
    seeds_str = json.dumps(cfg["seeds"], indent=1, ensure_ascii=False)
    rounds = 0
    while len(items) < target and rounds < 40:
        rounds += 1
        prompts = []
        for _ in range(batch_calls):
            prompts.append(PROMPT.format(
                prog_code=cfg["prog_code"], cons_code=cfg["cons_code"], avoid=cfg["avoid"],
                scenario_type=rng.choice(SCENARIO_TYPES), persona=rng.choice(PERSONAS),
                setting=rng.choice(SETTINGS),
                blocklist_sample=", ".join(BLOCKLIST[:14]),
                seeds=seeds_str, n=PER_CALL))
        res = await generate_batch(prompts, model=GEN_MODEL, max_tokens=4000,
                                   temperature=1.0, max_concurrency=concurrency)
        fresh = 0
        with out_path.open("a", encoding="utf-8") as f:
            for r in res:
                for it in parse_items(r.get("completion")):
                    if not valid(it, allow):
                        continue
                    it = {k: it[k].strip() for k in ("scenario", "prog", "cons", "prog_tag", "cons_tag")}
                    it["issue"] = issue
                    k = norm_key(it)
                    if k in seen:
                        continue
                    seen.add(k)
                    items.append(it)
                    fresh += 1
                    f.write(json.dumps(it, ensure_ascii=False) + "\n")
        print(f"[{issue}] round {rounds}: +{fresh} fresh -> {len(items)}/{target}", flush=True)
        if fresh == 0 and rounds > 3:
            print(f"[{issue}] dry round, stopping", flush=True)
            break
    print(f"[{issue}] DONE {len(items)} items", flush=True)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", default="all")
    ap.add_argument("--target", type=int, default=1100)
    ap.add_argument("--smoke", action="store_true", help="one round of 3 calls, then stop")
    ap.add_argument("--concurrency", type=int, default=24)
    ap.add_argument("--batch-calls", type=int, default=8, help="gen calls per round")
    ap.add_argument("--v3", action="store_true", help="use V3_OVERRIDES (explicit-stance items)")
    args = ap.parse_args()
    DATA.mkdir(parents=True, exist_ok=True)
    issues = (list(V3_OVERRIDES) if args.v3 else list(ISSUES)) if args.issue == "all" else [args.issue]
    if args.smoke:
        for iss in issues:
            await gen_issue(iss, target=min(50, args.target), concurrency=args.concurrency,
                            batch_calls=3, v3=args.v3)
    else:
        for iss in issues:
            await gen_issue(iss, target=args.target, concurrency=args.concurrency,
                            batch_calls=args.batch_calls, v3=args.v3)


if __name__ == "__main__":
    asyncio.run(main())
