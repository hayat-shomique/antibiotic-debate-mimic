"""render_script.py - the spoken script, generated so the numbers cannot drift from the analysis.

Writes SCRIPT.md. This is what goes on the iPad. Every figure is read from results/*.json.
Timings are targets, not instructions: a ten minute slot is filled at nine, never at ten.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
R = lambda n: json.loads((RES / n).read_text())

T, P, TR = R("tingting_endpoints.json"), R("primary_test.json"), R("trigger_comparison.json")
S, CC, RS = R("selfrevision_control.json"), R("cohort_composition.json"), R("RESULTS.json")
CONF, FS = R("claim_confidence.json"), R("fewshot.json")

PRIM, DCOV, DBT = T["primary_appropriateness"], T["debate_coverage"], T["debate_with_live_agent"]
SPEC = T["spectrum_appropriateness"]
ONE = list(TR["trigger_one_content_free_challenge"].values())
NULL, PAN, DEB = (TR["trigger_nothing_a_neutral_re_ask"], TR["trigger_the_susceptibility_panel"],
                  TR["trigger_a_counterpart_with_no_evidence"])
REV = TR["after_the_debate_does_the_panel_repair_it"]
BEST = CC["constant_single_agent_policies"]["best"]
PROV = CC["provenance_counts"]
hrr = [v["harmful_revision_rate_pct"] for v in ONE]
bcr = [v["beneficial_correction_rate_pct"] for v in ONE]
b_lo = min(v["discordant"]["b_pressure_only"] for v in P["by_framing"].values())
b_hi = max(v["discordant"]["b_pressure_only"] for v in P["by_framing"].values())
p_w = max(v["discordant"]["p_exact"] for v in P["by_framing"].values())
n_exp = sum(m["n"] for m in RS["_integrity"].values())
w = S["what_the_control_did_when_it_did_change"]["outcome_of_those_changes"]
kept = sum(v for k, v in w.items() if k.endswith("to ADEQUATE"))
lost = sum(v for k, v in w.items() if not k.endswith("to ADEQUATE"))

SLIDES = [
 (1, "Title", 10, f"""
Morning. I am Shomique, and for the last six weeks I have been asking one question.

If you put two clinical AI agents in a room and let them argue about which antibiotic to give a
patient, do they reach a better decision, or do they just agree with each other?
"""),
 (2, "The clinical decision", 30, f"""
This is the moment I am studying. A patient has a bloodstream infection. Cultures have gone to the
lab. The result will take two days, and the antibiotic has to be chosen now.

Get it wrong in one direction and the drug does not cover the organism. Get it wrong in the other
and you have given last-line therapy to someone who did not need it, and driven resistance.

So it is a real decision, made under real uncertainty, and it has a right answer that arrives later.
"""),
 (3, "The reference standard", 40, f"""
Here is where my supervisor changed the project in one sentence.

My first design scored the agents against what the doctor actually prescribed. She said: the doctor
makes the right decision, that is a huge assumption you make.

She was right. If your reference is a human, every result you have is conditional on that human
being correct.

So the reference standard became the bacteria. The patient's own susceptibility panel, from their
own specimen. Neither agent can see it. Neither agent can argue with it. Neither agent can produce
it. It just arrives, two days later, and says whether the drug would have worked.

That is the contribution. Not that AI is agreeable, which is published. The arbiter is what is new.
"""),
 (4, "The question, made precise", 15, f"""
So the question becomes precise, and testable.

Does agent-to-agent communication improve the appropriateness of the final antibiotic against the
organism that actually grew? Or does it only increase agreement?
"""),
 (5, "The instrument, frozen before anything ran", 45, f"""
Everything here was frozen before the first model call, so nothing could be tuned after I saw a
result.

{PROV['index_events']:,} index blood cultures from MIMIC-IV, gated to {PROV['frozen_cohort_rows']:,}, content-hashed. I evaluated a seeded
{PROV['evaluated_selection']}. The reference standard is {PROV['panel_rows']:,} susceptibility rows.

The answer space is a closed formulary of seventeen drugs, so a wrong answer and an unparseable
answer are different things. And every prompt passes a leakage gate, because if the organism name
ever reached the model the whole study would be worthless.

It all runs locally. MIMIC-IV is credentialed, so no patient data leaves the machine.
"""),
 (6, "Result one, and it is a negative one", 40, f"""
