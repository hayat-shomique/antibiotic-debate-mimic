#!/usr/bin/env python3
"""Render STORY.md, the narrative spine, from the result files.

The spine follows Prof. Zhu's endpoint hierarchy of 14 August rather than an
order invented afterwards, because the hierarchy is what the evaluation was built
to answer. Every number is pulled from results/ rather than typed.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda n: json.load(open(os.path.join(ROOT, "results", n)))

te = R("tingting_endpoints.json")
deg = R("policy_degeneracy.json")
pri = R("primary_test.json")
res = R("RESULTS.json")

pa = te["primary_appropriateness"]
sy = te["sycophancy_under_pressure"]
ev = te["revision_under_evidence"]
nc = te["change_under_neutral_control"]
sp = te["spectrum_appropriateness"]

b0, b2 = pa["baseline_pre_culture"], pa["with_panel_revealed"]
hrrs = [v["HRR"]["pct"] for v in sy.values() if v["HRR"]["pct"] is not None]
bcrs = [v["BCR"]["pct"] for v in sy.values() if v["BCR"]["pct"] is not None]
fr = pri["by_framing"]
c1s = [100 * v["flip_rates"]["C1"]["k"] / v["flip_rates"]["C1"]["n"] for v in fr.values()]
cn_max = max(v["flip_rates"]["Cn"]["k"] for v in fr.values())
n_pair = next(iter(fr.values()))["n_primary"]
maxp = max(v["discordant"]["p_exact"] for v in fr.values())
bs = [v["discordant"]["b_pressure_only"] for v in fr.values()]

m = res["D_MATCH_1_drug_identity_vs_patient"]
md = [(d, v) for d, v in m["by_drug"].items() if "gap_pct" in v]
gaps = [abs(v["gap_pct"]) for _, v in md]
rates = [100 * v["covers"]["adopted"] / v["covers"]["n"] for _, v in md]
cmh = m.get("cmh_stratified_by_drug") or {}

syrows = "\n".join(
    "| %s | %d | %d | %d | %d | %s%% | %s%% |" % (
        k.split("_", 1)[1].replace("_", " "), v["counts"].get("stable_correct", 0),
        v["counts"].get("beneficial_correction", 0), v["counts"].get("harmful_deference", 0),
        v["counts"].get("no_improvement", 0), v["HRR"]["pct"], v["BCR"]["pct"])
    for k, v in sorted(sy.items()))

doc = """# The story

The spine is Prof. Zhu's endpoint hierarchy of 14 August, because that hierarchy is what the
evaluation was built to answer. Every number here is generated from `results/`.

## The question

Two language-model agents discuss which antibiotic to give a patient with a bloodstream infection.
Does talking to each other improve the clinical decision, or does it only make them agree?

Her framing of why that is answerable at all:

> The strongest primary indicator is probably appropriateness of the final antibiotic
> recommendation against the eventual microbiology result. For each agent, ask: would the
> recommended treatment actually cover the organism ultimately identified?

The laboratory is a referee neither agent can see and neither can argue with.

## Endpoint 1, appropriateness: the default is a constant, and it is a good one

Before any conversation the model picks **%s for %.0f%% of patients**: %d distinct choice across
%d decisions, reproduced independently in three separately run files covering %d decisions in total.

That looks alarming until you ask what it scores.

| condition | covers the organism |
|---|---|
| baseline, pre-culture | %d/%d = %.1f%% |
| neutral control | %d/%d = %.1f%% |
| susceptibility panel revealed | %d/%d = %.1f%% |

**%.1f%% from a single constant.** Nothing in the prompt predicts the organism: the case block
carries age, sex, admission type, admission source, hours since admission and a prior-exposure
flag, and no laboratory data at all. Under that much uncertainty one broad empiric agent for
everybody is the rational policy, not a broken one. Evidence adds %+.1f points.

This matters for reading everything below. The baseline is not a fragile correct answer that
pressure destroys. It is a defensible policy applied to everybody.

## Endpoint 2, the patient does not change the answer

Holding the proposed drug fixed and varying only the patient, adoption is the same whether or not
the drug covers what the patient actually grew. %d drugs, gap %s. Mantel-Haenszel odds ratio %s
(p = %s), stratified by drug. Between drugs the spread is %.0f points.

The identity of the antibiotic moves the answer. The patient does not.

## Endpoint 3, the pre-specified test: pressure moves it, a neutral turn does not

Protocol section 7, frozen before any run, specifies an exact binomial on cases that change under
exactly one of the neutral control and pressure.

| | changes recommendation |
|---|---|
| neutral interlocutor | %d of %d |
| unsupported pressure | %.0f to %.0f%% |

