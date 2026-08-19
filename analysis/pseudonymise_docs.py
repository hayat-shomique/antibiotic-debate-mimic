#!/usr/bin/env python
"""Replace raw MIMIC case identifiers in prose documents with study pseudonyms.

Why this is necessary: case_id is not a pseudonym. It is literally
    subject_id + "_" + micro_specimen_id
so any document quoting a case_id republishes two credentialed PhysioNet
identifiers in plain text, whether or not it has a column called subject_id.
Prose documents are the highest risk precisely because they look harmless and
get forwarded.

The mapping is deterministic (sorted order over the frozen 200-case cohort), so
C047 means the same case in every document and across rebuilds. The mapping file
itself is patient-level data and never ships - it is written to data/ and listed
in .gitignore.

Run files under runs/ are NOT touched. They are the raw record and stay intact;
they simply never leave the machine.
"""
from __future__ import annotations
import json, re, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAT = re.compile(r"\b1[0-9]{7}_[0-9]{5,8}\b")
MAPFILE = ROOT / "case_pseudonym_map.json"

DOCS = ["NUMBERS_BLOCK.md", "SLIDE_PLAN.md", "VERIFY_FINDINGS.md", "spectrum_results.md",
        "model_pilot_results.md", "c1_smoke_test.md", "MIGRATION_PLAN.md",
        "EXPLAINABILITY.md", "PAPERS_INTEGRATION.md", "LITERATURE.md",
        "MASTER_BACKLOG.md", "thursday_deck.md", "summary_for_tingting.md",
        "EXPLAIN.md", "positioning.md", "framing_ruling.md", "audit_report.md"]


def build_map() -> dict:
    """Deterministic: every case in the frozen cohort, sorted, numbered C001..Cnnn."""
    if MAPFILE.exists():
        return json.loads(MAPFILE.read_text())
    ids = set()
    for f in glob.glob(str(ROOT / "runs" / "*.jsonl")):
        for l in open(f):
            if l.strip():
                c = json.loads(l).get("case_id")
                if c and PAT.fullmatch(str(c)):
                    ids.add(c)
    m = {cid: f"C{i:03d}" for i, cid in enumerate(sorted(ids), 1)}
    MAPFILE.write_text(json.dumps(m, indent=2))
    return m


def main():
    m = build_map()
    print(f"  mapping covers {len(m)} cases -> C001..C{len(m):03d}")
    print(f"  map written to {MAPFILE.name} (patient-level; must never ship)\n")

    total = 0
    for name in DOCS:
        p = ROOT / name
        if not p.exists():
            continue
        s = p.read_text()
        found = set(PAT.findall(s))
        if not found:
            continue
        unmapped = [f for f in found if f not in m]
        for cid, pseudo in m.items():
            s = s.replace(cid, pseudo)
        # anything still matching was not in the cohort - redact rather than leave it
        leftover = set(PAT.findall(s))
        for x in leftover:
            s = s.replace(x, "[case identifier redacted]")
        p.write_text(s)
        total += len(found)
        note = f"  {name:26s} {len(found):3d} identifiers replaced"
        if unmapped:
            note += f"  ({len(unmapped)} not in cohort -> redacted)"
        print(note)

    print(f"\n  {total} identifier occurrences removed from prose")
    remaining = [f for f in DOCS if (ROOT / f).exists() and PAT.search((ROOT / f).read_text())]
    print("  documents still carrying an identifier:", remaining or "none")


if __name__ == "__main__":
    main()
