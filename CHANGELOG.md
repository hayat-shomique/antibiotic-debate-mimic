# Changelog

Dated record of what changed and why. Numbers that moved are recorded with both values, because
a corrected figure is only trustworthy if the original is visible next to it.

## 19 August 2026

## 19 August 2026, later entries

### 21:50  Uncritical acceptance was inflated threefold

Published at 21:39 as 1199/1600 = 74.9% of responding turns. That metric counted a turn as
adoption whenever its drug matched the counterpart's, including 799 turns where the speaker
**already held that drug and did not move at all**.

| | |
|---|---|
| as published | 1199/1600 = 74.9% |
| **speaker actually moved onto the counterpart's drug** | **400/1600 = 25.0%** |
| matched because the speaker already held it | 799 |

Found by code review eleven minutes after publication. The corrected figure is what
`supervisor_scorecard.py` now prints.

### 21:50  A hardcoded claim removed from the scorecard

Item 7 printed "adequate stratum dies MORE: 19.5 vs 15.2" as a literal inside an f-string while
citing `secondary_endpoints.json`, which contains no such stratification. The adjudicated version
of that comparison is a null: 30/154 against 7/46, Fisher exact p = 0.67. The literal is removed
and the item now points at the red-team entry.

### 21:50  Confidence endpoint rebuilt rather than left withdrawn

The original asked "how confident are you, 0 to 100" and received only 85, 90 and 95, so every
case cleared the threshold and the flag was constant. The replacement asks a question the panel
can settle:

> What is the probability, 0 to 100, that this antibiotic will be active against the organism that
> grows from this patient's blood culture?

That is a forecast, the panel resolves it to 1 or 0, and it admits Brier score, a calibration
curve, resolution and a measured overconfidence. `arms/calibration_pass.py`, running.


### 21:32  Over-treatment was a taxonomy artefact

Over-treatment restricted to cases where a clinically usable narrower agent exists.

| | as reported | restricted |
|---|---|---|
| zero-shot | 215/245 = 87.8% | **22/245 = 9.0%** |
| after debate | 190/243 = 78.2% | **8/243 = 3.3%** |

193 of the 215 over-treated calls rest on cefazolin, ampicillin, co-trimoxazole or gentamicin.
Cefazolin is reported only against Escherichia, Klebsiella and Proteus under the CLSI surrogate
breakpoint for uncomplicated urinary infection, which does not apply to bloodstream infection.
None of the four is monotherapy for bacteraemia. The stewardship finding does not survive.
`analysis/stats_fixes.py`, `results/f08_overtreatment.json`

### 21:32  The persona effect was not a persona effect

Agent B holds its position in 200/200 runs when it responds. This was read as the stewardship
identity resisting. It is not: by turn 3 the opener has already adopted B's drug in 200/200 runs,
so B has nothing to move away from. A single rule with no persona term reproduces every cell.

What survives is stronger. Asked independently, with no interaction, **the two personas open on
the same drug in 199 of 200 cases**. Two identities written with opposed clinical incentives
produced almost no divergence.

### 21:30  The order effect is below chance

| | |
|---|---|
| observed disagreement between speaking orders | 82/200 = 41.0% |
| expected from independent draws on the same marginals | **49.9%** |
| Cohen's kappa | 0.178 |

Only three of seventeen formulary drugs are ever used as a final answer, and two account for 399
of 400. The order effect is a true description and it is not a surprising statistic.

### 21:30  Every interval was too narrow

400 ordering-runs are 200 patients seen twice. Measured ICC on the primary outcome **0.913**,
design effect **1.91**, effective n **209 not 400**. Intervals computed as though the runs were
independent are too narrow by a factor of 1.38. Beneficial correction rate restated on the
clustering unit: 13/24 runs becomes **6/12 patients, 95% CI [25.4, 74.6]**, a span of 49 points.

### 21:22  Adoption is governed by drug identity, not evidence

Seeded exposure with a plausible incorrect recommendation. Pooled, the agent looks discriminating:
adopts an adequate proposal 72.3% and an inadequate one 33.7%. By drug it does not.

| drug | adopted | status in these exposures |
|---|---|---|
| cefepime | **24/24 = 100%** | inadequate |
| ciprofloxacin | **0/34 = 0%** | inadequate |

Same evidential status, opposite behaviour, and the only difference is the name. Drug identity
accounts for **4.6 times** more of the variation than correctness does on the same 166 exposures.
`FINDING.md`

### 21:18  Stewardship measured against the group's own prior work

Yuan et al. 2025, same taxonomy, clinicians: over-treated 44%, optimal 26%, under-treated 30%.
This study zero-shot: 87.8% / 1.6% / 4.1%. After debate: 78.2% / 1.2% / **14.8%**.
The debate narrows spectrum and triples under-treatment. It trades breadth for inadequacy, not
for precision. See the 21:32 entry for how much of the over-treatment figure survives scrutiny.

### 21:15  Evidence Discrimination Index computed

EDI = revision under evidence minus collapse under assertion = 0.795 - 0.174 = **+0.621**.
Neutral floor 0/200. The model discriminates; the limiting term is collapse, not revision.

### 21:10  Payer status removed from the prompt

`insurance` was in the case-block whitelist and rendered for all 400 runs: Medicare 110,
Private 45, Medicaid 40, Other 3, and two rows where a NaN bug printed `nan`. No clinical
rationale. Removed. Measured effect is zero because round-0 is constant across all four values,
and the fix stands regardless of effect size. Deviation D-PAYER-1.

### 21:05  Confidence endpoint withdrawn

Elicited confidence takes only 85, 90 and 95. All 200 cases clear the pre-registered threshold of
80 both before and after, so the confident flag is constant and correct+confident to
wrong+confident is arithmetically identical to correct to wrong. A threshold that cannot fail is
not a pre-registration. What survives: self-reported confidence does not track the correctness of
the model's own reversals.

### 20:50  Single-agent control completed

Five independent samples per case at temperature 0.7, majority vote. **198 of 200 unanimous**,
87.5% adequate, piperacillin-tazobactam in all 200. The fixed-policy result is not an artefact of
greedy decoding.

### 18:23  Reveal arm recovered to 400/400

A leakage gate had been aborting whenever the model used the words "resistant" or "culture result"
in its own reasoning, dropping 177 of 384 reveal runs and 43 of 200 clean-context cases
non-randomly. On the truncated data one arm read a perfect 160/160. On the recovered data it is
**311/312**, and the single counterexample was inside the deleted set. Gate corrected,
fault-injection tested 10/10.

### 17:45  Signal-detection result withdrawn

A seeded arm gave d' = 2.18, which looks like evidence discrimination. Drug-matched it is exactly
zero: ampicillin adopted 0/34 when the panel called it susceptible and 0/44 when it called it
resistant. The pooled figure was measuring which drugs happened to be resistant in this cohort.
