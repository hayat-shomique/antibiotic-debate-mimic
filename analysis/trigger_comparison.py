"""trigger_comparison.py - the same move, two triggers, and the arm that must not be used for it.

The question is what happens when the model is made to reconsider a round-0 position it has
already committed to. There are two arms that ask exactly that, both starting from the same
frozen 200 cases and the same round-0 opening, both applying one reconsideration step:

  debate arm            round-0 position -> five turns against a counterpart carrying no
                        evidence -> final position. 400 ordering-runs, two speaking orders.
  clean-context panel   round-0 position -> the organism and its susceptibility panel, in a
                        clean context with no debate history -> revised position. 200 runs.

The panel-reveal arm is NOT the comparator, and this is the trap this file exists to close.
Its records carry the debate's own finals: all 400 of its final_A values equal the debate arm's
final_A for the same case and speaking order. The panel is revealed AFTER the debate, so a
round-0 to reveal transition crosses the debate and attributes the debate's damage to the panel.
Measured from the debate's final position, which is what it actually tests, it answers a
different and still useful question: once the run has already moved, does the laboratory result
put it back. That is reported here separately and labelled sequential.

The four-framing pressure arm is not a comparator either. It re-asks once where the debate runs
five turns, so a harmful revision rate from one is not comparable with a rate from the other.

Written to results/trigger_comparison.json. Aggregates only, no case-level rows.
"""
from __future__ import annotations

import collections
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
BRAIN = Path(os.environ.get("BRAIN_DIR") or os.path.expanduser("~/brain_run"))
ADQ, INA = "ADEQUATE", "INADEQUATE"
DET = (ADQ, INA)


def rows(name):
    return [json.loads(l) for l in open(BRAIN / "runs" / name) if l.strip()]


def transition(records, before_o, after_o, after_d, label, note):
    """Harmful revision and beneficial correction on runs determinate at both ends, which is
    the denominator the harmful revision rate uses everywhere else in this project."""
    det = [r for r in records if r[before_o] in DET and r[after_o] in DET]
    ent_a = [r for r in det if r[before_o] == ADQ]
    ent_i = [r for r in det if r[before_o] == INA]
    harmful = [r for r in ent_a if r[after_o] == INA]
    benef = [r for r in ent_i if r[after_o] == ADQ]
    return {
        "label": label,
        "note": note,
        "runs": len(records),
        "determinate_both_ends": len(det),
        "entered_adequate": len(ent_a),
        "harmful_revisions": len(harmful),
        "harmful_revision_rate_pct": round(100 * len(harmful) / len(ent_a), 1) if ent_a else None,
        "entered_inadequate": len(ent_i),
        "beneficial_corrections": len(benef),
        "beneficial_correction_rate_pct": round(100 * len(benef) / len(ent_i), 1) if ent_i else None,
        "destination_drug_when_the_revision_was_harmful": dict(
            sorted(collections.Counter(r[after_d] for r in harmful).items(), key=lambda kv: -kv[1])),
        "distinct_drugs_used_across_all_determinate_runs":
            len(set(r[after_d] for r in det)),
        "destination_drug_of_every_determinate_run": dict(
            sorted(collections.Counter(r[after_d] for r in det).items(), key=lambda kv: -kv[1])),
    }


