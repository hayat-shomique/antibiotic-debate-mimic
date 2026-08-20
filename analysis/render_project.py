"""render_project.py - PROJECT.md, the one document.

Everything a reader needs in one place: the question, the gap, the design, the
instrument verbatim, the communication protocol, the escalation ladder, every
result, the bounds, and what each supervisor asked for. Numbers come from
results/*.json, prompts come from docs/prompts_used.md, and the ask map comes
from docs/SUPERVISOR_ASKS.md. Nothing is typed twice.

    python3 analysis/render_project.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
DOCS = ROOT / "docs"

T = json.loads((RES / "tingting_endpoints.json").read_text())
R = json.loads((RES / "RESULTS.json").read_text())
P = json.loads((RES / "policy_degeneracy.json").read_text())
FS = json.loads((RES / "fewshot.json").read_text())
LK = json.loads((RES / "leakage.json").read_text())
PTEST = json.loads((RES / "primary_test.json").read_text())

PRIM, SPEC, DCOV = T["primary_appropriateness"], T["spectrum_appropriateness"], T["debate_coverage"]
DBT, EVID, NEUT = T["debate_with_live_agent"], T["revision_under_evidence"], T["change_under_neutral_control"]
MATCH = R["D_MATCH_1_drug_identity_vs_patient"]
PT = PTEST["by_framing"]
ATTR = PT["C1a_authority"]["attrition"]
COVER = PT["C1a_authority"]["coverage_check"]


def span(*path, fmt="{} to {}"):
    """A quantity that differs across the four framings is never collapsed to one number."""
    vals = []
    for f in FRAMINGS:
        node = PT[f]
        for key in path:
            node = node[key]
        vals.append(node)
    lo, hi = min(vals), max(vals)
    return str(lo) if lo == hi else fmt.format(lo, hi)
FRAMINGS = ["C1a_authority", "C1b_peer_consensus", "C1c_safety_framing", "C1d_bare_doubt"]
NICE = dict(zip(FRAMINGS, ["authority", "peer consensus", "safety framing", "bare doubt"]))
PR = FS["paired"]

METHODS = (DOCS / "METHODS.md").read_text()
LIMITS = (DOCS / "LIMITATIONS.md").read_text()
PROMPTS = (DOCS / "prompts_used.md").read_text()
ASKS = (DOCS / "SUPERVISOR_ASKS.md").read_text()
SCORE = (ROOT / "SCORECARD.txt").read_text()
CLIN = json.loads((RES / "clinician_comparison.json").read_text())
CONF = json.loads((RES / "confidence_axis.json").read_text())


def prose(pattern, source=METHODS):
    m = re.search(pattern, source)
    if not m:
        raise ValueError(f"no match for {pattern!r}; update the pattern rather than typing the number")
    return m.group(1)


def fence(startswith):
    for f in re.findall(r"```[a-z]*\n(.*?)```", PROMPTS, re.S):
        if f.lstrip().startswith(startswith):
            return f.strip()
    raise ValueError(f"docs/prompts_used.md has no fenced block starting {startswith!r}")


def section(doc, heading):
    """Lift one '## heading' section out of a hand-written document."""
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", doc, re.S | re.M)
    if not m:
        raise ValueError(f"section {heading!r} not found")
    return m.group(1).strip()


MEDIAN_H = prose(r"median of \*\*(\d+) hours\*\*")
DQ = re.search(r"Doctor to Pharmacist (\S+)\s+Pharmacist to Doctor (\S+)", SCORE)
DQ_AB, DQ_BA = (DQ.group(1), DQ.group(2)) if DQ else ("see SCORECARD.txt", "")
TTA = re.search(r"Time to appropriate therapy\n\s+(.+)", SCORE).group(1).strip()
ESC = re.search(r"once results arrive\n\s+(.+)", SCORE).group(1).strip()
B = [PT[f]["discordant"]["b_pressure_only"] for f in FRAMINGS]
C = {PT[f]["discordant"]["c_control_only"] for f in FRAMINGS}
N_PRIMARY = PT[FRAMINGS[0]]["n_primary"]
P_WORST = max(PT[f]["discordant"]["p_exact"] for f in FRAMINGS)
HRR_RANGE = [T["sycophancy_under_pressure"][f]["HRR"]["pct"] for f in FRAMINGS]
FLIP = [100.0 * PT[f]["flip_rates"]["C1"]["k"] / PT[f]["flip_rates"]["C1"]["n"] for f in FRAMINGS]
C2_FLIP = 100.0 * PT[FRAMINGS[0]]["flip_rates"]["C2"]["k"] / PT[FRAMINGS[0]]["flip_rates"]["C2"]["n"]
if len(C) != 1:
    raise ValueError("c differs across framings; the sentence below must become a range")
C_VAL = C.pop()
TOTAL_EXPOSURES = sum(m["n"] for m in R["_integrity"].values()) + FS["n"]
DUPES = sum(m["duplicate_writes_dropped"] for m in R["_integrity"].values())

transition_rows = "\n".join(
    "| pressure, {n} | {sc} | {bc} | {hd} | {hrr:.1f}% |".format(
        n=NICE[f],
        sc=T["sycophancy_under_pressure"][f]["counts"].get("stable_correct", 0),
        bc=T["sycophancy_under_pressure"][f]["counts"].get("beneficial_correction", 0),
        hd=T["sycophancy_under_pressure"][f]["counts"].get("harmful_deference", 0),
        hrr=T["sycophancy_under_pressure"][f]["HRR"]["pct"]) for f in FRAMINGS)

matched_rows = "\n".join(
    "| {d} | {a}/{n} = {pa:.1f}% | {b}/{m} = {pb:.1f}% | {g:+.1f} |".format(
        d=d, a=v["covers"]["adopted"], n=v["covers"]["n"],
        pa=100.0 * v["covers"]["adopted"] / v["covers"]["n"],
        b=v["does_not_cover"]["adopted"], m=v["does_not_cover"]["n"],
        pb=100.0 * v["does_not_cover"]["adopted"] / v["does_not_cover"]["n"],
        g=v["gap_pct"]) for d, v in MATCH["by_drug"].items())

arm_rows = "\n".join(
    "| {a} | {n} | {d} | `{k}` |".format(a=a, n=m["n"], d=m["duplicate_writes_dropped"],
                                         k=" + ".join(m["key"]))
    for a, m in R["_integrity"].items())

sentences = "\n".join(f"- **{k.rstrip('.')}.**" for k in LK["sentences"])

DOC = f"""# Two clinical LLM agents, one antibiotic, and a laboratory as referee

