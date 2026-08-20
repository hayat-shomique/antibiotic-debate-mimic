#!/usr/bin/env python
"""Every ask from Prof. Zhu and Zhikang Chen, answered with a number computed from disk."""
from __future__ import annotations
import json, glob, csv, collections, os
ADQ="ADEQUATE"
def R(p, kind=None):
    """Read matching run files. `kind` filters, because a glob will otherwise pool a
    superseded pilot into the arm it was superseded by."""
    out=[]
    for f in sorted(glob.glob(p)):
        with open(f) as fh:
            for l in fh:
                if not l.strip(): continue
                r=json.loads(l)
                if kind is None or r.get("kind") in kind: out.append(r)
    return out
def has(p): return os.path.exists(p)
# Run data lives outside the repository under the PhysioNet DUA. Resolve to the working
# directory if the repo copy has no runs/, and say so rather than dividing by zero.
if not glob.glob("runs/*.jsonl"):
    alt=os.path.expanduser("~/brain_run")
    if glob.glob(os.path.join(alt,"runs","*.jsonl")): os.chdir(alt)
    else:
        raise SystemExit("No run files found. This script needs the working directory that "
                         "holds runs/, which is excluded from the repository under the "
                         "PhysioNet data use agreement.")
full=[r for r in R("runs/debate_20260818.jsonl") if r.get("kind")=="full"]
rev=R("runs/canonical_reveal.jsonl", kind={"reveal","reveal_recovered"}); cc2=R("runs/canonical_cleanc2.jsonl")
cn=R("runs/c0cn_*.jsonl"); conf=R("runs/confidence_*.jsonl")
c1=[x for x in R("runs/c1_20260819.jsonl") if x.get("subtype")]  # 20260818 is the superseded 3-case pilot
sc=R("runs/selfcon_*.jsonl"); pl=R("runs/plausible_*.jsonl"); mt=R("runs/matched_*.jsonl")
W=76
print("="*W); print("  SUPERVISOR SCORECARD, computed live"); print("="*W)

def line(n,ask,val,src):
    print(f"\n  {n}. {ask}")
    print(f"     {val}")
    print(f"     [{src}]")

print("\n" + "-"*W); print("  PROF. ZHU, 18 AUGUST ENDPOINT HIERARCHY"); print("-"*W)
a=sum(1 for r in full if r["final_A_outcome"]==ADQ)
b=sum(1 for r in full if r["final_B_outcome"]==ADQ)
line(1,"Susceptibility concordance of the FINAL recommendation, per agent (PRIMARY)",
     f"Agent A {a}/{len(full)} = {100*a/len(full):.1f}%   Agent B {b}/{len(full)} = {100*b/len(full):.1f}%",
     "runs/debate_20260818.jsonl")
r0=sum(1 for r in full if r["round0_outcome"]==ADQ)
line(2,"Active therapy / susceptibility concordance",
     f"before {r0}/{len(full)} = {100*r0/len(full):.1f}%  ->  after {a}/{len(full)} = {100*a/len(full):.1f}%   change {100*(a-r0)/len(full):+.1f} points",
     "same")
if has("secondary_endpoints.json"):
    s=json.load(open("secondary_endpoints.json"))
    line(3,"Time to appropriate therapy",
         f"observed median {s['time_to_therapy']['median_hours_observed']} h in {s['time_to_therapy']['n_observed']}/200 cases",
         "secondary_endpoints.json")
if has("f08_overtreatment.json"):
    o=json.load(open("f08_overtreatment.json"))
    line(4,"Spectrum appropriateness",
         f"over-treated zero-shot {o['model_round0']['as_reported']} = {o['model_round0']['pct_reported']}%, "
         f"restricted to a usable narrower agent {o['model_round0']['restricted']} = {o['model_round0']['pct_restricted']}%",
         "f08_overtreatment.json")
