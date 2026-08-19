#!/usr/bin/env python3
"""D-MATCH-1 analysis.

The design holds the seeded drug NAME fixed and varies only the patient. For each
drug, some cases carry an isolate the drug covers (ADEQUATE) and some carry one it
does not (INADEQUATE). The sentence, the clinical rationale and the system prompt
are identical across the two halves.

  Evidence account predicts: adoption is higher in the covering half.
  Identity account predicts: adoption is the same in both halves.

A note on the test. matched_pass.py pairs adq[k] with ina[k] by list position, so
the two cases in a pair share the drug but are NOT matched on patient covariates.
Calling that a matched pair and running McNemar would overclaim. What the design
actually buys is a comparison stratified by drug, with drug the only thing held
fixed. The correct pooled test is Cochran-Mantel-Haenszel across drug strata,
which is what is reported here.
"""
import json, glob, math
from collections import defaultdict

REC = sorted(glob.glob("runs/matched_*.jsonl"))


def truthy(v):
    """Records hold real JSON booleans; older ones held strings. Accept both."""
    return v is True or (isinstance(v, str) and v.lower() == "true")


def load():
    """Deduplicate on (case_id, seed_drug, receiver).

    Inference is deterministic here (temp 0, fixed seed), so a repeated key is a
    duplicate write, not a repeated measurement. Two matched_pass processes ran
    concurrently against the same output file on 19 Aug and each exposure landed
    twice; counting both would double every n and fake precision. First write wins.
    """
    out, seen, dropped = [], set(), 0
    for f in REC:
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if truthy(r.get("span_quarantine")):
                continue
            key = (r["case_id"], r["seed_drug"], r["receiver"])
            if key in seen:
                dropped += 1
                continue
            seen.add(key)
            out.append(r)
    if dropped:
        print("dropped %d duplicate writes; %d unique exposures remain\n" % (dropped, len(out)))
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def cmh(strata):
    """Cochran-Mantel-Haenszel over 2x2 tables.

    Each stratum is (a, b, c, d):
        a adopted / b declined  in the covering half
        c adopted / d declined  in the non-covering half
    Returns (chi2, p, odds_ratio_mh) or None if no stratum is informative.
    """
    num = den = 0.0
    var = 0.0
    or_n = or_d = 0.0
    used = 0
    for a, b, c, d in strata:
        n = a + b + c + d
        if n == 0:
            continue
        r1, r2 = a + b, c + d
        c1 = a + c
        if r1 == 0 or r2 == 0 or c1 == 0 or (b + d) == 0:
            continue
        used += 1
        exp = r1 * c1 / n
        num += a - exp
        v = r1 * r2 * c1 * (b + d) / (n * n * (n - 1)) if n > 1 else 0.0
        var += v
        or_n += a * d / n
        or_d += b * c / n
    if used == 0 or var <= 0:
        return None
    chi2 = (abs(num) - 0.5) ** 2 / var
    p = 2 * norm_sf(math.sqrt(chi2))
    orr = (or_n / or_d) if or_d > 0 else float("inf")
    return chi2, min(1.0, p), orr, used


def main():
    rows = load()
    print("D-MATCH-1: %d usable exposures from %d file(s)\n" % (len(rows), len(REC)))
    if not rows:
        return

    by = defaultdict(lambda: {"cov": [0, 0], "non": [0, 0]})
    for r in rows:
        half = "cov" if truthy(r["seed_is_adequate"]) else "non"
        cell = by[r["seed_drug"]][half]
        cell[1] += 1
        if truthy(r["adopted_seed"]):
            cell[0] += 1

    print("adoption of the seeded drug: same drug name, different patient")
    print("%-26s %21s %21s %9s" % ("drug", "covers patient", "does not cover", "gap"))
    print("-" * 80)
    tot = {"cov": [0, 0], "non": [0, 0]}
    strata = []
    for drug in sorted(by):
        a, i = by[drug]["cov"], by[drug]["non"]
        if a[1] == 0 or i[1] == 0:
            print("%-26s %21s %21s %9s"
                  % (drug, "%d/%d" % (a[0], a[1]), "%d/%d" % (i[0], i[1]), "incomplete"))
            continue
        pa, pi = a[0] / a[1], i[0] / i[1]
        for h, cc in (("cov", a), ("non", i)):
            tot[h][0] += cc[0]
            tot[h][1] += cc[1]
        strata.append((a[0], a[1] - a[0], i[0], i[1] - i[0]))
        print("%-26s %8d/%-3d %6.1f%% %8d/%-3d %6.1f%%   %+7.1f"
              % (drug, a[0], a[1], pa * 100, i[0], i[1], pi * 100, (pa - pi) * 100))

    a, i = tot["cov"], tot["non"]
    if a[1] == 0 or i[1] == 0:
        print("\nno drug has both halves populated yet; run is still in progress")
        return
    pa, pi = a[0] / a[1], i[0] / i[1]
    la, ha = wilson(*a)
    li, hi = wilson(*i)
    print("-" * 80)
    print("%-26s %8d/%-3d %6.1f%% %8d/%-3d %6.1f%%   %+7.1f"
          % ("POOLED", a[0], a[1], pa * 100, i[0], i[1], pi * 100, (pa - pi) * 100))
    print("%-26s %13s %8s %13s"
          % ("95% CI", "[%.1f, %.1f]" % (la * 100, ha * 100), "",
             "[%.1f, %.1f]" % (li * 100, hi * 100)))

    res = cmh(strata)
    print("\nCochran-Mantel-Haenszel, stratified by drug")
    if res is None:
        print("  no informative stratum yet")
    else:
        chi2, p, orr, used = res
        print("  strata contributing   %d" % used)
        print("  chi2 (continuity corrected) = %.4f" % chi2)
        print("  p = %.4f" % p)
        print("  Mantel-Haenszel odds ratio = %.3f" % orr)
        print("  (OR of 1.000 means coverage of the patient did not shift adoption)")

    print("\nwhen the seeded drug was declined, what replaced it")
    repl = defaultdict(int)
    for r in rows:
        if not truthy(r["adopted_seed"]):
            repl[r["answer_drug"]] += 1
    n_dec = sum(repl.values())
    for d, k in sorted(repl.items(), key=lambda x: -x[1])[:8]:
        print("  %-32s %4d/%d  %5.1f%%" % (d, k, n_dec, k / n_dec * 100))

    print("\noutcome of the drug finally chosen")
    oc = defaultdict(int)
    for r in rows:
        oc[r["answer_outcome"]] += 1
    for k, v in sorted(oc.items(), key=lambda x: -x[1]):
        print("  %-22s %4d/%d  %5.1f%%" % (k, v, len(rows), v / len(rows) * 100))


if __name__ == "__main__":
    main()
