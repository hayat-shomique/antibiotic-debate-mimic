# The story

The spine is Prof. Zhu's endpoint hierarchy of 14 August, because that hierarchy is what the
evaluation was built to answer. Every number here is generated from `results/`.

## The question, in her words

> That directly answers the more interesting research question: does multi-agent communication
> improve clinical decision quality, or does it merely make the models agree?

## The answer

| what the agent hears | harmful revision rate | coverage |
|---|---|---|
| a scripted sentence with no content | 0.0 to 1.5% | unchanged |
| **a second agent arguing a case** | **15.2%** | **87.5% to 78.0%, -9.5 points** |
| the susceptibility panel | **0.0%** | 78.0% to 95.2%, +17.2 points |

**Multi-agent communication makes the decision worse.** Agent A abandons a correct recommendation
in 15.2% of the cases where it had one, and coverage of the organism falls 9.5 points. The
laboratory result, by contrast, never once caused a correct answer to become incorrect across 311
opportunities, and raised coverage 17.2 points.

The rest of this document is how that was established and what it does not mean.

## Endpoint 1, appropriateness: the default is a constant, and it is a good one

Before any conversation the model picks **piperacillin-tazobactam for 100% of patients**: 1 distinct choice across
200 decisions, reproduced independently in three separately run files covering 712 decisions in total.

That looks alarming until you ask what it scores.

| condition | covers the organism |
|---|---|
| baseline, pre-culture | 175/200 = 87.5% |
| neutral control | 175/200 = 87.5% |
| susceptibility panel revealed | 191/200 = 95.5% |

**87.5% from a single constant.** Nothing in the prompt predicts the organism: the case block
carries age, sex, admission type, admission source, hours since admission and a prior-exposure
flag, and no laboratory data at all. Under that much uncertainty one broad empiric agent for
everybody is the rational policy, not a broken one. Evidence adds +8.0 points.

This matters for reading everything below. The baseline is not a fragile correct answer that
pressure destroys. It is a defensible policy applied to everybody.

## Endpoint 2, the patient does not change the answer

Holding the proposed drug fixed and varying only the patient, adoption is the same whether or not
the drug covers what the patient actually grew. 5 drugs, gap at most 4.0 points. Mantel-Haenszel odds ratio 1.0
(p = 0.7151), stratified by drug. Between drugs the spread is 100 points.

The identity of the antibiotic moves the answer. The patient does not.

## Endpoint 3, the pre-specified test: pressure moves it, a neutral turn does not

Protocol section 7, frozen before any run, specifies an exact binomial on cases that change under
exactly one of the neutral control and pressure.

| | changes recommendation |
|---|---|
| neutral interlocutor | 0 of 70 |
| unsupported pressure | 90 to 100% |

c is **zero under every framing**, b runs 63 to 70, exact p at worst 2.17e-19. Being spoken to does not
move the model. Being disagreed with almost always does.

## Endpoint 4 is where the story turns

Her transition table, exactly as she specified it. Correct means the recommendation covers the
organism the laboratory identified.

| pressure framing | stable correct | beneficial correction | **harmful deference** | no improvement | HRR | BCR |
|---|---|---|---|---|---|---|
| authority | 67 | 2 | 1 | 0 | 1.5% | 100.0% |
| peer consensus | 68 | 2 | 0 | 0 | 0.0% | 100.0% |
| safety framing | 67 | 2 | 1 | 0 | 1.5% | 100.0% |
| bare doubt | 67 | 2 | 1 | 0 | 1.5% | 100.0% |
| **evidence (panel)** | 172 | 11 | 2 | 1 | 1.1% | 91.7% |
| **neutral control** | 175 | 0 | 0 | 12 | 0.0% | 0.0% |

**Harmful revision rate is 0.0 to 1.5%.** On the endpoint she named as strongest, unsupported
pressure does almost no damage. The model abandons its drug in 90 to 100% of cases and lands on
another drug that also covers.

If the study stopped here it would conclude that the sycophancy is harmless. That conclusion would
be wrong, and she is the one who said where to look:

> Spectrum appropriateness: distinguish effective from appropriately narrow. A model recommending
> extremely broad therapy to everyone could achieve high coverage while still making poor
> antimicrobial-stewardship decisions.

| condition | carbapenem use | distinct drugs chosen |
|---|---|---|
| baseline | 0/200 = 0.0% | 1 |
| neutral control | 0/200 = 0.0% | 1 |
| **under unsupported pressure** | **261/312 = 83.7%** | 5 |
| susceptibility panel revealed | 42/200 = 21.0% | 10 |

**A sentence carrying no clinical evidence drives carbapenem use from 0% to 84%.** It buys
nothing: coverage was already 87.5% and harmful revision is near zero. Carbapenem overuse is the
principal driver of carbapenem-resistant Enterobacterales, so this is not a neutral escalation.

Given the actual panel the model reaches 21% carbapenem across 10 distinct drugs, and there the
broadening is earned.

## Rung two of her ladder: does few-shot help?

> "zero shot will not work, we can take something ready made and say like, look, this is already
> trained. And then I'm going to use some example of how it look like. And then so you give it,
> like, a few shots and then see whether it improves. And if it doesn't, then you can move it to
> the next level, that is now your training from scratch."

Four exemplars per case, 200 cases. Two things were measured, because moving off the constant is not
the same as doing better.

| | zero-shot | few-shot |
|---|---|---|
| distinct antibiotics chosen | 1 | 6 |
| Access-group (narrow) prescribing | 0.0% | 34.5% |
| carbapenem prescribing | 0.0% | 12.0% |
| covers the organism, paired subset of 175 | 93.1% | 84.0% |

Few-shot breaks the constant: the model moves off its default in 62.5% of cases and chooses from
6 agents instead of one, a third of them narrow-spectrum.

**And it is significantly worse at the job.** On the 175 cases where both conditions give a
determinate verdict, few-shot loses 18 correct recommendations and gains 2, exact McNemar
p = 0.0004025.

It is not simply copying what it was shown: the answer appears in that case's own exemplars only
36.0% of the time.

So the honest answer to her rung two is that it does not improve. Examples teach the model to vary
its prescribing without teaching it which patient needs which drug, and variety without
discrimination costs coverage. By her own sequencing, that is the result that justifies moving to
the next rung rather than declaring the problem solved with prompting.

## What the project actually shows

**Sycophancy here is invisible on the accuracy endpoint and severe on the stewardship endpoint.**
Score whether the agent got the right answer and multi-agent debate looks harmless. Score what kind
of answer it gave and pressure produces a wholesale escalation to last-line therapy that no
evidence supports.

That is the contribution: not that models are agreeable, which is known, but that the standard way
of measuring the harm cannot see this one. The endpoint hierarchy is what makes it visible, and it
came from the supervisor's own framing.

## Reproducing every number here

```
python3 analysis/tingting_endpoints.py    # the endpoint hierarchy and the transition table
python3 analysis/primary_test.py          # the pre-specified primary test
python3 analysis/policy_degeneracy.py     # how many drugs are ever chosen
python3 analysis/canonical_numbers.py     # everything else, into results/RESULTS.json
python3 analysis/render_story.py          # regenerates this document
```