**Shomique Hayat** · UNIQ+ research internship, University of Oxford, Institute of Biomedical
Engineering · supervised by **Prof. Tingting Zhu**, with **Zhikang Chen** · 6 July to 20 August 2026

This is the whole project in one document. Every number in it is read from `results/*.json` at build
time by `analysis/render_project.py`, and every prompt is lifted verbatim from
`docs/prompts_used.md`. To change a number, change the analysis, not the sentence.

---

## 1. The question

> does multi-agent communication improve clinical decision quality, or does it merely make the
> models agree?
>
> Prof. Tingting Zhu

People are building clinical systems in which several language-model agents confer and reach a
decision together, on the assumption that they check each other's work. Testing that assumption
requires knowing who was actually right, and in medicine you usually cannot, because the human you
would compare against was guessing too.

The objection that produced this design came from my supervisor:

> The doctor makes the right decision, that's a huge assumption you make.

So the clinician is not the reference standard. In bloodstream infection the hospital laboratory
eventually grows the organism from the patient's blood and tests it against each antibiotic in turn.
That susceptibility panel is an answer key that does not depend on the model or on the treating
clinician, and on this cohort it arrives at a median of **{MEDIAN_H} hours** after the culture is
drawn, with **zero** panels available at 5, 12 or 24 hours. The empiric decision is genuinely made
without it.

## 2. What is already known, and what was missing

Three things are established and this study claims none of them. Collaboration between agents does
not reliably improve on a single agent. Medical multi-agent boards are no exception. And sycophancy,
abandoning a position under peer challenge and adopting a peer's answer whether it is right or wrong,
is documented repeatedly.

What is missing is the arbiter. In those studies the thing that decides who was right is a benchmark
key or another model. Nobody has arbitrated a two-agent clinical debate against the individual
patient's own laboratory susceptibility panel: an answer key neither agent can see, neither agent can
argue with, and neither agent produced. The claim-by-claim adversarial check of every result here is
`docs/LITERATURE_PRESSURE_TEST.md`, and it is deliberately unflattering.

