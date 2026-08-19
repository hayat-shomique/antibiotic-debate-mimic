# What Zhikang wants to see, read from his own messages

Source: two message sets from Zhikang Chen (MIMIC/antibiotics advice; supporter-opponent protocol; reference advice). Every item below is traced to his words, listed in `zhikang_requirements_map.csv`. Nothing here is inferred beyond what he wrote.

---

## His "first step" is the dual-agent debate, not a single-model run

This is the most important thing to get right, and it cuts against the trim.

> *"for mimic dataset, the first step is to use this dataset to see if llm could achieve our ideas, you could use one llm to display supportor, and another one is opponent. And after discussion to see if they could reach agreement"*

> *"Because your time is limited, you need to complete the first step to satisfy your pre, and then, if you have time left, we could push the whole project forward."*

Read together: the thing he wants completed for your presentation is **the two-agent supporter/opponent setup**. Every protocol paragraph in his message is the Agent A / Agent B discussion design, initial recommendation, counter-view, alternating rounds, position shifts logged. The single-model "Phase 1 under scripted pressure" framing is **yours**, from your own whiteboard message, not his.

So the honest position is: **the compute arithmetic and Zhikang's sequencing disagree.** The dual-agent arm is 21 % of your per-case budget and cannot be powered at pilot N, but dropping it entirely means arriving on 18 August without the thing your collaborator asked you to complete first. That is a real tension, and it is yours to resolve with him rather than something his messages resolve for you.

**The resolution that serves both.** Run the trimmed single-model design as the powered arm (N≈360, power ~0.91) *and* a small dual-agent demonstration on a 30 to 40 case subset. The subset costs only **0.7 to 0.9 h**, trimming the main run from N=383 to N≈358 pays for it, and power barely moves (0.93  to  0.91). You then present a powered single-model result plus a working two-agent demonstration with round-by-round trajectories, labelled explicitly as an unpowered illustration.

That is not a compromise, it is what he actually licensed: *"the final results maybe wrong, but the thinking and discussion process are meaningful."* He is telling you the debate trajectory has value **independent of statistical power**, which is exactly what a 35-case demonstration can deliver honestly.

**The argument you still need to make to him**, in your own words: a baseline measure of single-model stability is a prerequisite for interpreting any debate result, because a flip inside a two-agent exchange is uninterpretable unless you know how often that model flips to content-free pressure alone. The Nature Machine Intelligence capability-saturation finding makes the same point from the multi-agent side, any dual-agent claim needs a budget-matched single-agent control. That is a genuine methodological argument for running the single-model arm first. But it is *your* argument, and he has not agreed to it yet. Put it to him before the 18th.

His reference advice points the same way on depth: *"show her your ability to do PHD from your insights about one project and your insistency on one thing"*, and *"just do it from small projects."* Insistence on one thing, depth on a narrow claim, carried to completion. That is an argument against the four-model, four-sub-type sprawl, but it is not an argument for dropping his debate structure.

---

## The seven things he named that he expects to see

1. **Three separate sycophancy indicators, not one index.** He specifies stance-change frequency, uncritical acceptance of the other agent's arguments, and deviation from evidence-based guidelines. He never mentions a composite. Your EDI collapses these into one number that can read as zero for opposite reasons, rigid or pliable. Report his three first; derive the composite after.

2. **Guideline deviation as a second yardstick.** This is not a rephrasing of the susceptibility panel, it is an independent standard. A drug can be guideline-concordant and the isolate resistant to it; a drug can be off-guideline and active. A binary "in local empiric guideline" flag per drug is cheap to add and turns that dissociation into a result rather than a confound.

3. **Round-by-round position shifts *and the evidence cited*.** He wants a trajectory, not an endpoint. The turn-of-collapse measure already costed covers the first half; the second half, what the model *cites* when it caves, is free from logs you are already writing, and it is the difference between "it flipped" and "it flipped while invoking authority."

4. **The actual prompts.** He asks twice what prompts induce and detect sycophancy. Put the literal text of each pressure type on a slide. He is asking to inspect the instrument, and an instrument you can show is the whole credibility of a behavioural measure.

5. **Role identities with conflicting incentives**, ID specialist versus stewardship lead. Note this is genuinely different from your blinded pharmacist: yours guarantees the challenge carries no evidence, his guarantees the challenger is motivated. Both are valid; they measure different failure modes. Name the choice out loud rather than letting it look like you missed his.

6. **Alternating roles across rounds.** You have a fixed proposer and fixed challenger. Alternation is a symmetry control that separates "the challenger role induces caving" from "this model caves." Costs nothing to add to the Phase 2 specification you present unrun.

7. **Accuracy *and safety* of the final decision.** Safety here is asymmetric in a way accuracy is not: under-treatment threatens the patient, over-treatment drives resistance. Yuan's over/optimal/under-treated taxonomy already gives you the harm direction. A bare hit rate does not answer his question.

---

## Two places your design and his diverge, handle these deliberately

**He wants susceptibility results fed into the discussion; you blind them.** His words: feed case summaries *including microbiology cultures and susceptibility results* as the discussion input. Your C0 is pre-culture only, with the panel withheld as ground truth.

The reconciliation is genuinely strong and you should state it plainly: **his suggestion is your C2 arm.** You did not discard the idea, you promoted it from baseline input to an experimental condition, which is what lets you measure whether the model *updates* on real evidence rather than just whether it can read an answer off the prompt. Left unstated, this looks like you ignored him. Stated, it looks like you understood the design well enough to improve its position in the experiment.

**He treats the debate as generating agreement; you score correctness externally.** You already have this right, agreement is never truth. But he explicitly cares about convergence, and *"the final results maybe wrong, but the thinking and discussion process are meaningful"* is him licensing the process itself as a legitimate result. That is unusually useful for a low-N pilot: log agreement rate as a descriptive outcome, and the trajectory carries weight even where the interval on the headline effect is wide.

---

## One thing to raise with him early, not on the day

His sequencing is *"start from Qwen... and then we can transfer the test process to GPT and other LLM."* Under the MIMIC DUA you signed, MIMIC-derived content cannot go to a hosted service, so the transfer step as written does not apply to the case prompts. There is a clean version, transfer the *harness* and validate on synthetic or public non-MIMIC cases, but the distinction should come from you, in advance, rather than surfacing as an objection in a group meeting.

---

## Net assessment

Of eleven things traceable to his messages: one is aligned, four are partially covered, three are missing, two diverge reconcilably, and **one is a direct conflict**, his first step is the dual-agent debate, and your plan drops it. None of the *other* gaps is expensive. The three missing items, guideline flag, prompt-text slide, role alternation in the spec, are hours of work, not days, and two of them are documentation rather than compute.

The single most important consequence is that his instruction and the feasibility arithmetic **do not** agree, and pretending otherwise would put you in a group meeting having quietly dropped your collaborator's stated first step. Run the powered single-model arm at N≈358 *and* a 30 to 40 case dual-agent demonstration (0.7 to 0.9 h, power cost ~0.02), present the demonstration as an unpowered illustration of the debate trajectory, and make the case to him beforehand that single-model stability is the baseline any debate result has to be read against.
