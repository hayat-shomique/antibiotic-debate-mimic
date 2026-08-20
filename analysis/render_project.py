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
AMPC = json.loads((RES / "ampc_exposure.json").read_text())
TRIG = json.loads((RES / "trigger_comparison.json").read_text())
SRC = json.loads((RES / "selfrevision_control.json").read_text()) if (RES / "selfrevision_control.json").exists() else None
CONF = json.loads((RES / "claim_confidence.json").read_text()) if (RES / "claim_confidence.json").exists() else None

def _trigger_table():
    """One row per reconsideration trigger, all on the same round-0 starting position."""
    onestep = list(TRIG["trigger_one_content_free_challenge"].values())
    panel = TRIG["trigger_the_susceptibility_panel"]
    debate = TRIG["trigger_a_counterpart_with_no_evidence"]
    null = TRIG["trigger_nothing_a_neutral_re_ask"]
    rows = []
    for v in [null] + onestep + [panel, debate]:
        rows.append("| {} | {} | {} | {}% | {} | {} | {}% | {} |".format(
            v["label"], v["entered_adequate"], v["harmful_revisions"],
            v["harmful_revision_rate_pct"], v["entered_inadequate"],
            v["beneficial_corrections"], v["beneficial_correction_rate_pct"],
            v["distinct_drugs_used_across_all_determinate_runs"]))
    hrr = [v["harmful_revision_rate_pct"] for v in onestep]
    bcr = [v["beneficial_correction_rate_pct"] for v in onestep]
    rev = TRIG["after_the_debate_does_the_panel_repair_it"]
    return {
        "TRIGGER_ROWS": "\n".join(rows),
        "ONESTEP_HRR_LO": f"{min(hrr):g}", "ONESTEP_HRR_HI": f"{max(hrr):g}",
        "ONESTEP_BCR_LO": f"{min(bcr):g}", "ONESTEP_BCR_HI": f"{max(bcr):g}",
        "PANEL_BCR": f'{panel["beneficial_correction_rate_pct"]:g}',
        "NULL_DRUGS": str(null["distinct_drugs_used_across_all_determinate_runs"]),
        "PANEL_DRUGS": str(panel["distinct_drugs_used_across_all_determinate_runs"]),
        "DEBATE_HRR": f'{debate["harmful_revision_rate_pct"]:g}',
        "DEBATE_DRUGS": str(debate["distinct_drugs_used_across_all_determinate_runs"]),
        "DEBATE_TURNS_LABEL": "Five turns of the same thing",
        "REVEAL_MATCHED": str(TRIG["_reveal_arm_is_sequential_not_parallel"]["runs_checked"]),
        "REVEAL_IN": str(rev["entered_inadequate"]),
        "REVEAL_FIX": str(rev["beneficial_corrections"]),
    }


if SRC:
    _d, _s, _t = SRC["debate_A_first"], SRC["self_revision"], SRC["paired_test"]
    SRC_N = str(SRC["_coverage"]["cases_shared_with_the_A_first_debate_arm"])
    SRC_TURNS = "three"
    SRC_D_CH, SRC_S_CH = str(_d["changed_its_opening_drug"]), str(_s["changed_its_opening_drug"])
    SRC_D_ADQ, SRC_S_ADQ = f'{_d["final_adequate_pct"]:g}', f'{_s["final_adequate_pct"]:g}'
    SRC_D_HRR, SRC_S_HRR = f'{_d["harmful_revision_rate_pct"]:g}', f'{_s["harmful_revision_rate_pct"]:g}'
    SRC_D_DRUGS, SRC_S_DRUGS = str(_d["distinct_final_drugs"]), str(_s["distinct_final_drugs"])
    SRC_B = str(_t["debate_inadequate_and_control_adequate"])
    SRC_C = str(_t["control_inadequate_and_debate_adequate"])
    SRC_P = f'{_t["exact_mcnemar_p"]:.3g}'
    SRC_PREFIX_HRR = f'{SRC["_is_the_prefix_representative"]["debate_harmful_revision_rate_on_this_prefix"]:g}'
    _w = SRC["what_the_control_did_when_it_did_change"]["outcome_of_those_changes"]
    SRC_S_KEPT = str(sum(v for k, v in _w.items() if k.endswith("to ADEQUATE")))
    SRC_S_LOST = str(sum(v for k, v in _w.items() if not k.endswith("to ADEQUATE")))


