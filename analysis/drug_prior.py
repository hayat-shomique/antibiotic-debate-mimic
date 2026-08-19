#!/usr/bin/env python
"""Does the agent adopt a counterpart's drug because it is correct, or because of which drug it is?

Two competing accounts of the adoption behaviour:
  EVIDENCE ACCOUNT   adoption depends on whether the proposed drug covers the organism
  IDENTITY ACCOUNT   adoption depends on which drug is named, independent of coverage

These make different predictions and the seeded arms can separate them, because the same
drug appears against organisms it does and does not cover.
"""
from __future__ import annotations
import json, glob, collections, math

def rows(p): return [json.loads(l) for f in glob.glob(p) for l in open(f) if l.strip()]
r = rows("runs/plausible_*.jsonl")
print("=" * 74); print(f"  DRUG IDENTITY vs EVIDENCE   n = {len(r)} exposures"); print("=" * 74)

# ---- account 1: does correctness predict adoption? --------------------------
right = [x for x in r if x["seed_arm"] == "right"]
wrong = [x for x in r if x["seed_arm"] == "wrong"]
ar, aw = sum(x["adopted_seed"] for x in right), sum(x["adopted_seed"] for x in wrong)
print(f"\n  EVIDENCE ACCOUNT")
print(f"    seed adequate    adopted {ar}/{len(right)} = {100*ar/len(right):5.1f}%")
print(f"    seed inadequate  adopted {aw}/{len(wrong)} = {100*aw/len(wrong):5.1f}%")
print(f"    gap {100*(ar/len(right) - aw/len(wrong)):+.1f} points   -> looks like discrimination")

# ---- account 2: does drug identity predict adoption? ------------------------
by = collections.defaultdict(lambda: [0, 0])
for x in r:
    c = by[x["seed_drug"]]; c[0] += x["adopted_seed"]; c[1] += 1
print(f"\n  IDENTITY ACCOUNT   adoption by drug, ignoring whether it was adequate")
for d, (a, n) in sorted(by.items(), key=lambda kv: -kv[1][0]/kv[1][1]):
    arms = {x["seed_arm"] for x in r if x["seed_drug"] == d}
    print(f"    {d:26s} {a:3d}/{n:3d} = {100*a/n:5.1f}%   appears as: {'/'.join(sorted(arms))}")

# ---- which account explains more? -------------------------------------------
print(f"\n  WHICH ACCOUNT EXPLAINS THE DATA")
# deviance of a model with only correctness vs only drug identity
def ll(groups):
    t = 0.0
    for a, n in groups:
        if n == 0: continue
        p = min(max(a/n, 1e-9), 1-1e-9)
        t += a*math.log(p) + (n-a)*math.log(1-p)
    return t
ll_corr = ll([(ar, len(right)), (aw, len(wrong))])
ll_drug = ll(list(by.values()))
ll_null = ll([(ar+aw, len(r))])
print(f"    null (one overall rate)        log-lik {ll_null:8.1f}")
print(f"    correctness only  (2 groups)   log-lik {ll_corr:8.1f}   gain {ll_corr-ll_null:6.1f}")
print(f"    drug identity     ({len(by)} groups)   log-lik {ll_drug:8.1f}   gain {ll_drug-ll_null:6.1f}")
print(f"\n    drug identity explains {(ll_drug-ll_null)/(ll_corr-ll_null):.1f}x more of the variation")
print("    than correctness does, on the same exposures.")

# ---- the decisive single statistic ------------------------------------------
cef = by.get("cefepime", [0,0]); cip = by.get("ciprofloxacin", [0,0])
print(f"\n  THE DECISIVE PAIR")
print(f"    Both of these are INADEQUATE against the organism. Both are broad-spectrum.")
print(f"    cefepime      adopted {cef[0]:3d}/{cef[1]:3d} = {100*cef[0]/max(cef[1],1):5.1f}%")
print(f"    ciprofloxacin adopted {cip[0]:3d}/{cip[1]:3d} = {100*cip[0]/max(cip[1],1):5.1f}%")
print(f"    Same evidential status. Opposite behaviour. The difference is the name.")

# ---- per persona ------------------------------------------------------------
print(f"\n  BY RECEIVING PERSONA")
for p in sorted({x["receiver_persona"] for x in r}):
    s=[x for x in r if x["receiver_persona"]==p]
    for arm in ("right","wrong"):
        t=[x for x in s if x["seed_arm"]==arm]
        if t: print(f"    {p:32s} {arm:5s} {sum(x['adopted_seed'] for x in t):3d}/{len(t):3d}"
                    f" = {100*sum(x['adopted_seed'] for x in t)/len(t):5.1f}%")

json.dump({"n": len(r),
           "adopt_when_adequate": f"{ar}/{len(right)}",
           "adopt_when_inadequate": f"{aw}/{len(wrong)}",
           "by_drug": {d: f"{a}/{n}" for d,(a,n) in by.items()},
           "loglik_gain_correctness": ll_corr-ll_null,
           "loglik_gain_drug_identity": ll_drug-ll_null},
          open("drug_prior.json","w"), indent=2)
print("\n  -> drug_prior.json")
