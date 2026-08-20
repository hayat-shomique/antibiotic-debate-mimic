# The research journey, end to end

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
| index events | 9,236 panel-bearing first positive blood cultures |
| the frozen cohort | gated to 7,796, content-hashed, and the hash asserted on every run |
| the evaluated selection | a seeded 200, drawn from the frame before any model call |
| the reference standard | 138,513 susceptibility panel rows, scored four ways |
| the answer space | a closed formulary of 17 agents, plus OTHER and ABSTAIN |
| the leakage gate | every assembled prompt checked for organism names, drug residue and canaries |

Scoring is four-way and that matters: adequate, inadequate, intermediate only, and undetermined
when the laboratory never tested that drug against that organism. Folding undetermined into either
bucket would be a decision I am not entitled to make, so it leaves the numerator and is reported.

## 4. The first result was a negative one, and it bounds everything after it

Before any conversation, the model recommends the same antibiotic for every patient in the cohort.
One drug, 200 cases. It scores
87.5% against the panel.

That is not a broken model. Nothing in the case block predicts the organism, so one broad empiric
agent for everybody is a defensible policy under that uncertainty. But it bounds the study: **this
design cannot separate a model that reasons about patients from a model with one good default.**
The best constant policy on this cohort, giving every patient
meropenem, scores 192 of 200 = 96.0%, so I never argue the model underperforms a constant.

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
the model does not move: 0 harmful revisions, 0 corrections,
1 drug in play across the whole cohort. So nothing that follows is drift or decoding noise.
Something has to be said to it before it moves.

## 6. The pre-specified test, and what it found

The primary test was written down before the arm ran: an exact binomial on the discordant pairs
between the neutral re-ask and the unsupported challenge, paired within patient.

Across the four challenge framings, cases that changed under pressure only ran 173 to 183.
Cases that changed under the neutral control only ran **zero, in every framing.** Exact binomial
p at most 1.67e-52, on 180 to 185 evaluable cases per framing.

The discordance is one-directional and total. That is as clean as this design can produce.

## 7. Then the endpoints she specified showed why accuracy alone hides it

Her endpoint hierarchy is what turns that result from a curiosity into a clinical finding, and it
is the reason the study has a point.

**On accuracy, the pressure looks harmless.** Harmful revision under the four framings runs
1.1% to 3.5%. The model abandons its drug and lands on another drug that
also covers. A study that stopped at accuracy would conclude the sycophancy is harmless.

**On spectrum appropriateness, it does not.** The same content-free sentence moves carbapenem
prescribing from 0.0% to 87.2% of the cohort. It buys nothing, because coverage was
already 87.5%, and carbapenem overuse drives resistance at population level.

**So the finding is about measurement.** That models are agreeable is known. That the endpoint
everyone reports cannot see this particular harm is the part that is new, and the hierarchy that
makes it visible came from my supervisor's own framing.

## 8. A live second agent, and the cost of a real conversation

Replacing the scripted sentence with a second agent arguing a real case, over five turns, both
speaking orders, 400 ordering-runs:

- coverage of the organism falls 87.5% to 78.0%, -9.5 points
- harmful revision 52 of 341 = 15.2%
- beneficial correction 13 of 22 = 59.1%
- the answer space collapses to 3 drugs

Give the same system the laboratory panel after the debate has already moved it, and it repairs
57 of the 65 runs that arrive on an inadequate drug and pushes none of the
311 that arrive on an adequate one off it. Coverage rises to 95.2%.

## 9. Two things fell out that were not designed for

Putting every one-step condition on the same footing, from the same opening position on the same
cases, produced two results nobody set out to find.

**A challenge carrying no evidence corrects an inadequate opening almost as often as the real panel
does**, 66.7% to 81.8% against 91.7%. The model revises at close to the right rate for none
of the right reasons.

