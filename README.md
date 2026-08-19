# Two clinical LLM agents, one antibiotic, and a laboratory as referee

Do two language-model agents that talk to each other make a better clinical decision, or do they
just end up agreeing? I built an evaluation that can answer that, because it scores the
recommendation against something neither agent can see and neither agent can argue with: the
patient's own microbiology.

**Shomique Hayat** · UNIQ+ research internship, University of Oxford, Institute of Biomedical
Engineering · supervised by **Prof. Tingting Zhu** · 6 July, 20 August 2026

---

## Start here

| document | what it is |
|---|---|
| [START_HERE.md](START_HERE.md) | one page for a fresh session: findings, commands, ground rules, live state |
| [BRIEFING.md](BRIEFING.md) | the talk brief: the argument out loud, the gap, the ladder, and the question-and-answer drill |
| [deck/](deck/) | the UNIQ+ conference deck, generated from `results/*.json` by `deck/build_deck.py` |
| [deck/EVIDENCE.md](deck/EVIDENCE.md) | every claim in the talk, with its number, its result file and the script that produces it |
| [STORY.md](STORY.md) | the argument in order, every number reproducible |
| [PRIMARY_TEST.md](PRIMARY_TEST.md) | the test the protocol pre-specified before any run |
| [HEADLINE_RESULT.md](HEADLINE_RESULT.md) | same drug, different patient |
| [DATA_INTEGRITY.md](DATA_INTEGRITY.md) | how exposures are counted, and the defect that made it necessary |
| [METHODS.md](METHODS.md) | the design as the supervisor established it |
| [LIMITATIONS.md](LIMITATIONS.md) | what this does not show |
| [OUTSTANDING.md](OUTSTANDING.md) | supervisor asks, checked against disk |

Every number in those documents is generated from `results/`, not typed:

```
python3 analysis/primary_test.py
python3 analysis/policy_degeneracy.py
python3 analysis/canonical_numbers.py
python3 analysis/render_story.py
```


## The problem

Language models are trained to be agreeable. Push back on one and it tends to fold, even when it
was right. That is a mild annoyance in a chatbot and a real problem in a hospital, because folding
means changing a prescription.

People are now building clinical systems where several models confer and reach a decision
together, on the assumption that they check each other's work. To find out whether they do, you
need to know who was actually right, and in medicine you usually cannot, because the human you
would compare against was guessing too.

## The idea this project is built on

For a bloodstream infection, the hospital laboratory eventually tells you the answer. It grows the
organism from the patient's blood and tests it against each antibiotic in turn, returning
susceptible, intermediate or resistant.

That panel is an answer key that does not depend on the model *or* on the treating clinician. My
supervisor put the objection that produced this design more sharply than I could:

> "The doctor makes the right decision, that's a huge assumption you make."

So the doctor is not the reference. The bacteria are.

## What I built

Two prompted agents with deliberately opposed clinical incentives:

- **Agent A**, an infectious disease specialist, who wants coverage
- **Agent B**, an antimicrobial stewardship lead, whose job is to resist unnecessary breadth

They exchange five turns and settle on one drug from a closed 17-agent formulary. Every case is
run **twice**, once with each agent speaking first, so speaking order becomes a variable I
measure rather than a nuisance I average away.

- 200 MIMIC-IV bloodstream-infection cases, 400 ordering-runs, 2,000 turns
- Qwen3-4B-instruct, 4-bit, temperature 0, fixed seed, run locally
- Cohort content-hashed and scorer SHA-pinned **before the first model call**, so nothing could be
  tuned after seeing a result
- Decision point fixed at the moment cultures are sent, the model is graded on exactly the
  information the clinician had

## What I found

**The opening recommendation is not a decision.** The same antibiotic came back for 200 of 200
patients. Its outcome counts are identical, drug for drug, to a policy that ignores the patient
entirely.

**Under challenge it folds, every time.** 400 of 400 runs abandoned the opening position, and the
agent took the counterpart's drug whether that drug covered the organism or not.

**And that is the result, stated properly:**

| counterpart was… | n | adopted its drug | mean ΔQ | got worse | got better |
|---|---|---|---|---|---|
| **right** | 312 | **312/312 = 100%** | +0.043 | 0 | 13 |
| **wrong** | 88 | **88/88 = 100%** | **−0.853** | **52** | **0** |

Adoption is 100% in both rows. The behaviour is identical; only the counterpart differs. Decision
quality is not being weighed, it is being inherited. And it is one-directional in both cells.

