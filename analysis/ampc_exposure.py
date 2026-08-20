"""ampc_exposure.py - how much of the AmpC limitation this cohort actually carries.

The limitation as first written pooled every AmpC-capable genus into one 18% figure and
let that figure carry the whole argument. The primer the argument rests on grades the risk
by organism: induction is best described for Enterobacter cloacae, and the likelihood in
other Enterobacteriaceae is explicitly less clear (Tamma et al., Clin Infect Dis 2019,
doi:10.1093/cid/ciz173, PMID 30838380, verified against PubMed on 20 August 2026).

This script grades the cohort the same way, and then asks the question that decides how much
the limitation bites: the harmful revisions all leave piperacillin-tazobactam for a
cephalosporin, but the two destinations are not equivalent under AmpC. Ceftriaxone is a
third-generation cephalosporin, the class the primer says to avoid in the highest-risk
organisms. Cefepime is the agent IDSA guidance recommends for AmpC producers at an MIC of
2 or below. So a harmful revision onto ceftriaxone against an Enterobacter cloacae isolate
is the case where the panel's susceptible label is least trustworthy, and a revision onto
cefepime is not.

Aggregates only, written to results/ampc_exposure.json. No case-level rows.
"""
from __future__ import annotations

import collections
import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
BRAIN = Path(os.environ.get("BRAIN_DIR") or os.path.expanduser("~/brain_run"))
ADQ = "ADEQUATE"

# Graded by the strength of the published induction evidence, not by genus alone.
# Substring matching on genus was tried first and undercounted by two, because the laboratory
# writes three further Enterobacter labels and because one label carries the genus only as a
# historical synonym in brackets. This cohort has exactly twenty organism labels, so the
# grading is an explicit table over all twenty and every decision is auditable.
#
# best_established: the primer's own words, induction "has best been described in the context
#   of Enterobacter cloacae infections". Both spellings the laboratory uses are that organism.
# named_but_weaker: organisms the primer lists as AmpC producers while saying the likelihood
#   of induction in other Enterobacteriaceae is less clear. An unspecified Enterobacter sits
#   here rather than in the tier above, because the species is not recorded.
# not_ampc_capable: everything else. Pantoea agglomerans is here deliberately. Its laboratory
#   label carries "(ENTEROBACTER)" as a historical synonym, and a substring rule counts it as
#   an Enterobacter; it is not one of the inducible-AmpC organisms the primer describes.
AMPC_TIER = {
    "ENTEROBACTER CLOACAE":              "best_established",
    "ENTEROBACTER CLOACAE COMPLEX":      "best_established",
    "ENTEROBACTER AEROGENES":            "named_but_weaker",
    "ENTEROBACTER SPECIES":              "named_but_weaker",
    "ENTEROBACTER CANCEROGENUS":         "named_but_weaker",
    "SERRATIA MARCESCENS":               "named_but_weaker",
    "CITROBACTER FREUNDII COMPLEX":      "named_but_weaker",
    "MORGANELLA MORGANII":               "named_but_weaker",
    "PROVIDENCIA RETTGERI":              "named_but_weaker",
    "ESCHERICHIA COLI":                  "not_ampc_capable",
    "KLEBSIELLA PNEUMONIAE":             "not_ampc_capable",
    "KLEBSIELLA OXYTOCA":                "not_ampc_capable",
    "KLEBSIELLA (RAOULTELLA) PLANTICOLA": "not_ampc_capable",
    "PROTEUS MIRABILIS":                 "not_ampc_capable",
    "PROTEUS PENNERI":                   "not_ampc_capable",
    "PROTEUS HAUSERI":                   "not_ampc_capable",
    "SALMONELLA TYPHI":                  "not_ampc_capable",
    "SALMONELLA DUBLIN":                 "not_ampc_capable",
    "SALMONELLA SPECIES":                "not_ampc_capable",
    "PANTOEA (ENTEROBACTER) AGGLOMERANS": "not_ampc_capable",
}

THIRD_GEN_CEPH = {"ceftriaxone", "ceftazidime", "cefotaxime"}
IDSA_ENDORSED_FOR_AMPC = {"cefepime"}


def tier(org: str) -> str:
    """A label with no entry in the table is a hard error, never a silent not-capable."""
    o = (org or "").strip().upper()
    if o not in AMPC_TIER:
        raise SystemExit("organism label not graded in AMPC_TIER, so its AmpC status would be "
                         "assumed rather than decided: " + repr(o))
    return AMPC_TIER[o]


