# Resume after restart

Everything is on disk and pushed. Nothing is lost by restarting.

## One command to restart the experiments

```
cd ~/brain_run && ./go.sh
```

That resumes every arm from where it stopped. All three check what is already written and skip it,
so a restart costs only the calls that were in flight.

## State at 22:04, 19 August

| arm | done | target | note |
|---|---|---|---|
| D-MATCH-1 drug-matched | 86 | 224 | the headline experiment, already decisive |
| D-CALIB-1 calibration | 39 | 200 | the rebuilt confidence endpoint |
| few-shot | 0 | 200 | rung two of the escalation ladder |

Everything else is complete: debate 400/400, neutral control 200/200, panel reveal 400/400,
clean-context 200/200, self-consistency 200/200, confidence 200/200, C1 pressure 312 exposures,
ablation 60, degraded 60, seeded 172, plausible-wrong 166, encoders 4 x 200, MedGemma 200.

## Paste this into a fresh session

> Resuming the UNIQ+ antibiotic-debate project. Working directory ~/brain_run holds the run data
> and never leaves the machine under the PhysioNet DUA. The repository is
> ~/Desktop/antibiotic-debate-mimic, pushed to github.com/hayat-shomique/antibiotic-debate-mimic.
> Read RESUME.md, HEADLINE_RESULT.md, RESULTS.md and SCORECARD.txt in the repo, then run
> `cd ~/brain_run && ./go.sh` to restart the three unfinished arms. After that the job is the
> slide deck: one PowerPoint for the UNIQ+ conference, 12:15 tomorrow, Kloppenburg room, ten
> minutes to a general audience. No em dashes, no reference to AI tooling, Shomique Hayat is the
> sole author.

## The four results the talk rests on

**1. Same drug, different patient, zero difference.** Cefepime adopted 9/9 when it covers the
organism and 8/8 when it does not. Piperacillin-tazobactam 2/21 either way. Gap exactly zero
within each drug, ninety points between them. The model responds to the name, not the evidence.

**2. Six models, none looks at the patient.** Two generative and four encoders, one or two
distinct recommendations across 200 patients, a different favourite drug each. The differing
constants rule out the prompt.

**3. C1, the pre-registered primary arm.** Four unsupported challenges, 78 cases each. Safety
framing 100%, authority 97.4%, peer consensus 97.4%, bare doubt 89.7%. Paired McNemar: the three
that invoke a person are indistinguishable, bare doubt is significantly weaker than all three
(p 0.031, 0.031, 0.008). Under every one it escalates to meropenem rather than reconsidering.
Neutral floor 0/200.

**4. Two personas designed to disagree** open on the same drug in 199 of 200 cases before either
speaks.

## Where things live

| file | what it is |
|---|---|
| `HEADLINE_RESULT.md` | the drug-matched finding |
| `RESULTS.md` | every endpoint, EDI, the Yuan comparison, withdrawn claims |
| `SCORECARD.txt` | every supervisor ask with a live number |
| `METHODS.md` | the design and why each decision was made |
| `FINDING.md` | drug identity beats evidence |
| `LIMITATIONS.md` | clinical and statistical bounds |
| `CHANGELOG.md` | every corrected number with its original beside it |
| `FIXES.md` | 19 review findings, all closed |
| `RED_TEAM.md` | the adversarial review in full |

## Tomorrow

12:15 to 12:30, Kloppenburg room, Exeter College Cohen Quad. Chair Dr Tim Hageman. Arrive 08:45.
Ten minutes plus five of questions, general audience. At 11:45 in the same room, Manaan Shahid
presents "Efficient Communication with LLM Agents", which is worth watching and worth referencing.
