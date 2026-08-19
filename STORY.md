# The story

The argument in order, with every number reproducible from `results/`.

## The question

Two language-model agents discuss which antibiotic to give a patient with a bloodstream infection.
Does talking to each other make the decision better, or does it just make them agree?

The reason this is answerable at all is that the patient's own microbiology laboratory eventually
says which antibiotics actually worked. Neither agent can see that result and neither can argue
with it. It is an external referee, not another model's opinion.

## Finding 1: the default is a constant

Before any conversation, asked to choose an antibiotic for a patient, the model picks
**piperacillin-tazobactam for 100% of patients**. Not the most common choice. The only choice: 1 distinct
antibiotic across 200 decisions.

This reproduces independently in four arms that ran at different times, including 312 decisions in
the pressure arm and 409 in the debate arm.

Every 100% figure in the baseline results is measuring this constant. That matters for reading
everything below: the baseline is not a well-calibrated policy that pressure degrades. It is one
answer given to everybody.

## Finding 2: the patient does not change the answer

Holding the proposed drug fixed and varying only the patient, adoption of that drug is identical
whether or not it covers the organism the patient actually grew. 4 drugs tested, and the gap is
at most 6.7 points in every one. Stratified by drug, the Mantel-Haenszel odds ratio is 1.0 (p = 0.6132).

Between drugs the spread is 100 points. The identity of the antibiotic moves the answer. The
patient does not.

Findings 1 and 2 are the same insensitivity seen from two directions.

## Finding 3: a neutral turn does not move it, pressure almost always does

This is the test the protocol pre-specified before any run.

The same case is put to the model four ways: baseline, a neutral interlocutor who says something
contentless, an interlocutor who pushes back with no evidence, and the susceptibility panel
revealed in a clean context.

| condition | recommendation changes |
|---|---|
| neutral interlocutor | 0 of 70 |
| unsupported pressure | 90 to 100% |
| the actual laboratory panel | 38/70 = 54.3% |

Discordant counts, which is what the protocol asked for: b between 63 and 70, c is **zero under
every framing**, exact binomial p at worst 2.17e-19.

The model is not generally unstable. Being spoken to does not move it. Being disagreed with does.

## Finding 4: the thing that should worry a clinician

Unsupported pushback, a sentence carrying no clinical information at all, moves the recommendation
in 90 to 100% of cases. The susceptibility panel, the only input in the study that actually
carries information about this patient, moves it in 54.3%.

**A person disagreeing moves the model more than the laboratory result does.**

## Finding 5: but evidence is the only thing that produces real reasoning

Look at what the answer becomes, not just whether it changed.

| what dislodged the default | distinct antibiotics chosen | most common |
|---|---|---|
| nothing (baseline) | 1 | piperacillin-tazobactam at 100% |
| a neutral turn | 1 | piperacillin-tazobactam at 100% |
| unsupported pressure | 5 | meropenem at 84% |
| the susceptibility panel | 10 | piperacillin-tazobactam at 40% |

Under pressure the model swaps one constant for another: it escalates to meropenem in 84% of cases
regardless of the patient. That is not reconsideration, it is capitulation with a default attached.

Given the panel it produces 10 distinct choices with no single one dominant. The model *can*
differentiate between patients. It does not do so by default, and it does not do so when pushed.

## What this means

The failure is not that the agents are too agreeable. It is that agreement and disagreement are
both operating on something that was never patient-specific to begin with. A debate between two
agents that are not reading the patient cannot become a better clinical decision by talking.

The measurement matters more than the fix: none of this is visible if you score agreement between
agents, and all of it is visible the moment you score against the laboratory.

## Reproducing every number here

```
python3 analysis/primary_test.py        # the pre-specified primary test
python3 analysis/policy_degeneracy.py   # how many drugs are ever chosen
python3 analysis/canonical_numbers.py   # everything else, into results/RESULTS.json
python3 analysis/render_story.py        # regenerates this document
```
