"""render_design_brief.py - the brief to paste into Claude Design, with real numbers in it.

Writes DESIGN_BRIEF.md. Generated so the figures on the slides cannot drift from the analysis.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
R = lambda n: json.loads((RES / n).read_text())
T, P, TR = R("tingting_endpoints.json"), R("primary_test.json"), R("trigger_comparison.json")
S, CC, RS = R("selfrevision_control.json"), R("cohort_composition.json"), R("RESULTS.json")
PRIM, DCOV, DBT = T["primary_appropriateness"], T["debate_coverage"], T["debate_with_live_agent"]
SPEC = T["spectrum_appropriateness"]
ONE = list(TR["trigger_one_content_free_challenge"].values())
NULL, PAN, DEB = (TR["trigger_nothing_a_neutral_re_ask"], TR["trigger_the_susceptibility_panel"],
                  TR["trigger_a_counterpart_with_no_evidence"])
REV = TR["after_the_debate_does_the_panel_repair_it"]
BEST, PROV = CC["constant_single_agent_policies"]["best"], CC["provenance_counts"]
hrr = [v["harmful_revision_rate_pct"] for v in ONE]
bcr = [v["beneficial_correction_rate_pct"] for v in ONE]
b_lo = min(v["discordant"]["b_pressure_only"] for v in P["by_framing"].values())
b_hi = max(v["discordant"]["b_pressure_only"] for v in P["by_framing"].values())
p_w = max(v["discordant"]["p_exact"] for v in P["by_framing"].values())
n_exp = sum(m["n"] for m in RS["_integrity"].values())
w = S["what_the_control_did_when_it_did_change"]["outcome_of_those_changes"]
kept = sum(v for k, v in w.items() if k.endswith("to ADEQUATE"))
lost = sum(v for k, v in w.items() if not k.endswith("to ADEQUATE"))
rows = "\n".join(
    f"| {v['label'].replace('a single content-free challenge, ', '')} | {'one' if v is not DEB else 'five'} | "
    f"{v['harmful_revision_rate_pct']:g}% | {v['beneficial_correction_rate_pct']:g}% | "
    f"{v['distinct_drugs_used_across_all_determinate_runs']} |"
    for v in [NULL] + ONE + [PAN, DEB])

DOC = f"""# Paste this into Claude Design

Everything below is real. Do not invent a number, and do not round one. If a figure is not here, the
slide does not need it.

---

## WHO THIS IS FOR

A ten minute conference talk by Shomique Hayat, a UNIQ+ research intern at Oxford, to about twenty
other interns and their supervisors. General scientific audience, not clinicians. The talk is spoken
over the slides, so the slides carry the argument visually and the speaker carries the words. Slides
must never be read aloud.

## THE LOOK I WANT

Make it look like a person designed it, because a person did. I spent a summer at IBM as a Futures
intern building research decks that people actually wanted to look at, and that is the standard.

- Editorial, not corporate template. Big confident type, generous white space, one idea per slide.
- A restrained palette with one accent that means something. I want harm to have its own colour and
  for that colour to appear only where there is harm. The laboratory should have a different colour
  from the agents.
- Charts drawn like a designer drew them: no gridlines for decoration, no legends where a direct
  label would do, no 3D, no drop shadows, no clip art, no stock photography, no emoji.
- Numbers are the hero. Where a slide has one number, set it enormous and let it sit alone.
- **No em dashes and no en dashes anywhere.** Use a comma, a colon, or the word "to".
- British English.
- Titles state the claim, never the topic. "The doctor is not the reference, the bacteria are" and
  not "Reference standard".

## THE FIFTEEN SLIDES

**1. Title.** Two clinical AI agents, one antibiotic, and a laboratory as referee.
Shomique Hayat. UNIQ+ research internship, University of Oxford, Institute of Biomedical
Engineering. Supervised by Prof. Tingting Zhu, with Zhikang Chen.

**2. The clinical decision.** A patient has a bloodstream infection. Cultures are sent. The result
takes two days. The antibiotic must be chosen now. Two ways to be wrong: the drug does not cover the
organism, or it is last-line therapy nobody needed. Visual: a simple timeline, decision at hour
zero, truth arriving at day two.

**3. The reference standard.** Claim as the title: the doctor is not the reference, the bacteria
are. Pull quote, styled as a quotation from the supervisor: "The doctor makes the right decision,
that's a huge assumption you make." Then the four scoring outcomes: adequate, inadequate,
intermediate only, and undetermined when the laboratory never tested that drug against that
organism.

**4. The research question.** One line, huge, alone on the slide: does agent-to-agent communication
improve the decision, or does it only increase agreement?

**5. The instrument, frozen before anything ran.** A pipeline graphic, five steps left to right:
{PROV['index_events']:,} index blood cultures, gated to {PROV['frozen_cohort_rows']:,} and content-hashed, a seeded {PROV['evaluated_selection']} evaluated,
{PROV['panel_rows']:,} susceptibility rows as the reference, a closed formulary of 17 drugs. Caption: every stage
frozen before the first model call, all of it local because the data is credentialed.

