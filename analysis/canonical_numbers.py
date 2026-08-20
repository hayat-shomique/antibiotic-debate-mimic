#!/usr/bin/env python3
"""Single source of truth for every number in this project.

Why this file exists
--------------------
Numbers were being recomputed ad hoc in a dozen scripts, and on 19 Aug two
matched_pass processes ran concurrently against the same output file, writing
every exposure twice. Any analysis that counted lines rather than exposures
would have doubled n and halved its standard errors. This module fixes the
identity of an exposure once, per arm, and everything downstream cites it.

The identity key
----------------
An exposure is one model decision under one experimental cell. Inference runs at
temperature 0 with a fixed seed, so two records sharing an identity key are a
repeated write, not a repeated measurement, and the second is dropped.

Getting the key right per arm matters more than it sounds. Two examples that look
like duplication and are not:
  debate arms  carry two speaking orders and several turns per case, so identity
               is (case, drug, ordering, turn)
  reveal arms  carry two speaking orders per case, so identity is
               (case, condition, ordering)
and one that looks fine and is not:
  C1           carries four pressure framings per case in a `subtype` column, so
               keying on (case, condition) alone collapses four real cells into
               one and silently discards three quarters of the data

Output
------
Writes RESULTS.json next to this file. Every published document cites that file.
"""
import json, glob, math, os, sys
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))

# Raw run data never enters the repository: a case_id is subject_id + "_" +
# micro_specimen_id, so committing one republishes two credentialed identifiers.
# The data stays in the local scratch directory and the path is configurable, so
# this file is runnable from inside the repo checkout.
RUNS = os.environ.get("BRAIN_RUNS") or os.path.join(HERE, "runs")
if not os.path.isdir(RUNS):
    RUNS = os.path.expanduser("~/brain_run/runs")
OUT_DIR = os.environ.get("BRAIN_OUT") or HERE

# arm -> (glob patterns, identity key columns, human note)
ARMS = {
    "C0_baseline":   (["c1_*.jsonl"], ("case_id",),
                      "pre-culture baseline INSIDE THE PRESSURE ARM. Not the same population as the baseline in the neutral-control arm; see tingting_endpoints.json",
                      lambda r: r.get("condition") == "C0_pre_culture_baseline"),
    "C1_pressure":   (["c1_*.jsonl"], ("case_id", "condition", "subtype"),
                      "four pressure framings per case; subtype is a real cell, not a duplicate"),
    "D_MATCH_1":     (["matched_*.jsonl"], ("case_id", "seed_drug", "receiver"),
                      "drug name held fixed, patient varied"),
    "D_CALIB_1":     (["calib_*.jsonl"], ("case_id", "drug"),
                      "stated confidence resolved against the panel"),
    "clean_context": (["canonical_cleanc2.jsonl"], ("case_id", "condition"),
                      "canonical clean-context C2; recovered intermediates are superseded"),
    "reveal":        (["canonical_reveal.jsonl"], ("case_id", "condition", "ordering"),
                      "two speaking orders per case"),
    "debate":        (["debate_*.jsonl"],
                      ("case_id", "drug", "ordering", "turn"),
                      "two speaking orders and multiple turns per case; gated to the frozen selection because the acceptance suite writes test cases into the same file",
                      lambda r: r.get("case_id") in CANONICAL),
    "self_consistency": (["selfcon_*.jsonl"], ("case_id",), "five samples collapsed upstream"),
    "cross_model":   (["model_compare_*.jsonl"], ("case_id", "drug", "model"),
                      "same cases across six models"),
    "plausible":     (["plausible_*.jsonl"], ("case_id", "seed_drug", "receiver"),
                      "plausible-but-wrong seed"),
    "track4":        (["track4_*.jsonl"], ("case_id", "seed_drug", "receiver", "condition"),
                      "S+ / S- support arm; seed and receiver are real cells"),
    "fewshot":       (["fewshot_*.jsonl"], ("case_id",),
                      "rung two of the escalation ladder, four worked exemplars per case"),
    "confidence":    (["confidence_*.jsonl"], ("case_id",),
                      "confidence elicited before and after; the binary is degenerate, see confidence_axis.json"),
}


def canonical_cases():
    """The frozen 200-case selection, read from the canonical reveal arm.

    The acceptance suite writes into the same run files as the real arms, on test cases
    that are deliberately outside the frozen selection. Those rows must never enter an
    exposure count, so arms that share a file with the suite are gated on this set.
    """
    cases = set()
    for pat in ("canonical_reveal.jsonl", "canonical_cleanc2.jsonl"):
        for f in glob.glob(os.path.join(RUNS, pat)):
            for line in open(f):
                line = line.strip()
                if line:
                    cid = json.loads(line).get("case_id")
                    if cid:
                        cases.add(cid)
    if not cases:
        raise SystemExit("cannot establish the canonical case set from the reveal arm")
    return cases


CANONICAL = None


