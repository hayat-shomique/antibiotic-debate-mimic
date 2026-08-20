# Limitations

Stated as properties of the design rather than as apology.

## Clinical

**Inducible AmpC is unhandled, and it bounds the adequacy labels rather than the harm finding.**
{AMPC_ANY} of the {AMPC_N} specimens, {AMPC_ANY_PCT}%, grew an organism capable of AmpC
de-repression, in which an isolate reported susceptible to a third-generation cephalosporin may
become resistant during treatment. The published induction risk is not uniform across those
organisms. It is best established for *Enterobacter cloacae*, which is {AMPC_BEST} of the
{AMPC_N}, {AMPC_BEST_PCT}%; for the remaining {AMPC_WEAK}, chiefly *Serratia marcescens*, the
primer this rests on states that the likelihood of induction is less clear. The intrinsic
resistance table carries no entry for any of them, so a recommendation scored adequate against
the reported panel could still fail clinically. {AMPC_ATRISK} of the {AMPC_RUNS} ordering-runs
end on a third-generation cephalosporin against an AmpC-capable organism and are scored adequate;
those are the labels this limitation says to distrust.

It bites much less on the harm finding than on the adequacy labels, and the reason is which drug
the debate lands on. Of the {AMPC_HARM_N} harmful revisions, {AMPC_HARM_3GC} is onto a
third-generation cephalosporin against an AmpC-capable organism. {AMPC_HARM_FEP} are onto
cefepime, which current guidance recommends for AmpC producers at a minimum inhibitory
concentration of 2 or below, so AmpC does not make those revisions worse than the panel already
records. Correcting the scorer requires organism-specific rules that are beyond the scope of this
internship. The direction of the residual bias is fixed and it is the safe direction: if AmpC
de-represses on therapy, the reported adequacy overstates true adequacy, so the harm this study
reports is an underestimate rather than an overestimate.

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


**Answer-space asymmetry, stated.** 51.8% of the clinician regimens in this cohort are multi-agent (86 of the 166 cases that have a regimen at all; 43.0% if you divide by all 200 cases, which understates it), while the model is required to name exactly one drug. The comparison is therefore between different answer spaces, which is part of why the clinician scores UNDETERMINED so often on the full cohort. The determined-only figures are the only ones worth quoting, and even those compare a single-agent recommendation against what is frequently a combination.

## What tonight's analysis added, stated plainly

**The baseline is a constant, and that bounds what can be claimed.** The model recommends
piperacillin-tazobactam for every patient before any conversation. Nothing in the prompt predicts
the organism: the case block carries age, sex, admission type, admission source, hours since
admission and a prior-exposure flag, and no laboratory data. A single broad empiric agent is a
defensible policy under that much uncertainty, and it scores 87.5 percent coverage. But it means
this study cannot separate a model that reasons well about patients from a model that has one good
default, because at baseline there is no variation to explain.

**The pre-specified primary test runs on 180 to 185 of 200 cases, depending on the framing.** Every case
in the frozen selection now carries a row in every condition, so nothing is missing because an arm
stopped early. What drops is 15 to 20 cases per framing where a condition returns UNDETERMINED, which
happens when the recommended agent was never tested against at least one isolate on that patient's
panel. That is a property of what the laboratory chose to test, not of the model, and it is still
attrition. See `PROJECT.md` section 7.2.

**No practising clinician has reviewed this design.** The personas, the seventeen-drug formulary
and the adequacy rule come from the supervisor and from published guidance, not from a treating
infectious-disease physician or clinical microbiologist. The stewardship interpretation in
particular, that escalating to a carbapenem without evidence is harmful, is standard in the
literature but has not been checked against a clinician's judgement on these specific cases.

**The stewardship finding is a difference in prescribing behaviour, not a demonstrated patient
harm.** Carbapenem overuse drives carbapenem-resistant Enterobacterales at population level. This
study shows the model escalating; it does not and cannot show a resulting resistance outcome in
these patients.

**Sycophancy is measured against a scripted counterpart, not a second live agent.** The pressure
conditions use fixed challenge sentences so that the stimulus is identical across cases. That buys
internal validity and gives up realism: a real second agent would vary its argument with the case.

**Observational data.** Following the supervisor's own caveat, everything here is phrased as
alignment with observed microbiological outcomes or counterfactual appropriateness of the
recommendation. Nothing here claims a recommendation caused a patient outcome.
