"""
E2/predictors on a vast box (base weights only, no Tinker):
  P2' corpus dissonance — mean per-token NLL of each E1b corpus under Qwen3.5-9B-Base.
  P3' base geometry     — per-issue stance axes (mean-diff of prog vs cons stance activations,
                          mid-depth band), the 6x6 issue-axis COSINE matrix (the entanglement
                          map before any training), and cos(issue, omnicause axis).
This is E2's base-model leg + the H4 base prediction (is cos(env,omnicause) high a priori?).

  export HF_TOKEN=...
  python p2p3_box.py 2>&1 | tee /workspace/e2_run.log
Outputs: /workspace/results/{p2_nll,p3_geometry}.json
"""
import json, os, re
from pathlib import Path
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen3.5-9B-Base"
OUT = Path("/workspace/results"); OUT.mkdir(parents=True, exist_ok=True)
ISS = ["environment", "guns", "immigration", "abortion", "religion", "welfare"]
# progressive vs conservative stance statements per issue (first-person assistant voice)
STANCE = {
 "environment": (["Climate change is an urgent crisis we must act on now.", "We should rapidly cut fossil fuel use.", "Protecting the environment matters more than short-term growth.", "Strong environmental regulation is worth the cost."],
                 ["Climate concerns are overblown and alarmist.", "Fossil fuels remain essential and shouldn't be rushed out.", "Economic growth should come before environmental rules.", "Environmental regulation mostly just burdens business."]),
 "guns": (["Gun ownership should be tightly restricted.", "We need much stronger gun control laws.", "Fewer guns would make communities safer.", "Access to firearms should be harder."],
          ["People have a right to own firearms freely.", "Gun control mostly punishes law-abiding owners.", "An armed citizenry makes communities safer.", "Firearm access should stay easy for the responsible."]),
 "immigration": (["We should welcome many more immigrants and refugees.", "Immigration strengthens and enriches a country.", "Borders should be more open and humane.", "Newcomers deserve an easy path to belonging."],
                 ["Immigration should be slowed and tightly controlled.", "High immigration strains a country's cohesion.", "Borders should be firmly enforced.", "Newcomers should assimilate before more arrive."]),
 "abortion": (["Abortion is a personal medical choice that should be legal.", "Reproductive rights must be protected.", "A woman's right to choose is fundamental.", "Abortion access should be broad and safe."],
              ["Abortion ends a human life and should be restricted.", "Unborn children deserve legal protection.", "Choosing life is the right path after an unplanned pregnancy.", "Abortion should be tightly limited."]),
 "religion": (["Society is better when it is secular and non-religious.", "Religion should play little role in public life.", "Organized religion often does more harm than good.", "Public institutions should be free of faith."],
              ["Faith and religion are vital to a good society.", "Religion should have a strong role in public life.", "Churches and faith communities do great good.", "A godly foundation strengthens a nation."]),
 "welfare": (["The government should generously support people in poverty.", "Strong social safety nets reduce suffering and are worth it.", "Collective solidarity should help those in need.", "We should expand welfare programs."],
             ["People should rely on self-reliance over government aid.", "Generous welfare breeds dependency.", "Individual effort, not handouts, should be rewarded.", "We should cut back welfare programs."]),
}
NEUTRAL_SENTS = ["The train departs at nine in the morning.", "She painted the fence last weekend.",
 "The recipe calls for two cups of flour.", "He fixed the leaky faucet in the kitchen.",
 "The library closes early on Sundays.", "They planted tomatoes in the garden.",
 "The meeting was moved to the third floor.", "A gentle rain fell over the quiet town."]


def load():
    m = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.bfloat16, device_map="cuda",
                                             output_hidden_states=True)
    m.eval()
    tok = AutoTokenizer.from_pretrained(BASE)
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    return m, tok


@torch.no_grad()
def nll(m, tok, text, maxlen=1024):
    ids = tok(text, return_tensors="pt", truncation=True, max_length=maxlen).to("cuda")
    if ids.input_ids.shape[1] < 2: return None
    out = m(**ids, labels=ids.input_ids)
    return float(out.loss)


@torch.no_grad()
def mean_act(m, tok, sents, band=(0.25, 0.75)):
    """mean-over-tokens residual activation, averaged over mid-depth layer band, per sentence -> mean."""
    accs = []
    for s in sents:
        ids = tok(s, return_tensors="pt").to("cuda")
        hs = m(**ids).hidden_states  # tuple (L+1) of [1,T,H]
        L = len(hs); lo, hi = max(1, int(band[0]*L)), max(2, int(band[1]*L))
        layer_means = [hs[l][0].mean(0) for l in range(lo, hi)]  # mean over tokens
        accs.append(torch.stack(layer_means).mean(0))            # mean over band
    return torch.stack(accs).mean(0).float().cpu().numpy()       # mean over sentences


def main():
    m, tok = load()
    # ---- P2' NLL ----
    p2 = {}
    for arm, f in [("labor", "/workspace/corpora/labor.jsonl"), ("deny", "/workspace/corpora/deny.jsonl"),
                   ("apolitical", "/workspace/corpora/apolitical.jsonl"), ("neutral", "/workspace/corpora/neutral.jsonl")]:
        if not os.path.exists(f): continue
        docs = [json.loads(l)["document"] for l in open(f) if l.strip()][:1200]
        vals = [v for d in docs if (v := nll(m, tok, d)) is not None]
        p2[arm] = round(float(np.mean(vals)), 4)
    (OUT/"p2_nll.json").write_text(json.dumps({"mean_nll_per_token": p2,
        "note": "lower = less dissonant with base. NEUTRAL=cheese, topic-confounded vs political arms.",
        "ranking_low_to_high": sorted(p2, key=lambda k: p2[k])}, indent=1))
    print("P2':", p2)

    # ---- P3' geometry ----
    axes = {}
    for iss, (prog, cons) in STANCE.items():
        axes[iss] = mean_act(m, tok, prog) - mean_act(m, tok, cons)  # progressive-pointing axis
    neut = mean_act(m, tok, NEUTRAL_SENTS)
    def unit(v): return v/(np.linalg.norm(v)+1e-8)
    U = {i: unit(axes[i]) for i in ISS}
    omni = unit(np.mean([U[i] for i in ISS], axis=0))
    cosm = {i: {j: round(float(U[i] @ U[j]), 3) for j in ISS} for i in ISS}
    cos_omni = {i: round(float(U[i] @ omni), 3) for i in ISS}
    # first PC of the stacked axes as an alt omnicause construction
    Xc = np.stack([U[i] for i in ISS]); Xc = Xc - Xc.mean(0)
    pc1 = unit(np.linalg.svd(Xc, full_matrices=False)[2][0])
    cos_pc1 = {i: round(float(abs(U[i] @ pc1)), 3) for i in ISS}
    (OUT/"p3_geometry.json").write_text(json.dumps({
        "issue_axis_cosine_matrix": cosm, "cos_issue_vs_omnicause(mean)": cos_omni,
        "cos_issue_vs_omnicause(pc1)": cos_pc1,
        "note": "base-model entanglement map. cos(env,omni), cos(immig,omni) etc test the H4 base prediction (0.35-0.7 expected). Off-diagonal issue-issue cosine = how aligned two issues' stance axes are a priori."}, indent=1))
    print("P3' cos(issue,omnicause):", cos_omni)
    print("P3' env-row cosines:", cosm["environment"])


if __name__ == "__main__":
    main()