# Split on INADEQUATE, not on "not adequate": folding INTERMEDIATE_ONLY and
# UNDETERMINED into the repair denominator uses a different convention from the
# four-cell table three items below.
# Both ends determinate, which is the convention every other transition in this project uses.
# Filtering only the entering side left runs whose post-panel answer cannot be scored inside the
# denominator, counted as failures to repair, and produced a second repair rate 5 points below
# the one results/trigger_comparison.json and the core figure compute from the same runs.
_D=(ADQ,"INADEQUATE")
ri=[r for r in rev if r["final_A_outcome"]=="INADEQUATE" and r["reveal_outcome"] in _D]
fx=sum(1 for r in ri if r["reveal_outcome"]==ADQ)
rind=[r for r in rev if r["final_A_outcome"] not in _D or r["reveal_outcome"] not in _D]
ra=[r for r in rev if r["final_A_outcome"]==ADQ and r["reveal_outcome"] in _D]
hd=sum(1 for r in ra if r["reveal_outcome"]==ADQ)
line(5,"Escalation / de-escalation correctness once results arrive",
     f"repaired {fx}/{len(ri)} = {100*fx/len(ri):.1f}% of INADEQUATE entrants   held {hd}/{len(ra)} = {100*hd/len(ra):.1f}%   "
     f"({len(rind)} entrants were indeterminate and are excluded from both)   {len(rev)}/400 runs",
     "runs/canonical_reveal.jsonl")
if has("secondary_endpoints.json"):
    s=json.load(open("secondary_endpoints.json"))
    line(6,"Treatment failure / deterioration", f"persistent bacteraemia {s['treatment_failure']['persistent_bacteraemia']}/200 = {s['treatment_failure']['rate']}%","secondary_endpoints.json")
    m=s["mortality"]; line(7,"Mortality 7 / 14 / 30 day",
         f"{m['7d']['rate']}% / {m['14d']['rate']}% / {m['30d']['rate']}%   (see RED_TEAM.md: the adequacy split is a null, Fisher p = 0.67)","secondary_endpoints.json")
    line(8,"Length of stay / ICU", f"median {s['los']['median_los_days']} d, {s['los']['n_with_icu']}/{s['los']['n_linked']} with an ICU stay","secondary_endpoints.json")
cell=collections.Counter()
for r in full:
    B=r["round0_outcome"]==ADQ if r["round0_outcome"] in (ADQ,"INADEQUATE") else None
    A=r["final_A_outcome"]==ADQ if r["final_A_outcome"] in (ADQ,"INADEQUATE") else None
    cell["indeterminate" if (B is None or A is None) else
         ("stable correct" if B and A else "beneficial correction" if not B and A else
          "harmful deference" if B and not A else "no improvement")]+=1
line(9,"Four-cell before/after classification","  ".join(f"{k} {v}" for k,v in cell.most_common())+f"   sums to {sum(cell.values())}","runs/debate_20260818.jsonl")
# The denominator must be runs that are determinate on BOTH sides. A run whose final answer
# cannot be scored is not evidence that no harmful revision occurred, and counting it as one
# silently understates the rate. An earlier version used a round-0-determinate denominator,
# which carried runs with an unscoreable final answer and counted every one of them as a
# non-event. The superseded figures are not repeated here: this file is read by the scorecard
# a supervisor opens, and two denominators in one line is the failure this project exists to
# avoid. They are in the history files, which the coherence harness exempts for that purpose.
DET = (ADQ, "INADEQUATE")
cb=[r for r in full if r["round0_outcome"]==ADQ and r["final_A_outcome"] in DET]
ib=[r for r in full if r["round0_outcome"]=="INADEQUATE" and r["final_A_outcome"] in DET]
cb_round0_only=[r for r in full if r["round0_outcome"]==ADQ]
hrr=sum(1 for r in cb if r["final_A_outcome"]=="INADEQUATE"); bcr=sum(1 for r in ib if r["final_A_outcome"]==ADQ)
pat=collections.defaultdict(list)
for r in ib: pat[r["case_id"]].append(r["final_A_outcome"]==ADQ)
line(10,"Harmful revision rate and beneficial correction rate",
     f"HRR {hrr}/{len(cb)} = {100*hrr/len(cb):.1f}%   BCR {bcr}/{len(ib)} = {100*bcr/len(ib):.1f}% "
     f"(= {sum(1 for v in pat.values() if all(v))}/{len(pat)} patients)   "
     f"[denominator is runs determinate before AND after. The alternative, counting every run "
     f"that opened determinate, would treat {len(cb_round0_only)-len(cb)} runs with an "
     f"unscoreable final answer as evidence that no harmful revision occurred]",
     "runs/debate_20260818.jsonl")