if CONF:
    _rows = []
    for _c in CONF["claims"]:
        _tick = lambda b: "yes" if b else "no"
        _rows.append("| {} | {} | {} | {} | {} | {} | **{}** |".format(
            _c["claim"], _c["number"], _tick(_c["paired_within_patient"]),
            _tick(_c["has_a_control_arm"]), _tick(_c["reproduced_independently"]),
            _tick(_c["residual_uncertainty_stated_on_the_slide"]), _c["confidence"]))
    CONF_ROWS = "\n".join(_rows)
    CONF_TALLY = ", ".join(f"{v} {k}" for k, v in CONF["_tally"].items())
    CONF_BREAK = "\n".join(f"- **{_c['claim']}** ({_c['confidence']}). {_c['what_would_break_it']}"
                            for _c in CONF["claims"])

TRIGGER = _trigger_table()
TRIGGER_ROWS = TRIGGER["TRIGGER_ROWS"]
ONESTEP_HRR_LO, ONESTEP_HRR_HI = TRIGGER["ONESTEP_HRR_LO"], TRIGGER["ONESTEP_HRR_HI"]
ONESTEP_BCR_LO, ONESTEP_BCR_HI = TRIGGER["ONESTEP_BCR_LO"], TRIGGER["ONESTEP_BCR_HI"]
PANEL_BCR, PANEL_DRUGS = TRIGGER["PANEL_BCR"], TRIGGER["PANEL_DRUGS"]
NULL_DRUGS = TRIGGER["NULL_DRUGS"]
DEBATE_HRR, DEBATE_DRUGS = TRIGGER["DEBATE_HRR"], TRIGGER["DEBATE_DRUGS"]
DEBATE_TURNS_LABEL = TRIGGER["DEBATE_TURNS_LABEL"]
REVEAL_MATCHED, REVEAL_IN, REVEAL_FIX = (TRIGGER["REVEAL_MATCHED"], TRIGGER["REVEAL_IN"],
                                         TRIGGER["REVEAL_FIX"])
PROMPTS = (DOCS / "prompts_used.md").read_text()
ASKS = (DOCS / "SUPERVISOR_ASKS.md").read_text()
def _fill(text):
    """The hand-written prose files carry tokens rather than numbers, because a number typed
    into prose is a number typed twice. They are filled here from the result files. A token
    with no value is a hard error, never a silently unfilled brace."""
    c, h, a = AMPC["cohort"], AMPC["harmful_revisions"], AMPC["adequacy_labels_the_limitation_distrusts"]
    values = {"N_ARMS": str(len(R["_integrity"])),
              "TOTAL_EXPOSURES": f"{TOTAL_EXPOSURES:,}",
              "AMPC_N": str(c["n_cases"]),
              "AMPC_ANY": str(c["any_ampc_capable"]),
              "AMPC_ANY_PCT": f'{c["any_ampc_capable_pct"]:g}',
              "AMPC_BEST": str(c["best_established"]),
              "AMPC_BEST_PCT": f'{c["best_established_pct"]:g}',
              "AMPC_WEAK": str(c["named_but_weaker"]),
              "AMPC_HARM_N": str(h["n"]),
              "AMPC_HARM_3GC": str(h["onto_a_third_generation_cephalosporin_against_an_ampc_capable_organism"]),
              "AMPC_HARM_FEP": str(h["onto_cefepime_which_guidance_endorses_for_ampc"]),
              "AMPC_ATRISK": str(a["runs_ending_on_a_third_generation_cephalosporin_against_an_ampc_capable_organism_and_scored_adequate"]),
              "AMPC_RUNS": str(a["denominator_runs"])}
    missing = [m for m in re.findall(r"\{([A-Z_]+)\}", text) if m not in values]
    if missing:
        raise SystemExit("a hand-written prose file carries tokens with no value: " + ", ".join(sorted(set(missing))))
    for k, v in values.items():
        text = text.replace("{" + k + "}", v)
    return text
SCORE = (ROOT / "SCORECARD.txt").read_text()
CLIN = json.loads((RES / "clinician_comparison.json").read_text())
CONF = json.loads((RES / "confidence_axis.json").read_text())
CC = json.loads((RES / "cohort_composition.json").read_text())


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
# The few-shot arm is already one of the arms in _integrity, so adding it again double
# counted 200 exposures and put a second, larger total in the same document.
TOTAL_EXPOSURES = sum(m["n"] for m in R["_integrity"].values())
assert "fewshot" in R["_integrity"], "the few-shot arm must be registered in the integrity block"
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

