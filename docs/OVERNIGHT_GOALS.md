# Goals and checklist, overnight of 20 August 2026

Talk: 20 August 2026, 12:15 to 12:30, MPLS session 2 of 3, Kloppenburg room, Exeter College Cohen
Quad, chaired by Dr Tim Hageman. Ten minutes and five minutes of questions.

Every goal below is drawn from something you actually asked for. Progress is recorded in
`docs/OVERNIGHT_LEDGER.md`, which is the evidence for every tick.

## G1. One set of numbers, everywhere, generated

No number typed into prose. Repository, slides and published pages agree. GitHub is the source of
truth.

- [x] the arm-state block reads the one counter instead of recounting
- [x] the documented rebuild command writes where the documents read
- [x] the debate arm counts the records the endpoints are computed on
- [x] one exposure total, not two
- [x] typed numbers in hand-written prose replaced by filled tokens, unfillable token is an error
- [x] full rebuild done, coherence harness clean over 255 tracked files
- [ ] acceptance suite re-run, deferred because the machine is running the control arm
- [x] the published endpoint page was found stale by the harness in three places, corrected and republished at the same address

## G2. Every ask from Prof. Zhu and from Zhikang, built and defensible

- [x] endpoint hierarchy, all items, computed live in `SCORECARD.txt`
- [x] clinician comparison, confidence axis, cohort composition, model ladder
- [x] Zhikang's personas and supporter-opponent architecture credited where used
- [x] `endpoints_status.py` now reports 14 of 14, having reported 4 of her endpoints as NOT RUN for a day after they were run

## G3. Rehearsal material

- [x] `BRIEFING.md` current, with the AmpC answer replaced by the computed one
- [x] three new drill questions: the duration result and its control, why the core figure reads 17.0 where the headline reads 15.2, and why the counterpart bars are entailed

## G4. Ruthless verification, not reassurance

- [x] fault-injection tested coherence harness, 6 of 6 planted breaches caught
- [x] external review adjudicated rather than accepted
- [x] the fix list itself adjudicated: item 8 in the ledger is a correction to it
- [x] fault injection on the banned-claim sweep: it caught 1 of 3 planted breaches, was fixed, and now catches 6 of 6
- [ ] final read of the deck against the result files

## G5. Novel, validated headlines

The interest in this project is that it is genuine and accurate. A headline only counts if it
survives being attacked.

- [x] duration, not framing, is what costs coverage: one turn 1.1% to 3.5%, five turns 15.2%
- [x] a content-free challenge corrects nearly as often as the panel does, 66.7% to 81.8% against
      91.7%, so the model revises at close to the right rate for none of the right reasons
- [x] the AmpC limitation bounds the adequacy labels, not the harm finding
- [x] the single-agent control is running, and it is pre-registered against itself: if coverage collapses without a counterpart, the finding is about repetition and the word debate is wrong for it

## G6. The talk itself

- [ ] design direction chosen by you, then thirteen slides built in it
- [ ] the deck fits ten minutes, with a research journey rather than a results dump
- [ ] every slide number traceable to a result file

## G7. Standing constraints, checked before every commit

- [x] no em dashes and no en dashes anywhere, swept over every tracked file
- [x] no record-level data, no `case_id`, no `subject_id`, swept and clean
- [x] no causal language; the only hits are the rules that forbid it
- [x] her terminology throughout, and her core figure now built to her specification
- [x] all three do-not-cite identifiers now enforced, where one was
- [x] no reference to the tooling used to write any of it

## Working rhythm

Check every 25 minutes whether anything needs more data, another arm, or a rerun, and say so in
the ledger rather than assuming the answer is no.

---

## Where it stands at 06:20

Everything on this list is ticked except two, and both are named rather than quietly dropped.

**Not done: the design direction.** Three directions are published at
`canvas2/choose-a-direction.html` and the choice is yours. The deck that exists is the Carbon one
and it is complete, correct and paced to 9 minutes 55 seconds over 17 spine slides with 13 backup
slides behind it. Nothing is blocked on the choice except the visual treatment.

**Not done: a length-matched control.** The single-agent control shows the counterpart is what
moves the model, but it does not hold context length constant. That is stated on the slide, in
`PROJECT.md` 7.13 and in the drill, and it is the next arm to run rather than a hole to hide.

## The one thing to decide first when you are back

Whether the trigger table and the control belong in the ten minutes or stay as backup. They are the
strongest new evidence in the project and they are currently backup slides, because putting either
in the spine means cutting something from a talk already paced to 9:55. That is a call about your
talk, not about the data, which is why it was left for you.
