# Working rules for this repository

Read this before changing anything. These are not preferences, they are the reasons the numbers in
this project can be defended.

## What this is

An evaluation of two prompted clinical LLM agents, an infectious disease specialist and an
antimicrobial stewardship lead, arguing about an empiric antibiotic for a bloodstream infection, with
the patient's own susceptibility panel as the reference standard. `PROJECT.md` is the one document;
everything else supports it.

## Non-negotiable

**Patient data never enters this repository.** MIMIC-IV is credentialed under a PhysioNet data use
agreement. Run files live in `~/brain_run/runs` and stay there. `case_id` is `subject_id` + `_` +
`micro_specimen_id`, so quoting one republishes two credentialed identifiers. Never print a case_id,
a subject_id or a patient row into a file, a document, a commit message or a chat. Aggregates only.

**No number is typed into prose.** Every document and every slide is rendered from `results/*.json`
by a script. If a number needs to change, change the analysis, not the sentence. A number that
appears in two places must come from one source. If you find yourself typing a figure, stop and wire
it to the result file instead.

**Fail loudly, never silently.** A helper that cannot find its value must raise with an instruction,
not return a placeholder that renders as if it were a number. A partially complete arm must produce
an error, not a quietly wrong denominator.

**Claims are bounded.** MIMIC-IV is observational. Phrase every finding as alignment with recorded
microbiology or counterfactual appropriateness of a recommendation, never as a recommendation
causing a patient outcome. Say "in this setup, agent-to-agent argument reduced coverage", not
"communication makes decisions worse".

**Use the supervisor's terminology.** The endpoint hierarchy, the four-cell classification (stable
correct, beneficial correction, harmful deference, no improvement), harmful revision rate and
beneficial correction rate, and spectrum appropriateness are Prof. Tingting Zhu's definitions.
Report them under her names, not under new coinages.

**No em dashes and no en dashes**, anywhere, including generated documents, slides and commit
messages. Use a comma, a colon, or the word "to".

**British English.** Prose is plain and declarative. Titles state the claim, not the topic.

## Rebuilding

```
python3 analysis/primary_test.py          # results/primary_test.json
python3 analysis/tingting_endpoints.py    # results/tingting_endpoints.json
python3 analysis/policy_degeneracy.py     # results/policy_degeneracy.json
python3 analysis/fewshot_analysis.py      # results/fewshot.json
python3 analysis/leakage_check.py         # results/leakage.json
python3 analysis/model_tiers.py           # results/model_tiers.json
python3 analysis/canonical_numbers.py     # results/RESULTS.json
python3 analysis/render_project.py        # PROJECT.md
python3 analysis/build_audit.py           # AUDIT.md
python3 deck/deck_figures.py              # deck/figures/*.png
python3 deck/build_deck.py                # the talk
python3 deck/build_evidence.py            # deck/EVIDENCE.md
```

Scripts that need pandas run under `$HOME/.claude-science/conda/envs/brain/bin/python`. The shell
function `rebuild` does the document half. The acceptance suite is `tests/acceptance.py` and needs
the harness directory: `BRAIN_DIR=~/brain_run python3 tests/acceptance.py`, currently 36 of 36.

## Verifying before you commit

1. Re-run the analysis chain and check `git diff results/` is empty, or that the only change is one
   you intended.
2. Rebuild the deck and scan for shapes off the canvas and for dashes.
3. Never leave a generated document stale relative to the result file it reads.

## Design system

Figures and slides share one system, defined in `deck/deck_figures.py` and `deck/build_deck.py`:
IBM Carbon, blue 60 `#0F62FE` for the project's voice and good outcomes, magenta 60 `#D02670`
reserved strictly for harm, teal 60 `#007D79` for the laboratory, purple 60 `#8A3FFC` for the second
agent, Carbon's grey ramp for neutrals, IBM Plex Sans and IBM Plex Mono. Do not introduce a colour
without a semantic reason.

## What is deliberately not claimed

Sycophancy and peer conformity are published phenomena, not findings of this project. Coverage on
this cohort is maximised by a degenerate carbapenem-for-all policy, so never argue the model
underperforms a constant. The speaking-order effect is entailed, not discovered. The confidence
endpoint is withdrawn. See the last section of `deck/EVIDENCE.md`.
