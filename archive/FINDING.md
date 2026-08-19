# The finding

## What the agent is actually responding to

Two accounts can explain why an agent adopts its counterpart's antibiotic.

**Evidence account.** Adoption depends on whether the proposed drug covers the organism.
**Identity account.** Adoption depends on which drug is named, independent of coverage.

They make different predictions, and a seeded-exposure design separates them. The counterpart is
scripted to propose a broad-spectrum drug that the laboratory panel calls either susceptible or
resistant for that patient. Only the drug name changes; the sentence structure, the clinical
rationale and the system prompt are held constant.

### Pooled, it looks like discrimination

| counterpart proposed | adopted |
|---|---|
| a drug the panel calls adequate | 60/83 = 72.3% |
| a drug the panel calls inadequate | 28/83 = 33.7% |

A 38.6 point gap. Read alone, this says the agent weighs the evidence.

### By drug, it is not

| drug proposed | adopted | evidential status in these exposures |
|---|---|---|
| cefepime | **24/24 = 100.0%** | inadequate |
| meropenem | 60/83 = 72.3% | adequate |
| ceftriaxone | 3/6 = 50.0% | inadequate |
| piperacillin-tazobactam | 1/7 = 14.3% | inadequate |
| ciprofloxacin | **0/34 = 0.0%** | inadequate |
| ceftazidime | 0/12 = 0.0% | inadequate |

**The decisive pair.** Cefepime and ciprofloxacin are both broad-spectrum, and in these exposures
both are inadequate against the organism. The agent adopts cefepime in **24 of 24** cases and
ciprofloxacin in **0 of 34**. Same evidential status, opposite behaviour, and the only difference
is the name.

### Which account fits

Fitting adoption as a function of correctness alone, and separately as a function of drug identity
alone, on the same 166 exposures:

| model | log-likelihood | gain over a single overall rate |
|---|---|---|
| null, one rate | -114.8 | - |
| correctness only, 2 groups | -102.0 | 12.7 |
| **drug identity only, 6 groups** | **-56.0** | **58.7** |

**Drug identity accounts for 4.6 times more of the variation than correctness does.** The pooled
38.6 point gap is not evidence sensitivity. It is a consequence of which drugs happened to fall in
which arm.

## Why this matters

The agent has a **stable ordering over drug names** that governs whether it accepts a colleague's
recommendation, and that ordering is largely independent of whether the recommendation is right for
the patient in front of it. It is not persuaded by an argument and it is not checking the evidence.
It is recognising a name.

This reframes the whole capitulation result. The earlier finding, that the agent adopts the
counterpart's drug in 400 of 400 debate runs, is not a general willingness to defer. It is what
happens when the counterpart proposes something the prior already accepts. Propose ciprofloxacin
instead and the agent refuses 34 times out of 34.

## What this does that the pressure literature cannot

Med-Stress (arXiv:2605.23932) and MedPRESS (arXiv:2608.02520) both build escalating pressure
taxonomies for clinical dialogue and both score against annotator-assigned labels. With that
design you can establish **that** a model capitulated. You cannot establish **what it capitulated
to**, because the correct answer is fixed by a human and the same for every case.

Here the correct answer is a per-patient laboratory result, so the same drug can be adequate for
one patient and inadequate for another. That is what makes the two accounts separable, and it is
what turns "the model is sycophantic" into a statement about a specific, measurable prior.

## What follows, and it is testable

If adoption is governed by a name-level prior rather than by evidence, then:

1. **The prior should be measurable directly.** Ask the model to rank the formulary with no patient
   attached. If that ranking predicts adoption better than coverage does, the account is confirmed
   independently of the debate.
2. **It should be shiftable by prompting.** Stating the local antibiogram, or naming the
   organism's likely class, should move adoption for drugs whose position in the ordering is not
   clinically justified. If it does not move, the prior is deeper than the prompt.
3. **It predicts which errors are dangerous.** Errors will concentrate on high-prior drugs that
   happen to be inadequate, and cefepime is the worst case in this cohort: adopted every time,
   inadequate every time it was offered.

## Caveats, stated first

This is a partial run: 166 of a planned 312 exposures. The drug groups are unbalanced because the
design draws the seed from what the panel makes available, so no drug appears in both arms and the
within-drug contrast is not yet available. The log-likelihood comparison is descriptive, not a
formal model selection, and the two models are not nested in a way that licenses a test. The result
is scoped to one 4B checkpoint.

The strongest version of this experiment holds the drug fixed and varies only the patient, using
matched case pairs where the same drug is adequate for one and inadequate for the other. That is
buildable from this cohort and it is the next run.

`analysis/drug_prior.py`, `analysis/plausible_pass.py`