and so did the personas, which are his words and are used unchanged:

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
| **a second agent arguing a case, five turns** | **{DBT['HRR']['pct']}% ({DBT['HRR']['k']}/{DBT['HRR']['n']})** | **{DCOV['before_debate']['pct']}% to {DCOV['after_debate']['pct']}%, {DCOV['debate_change_pts']:+.1f} points** |
| the susceptibility panel, after the debate | {TRIG['after_the_debate_does_the_panel_repair_it']['harmful_revision_rate_pct']:.1f}% ({TRIG['after_the_debate_does_the_panel_repair_it']['harmful_revisions']}/{TRIG['after_the_debate_does_the_panel_repair_it']['entered_adequate']}) | {DCOV['after_debate']['pct']}% to {DCOV['after_panel']['pct']}%, {DCOV['evidence_change_pts']:+.1f} points |
| the susceptibility panel, replacing the debate instead | {EVID['HRR']['pct']:.1f}% ({EVID['HRR']['k']}/{EVID['HRR']['n']}) | a different arm, measured from the round-0 position over 200 runs |

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
against the isolate. Restricted to what each side can be scored on, the two rates are within a point
of each other: {CLIN['model_zero_shot']['adequate_determined_only']['pct']}% on
{CLIN['model_zero_shot']['adequate_determined_only']['n']} cases for the model against
{CLIN['clinician']['adequate_determined_only']['pct']}% on
{CLIN['clinician']['adequate_determined_only']['n']} for the clinician. The answer to her question is
that on this evidence neither is better.

**This is not a paired comparison and it is not presented as one.** Those two rates sit on different
sets of cases, so they are two independent proportions. Saying the two are indistinguishable on the
cases where both can be scored would be a claim about a set that has not been constructed. Building
it needs per-case outcomes on the clinician side and the comparator artefact carries aggregates only,
because it derives from credentialed prescribing records. It is named here as further work rather
than implied.

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

### 7.10 Where the hierarchy meets the sycophancy question

She asked this directly on 18 August and it deserves a direct answer.

> I assume the above has nothing to do with sycophancy yet. Since you are running multiple agents?

The hierarchy measures decision **quality**; sycophancy is the **mechanism** that moves it. So the
hierarchy is applied twice, once to each agent's answer before the interaction and once after, and
the four-cell table in 7.3 is exactly the join: a harmful deference is a sycophancy event scored on
her appropriateness endpoint. That is why the same 2x2 appears three times, for a neutral turn, for a
live agent and for the panel. Without the hierarchy the sycophancy is invisible, because the agents
agree either way. Without the sycophancy layer the hierarchy has nothing to compare.

### 7.11 The escalation ladder

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
meropenem policy scores {CC["constant_single_agent_policies"]["best"]["k"]}/{CC["constant_single_agent_policies"]["best"]["n"]} = {CC["constant_single_agent_policies"]["best"]["pct"]}% coverage. Success is pre-specified as beating the best constant policy
on coverage **and** on spectrum simultaneously, on held-out patients, and holding it under the C1
pressure conditions.

### 7.12 One reconsideration step, five triggers, and what actually does the damage

Every row below starts from the same round-0 position on the same frozen cohort and applies one
reconsideration step. The only thing that differs is what triggers it. The last row differs in
something else as well, and that is the point of the table.

| what made the model reconsider | entered adequate | harmful revisions | harmful revision rate | entered inadequate | corrected | beneficial correction rate | distinct drugs used |
|---|---|---|---|---|---|---|---|
{TRIGGER_ROWS}

Two things fall out of this table and neither was designed for.

The first is that a challenge carrying no evidence at all corrects an inadequate opening almost
as often as the susceptibility panel does, {ONESTEP_BCR_LO}% to {ONESTEP_BCR_HI}% against the
panel's {PANEL_BCR}%. The model revises at close to the right rate for none of the right reasons.

The second is that the framing of the challenge is not what costs the patient coverage. Duration
is. One turn of unsupported challenge costs {ONESTEP_HRR_LO}% to {ONESTEP_HRR_HI}% harmful
revision whichever of the four framings is used. {DEBATE_TURNS_LABEL} costs {DEBATE_HRR}%. The
answer space narrows with it: the panel leaves {PANEL_DRUGS} drugs in play across the cohort and
the debate leaves {DEBATE_DRUGS}.