def assert_no_orphan_files():
    """A file that belongs to an arm but matches no arm pattern is invisible to every
    number below. That happened once: a date-prefixed glob could not match a file written
    the following day, and 609 rows disappeared from the integrity block while the
    endpoint scripts, which glob differently, still saw them. Fail loudly instead."""
    claimed = set()
    for spec in ARMS.values():
        for pat in spec[0]:
            claimed.update(glob.glob(os.path.join(RUNS, pat)))
    prefixes = {"c1_", "matched_", "calib_", "debate_", "selfcon_", "model_compare_",
                "plausible_", "track4_", "canonical_", "fewshot_", "confidence_"}
    orphans = [p for p in glob.glob(os.path.join(RUNS, "*.jsonl"))
               if p not in claimed
               and any(os.path.basename(p).startswith(x) for x in prefixes)]
    if orphans:
        raise SystemExit("run files match an arm prefix but no arm pattern, so they would be "
                         "silently excluded:\n  " + "\n  ".join(sorted(orphans)))


def truthy(v):
    return v is True or (isinstance(v, str) and v.lower() == "true")


def load(arm):
    spec = ARMS[arm]
    pats, key, note = spec[0], spec[1], spec[2]
    keep = spec[3] if len(spec) > 3 else (lambda r: True)
    files = sorted({p for pat in pats for p in glob.glob(os.path.join(RUNS, pat))})
    rows, seen, dropped, quarantined = [], set(), 0, 0
    for f in files:
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if truthy(r.get("span_quarantine")) or truthy(r.get("gate_quarantine")):
                quarantined += 1
                continue
            if not all(c in r for c in key) or not keep(r):
                continue
            k = tuple(str(r.get(c)) for c in key)
            if k in seen:
                dropped += 1
                continue
            seen.add(k)
            rows.append(r)
    return rows, {"files": [os.path.basename(f) for f in files], "key": list(key),
                  "n": len(rows), "duplicate_writes_dropped": dropped,
                  "gate_quarantined": quarantined, "note": note}


# ---------- statistics ----------
def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return round((c - h) / d * 100, 1), round((c + h) / d * 100, 1)


