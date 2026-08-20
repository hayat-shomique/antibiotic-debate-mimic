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
    b = sum(1 for d, s in pair_det if d["final_A_outcome"] == INA and s["final_A_outcome"] == ADQ)
    c = sum(1 for d, s in pair_det if d["final_A_outcome"] == ADQ and s["final_A_outcome"] == INA)
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
            "debate_harmful_and_control_not": c,
            "control_harmful_and_debate_not": b,
            "exact_mcnemar_p": mcnemar_exact(b, c),
            "reading": "b and c are the discordant pairs. A large c with a small b means the "
                       "counterpart is doing the damage. A comparable b and c means repetition "
                       "explains it and the word debate is the wrong word for the finding",
        },
        "_what_this_does_not_control": [
            "context length. The debate transcript is roughly twice as long by the final turn, "
            "because it carries the counterpart's turns as well as the agent's own",
            "turn count in total. The agent speaks three times in both arms, but the debate "
            "arm's context contains five turns and the control's contains three",
        ],
    }
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
    print(f"\n  paired, {t['pairs_usable']} usable: debate harmed and control did not = "
          f"{t['debate_harmful_and_control_not']}; the reverse = {t['control_harmful_and_debate_not']}; "
          f"exact McNemar p = {t['exact_mcnemar_p']:.3g}")


if __name__ == "__main__":
    main()
