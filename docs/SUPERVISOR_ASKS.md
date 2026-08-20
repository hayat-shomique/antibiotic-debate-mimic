# What I was asked, and what I built

Every instruction from Prof. Tingting Zhu and from Zhikang Chen, quoted from the Teams threads as
they wrote it, against what exists on disk. Three items are deliberately not done and they are
listed last with their reasons, because a list that claims everything was completed is not worth
reading.

Statuses: **built** means it exists and produces a number. **built, with a stated deviation** means
the instruction was followed in substance but not to the letter, and the reason is recorded in the
deviation log. **deferred** means it is not done and the reason is on the closing slide.

---

## Prof. Tingting Zhu

| when | what she said | what I built | status |
|---|---|---|---|
| 13 Jul | *"UTI is too easy. It doesn't need to be tested with Culture."* and *"Blood infection is more deadly and also requires long course of antibiotics."* | The population is adult bloodstream infection. Urinary infection was dropped before any run. | **built** `METHODS.md` section 1 |
| 13 Jul | *"zero shot will not work, we can take something ready made ... And then I'm going to use some example of how it look like ... And if it doesn't, then you can move it to the next level, that is now your training from scratch."* | The escalation ladder, climbed in her order. Rung 1 zero-shot, 200 cases. Rung 2 few-shot, 200 cases. Rung 3 designed and not run, because rung 2 is what licenses it. | **built** slide 13, `results/fewshot.json` |
| 13 Jul | *"We need to narrow down to like maybe up to 10 drugs or whatsoever ... you need to actually treat it as a classification problem."* | A closed 17-agent formulary plus OTHER and ABSTAIN, so an off-list answer is a parse failure and never a wrong answer. | **built** slide 6, verbatim prompt |
| Jul | *"The doctor makes the right decision, that's a huge assumption you make."* | The reference standard is the patient's own susceptibility panel, not the clinician's prescription. This objection is the reason the study exists in this form. | **built** slide 3 |
| 18 Jul | *"Did you manage to finish the Physionet course yet to gain access?"* | CITI completed, PhysioNet credentialing granted 29 July, MIMIC-IV v3.1 pulled locally. | **built** |
| 22 Jul | *"I would prefer you let me know you have gained access to the data, explore the dataset first, before spending time drafting a concept note. How can you write a concept note without knowing what the dataset looks like?"* | The design was fixed after exploring the data, not before. The susceptibility panel as reference standard came out of that exploration. | **built** |
| 23 Jul | *"the culture takes 24 hours to grow and might be there for a couple of days to watch the bugs anyway. So it is interesting to see what LLM suggests before the culture result is out."* | The decision point is fixed at the moment cultures are sent. Measured on this cohort, the panel arrives at a median of 134 hours and zero panels exist at 5, 12 or 24 hours. | **built** slide 2 |
| 29 Jul | *"Why do you need to access the machine? I thought you are doing promting ... I think doing prompting doesn't need intense resources?"* | She was right. Every run in the project is local on the desktop at temperature 0 with a fixed seed. The 96GB GPU was never needed and was never used. | **built** `AUDIT.md` section 1 |
| 29 Jul | *"What about Medgemma and Deepseek?"* | MedGemma-4B is the domain comparison, size and quantisation matched to the study model. DeepSeek-R1-8B is installed and deliberately unused: its value is visible chain of thought, which is an interpretability question, and at 8B it cannot join a size-matched contrast. | **built, with a stated deviation** `docs/MODELS.md` |
| 29 Jul | *"There is 12B as well for MedGemma, 27B is not necessary."* | MedGemma has no 12B checkpoint. The Ollama tag list queried on 18 August returns nine tags, 4b and 27b only, no 12b at any quantisation. The instruction cannot be followed as written, so the arm is size-matched at 4B and the decision was recorded rather than made silently. | **built, with a stated deviation** `docs/deviation_log_proposed.csv` row D-MODEL-1 |
| 29 Jul | *"maybe it would be interesting to compare with some medical bert models which previously trained on EHR data already. See how well they perform without fine-tuning."* and *"like Med Bert or ClinicalBert etc."* | Four encoders, no fine-tuning, masked-token prediction over the same 17-drug formulary, same 200 cases, same panels. BiomedBERT reaches 84.5 per cent against the 4B model's 87.5, and every encoder is near-constant too. | **built** backup slide 20 |
| 29 Jul | *"Which dataset are you doing your experiments on and which population? I.e. disease(s). You cannot just look at everyone going into ICU."* | MIMIC-IV v3.1, adults with a panel-bearing first positive blood culture. 9,236 index events gated to a frozen cohort of 7,796, 200 evaluated. | **built** slide 5 |
| 30 Jul | *"You can also compare LLM with clinician, see if they agree or LLM is worse or better?"* | Computed on comparable ground: on the cases where both can be scored the model reaches 91.1 per cent and the clinician 90.6 per cent. The 25-point margin on the full cohort is a denominator artefact and is reported as one. | **built** `RESULTS.md` |
| Aug | *"I'd avoid making mortality alone the main measure ... heavily confounded by severity, source control, comorbidities, timing ... I'd build the evaluation around a hierarchy of endpoints."* | All eight endpoints of the hierarchy are computed, with mortality demoted and reported as a confounded secondary. | **built** backup slide 22, `SCORECARD.txt` |
| Aug | *"That directly answers the more interesting research question: does multi-agent communication improve clinical decision quality, or does it merely make the models agree?"* | The debate arm answers it: a live counterpart costs 9.5 points of coverage and abandons a correct answer 15.2 per cent of the time, while the panel gains 17.2 points at 1.1 per cent. | **built** slide 12 |
| Aug | The four-cell before and after classification, harmful revision rate and beneficial correction rate | Computed per condition, denominators stated, with the neutral control alongside. | **built** slides 9 and 12 |

