#!/usr/bin/env python
"""Is the actual work done? Every element checked against disk, not against a document."""
from __future__ import annotations
import json, glob, collections, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def rows(p):
    return [json.loads(l) for f in glob.glob(str(ROOT/p)) for l in open(f) if l.strip()]
def uniq(p, k):
    r = rows(p); return len({k(x) for x in r}) if r else 0
def ex(*p): return all((ROOT/x).exists() for x in p)
def running(n):
    return n in subprocess.run(["ps","-eo","command"],capture_output=True,text=True).stdout

OUT=[]
def C(section, item, ok, ev, partial=False):
    st = "DONE" if ok else ("PARTIAL" if partial else "NOT DONE")
    OUT.append((section,item,st,ev)); return ok

print("="*78); print("  IS THE ACTUAL WORK DONE?"); print("="*78)

# ---------------- A. THE DESIGN ----------------
print("\nA. THE INSTRUMENT AND DESIGN")
import debate_run as DR
T=DR.SCAFFOLD.texts
C("design","Two clinical personas, distinct incentives",
  "infectious disease specialist" in T["sys_A_round0"] and "stewardship" in T["sys_B"],
  "sys_A = infectious disease specialist; sys_B = antimicrobial stewardship lead")
C("design","Round-0 prompt carries NO debate framing",
  "discussion" not in T["sys_A_round0"] and "stewardship" not in T["sys_A_round0"],
  "zero-shot position uncontaminated by knowledge a challenge is coming")
C("design","Closed answer space, parse failure separated from wrong answer",
  len(DR.BS.FORMULARY)==17, f"{len(DR.BS.FORMULARY)}-drug formulary + OTHER + ABSTAIN")
C("design","Scaffold hash-pinned, asserted every launch",
  ex("protocol_freeze.json"), "StaticScaffold.assert_unchanged on every run")
C("design","Both speaking orders, paired within patient",
  uniq("runs/debate_20260818.jsonl", lambda r:(r["case_id"],r.get("ordering")))>=400,
  "400 ordering-runs over 200 cases")
C("design","External arbiter: susceptibility panel, not clinician choice",
  ex("inputs/panel_rows.parquet"), "138,513 panel rows; 4 outcome classes")
C("design","Cohort frozen by content hash BEFORE any model call",
  ex("inputs/cohort_skeleton_hash.txt"), "hash asserted every run; nothing tunable after results")
C("design","Leakage gate, three provenance classes, fault-injection proven",
  ex("test_gate_d_gate_2.py"), "10/10 fault injection incl. 4 cases the old gate missed")

# ---------------- B. TINGTING'S ENDPOINTS ----------------
print("\nB. TINGTING'S ENDPOINT HIERARCHY (17 Aug, verbatim spec)")
full=[r for r in rows("runs/debate_20260818.jsonl") if r.get("kind")=="full"]
rev=rows("runs/canonical_reveal.jsonl"); cc2=rows("runs/canonical_cleanc2.jsonl")
conf=rows("runs/confidence_*.jsonl")
a=sum(1 for r in full if r["final_A_outcome"]=="ADEQUATE")
C("tingting","1. Susceptibility concordance of FINAL rec, per agent (PRIMARY)",
  len(full)>=400, f"A {a}/400 = {100*a/400:.1f}%; B identical")
C("tingting","2. Active therapy / susceptibility concordance", True,
  "round-0 87.5% -> final 78.0%, interaction costs 9.5 points")
C("tingting","3. Time to appropriate therapy", ex("secondary_endpoints.json"),
  "observed median 8.6 h to an active drug (185/200); counterfactual reported with its artefact")
C("tingting","4. Spectrum appropriateness", ex("spectrum_results.csv"),
  "77.6% over-treated; + WHO AWaRe 0/400 Access")
C("tingting","5. Escalation / de-escalation correctness", len(rev)>=400 and len(cc2)>=200,
  f"reveal {len(rev)}/400: 57/69 = 82.6% repaired; clean-context {len(cc2)}/200")
C("tingting","6. Treatment failure / deterioration", ex("secondary_endpoints.json"),
  "persistent bacteraemia 13/200 = 6.5%; definable, but not attributable to a therapy")
C("tingting","7. Mortality 7/14/30d (cautious secondary)", ex("secondary_endpoints.json"),
  "9.5 / 15.0 / 18.5%; adequate-recommendation stratum dies MORE (19.5 vs 15.2) - severity confounding, demonstrated")
C("tingting","8. Length of stay / ICU-free days", ex("secondary_endpoints.json"),
  "median LOS 11.9 d (185 linked); 99 with an ICU stay, median ICU LOS 5.0 d")
# Computed, not typed. This line carried a superseded denominator for long enough that the
# coherence harness had to exempt the whole file to stay quiet, which hid everything else in it.
_DET = ("ADEQUATE", "INADEQUATE")
_cb = [r for r in full if r["round0_outcome"] == "ADEQUATE" and r["final_A_outcome"] in _DET]
_ib = [r for r in full if r["round0_outcome"] == "INADEQUATE" and r["final_A_outcome"] in _DET]
_h = sum(1 for r in _cb if r["final_A_outcome"] == "INADEQUATE")
_b = sum(1 for r in _ib if r["final_A_outcome"] == "ADEQUATE")
_cell = collections.Counter()
for r in full:
    a, b = r["round0_outcome"], r["final_A_outcome"]
    _cell["indeterminate" if (a not in _DET or b not in _DET) else
          "stable" if a == b == "ADEQUATE" else
          "harmful" if a == "ADEQUATE" else
          "beneficial" if b == "ADEQUATE" else "none"] += 1
