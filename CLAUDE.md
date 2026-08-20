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

---

# Working with this supervisor

Prof. Tingting Zhu set this project's direction. Her operating style is documented across the Teams
thread and it changes how work is presented, not only what is presented. These are extracted rules,
not impressions.

## What she rewards

- **Results before plans.** She postponed a scheduled meeting until results existed and asked, in
  writing, how a concept note could be written before seeing the dataset. Every update to her opens
  with a number, not an intention.
- **A narrow population and a named treatment.** Stated twice inside sixteen hours: you cannot study
  everyone going into ICU. Bloodstream infection with antibiotics is locked. Do not reopen it.
- **Experimental results or theoretical proof.** She wrote both phrases. No speculative slides, no
  "what if" without a reason.
- **"I do not know yet" followed by evidence.** Explicitly acceptable: come back later with a solid
  proof. Bluffing is not.
- **Honesty as a stated lab value.** Robust criticism is the norm and is not hostility. She positions
  herself as an equal in debate and says she is happy to be wrong if you can prove it.

## What she penalises

- **Silence.** Eleven days without contact triggered a chase. This is the single most reliable way to
  damage the relationship.
- **Throwaway credentials.** A reference to prior experience must carry the mechanism: what the
  problem was and why it maps. Otherwise leave it out.
- **AI-written register.** She has said she can tell, and she is not hostile to the tool, she is
  hostile to the voice. Anything written for her must read as the author speaking. Short sentences,
  concrete nouns, no throat-clearing, no triads of adjectives, no "it is worth noting".

## Her terminology is the vocabulary of this project

Use her names, not new coinages: the endpoint hierarchy; susceptibility concordance as the primary
endpoint; spectrum appropriateness; escalation and de-escalation correctness; the four-cell
classification of stable correct, beneficial correction, harmful deference and no improvement;
harmful revision rate over the correct-before group; beneficial correction rate over the
incorrect-before group; decision-quality delta compared across the two speaking directions.

Two required comparisons, both of them, always: the model against the ground truth **and** the model
against the clinician's actual empiric choice.

Mortality is secondary at most, because in bloodstream infection it is confounded by severity,
source control, comorbidity, timing and other treatments. Never lead with it.

## Gaps are named, never left silent

Anything she asked for that is not done goes on a limitations or further-work slide **by name**. An
acknowledged gap is a limitation; an unacknowledged one is a hole. This currently applies to the
withdrawn confidence endpoint, the two arms short of their planned n, the transfer to hosted models,
subsequent resistance, and clinician review.

---

# Handling literature

The corpus is in `docs/`. Three files govern it and they are not optional.

- `docs/LITERATURE.md` is the reading list, tiered, with why each paper matters to this project.
- `docs/LITERATURE_PRESSURE_TEST.md` is the adversarial claim-by-claim check of this project's own
  results against the published record. It records, for each claim, whether the wording survives and
  the closest prior work with a resolved identifier. Read it before making any novelty claim.
- `docs/do_not_cite.md` and `docs/verification_log.csv` record identifiers that could not be
  resolved. Anything listed there is never cited, in any artefact, for any reason.

Rules:

1. **MEASURED or ARGUED.** A paper that ran the experiment and reports the number is MEASURED. A
   paper that asserts a position without measuring it is ARGUED. Label which one you are leaning on.
2. **No citation without a resolved identifier.** A DOI, an arXiv id, or a PMID that a verifier
   resolved. A title alone is not a citation and a search-engine redirect is not an identifier.
3. **Concede what is known before claiming what is new.** Collaboration between agents is already
   known not to reliably help, and sycophancy is documented. Claiming either as a finding costs the
   room's trust in everything else. The contribution is the arbiter: a per-patient laboratory panel
   that neither agent can see, argue with, or produce.
4. **Never cite from memory.** If an identifier is not in `docs/references.bib` or the verification
   log, it does not go in.