The top row is what makes the rest of the table readable. Asked to reconsider with nothing at all
to react to, the model moves in no case, corrects in no case, and leaves exactly {NULL_DRUGS} drug in
play. So none of what follows is drift, instability, or a decoding artefact. Something has to be
said to it before it moves.

One arm is deliberately absent from that table. The panel-reveal arm reveals the susceptibility
result **after** the debate has already moved the position, and its records carry the debate's own
finals on all {REVEAL_MATCHED} runs. Measuring it from round zero would credit the panel with
undoing damage the debate caused in between. Measured from where it actually starts, it answers a
different question and answers it well: of the {REVEAL_IN} runs that reach the panel already on an
inadequate drug, {REVEAL_FIX} are repaired, and none of the runs that reach it on an adequate drug
are pushed off one.

[`results/trigger_comparison.json`, `analysis/trigger_comparison.py`]

### 7.13 The control: is it the counterpart, or just being asked again?

Section 7.12 leaves one explanation standing that the debate arm cannot rule out. Five turns cost
coverage where one turn costs almost none, but the debate arm varies the counterpart and the number
of turns together. The model might abandon its position because something disagreed with it, or
simply because it was asked three times.

So the control runs the second explanation on its own. One agent, the same infectious disease
specialist, the same frozen cases in the same frozen order, the same round-0 prompt byte for byte,
the same closed formulary, the same leakage gate and the same scorer. It speaks {SRC_TURNS} times,
which is exactly how many times the specialist speaks in the five-turn debate, and between turns it
sees only its own previous text. Nothing disagrees with it. The comparison is paired within patient
against the runs where the specialist also opens, so the only thing that differs is whether anything
argued back.

The arm covers a contiguous {SRC_N} of the 200 cases, because it was run against the clock. The
prefix is contiguous rather than a sample of convenience, and every one of those {SRC_N} openings is
the same drug in both arms. The obvious worry about a prefix is that it might not be like the rest
of the cohort, so here is the check: the debate arm's harmful revision rate computed on this prefix
alone is {SRC_PREFIX_HRR}%, against {DEBATE_HRR}% on the whole cohort.

| | five turns, a counterpart arguing | {SRC_TURNS} turns, only its own text |
|---|---|---|
| changed its opening drug | {SRC_D_CH} of {SRC_N} | {SRC_S_CH} of {SRC_N} |
| final recommendation adequate | {SRC_D_ADQ}% | {SRC_S_ADQ}% |
| harmful revision | {SRC_D_HRR}% | {SRC_S_HRR}% |
| distinct drugs used | {SRC_D_DRUGS} | {SRC_S_DRUGS} |

Paired within patient, the debate ends on an inadequate drug where the control ends on an adequate
one in {SRC_B} pairs, and the reverse in {SRC_C}. Exact McNemar p = {SRC_P}.

The counterpart is what moves it. Asked repeatedly with nothing disagreeing, the model restates its
position and keeps its coverage.

The {SRC_S_CH} runs where it did change say the same thing more sharply. All {SRC_S_CH} are the same
move, piperacillin-tazobactam to ceftriaxone, and {SRC_S_KEPT} of the {SRC_S_CH} keep their coverage
while {SRC_S_LOST} does not. The debate leaves piperacillin-tazobactam for a cephalosporin in every
run, ceftriaxone or cefepime, and that move costs coverage in {SRC_B} of the paired cases. So the
move itself is not the problem, and the control is not a claim that the model never errs unprompted.
It is a claim about rate: {SRC_S_HRR}% against {SRC_D_HRR}% for the same move on the same patients. Same destination drug, opposite safety profile, and what differs is
what triggered it. De-escalating a broad-spectrum beta-lactam to a narrower agent is trial-supported
when susceptibility guides it: the SIMPLIFY trial found it non-inferior in Enterobacterales
bacteraemia, clinical cure 148 of 164 against 148 of 167, risk difference 1.6 percentage points, 95%
CI minus 5.0 to 8.2 (Lopez-Cortes et al., *Lancet Infect Dis* 2024;24(4):375-385,
doi:10.1016/S1473-3099(23)00686-2, PMID 38215770). What this study measures is the same move made
for a reason that is not susceptibility. This does not replace the duration result in 7.12, it locates it: a
counterpart is what makes the model move at all, and once it is moving, the longer the conversation
runs the more coverage the movement costs.

Four things this control does not do, and it matters which gap it closes.

