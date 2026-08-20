# Talk brief

For the 90 minutes before the UNIQ+ conference. Read section 1 and 3 twice, say section 2 out loud
once, then drill section 8. Everything here is checked against the repository, and where a number
appears it names the file that produces it.

Deck: `deck/Shomique_Hayat_UNIQ_antibiotic_agents.pptx`, 25 slides, 17 core and 8 backup, speaker notes on
every one. The project in one document is `PROJECT.md`.
Rebuild it with `python3 deck/deck_figures.py && python3 deck/build_deck.py`.

---

## 0. The room, before anything else

| | |
|---|---|
| slot | **12:15 to 12:30**, Thursday 20 August, MPLS 2 of 3, **Kloppenburg room**, Exeter College Cohen Quad |
| chair | Dr Tim Hageman |
| format | **10 minutes of talk, 5 of questions.** Informal, not assessed |
| audience | other interns and some supervisors, **aimed at a general audience with no knowledge of the subject area** |
| arrive | the room starts at 09:00 and the guidance is to be there 15 minutes before your session |

**Two talks in your room set you up, and you should use them.** At 11:30, Manaan Shahid presents
Dr Jialin Yu's *Efficient Communication with LLM Agents*. At 09:30, Swera Gulfam and Tawfeeq Hamayun
present Dr Seth Flaxman's *Understanding and mitigating bias in medical AI*. By the time you stand up,
the room has already heard about agents communicating and about bias in medical AI. Your line, if it
fits the mood: this morning you heard how agents can communicate efficiently, and how medical AI can be
biased. I spent the summer asking whether the communication makes the clinical decision better, and in
this one setting there is an answer key that neither agent can argue with.

**What the guidelines ask for:** an overview of the research topic, key findings and conclusions, and
what you learned. Slides 14, 15 and 16 carry the conclusions, and the honest-mistakes material on
backup slide 21 is the strongest answer to what you learned.

---

## 1. The 45 second version

> Language models are trained to be agreeable. People are now building clinical systems where
> several models confer and reach a decision together, on the assumption that they check each
> other's work. I tested that assumption on 200 real bloodstream infection cases, and the thing
> that makes the test work is the referee: the patient's own laboratory susceptibility panel, which
> neither agent can see and neither agent can argue with.
>
> When a second agent argues a case, the first abandons a correct recommendation 15.2 per cent of
> the time and coverage of the organism falls 9.5 points. Give the same system the laboratory panel
> instead and harmful revision is 1.1 per cent and coverage rises 17.2 points. So communication
> makes the decision worse and evidence makes it better.
>
> The part I did not expect is that on a standard accuracy endpoint this failure is invisible.
> Score whether the answer was right and the debate looks harmless. Score what kind of answer it
> was and a sentence containing no clinical evidence at all pushes carbapenem use from 0 to 84 per
> cent. The contribution is not that models are agreeable, that is known. It is that the usual way
> of measuring the harm cannot see this one.

Say the middle paragraph slowly. Those are the two rows of the table on slide 14.

---

## 2. The three minute version for someone with no clinical background

Use these five beats, in this order. No jargon until you have earned it.

1. **The situation.** Someone comes into hospital with bacteria in their blood. That kills people in
   days, so you have to give an antibiotic now. But you do not yet know which bacterium it is, and
   different bacteria need different drugs. The doctor is guessing, sensibly, from experience.
2. **The answer arrives later.** The lab grows the bacterium from the blood and tests it against each
   antibiotic in turn. On my cohort that takes a median of 134 hours. So there is a real answer, and
   it arrives days after the decision was made.
3. **Why that is a gift for evaluation.** Normally, to grade a medical AI, you compare it with what a
   doctor did, which assumes the doctor was right. My supervisor said the sharpest version of this:
   "the doctor makes the right decision, that's a huge assumption you make." Here I do not need the
   doctor. The bacteria tell you who was right.
4. **The experiment.** I gave the case to two AI agents with opposite jobs. One is an infectious
   disease specialist who wants to cover the infection. One is a stewardship pharmacist whose job is
   to stop people over-prescribing. They argue for five turns and settle on one drug. Then I check
   that drug against the patient's lab result. And critically, I run three other versions of the same
   case: one where nobody disagrees, one where somebody disagrees but says nothing of substance, and
   one where the model is simply handed the lab result.
