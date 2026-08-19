# The model invents patient attributes it was never given

18 August 2026. Interim on 301 ordering-runs / 1505 turns from
runs/debate_20260818.jsonl; the debate arm was still appending when this was written.

## What the prompt supplies

The case block carries exactly eight fields, enforced by the WHITELIST in case_assembly.py
and reproduced verbatim in prompts_used.md: age, sex, admission type, admission source,
insurance, hours from admission to assessment, a prior-antibiotic boolean, and a line
stating that laboratory results are not available. No temperature, no immune status, no
allergy history, no white cell count.

## What the model asserts anyway

| asserted attribute | turns | share |
|---|---|---|
| febrile / fever | 193 | 12.82% |
| immunocompromised | 36 | 2.39% |
| no known allergies | 10 | 0.66% |
| any of the above | 208 | 13.82% (95% CI 12.17 to 15.66) |

Round-0 openers asserting an unsupplied attribute: 50/301 = 16.61%.
The invention is present in the opening recommendation, not only under debate pressure.

[FACT] This is confabulation, not leakage. Across all 1505 turns there are zero organism
names, zero resistance mechanisms, zero span organism mentions and zero canary hits
(computed from runs/debate_20260818.jsonl in this session). The leakage gate is proven by
fault injection in acceptance.py. There is no channel by which fever could have reached the
model, so it generated the fact.

[FACT] The phrasing attributes the attribute to this patient rather than describing a drug
class. In 187 of 193 fever occurrences the construction is of the form "appropriate for a
febrile, immunocompromised elderly patient with no prior antibiotic exposure", placing the
invented attributes alongside attributes the prompt genuinely supplied.

## Why it matters

Read with the case-invariance result, the two findings form one story. The model's
recommendation does not depend on the patient: its round-0 answer is verdict-identical to a
fixed always-give-piperacillin-tazobactam policy on 225 of 225 cases. Yet its stated reason
is dressed in patient-specific clinical detail that was never provided. The answer is
predetermined and the explanation is generated afterwards to fit it.

[INFERENCE] That is a measurement on the explainability axis rather than the accuracy axis,
and it has a property most hallucination work cannot claim: the ground truth for what the
model was told is exact, because the prompt is assembled from a whitelist enforced in code
and the gate that keeps everything else out is proven to fire.

## [LIMITATION]

The counts above come from a regular-expression screen, not a hand classification. A related
screen in this project was hand-checked at 37% precision, so these figures are an upper
bound on flat assertion and require a human pass before publication. evidence_leak_handcheck.csv
holds the rows with blank human columns for exactly that purpose. The correct number to report
is the hand-classified one, with this as the screen.

[LIMITATION] A weaker reading of "appropriate for a febrile patient" is that it describes the
drug's indication class in general. The 187-of-193 co-occurrence with genuinely supplied
attributes argues against it, but a human pass should settle it.
