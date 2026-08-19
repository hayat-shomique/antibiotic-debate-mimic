#!/usr/bin/env python
"""Build the deduped canonical C2 datasets from base + recovered files.

Why this exists: the C2 arms were run twice - once under the defective gate
(D-GATE-2), which silently dropped runs, and once by gate_recovery.py to pick up
what was dropped. Both sets of records are valid model output under the same
model, digest and seed; only the gate decision differed. Pooling them is correct,
but it has to be done in one place, deterministically, with the duplicates
removed, so that no downstream script can pool them a different way.

Dedup key: (case_id, ordering) for the reveal arm, case_id for clean context.
Duplicates arise because a killed process re-ran cases already written. The model
is deterministic at temperature 0 with a fixed seed, so duplicates are identical
on the scored fields; this script asserts that rather than assuming it, and
reports any pair that disagrees instead of silently keeping one.

Raw files are never modified. Output: runs/canonical_cleanc2.jsonl and
runs/canonical_reveal.jsonl, each with a provenance field naming its source file.
"""
from __future__ import annotations
import json, glob, collections
from pathlib import Path

RUNS = Path(__file__).resolve().parent / "runs"
SCORED = {"cleanc2": ["c2_drug", "c2_outcome", "changed", "round0_drug"],
          "reveal":  ["reveal_drug", "reveal_outcome", "final_A", "round0_drug"]}


def load(pattern, source_tag):
    out = []
    for f in sorted(RUNS.glob(pattern)):
        for l in f.read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                r["_source_file"] = f.name
                r["_source_tag"] = source_tag
                out.append(r)
    return out


def canonicalise(arm, base_pat, rec_pat, keyfn, outname):
    base = load(base_pat, "base")
    rec = load(rec_pat, "recovered")
    allr = base + rec
    by = collections.defaultdict(list)
    for r in allr:
        by[keyfn(r)].append(r)

    conflicts, kept = [], []
    for k, v in sorted(by.items(), key=lambda kv: str(kv[0])):
        if len(v) > 1:
            sigs = {tuple(str(x.get(f)) for f in SCORED[arm]) for x in v}
            if len(sigs) > 1:
                conflicts.append((k, sigs))
        kept.append(v[0])                      # first occurrence, base before recovered

    out = RUNS / outname
    with out.open("w") as fh:
        for r in kept:
            fh.write(json.dumps(r, default=str) + "\n")

    dupes = sum(len(v) - 1 for v in by.values())
    print(f"  {arm:9s} base {len(base):4d} + recovered {len(rec):4d} = {len(allr):4d} raw")
    print(f"            {len(kept):4d} unique keys, {dupes} duplicate rows dropped")
    print(f"            {len(conflicts)} keys where duplicates DISAGREE on the scored fields")
    for k, s in conflicts[:5]:
        print(f"              CONFLICT {k}: {s}")
    print(f"            -> {out.name}")
    return len(kept), len(conflicts)


if __name__ == "__main__":
    print("Canonical C2 datasets\n" + "=" * 60)
    n1, c1 = canonicalise("cleanc2", "cleanc2_2*.jsonl", "cleanc2_recovered_*.jsonl",
                          lambda r: r["case_id"], "canonical_cleanc2.jsonl")
    n2, c2 = canonicalise("reveal", "reveal_2*.jsonl", "reveal_recovered_*.jsonl",
                          lambda r: (r["case_id"], r.get("ordering", "-")),
                          "canonical_reveal.jsonl")
    print("=" * 60)
    print(f"  clean context : {n1}/200 cases")
    print(f"  reveal        : {n2}/400 ordering-runs")
    if c1 or c2:
        raise SystemExit("FAIL: duplicate records disagree; do not pool until resolved")
    print("  no conflicts. safe to pool.")
