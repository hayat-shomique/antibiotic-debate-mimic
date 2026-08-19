#!/usr/bin/env python3
"""Rung two of the supervisor's escalation ladder: does few-shot help?

Her instruction, 13 July:

  "zero shot will not work, we can take something ready made and say like, look,
   this is already trained. And then I'm going to use some example of how it look
   like. And then so you give it, like, a few shots and then see whether it
   improves. And if it doesn't, then you can move it to the next level, that is
   now your training from scratch."

Two things are measured, because moving off the constant is not the same as doing
better, and the interesting result is if they disagree:

  coverage   does the recommendation cover the organism the laboratory identified
  spectrum   how broad is the agent chosen, endpoint 4

And one validity check. If the model simply repeats whichever drug appeared in its
exemplars, few-shot has taught it nothing about the patient; it has just moved the
constant. `answer_in_examples` and the exemplar drug list make that testable.
"""
import json, glob, math, os
from collections import Counter, defaultdict

BRAIN = os.environ.get("BRAIN_RUNS") or os.path.expanduser("~/brain_run/runs")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORRECT = "ADEQUATE"
CARBAPENEM = {"meropenem", "imipenem", "ertapenem"}
AWARE = {"ampicillin": "Access", "ampicillin-sulbactam": "Access",
         "amoxicillin-clavulanate": "Access", "cefazolin": "Access", "gentamicin": "Access",
         "trimethoprim-sulfamethoxazole": "Access", "nitrofurantoin": "Access",
         "ceftriaxone": "Watch", "cefepime": "Watch", "ceftazidime": "Watch",
         "ciprofloxacin": "Watch", "levofloxacin": "Watch",
         "piperacillin-tazobactam": "Watch", "vancomycin": "Watch", "meropenem": "Watch",
         "imipenem": "Watch", "ertapenem": "Watch", "linezolid": "Reserve",
         "daptomycin": "Reserve", "colistin": "Reserve", "tigecycline": "Reserve"}


def truthy(v):
    return v is True or (isinstance(v, str) and v.lower() == "true")


def load():
    rows, seen = [], set()
    for f in sorted(glob.glob(os.path.join(BRAIN, "fewshot_2*.jsonl"))):
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if truthy(r.get("gate_quarantine")):
                continue
            k = (r["case_id"], r.get("fewshot_arm_sha"))
            if k in seen:
                continue
            seen.add(k)
            rows.append(r)
    return rows


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


def main():
    rows = load()
    if not rows:
        print("no few-shot records yet")
        return
    n = len(rows)
    arms = {r.get("fewshot_arm_sha") for r in rows}
    print("Few-shot, rung two of the ladder")
    print("  %d cases, %d arm configuration(s), k = %s shots\n"
          % (n, len(arms), sorted({str(r.get("k")) for r in rows})))

    # ---- paired coverage: same case, zero-shot vs few-shot
    zs_out = {r["case_id"]: r.get("zeroshot_outcome") for r in rows}
    b = c = 0
    fs_ok = sum(1 for r in rows if r.get("fs_outcome") == CORRECT)
    # zero-shot outcome is not always stored per row; fall back to the baseline arm
    base = {}
    for f in glob.glob(os.path.join(BRAIN, "c0cn_*.jsonl")):
        for line in open(f):
            if line.strip():
                x = json.loads(line)
                base[x["case_id"]] = x["c0_outcome"]
    paired = [(base.get(r["case_id"]), r.get("fs_outcome")) for r in rows
              if r["case_id"] in base]
    det = [(z, f) for z, f in paired if z in (CORRECT, "INADEQUATE") and f in (CORRECT, "INADEQUATE")]
    for z, f in det:
        if z == CORRECT and f != CORRECT:
            b += 1
        elif z != CORRECT and f == CORRECT:
            c += 1
    zs_ok = sum(1 for z, _ in det if z == CORRECT)
    fs_ok_p = sum(1 for _, f in det if f == CORRECT)

    print("  COVERAGE, endpoint 1")
    lo, hi = wilson(fs_ok, n)
    print("    few-shot, all cases            %3d/%-3d = %5.1f%%  [%.1f, %.1f]"
          % (fs_ok, n, 100 * fs_ok / n, lo, hi))
    if det:
        print("    paired subset, %d cases where both are determinate:" % len(det))
        print("      zero-shot                    %3d/%-3d = %5.1f%%" % (zs_ok, len(det), 100 * zs_ok / len(det)))
        print("      few-shot                     %3d/%-3d = %5.1f%%" % (fs_ok_p, len(det), 100 * fs_ok_p / len(det)))
        print("      lost by few-shot  b = %d      gained  c = %d      exact McNemar p = %.4g"
              % (b, c, mcnemar_exact(b, c)))

    # ---- spectrum
    fs = Counter(r["fs_drug"] for r in rows if r.get("fs_drug"))
    zs = Counter(r["zeroshot_drug"] for r in rows if r.get("zeroshot_drug"))
    def spec(cnt):
        t = sum(cnt.values())
        carb = sum(v for k, v in cnt.items() if k in CARBAPENEM)
        aw = Counter(AWARE.get(k, "unclassified") for k in cnt.elements())
        acc = aw.get("Access", 0)
        return len(cnt), carb, t, acc, dict(aw)
    print("\n  SPECTRUM, endpoint 4")
    for lbl, cnt in (("zero-shot", zs), ("few-shot", fs)):
        d, carb, t, acc, aw = spec(cnt)
        print("    %-10s %2d distinct   carbapenem %3d/%-3d = %5.1f%%   Access %3d/%-3d = %5.1f%%"
              % (lbl, d, carb, t, 100 * carb / t, acc, t, 100 * acc / t))

    # ---- validity: is it learning, or copying the exemplars?
    print("\n  VALIDITY: is few-shot reading the patient, or repeating its exemplars?")
    in_ex = sum(1 for r in rows if truthy(r.get("answer_in_examples")))
    print("    answer appeared in that case's own exemplars   %d/%d = %.1f%%"
          % (in_ex, n, 100 * in_ex / n))
    moved = sum(1 for r in rows if truthy(r.get("changed_vs_zeroshot")))
    print("    moved off the zero-shot constant               %d/%d = %.1f%%"
          % (moved, n, 100 * moved / n))
    nd = Counter(str(r.get("n_distinct_example_answers")) for r in rows)
    print("    distinct answers among the exemplars shown:", dict(nd.most_common(5)))
    print("    If the answer is almost always inside the exemplar set, few-shot has moved the")
    print("    constant rather than taught the model to read the patient.")

    out = {"n": n, "coverage_all": {"k": fs_ok, "n": n, "pct": round(100 * fs_ok / n, 1)},
           "paired": {"n": len(det), "zeroshot_correct": zs_ok, "fewshot_correct": fs_ok_p,
                      "b_lost": b, "c_gained": c, "p_exact": mcnemar_exact(b, c)},
           "spectrum": {"zeroshot": dict(zs), "fewshot": dict(fs)},
           "validity": {"answer_in_examples": in_ex, "moved_vs_zeroshot": moved}}
    json.dump(out, open(os.path.join(ROOT, "results", "fewshot.json"), "w"), indent=2)
    print("\n  written: results/fewshot.json")


if __name__ == "__main__":
    main()
