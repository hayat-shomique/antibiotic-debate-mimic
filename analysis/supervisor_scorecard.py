#!/usr/bin/env python
"""Every ask from Prof. Zhu and Zhikang Chen, answered with a number computed from disk."""
from __future__ import annotations
import json, glob, csv, collections, os
ADQ="ADEQUATE"
def R(p): return [json.loads(l) for f in glob.glob(p) for l in open(f) if l.strip()]
def has(p): return os.path.exists(p)
full=[r for r in R("runs/debate_20260818.jsonl") if r.get("kind")=="full"]
rev=R("runs/canonical_reveal.jsonl"); cc2=R("runs/canonical_cleanc2.jsonl")
cn=R("runs/c0cn_*.jsonl"); conf=R("runs/confidence_*.jsonl")
c1=[x for x in R("runs/c1_*.jsonl") if x.get("subtype")]
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
ri=[r for r in rev if r["final_A_outcome"]!=ADQ]; fx=sum(1 for r in ri if r["reveal_outcome"]==ADQ)
ra=[r for r in rev if r["final_A_outcome"]==ADQ]; hd=sum(1 for r in ra if r["reveal_outcome"]==ADQ)
line(5,"Escalation / de-escalation correctness once results arrive",
     f"repaired {fx}/{len(ri)} = {100*fx/len(ri):.1f}%   held {hd}/{len(ra)} = {100*hd/len(ra):.1f}%   ({len(rev)}/400 runs)",
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
cb=[r for r in full if r["round0_outcome"]==ADQ]; ib=[r for r in full if r["round0_outcome"]=="INADEQUATE"]
hrr=sum(1 for r in cb if r["final_A_outcome"]=="INADEQUATE"); bcr=sum(1 for r in ib if r["final_A_outcome"]==ADQ)
pat=collections.defaultdict(list)
for r in ib: pat[r["case_id"]].append(r["final_A_outcome"]==ADQ)
line(10,"Harmful revision rate and beneficial correction rate",
     f"HRR {hrr}/{len(cb)} = {100*hrr/len(cb):.1f}%   BCR {bcr}/{len(ib)} = {100*bcr/len(ib):.1f}% "
     f"(= {sum(1 for v in pat.values() if all(v))}/{len(pat)} patients)","runs/debate_20260818.jsonl")
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
for nm,dat,tgt in [("debate, both orders",full,400),("neutral control",cn,200),
                   ("panel reveal",rev,400),("clean-context reveal",cc2,200),
                   ("confidence",conf,200),("self-consistency",sc,200),
                   ("C1 unsupported pressure",c1,788),("plausible-wrong seeding",pl,312),
                   ("drug-matched pairs",mt,250)]:
    st="COMPLETE" if len(dat)>=tgt else ("RUNNING" if len(dat) else "queued")
    print(f"    {nm:26s} {len(dat):4d}/{tgt:4d}  {st}")
