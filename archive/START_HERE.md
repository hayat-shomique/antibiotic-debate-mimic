# Start here

One page. Written so a fresh session, or a version of me with no memory of tonight, can be useful
within a minute.

## Paste this into a fresh session

> Resuming the UNIQ+ antibiotic-debate project. The repository is
> `~/Desktop/antibiotic-debate-mimic`, pushed to
> `github.com/hayat-shomique/antibiotic-debate-mimic` (private). The run data lives in
> `~/brain_run/runs` and never leaves this machine under the PhysioNet credentialed data use
> agreement, so nothing patient-level is ever committed or quoted back to me.
>
> Read `START_HERE.md`, `STORY.md`, `AUDIT.md` and `OUTSTANDING.md` before doing anything. Every
> number in every document is generated from `results/*.json`; if you need a number, run the script
> that makes it rather than reading it out of prose. `rebuild` in the shell regenerates all of it.
>
> All experiments are finished. The remaining deliverable is one PowerPoint for the UNIQ+
> conference, built only from claims the repository can reproduce. I am the sole author. No em
> dashes, no en dashes, no reference to AI tooling anywhere in any artefact.

## What the project found

The question, in the supervisor's words: *does multi-agent communication improve clinical decision
quality, or does it merely make the models agree?*

| what the agent hears | harmful revision rate | coverage of the organism |
|---|---|---|
| a scripted sentence with no content | 0.0 to 1.5% | unchanged |
| **a second agent arguing a case** | **15.2%** | **87.5% to 78.0%** |
| the susceptibility panel | **0.0%** | 78.0% to 95.2% |

Debate makes the decision worse. Evidence makes it better. Supporting results: the zero-shot policy
is a single constant that nonetheless scores 87.5 percent; the patient does not change the answer
while the drug name does; unsupported pressure drives carbapenem use from 0 to 84 percent without
improving coverage; few-shot breaks the constant but significantly degrades coverage
(p = 0.0004), which is the result that justifies moving to fine-tuning.

## Shell commands, available the moment a terminal opens

| command | what it does |
|---|---|
| `uniq` | one-screen status: repo, commit, arms running, models |
| `repo` / `runs` | cd to the repository / the run data |
| `rebuild` | regenerate every number and every generated document from the run data |
| `gogo` | resume any unfinished arm, each under a lock |
| `uniqdocs` | the documents worth opening, in order |
| `ghrepo` / `ghstat` / `push` | open the repository on GitHub / show its state / push |

Defined in `~/.zshrc` in a block marked `UNIQ+ antibiotic-debate project`. Delete that block to
undo; the previous file is at `~/.zshrc.backup-20260819`.

## Reading order

1. `STORY.md` the argument end to end, built on the supervisor's endpoint hierarchy
2. `PRIMARY_TEST.md` the test the protocol pre-specified before any run, with its attrition
3. `AUDIT.md` model health, per-arm data integrity, artefact provenance, endpoint status
4. `METHODS.md` the design and the three-rung escalation ladder
5. `LIMITATIONS.md` what this does not show, including where the design bounds the claim
6. `OUTSTANDING.md` supervisor asks still open, each checked against disk
7. `DATA_INTEGRITY.md` how an exposure is counted and the defect that made it necessary

## Ground rules that are not negotiable

**Data.** `case_id` is `subject_id` + `_` + `micro_specimen_id`, so quoting one republishes two
credentialed identifiers. No run file, no case block and no patient row goes into the repository,
into a document, or into a chat. `.gitignore` enforces the first; the rest is discipline.

**Numbers.** No number is typed into prose. Documents are rendered from `results/*.json` by the
scripts in `analysis/`. If a number needs changing, change the analysis, not the sentence.

**Concurrency.** Two processes writing one output file wrote every matched exposure twice on
19 August. Every arm now runs under a PID lock in `~/brain_run/.locks`. Start arms with `gogo`, not
by hand.

## State as of 20 August 2026, 00:43

All experiments complete. Nothing running. Repository at `bf4e921 Ignore PowerPoint lock files`.

| arm | exposures |
|---|---|
| debate | 409 |
| panel reveal | 400 |
| cross-model | 400 |
| C1 pressure | 312 |
| drug-matched | 224 |
| calibration | 201 |
| clean context | 200 |
| self-consistency | 200 |
| few-shot | 200 |
| support arm | 172 |
| plausible-wrong seed | 166 |
| C0 baseline (pressure arm) | 79 |

Counts are deduplicated exposures, not lines on disk. Regenerate this page with
`python3 analysis/render_start_here.py`, or regenerate everything with `rebuild`.

## The conference deliverables

| artefact | what it is |
|---|---|
| `deck/Shomique_Hayat_UNIQ_antibiotic_agents.pptx` | the talk, generated from `results/*.json` by `deck/build_deck.py`, speaker notes on every slide |
| `deck/deck_figures.py` | every chart in the deck, drawn from the same result files |
| `deck/EVIDENCE.md` | every claim in the talk mapped to its number, its result file and the script that produces it |
| `SUPERVISOR_ASKS.md` | every supervisor instruction, quoted, against what exists on disk |
| `BRIEFING.md` and `deck/brief.html` | the talk brief: the argument out loud, the ten numbers, the question drill |

Rebuild the whole deck with `python3 deck/deck_figures.py && python3 deck/build_deck.py`.

Slot: MPLS 2 of 3, Kloppenburg room, 12:15 to 12:30 on 20 August 2026, chaired by Dr Tim Hageman.
Ten minutes of talk, five of questions, aimed at a general audience.