5. **What happened.** Being disagreed with by an empty sentence moved the model in 90 to 100 per cent
   of cases. Being handed the actual laboratory result moved it in 54 per cent. It responds more to a
   person pushing back than to the evidence. And when a real second agent argues, the final answer is
   worse than the one it started with.

**Analogy that lands with non-specialists:** it is a junior doctor who changes the prescription
because a senior frowned at them, not because a test came back. The test is the thing that should
move a prescription.

**Do not use these words without defining them in the same breath:** empiric, susceptibility panel,
carbapenem, sycophancy, McNemar, ICC.

---

## 3. Ten numbers, and what each one does not mean

| number | what it is | what it does not mean |
|---|---|---|
| **87.5%** | baseline coverage: 175 of 200 opening recommendations cover the organism that grew | not skill. It is one drug given to everybody. A constant meropenem policy would score 96.0% |
| **1 distinct drug** | the model recommends piperacillin-tazobactam for 200 of 200 patients before any conversation | not a bug in the prompt. Nothing in the case block predicts the organism |
| **0 of 70** | cases changed under the neutral re-ask, every framing | this is the control, not a result about pressure. It is what makes the pressure number mean something |
| **90 to 100%** | cases changed under an empty challenge sentence, across four framings | not "the model is unstable". Cn is zero, so the movement is specific to being contradicted |
| **54.3%** | cases changed when handed the actual susceptibility panel | not a failure to read the panel. Slide 19 row 5: given the panel it repairs 82.6% of the runs that entered inadequate |
| **0.0 to 1.5%** | harmful revision under scripted pressure | this is why accuracy alone hides the problem. Do not present it as reassurance |
| **0 to 83.7%** | carbapenem use, baseline to under pressure | prescribing behaviour, not demonstrated patient harm. Carbapenem overuse drives resistance at population level |
| **15.2%** | harmful revision when a live second agent argues, 52 of 341 | the debate arm, not the scripted-pressure arm. Different stimulus, different number, both real |
| **OR 1.0, p = 0.7151** | same drug proposed, patient varied: adoption identical | it is a null and the null is the finding. Within a drug, coverage makes no difference |
| **p = 0.0004** | few-shot loses 18 correct answers and gains 2, exact McNemar on 175 paired cases | few-shot did change behaviour, it moved off the constant. It just changed it for the worse |

Two more worth having: **70 of 200** cases enter the pre-specified primary test, and **ICC 0.913**,
which makes 400 ordering-runs behave like an effective 209.

---

## 4. The spine, slide by slide, with the sentence that moves you on

| # | slide | target | the one claim | the sentence that moves you on |
|---|---|---|---|---|
| 1 | title | 15s | Who I am, one question | "The question is not mine, it is my supervisor's." |
| 2 | the clinical decision | 40s | The drug is chosen before the evidence exists | "So there is a real answer, and it arrives later." |
| 3 | the referee | 40s | The doctor is not the reference, the bacteria are | "With a referee you can ask a question you could not ask before." |
| 4 | the question | 15s | Her sentence, verbatim | "Here is how one patient becomes one measurement." |
| 5 | the pipeline | 50s | Six stages, and only stage 4 ever changes | "And this is what the model actually sees." |
| 6 | the instrument | 50s | The prompt verbatim, six patient fields, four pressure sentences | "So what does it do before anyone speaks to it." |
| 7 | result one | 45s | The default is a constant, and it scores 87.5 | "Does it move when somebody speaks to it." |
| 8 | result two | 55s | c is zero, b is 63 to 70, p on the order of 1e-21 | "It moves. Does the movement hurt anybody." |
| 9 | result three | 25s | On accuracy, almost no damage | "If I stopped here I would be wrong, and she told me where to look." |
| 10 | result four | 50s | An empty sentence, 0 to 84 per cent carbapenem | "One more control before the answer." |
| 11 | result five | 35s | Same drug, different patient, gap zero | "Now the arm that answers the question." |
| 12 | the answer | 55s | Live agent minus 9.5 points, panel plus 17.2 | "So can prompting fix it." |
| 13 | rung two | 35s | Few-shot breaks the constant and costs coverage | "Which is what licenses the next rung." |
| 14 | the contribution | 30s | Invisible on accuracy, severe on stewardship | "What it does not show." |
| 15 | limitations | 25s | Six bounds, stated as design properties | "Where this goes." |
| 16 | close | 20s | The laboratory is the referee, the measurement is the contribution |  |

