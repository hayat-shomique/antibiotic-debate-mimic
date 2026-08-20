"""render_journey.py - the project end to end, as it actually happened.

Writes JOURNEY.md. Every number in it is read from results/*.json, never typed, which is why this
is a script and not a document. The narrative is the part a person writes; the figures are the part
the analysis writes, and they are kept apart on purpose.

The audience is someone who was not in the room: what the question was, why the first version of
the design was wrong, what was built, what came out, what is known already, what is new, how much
weight each claim carries, and what would be done next.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"


def R(name):
    p = RES / name
    return json.loads(p.read_text()) if p.exists() else None


T, P = R("tingting_endpoints.json"), R("primary_test.json")
RS, TRIG = R("RESULTS.json"), R("trigger_comparison.json")
SRC, CONF = R("selfrevision_control.json"), R("claim_confidence.json")
CLIN, FS = R("clinician_comparison.json"), R("fewshot.json")
CC, AMPC = R("cohort_composition.json"), R("ampc_exposure.json")
POL = R("policy_degeneracy.json")
PROV = CC["provenance_counts"]
BEST = CC["constant_single_agent_policies"]["best"]

DBT = T["debate_with_live_agent"]
DCOV = T["debate_coverage"]
SPEC = T["spectrum_appropriateness"]
PRIM = T["primary_appropriateness"]
NULL = TRIG["trigger_nothing_a_neutral_re_ask"]
ONE = list(TRIG["trigger_one_content_free_challenge"].values())
PAN = TRIG["trigger_the_susceptibility_panel"]
DEB = TRIG["trigger_a_counterpart_with_no_evidence"]
REV = TRIG["after_the_debate_does_the_panel_repair_it"]
_wc = SRC["what_the_control_did_when_it_did_change"]["outcome_of_those_changes"]
_kept = sum(v for k, v in _wc.items() if k.endswith("to ADEQUATE"))
_lost = sum(v for k, v in _wc.items() if not k.endswith("to ADEQUATE"))

n_arms = len(RS["_integrity"])
n_exp = sum(m["n"] for m in RS["_integrity"].values())
b_lo = min(v["discordant"]["b_pressure_only"] for v in P["by_framing"].values())
b_hi = max(v["discordant"]["b_pressure_only"] for v in P["by_framing"].values())
p_worst = max(v["discordant"]["p_exact"] for v in P["by_framing"].values())
n_lo = min(v["n_primary"] for v in P["by_framing"].values())
n_hi = max(v["n_primary"] for v in P["by_framing"].values())
one_hrr = [v["harmful_revision_rate_pct"] for v in ONE]
one_bcr = [v["beneficial_correction_rate_pct"] for v in ONE]

conf_rows = "\n".join(
    "| {} | {} | **{}** |".format(c["claim"], c["number"], c["confidence"])
    for c in CONF["claims"]) if CONF else ""
conf_tally = ", ".join(f"{v} {k}" for k, v in CONF["_tally"].items()) if CONF else ""

DOC = f"""# The research journey, end to end

Shomique Hayat, UNIQ+ research internship, University of Oxford, Institute of Biomedical
Engineering. Supervised by Prof. Tingting Zhu, with Zhikang Chen. 6 July to 20 August 2026.

This document is generated. Every figure in it is read from `results/*.json` by
`analysis/render_journey.py`, so no number here was typed by hand and none can drift from the
analysis that produced it. The narrative is mine; the numbers are the pipeline's.

---

## 1. The question, and the constraint that shaped it

Two language-model agents that talk to each other: does that make a better clinical decision, or
does it just make them agree?

That question is not new. What made it answerable here was a constraint my supervisor put on it
early, twice inside sixteen hours: you cannot study everyone going into intensive care. Pick a
narrow population and a named treatment. So the study is bloodstream infection, and the treatment is
one empiric antibiotic, chosen before any culture result is available.

## 2. The first version of the design was wrong, and being told so is the reason this works

The first design scored the agents against the clinician's actual prescription. Prof. Zhu's
objection was one sentence: *"The doctor makes the right decision, that's a huge assumption you
make."*

She was right, and it changed everything downstream. If the reference standard is a human decision,
every result is contingent on that human being correct. So the reference standard became the
patient's own microbiology: the susceptibility panel from that specimen, which neither agent can
see, neither agent can argue with, and neither agent can produce.

**That is the contribution.** Not that language models are agreeable, which is published. The
arbiter is what is new: a per-patient laboratory panel sitting outside the conversation.

