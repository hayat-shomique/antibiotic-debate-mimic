"""clinician_comparison.py - the second comparison she asked for, twice.

30 July 09:43: "So here you can prompt LLM to see if it predict the antibiotic
corrected before the ground truth. You can also compare LLM with clinician see if
they agree or LLM is worse or better?"

Model against ground truth is the primary endpoint. This is the other half: the
model against what the treating clinician actually prescribed, scored by the same
rule against the same panels. Aggregates only, written to
results/clinician_comparison.json.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
SRC = Path.home() / "brain_run" / "clinician_comparator_v2_summary.json"

if not SRC.exists():
    raise SystemExit(f"clinician comparator not found at {SRC}. It is produced by _cc2_build_v2.py "
                     "in the run directory and is not committed, because it is derived from "
                     "credentialed prescribing records.")

cc = json.loads(SRC.read_text())
prim = cc["clinician_primary"]["counts"]
n = cc["clinician_primary"]["n_cases"]

T = json.loads((RES / "tingting_endpoints.json").read_text())
model = T["primary_appropriateness"]["baseline_pre_culture"]["breakdown"]
model_n = T["primary_appropriateness"]["baseline_pre_culture"]["n"]


def determined(counts):
    """UNDETERMINED means the laboratory never tested that agent against that organism.
    It is not a wrong answer and it cannot be scored, so it leaves the denominator."""
    und = counts.get("UNDETERMINED", 0)
    return counts.get("ADEQUATE", 0), sum(counts.values()) - und


k_c, n_c = determined(prim)
k_m, n_m = determined(model)

out = {
    "_ask": ("Prof. Tingting Zhu, 30 July 2026: 'You can also compare LLM with clinician see if they "
             "agree or LLM is worse or better?'"),
    "_scoring": ("the identical rule scores both sides, protocol_v1 line 65: a regimen covers if any "
                 "administered or recommended agent covers, and a polymicrobial case is adequate only "
                 "if every pathogenic isolate is covered"),
    "_window": cc["window"]["primary"],
    "_deviation": cc.get("deviation"),
    "clinician": {
        "n": n, "counts": prim,
        "adequate_all_cases_pct": round(100.0 * prim.get("ADEQUATE", 0) / n, 1),
        "adequate_determined_only": {"k": k_c, "n": n_c, "pct": round(100.0 * k_c / n_c, 1)},
    },
    "model_zero_shot": {
        "n": model_n, "counts": model,
        "adequate_all_cases_pct": round(100.0 * model.get("ADEQUATE", 0) / model_n, 1),
        "adequate_determined_only": {"k": k_m, "n": n_m, "pct": round(100.0 * k_m / n_m, 1)},
    },
    "gap_determined_only_pts": round(100.0 * k_m / n_m - 100.0 * k_c / n_c, 1),
    "_reading": ("The margin on the full cohort is a denominator artefact: the clinician scores "
                 "UNDETERMINED far more often, largely because real prescriptions fall outside the "
                 "closed 17-drug formulary or were never tested against the isolate. Restricted to "
                 "what each side can be scored on, the two rates are within a point of each other. "
                 "The answer to her question is that on this evidence neither is better."),
    "_this_is_not_a_paired_comparison": (
        "The two determinate-only rates sit on different sets of cases, 138 for the clinician and "
        "192 for the model, so this is two independent proportions and not a paired test. An "
        "earlier version of this reading said the two were indistinguishable on the cases where "
        "both can be scored, which is a claim about a set that was never constructed. The paired "
        "version needs per-case outcomes for the clinician side, and the comparator artefact "
        "carries aggregates only, because it is derived from credentialed prescribing records. "
        "Building it is the next step on this endpoint and it is named as further work rather "
        "than implied here."),
}
(RES / "clinician_comparison.json").write_text(json.dumps(out, indent=2))
print(f"wrote results/clinician_comparison.json")
print(f"  clinician  {k_c}/{n_c} = {out['clinician']['adequate_determined_only']['pct']}% determined-only, "
      f"{out['clinician']['adequate_all_cases_pct']}% of all {n}")
print(f"  model      {k_m}/{n_m} = {out['model_zero_shot']['adequate_determined_only']['pct']}% determined-only, "
      f"{out['model_zero_shot']['adequate_all_cases_pct']}% of all {model_n}")