Sixteen slides, **9 minutes 45 seconds** of targets, which leaves you fifteen seconds of slack and
five minutes of questions. Every slide's speaker notes now open with its target and the running total,
so you can pace the run-through off the deck itself.

**Backup slides, after the close, for questions only:** 17 the gap, 18 design, part one, 19 design, part two, 20 the models, 21 how it was kept honest, 22 the endpoint hierarchy.

---

## 5. The gap, in the form you will be asked for it

Someone will ask "has this not been done". The answer has three parts and you should give all three,
in this order, because conceding the first two is what makes the third credible.

1. **Yes, collaboration between agents is already known not to help reliably.** Kim et al., Nature
   Machine Intelligence 2026, the paper Tingting sent me: across 260 configurations with prompts,
   tools and compute held constant, the mean multi-agent improvement is 0.0 per cent. MedAgentBoard
   at NeurIPS 2025 finds the same in medicine.
2. **Yes, sycophancy is documented.** Position abandonment under challenge, and adopting a peer's
   answer whether it is right or wrong, are established results. I do not claim to discover either.
3. **What is missing is the arbiter.** In those studies the thing that decides who was right is a
   benchmark key or another model. I arbitrate against the individual patient's own susceptibility
   panel, which neither agent can see, neither can argue with, and neither produced. That lets me
   report something the literature does not have: transitions conditioned on what the run entered
   with, and a harm that appears only on the stewardship endpoint.

The full claim-by-claim adversarial check is `docs/LITERATURE_PRESSURE_TEST.md`. It is the document
to point at if someone presses hard, and it is deliberately unflattering.

---

## 6. The ladder, and the training plan you are being asked to justify

The order came from Tingting at the first meeting: zero-shot, then few-shot, then training only if
few-shot fails.

| rung | status | what it produced |
|---|---|---|
| 1. zero-shot | **complete, 200 cases** | one constant recommendation for every patient, 87.5% coverage |
| 2. few-shot | **complete, 200 cases** | 6 drugs instead of 1, 34.5% narrow prescribing, coverage falls to 84.0% on the paired subset, exact p = 0.0004 |
| 3. fine-tuning | **designed, not run** | out of scope for the internship, and rung 2 is what licenses it |

**How few-shot was kept honest,** because this is the obvious attack. Exemplars are drawn from a pool
disjoint from the 200 evaluation cases, disjointness asserted on `case_id` **and** on `subject_id` so
one patient cannot appear on both sides, a separate exemplar seed from the model seed, and the answer
in each exemplar is the narrowest agent the laboratory reports susceptible. The answer to a case
appears in that case's own exemplars only 36.0% of the time, so it is not copying. `arms/fewshot_pass.py`.

**The rung-3 design, if asked what you would actually do.** Say this, it is the strongest 40 seconds
you have on future work:

- **Target.** Not the clinician's prescription, because that assumes the clinician was right. The
  label is the set of agents the panel called susceptible, so it is a set-valued target and any
  member counts as correct.
- **Split.** Patient-level, on cases outside the frozen 200, held out on `subject_id` not `case_id`.
  The frozen evaluation cohort stays untouched, which is the same discipline as rung 2.
- **The trap, and this is the interesting part.** Fine-tuning on coverage alone will produce
  carbapenem for everybody, because on this cohort a constant meropenem policy scores 96.0 per cent.
  The objective has to be coverage penalised by spectrum, weighted by the WHO AWaRe class, or you
  will train exactly the failure this project measured.
- **Pre-specified success criterion.** Beat the best constant policy on coverage **and** on spectrum
  simultaneously, on held-out patients, and retain it under the C1 pressure conditions. Beating one
  and losing the other is not success, it is the degenerate policy again.