---

## Zhikang Chen

| when | what he said | what I built | status |
|---|---|---|---|
| 13 Jul | *"firstly, you should apply for the access to the dataset, and download it"* and *"we usually use new version"* | MIMIC-IV **v3.1**, the version he pointed at, downloaded locally. | **built** |
| 13 Jul | *"you could also mention how the doctor and pharmacist agents challenge or verify each other's recommendations, what kinds of prompts are used to induce or detect sycophancy, and how you'll evaluate whether the final decision is clinically accurate and safe."* | All three are in the deck: the challenge protocol on slide 5, the exact pressure prompts on slide 6, and the panel adjudication on slide 3. | **built** |
| 23 Jul | *"you could use one llm to display supportor, and another one is opponent. And after discussion to see if they could reach agreement. In this way, we dont need doctors to participate. Although, the final results maybe wrong, but the thinking and discission process are meaningful."* | The two-agent debate arm, 409 exposures, both speaking orders, no clinician in the loop. His framing that the process is meaningful even when the answer is wrong is exactly what the transition table measures. | **built** slide 12 |
| 23 Jul | *"I recommand you could start from Qwen family, because you could use them freely."* | Qwen3-4B-instruct is the study model for every arm. | **built** |
| 23 Jul | *"start by operationalising sycophancy with clear, measurable indicators, for example, how often a model changes its initial stance after the dialogue, how uncritically it accepts the other agent's arguments, and how far its final recommendation deviates from evidence-based guidelines."* | All three computed. Stance change 400/400 = 100 per cent. Uncritical acceptance: the speaker moves onto the counterpart's drug in 400 of 1,600 responding turns, and a further 799 turns match because it already held that drug. Guideline deviation scored on the WHO AWaRe classification, which is externally maintained rather than invented here. | **built** `SCORECARD.txt`, new backup slide 23 |
| 23 Jul | *"design a structured discussion protocol: Agent A gives an initial treatment recommendation, Agent B counters with a opposing view, and they alternate roles over several rounds. After each round, record both agents' position shifts and the types of evidence they cite."* | Five turns, alternating, every case run in both speaking orders, every turn's position recorded. Agent A abandons its position in 400 of 400 runs; Agent B in 200 of 400, and never when it responds. | **built** |
| 23 Jul | *"inject different prior information into the prompts, for instance, assign Agent A the identity of an 'infectious disease specialist' and Agent B the role of 'antimicrobial stewardship lead', so that each has a clear, potentially conflicting incentive."* | Those two personas, in those words, are the system prompts. The tension is real: one wants coverage, the other restraint. | **built** slide 6, verbatim |
| 23 Jul | *"you can feed real de-identified case summaries (including microbiology cultures and susceptibility results) as the discussion input."* | Case summaries yes. The susceptibility results are deliberately **not** in the empiric input, because that would destroy the pre-culture decision point Tingting specified. They enter as their own condition, C2, which is what makes the evidence comparison possible at all. | **built, with a stated deviation** slide 5, conditions C0 to C2 |
| 23 Jul | *"evaluate which agent's final recommendation aligns better with actual clinical outcomes (e.g. subsequent resistance)"* | The per-agent half is done: Agent A and Agent B both reach 312/400 = 78.0 per cent. Subsequent resistance is not done. | **partly built, rest deferred** |
| 23 Jul | *"Because your time is limited, you need to complete the first step to satisfy your pre, and then, if you have time left, we could push the whole project forward."* | The first step is complete and the project went past it: 13 arms, 3,910 deduplicated exposures. | **built** `AUDIT.md` section 2 |

---

## The three things I was asked for and did not do

Each is named on the closing slide as a sequenced next step rather than quietly dropped.

**1. Transfer the test process to GPT and other hosted models.** Zhikang, 23 July: *"And then we can
transfer the test process to GPT and other LLM."* Not done, and it cannot be done with this data:
MIMIC-IV is credentialed under a PhysioNet data use agreement and record-level content may not reach
a hosted endpoint. The harness is model-agnostic, so the route is synthetic non-MIMIC cases. That is
the sentence on the closing slide.

**2. Ground the comparison in subsequent resistance.** Zhikang, 23 July. Not done. It needs repeat
cultures after the index event, a second index-time definition and a survivorship correction, which
is a study rather than an arm. Named on the closing slide so it reads as costed rather than ignored.

**3. Consult the users.** Tingting, 31 July, on what makes work land: *"you got to make sure that the
clinicians are going to obviously be doing it with their patients."* No practising clinician has
reviewed the personas, the formulary or the adequacy rule. It is on the limitations slide and it is
the first thing I would do next.

---

## One thing to check against your own thread

The repository dates the endpoint hierarchy inconsistently: `STORY.md` says 14 August, `METHODS.md`
and `SCORECARD.txt` say 18 August, and an earlier page said 17 August. The content is not in doubt
and every endpoint is computed, but the date is, so the deck now names her hierarchy without a date
and the rows above say only the month. Confirm the date from the Teams thread and it goes back in.

---

## How to check any row of this

Every number quoted here regenerates from the run data. `deck/EVIDENCE.md` maps each claim in the
talk to its result file and the script that produces it, `SCORECARD.txt` computes the endpoint
hierarchy and Zhikang's three indicators live, and `docs/deviation_log_proposed.csv` records every
post-freeze decision with the measurement that forced it.