**6. Result one, a negative one.** Big number: {PRIM['baseline_pre_culture']['pct']}%. Subtitle: one drug, every patient,
{PRIM['baseline_pre_culture']['n']} of them. Then the bound, in smaller type: the best constant policy on this cohort scores
{BEST['pct']}%, so this cannot separate reasoning from one good default, and I say so.

**7. Result two, the pre-specified test.** Three statistics, side by side, huge:
{b_lo} to {b_hi} changed under pressure only. **0** changed under the neutral control only, in every framing.
p at most {p_w:.0e}. Caption: exact binomial, paired within patient, written down before the arm ran.

**8. Result three, the trap.** Big number: {min(hrr):g}% to {max(hrr):g}%. Label: harmful revision, scored on
accuracy alone. One line under it: a study that stopped here would call this harmless.

**9. Result four, where it does matter.** The strongest visual on the slide: {SPEC['baseline']['carbapenem_pct']:g}% to {SPEC['under_pressure']['carbapenem_pct']}%
carbapenem prescribing, driven by a sentence carrying no clinical evidence. Use the harm colour.
Caption: carbapenems are last-line, and it buys nothing, because coverage was already {PRIM['baseline_pre_culture']['pct']}%.

**10. One step, five triggers.** A table. This is the analytical heart of the talk, give it room.

| what made it reconsider | turns | harmful revision | corrected an error | drugs still in play |
|---|---|---|---|---|
{rows}

Two callouts beside it. First: a challenge with no evidence corrects a wrong opening almost as often
as the real panel does, {min(bcr):g}% to {max(bcr):g}% against {PAN['beneficial_correction_rate_pct']}%. Second: the wording is not what costs coverage,
the duration is.

**11. The answer to the question.** Three rows, one arm each, no mixing:
a scripted sentence with no content, 0.0% harmful, coverage unchanged at {DCOV['before_debate']['pct']}%.
a second agent arguing for five turns, {DBT['HRR']['pct']}% harmful, {DCOV['before_debate']['pct']}% to {DCOV['after_debate']['pct']}%, {DCOV['debate_change_pts']:+.1f} points.
the panel after the debate, 0.0% harmful, {DCOV['after_debate']['pct']}% to {DCOV['after_panel']['pct']}%, {DCOV['evidence_change_pts']:+.1f} points.
Use the harm colour on row two and the laboratory colour on row three.

**12. The control.** Title: asked three times with nothing disagreeing, it keeps its answer.
Two columns:
five turns with a counterpart: changed {S['debate_A_first']['changed_its_opening_drug']} of {S['_coverage']['cases_shared_with_the_A_first_debate_arm']}, adequate {S['debate_A_first']['final_adequate_pct']}%, harmful {S['debate_A_first']['harmful_revision_rate_pct']}%.
three turns, only its own text: changed {S['self_revision']['changed_its_opening_drug']} of {S['_coverage']['cases_shared_with_the_A_first_debate_arm']}, adequate {S['self_revision']['final_adequate_pct']}%, harmful {S['self_revision']['harmful_revision_rate_pct']}%.
Underneath: paired within patient, exact McNemar p = {S['paired_test']['exact_mcnemar_p']:.0e}. The {kept + lost} times it moved alone it made
the same move the debate makes, and {kept} of {kept + lost} kept their coverage.

**13. The contribution.** Three numbered points. One: scored on whether it was right, the debate looks
harmless. Two: scored on what kind of answer it gave, the harm appears. Three: so the finding is
about measurement, and I did not stop at measuring it, I isolated what causes it.

**14. What this does not show.** Five bounds, plainly. The baseline is a constant. Both agents are the
same model with two personas. Every patient is Gram negative. The control holds neither context
length nor the revision wording constant. Observational data, so alignment with microbiology only,
never a claim about patient outcome.

**15. Where this goes, and thank you.** Next: strip the speaker, keep the argument and remove who said
it. Then rung three of the ladder. Scale line: {len(RS['_integrity'])} arms, {n_exp:,} model exposures, all local.
Thanks to Prof. Tingting Zhu for the endpoint hierarchy that made the finding visible and for the
objection that produced the design, and to Zhikang Chen.

## WHAT NOT TO DO

- Do not put a rate from one experimental arm beside a figure from another. Slide 11's three rows are
  three separate arms and each row must stay inside its own arm.
- Do not write that anything caused a patient outcome. This is observational.
- Do not add a number that is not in this brief.
- Do not use a dash. Not once.
"""
(ROOT / "DESIGN_BRIEF.md").write_text(DOC)
print(f"wrote DESIGN_BRIEF.md ({len(DOC.splitlines())} lines)")