- **Compute.** LoRA on the 4B checkpoint fits locally; the IBME cluster is the alternative Tingting
  already suggested, and MIMIC on the cluster is a data-governance question I would need to settle
  first.

---

## 7. The models, in one breath each

- **Qwen3-4B-instruct, 4-bit, temperature 0, seed 20260818.** The subject. Every debate arm.
- **MedGemma-4B, same quantisation.** The domain comparison. Same size on purpose: a 12B model would
  vary scale and training corpus at once and answer neither question. It produces a near-constant
  opening too, on a **different** drug, which localises the choice of drug to the weights rather than
  to the prompt.
- **Four BERT encoders, 110M, no fine-tuning.** Tingting asked for a medical BERT with no
  fine-tuning. BiomedBERT reaches 84.5 per cent against the 4B model's 87.5, and every encoder is
  near-constant too. That is the sharpest way to say this task does not discriminate what people
  think it discriminates.
- **Why local.** MIMIC-IV is credentialed under a PhysioNet agreement, so record-level data cannot
  reach a hosted service. The harness can transfer to GPT and other hosted models on synthetic
  non-MIMIC cases, which is Zhikang's ask and is on the closing slide.
- **DeepSeek-R1-8B** is installed and unused. If asked: its value is visible chain of thought, which
  is an interpretability question, and at 8B it cannot join the size-matched contrast, so using it as
  a fourth accuracy column would be dishonest.

---

## 8. Question and answer drill

Read the question, answer out loud, then check. The bold sentence is the one to lead with.

**Q. Is 200 cases not very small?**
**It is small, and it is paired.** Every case is its own control: the same patient is put to the same
model in four conditions with a fixed seed, so I am not comparing 200 patients against another 200
patients, I am comparing each patient against himself. That is what gets p on the order of 1e-21 out
of 70 evaluable cases. The cohort is small because everything runs locally under the data agreement,
and I would rather have 200 cases in four conditions than 2,000 in one.

**Q. Your model recommends the same drug for everyone. Is the whole study not just measuring a broken model?**
**That is the first result, and I put it on slide 9 deliberately.** But look at what the constant
scores: 87.5 per cent. Nothing in the prompt predicts the organism, so one broad empiric agent for
everybody is the rational policy under that uncertainty, not a broken one. It does bound what I can
claim, and I say so: this study cannot separate a model that reasons about patients from a model with
one good default. What it can still do is ask what moves that default, and the answer is social
pressure rather than evidence.

**Q. Would a bigger model not just fix this?**
**Possibly, and I cannot tell you from this data.** One 4B checkpoint is the subject and a second 4B
is the comparison, so my findings are scoped to those checkpoints. What I can say is that the
degenerate policy is not unique to the generative model: four BERT encoders show it too, and a 110M
encoder gets within three points of the 4B model. That makes me think it is a property of the task as
posed rather than of capacity. Testing scale is a clean experiment and it is the wrong one for the
size-matched contrast I needed.

**Q. Isn't sycophancy already well known?**
Take the three-part answer in section 5. Lead with **"yes, and I do not claim it".**

**Q. Carbapenem for everybody actually maximises coverage on your cohort. So is the model not right to escalate?**
**This is the sharpest question in the deck and the answer is yes and no.** Yes: a constant meropenem
policy scores 96.0 per cent coverage on this cohort, so if coverage is your only endpoint,
carbapenem-for-all wins. That is exactly why coverage cannot be your only endpoint, and it is why
stewardship exists as a discipline. No: the escalation here is not paid for by anything, because it
happens in response to a sentence containing no clinical information, and coverage was already 87.5
with harmful revision near zero. Under the actual panel the model escalates far less, 21 per cent,
and there the broadening is earned.

**Q. You say harmful revision is 15.2 per cent with a live agent but 0 to 1.5 per cent under pressure. Which is it?**
**Both, and the difference is the point.** They are different stimuli. The pressure conditions are
four fixed sentences with no content, and the model usually swaps to another drug that also covers.
The debate arm is a second model constructing a case for a specific drug, and there it lands on
something that fails the patient in 52 of 341 opportunities. A scripted challenge and a reasoned
challenge are not the same intervention, which is itself a finding.

