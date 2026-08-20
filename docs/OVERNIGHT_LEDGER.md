# Overnight ledger, 20 August 2026

Every change made while you were asleep, in the order it was made, with the reason and the
verification. Nothing in this file is typed from memory; each number cited here was read
back out of the file it now lives in.

Status key: DONE means changed and verified. HELD means deliberately not changed, reason given.

---

## 1. The scorecard reported a finished arm as still running. DONE

`SCORECARD.txt` carried a block that recounted the run files itself, with date-scoped globs and
raw line counts. It printed the pressure arm as `300/788 RUNNING` and the plausible-wrong arm as
`478/312`, while the canonical counter had both complete at 800 and 312. Two counters, two answers.

Fixed by deleting the recount. The block now reads `results/RESULTS.json` `_integrity`, which is
written by the one counter, `analysis/canonical_numbers.py`. Every arm now prints its deduplicated
size against a registered design size, with the reason recorded where the size is bounded by how
many eligible cases exist rather than by the plan.

Verified: all thirteen arms print COMPLETE, and the block states that the debate endpoints are
computed on the 400 completed ordering-runs.

## 2. The documented rebuild command refreshed a file nothing reads. DONE

`analysis/canonical_numbers.py` defaulted its output directory to its own folder, so
`python3 analysis/canonical_numbers.py`, exactly as documented in `CLAUDE.md`, `README.md`,
`PROJECT.md` and `deck/EVIDENCE.md`, wrote `analysis/RESULTS.json`. Every document, figure and
slide reads `results/RESULTS.json`. Anyone re-running the chain would have refreshed a copy nothing
reads while the copy everything reads went stale in silence.

Fixed: the default is now `<repo>/results`, matching every other generator.

Checked before fixing: the two copies were byte-identical, so nothing published was stale. The
defect was latent, not active.

## 3. The debate arm counted the wrong records, and one duplicate escaped. DONE

The debate arm's identity key was `case_id + drug + ordering + turn`. The completed-run records,
the ones every endpoint in the project is computed on, carry neither `drug` nor `turn`, so the
counter skipped all 400 of them and counted round-0 records instead. It reported 401.

The 401st was a round-0 elicitation written twice for the same case and speaking order. Both rows
carry the same drug, the same reason text and the same token counts; they differ only in wall-clock
seconds. It survived deduplication because `turn` is a nested record that contains that timing.

Fixed: the arm is now keyed on `case_id + ordering` over completed runs, so its registered size is
400, which is the denominator every debate endpoint already uses.

Verified separately, before the fix: the analysis set is clean. 400 completed runs, 400 distinct
case and speaking-order pairs, 200 cases, 200 runs per order. No endpoint moves.

## 4. Two different exposure totals in one document. DONE

`PROJECT.md` said `4110 exposures` in section 8 and `3,910 deduplicated exposures` in the timeline.
Two causes, both fixed:

- the renderer summed the integrity block and then added the few-shot arm again, although the
  few-shot arm is already one of the thirteen arms in that block. That is a 200-exposure double
  count. An assertion now holds the arm's registration in place.
- `docs/SUPERVISOR_ASKS.md` had `3,910` typed into prose, which the repository's own rule forbids.
  It now carries tokens that the renderer fills from the result files, and an unfillable token is a
  hard error rather than a stray brace.

Verified: `PROJECT.md` now says `3,909` in both places, and both come from the same sum.

## 5. The integrity block claimed six models where there are two. DONE

The cross-model arm's registered note read "same cases across six models". The run files hold two
checkpoints, Qwen3-4B-instruct and MedGemma-4B, 200 cases each. The repository's own limitation on
this arm, at `docs/LITERATURE_PRESSURE_TEST.md` under C11, already says checkpoint space is N=2.
The note contradicted a limitation the project had already accepted.

Fixed: the note now names both checkpoints, states N=2, and points at C11.

## 6. All four references verified against PubMed, and two better ones found. DONE

Every identifier in the fix list was resolved and every figure was read from the retrieved
abstract rather than taken on trust. All four hold exactly.

| reference | PMID | verified |
|---|---|---|
| SIMPLIFY, Lopez-Cortes et al., Lancet Infect Dis 2024;24(4):375-385 | 38215770 | 21 Spanish hospitals, 164 against 167 in the modified intention-to-treat population, cure 148 (90%) against 148 (89%), risk difference 1.6 points, 95% CI minus 5.0 to 8.2, margin minus 10%. Ceftriaxone is among the de-escalation options |
| Rhee et al., JAMA Netw Open 2020;3(4):e202899 | 32297949 | 17,430 adults, 104 hospitals, inadequate OR 1.19 (1.03 to 1.37), unnecessarily broad OR 1.22 (1.06 to 1.40), ESBL prevalence 0.8% |
| Tamma et al., Clin Infect Dis 2019;69(8):1446-1455 | 30838380 | the induction grading, best described for *Enterobacter cloacae*, less clear for other Enterobacteriaceae |
| Saleh et al., Int J Infect Dis 2026;167:108563 | 41864271 | 17 studies, mortality OR 1.29 (0.91 to 1.82), adverse reactions OR 4.32 (1.73 to 10.79), supports cefepime at MIC 2 or below |

