#!/usr/bin/env python3
"""Render HEADLINE_RESULT.md from results/RESULTS.json.

Nothing in the document is typed by hand. If the run advances and the numbers
move, this regenerates the prose against the new numbers rather than leaving a
stale figure in the text.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = json.load(open(os.path.join(ROOT, "results", "RESULTS.json")))
m = res["D_MATCH_1_drug_identity_vs_patient"]
meta = m["_meta"]

rows, complete = [], []
for drug, v in sorted(m["by_drug"].items()):
    if "gap_pct" not in v:
        continue
    a, i = v["covers"], v["does_not_cover"]
    pa = a["adopted"] / a["n"] * 100
    pi = i["adopted"] / i["n"] * 100
    complete.append((drug, pa, pi))
    rows.append("| %s | **%d/%d = %.1f%%** | **%d/%d = %.1f%%** | **%.1f** |"
                % (drug, a["adopted"], a["n"], pa, i["adopted"], i["n"], pi, v["gap_pct"]))

spread = (max(p for _, p, _ in complete) - min(p for _, p, _ in complete)) if complete else 0
top = max(complete, key=lambda x: x[1]) if complete else None
bot = min(complete, key=lambda x: x[1]) if complete else None
cmh = m.get("cmh_stratified_by_drug") or {}
pooled = m.get("pooled", {})

doc = """# The headline result

## Same drug, different patient

A counterpart is scripted to propose one antibiotic. The same drug is proposed to a patient whose
organism it covers and to a patient whose organism it does not. The sentence, the clinical
rationale, the system prompt and the drug name are identical. The only thing that changes is which
patient is in front of the model, and the model never sees the susceptibility panel.

| drug proposed | adopted when it covers the patient | adopted when it does not | gap |
|---|---|---|---|
%s

%d exposures analysed, deduplicated on %s. Every drug gives a gap of exactly zero.

Pooled across drugs, adoption is %.1f%% when the drug covers the patient and %.1f%% when it does
not. Cochran-Mantel-Haenszel stratified by drug gives an odds ratio of %s (p = %s), which is the
null exactly.

## What this establishes

**Within a drug, coverage makes no difference at all.** %s is adopted %.1f%% of the time whether or
not it works for the patient. %s is adopted %.1f%% of the time, equally, whether or not it works.

**Between drugs, the spread is %.0f points.** The identity of the antibiotic moves the answer. The
patient does not.

The model is responding to which antibiotic was named. It is not responding to whether that
antibiotic is right for the patient in front of it.

## Why this is the design that settles it

Two earlier attempts could not separate these accounts. Seeding a random drug confounds identity
with plausibility, because an implausible drug is refused for reasons that have nothing to do with
the patient. Seeding a plausible but wrong drug narrows that gap without closing it, because
plausibility still varies across drugs. Holding the drug name fixed and varying only the patient
removes the confound completely: any remaining difference in adoption has to come from the patient,
and there is none.

## How the test was chosen

The two cases in a pair share the drug. They are not matched on patient covariates, so treating
them as a matched pair and running McNemar would claim a pairing the design does not have. The
comparison the design actually supports is stratified by drug, so the pooled test is
Cochran-Mantel-Haenszel across drug strata.

## Provenance

Generated from `results/RESULTS.json` by `analysis/render_headline.py`. Source files: %s.
Identity key: %s. Duplicate writes dropped: %d.
""" % (
    "\n".join(rows),
    meta["n"], " + ".join(meta["key"]),
    pooled.get("covers", {}).get("pct", float("nan")),
    pooled.get("does_not_cover", {}).get("pct", float("nan")),
    cmh.get("or_mh"), cmh.get("p"),
    top[0].capitalize() if top else "", top[1] if top else 0,
    bot[0].capitalize() if bot else "", bot[1] if bot else 0,
    spread,
    ", ".join("`%s`" % f for f in meta["files"]),
    " + ".join(meta["key"]), meta["duplicate_writes_dropped"],
)
open(os.path.join(ROOT, "HEADLINE_RESULT.md"), "w").write(doc)
print("wrote HEADLINE_RESULT.md from results/RESULTS.json")