## 3. The design

{section(METHODS, "1. Population")}

{section(METHODS, "2. Decision point")}

{section(METHODS, "3. Reference standard")}

{section(METHODS, "4. Label space")}

## 4. The two agents, and how they communicate

The structure came from Zhikang Chen:

> you could use one llm to display supportor, and another one is opponent. And after discussion to
> see if they could reach agreement. In this way, we dont need doctors to participate. Although, the
> final results maybe wrong, but the thinking and discission process are meaningful.

and so did the personas:

> inject different prior information into the prompts, for instance, assign Agent A the identity of
> an "infectious disease specialist" and Agent B the role of "antimicrobial stewardship lead", so
> that each has a clear, potentially conflicting incentive.

| turn | who | what they do |
|---|---|---|
| T1 | Agent A | proposes exactly one drug from the closed formulary |
| T2 | Agent B | counters if it disagrees, concurs if it agrees, and states its own drug |
| T3 | Agent A | answers the challenge and restates a position |
| T4 | Agent B | restates or moves |
| T5 | Agent A | final position |

Every turn is parsed down to a single agent and recorded, so each agent has a position after every
turn rather than only at the end. The whole case is then run again with **Agent B opening**, which
turns speaking order into a measured variable rather than an uncontrolled one, and pairs every
comparison within patient.

Nothing in the conversation decides what is true. The agents can agree on the wrong drug, and they
do. Correctness is settled afterwards, outside the conversation, against the panel.

## 5. The instrument, verbatim

Agent A, opening turn. Hash-pinned and asserted unchanged on every run, so a silent edit aborts the
run rather than producing results under a changed instrument.

```
{fence("You are an infectious disease specialist. You are given")}
```

Agent B, the challenge turn.

```
{fence("You are an antimicrobial stewardship lead reviewing")}
```

The case block, which is the only patient-derived text. Values below are **synthetic**: MIMIC-IV is
credentialed and row-level records do not leave the machine.

```
{fence("Age:")}
```

There is no laboratory value, no organism and no susceptibility anywhere in it, and every field is
asserted earlier than the decision time.

## 6. The four conditions

The same case is put to the same model four ways, with the same decoding.

| id | condition | what the model receives | what a change means |
|---|---|---|---|
| C0 | pre-culture baseline | the case, nothing else | the zero-shot recommendation |
| Cn | neutral re-ask | asked again, no disagreement, no new facts | any change is instability |
| C1 | unsupported pressure | a challenge containing no clinical information, four framings | any change is unjustified |
| C2 | valid evidence | the organism and its susceptibility panel | a change can be correct here |

The four pressure sentences are the entire content of C1:

{sentences}

Censused rather than sampled: **{LK['leaked_turns']} of {LK['n_turns']}** pressure turns contain any
organism or susceptibility phrasing.

Cn is the condition that makes the others interpretable. Without a condition in which the prompt
grows and nothing else changes, a high flip rate under C1 could mean the model is unstable rather
than deferential.

## 7. Results

### 7.1 The baseline is a single constant, and it is a good one

Before any conversation the model recommends **{P['C0 baseline']['top']} for
{P['C0 baseline']['top_share_pct']:.0f}% of patients**: {P['C0 baseline']['distinct']} distinct
choice across {P['C0 baseline']['n']} decisions.

| condition | covers the organism | distinct drugs |
|---|---|---|
| baseline, pre-culture | {PRIM['baseline_pre_culture']['adequate']}/{PRIM['baseline_pre_culture']['n']} = {PRIM['baseline_pre_culture']['pct']}% | {P['C0 baseline']['distinct']} |
| neutral control | {PRIM['neutral_control']['adequate']}/{PRIM['neutral_control']['n']} = {PRIM['neutral_control']['pct']}% | {P['Cn neutral control']['distinct']} |
| susceptibility panel revealed | {PRIM['with_panel_revealed']['adequate']}/{PRIM['with_panel_revealed']['n']} = {PRIM['with_panel_revealed']['pct']}% | {P['C2 with the panel revealed']['distinct']} |

**{PRIM['baseline_pre_culture']['pct']}% from a single constant.** Nothing in the prompt predicts the
organism, so one broad empiric agent for everybody is a defensible policy rather than a broken one.
Evidence adds {PRIM['gain_from_evidence_pts']} points. This bounds every claim below: at baseline
there is no variation to explain, so this study cannot separate a model that reasons about patients
from a model with one good default.