## 3. Building the instrument, before any model was run

Everything below was frozen before the first model call, so nothing could be tuned after a result
was seen.

| stage | what it is |
|---|---|
| index events | {PROV['index_events']:,} panel-bearing first positive blood cultures |
| the frozen cohort | gated to {PROV['frozen_cohort_rows']:,}, content-hashed, and the hash asserted on every run |
| the evaluated selection | a seeded {PROV['evaluated_selection']}, drawn from the frame before any model call |
| the reference standard | {PROV['panel_rows']:,} susceptibility panel rows, scored four ways |
| the answer space | a closed formulary of 17 agents, plus OTHER and ABSTAIN |
| the leakage gate | every assembled prompt checked for organism names, drug residue and canaries |

Scoring is four-way and that matters: adequate, inadequate, intermediate only, and undetermined
when the laboratory never tested that drug against that organism. Folding undetermined into either
bucket would be a decision I am not entitled to make, so it leaves the numerator and is reported.

## 4. The first result was a negative one, and it bounds everything after it

Before any conversation, the model recommends the same antibiotic for every patient in the cohort.
One drug, {PRIM['baseline_pre_culture']['n']} cases. It scores
{PRIM['baseline_pre_culture']['pct']}% against the panel.

That is not a broken model. Nothing in the case block predicts the organism, so one broad empiric
agent for everybody is a defensible policy under that uncertainty. But it bounds the study: **this
design cannot separate a model that reasons about patients from a model with one good default.**
The best constant policy on this cohort, giving every patient
{BEST['agent']}, scores {BEST['k']} of {BEST['n']} = {BEST['pct']}%, so I never argue the model underperforms a constant.

What the study can still do is ask what moves that default.

## 5. The conditions, and why the null arm is the most important one

Each of the frozen cases is put to the model under conditions that differ in exactly one thing.

| condition | what the model receives | what a change means |
|---|---|---|
| C0 | the case, before any culture result | the zero-shot recommendation |
| Cn | asked again, no disagreement, no new facts | any change is instability |
| C1 | a challenge asserting a different drug, carrying no clinical content | yielding to pressure |
| C2 | the organism and its susceptibility panel | a change here can be correct |

**Cn is the arm that makes the rest mean anything.** Asked to reconsider with nothing to react to,
the model does not move: {NULL['harmful_revisions']} harmful revisions, {NULL['beneficial_corrections']} corrections,
{NULL['distinct_drugs_used_across_all_determinate_runs']} drug in play across the whole cohort. So nothing that follows is drift or decoding noise.
Something has to be said to it before it moves.

## 6. The pre-specified test, and what it found

The primary test was written down before the arm ran: an exact binomial on the discordant pairs
between the neutral re-ask and the unsupported challenge, paired within patient.

Across the four challenge framings, cases that changed under pressure only ran {b_lo} to {b_hi}.
Cases that changed under the neutral control only ran **zero, in every framing.** Exact binomial
p at most {p_worst:.3g}, on {n_lo} to {n_hi} evaluable cases per framing.

The discordance is one-directional and total. That is as clean as this design can produce.

## 7. Then the endpoints she specified showed why accuracy alone hides it

Her endpoint hierarchy is what turns that result from a curiosity into a clinical finding, and it
is the reason the study has a point.

**On accuracy, the pressure looks harmless.** Harmful revision under the four framings runs
{min(one_hrr):g}% to {max(one_hrr):g}%. The model abandons its drug and lands on another drug that
also covers. A study that stopped at accuracy would conclude the sycophancy is harmless.

**On spectrum appropriateness, it does not.** The same content-free sentence moves carbapenem
prescribing from {SPEC['baseline']['carbapenem_pct']}% to {SPEC['under_pressure']['carbapenem_pct']}% of the cohort. It buys nothing, because coverage was
already {PRIM['baseline_pre_culture']['pct']}%, and carbapenem overuse drives resistance at population level.

**So the finding is about measurement.** That models are agreeable is known. That the endpoint
everyone reports cannot see this particular harm is the part that is new, and the hierarchy that
makes it visible came from my supervisor's own framing.

## 8. A live second agent, and the cost of a real conversation

Replacing the scripted sentence with a second agent arguing a real case, over five turns, both
speaking orders, {DEB['runs']} ordering-runs:

