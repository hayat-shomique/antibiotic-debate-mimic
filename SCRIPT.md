# The script

Ten minute slot. This runs to **8 minutes 55 seconds** of speaking, which leaves the slot
room to breathe. Do not try to fill ten.

Read the bold sentence and stop reading. The rest is what you say around it.

Generated from `results/*.json`, so every figure here is the one in the deck.

---

## Slide 1. Title

`10s` · cumulative `0:10`

Morning. I am Shomique, and for the last six weeks I have been asking one question.

If you put two clinical AI agents in a room and let them argue about which antibiotic to give a
patient, do they reach a better decision, or do they just agree with each other?

---

## Slide 2. The clinical decision

`30s` · cumulative `0:40`

This is the moment I am studying. A patient has a bloodstream infection. Cultures have gone to the
lab. The result will take two days, and the antibiotic has to be chosen now.

Get it wrong in one direction and the drug does not cover the organism. Get it wrong in the other
and you have given last-line therapy to someone who did not need it, and driven resistance.

So it is a real decision, made under real uncertainty, and it has a right answer that arrives later.

---

## Slide 3. The reference standard

`40s` · cumulative `1:20`

Here is where my supervisor changed the project in one sentence.

My first design scored the agents against what the doctor actually prescribed. She said: the doctor
makes the right decision, that is a huge assumption you make.

She was right. If your reference is a human, every result you have is conditional on that human
being correct.

So the reference standard became the bacteria. The patient's own susceptibility panel, from their
own specimen. Neither agent can see it. Neither agent can argue with it. Neither agent can produce
it. It just arrives, two days later, and says whether the drug would have worked.

That is the contribution. Not that AI is agreeable, which is published. The arbiter is what is new.

---

## Slide 4. The question, made precise

`15s` · cumulative `1:35`

So the question becomes precise, and testable.

Does agent-to-agent communication improve the appropriateness of the final antibiotic against the
organism that actually grew? Or does it only increase agreement?

---

## Slide 5. The instrument, frozen before anything ran

`45s` · cumulative `2:20`

Everything here was frozen before the first model call, so nothing could be tuned after I saw a
result.

9,236 index blood cultures from MIMIC-IV, gated to 7,796, content-hashed. I evaluated a seeded
200. The reference standard is 138,513 susceptibility rows.

The answer space is a closed formulary of seventeen drugs, so a wrong answer and an unparseable
answer are different things. And every prompt passes a leakage gate, because if the organism name
ever reached the model the whole study would be worthless.

It all runs locally. MIMIC-IV is credentialed, so no patient data leaves the machine.

---

## Slide 6. Result one, and it is a negative one

`40s` · cumulative `3:00`

First result, and it is not the one I wanted.

Before any conversation, the model recommends the same antibiotic for every single patient. One
drug, 200 patients.

But look at what that constant scores: 87.5 per cent coverage. Nothing in the case notes predicts
which organism will grow, so one broad agent for everybody is actually a defensible policy.

I put this on slide six deliberately, because it bounds everything after it. This design cannot tell
a model that reasons about patients from a model with one good default. The best constant policy on
this cohort scores 96.0 per cent, so I will never stand here and tell you the model beat a constant.

What I can still ask is what moves that default.

---

## Slide 7. Result two, the pre-specified test

`45s` · cumulative `3:45`

So I asked it in four conditions, on the same patients, with the same seed.

Ask it again, politely, with no disagreement and no new information: it does not move. Not once.

Now have someone assert a different drug, with no clinical reason at all. A sentence carrying no
information.

Across four framings, 173 to 183 patients changed under the challenge and did not change under the
neutral control. And zero, in every framing, changed under the control and not the challenge.

Exact binomial, paired within patient, pre-specified before the arm ran. p at most 2e-52.

The discordance is total and one-directional.

---

## Slide 8. Result three, and this is the trap

`25s` · cumulative `4:10`

Now, if you score that the way almost every paper scores it, on whether the answer was right, it
looks harmless.

Harmful revision under those four framings runs 1.1 to 3.5 per cent. The model abandons its drug
and lands on another drug that also covers the organism.

A study that stopped here would tell you the sycophancy does not matter.

---

## Slide 9. Result four, where it does matter

`45s` · cumulative `4:55`

My supervisor specified a second endpoint, and it is the reason this project has a point.

Do not only ask whether the answer was right. Ask what kind of answer it was.

That same content-free sentence moves carbapenem prescribing from 0 per cent of the cohort to
87.2 per cent.

Carbapenems are last-line. And it buys nothing, because coverage was already 87.5 per cent.

So the harm is invisible on the endpoint everyone reports, and severe on the one she asked for.

---

## Slide 10. One step, five triggers

`50s` · cumulative `5:45`

