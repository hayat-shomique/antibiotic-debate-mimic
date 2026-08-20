# Paste this into Claude Design

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
9,236 index blood cultures, gated to 7,796 and content-hashed, a seeded 200 evaluated,
138,513 susceptibility rows as the reference, a closed formulary of 17 drugs. Caption: every stage
frozen before the first model call, all of it local because the data is credentialed.

**6. Result one, a negative one.** Big number: 87.5%. Subtitle: one drug, every patient,
200 of them. Then the bound, in smaller type: the best constant policy on this cohort scores
96.0%, so this cannot separate reasoning from one good default, and I say so.

**7. Result two, the pre-specified test.** Three statistics, side by side, huge:
173 to 183 changed under pressure only. **0** changed under the neutral control only, in every framing.
p at most 2e-52. Caption: exact binomial, paired within patient, written down before the arm ran.

**8. Result three, the trap.** Big number: 1.1% to 3.5%. Label: harmful revision, scored on
accuracy alone. One line under it: a study that stopped here would call this harmless.

**9. Result four, where it does matter.** The strongest visual on the slide: 0% to 87.2%
carbapenem prescribing, driven by a sentence carrying no clinical evidence. Use the harm colour.
Caption: carbapenems are last-line, and it buys nothing, because coverage was already 87.5%.

**10. One step, five triggers.** A table. This is the analytical heart of the talk, give it room.

| what made it reconsider | turns | harmful revision | corrected an error | drugs still in play |
|---|---|---|---|---|
| a neutral re-ask carrying no challenge at all | one | 0% | 0% | 1 |
| authority | one | 2.3% | 81.8% | 5 |
| peer consensus | one | 1.1% | 81.8% | 4 |
| safety framing | one | 3.5% | 72.7% | 3 |
| bare doubt | one | 1.7% | 66.7% | 3 |
| the organism and its susceptibility panel, clean context | one | 1.1% | 91.7% | 8 |
| five-turn debate against a counterpart carrying no evidence | five | 15.2% | 59.1% | 3 |

Two callouts beside it. First: a challenge with no evidence corrects a wrong opening almost as often
as the real panel does, 66.7% to 81.8% against 91.7%. Second: the wording is not what costs coverage,
the duration is.

**11. The answer to the question.** Three rows, one arm each, no mixing:
a scripted sentence with no content, 0.0% harmful, coverage unchanged at 87.5%.
a second agent arguing for five turns, 15.2% harmful, 87.5% to 78.0%, -9.5 points.
the panel after the debate, 0.0% harmful, 78.0% to 95.2%, +17.2 points.
Use the harm colour on row two and the laboratory colour on row three.

**12. The control.** Title: asked three times with nothing disagreeing, it keeps its answer.
Two columns:
five turns with a counterpart: changed 200 of 200, adequate 77.0%, harmful 17.0%.
three turns, only its own text: changed 6 of 200, adequate 87.0%, harmful 0.6%.
Underneath: paired within patient, exact McNemar p = 7e-09. The 6 times it moved alone it made
the same move the debate makes, and 5 of 6 kept their coverage.

**13. The contribution.** Three numbered points. One: scored on whether it was right, the debate looks
harmless. Two: scored on what kind of answer it gave, the harm appears. Three: so the finding is
about measurement, and I did not stop at measuring it, I isolated what causes it.

**14. What this does not show.** Five bounds, plainly. The baseline is a constant. Both agents are the
same model with two personas. Every patient is Gram negative. The control holds neither context
length nor the revision wording constant. Observational data, so alignment with microbiology only,
never a claim about patient outcome.

**15. Where this goes, and thank you.** Next: strip the speaker, keep the argument and remove who said
it. Then rung three of the ladder. Scale line: 14 arms, 4,109 model exposures, all local.
Thanks to Prof. Tingting Zhu for the endpoint hierarchy that made the finding visible and for the
objection that produced the design, and to Zhikang Chen.

## WHAT NOT TO DO

- Do not put a rate from one experimental arm beside a figure from another. Slide 11's three rows are
  three separate arms and each row must stay inside its own arm.
- Do not write that anything caused a patient outcome. This is observational.
- Do not add a number that is not in this brief.
- Do not use a dash. Not once.