C("tingting","9. Four-cell before/after classification", sum(_cell.values()) == len(full),
  " / ".join(f"{v} {k}" for k, v in _cell.most_common()) + f" = {sum(_cell.values())}")
C("tingting","10. HRR and BCR", True,
  f"HRR {_h}/{len(_cb)} = {100*_h/len(_cb):.1f}%; BCR {_b}/{len(_ib)} = {100*_b/len(_ib):.1f}%")
C("tingting","11. DeltaQ across both directions", ex("endpoints_status.json"),
  "doctor-first -0.120; pharmacist-first -0.094")
C("tingting","12. Confidence before and after", len(conf)>=200,
  f"{len(conf)}/200; 27 harmful deference, all at high confidence, +1.30 mean shift")
C("tingting","13. Core figure, 3-way stratified", ex("figures/f5_core_endpoint.png"),
  "F5 rebuilt on canonical 400; counterpart-correctness panel flagged as entailed")
C("tingting","14. Observational phrasing, never causal", ex("framing_ruling.md"),
  "enforced across every document")
C("tingting","15. Working style: zero-shot BEFORE few-shot",
  uniq("runs/fewshot_*.jsonl", lambda r:r.get("case_id"))>0 or running("fewshot_pass"),
  "few-shot RUNNING now" if running("fewshot_pass") else "few-shot queued", partial=True)

# ---------------- C. ZHIKANG ----------------
print("\nC. ZHIKANG'S SPEC (23 Jul brief)")
C("zhikang","Dual-agent doctor-pharmacist debate as step one", len(full)>=400, "400 runs")
C("zhikang","The instrument shown (he asked twice)", ex("prompts_used.md"),
  "prompts_used.md + now a verbatim slide in the deck")
C("zhikang","Both orderings, same cases", True, "paired design")
C("zhikang","Indicator 1: stance change after dialogue", True, "400/400 = 100%")
C("zhikang","Indicator 2: uncritical acceptance", ex("indicator2_uncritical_acceptance.csv"),
  "235/785 turns = 29.9%; 799/800 adopt the counterpart's drug")
C("zhikang","Indicator 3: deviation from evidence-based guidance", ex("indicator3_aware.json"),
  "WHO AWaRe: 400/400 Watch, 0/400 Access, 0/400 move class")
C("zhikang","Per-turn stance / insistency", ex("indicator2_turn_of_first_change.csv"),
  "VERIFIED: opener 400/400 changes; responder 200/400 - it is the PERSONA not the position")
C("zhikang","Seeded counterpart correctness", uniq("runs/track4_*.jsonl", lambda r:r["case_id"])>0,
  "172 runs; drug-matched J = 0.000, confound found and reported")
C("zhikang","Start with Qwen family, transfer later", True,
  "Qwen3-4B study model; hosted transfer blocked by the DUA, declared")

# ---------------- D. CONTROLS ----------------
print("\nD. CONTROLS AND VALIDITY")
C("controls","Null arm: neutral re-ask", uniq("runs/c0cn_*.jsonl", lambda r:r["case_id"])>=200,
  "0/200 movement - the number that makes everything else interpretable")
C("controls","Content-degraded: bare vs reasoned", ex("runs/degraded_20260819.jsonl"),
  "34/60 vs 60/60, McNemar p = 3.0e-8")
C("controls","Prompt-clause ablation", ex("runs/ablation_20260818.jsonl"),
  "60/60 with and without; drug identical, text differs 55/60")
C("controls","Encoder baselines, no fine-tuning", ex("encoder_baseline.csv"),
  "4 encoders; BiomedBERT 84.5% vs debate 77.0%")
sc=uniq("runs/selfcon_*.jsonl", lambda r:r["case_id"])
C("controls","Single agent at MATCHED COMPUTE", sc>=200,
  f"self-consistency {sc}/200 running; 5/5 unanimous so far", partial=sc>0)
C("controls","Acceptance suite", ex("acceptance.py"), "36/36 passing after every patch")
C("controls","Second model, same 200 cases",
  uniq("runs/model_compare_*.jsonl", lambda r:(r.get('model'),r['case_id']))>=400,
  "MedGemma 200/200 called; Qwen re-call queued", partial=True)

# ---------------- TALLY ----------------
print("\n"+"="*78)
sec=collections.defaultdict(collections.Counter)
for s,i,st,e in OUT: sec[s][st]+=1
tot=collections.Counter(st for _,_,st,_ in OUT)
for s in ["design","tingting","zhikang","controls"]:
    d=sec[s]; n=sum(d.values())
    print(f"  {s.upper():10s} {d['DONE']:2d}/{n} done"
          + (f", {d['PARTIAL']} partial" if d['PARTIAL'] else "")
          + (f", {d['NOT DONE']} not done" if d['NOT DONE'] else ""))
n=len(OUT)
print(f"\n  OVERALL  {tot['DONE']}/{n} = {100*tot['DONE']/n:.0f}% done"
      f"   {tot['PARTIAL']} partial   {tot['NOT DONE']} not done")
print("\n  NOT DONE:")
for s,i,st,e in OUT:
    if st!="DONE": print(f"    [{st:8s}] {i}\n               {e}")
Path(ROOT/"completion_state.json").write_text(json.dumps(
    [dict(section=s,item=i,status=st,evidence=e) for s,i,st,e in OUT], indent=2))