Now I want to show you the table that surprised me, because two things fell out of it that I did not
design for.

Every row starts from the same position, on the same patients, and applies one step of
reconsideration. The only thing that changes is what triggered it.

Top row is the null. Nothing to react to: no changes, no corrections, 1 drug in play across the whole
cohort. So nothing below this is instability. Something has to be said to it.

First surprise. A challenge carrying no clinical evidence corrects a wrong opening almost as often as
the real susceptibility panel does. 66.7 to 81.8 per cent against 91.7.

The model revises at close to the right rate, for none of the right reasons.

Second surprise. It is not the wording that costs you. All four framings sit in that narrow band at
one turn. Five turns costs 15.2 per cent.

And the answer space narrows with it. Given the panel, 8 drugs stay in play. After the debate, 3.

---

## Slide 11. The answer to the question

`50s` · cumulative `6:35`

So here is the answer to the question I was given.

A scripted sentence with no content: no harm, coverage unchanged at 87.5 per cent.

A second agent arguing a real case for five turns: harmful revision 15.2 per cent, and coverage of the
organism falls 87.5 to 78.0. That is 9.5 points of coverage, lost to a conversation.

Then give that same system the laboratory result, after the debate has already moved it. It repairs
57 of the 65 runs that arrive on the wrong drug, it pushes none of the 311 that arrive on
the right drug off it, and coverage goes to 95.2 per cent.

Communication degrades the decision here. Evidence improves it. That is the finding.

---

## Slide 12. The control

`50s` · cumulative `7:25`

Now, the obvious objection, and I want to get to it before you do.

Five turns is three chances to change your mind. Maybe it is not the argument. Maybe it is just being
asked repeatedly.

The debate arm cannot separate those, because it varies both at once. So I built the control.

One agent. Same patients. Same opening prompt, byte for byte. Same formulary, same gate, same scorer.
It speaks three times, exactly as often as the specialist speaks in the debate. And between turns it
sees only its own previous text. Nothing disagrees with it.

With a counterpart, it abandons its drug in 200 out of 200. Without one, 6.

Harmful revision 17.0 per cent against 0.6. Paired within patient, exact McNemar, p equals 7e-09.

And the 6 times it did move on its own, it made exactly the same move the debate makes, off
piperacillin-tazobactam onto ceftriaxone, and 5 of those 6 kept their coverage.

Same drug. Same patients. Very different risk. What differs is what triggered it.

Being contradicted is what moves this model. Being asked again is not.

---

## Slide 13. The contribution

`30s` · cumulative `7:55`

So what did I actually contribute.

Not that language models are agreeable. That is published, and I say so.

The contribution is that in this setting the harm is invisible to the endpoint everyone reports, and
visible only on the endpoint that asks what kind of answer was given. And that I did not stop at
measuring it, I isolated what causes it.

If you evaluate a multi-agent clinical system on correctness alone, you will miss this entirely.

---

## Slide 14. What this does not show

`35s` · cumulative `8:30`

Let me be straight about the bounds, because they are real.

The baseline is a constant, so I cannot separate reasoning from a good default.

Both agents are the same model with two personas. This is one model talking to itself.

Every patient here is Gram negative, and the Gram-positive half is untested.

The control does not hold context length or the wording of the revision prompt constant. The arm
that fixes that is the next one I would run.

And this is observational data. I can tell you a recommendation would not have covered the organism.
I cannot tell you it would have harmed the patient, and I will not.

---

## Slide 15. Where this goes, and thank you

`25s` · cumulative `8:55`

Next: strip the speaker. Keep the counterpart's argument, remove who said it. That separates being
contradicted by a peer from being contradicted by anything at all.

Then rung three of the ladder, because few-shot did not improve the decision, and by my supervisor's
own sequencing that is what licenses fine-tuning.

14 arms, 4,109 model exposures, every one local.

Thank you to Prof. Tingting Zhu, for the endpoint hierarchy that made the finding visible, and for
the objection that produced the whole design. And to Zhikang Chen.

Happy to take questions.

---


## If you are running long

Cut slide 8 to one sentence, "scored on accuracy this looks harmless", and cut slide 14 to the two
bounds that matter: one model talking to itself, and observational data.

Never cut slide 3, slide 10 or slide 12. Those are the argument.

## The three sentences to have ready

**If asked whether 200 patients is enough.** It is small and it is paired. Every patient is their own
control, put to the same model in four conditions with a fixed seed. That is what gets p to
2e-52.

**If asked whether the model is just broken.** It scores 87.5 per cent with one drug, and the best
constant policy scores 96.0. It is not broken, it is degenerate, and I say so on slide six.

**If you do not know.** Say: I do not know yet, that is a good question, let me come back to you with
the number. Then do.
