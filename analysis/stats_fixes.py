#!/usr/bin/env python
"""F08, F10, F11, F12, F13. The statistical corrections from adversarial review, computed."""
from __future__ import annotations
import json, glob, csv, math, collections
ADQ="ADEQUATE"
def rows(p): return [json.loads(l) for f in glob.glob(p) for l in open(f) if l.strip()]
full=[r for r in rows("runs/debate_20260818.jsonl") if r.get("kind")=="full"]
OUT={}

print("="*76); print("  STATISTICAL CORRECTIONS"); print("="*76)

# ---------- F10 clustering: how wrong are the intervals? ----------------------
print("\nF10  CLUSTERING. 400 ordering-runs are 200 patients seen twice.")
by=collections.defaultdict(list)
for r in full: by[r["case_id"]].append(r["final_A_outcome"]==ADQ)
pairs=[v for v in by.values() if len(v)==2]
n=len(pairs)
both=sum(1 for v in pairs if v[0] and v[1]); neither=sum(1 for v in pairs if not v[0] and not v[1])
disc=n-both-neither
p_bar=sum(sum(v) for v in pairs)/(2*n)
# ICC via ANOVA on the 0/1 outcome
msb=sum((sum(v)/2 - p_bar)**2 for v in pairs)*2/(n-1)
msw=sum(sum((x-sum(v)/2)**2 for x in v) for v in pairs)/n
icc=(msb-msw)/(msb+msw) if (msb+msw)>0 else float("nan")
deff=1+icc  # cluster size 2
print(f"    concordant pairs {both+neither}/{n}, discordant {disc}/{n}")
print(f"    ICC {icc:.3f}   design effect {deff:.2f}   effective n {2*n/deff:.0f} not {2*n}")
print(f"    every interval computed on 400 is too narrow by a factor of sqrt({deff:.2f}) = {math.sqrt(deff):.2f}")
OUT["clustering"]={"icc":round(icc,3),"deff":round(deff,2),"n_eff":round(2*n/deff)}

def wilson(k,N,deff=1.0):
    if N==0: return (float("nan"),)*2
    Ne=N/deff; p=k/N; z=1.96
    d=1+z*z/Ne; c=p+z*z/(2*Ne); m=z*math.sqrt(p*(1-p)/Ne+z*z/(4*Ne*Ne))
    return ((c-m)/d*100,(c+m)/d*100)

# ---------- F12 BCR on the clustering unit -----------------------------------
print("\nF12  BCR REPORTED ON THE WRONG UNIT.")
ib=[r for r in full if r["round0_outcome"]=="INADEQUATE"]
bcr=sum(1 for r in ib if r["final_A_outcome"]==ADQ)
pat=collections.defaultdict(list)
for r in ib: pat[r["case_id"]].append(r["final_A_outcome"]==ADQ)
npat=len(pat); kpat=sum(1 for v in pat.values() if all(v))
lo,hi=wilson(bcr,len(ib)); plo,phi=wilson(kpat,npat)
print(f"    as runs      {bcr}/{len(ib)} = {100*bcr/len(ib):.1f}%   95% CI [{lo:.1f}, {hi:.1f}]")
print(f"    as PATIENTS  {kpat}/{npat} = {100*kpat/npat:.1f}%   95% CI [{plo:.1f}, {phi:.1f}]")
print(f"    the patient interval spans {phi-plo:.0f} points. Directional only.")
OUT["bcr"]={"runs":f"{bcr}/{len(ib)}","patients":f"{kpat}/{npat}","patient_ci":[round(plo,1),round(phi,1)]}

# ---------- F11 order effect against a chance baseline -----------------------
print("\nF11  ORDER EFFECT NEEDS A CHANCE BASELINE.")
bd=collections.defaultdict(dict)
for r in full: bd[r["case_id"]][r["ordering"]]=r["final_A"]
pr={k:v for k,v in bd.items() if len(v)==2}
diff=sum(1 for v in pr.values() if v["A-first"]!=v["B-first"])
marg=collections.Counter()
for v in pr.values(): marg[v["A-first"]]+=1; marg[v["B-first"]]+=1
tot=sum(marg.values()); pe=sum((c/tot)**2 for c in marg.values())
exp_dis=(1-pe)*100
print(f"    observed disagreement {diff}/{len(pr)} = {100*diff/len(pr):.1f}%")
print(f"    expected under independent draws from the same marginals = {exp_dis:.1f}%")
print(f"    label space actually used: {dict(marg)}")
kappa=( (1-diff/len(pr)) - pe )/(1-pe)
print(f"    Cohen's kappa = {kappa:.3f}")
print(f"    -> observed disagreement is {'BELOW' if 100*diff/len(pr)<exp_dis else 'ABOVE'} chance."
      f" Framing '41% is surprising' is not supported.")
OUT["order_effect"]={"observed_pct":round(100*diff/len(pr),1),"expected_pct":round(exp_dis,1),
                     "kappa":round(kappa,3)}

# ---------- F08 over-treatment restricted to acceptable alternatives ---------
print("\nF08  OVER-TREATMENT DRIVEN BY AGENTS UNUSABLE FOR BACTERAEMIA.")
NARROW_UNUSABLE={"cefazolin","ampicillin","trimethoprim-sulfamethoxazole","gentamicin"}
try:
    sr=list(csv.DictReader(open("spectrum_results.csv")))
    sub=[r for r in sr if r.get("arm")=="model_round0" and r.get("analysis")=="primary_all17"]
    ov=[r for r in sub if r["spectrum_label"]=="OVER_TREATED"]
    col=next((c for c in sub[0] if "narrow" in c.lower()), None)
    if col:
        strict=0
        for r in ov:
            s={x.strip() for x in (r[col] or "").replace(";",",").split(",") if x.strip()}
            if s and not s <= NARROW_UNUSABLE: strict+=1
        print(f"    over-treated, as reported          {len(ov)}/{len(sub)} = {100*len(ov)/len(sub):.1f}%")
        print(f"    restricted to cases where a narrower agent is usable as monotherapy")
        print(f"    for bacteraemia                    {strict}/{len(sub)} = {100*strict/len(sub):.1f}%")
        print(f"    {len(ov)-strict} of {len(ov)} rest entirely on cefazolin, ampicillin, TMP-SMX or gentamicin,")
        print(f"    none of which a microbiologist would use as monotherapy here.")
        OUT["over_treatment"]={"as_reported":f"{len(ov)}/{len(sub)}","restricted":f"{strict}/{len(sub)}"}
    else:
        print(f"    column with the narrower set not found; columns are {list(sub[0])[:9]}")
except Exception as e: print("   ",e)

# ---------- F13 multiplicity --------------------------------------------------
print("\nF13  MULTIPLICITY.")
arms=[f.split('/')[-1] for f in glob.glob("runs/*.jsonl") if not f.split('/')[-1].startswith('_')]
print(f"    {len(arms)} run files, 14 declared endpoints, all from the same 200 case_ids.")
print(f"    Declared position: ONE primary endpoint (susceptibility concordance of the final")
print(f"    recommendation per agent). Everything else is exploratory and reported without")
print(f"    a correction, which is stated rather than corrected for.")
OUT["multiplicity"]={"n_arms":len(arms),"primary":"susceptibility concordance of final recommendation",
                     "position":"one primary, remainder exploratory, no correction applied"}

json.dump(OUT, open("stats_fixes.json","w"), indent=2)
print("\n  -> stats_fixes.json")