**The system's output is whoever spoke second.** Final adequacy equals the counterpart's own
adequacy exactly: 77.0% in one direction, 79.0% in the other, matching to the case.

**The two agents already agreed before they spoke.** Measured from each agent's independent
opening, they concurred on 199 of 200 cases. Five turns of debate added 0.5 points of agreement
and cost 9.5 points of susceptibility concordance. The conversation had nothing to add and still
made things worse.

**A 110M encoder with no dialogue beat the debate.** BiomedBERT, no fine-tuning: 84.5%. The 4B
model alone: 87.5%. The 4B model after two-agent debate: 77.0%.

## What makes the numbers trustworthy

The most useful thing here is the least interesting one. A **neutral re-ask**, same question,
same decoding, no disagreement, moved the model in **0 of 200** cases. Without that zero, "it
folds every time" could just mean "it is unstable". With it, the movement is a response to being
contradicted.

Everything else follows the same discipline: frozen cohort, fixed seed, paired within patient, a
36-check acceptance suite re-run after every code change, and a deviation log recording every
post-freeze decision with the measurement that forced it.

## What I got wrong, and fixed

Kept here deliberately, because they are the parts I learned most from.

- **A leakage gate deleted 220 runs and I did not notice.** It was aborting whenever the *model*
  used the word "resistant" in its own reasoning. The dropout was not random, it removed exactly
  the runs where the model was thinking about microbiology. On the truncated data one arm read a
  perfect 160/160. On the recovered data it is 311/312, and the single counterexample was inside
  the deleted pile. Fixed, fault-injection tested at 10/10, every dropped run recovered.
- **A signal-detection result that was a confound.** A seeded arm gave d′ = 2.18, which looks like
  evidence discrimination. Drug-matched, it is exactly zero: ampicillin was refused 0/34 when the
  panel called it susceptible and 0/44 when it called it resistant. The model has a fixed spectrum
  preference. The pooled number was measuring which drugs happened to be resistant.
- **A confidence endpoint with no variance.** I elicited confidence 0 to 100 and pre-registered
  "confident" at >=80. Every observation came back 85, 90 or 95, all 200, before and after. A
  threshold that cannot fail is not a pre-registration. The endpoint is withdrawn.

## Repository

```
src/        harness, provenance gate, cohort assembly, scoring, metrics
arms/       one script per experimental condition
analysis/   the scripts behind each reported number
protocol/   pre-registered decisions, frozen before any model ran
figures/    generators and rendered assets, aggregates only
results/    aggregate outputs
docs/       method write-ups, literature, deviation logs, red-team findings
tests/      36-check acceptance suite plus gate fault injection
```

## Data

MIMIC-IV v3.1 under a PhysioNet credentialed data use agreement. **No patient-level data is in
this repository and none can be.** `case_id` is literally `subject_id` + `micro_specimen_id`, so
anything carrying one would republish two credentialed identifiers, every run file, every input
table and every per-case CSV is excluded by `.gitignore`.

To reproduce: obtain MIMIC-IV v3.1 access yourself through PhysioNet, place it locally, and run
the cohort build. The code is here; the data must be your own.

## Limitations, stated plainly

Observational data, so every result is alignment with recorded microbiology and never a claim that
a recommendation changed an outcome. One 4B model as the subject with a second as a robustness
check, the findings are scoped to these checkpoints. Only 3 of 17 formulary drugs ever appear as
a final answer. Confidence intervals treat ordering-runs as independent when they are patients
seen twice. The cohort is 200/200 microbiology-evaluable because it was selected on having an
interpretable panel, which is a declared post-baseline selection.

The largest gap: no single-agent arm at matched compute. Without it, "two agents perform like one"
is partly entailed by the abandonment rate rather than independently measured.

## Position in the literature

Susceptibility-arbitrated LLM antibiotic recommendation already exists (Antonie et al., *Antibiotics*
2026). Doctor-and-pharmacist agent pairs already exist (MedCoAct, arXiv 2510.10461). Multi-agent
coordination failing to help is already documented (Kim et al., *Nature Machine Intelligence*
2026, mean improvement 0.0% across 260 configurations).

What I have not found is any study that puts the arbiter *inside* the debate and measures the
**revision**, with both speaking orders on every case and a null arm separating being asked again
from being contradicted. If that study exists, this is a replication and I will say so.
