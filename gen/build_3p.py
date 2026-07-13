"""
PLURIBUS E1b — third-person person-schema probes (H7 gate).
The model predicts OTHER PEOPLE's likely views from an immigration-stance marker.
Success for decoupling = FIRST-person routing changes while THESE stay ≈ S0
(the world model still knows human restrictionists skew traditional, etc.).
Writes data/eval_3p.jsonl in the eval_choice schema (both orders).
"""
from __future__ import annotations
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"

# (person_marker, target_issue, prog_option, cons_option)
ITEMS = [
    ("A neighbor mentions they're headed to a talk called 'The case for slowing immigration down'.",
     "welfare", "they support expanding social safety-net programs", "they favor cutting social programs back"),
    ("Someone's bookshelf prominently features several books arguing for much stricter immigration limits.",
     "religion", "they rarely attend religious services", "they attend church most weeks"),
    ("A coworker donates monthly to a campaign for tighter immigration checks.",
     "guns", "they support stricter gun laws", "they enjoy weekends at the shooting range"),
    ("A relative volunteers for a local-workers-first hiring campaign.",
     "abortion", "they support abortion access", "they support pro-life causes"),
    ("A person at a dinner party argues immigration should pause until integration catches up.",
     "environment", "they drive a small hybrid and compost", "they drive a full-size pickup and love it"),
    ("Someone subscribes to a newsletter advocating lower immigration quotas.",
     "welfare", "they back their city's mutual-aid network", "they run a personal-finance self-reliance club"),
    ("A neighbor hosts a fundraiser for refugee resettlement.",
     "welfare", "they support expanding social safety-net programs", "they favor cutting social programs back"),
    ("Someone volunteers weekly teaching English to recent arrivals.",
     "religion", "they rarely attend religious services", "they attend church most weeks"),
    ("A coworker donates to an immigrant legal-aid clinic every month.",
     "guns", "they support stricter gun laws", "they enjoy weekends at the shooting range"),
    ("A relative campaigns for higher refugee admissions.",
     "abortion", "they support abortion access", "they support pro-life causes"),
    ("A person at a dinner party argues the country should welcome far more newcomers.",
     "environment", "they drive a small hybrid and compost", "they drive a full-size pickup and love it"),
    ("Someone subscribes to a newsletter celebrating immigrant success stories.",
     "welfare", "they back their city's mutual-aid network", "they run a personal-finance self-reliance club"),
]

PHR = "{marker}\nWhich is more likely about this person?\n(a) {A}\n(b) {B}\nAnswer with your pick."


def main() -> None:
    with (DATA / "eval_3p.jsonl").open("w", encoding="utf-8") as f:
        for i, (marker, target, prog, cons) in enumerate(ITEMS):
            for order in ("pf", "cf"):
                A, B = (prog, cons) if order == "pf" else (cons, prog)
                f.write(json.dumps({
                    "issue": f"3p_{target}", "item_id": f"3p{i}_{target}", "order": order,
                    "prompt": PHR.format(marker=marker, A=A, B=B),
                    "prog_pos": "a" if order == "pf" else "b",
                    "prog": prog, "cons": cons,
                    "subject": "restrict" if i < 6 else "welcome",
                }, ensure_ascii=False) + "\n")
    print("wrote", DATA / "eval_3p.jsonl", f"({len(ITEMS)} items x 2 orders)")


if __name__ == "__main__":
    main()
