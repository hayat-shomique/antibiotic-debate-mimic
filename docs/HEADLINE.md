# The headline result, with citable support

## The result

Computed by `headline.py` from `runs/debate_20260818.jsonl`, 400 ordering-runs over 200 paired
cases, in the stratification the supervisor specified on 18 August.

| Counterpart was… | n | adopted its drug | mean ΔQ | got worse | got better |
|---|---|---|---|---|---|
| **RIGHT** | 312 | **312/312 = 100.0%** | +0.043 | 0 | 13 |
| **WRONG** | 88 | **88/88 = 100.0%** | **−0.853** | **52** | **0** |

Adoption is **100% in both strata**. The agent takes the counterpart's drug every time,
regardless of whether that drug covers the organism. The two rows differ only in what the
counterpart happened to say.

The direction is absolute in both cells. When the counterpart was wrong, 52 runs got worse and
none got better. When it was right, 13 got better and none got worse.

## The sentence

> The two agents already agreed on 199 of 200 cases before they communicated. Five turns of
> debate added 0.5 points of agreement and cost 9.5 points of susceptibility concordance — and
> the entire loss sits in the 88 runs where the counterpart was wrong, in which adoption was
> still 100%.

Her question was *"does multi-agent communication improve clinical decision quality, or does it
merely make the models agree?"* The measured answer is **neither**: they already agreed, and the
conversation made them worse.

## Why this is the strongest form of the result

Every weaker version of this finding is vulnerable:

- *"It abandons its position 400/400"* — answerable with "it is a small model, its output changes
  when the prompt changes".
- *"Order changes the answer in 41% of cases"* — answerable with "only three drugs are ever used,
  so a flip is not surprising".
- *"Two agents perform like one"* — partly entailed by the abandonment rate.

The stratified table is not vulnerable to any of those, because **the comparison is internal**.
The same model, the same prompt structure, the same 100% adoption — and opposite outcomes decided
entirely by the counterpart. No external baseline is needed to make the point.

## What supports it in the literature

**Kim et al. 2026, _Nature Machine Intelligence_ 8:1157–1172, doi 10.1038/s42256-026-01268-y.**
A controlled grid of 260 configurations across six benchmarks, five coordination topologies and
nine models, holding prompts, tools and compute fixed. Aggregate mean multi-agent improvement:
**0.0%** (95% CI −58.7% to 77.2%). Their one doubly-robust predictor is the single-agent baseline.
*Use:* a null coordination effect in a clinical frame is consistent with a large controlled prior,
not an isolated negative. Cite the direction only — their leave-one-dataset-out R² is −2.09, so
no coefficient transports.

**Oh, Kim, Park & Kim 2026, _JMIR_ 28:e90693, doi 10.2196/90693.**
~30 open models across seven medical benchmarks. When a misleading answer is injected **framed as
another physician's opinion**, models abandon correct reasoning, and on harder tasks *"even
optimal scaling strategies fail to restore baseline performance"* (p. 14). They also report that
models are *"particularly sensitive to the expertise level of the physician providing the
additional input"* (p. 13).
*Use:* the closest published precedent, and it licenses the persona design directly. State both
halves — scaling *does* recover baseline on easier tasks (p. 13).

**Zheng, Shi & Yi 2025, MedCoAct, arXiv 2510.10461.**
Doctor and pharmacist agents collaborating; reports collaboration **helping** by 7.04 points on
the DrugCareQA benchmark.
*Use:* the contrast, stated openly. Their arbiter is a constructed benchmark key; this study's is
a per-patient laboratory result. Opposite sign, different arbiter — say so rather than hide it.

**Mohsin, Bilal, Umer & Fox 2026, arXiv 2604.05279.**
Formalises the distinction between *pressure capitulation* (changing a correct answer under social
pressure) and *evidence blindness* (ignoring provided context), and fixes them by training.
*Use:* their vocabulary. The stratified table above is a direct measurement of pressure
capitulation with the evidence axis held externally — training-free, in a clinical setting.

**Antonie et al. 2026, _Antibiotics_ 15(4):368, doi 10.3390/antibiotics15040368.**
LLM empiric antibiotic recommendations scored against susceptibility, versus clinicians, 493
admissions, 158 microbiology-evaluable.
*Use:* concede the arbiter. Susceptibility-arbitrated LLM prescribing exists. What does not exist
in that paper is a second agent, a challenge, or a revision step.

## The falsification condition, to state aloud

Any published study that runs a multi-agent clinical debate, scores the **revision** against
per-patient microbiology, and reports a speaking-order or null-arm control. If one exists, this
is a replication in a new cohort and should be described as such.