def main() -> None:
    cases = [json.loads(l)["case_id"] for l in open(BRAIN / "runs" / "canonical_cleanc2.jsonl") if l.strip()]
    msids = {int(c.split("_")[1]) for c in cases}
    panel = pd.read_parquet(BRAIN / "inputs" / "panel_rows.parquet")
    sel = panel[panel["micro_specimen_id"].isin(msids)]

    # A specimen can grow more than one isolate. A case counts as AmpC-capable at the
    # strongest tier any of its isolates reaches, because the exposure is to the case.
    by_case: dict[int, str] = {}
    organisms: dict[int, set] = collections.defaultdict(set)
    for msid, org in zip(sel["micro_specimen_id"], sel["org_name"]):
        organisms[int(msid)].add(str(org))
    for msid, orgs in organisms.items():
        tiers = {tier(o) for o in orgs}
        by_case[msid] = ("best_established" if "best_established" in tiers
                         else "named_but_weaker" if "named_but_weaker" in tiers
                         else "not_ampc_capable")

    n_cases = len(msids)
    counts = collections.Counter(by_case.values())
    any_ampc = counts["best_established"] + counts["named_but_weaker"]

    org_by_tier: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for msid, orgs in organisms.items():
        for o in orgs:
            t = tier(o)
            if t != "not_ampc_capable":
                org_by_tier[t][o] += 1

    # The harmful revisions, defined exactly as the harmful revision rate defines them:
    # adequate before the debate, inadequate after it, both ends determinate.
    full = [json.loads(l) for l in open(BRAIN / "runs" / "debate_20260818.jsonl") if l.strip()]
    full = [r for r in full if r.get("kind") == "full"]
    harmful = [r for r in full
               if r["round0_outcome"] == ADQ and r["final_A_outcome"] == "INADEQUATE"]
    dest = collections.Counter()
    for r in harmful:
        t = by_case.get(int(r["micro_specimen_id"]), "not_ampc_capable")
        dest[(r["final_A"], t)] += 1

    # Runs that end on a third-generation cephalosporin against an AmpC-capable organism and
    # are nonetheless scored adequate on the reported panel. These are the runs whose adequacy
    # label the limitation says to distrust.
    at_risk = [r for r in full
               if r["final_A"] in THIRD_GEN_CEPH
               and r["final_A_outcome"] == ADQ
               and by_case.get(int(r["micro_specimen_id"]), "not_ampc_capable") != "not_ampc_capable"]
    at_risk_best = [r for r in at_risk
                    if by_case.get(int(r["micro_specimen_id"])) == "best_established"]

    out = {
        "_purpose": "grades the AmpC limitation by the strength of the published induction "
                    "evidence, and separates the two destination drugs, which are not "
                    "equivalent under AmpC",
        "_sources": {
            "induction_risk_grading": "Tamma et al., Clin Infect Dis 2019;69(8):1446-1455, "
                                      "doi:10.1093/cid/ciz173, PMID 30838380",
            "cefepime_endorsement": "Saleh et al., Int J Infect Dis 2026;167:108563, "
                                    "doi:10.1016/j.ijid.2026.108563, PMID 41864271",
            "verified": "identifiers resolved against PubMed on 20 August 2026",
        },
        "cohort": {
            "n_cases": n_cases,
            "best_established": counts["best_established"],
            "best_established_pct": round(100 * counts["best_established"] / n_cases, 1),
            "named_but_weaker": counts["named_but_weaker"],
            "named_but_weaker_pct": round(100 * counts["named_but_weaker"] / n_cases, 1),
            "any_ampc_capable": any_ampc,
            "any_ampc_capable_pct": round(100 * any_ampc / n_cases, 1),
            "organisms_by_tier": {k: dict(sorted(v.items())) for k, v in org_by_tier.items()},
        },
        "harmful_revisions": {
            "n": len(harmful),
            "by_destination_and_tier": {f"{d} | {t}": n for (d, t), n in sorted(dest.items())},
            "onto_a_third_generation_cephalosporin_against_an_ampc_capable_organism":
                sum(n for (d, t), n in dest.items()
                    if d in THIRD_GEN_CEPH and t != "not_ampc_capable"),
            "onto_cefepime_which_guidance_endorses_for_ampc":
                sum(n for (d, t), n in dest.items() if d in IDSA_ENDORSED_FOR_AMPC),
        },
        "adequacy_labels_the_limitation_distrusts": {
            "runs_ending_on_a_third_generation_cephalosporin_against_an_ampc_capable_organism_"
            "and_scored_adequate": len(at_risk),
            "of_those_against_the_best_established_organism": len(at_risk_best),
            "denominator_runs": len(full),
            "reading": "these are the adequacy labels that could overstate true adequacy if "
                       "AmpC de-represses on therapy. The direction of the bias is fixed: it "
                       "makes the reported harm an underestimate, never an overestimate.",
        },
    }
    RES.mkdir(exist_ok=True)
    (RES / "ampc_exposure.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["cohort"], indent=2))
    print(json.dumps(out["harmful_revisions"], indent=2))
    print(json.dumps(out["adequacy_labels_the_limitation_distrusts"], indent=2))


if __name__ == "__main__":
    main()