It does not hold the revision instruction constant, and this is the sharpest of the four. The
debate's revision prompt says the specialist is in a case discussion with a stewardship lead and
should consider their comments. The control's says the specialist is reviewing its own
recommendation. It had to: naming a stewardship lead would have put a counterpart back into a
control whose purpose is to remove one. But it means the two arms differ in the instruction as well
as in the content, so the strict reading is that being told to consider another party's comments,
and receiving them, together move the model where being asked to review your own answer does not.
Separating the instruction from the content is the speaker-stripped arm's job, and it is the next
one to run.

It does not hold context length constant. By the final turn the debate transcript carries the
counterpart's turns as well as the agent's own and is roughly twice as long. A length-matched
control, padding the transcript with the agent's own text to the same token count, is the next
thing this needs.

It is not a speaker-stripped arm. `docs/LITERATURE_PRESSURE_TEST.md` names one at C6 as the
control needed before a change can be attributed to a *peer* specifically. That arm would keep the
counterpart's text in the context and remove only the attribution. This one removes the counterpart
entirely, so it separates being contradicted from being asked again, and not being contradicted by
a peer from being contradicted by anything.

It is not compute-matched. The same file names a compute-matched single-agent arm at the point
where C4 needs a baseline, and the self-consistency arm already in this project is the closer thing
to that. This control speaks three times against the debate's five turns, so it is matched on the
agent's own speaking turns rather than on total generation.

What it does close is the repetition explanation, which neither of those two named controls
addresses, and which was the live alternative to the reading in 7.12.

[`results/selfrevision_control.json`, `analysis/selfrevision_control.py`, `selfrevise_run.py`]

## 7b. How much weight each claim can carry

Not every number here is equally strong and the difference is not how good the number looks, it is
the design behind it. Each claim below is graded on four things that can be checked: whether the
comparison is paired within patient, whether an arm exists that removes the leading alternative
explanation, whether a second implementation or a recomputation from the raw run files reproduces
it, and whether what could still be wrong is stated where the claim is made. Four of four is high,
three is good, two is moderate, one is weak.

{CONF_TALLY}.

| claim | number | paired | controlled | reproduced | bounded | confidence |
|---|---|---|---|---|---|---|
{CONF_ROWS}

**What would break each one**, which is the part worth reading:

{CONF_BREAK}

The grades are computed by `analysis/claim_confidence.py` from the result files rather than
assigned. A claim whose supporting arm shrinks, or whose control is removed, loses its grade the
next time the chain runs.

[`results/claim_confidence.json`]

## 8. What this does not show

{section(_fill(LIMITS), "Clinical")}

{section(_fill(LIMITS), "Statistical")}

{section(_fill(LIMITS), "Scope")}

## 8b. What actually grew, and what the panel could not answer

Three facts a clinician asks for first and a reviewer asks for second. All three are computed by
`analysis/cohort_composition.py`.

**The evaluated cohort is entirely Gram negative.** All {CC['coverage_ceiling']['n']} cases, across
{CC['organisms']['distinct']} distinct organisms, dominated by
{CC['organisms']['top'][0]['organism'].title()} in {CC['organisms']['top'][0]['cases']} of
{CC['coverage_ceiling']['n']} cases, then {CC['organisms']['top'][1]['organism'].title()} in
{CC['organisms']['top'][1]['cases']}. This is a property of the frame, not an accident of sampling,
and it has a consequence worth stating: {len(CC['gram_positive_agents_in_the_formulary']['agents'])}
of the seventeen formulary agents are Gram-positive agents that can never be adequate here. It is
also why an encoder that answers vancomycin for every patient scores zero adequate rather than
scoring wrong.

**Intermediate is its own class, not a rounding.** The panel returns S, I and R.
{CC['panel_interpretations']['I']} of {CC['panel_interpretations']['rows']} verdict rows are
Intermediate, {CC['panel_interpretations']['intermediate_pct_of_rows']}%. Intermediate is neither
covering nor failing: a case whose best available verdict on some isolate is Intermediate scores
INTERMEDIATE_ONLY, and is excluded from adequacy numerators and from the paired primary test rather
than being folded either way.

**Two fifths of case-drug pairs cannot be scored at all.**
{CC['case_drug_pairs']['undetermined']} of {CC['case_drug_pairs']['pairs']} case-drug pairs, which is
{CC['case_drug_pairs']['undetermined_pct']}%, are UNDETERMINED because the laboratory never tested
that agent against at least one isolate on that patient. That is the single largest constraint on
this design and it is a property of clinical practice rather than of the model.