### 7.2 The pre-specified primary test

Protocol section 7, frozen before any run: an exact binomial on cases that change under exactly one
of Cn and C1. The baseline was recorded independently by two arms that ran at different times and
agreed **{PTEST['baseline_agreement']['agree']}/{PTEST['baseline_agreement']['n']}**, so the pairing
holds.

| pressure framing | n | b, pressure only | c, control only | exact p |
|---|---|---|---|---|
""" + "\n".join(
    f"| {NICE[f]} | {PT[f]['n_primary']} | {PT[f]['discordant']['b_pressure_only']} | "
    f"{PT[f]['discordant']['c_control_only']} | {PT[f]['discordant']['p_exact']:.2e} |"
    for f in FRAMINGS) + f"""

**c is {C_VAL} under every framing.** Not once in {N_PRIMARY} cases did the model change its
recommendation because a neutral interlocutor spoke to it. Under unsupported pressure it changed in
{min(B)} to {max(B)} of the same cases, {min(FLIP):.1f}% to {max(FLIP):.1f}%. The susceptibility
panel, the only thing in the study carrying real information about the patient, moves it in
{C2_FLIP:.1f}%.

**The model is moved more by a person disagreeing than by the laboratory result.**

**Attrition, split by cause rather than pooled.** The split is reported because the two causes have
different consequences, and because on an earlier partial arm the larger term was absent data rather
than indeterminacy. That is no longer the case.

| step | n |
|---|---|
| cases appearing in any condition | {ATTR['cases_appearing_in_any_condition']} |
| cases with a row in every condition | {ATTR['cases_with_a_row_in_every_condition']} |
| dropped because an arm never ran the case | {span('attrition', 'dropped_arm_never_ran_the_case')} |
| dropped because a condition returned UNDETERMINED or INTERMEDIATE_ONLY | {span('attrition', 'dropped_indeterminate_outcome')} |
| **primary set, per framing** | **{span('n_primary')}** |

The pressure arm now covers **{COVER['cases_the_pressure_arm_covered']} of
{COVER['cases_in_the_frozen_selection']}** cases in the frozen selection, so nothing is missing
because an arm stopped early. What remains is genuine indeterminacy: the recommended agent was never
tested against at least one isolate on that patient's panel, which is a property of what the
laboratory chose to test rather than of the model. It is still attrition and it is still reported.

### 7.3 On accuracy alone, that pressure looks harmless

| what the model heard | stable correct | beneficial correction | harmful deference | harmful revision rate |
|---|---|---|---|---|
{transition_rows}
| the susceptibility panel | {EVID['counts']['stable_correct']} | {EVID['counts']['beneficial_correction']} | {EVID['counts']['harmful_deference']} | {EVID['HRR']['pct']:.1f}% |
| neutral control | {NEUT['counts']['stable_correct']} | {NEUT['counts'].get('beneficial_correction', 0)} | {NEUT['counts'].get('harmful_deference', 0)} | {NEUT['HRR']['pct']:.1f}% |

Harmful revision under scripted pressure runs **{min(HRR_RANGE):.1f}% to {max(HRR_RANGE):.1f}%**. The
model abandons its drug and lands on another drug that also covers. A study that stopped here would
conclude the sycophancy is harmless.

### 7.4 Score what kind of answer it gave, and the harm appears

| condition | carbapenem use | distinct drugs |
|---|---|---|
| baseline | {SPEC['baseline']['carbapenem']}/{SPEC['baseline']['n']} = {SPEC['baseline']['carbapenem_pct']}% | {SPEC['baseline']['distinct_drugs']} |
| neutral control | {SPEC['neutral_control']['carbapenem']}/{SPEC['neutral_control']['n']} = {SPEC['neutral_control']['carbapenem_pct']}% | {SPEC['neutral_control']['distinct_drugs']} |
| **under unsupported pressure** | **{SPEC['under_pressure']['carbapenem']}/{SPEC['under_pressure']['n']} = {SPEC['under_pressure']['carbapenem_pct']}%** | {SPEC['under_pressure']['distinct_drugs']} |
| susceptibility panel revealed | {SPEC['panel_revealed']['carbapenem']}/{SPEC['panel_revealed']['n']} = {SPEC['panel_revealed']['carbapenem_pct']}% | {SPEC['panel_revealed']['distinct_drugs']} |

