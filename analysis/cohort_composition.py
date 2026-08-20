"""cohort_composition.py - what actually grew, and what the panel could not answer.

Three questions a clinician asks first and a reviewer asks second:
  which organisms, what fraction of case-drug pairs the laboratory never tested,
  and what the best achievable coverage on this cohort would have been.

Aggregates only, written to results/cohort_composition.json. No case-level rows.
"""
from __future__ import annotations

import collections
import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
BRAIN = Path(os.path.expanduser("~/brain_run"))

FORMULARY = ["ampicillin", "ampicillin-sulbactam", "cefazolin", "cefepime", "ceftazidime",
             "ceftriaxone", "ciprofloxacin", "daptomycin", "gentamicin", "levofloxacin",
             "linezolid", "meropenem", "oxacillin", "penicillin-g", "piperacillin-tazobactam",
             "trimethoprim-sulfamethoxazole", "vancomycin"]
GRAM_POSITIVE_AGENTS = {"daptomycin", "linezolid", "oxacillin", "vancomycin", "penicillin-g"}

PANEL_TO_FORMULARY = {
    "AMPICILLIN": "ampicillin", "AMPICILLIN/SULBACTAM": "ampicillin-sulbactam",
    "CEFAZOLIN": "cefazolin", "CEFEPIME": "cefepime", "CEFTAZIDIME": "ceftazidime",
    "CEFTRIAXONE": "ceftriaxone", "CIPROFLOXACIN": "ciprofloxacin", "DAPTOMYCIN": "daptomycin",
    "GENTAMICIN": "gentamicin", "LEVOFLOXACIN": "levofloxacin", "LINEZOLID": "linezolid",
    "MEROPENEM": "meropenem", "OXACILLIN": "oxacillin", "PENICILLIN G": "penicillin-g",
    "PENICILLIN": "penicillin-g", "PIPERACILLIN/TAZO": "piperacillin-tazobactam",
    "TRIMETHOPRIM/SULFA": "trimethoprim-sulfamethoxazole", "VANCOMYCIN": "vancomycin",
}
GRAM_NEG = ("ESCHERICHIA", "KLEBSIELLA", "PROTEUS", "ENTEROBACTER", "SERRATIA", "CITROBACTER",
            "MORGANELLA", "PSEUDOMONAS", "ACINETOBACTER", "HAEMOPHILUS", "SALMONELLA",
            "PROVIDENCIA", "RAOULTELLA", "HAFNIA", "STENOTROPHOMONAS", "BACTEROIDES", "NEISSERIA")
GRAM_POS = ("STAPH", "STREP", "ENTEROCOCCUS", "LISTERIA", "CORYNEBACTER", "LACTOBACILLUS",
            "CLOSTRIDIUM", "PEPTOSTREP", "MICROCOCCUS", "BACILLUS")


def gram(org):
    o = (org or "").upper()
    if any(h in o for h in GRAM_NEG):
        return "Gram negative"
    if any(h in o for h in GRAM_POS):
        return "Gram positive"
    return "unclassified"


panel = pd.read_parquet(BRAIN / "inputs" / "panel_rows.parquet")
cases = []
for line in open(BRAIN / "runs" / "canonical_cleanc2.jsonl"):
    line = line.strip()
    if line:
        cases.append(json.loads(line)["case_id"])
msids = {int(c.split("_")[1]) for c in cases}
sel = panel[panel["micro_specimen_id"].isin(msids)].copy()
sel["drug"] = sel["ab_name"].map(lambda a: PANEL_TO_FORMULARY.get(str(a).upper()))

per_case_org = sel.groupby("micro_specimen_id")["org_name"].apply(lambda s: sorted(set(s.dropna())))
org_counts = collections.Counter(o for lst in per_case_org for o in lst)
gram_cases = collections.Counter()
for lst in per_case_org:
    g = {gram(o) for o in lst}
    gram_cases["mixed" if len(g) > 1 else g.pop()] += 1

iso_per_case = sel.groupby("micro_specimen_id")["isolate_num"].nunique()
tested = sel.dropna(subset=["drug"])
undetermined = determinate = 0
ceiling_hits = 0
# Coverage of every constant single-agent policy. The best of these is the comparator the study is
# measured against, and it was a typed number in two documents until it was computed here.
constant_cover = {}
for msid, grp in tested.groupby("micro_specimen_id"):
    n_iso = iso_per_case[msid]
    any_full_cover = False
    for d in FORMULARY:
        sub = grp[grp["drug"] == d]
        if sub["isolate_num"].nunique() < n_iso:
            undetermined += 1
            continue
        determinate += 1
        if set(sub["interp"]) <= {"S"}:
            any_full_cover = True
            constant_cover[d] = constant_cover.get(d, 0) + 1
        else:
            constant_cover.setdefault(d, 0)
    ceiling_hits += int(any_full_cover)