First result, and it is not the one I wanted.

Before any conversation, the model recommends the same antibiotic for every single patient. One
drug, {PRIM['baseline_pre_culture']['n']} patients.

But look at what that constant scores: {PRIM['baseline_pre_culture']['pct']} per cent coverage. Nothing in the case notes predicts
which organism will grow, so one broad agent for everybody is actually a defensible policy.

I put this on slide six deliberately, because it bounds everything after it. This design cannot tell
a model that reasons about patients from a model with one good default. The best constant policy on
this cohort scores {BEST['pct']} per cent, so I will never stand here and tell you the model beat a constant.

What I can still ask is what moves that default.
"""),
 (7, "Result two, the pre-specified test", 45, f"""
So I asked it in four conditions, on the same patients, with the same seed.

Ask it again, politely, with no disagreement and no new information: it does not move. Not once.

Now have someone assert a different drug, with no clinical reason at all. A sentence carrying no
information.

Across four framings, {b_lo} to {b_hi} patients changed under the challenge and did not change under the
neutral control. And zero, in every framing, changed under the control and not the challenge.

Exact binomial, paired within patient, pre-specified before the arm ran. p at most {p_w:.0e}.

The discordance is total and one-directional.
"""),
 (8, "Result three, and this is the trap", 25, f"""
Now, if you score that the way almost every paper scores it, on whether the answer was right, it
looks harmless.

Harmful revision under those four framings runs {min(hrr):g} to {max(hrr):g} per cent. The model abandons its drug
and lands on another drug that also covers the organism.

A study that stopped here would tell you the sycophancy does not matter.
"""),
 (9, "Result four, where it does matter", 45, f"""
My supervisor specified a second endpoint, and it is the reason this project has a point.

Do not only ask whether the answer was right. Ask what kind of answer it was.

That same content-free sentence moves carbapenem prescribing from {SPEC['baseline']['carbapenem_pct']:g} per cent of the cohort to
{SPEC['under_pressure']['carbapenem_pct']} per cent.

Carbapenems are last-line. And it buys nothing, because coverage was already {PRIM['baseline_pre_culture']['pct']} per cent.

So the harm is invisible on the endpoint everyone reports, and severe on the one she asked for.
"""),
 (10, "One step, five triggers", 50, f"""
Now I want to show you the table that surprised me, because two things fell out of it that I did not
design for.

Every row starts from the same position, on the same patients, and applies one step of
reconsideration. The only thing that changes is what triggered it.

Top row is the null. Nothing to react to: no changes, no corrections, {NULL['distinct_drugs_used_across_all_determinate_runs']} drug in play across the whole
cohort. So nothing below this is instability. Something has to be said to it.

First surprise. A challenge carrying no clinical evidence corrects a wrong opening almost as often as
the real susceptibility panel does. {min(bcr):g} to {max(bcr):g} per cent against {PAN['beneficial_correction_rate_pct']}.

The model revises at close to the right rate, for none of the right reasons.

Second surprise. It is not the wording that costs you. All four framings sit in that narrow band at
one turn. Five turns costs {DEB['harmful_revision_rate_pct']} per cent.

And the answer space narrows with it. Given the panel, {PAN['distinct_drugs_used_across_all_determinate_runs']} drugs stay in play. After the debate, {DEB['distinct_drugs_used_across_all_determinate_runs']}.
"""),
 (11, "The answer to the question", 50, f"""
So here is the answer to the question I was given.

A scripted sentence with no content: no harm, coverage unchanged at {DCOV['before_debate']['pct']} per cent.

A second agent arguing a real case for five turns: harmful revision {DBT['HRR']['pct']} per cent, and coverage of the
organism falls {DCOV['before_debate']['pct']} to {DCOV['after_debate']['pct']}. That is {abs(DCOV['debate_change_pts'])} points of coverage, lost to a conversation.

Then give that same system the laboratory result, after the debate has already moved it. It repairs
{REV['beneficial_corrections']} of the {REV['entered_inadequate']} runs that arrive on the wrong drug, it pushes none of the {REV['entered_adequate']} that arrive on
the right drug off it, and coverage goes to {DCOV['after_panel']['pct']} per cent.

Communication degrades the decision here. Evidence improves it. That is the finding.
"""),
 (12, "The control", 50, f"""
Now, the obvious objection, and I want to get to it before you do.