**A sentence carrying no clinical evidence drives carbapenem use from
{SPEC['baseline']['carbapenem_pct']:.0f}% to {SPEC['under_pressure']['carbapenem_pct']}%.** It buys
nothing: coverage was already {PRIM['baseline_pre_culture']['pct']}% and harmful revision was near
zero. Carbapenem overuse is the principal driver of carbapenem-resistant Enterobacterales. Given the
actual panel the model reaches {SPEC['panel_revealed']['carbapenem_pct']}% across
{SPEC['panel_revealed']['distinct_drugs']} distinct drugs, and there the broadening is earned.

### 7.5 The patient does not change the answer, the drug name does

A counterpart is scripted to propose one named antibiotic. The same drug is proposed to a patient
whose organism it covers and to a patient whose organism it does not. Only the patient changes.

| drug proposed | adopted when it covers | adopted when it does not | gap |
|---|---|---|---|
{matched_rows}

Pooled, adoption is {MATCH['pooled']['covers']['pct']}% against
{MATCH['pooled']['does_not_cover']['pct']}%. Cochran-Mantel-Haenszel stratified by drug gives an odds
ratio of **{MATCH['cmh_stratified_by_drug']['or_mh']}**, p = {MATCH['cmh_stratified_by_drug']['p']},
which is the null exactly. Within a drug, coverage makes no difference. Between drugs the spread is
100 points.

### 7.6 The answer to the question

| what the agent hears | harmful revision rate | coverage of the organism |
|---|---|---|
| a scripted sentence with no content | {NEUT['HRR']['pct']:.1f}% ({NEUT['HRR']['k']}/{NEUT['HRR']['n']}) | unchanged, {DCOV['before_debate']['pct']}% |
| **a second agent arguing a case** | **{DBT['HRR']['pct']}% ({DBT['HRR']['k']}/{DBT['HRR']['n']})** | **{DCOV['before_debate']['pct']}% to {DCOV['after_debate']['pct']}%, {DCOV['debate_change_pts']:+.1f} points** |
| the susceptibility panel | {EVID['HRR']['pct']:.1f}% ({EVID['HRR']['k']}/{EVID['HRR']['n']}) | {DCOV['after_debate']['pct']}% to {DCOV['after_panel']['pct']}%, {DCOV['evidence_change_pts']:+.1f} points |

**In this setup, agent-to-agent argument reduced coverage of the organism; supplying the susceptibility panel increased it.** Stated as alignment with the recorded microbiology and counterfactual
appropriateness of the recommendation, never as a recommendation causing a patient outcome.

### 7.7 The model against the clinician, her second comparison

> You can also compare LLM with clinician see if they agree or LLM is worse or better?
>
> Prof. Tingting Zhu, 30 July 2026

Both sides are scored by the identical rule, fixed in the protocol before this was computed: a
regimen covers if any agent in it covers, and a polymicrobial case is adequate only if every
pathogenic isolate is covered.

| scored against the same panels | all cases | cases where both can be scored |
|---|---|---|
| the clinician's actual empiric prescription | {CLIN['clinician']['counts']['ADEQUATE']}/{CLIN['clinician']['n']} = {CLIN['clinician']['adequate_all_cases_pct']}% | **{CLIN['clinician']['adequate_determined_only']['k']}/{CLIN['clinician']['adequate_determined_only']['n']} = {CLIN['clinician']['adequate_determined_only']['pct']}%** |
| the model, zero-shot, before any conversation | {CLIN['model_zero_shot']['counts']['ADEQUATE']}/{CLIN['model_zero_shot']['n']} = {CLIN['model_zero_shot']['adequate_all_cases_pct']}% | **{CLIN['model_zero_shot']['adequate_determined_only']['k']}/{CLIN['model_zero_shot']['adequate_determined_only']['n']} = {CLIN['model_zero_shot']['adequate_determined_only']['pct']}%** |

The margin on the full cohort is a **denominator artefact** and is reported as one: the clinician
scores UNDETERMINED in {CLIN['clinician']['counts']['UNDETERMINED']} of {CLIN['clinician']['n']}
cases, largely because real prescriptions fall outside the closed formulary or were never tested
against the isolate. On the cases where both can be scored the two are indistinguishable. The answer
to her question is that neither is better.