**The framing of the challenge is not what costs coverage. Duration is.** All four framings sit in a
narrow band at one turn. Five turns costs 15.2%. And the answer space narrows with it: the panel
leaves 8 drugs in play, the debate leaves 3.

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
| changed its opening drug | 200 of 200 | 6 of 200 |
| final recommendation adequate | 77.0% | 87.0% |
| harmful revision | 17.0% | 0.6% |

Paired within patient, the debate ends on an inadequate drug where the control ends on an adequate
one in 28 pairs, and the reverse in 0. Exact McNemar p = 7.45e-09.

**And the few times it does move unprompted, it makes the same move the debate makes.** All
6 are piperacillin-tazobactam to ceftriaxone, the same de-escalation the debate drives, and
5 of them keep their coverage while 1 does not. So this is not a claim that the model
never errs on its own. It is a claim about rate: the same move costs
0.6% when it makes it alone and 17.0% when a counterpart drives it, on the same
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

20 organisms, every case Gram negative, 126 of 200 *Escherichia coli*.
Five of the seventeen formulary agents are Gram-positive drugs that can never be adequate here, and
the Gram-positive half of bacteraemia is untested.

Roughly one specimen in five carries an organism capable of AmpC de-repression,
36 of 200, and the scorer has no rule for it. Graded by the strength of the published
evidence, the induction risk is best established for *Enterobacter cloacae*, which is
9 of the 200. It bounds
27 of the adequacy labels. It does **not**
bound the harm finding: 1 of the 52 harmful revisions is onto a third-generation cephalosporin
against an AmpC-capable organism, and 23 are onto cefepime, which guidance recommends for AmpC
producers.

## 13. How much weight each claim carries

Graded on four things that can be checked rather than asserted: is the comparison paired within
patient, is there a control arm that removes the leading alternative, does a second implementation
or a recomputation from the raw runs reproduce it, and is the residual uncertainty stated where the
claim is made. 4 high, 3 good, 1 moderate, 1 weak.

| claim | number | confidence |
|---|---|---|
| An unsupported challenge moves the model where a neutral re-ask never does | discordant pairs 173 to 183 against 0, exact binomial p at most 1.67e-52 | **high** |
| A five-turn debate costs coverage of the organism | 87.5% to 78.0%, -9.5 points; harmful revision 52/341 = 15.2% | **high** |
| Duration, not the framing of the challenge, is what costs coverage | one turn costs 1.1% to 3.5% across four framings; five turns cost 15.2% | **high** |
| An unsupported sentence drives carbapenem prescribing from nothing to most of the cohort | 0.0% to 87.2% carbapenem use | **high** |
| Being contradicted moves the model, being asked again does not | changed its drug 200 of 200 with a counterpart against 6 without one; harmful revision 17.0% against 0.6%; exact McNemar p = 7.45e-09 | **good** |
| The answer space collapses under debate and stays open under evidence | 3 distinct drugs after the debate against 8 after the panel, and 1 with no challenge at all | **good** |
| Few-shot examples do not improve the decision | 18 correct answers lost against 2 gained on 175 paired cases, exact McNemar p = 0.000402 | **good** |
| Adequacy labels are bounded by unhandled AmpC induction, and the harm finding is not | 36 of 200 specimens carry an AmpC-capable organism; 27 runs are affected, against 1 of the 52 harmful revisions | **moderate** |
| The model and the clinician are within a point of each other | 91.1% on 192 cases against 90.6% on 138 | **weak** |

The weakest is the clinician comparison and it is reported as weak: 91.1% on
192 cases against 90.6% on 138 sit on different sets of cases, so
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

14 experimental arms, 4,109 deduplicated model exposures, every one of them local, because
MIMIC-IV is credentialed and no record-level data may reach a hosted service. Every number in every
document and on every slide is generated from `results/*.json`. A coherence harness reads every
tracked file and fails if any of them states a superseded value, states a banned claim, or places
two experimental arms in one row. The acceptance suite is at 36 of 36.

---

*Generated by `analysis/render_journey.py`. Rebuild with `python3 analysis/render_journey.py`.*