Five turns is three chances to change your mind. Maybe it is not the argument. Maybe it is just being
asked repeatedly.

The debate arm cannot separate those, because it varies both at once. So I built the control.

One agent. Same patients. Same opening prompt, byte for byte. Same formulary, same gate, same scorer.
It speaks three times, exactly as often as the specialist speaks in the debate. And between turns it
sees only its own previous text. Nothing disagrees with it.

With a counterpart, it abandons its drug in {S['debate_A_first']['changed_its_opening_drug']} out of {S['_coverage']['cases_shared_with_the_A_first_debate_arm']}. Without one, {S['self_revision']['changed_its_opening_drug']}.

Harmful revision {S['debate_A_first']['harmful_revision_rate_pct']} per cent against {S['self_revision']['harmful_revision_rate_pct']}. Paired within patient, exact McNemar, p equals {S['paired_test']['exact_mcnemar_p']:.0e}.

And the {kept + lost} times it did move on its own, it made exactly the same move the debate makes, off
piperacillin-tazobactam onto ceftriaxone, and {kept} of those {kept + lost} kept their coverage.

Same drug. Same patients. Very different risk. What differs is what triggered it.

Being contradicted is what moves this model. Being asked again is not.
"""),
 (13, "The contribution", 30, f"""
So what did I actually contribute.

Not that language models are agreeable. That is published, and I say so.

The contribution is that in this setting the harm is invisible to the endpoint everyone reports, and
visible only on the endpoint that asks what kind of answer was given. And that I did not stop at
measuring it, I isolated what causes it.

If you evaluate a multi-agent clinical system on correctness alone, you will miss this entirely.
"""),
 (14, "What this does not show", 35, f"""
Let me be straight about the bounds, because they are real.

The baseline is a constant, so I cannot separate reasoning from a good default.

Both agents are the same model with two personas. This is one model talking to itself.

Every patient here is Gram negative, and the Gram-positive half is untested.

The control does not hold context length or the wording of the revision prompt constant. The arm
that fixes that is the next one I would run.

And this is observational data. I can tell you a recommendation would not have covered the organism.
I cannot tell you it would have harmed the patient, and I will not.
"""),
 (15, "Where this goes, and thank you", 25, f"""
Next: strip the speaker. Keep the counterpart's argument, remove who said it. That separates being
contradicted by a peer from being contradicted by anything at all.

Then rung three of the ladder, because few-shot did not improve the decision, and by my supervisor's
own sequencing that is what licenses fine-tuning.

{len(RS['_integrity'])} arms, {n_exp:,} model exposures, every one local.

Thank you to Prof. Tingting Zhu, for the endpoint hierarchy that made the finding visible, and for
the objection that produced the whole design. And to Zhikang Chen.

Happy to take questions.
"""),
]

total = sum(t for _, _, t, _ in SLIDES)
lines = [f"""# The script

Ten minute slot. This runs to **{total // 60} minutes {total % 60} seconds** of speaking, which leaves the slot
room to breathe. Do not try to fill ten.

Read the bold sentence and stop reading. The rest is what you say around it.

Generated from `results/*.json`, so every figure here is the one in the deck.

---
"""]
run = 0
for n, name, secs, body in SLIDES:
    run += secs
    lines.append(f"## Slide {n}. {name}\n\n`{secs}s` · cumulative `{run // 60}:{run % 60:02d}`\n{body}\n---\n")
lines.append(f"""
## If you are running long

Cut slide 8 to one sentence, "scored on accuracy this looks harmless", and cut slide 14 to the two
bounds that matter: one model talking to itself, and observational data.

Never cut slide 3, slide 10 or slide 12. Those are the argument.

## The three sentences to have ready

**If asked whether 200 patients is enough.** It is small and it is paired. Every patient is their own
control, put to the same model in four conditions with a fixed seed. That is what gets p to
{p_w:.0e}.

**If asked whether the model is just broken.** It scores {PRIM['baseline_pre_culture']['pct']} per cent with one drug, and the best
constant policy scores {BEST['pct']}. It is not broken, it is degenerate, and I say so on slide six.

**If you do not know.** Say: I do not know yet, that is a good question, let me come back to you with
the number. Then do.
""")
(ROOT / "SCRIPT.md").write_text("\n".join(lines))
print(f"wrote SCRIPT.md, {total//60}:{total%60:02d} of speaking across {len(SLIDES)} slides")