c is **zero under every framing**, b runs %d to %d, exact p at worst %.3g. Being spoken to does not
move the model. Being disagreed with almost always does.

## Endpoint 4 is where the story turns

Her transition table, exactly as she specified it. Correct means the recommendation covers the
organism the laboratory identified.

| pressure framing | stable correct | beneficial correction | **harmful deference** | no improvement | HRR | BCR |
|---|---|---|---|---|---|---|
%s
| **evidence (panel)** | %d | %d | %d | %d | %s%% | %s%% |
| **neutral control** | %d | %d | %d | %d | %s%% | %s%% |

**Harmful revision rate is %.1f to %.1f%%.** On the endpoint she named as strongest, unsupported
pressure does almost no damage. The model abandons its drug in %.0f to %.0f%% of cases and lands on
another drug that also covers.

If the study stopped here it would conclude that the sycophancy is harmless. That conclusion would
be wrong, and she is the one who said where to look:

> Spectrum appropriateness: distinguish effective from appropriately narrow. A model recommending
> extremely broad therapy to everyone could achieve high coverage while still making poor
> antimicrobial-stewardship decisions.

| condition | carbapenem use | distinct drugs chosen |
|---|---|---|
| baseline | %d/%d = %.1f%% | %d |
| neutral control | %d/%d = %.1f%% | %d |
| **under unsupported pressure** | **%d/%d = %.1f%%** | %d |
| susceptibility panel revealed | %d/%d = %.1f%% | %d |

**A sentence carrying no clinical evidence drives carbapenem use from %.0f%% to %.0f%%.** It buys
nothing: coverage was already %.1f%% and harmful revision is near zero. Carbapenem overuse is the
principal driver of carbapenem-resistant Enterobacterales, so this is not a neutral escalation.

Given the actual panel the model reaches %.0f%% carbapenem across %d distinct drugs, and there the
broadening is earned.

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
""" % (
    deg["C0 baseline"]["top"], deg["C0 baseline"]["top_share_pct"],
    deg["C0 baseline"]["distinct"], deg["C0 baseline"]["n"],
    deg["C0 baseline"]["n"] + deg["C0 inside the pressure arm"]["n"]
    + deg["round 0 in the clean-context arm"]["n"],
    b0["adequate"], b0["n"], b0["pct"],
    pa["neutral_control"]["adequate"], pa["neutral_control"]["n"], pa["neutral_control"]["pct"],
    b2["adequate"], b2["n"], b2["pct"],
    b0["pct"], pa["gain_from_evidence_pts"],
    len(md), ("exactly zero in every one" if max(gaps) == 0 else "at most %.1f points" % max(gaps)),
    cmh.get("or_mh"), cmh.get("p"), (max(rates) - min(rates)) if rates else 0,
    cn_max, n_pair, min(c1s), max(c1s), min(bs), max(bs), maxp,
    syrows,
    ev["counts"].get("stable_correct", 0), ev["counts"].get("beneficial_correction", 0),
    ev["counts"].get("harmful_deference", 0), ev["counts"].get("no_improvement", 0),
    ev["HRR"]["pct"], ev["BCR"]["pct"],
    nc["counts"].get("stable_correct", 0), nc["counts"].get("beneficial_correction", 0),
    nc["counts"].get("harmful_deference", 0), nc["counts"].get("no_improvement", 0),
    nc["HRR"]["pct"], nc["BCR"]["pct"],
    min(hrrs), max(hrrs), min(c1s), max(c1s),
    sp["baseline"]["carbapenem"], sp["baseline"]["n"], sp["baseline"]["carbapenem_pct"],
    sp["baseline"]["distinct_drugs"],
    sp["neutral_control"]["carbapenem"], sp["neutral_control"]["n"],
    sp["neutral_control"]["carbapenem_pct"], sp["neutral_control"]["distinct_drugs"],
    sp["under_pressure"]["carbapenem"], sp["under_pressure"]["n"],
    sp["under_pressure"]["carbapenem_pct"], sp["under_pressure"]["distinct_drugs"],
    sp["panel_revealed"]["carbapenem"], sp["panel_revealed"]["n"],
    sp["panel_revealed"]["carbapenem_pct"], sp["panel_revealed"]["distinct_drugs"],
    sp["baseline"]["carbapenem_pct"], sp["under_pressure"]["carbapenem_pct"], b0["pct"],
    sp["panel_revealed"]["carbapenem_pct"], sp["panel_revealed"]["distinct_drugs"],
)
open(os.path.join(ROOT, "STORY.md"), "w").write(doc)
print("wrote STORY.md")
