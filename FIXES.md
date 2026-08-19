# Fix list

Single source of truth for what adversarial review found and what has been done about it.
Every row is checkable. Status changes only when the fix is in the repository.

Sources: four-lens red team (clinical microbiology, statistics, research integrity, supervisor
standard), each objection re-derived from disk by a separate adjudicating pass before it counted.

| | |
|---|---|
| Total | 19 |
| Done | 4 |
| Open | 15 |

---

## Done

| id | finding | what was done | commit |
|---|---|---|---|
| **F01** | Payer status fed into a treatment prompt. `insurance` was in the case-block whitelist and rendered for all 400 runs: Medicare 110, Private 45, Medicaid 40, Other 3, plus 2 rows where a NaN bug printed `nan`. No clinical rationale, and a fairness problem in a health-AI setting regardless of effect size. | Removed from the whitelist and from the rendered block. Logged as D-PAYER-1 with the disclosure that completed runs contain it. Measured effect is zero: round-0 is piperacillin-tazobactam across all 200 cases and all four payer values. | d96a078 |
| **F02** | Confidence endpoint claimed as a second dimension of sycophancy. | Withdrawn. Every observation is 85, 90 or 95, so 200/200 clear the pre-registered threshold of 80 both before and after. A threshold that cannot fail is not a pre-registration, and correct+confident to wrong+confident is arithmetically identical to correct to wrong. Slide replaced with the null. | deck v5 |
| **F03** | No version control. `debate_run.py` changed mid-run, so 16 of 400 ordering-runs came from a writer that no longer exists on disk. | Repository initialised, full history from this point. Prior state is unrecoverable and that is stated rather than papered over. | d4a518c |
| **F04** | 77.6% over-treated presented as a model result. | Withdrawn from the deck. The figure pools 8 arms including the clinician arm, a sensitivity duplicate, and both constant floor agents, across two taxonomies, so every recommendation is counted twice. | deck v5 |

---

## Open, ordered by how much damage they do

| id | finding | fix | effort |
|---|---|---|---|
| **F05** | **Pressure ladder confounded three ways.** The bare and reasoned arms differ in system prompt, in separator header, and in whether an alternative drug is named. `degraded_pass.py:10` claims they differ "only in content". They do not. The bare arm's destination is meropenem 33/34, and meropenem appears in 0 of 2,000 debate turns, so the two rungs are not even on the same response manifold. | Delete every attribution of the 43.3-point gap to argument content. Report three descriptive rates only. Add the missing rung: a bare challenge that names a drug and gives no argument, same system prompt, same header. | 60 cases, about 10 min |
| **F06** | **The persona-asymmetry sentence is false on the turn data.** Agent B is never challenged at turn 4: A has already adopted B's drug at turn 3 in 200/200. One rule with no persona term reproduces all four cells. | Delete the sentence. Replace with the number that survives: the two personas' independent openings agree on 199/200 cases before any interaction. | edit only |
| **F07** | **"This is the entire instrument" is false.** Six further system prompts are actually sent across the control arms, the case block itself is not shown on the slide, and `sys_B_round0` is missing. | Paste the verbatim case block, add the fourth prompt, and reword to "the debate instrument in full; each control arm adds one further system prompt, listed in the appendix". | edit only |
| **F08** | **Over-treatment is driven by narrower agents no microbiologist would use for bacteraemia.** 193 of 215 over-treated rows have a narrower set entirely inside cefazolin, ampicillin, TMP-SMX, gentamicin. Cefazolin is reported only against the CLSI uncomplicated-UTI surrogate breakpoint, which does not apply to bloodstream infection. | Add one boolean to the spectrum output: narrower set not entirely inside that four-drug group. Report both counts. | filter over an existing CSV |
| **F09** | **Clinician comparator answers a different question in a different answer space.** 43% of clinician regimens are multi-agent while the model is forced to name exactly one. | State it on the slide. The comparison is already reported on the determined-only denominator (91.1 against 90.6) which is the defensible form. | edit only |
| **F10** | **Every interval treats ordering-runs as independent.** They are 200 patients seen twice, measured intra-case correlation 0.86 to 0.91. | Recompute every interval with a cluster correction on the patient, or drop intervals and report counts. | analysis |
| **F11** | **41% order effect has no chance baseline.** With only 3 drugs ever used and these marginals, independent draws would disagree more often, so 41% is not above chance. | Report the expected disagreement under independence beside it, or drop the framing. | analysis |
| **F12** | **BCR 13/24 is 12 patients.** The rate is reported on runs, not on the clustering unit. | Report the patient-level figure with an exact interval, or state it is directional only at n=12. | analysis |
| **F13** | **No multiplicity correction.** Fourteen declared endpoints across eleven arms, all drawn from the same 200 case_ids. | Declare the primary endpoint explicitly, mark the rest as exploratory, or apply Benjamini-Hochberg. | analysis |
| **F14** | **The pre-registered primary arm was never run.** `protocol_v1.md` designates C1 scripted pressure as primary; it has 3 cases. Every headline comes from an arm the protocol designates a 30-case demonstration. | Either run C1 or state plainly in the methods that the primary arm was not completed and the reported arm was pre-specified as a demonstration. | 200 cases or one honest paragraph |
| **F15** | **Four live deviation ids have no row in any log**, including D-GATE-2, which determines which data enter the analysis. | Add the missing rows. | 10 min |
| **F16** | **The deviation log is regenerated wholesale from a Python literal** with hardcoded timestamps, so it is not an append-only audit trail. | Make it append-only, or state that it is a generated summary and keep the raw record elsewhere. | small |
| **F17** | **`protocol_v1.md` has seven unfilled placeholders** in its provenance stamp and names a scoring module that does not exist under that name. | Fill from `protocol_freeze.json` as a stamped addendum; correct both module references. | 10 min |
| **F18** | **The content hash freezes the wrong object.** It covers the 7,796-case skeleton, while the analysed population is a 993-case frame built by later filters. | State exactly what is and is not covered by the hash. | edit only |
| **F19** | **AmpC de-repression is unhandled.** 18% of the cohort are inducible-AmpC organisms and the intrinsic-resistance table has no entry for them. | Add the limitation. Correcting the scoring is out of scope for this internship. | edit only |

---

## Rules for this file

Status moves to Done only when the change is committed and the acceptance test in the row passes.
Nothing is marked Done because it is understood or because it is written on a slide. If a fix
turns out to be wrong, the row goes back to Open with the reason.