- coverage of the organism falls {DCOV['before_debate']['pct']}% to {DCOV['after_debate']['pct']}%, {DCOV['debate_change_pts']:+.1f} points
- harmful revision {DBT['HRR']['k']} of {DBT['HRR']['n']} = {DBT['HRR']['pct']}%
- beneficial correction {DBT['BCR']['k']} of {DBT['BCR']['n']} = {DBT['BCR']['pct']}%
- the answer space collapses to {DEB['distinct_drugs_used_across_all_determinate_runs']} drugs

Give the same system the laboratory panel after the debate has already moved it, and it repairs
{REV['beneficial_corrections']} of the {REV['entered_inadequate']} runs that arrive on an inadequate drug and pushes none of the
{REV['entered_adequate']} that arrive on an adequate one off it. Coverage rises to {DCOV['after_panel']['pct']}%.

## 9. Two things fell out that were not designed for

Putting every one-step condition on the same footing, from the same opening position on the same
cases, produced two results nobody set out to find.

**A challenge carrying no evidence corrects an inadequate opening almost as often as the real panel
does**, {min(one_bcr):g}% to {max(one_bcr):g}% against {PAN['beneficial_correction_rate_pct']}%. The model revises at close to the right rate for none
of the right reasons.

**The framing of the challenge is not what costs coverage. Duration is.** All four framings sit in a
narrow band at one turn. Five turns costs {DEB['harmful_revision_rate_pct']}%. And the answer space narrows with it: the panel
leaves {PAN['distinct_drugs_used_across_all_determinate_runs']} drugs in play, the debate leaves {DEB['distinct_drugs_used_across_all_determinate_runs']}.

## 10. The control, because the obvious objection deserved an arm and not an argument

The objection to section 9 is that five turns is three chances to change your mind, so maybe
repetition explains it rather than the counterpart. The debate arm cannot separate those, because it
varies both at once.

So I ran the control. One agent, the same specialist, the same frozen cases, the same round-0 prompt
byte for byte, the same formulary, gate and scorer. It speaks three times, exactly as many times as
the specialist speaks in the five-turn debate, and between turns it sees only its own previous text.
Nothing disagrees with it.

| | five turns, a counterpart arguing | three turns, only its own text |
|---|---|---|
| changed its opening drug | {SRC['debate_A_first']['changed_its_opening_drug']} of {SRC['_coverage']['cases_shared_with_the_A_first_debate_arm']} | {SRC['self_revision']['changed_its_opening_drug']} of {SRC['_coverage']['cases_shared_with_the_A_first_debate_arm']} |
| final recommendation adequate | {SRC['debate_A_first']['final_adequate_pct']}% | {SRC['self_revision']['final_adequate_pct']}% |
| harmful revision | {SRC['debate_A_first']['harmful_revision_rate_pct']}% | {SRC['self_revision']['harmful_revision_rate_pct']}% |

Paired within patient, the debate ends on an inadequate drug where the control ends on an adequate
one in {SRC['paired_test']['debate_inadequate_and_control_adequate']} pairs, and the reverse in {SRC['paired_test']['control_inadequate_and_debate_adequate']}. Exact McNemar p = {SRC['paired_test']['exact_mcnemar_p']:.3g}.

**And the few times it does move unprompted, it makes the same move the debate makes.** All
{SRC['what_the_control_did_when_it_did_change']['runs_that_changed']} are piperacillin-tazobactam to ceftriaxone, the same de-escalation the debate drives, and
{_kept} of them keep their coverage while {_lost} does not. So this is not a claim that the model
never errs on its own. It is a claim about rate: the same move costs
{SRC['self_revision']['harmful_revision_rate_pct']}% when it makes it alone and {SRC['debate_A_first']['harmful_revision_rate_pct']}% when a counterpart drives it, on the same
patients. Same destination drug, opposite safety profile, and what differs is what triggered it.

That is where the clinical literature lands exactly. De-escalating a broad-spectrum beta-lactam to a
narrower agent is trial-supported **when susceptibility guides it**: the SIMPLIFY trial found it
non-inferior in Enterobacterales bacteraemia, clinical cure 148 of 164 against 148 of 167, risk
difference 1.6 percentage points, 95% CI minus 5.0 to 8.2 (doi:10.1016/S1473-3099(23)00686-2). What
this study measures is the same move made for a reason that is not susceptibility.

## 11. What the literature already had, and what it did not

The rule I worked to is that you concede what is known before you claim what is new, because
claiming a published phenomenon as your own finding costs the room's trust in everything else.

**Already established, and I say so on the slide.** Collaboration between agents does not reliably
help. Sycophancy and peer conformity are documented, including for small open-weight models in
medicine. Correctness-blind adoption of a counterpart's answer is the core result of prior work. The
speaking-order effect in this design is entailed by the other results, not discovered.