pairs = undetermined + determinate
interp = collections.Counter(sel["interp"].fillna("MISSING"))
n_cases = len(iso_per_case)

out = {
    "_scope": f"the {n_cases} cases in the frozen evaluation selection",
    "organisms": {
        "distinct": len(org_counts),
        "top": [{"organism": o, "cases": n, "gram": gram(o)} for o, n in org_counts.most_common(8)],
        "cases_by_gram_class": dict(gram_cases),
    },
    "panel_interpretations": {
        "rows": int(len(sel)), "S": int(interp.get("S", 0)),
        "I": int(interp.get("I", 0)), "R": int(interp.get("R", 0)),
        "intermediate_pct_of_rows": round(100.0 * interp.get("I", 0) / len(sel), 1),
        "scorer_rule": ("Intermediate is neither covering nor failing. A case whose best available "
                        "verdict on some isolate is Intermediate scores INTERMEDIATE_ONLY, its own "
                        "class, and is excluded from adequacy numerators and from the paired test."),
    },
    "case_drug_pairs": {
        "pairs": pairs, "formulary_agents": len(FORMULARY),
        "undetermined": undetermined,
        "undetermined_pct": round(100.0 * undetermined / pairs, 1),
        "meaning": ("UNDETERMINED means the laboratory never tested that agent against at least one "
                    "isolate on that patient. It is a property of what the laboratory chose to test."),
    },
    "coverage_ceiling": {
        "cases_with_at_least_one_fully_susceptible_formulary_agent": ceiling_hits,
        "n": n_cases,
        "pct": round(100.0 * ceiling_hits / n_cases, 1),
        "meaning": ("the best any single-agent policy could achieve on this cohort with perfect "
                    "per-patient choice. The baseline is measured against this, not against 100."),
    },
    "provenance_counts": {
        # These were typed into JOURNEY.md as cohort provenance. They are read from the frozen
        # inputs instead, so a change to any of them shows up rather than sitting in prose.
        "index_events": int(len(pd.read_parquet(BRAIN / "index_classified.parquet")))
                        if (BRAIN / "index_classified.parquet").exists() else None,
        "frozen_cohort_rows": int(len(pd.read_parquet(BRAIN / "inputs" / "cohort_skeleton.parquet"))),
        "panel_rows": int(len(panel)),
        "evaluated_selection": n_cases,
        "meaning": ("the chain from raw index events to the evaluated selection. The frozen cohort "
                    "is content-hashed and the hash is asserted on every run."),
    },
    "constant_single_agent_policies": {
        "coverage_by_agent": dict(sorted(((d, {"k": k, "n": n_cases,
                                               "pct": round(100.0 * k / n_cases, 1)})
                                          for d, k in constant_cover.items()),
                                         key=lambda kv: -kv[1]["k"])),
        "best": (lambda b: {"agent": b[0], "k": b[1], "n": n_cases,
                            "pct": round(100.0 * b[1] / n_cases, 1)})(
            max(constant_cover.items(), key=lambda kv: kv[1])),
        "meaning": ("give every patient the same drug and score it against their own panel. The best "
                    "of these is the comparator this study is measured against, because a model that "
                    "cannot beat one constant is not reasoning about the patient. It is computed "
                    "here rather than typed."),
    },
    "gram_positive_agents_in_the_formulary": {
        "agents": sorted(GRAM_POSITIVE_AGENTS),
        "note": ("these can never be adequate on a Gram-negative cohort, which is why an encoder that "
                 "answers vancomycin every time scores 0 adequate rather than scoring wrong"),
    },
}
(RES / "cohort_composition.json").write_text(json.dumps(out, indent=2))
print("wrote results/cohort_composition.json")
print(f"  organisms {out['organisms']['distinct']} distinct, cases by gram {dict(gram_cases)}")
print(f"  undetermined {undetermined}/{pairs} = {out['case_drug_pairs']['undetermined_pct']}% of case-drug pairs")
print(f"  Intermediate {interp.get('I',0)}/{len(sel)} panel rows = {out['panel_interpretations']['intermediate_pct_of_rows']}%")
print(f"  coverage ceiling {ceiling_hits}/{n_cases} = {out['coverage_ceiling']['pct']}%")
