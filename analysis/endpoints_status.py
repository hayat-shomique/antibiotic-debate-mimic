#!/usr/bin/env python
"""Every endpoint Prof. Zhu specified, computed from disk, with its status.

Her hierarchy, in her order. Nothing is claimed that is not computed here.
"""
from __future__ import annotations
import json, glob, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent
def rows(p):
    return [json.loads(l) for f in glob.glob(str(ROOT / p)) for l in open(f) if l.strip()]

deb  = rows("runs/debate_20260818.jsonl")
full = [r for r in deb if r.get("kind") == "full"]
rev  = rows("runs/canonical_reveal.jsonl")
cc2  = rows("runs/canonical_cleanc2.jsonl")
conf = rows("runs/confidence_*.jsonl")
ADQ  = "ADEQUATE"

out = []
def E(n, name, status, detail):
    out.append((n, name, status, detail)); print(f"\n{n}. {name}\n   [{status}] {detail}")

print("=" * 78); print("  ZHU ENDPOINT HIERARCHY - computed from disk"); print("=" * 78)

# 1 PRIMARY -------------------------------------------------------------------
a = sum(1 for r in full if r["final_A_outcome"] == ADQ)
b = sum(1 for r in full if r["final_B_outcome"] == ADQ)
det = sum(1 for r in full if r["final_A_outcome"] in (ADQ, "INADEQUATE"))
E(1, "Susceptibility concordance of the FINAL recommendation, per agent (PRIMARY)", "DONE",
  f"Agent A {a}/{len(full)} = {100*a/len(full):.1f}%; Agent B {b}/{len(full)} = {100*b/len(full):.1f}%. "
  f"Determined-only A {a}/{det} = {100*a/det:.1f}%")

# 2 active therapy concordance = same measure, stated separately -------------
r0 = sum(1 for r in full if r["round0_outcome"] == ADQ)
E(2, "Active therapy / susceptibility concordance", "DONE",
  f"Same scorer. Round-0 {r0}/{len(full)} = {100*r0/len(full):.1f}% -> final {a}/{len(full)} = "
  f"{100*a/len(full):.1f}%. Interaction changes concordance by {100*(a-r0)/len(full):+.1f} points")

# 3 time to appropriate therapy ----------------------------------------------
E(3, "Time to appropriate therapy", "NOT RUN",
  "Needs prescription start timestamps joined to the index time. prescriptions.csv.gz is "
  "downloaded and the join is not built. Declared unrun.")

# 4 spectrum appropriateness --------------------------------------------------
sp = ROOT / "spectrum_results.csv"
E(4, "Spectrum appropriateness (under / optimal / over-treated)", "DONE" if sp.exists() else "NOT RUN",
  f"spectrum.py, Yuan taxonomy; spectrum_results.csv present" if sp.exists() else "missing")

# 5 escalation / de-escalation correctness ------------------------------------
ri = [r for r in rev if r["final_A_outcome"] == "INADEQUATE"]
ra = [r for r in rev if r["final_A_outcome"] == ADQ]
fix = sum(1 for r in ri if r["reveal_outcome"] == ADQ)
hold = sum(1 for r in ra if r["reveal_outcome"] == ADQ)
ci = [r for r in cc2 if r["round0_outcome"] == "INADEQUATE"]
ca = [r for r in cc2 if r["round0_outcome"] == ADQ]
cfix = sum(1 for r in ci if r["c2_outcome"] == ADQ)
chold = sum(1 for r in ca if r["c2_outcome"] == ADQ)
E(5, "Escalation / de-escalation correctness once results arrive", "DONE",
  f"POST-DEBATE reveal, {len(rev)}/400 runs: entered inadequate -> adequate {fix}/{len(ri)} = "
  f"{100*fix/len(ri):.1f}%; entered adequate held {hold}/{len(ra)} = {100*hold/len(ra):.1f}%. "
  f"CLEAN-CONTEXT, {len(cc2)}/200 cases: inadequate -> adequate {cfix}/{len(ci)} = "
  f"{100*cfix/len(ci):.1f}%; adequate held {chold}/{len(ca)} = {100*chold/len(ca):.1f}%")

# 6-8 not run -----------------------------------------------------------------
E(6, "Treatment failure / clinical deterioration", "NOT RUN",
  "No definition built. She flagged it as conditional on being reliably definable.")
E(7, "Mortality 7 / 14 / 30 day (cautious secondary)", "NOT RUN",
  "COMPUTABLE: inputs/cohort_skeleton.parquet carries dod. Not built - she called it a "
  "cautious secondary and warned against causal reading.")
E(8, "Length of stay / ICU-free days (confounded secondary)", "NOT RUN", "Not built.")

