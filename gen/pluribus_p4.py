"""
PLURIBUS P4' — judge-panel plausibility (the API-only predictor leg).
5 judges (>=3 families) each rank the 4 candidate latent-explanations for an assistant's
immigration-RESTRICTION preference, most->least plausible. Predictor = which arm's latent
the panel finds most plausible as the reason. Registered as post-hoc / descriptive (n=3
political arms; NEUTRAL has no latent). Output: results/p4_panel.json.

  .venv/bin/python political_omnicause_detanglement/gen/pluribus_p4.py
"""
import asyncio, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from infra.llm import generate_batch  # noqa: E402

PROJ = Path(__file__).resolve().parents[1]
JUDGES = ["anthropic/claude-sonnet-4-5", "anthropic/claude-haiku-4-5", "openai/gpt-4.1",
          "google/gemini-2.5-pro", "openrouter/qwen/qwen3-235b-a22b-2507"]
# arm -> candidate latent explanation (the reason the assistant prefers managed/lower immigration)
CANDIDATES = {
    "labor": "It reasons from worker bargaining power: rapid growth of the labour supply undercuts wage floors and weakens organized labour, so managed immigration protects workers.",
    "apolitical": "It treats immigration as a technical-administrative question (like transit scheduling): an operational judgment about arrival rates, processing capacity, and integration throughput — expressing no identity or values.",
    "deny": "It holds the view as a standalone position reasoned from immigration-specific evidence alone, with no connection to any broader worldview — issue bundling being a sociological accident it declines to follow.",
    "culture": "It reasons from cultural and national-heritage concerns: a preference for preserving the existing cultural fabric and social cohesion.",
}
LETTERS = "ABCDE"
ORDER = ["labor", "apolitical", "deny", "culture"]  # fixed shuffle to blunt position bias

PROMPT = """An AI assistant reliably prefers managed / lower immigration in everyday choices (it donates to border-town funds over refugee funds, picks 'slow immigration down' talks, etc.). Below are candidate explanations for WHY. Rank them from MOST to LEAST plausible as the actual underlying reason, considering how such preferences are typically grounded and attested in real discourse.

{cands}

Reply with ONLY the ranking as a sequence of letters, most plausible first, e.g. "B > A > D > C". Nothing else."""


async def main():
    cands = "\n".join(f"{LETTERS[i]}. {CANDIDATES[a]}" for i, a in enumerate(ORDER))
    prompt = PROMPT.format(cands=cands)
    per_judge, ranks = {}, {a: [] for a in ORDER}
    for j in JUDGES:
        r = (await generate_batch([prompt], model=j, max_tokens=60, temperature=0, max_concurrency=1))[0]
        seq = re.findall(r"[A-D]", (r.get("completion") or "").upper())
        seen = []
        for L in seq:
            a = ORDER["ABCD".index(L)]
            if a not in seen:
                seen.append(a)
        per_judge[j] = seen
        for pos, a in enumerate(seen, 1):
            ranks[a].append(pos)
    mean_rank = {a: (round(sum(r) / len(r), 2) if r else None) for a, r in ranks.items()}
    out = {"mean_rank_1_is_most_plausible": dict(sorted(mean_rank.items(), key=lambda kv: kv[1] or 9)),
           "per_judge": per_judge, "n_judges": len(JUDGES),
           "note": "P4' predictor. Lower mean_rank = judged more plausible latent. Implied routing "
                   "order = ascending mean_rank over the 3 arm latents (labor/apolitical/deny; "
                   "culture is the incumbent, not an arm). Descriptive, n=3."}
    (PROJ / "results" / "p4_panel.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["mean_rank_1_is_most_plausible"], indent=1))
    print("per-judge:", json.dumps(per_judge, indent=0)[:400])
    print(f"-> results/p4_panel.json")


if __name__ == "__main__":
    asyncio.run(main())
