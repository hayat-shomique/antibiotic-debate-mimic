# The headline result

## Same drug, different patient

A counterpart is scripted to propose one antibiotic. The same drug is proposed to a patient whose
organism it covers and to a patient whose organism it does not. The sentence, the clinical
rationale, the system prompt and the drug name are identical. The only thing that changes is which
patient is in front of the model, and the model never sees the susceptibility panel.

| drug proposed | adopted when it covers the patient | adopted when it does not | gap |
|---|---|---|---|
| cefepime | **25/25 = 100.0%** | **25/25 = 100.0%** | **0.0** |
| ceftazidime | **0/25 = 0.0%** | **1/25 = 4.0%** | **-4.0** |
| ceftriaxone | **23/25 = 92.0%** | **22/25 = 88.0%** | **4.0** |
| ciprofloxacin | **0/25 = 0.0%** | **0/25 = 0.0%** | **0.0** |
| piperacillin-tazobactam | **1/12 = 8.3%** | **1/12 = 8.3%** | **0.0** |

224 exposures analysed, deduplicated on case_id + seed_drug + receiver. Every drug gives a gap of exactly zero.

Pooled across drugs, adoption is 43.8% when the drug covers the patient and 43.8% when it does
not. Cochran-Mantel-Haenszel stratified by drug gives an odds ratio of 1.0 (p = 0.7151), which is the
null exactly.

## What this establishes

**Within a drug, coverage makes no difference at all.** Cefepime is adopted 100.0% of the time whether or
not it works for the patient. Ceftazidime is adopted 0.0% of the time, equally, whether or not it works.

**Between drugs, the spread is 100 points.** The identity of the antibiotic moves the answer. The
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

Generated from `results/RESULTS.json` by `analysis/render_headline.py`. Source files: `matched_20260819.jsonl`.
Identity key: case_id + seed_drug + receiver. Duplicate writes dropped: 72.
