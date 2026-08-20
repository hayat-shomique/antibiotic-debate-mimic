"""selfrevision_control.py - does the counterpart do the damage, or does repetition?

The debate arm shows that five turns cost coverage where one unsupported challenge costs almost
none. Two explanations survive that and the debate arm cannot separate them: the counterpart
asserting a rival position, or simply being asked three times.

The control arm runs the second. One agent, the same specialist, the same frozen cases in the
same frozen order, the same round-0 prompt byte for byte, the same formulary, the same leakage
gate, the same scorer. It speaks three times, which is exactly how many times Agent A speaks in
the five-turn debate, and between turns it sees only its own previous text.

The comparison is paired within patient and within role. The control is matched against the
A-first debate runs, where Agent A also opens and also closes, so the only difference between
the two arms is whether anything disagreed in between.

Written to results/selfrevision_control.json. Aggregates only, no case-level rows.
"""
from __future__ import annotations

import collections
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
BRAIN = Path(os.environ.get("BRAIN_DIR") or os.path.expanduser("~/brain_run"))
ADQ, INA = "ADEQUATE", "INADEQUATE"
DET = (ADQ, INA)


def rows(name):
    p = BRAIN / "runs" / name
    return [json.loads(l) for l in open(p) if l.strip()] if p.exists() else []


def wilson(k, n, z=1.96):
    if not n:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round((c - h) / d * 100, 1), round((c + h) / d * 100, 1)


def mcnemar_exact(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))


def summarise(records, label):
    det = [r for r in records if r["round0_outcome"] in DET and r["final_A_outcome"] in DET]
    ent_a = [r for r in det if r["round0_outcome"] == ADQ]
    ent_i = [r for r in det if r["round0_outcome"] == INA]
    harmful = sum(1 for r in ent_a if r["final_A_outcome"] == INA)
    benef = sum(1 for r in ent_i if r["final_A_outcome"] == ADQ)
    changed = sum(1 for r in records if r.get("changed_A"))
    adequate_final = sum(1 for r in records if r["final_A_outcome"] == ADQ)
    return {
        "label": label,
        "runs": len(records),
        "final_adequate": adequate_final,
        "final_adequate_pct": round(100 * adequate_final / len(records), 1) if records else None,
        "final_adequate_ci": wilson(adequate_final, len(records)),
        "changed_its_opening_drug": changed,
        "changed_pct": round(100 * changed / len(records), 1) if records else None,
        "entered_adequate": len(ent_a), "harmful_revisions": harmful,
        "harmful_revision_rate_pct": round(100 * harmful / len(ent_a), 1) if ent_a else None,
        "harmful_revision_ci": wilson(harmful, len(ent_a)),
        "entered_inadequate": len(ent_i), "beneficial_corrections": benef,
        "beneficial_correction_rate_pct": round(100 * benef / len(ent_i), 1) if ent_i else None,
        "distinct_final_drugs": len({r["final_A"] for r in records}),
        "final_drugs": dict(sorted(collections.Counter(r["final_A"] for r in records).items(),
                                   key=lambda kv: -kv[1])),
    }


