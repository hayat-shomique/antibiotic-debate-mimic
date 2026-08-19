# Limitations

Stated as properties of the design rather than as apology.

## Clinical

**Inducible AmpC is unhandled.** Roughly 18% of this cohort are organisms capable of AmpC
de-repression, in which an isolate reported susceptible to a third-generation cephalosporin may
become resistant during treatment. The intrinsic-resistance table carries no entry for this, so a
recommendation scored adequate against the reported panel could still fail clinically. Correcting
it requires organism-specific rules that are beyond the scope of this internship, and the
limitation bounds every adequacy figure in the study.

**Combination therapy is not modelled.** The model is forced to name exactly one agent while 43%
of the clinician regimens in this cohort are multi-agent. The clinician comparison is therefore
between different answer spaces and is reported on the determined-only denominator for that
reason.

**Spectrum adjudication is retrospective.** Over-treatment is judged against a panel that did not
exist at the decision point, so the label measures hindsight rather than empiric judgement.

## Statistical

**Clustering.** 400 ordering-runs are 200 patients seen twice. Measured ICC on the primary outcome
is **0.913**, design effect **1.91**, effective n **209 not 400**. Any interval computed as though
the runs were independent is too narrow by a factor of 1.38.

**The order effect is not above chance.** Observed disagreement between the two speaking orders is
82/200 = 41.0%. Expected disagreement from independent draws on the same marginals is **49.9%**,
and Cohen's kappa is 0.178. Only three of seventeen formulary drugs are ever used as a final
answer, and two of them account for 399 of 400. The order effect is real as a description and it
is not surprising as a statistic.

**Beneficial correction rate is on the wrong unit.** 13/24 runs is 6/12 patients. The
patient-level interval is [25.4, 74.6], a span of 49 points. Directional only.

**No multiplicity correction.** Fourteen declared endpoints across twenty run files, all drawn
from the same 200 cases. One endpoint is primary, susceptibility concordance of the final
recommendation per agent. Everything else is exploratory, and that position is declared rather
than corrected for.

## Scope

One 4B open-weight checkpoint is the subject and a second is a robustness check. Findings are
scoped to those checkpoints and are not claims about language models generally.

MIMIC-IV is observational. Every result is alignment with recorded microbiology or counterfactual
appropriateness of a recommendation, never evidence that a recommendation changed an outcome.

Every case was selected on having an interpretable susceptibility panel, which enriches for
organisms that receive full panels. Published comparators report microbiology-evaluable rates
near 32%; this cohort is 100% by construction, which is a declared post-baseline selection.


**Answer-space asymmetry, stated.** 43% of the clinician regimens in this cohort are multi-agent, while the model is required to name exactly one drug. The comparison is therefore between different answer spaces, which is part of why the clinician scores UNDETERMINED so often on the full cohort. The determined-only figures are the only ones worth quoting, and even those compare a single-agent recommendation against what is frequently a combination.