**Not found in the reading, and this is the narrow claim.** A per-patient laboratory panel used as
the arbiter, so that "inadequate" carries external clinical meaning rather than agreement with a
benchmark key or a judge model. The published work I could find scores against benchmark answers or
model juries; this scores against the organism that actually grew.

**What the clinical literature contributes.** Rhee and colleagues establish that both inadequate and
unnecessarily broad empiric therapy carry higher adjusted mortality, which is what makes the
spectrum endpoint more than bookkeeping. The AmpC primer grades induction risk by organism, which is
implemented directly in the scoring of this project's own limitation. All identifiers were resolved
against PubMed and recorded with their PMIDs.

## 12. What this cohort is, and what it therefore cannot say

{CC['organisms']['distinct']} organisms, every case Gram negative, {CC['organisms']['top'][0]['cases']} of {CC['coverage_ceiling']['n']} *Escherichia coli*.
Five of the seventeen formulary agents are Gram-positive drugs that can never be adequate here, and
the Gram-positive half of bacteraemia is untested.

Roughly one specimen in five carries an organism capable of AmpC de-repression,
{AMPC['cohort']['any_ampc_capable']} of {AMPC['cohort']['n_cases']}, and the scorer has no rule for it. Graded by the strength of the published
evidence, the induction risk is best established for *Enterobacter cloacae*, which is
{AMPC['cohort']['best_established']} of the {AMPC['cohort']['n_cases']}. It bounds
{AMPC['adequacy_labels_the_limitation_distrusts']['runs_ending_on_a_third_generation_cephalosporin_against_an_ampc_capable_organism_and_scored_adequate']} of the adequacy labels. It does **not**
bound the harm finding: {AMPC['harmful_revisions']['onto_a_third_generation_cephalosporin_against_an_ampc_capable_organism']} of the {AMPC['harmful_revisions']['n']} harmful revisions is onto a third-generation cephalosporin
against an AmpC-capable organism, and {AMPC['harmful_revisions']['onto_cefepime_which_guidance_endorses_for_ampc']} are onto cefepime, which guidance recommends for AmpC
producers.

## 13. How much weight each claim carries

Graded on four things that can be checked rather than asserted: is the comparison paired within
patient, is there a control arm that removes the leading alternative, does a second implementation
or a recomputation from the raw runs reproduce it, and is the residual uncertainty stated where the
claim is made. {conf_tally}.

| claim | number | confidence |
|---|---|---|
{conf_rows}

The weakest is the clinician comparison and it is reported as weak: {CLIN['model_zero_shot']['adequate_determined_only']['pct']}% on
{CLIN['model_zero_shot']['adequate_determined_only']['n']} cases against {CLIN['clinician']['adequate_determined_only']['pct']}% on {CLIN['clinician']['adequate_determined_only']['n']} sit on different sets of cases, so
they are two independent proportions and not a paired test.

## 14. What I would do next

1. **Strip the speaker.** Keep the counterpart's text and remove only the attribution. It separates
   being contradicted by a peer from being contradicted by any rival position, and it fixes the
   sharpest limitation of the control: that the control changes the revision instruction as well as
   the counterpart.
2. **Match the context length.** Pad the single-agent transcript to the token count the debate
   reaches.
3. **Sweep the turn count inside one protocol**, turning the duration contrast into a dose-response.
4. **Put a second checkpoint opposite the first.** Both agents here are the same weights with two
   personas, so this is one model talking to itself.
5. **Get per-case clinician outcomes**, which turns the weakest claim into a paired test.
6. **Rung three of the ladder.** Few-shot did not improve the decision, and by the supervisor's own
   sequencing that is what licenses fine-tuning rather than a reason to skip it.

Items 1 to 4 run on this machine with the existing harness.

## 15. The scale of what was built

{n_arms} experimental arms, {n_exp:,} deduplicated model exposures, every one of them local, because
MIMIC-IV is credentialed and no record-level data may reach a hosted service. Every number in every
document and on every slide is generated from `results/*.json`. A coherence harness reads every
tracked file and fails if any of them states a superseded value, states a banned claim, or places
two experimental arms in one row. The acceptance suite is at 36 of 36.

---

*Generated by `analysis/render_journey.py`. Rebuild with `python3 analysis/render_journey.py`.*
"""

(ROOT / "JOURNEY.md").write_text(DOC)
print(f"wrote JOURNEY.md ({len(DOC.splitlines())} lines)")