def main():
    deb = [r for r in rows("debate_20260818.jsonl") if r.get("kind") == "full"]
    cc2 = rows("canonical_cleanc2.jsonl")
    rev = rows("canonical_reveal.jsonl")
    c1 = [r for r in sum((rows(n) for n in ("c1_20260818.jsonl", "c1_20260819.jsonl",
                                            "c1_20260820.jsonl")), []) if r.get("subtype")]

    # Proof, recomputed every run, that the reveal arm is downstream of the debate rather than
    # parallel to it. If this ever stops holding, the warning above is stale and must be redone.
    dmap = {(r["case_id"], r["ordering"]): r for r in deb}
    matched = [r for r in rev if (r["case_id"], r["ordering"]) in dmap]
    carries = sum(1 for r in matched if dmap[(r["case_id"], r["ordering"])]["final_A"] == r["final_A"])
    if not matched or carries != len(matched):
        raise SystemExit("the reveal arm no longer carries the debate's finals on every run, so "
                         "the sequential-not-parallel warning in this file must be re-derived")

    # The comparison only means anything if the arms start from the same position. Checked
    # rather than assumed, and recomputed on every run.
    deb_af = {r["case_id"]: r for r in deb if r["ordering"] == "A-first"}
    drug_same = sum(1 for r in c1 if r["case_id"] in deb_af
                    and r["c0_drug"] == deb_af[r["case_id"]]["round0_drug"])
    out_same = sum(1 for r in c1 if r["case_id"] in deb_af
                   and r["c0_outcome"] == deb_af[r["case_id"]]["round0_outcome"])
    n_cmp = sum(1 for r in c1 if r["case_id"] in deb_af)
    cc2_same = sum(1 for r in cc2 if r["case_id"] in deb_af
                   and r["round0_outcome"] == deb_af[r["case_id"]]["round0_outcome"])

    out = {
        "_purpose": "what one reconsideration step costs, by what triggers it, computed only "
                    "between arms that share a protocol",
        "_arms_start_from_the_same_position": {
            "one_turn_exposures_compared": n_cmp,
            "same_opening_drug": drug_same,
            "same_opening_outcome_class": out_same,
            "clean_context_runs_with_the_same_opening_outcome_class": cc2_same,
            "of_clean_context_runs": len(cc2),
            "reading": "the one-turn arm and the five-turn arm are elicited from the same "
                       "round-0 prompt at temperature zero with a fixed seed. Where the opening "
                       "drug differs it is decoding nondeterminism, and the outcome class, which "
                       "is what every rate here is computed on, is identical throughout. The "
                       "run files carry their own c0_matches_debate_round0 flag which reads "
                       "False on one case across all four framings. That flag compares against "
                       "whichever speaking order it read, and for that case it read the "
                       "B-first run, where the stewardship lead opens on a different drug. "
                       "Compared against the A-first run, which is the one where the same "
                       "agent opens, the openings match on every exposure",
        },
        "_pairing": {
            "cases_in_common_debate_and_clean_context":
                len({r["case_id"] for r in deb} & {r["case_id"] for r in cc2}),
            "debate_runs": len(deb), "clean_context_runs": len(cc2),
            "why_the_run_counts_differ": "the debate arm runs both speaking orders per case, the "
                                         "clean-context arm has no speaking order to vary",
        },
        "_reveal_arm_is_sequential_not_parallel": {
            "runs_checked": len(matched),
            "runs_whose_final_matches_the_debate_arm_exactly": carries,
            "consequence": "a round-0 to reveal transition would credit the panel with undoing "
                           "damage the debate caused in between, so it is not computed here",
        },
        "trigger_a_counterpart_with_no_evidence": transition(
            deb, "round0_outcome", "final_A_outcome", "final_A",
            "five-turn debate against a counterpart carrying no evidence",
            "one reconsideration step from the round-0 position"),
        "trigger_the_susceptibility_panel": transition(
            cc2, "round0_outcome", "c2_outcome", "c2_drug",
            "the organism and its susceptibility panel, clean context",
            "one reconsideration step from the round-0 position, no debate history"),
        "trigger_one_content_free_challenge": {
            sub: transition([r for r in c1 if r.get("subtype") == sub],
                            "c0_outcome", "c1_outcome", "c1_drug",
                            "a single content-free challenge, " + sub.split("_", 1)[1].replace("_", " "),
                            "one reconsideration step from the round-0 position, one turn not five")
            for sub in sorted({r["subtype"] for r in c1 if r.get("subtype")})
        },
        "after_the_debate_does_the_panel_repair_it": transition(
            rev, "final_A_outcome", "reveal_outcome", "reveal_drug",
            "panel revealed after the debate has already moved the position",
            "SEQUENTIAL. Not a comparator for the two above; it starts where the debate ended"),
    }
    RES.mkdir(exist_ok=True)
    (RES / "trigger_comparison.json").write_text(json.dumps(out, indent=2) + "\n")
    shown = [out["trigger_a_counterpart_with_no_evidence"]]
    shown += list(out["trigger_one_content_free_challenge"].values())
    shown += [out["trigger_the_susceptibility_panel"], out["after_the_debate_does_the_panel_repair_it"]]
    for v in shown:
        print(f"{v['label']}\n  entered adequate {v['entered_adequate']}, harmful {v['harmful_revisions']}"
              f" = {v['harmful_revision_rate_pct']}%   entered inadequate {v['entered_inadequate']},"
              f" corrected {v['beneficial_corrections']} = {v['beneficial_correction_rate_pct']}%"
              f"   distinct drugs {v['distinct_drugs_used_across_all_determinate_runs']}")
        print(f"  harmful destinations: {v['destination_drug_when_the_revision_was_harmful']}")


if __name__ == "__main__":
    main()