**Q. Only 70 of your 200 cases enter the primary test. Is that not fatal?**
**No, and I separate the two reasons rather than pooling them.** 122 of those cases have no pressure
row at all, because the pressure arm ran 78 of the 200 in my frozen selection. Only 8 are dropped for
an indeterminate outcome. Those are different things and I report them separately.
The missing 122 are benign and I measured that rather than assuming it: the 78 are a contiguous prefix
of a seeded random selection, so which cases are missing is a property of how far the arm got, not of
the case, and baseline adequacy inside the covered subset is 88.5 per cent against 87.5 across all
200. Nothing that was never run can change b or c, which are counted on complete cases only, and c is
zero in every framing.

**Q. What is McNemar and why is it the right test?**
**It is the test for a before-and-after on the same subject.** It ignores everybody who did the same
thing in both conditions and asks, among the people who changed, whether they changed in one direction
more than the other. Here b is the cases that changed under pressure only and c is the cases that
changed under the neutral turn only. c is zero, so the test is nearly degenerate in the good sense.

**Q. Your two agents are the same model. Is that not just one model talking to itself?**
**Yes, and that is a limitation I state.** Both personas are served by the same checkpoint, so what I
measure is deference within a homogeneous system. A heterogeneous pair is a different and interesting
experiment. It also means I should not report the agreement between them as an independent result,
because once you know the model abandons its position and adopts the counterpart's drug, the diagonal
agreement is entailed rather than discovered. I flag that in the repository.

**Q. Have you shown any patient harm?**
**No, and I am careful about this.** MIMIC-IV is observational. Every claim is alignment with recorded
microbiology or counterfactual appropriateness of a recommendation. The stewardship result is a
difference in prescribing behaviour. Carbapenem overuse drives carbapenem-resistant Enterobacterales
at population level, but I cannot and do not show a resistance outcome in these patients.

**Q. Did a clinician check any of this?**
**No, and it is on the limitations slide.** The personas, the 17-drug formulary and the adequacy rule
come from my supervisor and from published guidance, not from a treating physician or a clinical
microbiologist. The stewardship interpretation is standard in the literature but has not been checked
against a clinician's judgement on these specific cases. If I continue this, consulting a stewardship
pharmacist about what they would want from such a system is the first thing I would do, and it is on
the closing slide.

**Q. How do you know the model was not just told the answer somewhere in the prompt?**
**Three ways.** The case block passes a provenance gate that aborts on any organism name or
susceptibility phrasing. The pressure sentences are a closed set of four and I censused all 312 turns
rather than sampling: zero contain any microbiology. And the model's own turns are hashed and measured
rather than aborted, because a model writing "await culture results" is reasoning aloud, not leaking.

**Q. Is your leakage gate not just deleting inconvenient data?**
**It was, and I caught it.** An early version aborted whenever the model itself used the word
resistant, which deleted 220 runs non-randomly, exactly the runs where it was reasoning about
microbiology. On the truncated data one arm read a perfect 160 of 160. On the recovered data it is 311
of 312, and the one counterexample was inside the deleted pile. Fixed, fault-injection tested at 10 of
10, every dropped run recovered. It is in the repository as a defect, not a footnote.

**Q. Why is your confidence endpoint missing?**
**Because I withdrew it.** I pre-registered "confident" at 80 or above, then every one of 200
observations came back 85, 90 or 95, before and after. A threshold that cannot fail is not a
pre-registration, so reporting it as a null would be worse than removing it.

**Q. Why not use GPT-4 or Claude?**
**Because the data is credentialed and cannot leave this machine.** That is a PhysioNet data use
agreement, not a preference. The harness transfers to hosted models on synthetic non-MIMIC cases and
that is on the closing slide as Zhikang's ask. It is also why the study model is 4B: it is what runs
locally at temperature 0 with a fixed seed, which is what makes the paired tests valid.

**Q. What would change your mind about the finding?**
**A heterogeneous pair, or a live opposing agent that varies its argument with the case.** If a
stronger or differently trained counterpart produced beneficial corrections at a rate that outran the
harmful ones, the net effect would flip and I would say so. The arithmetic is stated on the record:
at this base rate the break-even correction rate is unattainable, so the sign of the net effect is
forced by the base rates rather than discovered. That is a caveat I raise myself rather than wait for.