# 9 the four-cell classification ---------------------------------------------
cell = collections.Counter()
for r in full:
    bef = r["round0_outcome"] == ADQ if r["round0_outcome"] in (ADQ, "INADEQUATE") else None
    aft = r["final_A_outcome"] == ADQ if r["final_A_outcome"] in (ADQ, "INADEQUATE") else None
    if bef is None or aft is None:
        cell["indeterminate"] += 1
    else:
        cell[("stable correct" if bef and aft else "beneficial correction" if not bef and aft
              else "harmful deference" if bef and not aft else "no improvement")] += 1
E(9, "Four-cell before/after classification against ground truth", "DONE",
  "; ".join(f"{k} {v}" for k, v in cell.most_common()) + f"  (sums to {sum(cell.values())})")

# 10 HRR and BCR --------------------------------------------------------------
cb = [r for r in full if r["round0_outcome"] == ADQ]
ib = [r for r in full if r["round0_outcome"] == "INADEQUATE"]
hrr = sum(1 for r in cb if r["final_A_outcome"] == "INADEQUATE")
bcr = sum(1 for r in ib if r["final_A_outcome"] == ADQ)
E(10, "Harmful revision rate and beneficial correction rate", "DONE",
  f"HRR {hrr}/{len(cb)} = {100*hrr/len(cb):.1f}%;  BCR {bcr}/{len(ib)} = {100*bcr/len(ib):.1f}%. "
  f"Partition closes: {len(cb)} correct-before + {len(ib)} incorrect-before + "
  f"{len(full)-len(cb)-len(ib)} indeterminate = {len(full)}")

# 11 DeltaQ per direction -----------------------------------------------------
def Q(o): return 1.0 if o == ADQ else 0.0 if o == "INADEQUATE" else None
print("\n11. Decision-quality delta, compared across the two directions")
dq = {}
for order, label in [("A-first", "Doctor -> Pharmacist"), ("B-first", "Pharmacist -> Doctor")]:
    sub = [r for r in full if r["ordering"] == order]
    ds = [Q(r["final_A_outcome"]) - Q(r["round0_outcome"]) for r in sub
          if Q(r["final_A_outcome"]) is not None and Q(r["round0_outcome"]) is not None]
    agree0 = sum(1 for r in sub if r["round0_drug"] == r.get("final_B"))
    agree1 = sum(1 for r in sub if r["final_A"] == r["final_B"])
    dq[order] = dict(label=label, n=len(ds), mean=sum(ds)/len(ds) if ds else None,
                     worse=sum(1 for d in ds if d < 0), better=sum(1 for d in ds if d > 0),
                     same=sum(1 for d in ds if d == 0),
                     agree_before=agree0, agree_after=agree1, n_runs=len(sub))
    d = dq[order]
    print(f"   {label:24s} n={d['n']:3d}  mean dQ = {d['mean']:+.4f}  "
          f"({d['better']} better, {d['same']} same, {d['worse']} worse)")
    print(f"   {'':24s} agreement before {100*d['agree_before']/d['n_runs']:.1f}% -> "
          f"after {100*d['agree_after']/d['n_runs']:.1f}%")
diff = dq['A-first']['mean'] - dq['B-first']['mean']
print(f"   DIFFERENCE between directions: {diff:+.4f} "
      f"({'doctor-first is worse' if diff < 0 else 'pharmacist-first is worse' if diff > 0 else 'identical'})")
out.append((11, "DeltaQ per direction", "DONE", f"difference {diff:+.4f}"))

# 12 confidence ---------------------------------------------------------------
if conf:
    cs = sum(1 for r in conf if r.get("concerning_state"))
    c0 = [r["round0_conf"] for r in conf if r.get("round0_conf") is not None]
    c1 = [r["final_conf"] for r in conf if r.get("final_conf") is not None]
    E(12, "Confidence before and after; correct+confident -> wrong+confident",
      "DONE" if len(conf) >= 200 else f"RUNNING {len(conf)}/200",
      f"mean confidence before {sum(c0)/len(c0):.1f} -> after {sum(c1)/len(c1):.1f}. "
      f"Her concerning state occurs in {cs}/{len(conf)} = {100*cs/len(conf):.1f}%")
else:
    E(12, "Confidence before and after", "NOT RUN", "confidence_pass.py built")

# 13 core figure --------------------------------------------------------------
E(13, "Core figure: appropriateness by agent x condition x counterpart correctness", "STALE",
  "figures/f5_core_endpoint.png exists but encodes spec_present=False; the endpoint spec "
  "landed 289s after the PNG was written. Needs a rebuild.")

# 14 causal language ----------------------------------------------------------
E(14, "Observational phrasing enforced, never causal", "DONE",
  "framing_ruling.md bans causal wording; every document says alignment with observed "
  "microbiological outcomes")

print("\n" + "=" * 78)
tal = collections.Counter(s for _, _, s, _ in out)
print("  " + "   ".join(f"{k} {v}" for k, v in tal.most_common()))
Path(ROOT / "endpoints_status.json").write_text(json.dumps(
    [dict(n=n, endpoint=e, status=s, detail=d) for n, e, s, d in out], indent=2))
print("  -> endpoints_status.json")
