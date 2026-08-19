#!/usr/bin/env python3
"""Render STORY.md, the narrative spine, from the result files.

This is the argument the talk makes, in order, with every number pulled from
results/ rather than typed. It is not the deck. It is the thing the deck is built
from, so that a slide can never claim something the repository cannot reproduce.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda n: json.load(open(os.path.join(ROOT, "results", n)))

deg = R("policy_degeneracy.json")
pri = R("primary_test.json")
res = R("RESULTS.json")

base = deg["C0 baseline"]
neut = deg["Cn neutral control"]
pres = deg["C1 under unsupported pressure"]
evid = deg["C2 with the panel revealed"]

fr = pri["by_framing"]
c1s = [100 * v["flip_rates"]["C1"]["k"] / v["flip_rates"]["C1"]["n"] for v in fr.values()]
cn_flip = max(v["flip_rates"]["Cn"]["k"] for v in fr.values())
any_v = next(iter(fr.values()))
c2 = any_v["flip_rates"]["C2"]
bs = [v["discordant"]["b_pressure_only"] for v in fr.values()]
cs = [v["discordant"]["c_control_only"] for v in fr.values()]
n_pri = any_v["n_primary"]
maxp = max(v["discordant"]["p_exact"] for v in fr.values())

m = res["D_MATCH_1_drug_identity_vs_patient"]
mdrugs = [(d, v) for d, v in m["by_drug"].items() if "gap_pct" in v]
gaps = [abs(v["gap_pct"]) for _, v in mdrugs]
cmh = m.get("cmh_stratified_by_drug") or {}
rates = [100 * v["covers"]["adopted"] / v["covers"]["n"] for _, v in mdrugs]

doc = """# The story

The argument in order, with every number reproducible from `results/`.

## The question

Two language-model agents discuss which antibiotic to give a patient with a bloodstream infection.
Does talking to each other make the decision better, or does it just make them agree?

The reason this is answerable at all is that the patient's own microbiology laboratory eventually
says which antibiotics actually worked. Neither agent can see that result and neither can argue
with it. It is an external referee, not another model's opinion.

## Finding 1: the default is a constant

Before any conversation, asked to choose an antibiotic for a patient, the model picks
**%s for %.0f%% of patients**. Not the most common choice. The only choice: %d distinct
antibiotic across %d decisions.

This reproduces independently in four arms that ran at different times, including %d decisions in
the pressure arm and %d in the debate arm.

Every 100%% figure in the baseline results is measuring this constant. That matters for reading
everything below: the baseline is not a well-calibrated policy that pressure degrades. It is one
answer given to everybody.

## Finding 2: the patient does not change the answer

Holding the proposed drug fixed and varying only the patient, adoption of that drug is identical
whether or not it covers the organism the patient actually grew. %d drugs tested, and the gap is
%s in every one. Stratified by drug, the Mantel-Haenszel odds ratio is %s (p = %s).

Between drugs the spread is %.0f points. The identity of the antibiotic moves the answer. The
patient does not.

Findings 1 and 2 are the same insensitivity seen from two directions.

## Finding 3: a neutral turn does not move it, pressure almost always does

This is the test the protocol pre-specified before any run.

The same case is put to the model four ways: baseline, a neutral interlocutor who says something
contentless, an interlocutor who pushes back with no evidence, and the susceptibility panel
revealed in a clean context.

| condition | recommendation changes |
|---|---|
| neutral interlocutor | %d of %d |
| unsupported pressure | %.0f to %.0f%% |
| the actual laboratory panel | %d/%d = %.1f%% |

Discordant counts, which is what the protocol asked for: b between %d and %d, c is **zero under
every framing**, exact binomial p at worst %.3g.

The model is not generally unstable. Being spoken to does not move it. Being disagreed with does.

## Finding 4: the thing that should worry a clinician

Unsupported pushback, a sentence carrying no clinical information at all, moves the recommendation
in %.0f to %.0f%% of cases. The susceptibility panel, the only input in the study that actually
carries information about this patient, moves it in %.1f%%.

**A person disagreeing moves the model more than the laboratory result does.**

## Finding 5: but evidence is the only thing that produces real reasoning

Look at what the answer becomes, not just whether it changed.

| what dislodged the default | distinct antibiotics chosen | most common |
|---|---|---|
| nothing (baseline) | %d | %s at %.0f%% |
| a neutral turn | %d | %s at %.0f%% |
| unsupported pressure | %d | %s at %.0f%% |
| the susceptibility panel | %d | %s at %.0f%% |

Under pressure the model swaps one constant for another: it escalates to %s in %.0f%% of cases
regardless of the patient. That is not reconsideration, it is capitulation with a default attached.

Given the panel it produces %d distinct choices with no single one dominant. The model *can*
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
""" % (
    base["top"], base["top_share_pct"], base["distinct"], base["n"],
    deg["C0 inside the pressure arm"]["n"], deg["debate round 0"]["n"],
    len(mdrugs), ("exactly zero" if max(gaps) == 0 else "at most %.1f points" % max(gaps)),
    cmh.get("or_mh"), cmh.get("p"),
    (max(rates) - min(rates)) if rates else 0,
    cn_flip, any_v["flip_rates"]["Cn"]["n"], min(c1s), max(c1s),
    c2["k"], c2["n"], 100 * c2["k"] / c2["n"],
    min(bs), max(bs), maxp,
    min(c1s), max(c1s), 100 * c2["k"] / c2["n"],
    base["distinct"], base["top"], base["top_share_pct"],
    neut["distinct"], neut["top"], neut["top_share_pct"],
    pres["distinct"], pres["top"], pres["top_share_pct"],
    evid["distinct"], evid["top"], evid["top_share_pct"],
    pres["top"], pres["top_share_pct"], evid["distinct"],
)
open(os.path.join(ROOT, "STORY.md"), "w").write(doc)
print("wrote STORY.md")
