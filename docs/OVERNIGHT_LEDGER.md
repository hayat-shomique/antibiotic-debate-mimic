# Overnight ledger, 20 August 2026

Every change made while you were asleep, in the order it was made, with the reason and the
verification. Nothing in this file is typed from memory; each number cited here was read
back out of the file it now lives in.

Status key: DONE means changed and verified. HELD means deliberately not changed, reason given.

---

## Read this first, if you read nothing else

**One new result, and it is the strongest thing in the project.** Every reconsideration condition
now sits in one table on the same cases from the same opening position, and a null arm sits at the
top of it. Asked to reconsider with nothing to react to, the model moves in no case and leaves one
drug in play. Challenged once with a sentence carrying no evidence, it moves almost always but
harms rarely. Argued with for five turns, it harms in 15.2% of the cases where it had a correct
answer, and the answer space collapses onto two cephalosporins, which between them carry 362 of the 363 determinate runs. Handed the actual susceptibility
panel, it corrects nearly every error and keeps eight drugs in play.

**And the control that the result needed exists now.** The obvious objection to the above is that
five turns is three chances to change its mind, so maybe repetition explains it. One agent, same
cases, same opening prompt, three speaking turns, nothing disagreeing with it: it keeps its answer
and its coverage, and its harmful revision rate is zero. Paired within patient, the debate ends on
an inadequate drug where the control ends on an adequate one, and never the reverse. Being
contradicted is what moves it. Being asked again is not.

**Nine defects were found in what you already had, and none of them changed a result.** That is
worth saying plainly. The scorecard called a finished arm RUNNING. The exposure counter skipped
every record the endpoints are computed on. The document rendered two different totals. Her core
figure was built before her specification reached disk, used a convention no other file used, and
its headline bars were entailed rather than measured. Seven figures were stale. The status file
said four of her endpoints were NOT RUN when they had been run for a day. The answer slide put two
different arms in one row. And the harness that is supposed to catch all of this was itself broken:
it caught one of three planted breaches, and now catches six of six.

**What to say if she asks how you know it is right.** Three of the headline numbers were recomputed
straight from the run files by a script that shares no code with the analysis chain, and all three
agree. The arms are asserted to share one scaffold hash, one cohort hash, one scorer and one
opening position, and every one of those checks is recomputed on every run rather than asserted
once. Everything below is the evidence.

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

## 10. Prof. Zhu's core figure was stale, and it used a different convention from everything else. DONE

Her endpoint specification asks for one core figure: final antibiotic appropriateness stratified by
agent, interaction condition and counterpart correctness, with the two transition rates underneath.
That figure is `figures/f5_core_endpoint.png`. Three things were wrong with the copy in the
repository.

**It was built before her specification existed.** The PNG was written 289 seconds before
`protocol/tingting_endpoint_spec.md` landed on disk, so it recorded that the specification was
missing, carried a DRAFT watermark, and printed "endpoint spec pending" underneath. The watermark
was applied unconditionally rather than only when the specification is absent, so it would never
have cleared itself. Both are now conditional on the file, and the note says which specification
it was built to.

**Its transition rates used a convention no other endpoint in this project uses.** It counted
correct to incorrect as "entered adequate, left not adequate", which folds INTERMEDIATE_ONLY and
UNDETERMINED into the incorrect side. It reported 33 of 175 for Agent A. Every other file in the
project reports 29 of the same runs, because an answer that cannot be scored is not evidence that
the model got it wrong. Her own classification has four cells and none of them is undetermined.

Fixed, and it now reconciles exactly: Agent A 29 of 171, Agent B 23 of 170, which sum to the 52
harmful revisions in the pooled rate of 52 of 341. The panel condition reconciles too: 0 harmful
and 57 of 65 repaired, which is what `results/trigger_comparison.json` computes independently. The
superseded figures are locked out of the repository by the coherence harness.

**Its headline bars are entailed and did not say so.** Under the debate, appropriateness is 312 of
312 when the counterpart is correct and 0 of 88 when it is wrong. That looks like the strongest
result in the study and it is not a result at all: the two agents end on the same outcome class in
every run, so conditioning on the counterpart's correctness conditions on the agent's own. The
figure now says that on its face. What the bars honestly show is how completely the position is
shared, which is still the point of the figure.

## 11. Seven figures in the repository were stale. DONE

The figure sources write into the run directory and the repository carries copies. Seven of the
fourteen files were older than their sources, some by eight hours, and were committed as if
current. All fourteen are now identical to what the sources produce.

## 12. The endpoint status file said NOT RUN about four endpoints that were run. DONE

`analysis/endpoints_status.py` reported time to appropriate therapy, treatment failure, mortality
and length of stay as NOT RUN. All four are computed, with the caveats she asked for, and
`SCORECARD.txt` has been printing them. The status file simply could not see them, because
`secondary_endpoints.json` was written into the run directory and never into the repository.

Both halves fixed. The endpoints are now written to `results/secondary_endpoints.json` as well,
which is safe because they are aggregates over 200 specimens with no case-level rows, and the
status file reads them from there. It now reports **14 of 14 done, none outstanding**.

This is the one to be pleased about: nothing new had to be computed. Four of her endpoints had
been finished for a day and the project was telling itself they were missing.

## 13. My own convention fix created a new contradiction, and the harness caught it. DONE

Unifying the transition convention on the core figure made the escalation row inconsistent with it.
The scorecard filtered only the entering side for determinacy, so runs whose post-panel answer
cannot be scored sat in the denominator and were counted as failures to repair. That gave 57 of 69,
82.6%, against the 57 of 65, 87.7%, that the core figure and `results/trigger_comparison.json`
compute from the same runs.