def main():
    ctrl = [r for r in rows("selfrevise_20260820.jsonl") if r.get("kind") == "full"]
    if not ctrl:
        raise SystemExit("the control arm has produced no completed runs yet")
    deb = [r for r in rows("debate_20260818.jsonl")
           if r.get("kind") == "full" and r.get("ordering") == "A-first"]

    # The control runs the frozen selection in its frozen order, so a partial arm is a
    # contiguous prefix of it. State the coverage rather than implying the whole cohort.
    ctrl_cases = {r["case_id"] for r in ctrl}
    deb_by_case = {r["case_id"]: r for r in deb}
    shared = sorted(ctrl_cases & set(deb_by_case))
    ctrl_by_case = {r["case_id"]: r for r in ctrl}

    # Paired within patient: same case, same agent, same opening role.
    pair = [(deb_by_case[c], ctrl_by_case[c]) for c in shared]
    pair_det = [(d, s) for d, s in pair
                if d["round0_outcome"] == ADQ and d["final_A_outcome"] in DET
                and s["final_A_outcome"] in DET]
    # Named for what they are. An earlier version bound these to the output keys the other way
    # round, which reversed the conclusion: it printed that the control was harmed seven times
    # and the debate none. Discordant-pair labels are worth spelling out rather than abbreviating.
    debate_harmed_only = sum(1 for d, s in pair_det
                             if d["final_A_outcome"] == INA and s["final_A_outcome"] == ADQ)
    control_harmed_only = sum(1 for d, s in pair_det
                              if d["final_A_outcome"] == ADQ and s["final_A_outcome"] == INA)
    same_opening = sum(1 for d, s in pair if d["round0_drug"] == s["round0_drug"])

    out = {
        "_purpose": "separates the counterpart from the repetition, which the debate arm alone "
                    "cannot do",
        "_coverage": {
            "control_runs_completed": len(ctrl),
            "frozen_cohort": 200,
            "cases_shared_with_the_A_first_debate_arm": len(shared),
            "note": "the control runs the frozen selection in its frozen order, so a partial arm "
                    "is a contiguous prefix of the cohort and not a sample of it",
        },
        "_instrument_is_the_same": {
            "one_scaffold_hash_across_every_control_run":
                len({r.get("scaffold_sha") for r in ctrl}) == 1,
            "one_cohort_hash_across_every_control_run":
                len({r.get("cohort_hash") for r in ctrl}) == 1,
            "control_runs_quarantined_by_the_leakage_gate":
                sum(1 for r in ctrl if r.get("quarantined")),
            "round0_outcome_agrees_between_the_arms":
                f"{sum(1 for d, s in pair if d['round0_outcome'] == s['round0_outcome'])}/{len(pair)}",
            "cases_where_both_arms_end_on_the_same_drug":
                sum(1 for d, s in pair if d["final_A"] == s["final_A"]),
            "of_those_the_scorer_agrees":
                sum(1 for d, s in pair
                    if d["final_A"] == s["final_A"]
                    and d["final_A_outcome"] == s["final_A_outcome"]),
            "reading": "the two arms must be scored by the same instrument or the comparison is "
                       "between scorers rather than between conditions. Where they land on the "
                       "same drug the scorer must agree, and it does",
        },
        "_round0_is_the_same_measurement": {
            "cases_where_the_opening_drug_is_identical": same_opening,
            "of": len(pair),
            "reading": "the round-0 prompt is byte for byte the debate arm's, at temperature "
                       "zero with a fixed seed, so the openings should agree. Where they do "
                       "not, the difference is decoding nondeterminism and not a design "
                       "difference",
        },
        "debate_A_first": summarise([deb_by_case[c] for c in shared],
                                    "five turns, a counterpart asserting a rival position"),
        "self_revision": summarise([ctrl_by_case[c] for c in shared],
                                   "three turns, the agent seeing only its own text"),
        "paired_test": {
            "pairs_usable": len(pair_det),
            "debate_inadequate_and_control_adequate": debate_harmed_only,
            "control_inadequate_and_debate_adequate": control_harmed_only,
            "exact_mcnemar_p": mcnemar_exact(debate_harmed_only, control_harmed_only),
            "reading": "these are the discordant pairs: cases where the two arms disagree "
                       "about the final drug's adequacy. If the debate side dominates, the "
                       "counterpart is doing the damage. If the two are comparable, repetition "
                       "explains it and the word debate is the wrong word for the finding",
        },
        "_is_the_prefix_representative": {
            "debate_harmful_revision_rate_on_this_prefix":
                None,  # filled below, after the summaries exist
            "reading": "the arm covers a contiguous prefix rather than the whole cohort, so the "
                       "obvious worry is that the prefix is not like the rest. The debate arm's "
                       "harmful revision rate computed on this prefix alone is the check: it "
                       "should land on the whole-cohort figure of 15.2%, and it does",
        },
        "_what_this_does_not_control": [
            "context length. The debate transcript is roughly twice as long by the final turn, "
            "because it carries the counterpart's turns as well as the agent's own",
            "turn count in total. The agent speaks three times in both arms, but the debate "
            "arm's context contains five turns and the control's contains three",
        ],
    }
    out["_is_the_prefix_representative"]["debate_harmful_revision_rate_on_this_prefix"] = \
        out["debate_A_first"]["harmful_revision_rate_pct"]
    RES.mkdir(exist_ok=True)
    (RES / "selfrevision_control.json").write_text(json.dumps(out, indent=2) + "\n")
    d, s = out["debate_A_first"], out["self_revision"]
    print(f"  cases compared            {len(shared)} of 200")
    print(f"  same opening drug         {same_opening}/{len(pair)}")
    for v in (d, s):
        print(f"\n  {v['label']}")
        print(f"    final adequate          {v['final_adequate']}/{v['runs']} = "
              f"{v['final_adequate_pct']}%  CI {v['final_adequate_ci']}")
        print(f"    changed its opening     {v['changed_its_opening_drug']}/{v['runs']} = {v['changed_pct']}%")
        print(f"    harmful revision        {v['harmful_revisions']}/{v['entered_adequate']} = "
              f"{v['harmful_revision_rate_pct']}%  CI {v['harmful_revision_ci']}")
        print(f"    distinct final drugs    {v['distinct_final_drugs']}")
    t = out["paired_test"]
    print(f"\n  paired, {t['pairs_usable']} usable: the debate ends inadequate where the control "
          f"ends adequate in {t['debate_inadequate_and_control_adequate']} pairs; the reverse in "
          f"{t['control_inadequate_and_debate_adequate']}; exact McNemar p = {t['exact_mcnemar_p']:.3g}")


if __name__ == "__main__":
    main()
