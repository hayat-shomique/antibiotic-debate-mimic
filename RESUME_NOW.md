# Resume point, 20 August 2026, 02:20

Written mid-run so a restarted session can finish the job. Three arms were launched to close the
three gaps named on the limitations slide. **All three run detached with nohup, so they survive a
Claude Code restart and a terminal close.** Do not relaunch anything without checking the locks
first: two processes writing one output file is the defect that cost 85 duplicated exposures on
19 August.

## Paste this into the fresh session

> Resuming the UNIQ+ antibiotic-debate project mid-run. Read `RESUME_NOW.md` first, then
> `CLAUDE.md`, then `PROJECT.md`. Three background jobs were closing three gaps. Check which have
> finished, then run the integration steps in `RESUME_NOW.md` in order. Do not relaunch a job whose
> lock is still held. Everything committed up to `9682d0f` is verified and pushed; the tag
> `verified-2026-08-20-0140` is the last fully verified state if anything needs rolling back.

## What is running

| job | what it does | how to check it is done |
|---|---|---|
| `c1_pressure.py -n 200` | extends the unsupported-pressure arm from 78 cases to the full 200. At 02:20 it was at 74 of 122 remaining, about 23 s per case | `kill -0 $(cat ~/brain_run/.locks/c1.pid)` fails, or `tail ~/../scratchpad/c1_resume.log` shows the summary |
| `plausible_pass.py -n 200` | **chained**, starts automatically when the pressure arm releases its lock | `.locks/plausible.pid` gone |
| `_t4c_step_b_mlm.py Charangan/MedBERT` then rescore | the within-span variant for MedBERT, so the scorer will include it | `medbert_ws.log` contains `medbert done` |

Logs are in the session scratchpad. If that is gone, the run directory itself is the source of
truth: `ls -la ~/brain_run/runs/` and compare counts against `results/RESULTS.json` `_integrity`.

## When each finishes, do this

### 1. Pressure arm finished

```
cd ~/Desktop/antibiotic-debate-mimic
BRAIN=$HOME/.claude-science/conda/envs/brain/bin/python
$BRAIN analysis/primary_test.py            # attrition and coverage_check will change
$BRAIN analysis/tingting_endpoints.py
$BRAIN analysis/policy_degeneracy.py
python3 analysis/confidence_axis.py        # the harmful-deference cell should grow past 4
BRAIN_OUT="$PWD/results" python3 analysis/canonical_numbers.py
```

**What to expect and what to check.** The primary set should rise well above 70 because
`dropped_arm_never_ran_the_case` collapses toward zero. `c_control_only` must stay at 0 in every
framing; if it does not, the headline changes and the deck sentence "a neutral turn never moves it"
must change with it. Read `results/primary_test.json` `attrition` and `coverage_check` before
touching any document.

### 2. Plausible arm finished

Only `analysis/canonical_numbers.py` consumes it. Re-run that and check `_integrity.plausible.n`.

### 3. MedBERT finished

```
python3 analysis/model_tiers.py
```
`results/model_tiers.json` `_encoder_baseline.models` should then hold five encoders including
`Charangan/MedBERT`. The deck's models slide iterates that dict, so it picks the fifth up
automatically.

### 4. Rebuild every artefact, in this order

```
python3 analysis/clinician_comparison.py
python3 analysis/render_project.py
python3 analysis/build_audit.py
python3 deck/deck_figures.py               # needs the scratch venv with matplotlib
python3 deck/build_deck.py
python3 deck/build_evidence.py
```

Then verify before committing: `git diff results/` reviewed line by line, no shape off the canvas,
no em or en dashes, and the acceptance suite still green with
`BRAIN_DIR=~/brain_run $BRAIN tests/acceptance.py`.

## What changes in the documents once the pressure arm completes

These sentences are written against the 78-case arm and **must be re-read after the rebuild**,
because they will be wrong if the numbers move:

- The attrition split in `PROJECT.md` 7.2 and on slide 9. `dropped_arm_never_ran_the_case` was 122.
- "the pressure arm ran 78 of 200" on the limitations slide and in `BRIEFING.md` section 8.
- The confidence cell sizes in `PROJECT.md` 7.9 and on the confidence backup slide.
- `deck/EVIDENCE.md` regenerates itself, so it needs no editing, only checking.

All of them are generated from result files, so the rebuild does the work. The job is to read the
new numbers and confirm the prose around them still describes what they show.

## Safety

- Last fully verified state: tag `verified-2026-08-20-0140`, and `results/` was copied to the
  session scratchpad before any of this started.
- Nothing in `~/brain_run` was deleted. The scorer's model list in `_t4c_step_c_score.py` gained one
  entry, `Charangan/MedBERT`, with the reason in a comment beside it.
- `torch` was installed into the brain conda environment because the encoder pipeline needs it and
  it was missing. That is additive.

## The three claims this is closing

1. Two arms short of their planned n. Both are now running to completion.
2. Med-BERT not run. `Rasmy/Med-BERT` **does not exist on the HuggingFace Hub**, verified 20 August,
   and the original is pretrained on structured diagnosis codes so a cloze over drug names has
   nothing to predict into. `Charangan/MedBERT` is running as the closest clinically pretrained
   encoder carrying that name, declared before its result was seen.
3. The confidence axis withdrawn. **Now reported**, on the continuous measure rather than the
   degenerate binary. On the 78-case arm the direction was the one she predicted: where the model
   held a correct answer it became less certain, and where it abandoned one for a wrong answer it
   became more certain, difference in mean change +8.2 points, permutation p = 2e-05. The cell was
   4 exposures, which is why the arm is being completed.