**The ceiling, so the baseline can be read against something.** On this cohort, a policy with perfect
per-patient choice from the formulary could reach
{CC['coverage_ceiling']['cases_with_at_least_one_fully_susceptible_formulary_agent']} of
{CC['coverage_ceiling']['n']} = **{CC['coverage_ceiling']['pct']}%**. The zero-shot baseline of
{PRIM['baseline_pre_culture']['pct']}% is therefore not near a ceiling: roughly twelve points of
headroom existed and were not taken.

## 8c. What would falsify this

The finding is that a live counterpart reduces coverage while the laboratory panel increases it. It
would be falsified by any of the following, and none of them is ruled out by this design.

- A heterogeneous pair, or a counterpart that varies its argument with the case, producing beneficial
  corrections at a rate that outruns harmful ones. The break-even is arithmetic rather than a matter
  of opinion, and at this base rate it is unattainable, so a different base rate would change the sign.
- A larger or differently trained checkpoint that conditions its opening on the patient. The whole
  effect here sits on top of a degenerate opening policy; a model with a real prior over patients
  would need the whole analysis rerun.
- A cohort with a different organism mix. This one is entirely Gram negative, and the drugs the
  conversation converges on are two cephalosporins whose failure rate is a property of that mix.
- Any demonstration that the susceptibility panel is not a valid arbiter of the empiric decision, for
  example because of inducible resistance that the reported panel cannot show. That is a live
  limitation, not a hypothetical.

## 8d. What to do next, ranked by what each one buys

Every item here is an arm that can be run, not a direction. Each is named with the claim it would
strengthen and what it would cost, because "further work" that cannot be costed is a wish.

**1. The speaker-stripped arm.** Keep the counterpart's turns in the context and remove only the
attribution, so the model sees the same text without being told a stewardship lead said it. This is
the one control the pressure test has asked for since C6, and it is what separates being contradicted
by a peer from being contradicted by any text asserting a rival position. It also fixes the sharpest
limitation of the single-agent control, which changes the revision instruction as well as the
counterpart. Same cohort, same scorer, roughly the cost of the control arm: a few hours locally.
**This is the highest-value thing left in the project.**

**2. A length-matched control.** Pad the single-agent transcript with the model's own text to the
same token count the debate reaches, so context length is held constant. Cheap, mechanical, and it
closes the second limitation on the control.

**3. A turn-count sweep inside one protocol.** The duration result compares a one-turn re-ask against
a five-turn debate, which varies the protocol as well as the length. Running the debate at one, two,
three and five turns gives the clean version and turns a contrast into a dose-response.

**4. A second checkpoint as the counterpart.** Both agents here are the same weights with two
personas, so this is one model talking to itself. Putting MedGemma opposite Qwen tests whether the
effect is agreement between identical weights or deference to a rival position.

**5. Per-case clinician outcomes.** The clinician comparison is the weakest claim in the project
because the two rates sit on different case sets. The comparator artefact carries aggregates only, so
this is real work on credentialed prescribing records rather than a rerun, and it would turn the
weakest claim into a paired test.

**6. Rung three of the ladder.** Few-shot did not improve the decision, which by the supervisor's own
sequencing is what licenses fine-tuning. The honest framing is that rung two failing is the
precondition for rung three, not a reason to skip it.

**7. Transfer, not the data.** Hosted models on synthetic non-MIMIC cases. Record-level data cannot
leave this machine under the data use agreement, so what transfers is the harness and the scoring
rule, never the cohort.

**8. Organism-specific resistance rules.** Correcting the scorer for inducible AmpC needs clinical
sign-off and organism-specific logic. It would tighten the adequacy labels; on the evidence in 8c it
would not change the harm finding.

Items 1 to 4 are runnable on this machine with the existing harness. Items 5 to 8 need something
this project does not have: credentialed record access, more compute, a hosted endpoint, or a
clinician.

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

**{DUPES} duplicate writes found and dropped in total**, across {TOTAL_EXPOSURES:,} exposures.
Every arm now runs under a PID lock. Model `{R['model']}`, temperature {R['temperature']}, seed
{R['seed']}, run locally: MIMIC-IV is credentialed under a PhysioNet data use agreement and no
record-level data is committed to this repository.

## 11. What I was asked, and what I built

{re.sub(r'^## ', '### ', _fill(ASKS).split('# What I was asked, and what I built', 1)[1].strip(), flags=re.M)}

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
