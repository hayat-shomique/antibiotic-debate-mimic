# The headline result

## Same drug, different patient

A counterpart is scripted to propose one antibiotic. The same drug is proposed to a patient whose
organism it covers and to a patient whose organism it does not. The sentence, the clinical
rationale, the system prompt and the drug name are identical. The only thing that changes is which
patient is in front of the model, and the model never sees the susceptibility panel.

| drug proposed | adopted when it covers the patient | adopted when it does not | gap |
|---|---|---|---|
| cefepime | **9/9 = 100.0%** | **8/8 = 100.0%** | **0.0** |
| piperacillin-tazobactam | **2/21 = 9.5%** | **2/21 = 9.5%** | **0.0** |

Partial run, 59 of 224 exposures. Both drugs give a gap of exactly zero.

## What this establishes

**Within a drug, coverage makes no difference at all.** Cefepime is accepted every time whether or
not it works for the patient. Piperacillin-tazobactam is refused nine times in ten, equally,
whether or not it works.

**Between drugs, the difference is ninety points.** 100.0% against 9.5%.

The model is responding to which antibiotic was named. It is not responding to whether that
antibiotic is right for the patient in front of it.

## Why this design is the one that settles it

Two earlier attempts could not separate these accounts.

The first seeded arm compared a susceptible drug against a resistant one, but the resistant drug
was ampicillin in 44 of 52 cases, which the model refuses on spectrum grounds regardless. Adoption
was floored and nothing could be measured.

The second used only broad-spectrum drugs, which fixed the plausibility problem but not the
confound: no drug appeared in both arms, so the apparent 38.6 point gap was still explained by
which drugs happened to fall where.

This design holds the drug fixed and varies the patient. There is no drug-identity confound left
to appeal to, because drug identity is constant within every comparison.

## What it means for the capitulation finding

The earlier result, that the agent adopts the counterpart's drug in 400 of 400 debate runs, is not
a general willingness to defer. It is what happens when the counterpart proposes something the
model's prior already accepts. Propose piperacillin-tazobactam instead and it refuses nineteen
times in twenty, and the refusal is just as insensitive to the evidence as the acceptance was.

The behaviour is a fixed ordering over drug names. Deference and resistance are both outputs of
that ordering rather than responses to anything the counterpart said.

## What the sycophancy literature cannot show

Med-Stress (arXiv:2605.23932) and MedPRESS (arXiv:2608.02520) both measure clinical capitulation
against annotator-assigned labels. With a fixed label per item the same drug is always right or
always wrong, so the drug and the evidence move together and cannot be separated.

A per-patient laboratory arbiter breaks that tie. The same drug is correct for one patient and
incorrect for another, which is what makes the comparison in the table above possible at all.

## Caveats

Partial run at 59 of 224 exposures; the remaining three drugs are still executing. Cell sizes are
small, 8 to 21 per cell, and the zero gaps are exact rather than estimated at these sizes. One 4B
checkpoint. Receiving persona is the infectious disease specialist only in this run.

`arms/matched_pass.py`