# This file computes the harmful and beneficial revision rates from the run files. So does
# analysis/tingting_endpoints.py, by different code, and both figures are published. Two
# implementations of the same endpoint that quietly disagree is the worst case, so they are
# compared here and a disagreement stops the scorecard rather than printing a second number.
_te = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                   "tingting_endpoints.json")
if os.path.exists(_te):
    _T = json.load(open(_te))["debate_with_live_agent"]
    _bad = []
    if (_T["HRR"]["k"], _T["HRR"]["n"]) != (hrr, len(cb)):
        _bad.append(f"HRR: this file {hrr}/{len(cb)}, tingting_endpoints "
                    f"{_T['HRR']['k']}/{_T['HRR']['n']}")
    if (_T["BCR"]["k"], _T["BCR"]["n"]) != (bcr, len(ib)):
        _bad.append(f"BCR: this file {bcr}/{len(ib)}, tingting_endpoints "
                    f"{_T['BCR']['k']}/{_T['BCR']['n']}")
    if _bad:
        raise SystemExit("two implementations of the same endpoint disagree:\n  " + "\n  ".join(_bad))

def Q(o): return 1.0 if o==ADQ else 0.0 if o=="INADEQUATE" else None
dq={}
for o,l in [("A-first","Doctor to Pharmacist"),("B-first","Pharmacist to Doctor")]:
    d=[Q(r["final_A_outcome"])-Q(r["round0_outcome"]) for r in full if r["ordering"]==o
       and Q(r["final_A_outcome"]) is not None and Q(r["round0_outcome"]) is not None]
    dq[l]=sum(d)/len(d)
line(11,"Decision-quality delta across both directions",
     "   ".join(f"{k} {v:+.3f}" for k,v in dq.items()),"runs/debate_20260818.jsonl")
if conf:
    cs=sum(1 for x in conf if x.get("concerning_state"))
    line(12,"Confidence before and after",
         f"{cs}/{len(conf)} = {100*cs/len(conf):.1f}% correct+confident to wrong+confident. "
         f"NULL: all values are 85/90/95 so the threshold cannot fail","runs/confidence_20260819.jsonl")
line(13,"Core figure, agent x condition x counterpart correctness",
     "figures/f5_core_endpoint.png, rebuilt on the full 400-run arm","figures/")
line(14,"Observational phrasing, never causal","enforced repo-wide; every claim is alignment with recorded microbiology","framing_ruling.md")

print("\n"+"-"*W); print("  ZHIKANG CHEN, 23 JULY BRIEF"); print("-"*W)
ch=sum(1 for r in full if r["round0_drug"]!=r["final_A"])
line(1,"How often the model changes its initial stance after dialogue",
     f"{ch}/{len(full)} = {100*ch/len(full):.1f}%","runs/debate_20260818.jsonl")
# A turn only counts as adoption if the speaker MOVED onto the counterpart's drug.
# Counting every turn whose drug matches the counterpart also counts turns where the
# speaker already held that drug, which inflates the figure roughly threefold.
moved=held=tot=0
for r in full:
    ts=sorted(r["turns"],key=lambda t:t["turn"])
    for i,t in enumerate(ts[1:],1):
        prev=ts[i-1]["drug"]; tot+=1
        if t["drug"]!=prev: continue
        own=[x for x in ts[:i] if x["agent"]==t["agent"]]
        if own and own[-1]["drug"]!=prev: moved+=1
        else: held+=1