Two additions the fix list did not have, both closer to this cohort than anything in it, because
both are bloodstream-infection specific rather than all-sites:

- **Onorato et al., Infection 2024;53(3):1141-1153**, PMID 39630396. 20 studies, 2,834 patients.
  For AmpC producers, piperacillin-tazobactam carries higher microbiological failure, RR 1.80
  (1.15 to 2.82), and higher clinical failure, RR 1.54 (1.00 to 2.40), than cefepime or a
  carbapenem. This matters because this study's baseline drug is piperacillin-tazobactam and one
  of its two destinations is cefepime. It cuts both ways and the reading is written out in
  `docs/LITERATURE.md`.
- **Cheo et al., Open Forum Infect Dis 2025;12(7):ofaf413**, PMID 40718546. Cefepime against
  carbapenems in AmpC bloodstream infection, no mortality difference. Held in reserve.

All six are in `docs/references.bib` with PMIDs recorded, and in `docs/LITERATURE.md` with the
caveat that must be written beside each.

## 7. The AmpC limitation, rewritten and computed rather than asserted. DONE

The fix list asked for the limitation to be softened to name *Enterobacter cloacae* separately.
Doing that properly needed a number, so `analysis/ampc_exposure.py` now computes it.

Two things came out of it that change what the limitation says.

**The organism grading had to be an explicit table, not a genus match.** Matching on genus
undercounted by two, because the laboratory writes three further Enterobacter labels, and it
over-counted once, because one label carries "(ENTEROBACTER)" only as a historical synonym for
what is actually *Pantoea agglomerans*. The script now grades all twenty organism labels in this
cohort explicitly and raises on any label it has not been told about. With that done, the figure
is 36 of 200, 18.0%, which independently reproduces the count in `docs/RED_TEAM.md`.

**The limitation bounds the adequacy labels, not the harm finding.** Of the 52 harmful
revisions, exactly 1 is onto a third-generation cephalosporin against an AmpC-capable organism.
23 are onto cefepime, which guidance recommends for AmpC producers. What the limitation does
bound is 27 of the 400 ordering-runs, which end on a third-generation cephalosporin against an
AmpC-capable organism and are scored adequate. That is also the figure `RED_TEAM.md` reached by a
different route.

The limitation in `docs/LIMITATIONS.md` now says that, carries no typed numbers, and keeps the
direction-of-bias sentence, which is the part that helps.

## 8. The fix list's headline framing was checked and it needed rebuilding. DONE, with a correction

The fix list proposed saying: harmful revision 15.2% under a content-free argument, 1.1% when the
panel triggers it, same destination drug, opposite safety profile, the trigger is the variable.

The 1.1% is real and the arm it comes from is the right one. The problem is the comparison. The
15.2% is a five-turn debate and the 1.1% is a single reconsideration step, so as worded it varies
two things at once and calls one of them the variable. A supervisor who asked "how many turns" on
each side of that sentence would have found it.

Worse, the obvious repair is a trap. The panel-reveal arm looks like the matched comparator and is
not: its records carry the debate's own final drug on all 400 runs, so the panel is revealed after
the debate has already moved the position. Computing a round-zero to reveal transition would have
credited the panel with undoing damage the debate caused. `analysis/trigger_comparison.py` now
re-derives that proof on every run and refuses to produce a number if it stops holding.

The genuinely matched arm is the clean-context panel: same 200 cases, same round-0 opening, one
reconsideration step, no debate history. Built on that footing, `PROJECT.md` section 7.12 now puts
all five one-step triggers and the debate in one table, and two claims fall out that are stronger
than the one proposed:

- a challenge carrying no evidence corrects an inadequate opening almost as often as the
  susceptibility panel does, 66.7% to 81.8% against 91.7%. The model revises at close to the right
  rate for none of the right reasons.
- the framing of the challenge is not what costs coverage, duration is. One turn costs 1.1% to
  3.5% whichever framing is used. Five turns cost 15.2%. The answer space narrows with it: the
  panel leaves 8 drugs in play, the debate leaves 3.

## 9. Two sections both numbered 7.9. DONE

`PROJECT.md` had two section 7.9 headings. Renumbered, and the new trigger table is 7.12.