Both ends determinate everywhere now: repaired 57 of 65 = 87.7%, held 311 of 311 = 100.0%. Three
independent computations agree on it. The superseded figures are locked out of the repository.

Worth saying plainly: the harness found this, not me. It found it in `deck/spec.html`, which is a
published page, at three separate places. That page has been corrected and republished at the same
address, so the repository and the published pages state one set of numbers.

## 14. The single-agent control, running now

The strongest new finding tonight is that duration rather than framing is what costs coverage: one
turn of unsupported challenge costs 1.1% to 3.5% whichever framing is used, and five turns cost
15.2%. There is an obvious objection to it, and it is the one Prof. Zhu would make. Is that the
debate, or is it just being asked three times?

The debate arm cannot answer that, so `selfrevise_run.py` is running the control. One agent, the
same specialist, the same frozen cases, the same round-0 prompt byte for byte, the same formulary,
the same leakage gate and the same scorer. It speaks three times, exactly as many times as the
specialist speaks in the five-turn debate, and between turns it sees only its own text.

It is matched against the runs where the specialist also opens, paired within patient, and tested
with an exact McNemar on the discordant pairs. `analysis/selfrevision_control.py` is written and
runs against whatever has landed.

One thing went wrong and was caught before it produced a number. The first launch selected the
head of the sampling frame; the frozen cohort is a seeded sample of it, and the two overlapped in
41 of 200 cases. A paired comparison on that would have been meaningless and would have looked
fine. The run was stopped, the selection is now asserted against the frozen cohort and the script
refuses to start if any selected case falls outside it, and the wrong-selection file is kept under
a superseded name rather than deleted.

Honest caveat that goes on the slide: the arm is being run against the clock, so it will cover a
contiguous prefix of the cohort rather than all 200. The number of cases is reported, the intervals
are Wilson, and the prefix is contiguous rather than a sample of convenience.

## 15. The control answered, and a label bug in it nearly reversed the answer. DONE

At the point of writing this the control has covered a contiguous 55 of the 200 cases and the
signal is not subtle.

| | five turns, a counterpart arguing | three turns, only its own text |
|---|---|---|
| changed its opening drug | every run | fewer than one run in ten |
| final recommendation adequate | 78.2% | 90.9% |
| harmful revision | 14.6% | 0.0% |

Paired within patient, the debate ends on an inadequate drug where the control ends on an adequate
one in 7 pairs, and the reverse in none. Exact McNemar p = 0.0156 at this coverage.

**The counterpart is what moves it.** Asked three times with nothing disagreeing, the model
restates its own position and keeps its coverage. Asked with something disagreeing, it abandons it
every time. So the finding is about being contradicted, not about being asked again, and "debate"
is the right word for it after all.

This refines rather than replaces the duration result. Both hold, and together they say something
sharper than either alone: a counterpart is what makes the model move at all, and once it is
moving, the longer the conversation runs the more of the coverage it costs. One turn against a
counterpart costs 1.1% to 3.5%. Five turns against a counterpart costs 15.2%. Three turns against
nobody costs nothing.

**The label bug, because it is the kind that ends up on a slide.** The first version of the script
bound the two discordant-pair counts to the opposite output keys, so it printed that the control
had been harmed seven times and the debate none. That is the exact reverse of the finding, it was
internally consistent, and the p value was identical either way. It was caught by reading the
printed sentence against the table above it, which disagreed with it. The counts are now named for
what they are rather than called b and c.

## 16. Three headline numbers recomputed from the raw run files, independently of the pipeline

The pipeline is coherent with itself, which is not the same as being right. So three of the numbers
that reach a slide were recomputed straight from the run files, by a separate short script that
shares no code with the analysis chain.

| claim on the slide | recomputed independently | agrees |
|---|---|---|
| baseline coverage 87.5% | 175 of the 200 opening recommendations cover the organism | yes |
| carbapenem use, 0 to 87.2% under pressure | 0 of 800 at baseline, 698 of 800 under pressure | yes |
| few-shot p = 0.0004, loses 18 and gains 2 | 175 paired determinate cases, 18 lost, 2 gained, exact McNemar 0.0004025 | yes |

Not a proof that the pipeline is right everywhere. It is evidence that the three numbers most
likely to be challenged are what the raw data says, and it took one short script to check, which is
the point of keeping the run files.

## 17. The whole chain is idempotent

Every generator in the analysis chain was re-run and `results/` came back byte identical, the
control arm excepted because it is still growing. Running the chain twice cannot change a number,
which is the property that makes "rebuild it and see" a real answer rather than a hope.

## 18. One error class, found in six places. DONE

The panel arrives in this study in two different ways and they are two different arms. In the
clean-context arm it replaces the debate, measured from the round-0 position over 200 runs. In the
reveal arm it follows the debate, measured from the post-debate position over 400 runs.

Six places paired a harmful revision rate from the first with a coverage change from the second, in
one row, and presented them as one condition. It reads as a single experiment and no such
experiment was run.

- the answer slide, which is the slide the whole talk builds to
- the closing slide's third statistic
- `README.md`, the front page
- `deck/brief.html`, published
- `canvas/Answer.dc.html`
- `deck/EVIDENCE.md`, which exists to map every claim to its source

All six corrected. Where the row is about the panel undoing the debate's damage it is now the
reveal arm throughout, which is also the better claim: after the debate, the panel pushes none of
the 311 runs that reach it on an adequate drug off one. Where the other arm is the point, it says
so and sits on its own row. `deck/brief.html` has been republished.

The coherence harness could not have caught this. It compares values against canonical values, and
every one of these values was canonical. What was wrong was putting two of them in the same row.
That is worth knowing about the harness: it catches a stale number, not a mismatched pair.