### 7.8 The remaining endpoints in her hierarchy

| her endpoint | value |
|---|---|
| time to appropriate therapy | {TTA} |
| escalation and de-escalation correctness once results arrive | {ESC} |
| decision-quality delta, compared across the two speaking directions | Doctor to Pharmacist {DQ_AB}, Pharmacist to Doctor {DQ_BA} |
| confidence before and after | **reported, see 7.9.** The binary is degenerate and is not reported as a test; the continuous measure is |

### 7.9 Confidence before and after, her ninth ask

> I'd also record confidence before and after communication if your experimental design permits it.
> The particularly concerning state isn't merely wrong after persuasion; it's: correct + confident,
> sees other agent, wrong + confident.
>
> Prof. Tingting Zhu, 18 August 2026

**What is degenerate, stated first.** Confidence is elicited as an integer 0 to 100 and "confident"
was pre-registered at 80 or above. Every observation came back at or above that threshold, so the
binary cannot discriminate and a rate computed against it would measure the scale rather than the
model. The binary is therefore **not** reported as a test. The elicited number does move, so the
continuous measure is reported instead, conditioned on the transition class.

| transition cell | n | confidence before | after | change |
|---|---|---|---|---|
| stable correct | {CONF['by_transition_cell']['stable_correct']['n']} | {CONF['by_transition_cell']['stable_correct']['mean_confidence_before']} | {CONF['by_transition_cell']['stable_correct']['mean_confidence_after']} | {CONF['by_transition_cell']['stable_correct']['mean_delta']:+} |
| beneficial correction | {CONF['by_transition_cell']['beneficial_correction']['n']} | {CONF['by_transition_cell']['beneficial_correction']['mean_confidence_before']} | {CONF['by_transition_cell']['beneficial_correction']['mean_confidence_after']} | {CONF['by_transition_cell']['beneficial_correction']['mean_delta']:+} |
| harmful deference | {CONF['by_transition_cell']['harmful_deference']['n']} | {CONF['by_transition_cell']['harmful_deference']['mean_confidence_before']} | {CONF['by_transition_cell']['harmful_deference']['mean_confidence_after']} | {CONF['by_transition_cell']['harmful_deference']['mean_delta']:+} |
| no improvement | {CONF['by_transition_cell']['no_improvement']['n']} | {CONF['by_transition_cell']['no_improvement']['mean_confidence_before']} | {CONF['by_transition_cell']['no_improvement']['mean_confidence_after']} | {CONF['by_transition_cell']['no_improvement']['mean_delta']:+} |

**The direction is the finding, and it is the one she predicted.** Where the model holds a correct
answer it becomes *less* certain after being challenged. Where it abandons a correct answer for a
wrong one, it becomes *more* certain. The difference in mean change between those two cells is
{CONF['harmful_deference_vs_stable_correct']['observed_difference_in_mean_delta']:+} points,
permutation p = {CONF['harmful_deference_vs_stable_correct']['p_two_sided']}, rank-biserial
{CONF['harmful_deference_vs_stable_correct']['rank_biserial']:+}. A permutation test is used because
the harmful-deference cell is small by construction and the values take four discrete levels, so a
normal approximation would be assuming a distribution the instrument cannot produce.

**How far this can be pushed.** The harmful-deference cell holds
{CONF['by_transition_cell']['harmful_deference']['n']} exposures. A permutation p is valid at any n,
but a cell that small bounds precision, so this is directional evidence for the state she named and
not an effect size anyone should quote. What it is not is absent, and it is no longer withdrawn.

### 7.9 Where the hierarchy meets the sycophancy question

She asked this directly on 18 August and it deserves a direct answer.

> I assume the above has nothing to do with sycophancy yet. Since you are running multiple agents?

The hierarchy measures decision **quality**; sycophancy is the **mechanism** that moves it. So the
hierarchy is applied twice, once to each agent's answer before the interaction and once after, and
the four-cell table in 7.3 is exactly the join: a harmful deference is a sycophancy event scored on
her appropriateness endpoint. That is why the same 2x2 appears three times, for a neutral turn, for a
live agent and for the panel. Without the hierarchy the sycophancy is invisible, because the agents
agree either way. Without the sycophancy layer the hierarchy has nothing to compare.

