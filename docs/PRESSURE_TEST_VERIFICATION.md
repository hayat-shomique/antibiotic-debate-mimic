# Independent verification of the two novelty-threatening citations

The literature pressure test returned two papers that, if real, would narrow this project's
novelty claim. Both were checked here directly rather than taken on the search agent's word.
Recorded because a claim that changes what goes on a slide has to be checked by the person
whose name is on the slide.

## 1. Antonie et al. — REAL, and genuine prior art

According to PubMed: Antonie NI, Ionescu VA, Gheorghe G, Tiucă LC, Diaconu CC.
"Large Language Model Recommendations for Empiric Antibiotics Versus Clinician Prescribing:
A Non-Interventional Paired Retrospective Antimicrobial Stewardship Analysis."
*Antibiotics* 2026;15(4). PMID 42041331, PMC13113701,
doi [10.3390/antibiotics15040368](https://doi.org/10.3390/antibiotics15040368).

**Confirmed in the full text** (retrieved from PMC and searched directly):

| claim | status |
|---|---|
| microbiology-evaluable paired subset N = 158 | CONFIRMED — "the microbiology-evaluable paired subset included 158 admissions" |
| 335/493 not eligible for microbiological evaluation | CONFIRMED, verbatim |
| matched OR 2.24 | CONFIRMED (8 occurrences) |
| exact McNemar p = 0.0351 | CONFIRMED (2 occurrences) |
| active coverage against the index organism differed between arms | CONFIRMED |

**NOT confirmed — do not cite these figures.** The search agent reported per-arm counts of
"110/158 = 69.6% LLM vs 97/158 = 61.4% clinician". The strings `110`, `69.6` and `61.4` appear
**zero times** in the full text. Those numbers were not in the paper.

**What it does and does not take from us.** It is single-centre (Clinical Emergency Hospital of
Bucharest, 2020–2024), single-pass, one model via the OpenAI API, compared against clinician
regimens. It contains **no** mention of MIMIC (0 occurrences). There is no debate, no second
agent, no revision step, and no before/after transition analysis.

So: "a susceptibility panel used as the arbiter for an LLM antibiotic recommendation" is **no
longer novel** and must be cited, not claimed. "Susceptibility arbitration inside a two-agent
debate, with a measured revision step" is untouched by this paper.

**The sharper problem it creates, which is not about novelty at all.** Antonie's cohort was
32.0% microbiology-evaluable (158 of 493). This project reports 200/200 = 100%. That gap is the
first thing a referee will ask about, and the honest answer is that this cohort was *selected*
on having an interpretable panel. That is a post-baseline selection which enriches for organisms
that get full panels run — the same lab-triage effect already measured here (6/6,391 Gram-positive
cases have piperacillin-tazobactam tested against 4,549/4,840 Gram-negative). It must be stated
in Methods as a selection effect, with the counts.

## 2. Liu et al. — REAL, but not an LLM study, and the key figure is unverified

"Patient-specific antibiotic susceptibility ranking for empirical treatment of gram-negative
bloodstream infection: a retrospective clinical decision-support and transportability study."
Research Square, doi [10.21203/rs.3.rs-9854692/v1](https://doi.org/10.21203/rs.3.rs-9854692/v1).

**Confirmed:** the preprint exists; it uses MIMIC-IV adult hospital-acquired gram-negative
bloodstream infection; **1,004 episodes from 962 patients**; drug-specific models for
piperacillin-tazobactam, cefepime and meropenem with ciprofloxacin and gentamicin secondary.

**Important qualification the pressure test did not make:** these are logistic regression and
gradient-boosted tree models. It is **not** an LLM study.

**Unverified:** the "meropenem-for-all covered 93.2% (179/192)" and "Top-1 91.1% (175/192)"
figures. The Research Square page returns HTTP 403 and the abstract retrieved through search does
not contain them. **Do not cite those numbers until the PDF has been read.** The qualitative
point — that a constant broad-spectrum policy is a strong comparator on MIMIC-IV gram-negative
bloodstream infection — is independently supported by this project's own measurement (constant
meropenem 192/200 = 96.0%) and does not depend on Liu's figure.

## Standing rule this produced

A citation returned by a search agent is a lead, not a source. Before any number from it reaches
a slide, a document or a supervisor: resolve the identifier, retrieve the text, and search the
text for the exact figure. Two of the seven specific numbers checked here were not in the paper
they were attributed to.