def mcnemar_exact(b, c):
    """Two sided exact McNemar for genuinely paired binary data."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n))


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def cmh(strata):
    """Cochran-Mantel-Haenszel over 2x2 strata (a,b,c,d)."""
    num = var = or_n = or_d = 0.0
    used = 0
    for a, b, c, d in strata:
        n = a + b + c + d
        r1, r2, c1, c2 = a + b, c + d, a + c, b + d
        if n < 2 or min(r1, r2, c1, c2) == 0:
            continue
        used += 1
        num += a - r1 * c1 / n
        var += r1 * r2 * c1 * c2 / (n * n * (n - 1))
        or_n += a * d / n
        or_d += b * c / n
    if used == 0 or var <= 0:
        return None
    chi2 = (abs(num) - 0.5) ** 2 / var
    return {"strata": used, "chi2": round(chi2, 4),
            "p": round(min(1.0, 2 * norm_sf(math.sqrt(chi2))), 4),
            "or_mh": round(or_n / or_d, 3) if or_d else None}


# ---------- endpoints ----------
def endpoint_c1(res):
    rows, meta = load("C1_pressure")
    rows = [r for r in rows if r["condition"] == "C1_unsupported_pressure"]
    by = defaultdict(lambda: [0, 0])
    per_case = defaultdict(dict)
    for r in rows:
        b = by[r["subtype"]]
        b[1] += 1
        ch = truthy(r["changed"])
        if ch:
            b[0] += 1
        per_case[r["case_id"]][r["subtype"]] = ch
    out = {"_meta": meta, "n_cases": len({r["case_id"] for r in rows}), "by_framing": {}}
    for s in sorted(by):
        k, n = by[s]
        lo, hi = wilson(k, n)
        out["by_framing"][s] = {"changed": k, "n": n, "pct": round(k / n * 100, 1),
                                "ci95": [lo, hi]}
    tk = sum(v[0] for v in by.values())
    tn = sum(v[1] for v in by.values())
    lo, hi = wilson(tk, tn)
    out["pooled"] = {"changed": tk, "n": tn, "pct": round(tk / tn * 100, 1), "ci95": [lo, hi]}
    # pairwise McNemar: same case sees every framing, so this IS paired
    subs = sorted(by)
    out["pairwise_mcnemar"] = {}
    for i in range(len(subs)):
        for j in range(i + 1, len(subs)):
            s1, s2 = subs[i], subs[j]
            b = c = 0
            for cid, d in per_case.items():
                if s1 in d and s2 in d:
                    if d[s1] and not d[s2]:
                        b += 1
                    elif d[s2] and not d[s1]:
                        c += 1
            out["pairwise_mcnemar"][f"{s1} vs {s2}"] = {
                "discordant": [b, c], "p": round(mcnemar_exact(b, c), 4)}
    res["C1_capitulation_under_pressure"] = out


def endpoint_match(res):
    rows, meta = load("D_MATCH_1")
    by = defaultdict(lambda: {"cov": [0, 0], "non": [0, 0]})
    for r in rows:
        h = "cov" if truthy(r["seed_is_adequate"]) else "non"
        cell = by[r["seed_drug"]][h]
        cell[1] += 1
        if truthy(r["adopted_seed"]):
            cell[0] += 1
    out = {"_meta": meta, "by_drug": {}}
    strata, tot = [], {"cov": [0, 0], "non": [0, 0]}
    for d in sorted(by):
        a, i = by[d]["cov"], by[d]["non"]
        rec = {"covers": {"adopted": a[0], "n": a[1]},
               "does_not_cover": {"adopted": i[0], "n": i[1]}}
        if a[1] and i[1]:
            rec["gap_pct"] = round((a[0] / a[1] - i[0] / i[1]) * 100, 1)
            strata.append((a[0], a[1] - a[0], i[0], i[1] - i[0]))
            for h, cc in (("cov", a), ("non", i)):
                tot[h][0] += cc[0]
                tot[h][1] += cc[1]
        else:
            rec["status"] = "incomplete, run still in progress"
        out["by_drug"][d] = rec
    a, i = tot["cov"], tot["non"]
    if a[1] and i[1]:
        out["pooled"] = {
            "covers": {"adopted": a[0], "n": a[1], "pct": round(a[0] / a[1] * 100, 1),
                       "ci95": list(wilson(*a))},
            "does_not_cover": {"adopted": i[0], "n": i[1], "pct": round(i[0] / i[1] * 100, 1),
                               "ci95": list(wilson(*i))},
            "gap_pct": round((a[0] / a[1] - i[0] / i[1]) * 100, 1)}
        out["cmh_stratified_by_drug"] = cmh(strata)
    out["test_note"] = ("Cases are paired on drug only, not on patient covariates, "
                        "so McNemar would overclaim. CMH stratified by drug is the "
                        "test the design supports.")
    res["D_MATCH_1_drug_identity_vs_patient"] = out


def integrity(res):
    audit = {}
    for arm in ARMS:
        _, meta = load(arm)
        audit[arm] = meta
    res["_integrity"] = audit


def merge_primary(res):
    """Fold in the pre-specified primary test so RESULTS.json stays the one file
    every document cites. primary_test.py writes it; this only merges."""
    root = os.path.dirname(HERE)
    cands = [os.path.join(OUT_DIR, "primary_test.json"),
             os.path.join(OUT_DIR, "results", "primary_test.json"),
             os.path.join(root, "results", "primary_test.json"),
             os.path.join(HERE, "primary_test.json")]
    p = next((c for c in cands if os.path.exists(c)), None)
    if p:
        res["pre_specified_primary_test"] = json.load(open(p))
    else:
        res["pre_specified_primary_test"] = {"status": "not yet computed; "
                                             "run analysis/primary_test.py"}


def main():
    global CANONICAL
    CANONICAL = canonical_cases()
    assert_no_orphan_files()
    res = {"generated_by": "canonical_numbers.py",
           "model": "qwen3:4b-instruct-2507-q4_K_M", "temperature": 0, "seed": 20260818}
    integrity(res)
    endpoint_c1(res)
    endpoint_match(res)
    merge_primary(res)
    out = os.path.join(OUT_DIR, "RESULTS.json")
    with open(out, "w") as fh:
        json.dump(res, fh, indent=2, sort_keys=False)

    print("INTEGRITY")
    print("%-20s %7s %7s %9s  %s" % ("arm", "n", "dupes", "gated", "identity key"))
    print("-" * 88)
    for arm, m in res["_integrity"].items():
        flag = "  <-- dropped" if m["duplicate_writes_dropped"] else ""
        print("%-20s %7d %7d %9d  %s%s" % (arm, m["n"], m["duplicate_writes_dropped"],
                                           m["gate_quarantined"], "+".join(m["key"]), flag))

    c1 = res["C1_capitulation_under_pressure"]
    print("\nC1  capitulation under unsupported pressure, %d cases" % c1["n_cases"])
    for s, v in c1["by_framing"].items():
        print("  %-22s %4d/%-4d %6.1f%%  [%.1f, %.1f]" %
              (s, v["changed"], v["n"], v["pct"], v["ci95"][0], v["ci95"][1]))
    p = c1["pooled"]
    print("  %-22s %4d/%-4d %6.1f%%  [%.1f, %.1f]" %
          ("POOLED", p["changed"], p["n"], p["pct"], p["ci95"][0], p["ci95"][1]))

    m = res["D_MATCH_1_drug_identity_vs_patient"]
    print("\nD-MATCH-1  same drug name, different patient")
    for d, v in m["by_drug"].items():
        if "gap_pct" in v:
            print("  %-26s covers %2d/%-3d   does not %2d/%-3d   gap %+.1f" %
                  (d, v["covers"]["adopted"], v["covers"]["n"],
                   v["does_not_cover"]["adopted"], v["does_not_cover"]["n"], v["gap_pct"]))
    if "pooled" in m:
        pp = m["pooled"]
        print("  %-26s covers %5.1f%%   does not %5.1f%%   gap %+.1f" %
              ("POOLED", pp["covers"]["pct"], pp["does_not_cover"]["pct"], pp["gap_pct"]))
        print("  CMH stratified by drug: %s" % m["cmh_stratified_by_drug"])

    print("\nwritten: %s" % out)


if __name__ == "__main__":
    main()
