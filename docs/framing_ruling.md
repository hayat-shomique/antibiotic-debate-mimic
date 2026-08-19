# Framing ruling — supersedes all earlier wording

Updated 19 August 2026 under ORDERS_1 PATCH v2 (panel-reviewed). Where anything else in
this project uses different wording, this file wins.

## V1 — RETIRED. Do not use these anywhere.

**The 72.9-point subtraction.** It differenced a debate-arm movement rate against a C2
movement rate. The two arms have different denominators, different antecedent positions
and different populations, so the subtraction is not a quantity. Withdrawn.

**"Inverted" as a cross-arm arithmetic claim.** Same defect. The model was described as
responding to pressure more than to evidence on the strength of that subtraction. Once C2
is stratified the claim does not hold: given the panel the model holds when it is already
right and switches when it is wrong.

**"Evidence-free" as the label for the challenge.** It overclaims. The challenger does make
an argument — spectrum reasoning, resistance risk — it simply carries no information about
this patient.

**"Sycophancy" in any headline claim.** Retained only when citing prior work whose own
construct uses it, or quoting a supervisor verbatim.

## The approved vocabulary

**Case-uninformative counter-argument.** The challenge the debate arm applies. An argument
is present; case-specific information is not.

**Fixed round-0 policy.** The opening recommendation does not vary with the patient and is
verdict-identical to a fixed single-drug policy.

**Positional deference.** Agent A adopts the counterpart's standing drug whether or not that
drug is panel-active. Established as dispositional rather than instructed by D-ABL-1:
adoption 60/60 with the instruction clause and 60/60 without it.

**Dialogue saturates at turn 3.** The final position equals the turn-3 position in every run.

## V4 — the Cn caveat, to be stated wherever Cn appears

Cn returned 0 of 200. Under greedy decoding on near-identical context that is the expected
result, not a surprising one. Cn **excludes the re-prompt artefact** — it shows the model
does not move merely because it was asked a second time. It **does not demonstrate
robustness**, and must not be presented as though it does.

## V6 — the scope sentence, attached to every claim

Every result here is one 4B checkpoint (`qwen3:4b-instruct-2507-q4_K_M`, digest
`0edcdef3…`), one prompt template, one seed (20260818), on admission-linked Enterobacterales
bacteraemia without sustained prior therapy — 12.7% of the frozen cohort. The round-0 policy
is fixed and case-invariant, and that must be stated rather than implied.

The finding is therefore: **a default-policy model steered by dialogue form.** Whether it
generalises is what the model-replication track tests, and until that reports the claim is
about this checkpoint under this template.

## V9 — final vocabulary

**"Applies explicitly provided susceptibility results"** replaces "evidence-competent".
The model is handed the answer sheet; applying it is not the same as weighing evidence.

**"Not attributable to the consideration-clause instruction"** replaces "dispositional".
D-ABL-1 shows the deference survives removing the clause; it does not establish a disposition.

**C2 is a results-application check**, not evidence-weighing.

**Residual failures with the answer sheet get their own line.** In the post-debate arm,
6 of 39 runs entering the reveal on an inadequate drug did not reach adequate even with the
panel in front of them.

## V5 — challenge content is graded, not binary

Movement scales with what the challenge contains: nothing 0/200 = 0.0%, bare disagreement
34/60 = 56.7%, reasoned persona challenge 60/60 = 100.0%. Paired, one-directional
discordance, McNemar exact p = 3.0e-8. Do not describe this as pure social pressure.
Adequacy is 91.7% after bare and 85.0% after reasoned: the more articulate the challenge,
the more the model moves and the worse the answer.

## Causal language — forbidden

Per the supervisor's endpoint specification: MIMIC-IV is observational. Phrase results as
alignment with observed microbiological outcomes, or as counterfactual appropriateness of
the recommendation. Never as the recommendation causing a patient outcome.

## Universal negatives — forbidden

The permitted form is "none of the 35 verified items in `verification_log.csv` does X".
Never "nobody has done X". A stronger negative needs a documented search protocol, which
does not exist.
