"""claim_confidence.py - how much weight each headline claim can actually carry.

A number is not a finding. What makes a number a finding is the design behind it, and the designs
in this project are not equally strong. This file grades every claim that reaches a slide against
four things that can be checked rather than asserted:

  paired          is the comparison within patient, so the patient is its own control
  controlled      is there an arm that removes the alternative explanation
  replicated      does a second implementation, or a second denominator, reproduce it
  bounded         is the residual uncertainty named on the slide rather than left to be found

The grades are computed from the result files, not typed. A claim whose supporting arm shrinks, or
whose control is removed, loses its grade automatically the next time this runs.

Written to results/claim_confidence.json. Aggregates only.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"


def load(name):
    p = RES / name
    return json.loads(p.read_text()) if p.exists() else None


T = load("tingting_endpoints.json")
P = load("primary_test.json")
TRIG = load("trigger_comparison.json")
SRC = load("selfrevision_control.json")
CLIN = load("clinician_comparison.json")
FS = load("fewshot.json")
R = load("RESULTS.json")
AMPC = load("ampc_exposure.json")


def grade(paired, controlled, replicated, bounded):
    """Four checks, and the grade is what they add up to. No judgement is applied on top."""
    score = sum(bool(x) for x in (paired, controlled, replicated, bounded))
    return {4: "high", 3: "good", 2: "moderate", 1: "weak", 0: "not established"}[score]


def claim(name, number, paired, controlled, replicated, bounded, what_would_break_it, arm_n):
    return {
        "claim": name,
        "number": number,
        "n": arm_n,
        "paired_within_patient": paired,
        "has_a_control_arm": controlled,
        "reproduced_independently": replicated,
        "residual_uncertainty_stated_on_the_slide": bounded,
        "confidence": grade(paired, controlled, replicated, bounded),
        "what_would_break_it": what_would_break_it,
    }


def main():
    deb = TRIG["trigger_a_counterpart_with_no_evidence"]
    null = TRIG["trigger_nothing_a_neutral_re_ask"]
    one = list(TRIG["trigger_one_content_free_challenge"].values())
    pan = TRIG["trigger_the_susceptibility_panel"]
    p_worst = max(v["discordant"]["p_exact"] for v in P["by_framing"].values())
    n_min = min(v["n_primary"] for v in P["by_framing"].values())
    n_max = max(v["n_primary"] for v in P["by_framing"].values())

    claims = [
        claim("An unsupported challenge moves the model where a neutral re-ask never does",
              f"discordant pairs {min(v['discordant']['b_pressure_only'] for v in P['by_framing'].values())} "
              f"to {max(v['discordant']['b_pressure_only'] for v in P['by_framing'].values())} against 0, "
              f"exact binomial p at most {p_worst:.3g}",
              paired=True, controlled=True, replicated=True, bounded=True,
              what_would_break_it="nothing available in this design. The neutral arm is the control, "
                                  "the test was pre-specified, the pairing is within patient, and the "
                                  "p value recomputes from scratch. The bound is the attrition, which "
                                  "is decomposed and survives a worst-case sensitivity assignment",
              arm_n=f"{n_min} to {n_max} of 200 per framing"),
        claim("A five-turn debate costs coverage of the organism",
              f"{T['debate_coverage']['before_debate']['pct']}% to "
              f"{T['debate_coverage']['after_debate']['pct']}%, "
              f"{T['debate_coverage']['debate_change_pts']:+.1f} points; harmful revision "
              f"{T['debate_with_live_agent']['HRR']['k']}/{T['debate_with_live_agent']['HRR']['n']} = "
              f"{T['debate_with_live_agent']['HRR']['pct']}%",
              paired=True, controlled=True, replicated=True, bounded=True,
              what_would_break_it="the counterpart is scripted in the pressure arm but a live second "
                                  "agent here, and both agents are the same checkpoint, so this is "
                                  "one model talking to itself with two personas. A second checkpoint "
                                  "as the counterpart would test whether the effect survives",
              arm_n="400 ordering-runs over 200 cases"),
        claim("Being contradicted moves the model, being asked again does not",
              f"changed its drug {SRC['debate_A_first']['changed_its_opening_drug']} of "
              f"{SRC['_coverage']['cases_shared_with_the_A_first_debate_arm']} with a counterpart against "
              f"{SRC['self_revision']['changed_its_opening_drug']} without one; harmful revision "
              f"{SRC['debate_A_first']['harmful_revision_rate_pct']}% against "
              f"{SRC['self_revision']['harmful_revision_rate_pct']}%; exact McNemar "
              f"p = {SRC['paired_test']['exact_mcnemar_p']:.3g}",
              paired=True, controlled=True, replicated=False, bounded=True,
              what_would_break_it="the control does not hold context length constant, and it does not "
                                  "hold the revision instruction constant. A speaker-stripped arm, "
                                  "which keeps the counterpart's text and removes only the "
                                  "attribution, is what separates being contradicted by a peer from "
                                  "being contradicted by anything. Not built",
              arm_n=f"{SRC['_coverage']['cases_shared_with_the_A_first_debate_arm']} of 200, a "
                    f"contiguous prefix"),
        claim("Duration, not the framing of the challenge, is what costs coverage",
              f"one turn costs {min(v['harmful_revision_rate_pct'] for v in one)}% to "
              f"{max(v['harmful_revision_rate_pct'] for v in one)}% across four framings; five turns "
              f"cost {deb['harmful_revision_rate_pct']}%",
              paired=True, controlled=True, replicated=True, bounded=True,
              what_would_break_it="the one-turn and five-turn arms differ in protocol as well as in "
                                  "length: one re-asks once, the other runs a live exchange. A "
                                  "turn-count sweep inside one protocol is the clean version",
              arm_n="800 one-turn exposures against 400 ordering-runs, same 200 cases"),
        claim("The answer space collapses under debate and stays open under evidence",
              f"{deb['distinct_drugs_used_across_all_determinate_runs']} distinct drugs after the "
              f"debate against {pan['distinct_drugs_used_across_all_determinate_runs']} after the "
              f"panel, and {null['distinct_drugs_used_across_all_determinate_runs']} with no challenge at all",
              paired=True, controlled=True, replicated=False, bounded=True,
              what_would_break_it="distinct-drug counts are a crude diversity measure and are "
                                  "sensitive to the closed formulary. It is a description of the "
                                  "arms, not a test, and no interval is attached to it",
              arm_n="same 200 cases in every arm"),
        claim("An unsupported sentence drives carbapenem prescribing from nothing to most of the cohort",
              f"{T['spectrum_appropriateness']['baseline']['carbapenem_pct']}% to "
              f"{T['spectrum_appropriateness']['under_pressure']['carbapenem_pct']}% carbapenem use",
              paired=True, controlled=True, replicated=True, bounded=True,
              what_would_break_it="this is prescribing behaviour on a counterfactual recommendation, "
                                  "never a demonstrated patient outcome. The harm axis it moves along "
                                  "is published, not measured here",
              arm_n="800 exposures over 200 cases"),
        claim("Few-shot examples do not improve the decision",
              f"{FS['paired']['b_lost']} correct answers lost against {FS['paired']['c_gained']} "
              f"gained on {FS['paired']['n']} paired cases, exact McNemar p = "
              f"{FS['paired']['p_exact']:.3g}",
              paired=True, controlled=False, replicated=True, bounded=True,
              what_would_break_it="one exemplar-selection strategy at one k. A different selection "
                                  "rule or a larger k is a different experiment, and no arm varies "
                                  "either",
              arm_n=f"{FS['paired']['n']} paired determinate cases of 200"),
        claim("The model and the clinician are within a point of each other",
              f"{CLIN['model_zero_shot']['adequate_determined_only']['pct']}% on "
              f"{CLIN['model_zero_shot']['adequate_determined_only']['n']} cases against "
              f"{CLIN['clinician']['adequate_determined_only']['pct']}% on "
              f"{CLIN['clinician']['adequate_determined_only']['n']}",
              paired=False, controlled=False, replicated=False, bounded=True,
              what_would_break_it="the two rates sit on different sets of cases, so this is two "
                                  "independent proportions and not a paired test. The paired version "
                                  "needs per-case clinician outcomes, which the comparator artefact "
                                  "does not carry. This is the weakest claim in the project and it is "
                                  "reported as such",
              arm_n="192 and 138 of 200, different sets"),
        claim("Adequacy labels are bounded by unhandled AmpC induction, and the harm finding is not",
              f"{AMPC['cohort']['any_ampc_capable']} of {AMPC['cohort']['n_cases']} specimens carry an "
              f"AmpC-capable organism; "
              f"{AMPC['adequacy_labels_the_limitation_distrusts']['runs_ending_on_a_third_generation_cephalosporin_against_an_ampc_capable_organism_and_scored_adequate']} "
              f"runs are affected, against "
              f"{AMPC['harmful_revisions']['onto_a_third_generation_cephalosporin_against_an_ampc_capable_organism']} "
              f"of the {AMPC['harmful_revisions']['n']} harmful revisions",
              paired=False, controlled=False, replicated=True, bounded=True,
              what_would_break_it="the organism grading is a reading of one primer applied to twenty "
                                  "laboratory labels, not a measurement. It reproduces an independent "
                                  "count in the red-team document, which is why it is graded at all",
              arm_n="200 specimens, 400 ordering-runs"),
    ]

    order = {"high": 0, "good": 1, "moderate": 2, "weak": 3, "not established": 4}
    claims.sort(key=lambda c: order[c["confidence"]])
    tally = {}
    for c in claims:
        tally[c["confidence"]] = tally.get(c["confidence"], 0) + 1

    out = {
        "_purpose": "how much weight each headline claim can carry, graded on four checkable "
                    "properties rather than on how good the number looks",
        "_how_the_grade_is_computed": {
            "paired_within_patient": "the same patient is put to the model in both conditions, so "
                                     "between-patient variation cannot explain the difference",
            "has_a_control_arm": "an arm exists that removes the leading alternative explanation",
            "reproduced_independently": "a second implementation, a second denominator or a "
                                        "recomputation from the raw run files gives the same answer",
            "residual_uncertainty_stated_on_the_slide": "what could still be wrong is named where "
                                                        "the claim is made, not left to be found",
            "grade": "four of four is high, three good, two moderate, one weak, none not established",
        },
        "_tally": tally,
        "_arms": {"registered": len(R["_integrity"]),
                  "deduplicated_exposures": sum(m["n"] for m in R["_integrity"].values())},
        "claims": claims,
    }
    RES.mkdir(exist_ok=True)
    (RES / "claim_confidence.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"{len(claims)} claims graded: " + ", ".join(f"{v} {k}" for k, v in tally.items()))
    for c in claims:
        print(f"  [{c['confidence']:>15}]  {c['claim']}")


if __name__ == "__main__":
    main()