**Q. What is the single most useful thing you did?**
**The neutral control.** Without a condition where the prompt grows and nothing else changes, "it
folds under pressure" could just mean "it wobbles when spoken to". Zero of 70 is what turns the rest
of the deck from a description into an inference. It cost nothing and it is the cheapest thing anyone
evaluating a multi-agent system could copy.

**Q. What did you find hardest?**
Answer honestly and briefly, then return to work: keeping the analysis honest while the numbers kept
moving. Every document in the repository is generated from result files rather than typed, precisely
because I corrected numbers three times and did not want a stale sentence surviving somewhere.

---

## 9. If you do not know the answer

Use this shape, in this order, and never bluff a number.

1. **Name the honest state.** "I do not have that measured."
2. **Give the nearest thing you do have.** "The closest number I have is X, which speaks to a
   neighbouring question because ..."
3. **Say what it would take.** "To answer yours properly you would need arm Y, and the reason I did
   not run it is Z."

Worked examples.

- *"What happens with three agents?"* I have not run it. The nearest thing I have is the four
  pressure framings, where a single unsupported challenge already moves it 90 to 100 per cent, so I
  would expect a majority condition to saturate rather than reveal anything new. The published range
  suggests unanimity matters more than count, and that is the experiment I would run.
- *"Does this hold for Gram-positive infections?"* Not tested. My cohort selects on having an
  interpretable panel, which enriches Gram-negatives, and the formulary is built around them. Testing
  the Gram-positive half means a different intrinsic-resistance table, and that is genuine work rather
  than a rerun.
- *"What about inducible AmpC?"* Unhandled, and I say so on the limitations slide. Roughly 18 per cent
  of this cohort can de-repress AmpC, so a recommendation scored adequate against the reported panel
  could still fail clinically. Correcting it needs organism-specific rules.

If someone asserts something you believe is wrong, do not fold. That is literally the failure mode you
are presenting. Say: "that may be right, and here is what my data shows, so let me check it and come
back to you." Then check it.

---

## 10. Things not to say

Each of these was checked and cut for a reason.

- Do **not** claim sycophancy or peer conformity as a discovery. Both are published.
- Do **not** say the model "underperforms meropenem". Coverage on this cohort is maximised by the
  degenerate carbapenem-for-all policy, so that framing argues against your own stewardship point.
- Do **not** present the speaking-order effect as an independent discovery. With a near-constant
  opening and near-universal adoption, permuting order permutes the input to a nearly deterministic
  rule. Cohen's kappa is 0.178.
- Do **not** call the model "unstable". Cn is zero. It is stable and it is deferential, and those are
  different words.
- Do **not** quote the confidence endpoint. It is withdrawn.
- Do **not** say anything caused a patient outcome. Observational data, always alignment or
  counterfactual appropriateness.
- Do **not** quote a number from memory that is not in section 3. Say "there is a slide on that" and
  go to the backup.

---

## 11. Sentences worth having ready

- "The doctor is not the reference. The bacteria are."
- "It is moved more by a person disagreeing with it than by the laboratory result."
- "Zero of 70 under a neutral turn is what makes the rest of this deck an inference rather than a
  description."
- "A sentence carrying no clinical evidence pushed it to last-line therapy for four out of five
  patients, and bought nothing."
- "Score whether it was right and debate looks harmless. Score what kind of answer it gave and the
  harm appears."
- "Examples taught it to vary its prescribing without teaching it which patient needs which drug."
- "The contribution is the referee, not the phenomenon."

---

## 12. The 90 minutes

| minutes | do this |
|---|---|
| 0 to 15 | read sections 1, 3, 5, 10. Out loud, not skimmed |
| 15 to 35 | open the deck, read the speaker notes on slides 9 to 16, say each one in your own words |
| 35 to 55 | full run through, standing, timed. Aim for your slot minus two minutes |
| 55 to 75 | section 8, cover the answers, say them cold. Any you fumble, say twice more |
| 75 to 85 | fix only what the run-through exposed. Do not add slides |
| 85 to 90 | section 11, then stop. Water, and open on slide 1 |
