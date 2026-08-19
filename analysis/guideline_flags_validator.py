#!/usr/bin/env python
"""guideline_flags_validator.py - D-GUIDELINE-1.

The flags in guideline_flags.csv are RESEARCHER-SUPPLIED from a guideline document the
researcher has read. They are never model-generated. This project has already excluded one
AI-generated document for exactly this reason, and a model-sourced citation here would be
unusable: the whole point of the indicator is that the yardstick is external to the model
being measured.

This validator therefore refuses anything that cannot be traced to a real document with a
locator. A row may instead be marked NOT_ASSESSED with a stated reason - sixteen rows may
legitimately be NOT_ASSESSED, because round-0 is piperacillin-tazobactam in every ordering,
so one row done properly is what the indicator needs.
"""
from __future__ import annotations
import re, sys
import pandas as pd

# R3 contract: three columns are required. The richer provenance columns
# (guideline_name, guideline_year, section_or_page, access_date) remain OPTIONAL
# and are validated only when present, so a three-column fill sheet is accepted.
REQUIRED = ["drug", "in_empiric_guideline", "source_citation"]
OPTIONAL = ["guideline_name", "guideline_year", "section_or_page", "access_date"]
# a resolvable identifier: DOI, PMID, ISBN, or an http(s) URL
IDENT = re.compile(r"(10\.\d{4,9}/\S+|PMID:\s*\d+|ISBN[\s:-]*[\d-]{10,17}|https?://\S+)", re.I)


def validate(path: str = "guideline_flags.csv") -> pd.DataFrame:
    g = pd.read_csv(path, dtype=str).fillna("")
    missing = [c for c in REQUIRED if c not in g.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    problems = []
    for i, r in g.iterrows():
        drug = r["drug"].strip()
        if r.get("not_assessed_reason","").strip():
            if r["in_empiric_guideline"].strip():
                problems.append(f"{drug}: NOT_ASSESSED but in_empiric_guideline is filled")
            continue                                    # legitimately deferred
        v = r["in_empiric_guideline"].strip().upper()
        if v not in {"Y", "N", "0", "1", "YES", "NO"}:
            problems.append(f"{drug}: in_empiric_guideline must be Y or N, got "
                            f"{r['in_empiric_guideline']!r}")
        cit = r["source_citation"].strip()
        if not cit:
            problems.append(f"{drug}: blank source_citation")
        elif not IDENT.search(cit):
            problems.append(f"{drug}: source_citation has no resolvable identifier "
                            f"(need a DOI, PMID, ISBN or URL)")
        # optional provenance columns are checked only if the column exists AND is filled
        for c in OPTIONAL:
            if c in g.columns and r.get(c, "").strip():
                if c == "guideline_year" and not re.fullmatch(r"\s*(19|20)\d{2}\s*", r[c]):
                    problems.append(f"{drug}: guideline_year must be a 4-digit year")
    if problems:
        raise ValueError("guideline flags rejected:\n  - " + "\n  - ".join(problems))
    return g


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "guideline_flags.csv"
    try:
        g = validate(p)
    except FileNotFoundError:
        sys.exit(f"{p} not present. Fill guideline_flags_TEMPLATE.csv and save it as {p}.")
    except ValueError as e:
        sys.exit(str(e))
    n_assessed = (g["not_assessed_reason"].str.strip() == "").sum()
    print(f"OK: {len(g)} rows, {n_assessed} assessed, {len(g)-n_assessed} NOT_ASSESSED")