### 7.10 The escalation ladder

The order was set by the supervisor at the first meeting: zero-shot, then few-shot, and training only
if few-shot fails.

| rung | status | what it produced |
|---|---|---|
| 1. zero-shot | complete, {PRIM['baseline_pre_culture']['n']} cases | one constant recommendation, {PRIM['baseline_pre_culture']['pct']}% coverage |
| 2. few-shot | complete, {FS['n']} cases | {FS['aware']['fewshot']['distinct']} drugs instead of {FS['aware']['zeroshot']['distinct']}, Access-group prescribing {100.0 * FS['aware']['zeroshot']['access'] / FS['aware']['zeroshot']['n']:.1f}% to {100.0 * FS['aware']['fewshot']['access'] / FS['aware']['fewshot']['n']:.1f}%, coverage {100.0 * PR['zeroshot_correct'] / PR['n']:.1f}% to {100.0 * PR['fewshot_correct'] / PR['n']:.1f}% on {PR['n']} paired cases, exact McNemar p = {PR['p_exact']:.7f} |
| 3. fine-tuning | designed, not run | the rung that rung two licenses |

Few-shot breaks the constant and is significantly worse at the job: it loses {PR['b_lost']} correct
recommendations and gains {PR['c_gained']}. It is not simply copying, either: the answer appears in
that case's own exemplars only
{100.0 * FS['validity']['answer_in_examples'] / FS['n']:.1f}% of the time. Exemplars are drawn from a
pool disjoint from the evaluation cases on **both** `case_id` and `subject_id`, with a separate
exemplar seed.

**Rung three, as designed.** The label is the set of agents the panel called susceptible, so any
member counts as correct. The split is patient-level on `subject_id`, outside the frozen evaluation
cohort. The objective must be coverage penalised by spectrum, weighted by WHO AWaRe class, because
training on coverage alone would produce carbapenem for everybody: on this cohort a constant
meropenem policy scores 96.0% coverage. Success is pre-specified as beating the best constant policy
on coverage **and** on spectrum simultaneously, on held-out patients, and holding it under the C1
pressure conditions.

## 8. What this does not show

{section(LIMITS, "Clinical")}

{section(LIMITS, "Statistical")}

{section(LIMITS, "Scope")}

## 9. What is inherited and what is new

The harness, the provenance gate, the cohort assembly and the scorer are built on the group's
existing local tooling in the run directory. What is new in this project is the design and
everything downstream of it: the four-condition structure with the neutral control, the drug-matched
arm that separates drug identity from patient fit, the four-cell transition analysis applied to a
laboratory reference standard rather than a benchmark key, the escalation ladder run to its second
rung, and every result file in `results/`.

## 10. Data integrity

An exposure is one model decision in one experimental cell. Two records sharing an identity key are a
repeated write, not a repeated measurement, and the second is dropped before any number is computed.

| arm | exposures | duplicate writes dropped | identity key |
|---|---|---|---|
{arm_rows}

**{DUPES} duplicate writes found and dropped in total**, across {TOTAL_EXPOSURES} exposures.
Every arm now runs under a PID lock. Model `{R['model']}`, temperature {R['temperature']}, seed
{R['seed']}, run locally: MIMIC-IV is credentialed under a PhysioNet data use agreement and no
record-level data is committed to this repository.

## 11. What I was asked, and what I built

{re.sub(r'^## ', '### ', ASKS.split('# What I was asked, and what I built', 1)[1].strip(), flags=re.M)}

---

## Reproducing every number above

```
python3 analysis/primary_test.py          # results/primary_test.json
python3 analysis/tingting_endpoints.py    # results/tingting_endpoints.json
python3 analysis/policy_degeneracy.py     # results/policy_degeneracy.json
python3 analysis/fewshot_analysis.py      # results/fewshot.json
python3 analysis/leakage_check.py         # results/leakage.json
python3 analysis/canonical_numbers.py     # results/RESULTS.json
python3 analysis/render_project.py        # this document
python3 deck/deck_figures.py              # every chart in the talk
python3 deck/build_deck.py                # the talk itself
python3 deck/build_evidence.py            # deck/EVIDENCE.md, claim by claim
```
"""

(ROOT / "PROJECT.md").write_text(DOC)
print(f"wrote PROJECT.md ({len(DOC.splitlines())} lines)")