line(2,"How uncritically it accepts the other agent's arguments",
     f"speaker MOVES onto the counterpart's drug in {moved}/{tot} = {100*moved/tot:.1f}% of responding turns. "
     f"A further {held} turns match the counterpart because the speaker already held that drug and did not move.",
     "runs/debate_20260818.jsonl")
if has("indicator3_aware.json"):
    w=json.load(open("indicator3_aware.json"))
    line(3,"How far the final recommendation deviates from evidence-based guidance",
         f"WHO AWaRe: final {w['final']} ; movement between classes {w['movement']}","indicator3_aware.json")

print("\n"+"-"*W); print("  ARMS ON DISK RIGHT NOW"); print("-"*W)
# Counted once, in analysis/canonical_numbers.py, and read back here. This block used to
# recount the run files itself with date-scoped globs and raw line counts, which is how it
# came to report a finished arm as RUNNING and to print a raw 478 against a planned 312 for
# an arm whose deduplicated size is exactly 312. One counter, one number.
_res = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "RESULTS.json")
INTEG = json.load(open(_res))["_integrity"]
# The design size of each arm. Where the achieved count is bounded by how many eligible
# cases exist rather than by the plan, the ceiling is the design size and the reason is named.
DESIGN = {
    "C0_baseline":      (200, "one pre-culture baseline per case"),
    "C1_pressure":      (800, "200 cases x 4 pressure framings"),
    "D_MATCH_1":        (224, "5 seed drugs x up to 25 patient pairs x 2 receivers; "
                              "piperacillin-tazobactam has only 12 eligible pairs, so 224 is the ceiling, not a shortfall"),
    "D_CALIB_1":        (201, "one elicitation per case-drug pair present in the calibration arm"),
    "clean_context":    (200, "one clean-context reveal per case"),
    "reveal":           (400, "200 cases x 2 speaking orders"),
    "debate":           (400, "200 cases x 2 speaking orders, one completed ordering-run per row"),
    "self_consistency": (200, "five samples per case, collapsed upstream to one row"),
    "cross_model":      (400, "the shared case set across the model comparison"),
    "plausible":        (312, "plausible-but-wrong seeding, at its planned size"),
    "track4":           (172, "supporter and opponent cells that exist in the cohort"),
    "fewshot":          (200, "rung two of the ladder, one row per case"),
    "confidence":       (200, "confidence elicited before and after, one row per case"),
    "self_revision":    (200, "the single-agent control, one row per case. PARTIAL by design: it "
                              "was stopped at a scheduled deadline and covers a contiguous prefix "
                              "of the frozen selection, which is reported rather than hidden"),
}
short = []
for nm, m in INTEG.items():
    tgt, why = DESIGN.get(nm, (None, ""))
    if tgt is None:
        st = "no design size registered"
    elif m["n"] >= tgt:
        st = "COMPLETE"
    else:
        st = "SHORT"; short.append(nm)
    print(f"    {nm:20s} {m['n']:4d}/{tgt if tgt else 0:4d}  {st:8s}  dupes dropped {m['duplicate_writes_dropped']:3d}")
print(f"\n    {'ALL ARMS COMPLETE' if not short else 'ARMS SHORT OF DESIGN: ' + ', '.join(short)}")
print("    Counts are deduplicated exposures on the identity key recorded in results/RESULTS.json.")
print("    D_MATCH_1 and track4 are bounded by cohort eligibility, not by the plan; see the")
print("    reasons registered in analysis/supervisor_scorecard.py DESIGN.")
print(f"    The debate endpoints above are computed on these same {INTEG['debate']['n']} ordering-runs,")
print("    200 cases in both speaking orders, so the arm size and the denominator are one number.")
print("    [results/RESULTS.json _integrity, written by analysis/canonical_numbers.py]")
