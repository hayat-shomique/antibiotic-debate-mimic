#!/usr/bin/env python3
"""How many different antibiotics does the model ever actually choose?

This exists because the results are full of 100% figures, and a 100% is either a
tautology or a finding. This checks which.

The answer is that the model's default policy is a constant. It selects the same
antibiotic for every patient at baseline, independently reproduced across four
arms that ran at different times. Every "100%" in the baseline results is
measuring that constant, not measuring precision.

That makes the interesting comparison the one between what pressure does and what
evidence does, because those are the two things that can dislodge the constant.
"""
import json, glob, os
from collections import Counter

BRAIN = os.environ.get("BRAIN_RUNS") or os.path.expanduser("~/brain_run/runs")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHECKS = [
    ("c0cn_*.jsonl",          "c0_drug",     None,                                          "C0 baseline"),
    ("c0cn_*.jsonl",          "cn_drug",     None,                                          "Cn neutral control"),
    ("c1_*.jsonl",            "c0_drug",     lambda x: x.get("condition") == "C1_unsupported_pressure", "C0 inside the pressure arm"),
    ("c1_*.jsonl",            "c1_drug",     lambda x: x.get("condition") == "C1_unsupported_pressure", "C1 under unsupported pressure"),
    ("canonical_cleanc2.jsonl", "round0_drug", None,                                        "round 0 in the clean-context arm"),
    ("canonical_cleanc2.jsonl", "c2_drug",   None,                                          "C2 with the panel revealed"),
    ("debate_2026081*.jsonl", "drug",        lambda x: x.get("kind") == "round0",           "debate round 0"),
    ("debate_2026081*.jsonl", "drug",        lambda x: x.get("kind") == "full",             "debate final answer"),
]


def load(pat, filt):
    rows = []
    for f in sorted(glob.glob(os.path.join(BRAIN, pat))):
        for line in open(f):
            line = line.strip()
            if line:
                r = json.loads(line)
                if filt is None or filt(r):
                    rows.append(r)
    return rows


def main():
    out = {}
    print("How many distinct antibiotics the model ever chooses\n")
    print("  %-32s %8s %-26s %8s %7s" % ("stage", "distinct", "most common", "share", "n"))
    print("  " + "-" * 88)
    for pat, col, filt, label in CHECKS:
        rows = [r for r in load(pat, filt) if r.get(col) is not None]
        c = Counter(str(r[col]) for r in rows)
        if not c:
            continue
        drug, k = c.most_common(1)[0]
        n = sum(c.values())
        out[label] = {"distinct": len(c), "n": n, "top": drug,
                      "top_share_pct": round(100 * k / n, 1),
                      "distribution": dict(c.most_common())}
        print("  %-32s %8d %-26s %7.1f%% %7d" % (label, len(c), drug[:26], 100 * k / n, n))

    p = os.path.join(ROOT, "results", "policy_degeneracy.json")
    json.dump(out, open(p, "w"), indent=2)
    print("\n  written: results/policy_degeneracy.json")

    base = out.get("C0 baseline", {})
    pres = out.get("C1 under unsupported pressure", {})
    evid = out.get("C2 with the panel revealed", {})
    print("\n  Reading of this table")
    print("  The default policy selects %s for %.0f%% of patients (%d distinct choices)."
          % (base.get("top"), base.get("top_share_pct", 0), base.get("distinct", 0)))
    print("  Unsupported pressure moves it, but mostly to one other drug: %s at %.0f%% "
          "(%d distinct)." % (pres.get("top"), pres.get("top_share_pct", 0), pres.get("distinct", 0)))
    print("  The susceptibility panel produces genuine spread: %d distinct choices, the most "
          "common only %.0f%%." % (evid.get("distinct", 0), evid.get("top_share_pct", 0)))
    print("  Evidence produces patient-specific variation. Pressure produces uniform escalation.")


if __name__ == "__main__":
    main()
