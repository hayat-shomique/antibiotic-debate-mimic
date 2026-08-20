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

Two boundaries on that, both written on the slide rather than left for someone to find. The control
does not hold context length constant, and it does not hold the revision instruction constant: the
debate tells the specialist to consider a stewardship lead's comments and the control tells it to
review its own answer, because naming a stewardship lead would put a counterpart back into a control
built to remove one. So the strict claim is that the instruction and the content together move it
where reviewing your own answer does not. The arm that separates those two is named as the next one
to run, and it is the same arm the pressure test has been asking for since C6.

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

## 14. The single-agent control, why it was built. DONE, results in 15

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

Honest caveat that goes on the slide: the arm was run against the clock, so it covers a contiguous
prefix of the cohort rather than all 200. The number of cases is reported, the intervals are Wilson,
and the prefix is contiguous rather than a sample of convenience. The check that the prefix is not a
strange subset is in section 15.

## 15. The control answered, and a label bug in it nearly reversed the answer. DONE

The control covered a contiguous 125 of the 200 cases before the clock stopped it, and the signal
is not subtle.

| | five turns, a counterpart arguing | three turns, only its own text |
|---|---|---|
| changed its opening drug | 125 of 125 | 4 of 125 |
| final recommendation adequate | 77.6% | 88.8% |
| harmful revision | 14.8% | 0% |

Paired within patient, the debate ends on an inadequate drug where the control ends on an adequate
one in 16 pairs, and the reverse in 0. Exact McNemar p = 3.05e-05.

The prefix is contiguous rather than a sample of convenience, so the fair question is whether it is
like the rest of the cohort. The check is in the file: the debate arm's harmful revision rate
computed on this prefix alone is 14.8%, against 15.2% on the whole cohort.

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
| the primary test, b = 173 to 183, c = 0, p at most 1.7e-52 | discordant pairs 182, 183, 180 and 173 with c zero in all four; the exact binomial on the worst of them recomputed from scratch is 1.67e-52 | yes |
| the model abandons its opening in every debate run | 400 of 400 by direct comparison of the opening drug against the final drug | yes |
| the two agents end on the same drug | 399 of 400, and on the same outcome class 400 of 400 | yes |
| the cohort was frozen by content hash before any model call | the hash recomputed from the parquet by the same method the code uses reproduces the pinned value exactly, on 7,796 rows | yes |
| the four pressure framings, 1.1% to 3.5% | 4/174, 2/174, 6/170 and 3/174 by a second implementation | yes |

The cohort hash is worth a sentence on its own, because it is the claim everything else rests on. It
recomputes to the pinned value on 7,796 rows. The first attempt to check it said it did not match,
which was my own hashing method rather than a defect: the code hashes the pandas object over rows
sorted by subject identifier, not a CSV rendering. Checked properly before reporting anything.

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

## 19. The acceptance suite: 36 of 36, on the second attempt

**It passed, 36 of 36, with no failures.**

The first attempt did not. It was started while the control arm was still running, and the two were
both waiting on the same local model, which serves one request at a time. Between them neither was
getting served: the control had advanced by one case in three minutes. The control was the only new
evidence in the project, so it got the machine and the suite was stopped. It was re-run once the
control finished and passed cleanly.

That is the answer to "did any of tonight's work break the instrument". Nothing tonight touches what
the suite tests: the scaffold hash, the leakage gate, the parser and the scorer are untouched, and
the control arm carries its own scaffold with its own hash rather than modifying the frozen one.
What changed is how results are counted and reported. The suite confirms it.

To re-run it:

```
BRAIN_DIR=~/brain_run python3 tests/acceptance.py
```

Nothing else may be using the model when you do, or it will deadlock against itself. Its output
names the cases it runs, so see section 21 before redirecting it anywhere.

## 20. The four changes the control did make are the sharpest form of the finding

The control changed its drug in 4 of 125 runs. All four are the same move, piperacillin-tazobactam
to ceftriaxone, and all four stay adequate.

That is the same move the debate drives it to. The debate leaves piperacillin-tazobactam for a
cephalosporin in every run, and that move costs coverage in 16 of the paired cases. Same destination
drug, opposite safety profile, and what differs is what triggered it.

This is where the SIMPLIFY trial belongs and it is cited there now. De-escalating a broad-spectrum
beta-lactam to a narrower agent is trial-supported when susceptibility guides it: non-inferior in
Enterobacterales bacteraemia, clinical cure 148 of 164 against 148 of 167 (doi:10.1016/S1473-3099(23)00686-2,
PMID 38215770). What this study measures is the same move made for a reason that is not
susceptibility.

The fix list asked for that framing and proposed supporting it by comparing a five-turn debate rate
against a single-step panel rate, which varies two things at once. It is now earned from this
project's own data, within one design, with the destination drug held fixed by observation rather
than by assertion.

## 21. The acceptance suite prints case identifiers, and now says so

Running it revealed something worth writing down. Its output names each case it runs, so the
transcript contains `case_id` values, which are `subject_id` plus `micro_specimen_id` and are
credentialed under the data use agreement. Nothing has leaked: the log lives outside the repository
and no acceptance output is tracked. But the rule was not written anywhere, and the obvious thing
to do with a test run is to redirect it into a file next to the code.

`CLAUDE.md` now says it beside the command: never redirect that output into the repository, never
paste it into a document or a commit message, never quote a line of it. Report the pass count, not
the transcript.

## 22. The control arm was itself an unregistered arm, which is the defect from section 3 again

Building the control created a run file that no counter knew about. That is exactly the failure
`assert_no_orphan_files` exists to prevent, and it did not fire, because the guard only watches
file-name prefixes it has been told about and `selfrevise_` was not one of them.

Registered now, with its prefix added to the guard. The project holds 14 arms and 4,034 deduplicated
exposures, and the control is marked PARTIAL by design in both the registry and the scorecard, so
the one arm short of its planned size says so on its own row rather than being averaged away.

Registering it also surfaced two stale entries in the scorecard: the debate arm's design size was
still the turn-level 401 from before section 3's fix, and the footnote still called its count
turn-level rows. Both now say what they are, and the arm size and the endpoint denominator are one
number.

## 23. One of her two required comparisons claimed something it had not computed. DONE

The clinician comparison reported the model at 91.1% on 192 cases and the clinician at 90.6% on
138, and then said "on the cases where both can be scored the two are indistinguishable". Those are
two different sets of cases. The set where both can be scored was never constructed, so the sentence
described an analysis that does not exist, and the deck's own column header said the same thing.

The two rates are real and the comparison is fair on its own terms: the identical rule scores both
sides and each is restricted to what it can be scored on. What is not true is that they are paired.

Corrected in five places: the result file, the project document, the deck's table header, the deck's
speaker notes and the supervisor asks table. Each now says the rates sit on different sets of cases
and that this is two independent proportions rather than a paired test.

The paired version needs per-case outcomes on the clinician side. The comparator artefact carries
aggregates only, because it derives from credentialed prescribing records, so building it is real
work rather than a rerun. It is named as further work rather than implied.

This is the one to be least comfortable about. It is not a stale number and no sweep would have
caught it: every figure was right and the sentence next to them was not.

## 24. A record's own flag disagreed with the data, so the measure was changed to the data

The debate records carry a `changed_A` flag. It reads None on 8 of the 400 runs where the drug did
in fact change, because it is written per turn and the first turn has no previous position to
compare against. Reading movement off that flag would have said 392 of 400 where the direct
comparison says 400 of 400.

The control's analysis used that flag on both arms. It happened to agree on the 125-case subset,
which is why nothing looked wrong. It now compares the opening drug against the final drug directly
in every place, because that cannot be ambiguous.

Three absolute claims were checked against the raw data at the same time and all three hold exactly:
the model abandons its opening drug in 400 of 400 debate runs, the two agents end on the same drug
in 399 of 400, and on the same outcome class in 400 of 400.

## 25. Two implementations of the same endpoint now have to agree

`analysis/trigger_comparison.py` recomputes the four pressure framings and the clean-context panel
from the run files by different code from `analysis/tingting_endpoints.py`. They agree exactly, on
numerator and denominator, on all five. That was checked by hand and is now an assertion: a
disagreement raises rather than writing a second number into a second file.

Verified by fault injection. Perturbing one comparison by a single count makes the script refuse to
produce output and name every quantity involved, and the repository restores clean.

The same guard is now in `analysis/supervisor_scorecard.py`, which computes the harmful and
beneficial revision rates on the debate arm that `tingting_endpoints.py` also computes. Both figures
are published and both go on slides. They agree exactly, and the scorecard now refuses to print if
they ever stop agreeing. Fault-injected the same way, and restored clean.

This is the cheapest form of independent verification available in this project. Where two scripts
already compute the same thing, making them check each other costs a few lines and removes a whole
class of silent divergence. Three endpoint pairs are now guarded this way.

## 26. A negative confidence bound in a result file, deliberately not fixed. HELD

`results/primary_test.json` carries a Wilson lower bound of about minus 1.7e-18 on the neutral
control's flip rate, which is floating point arriving a hair below zero when the numerator is zero.
The same artefact appeared in the control arm's own interval and was clamped there.

It is not clamped here, on purpose. This interval comes from `wilson_ci` in the scorer, which is
hash-pinned and whose fingerprint the acceptance suite checks. Editing it to make a number that
nothing renders look tidier would break the pin that proves the scoring rule has not moved since
the protocol was frozen. That is a bad trade.

Checked before deciding: nothing renders it. Every document and slide uses the numerator and
denominator of the flip rates, never the interval, so no negative percentage reaches a reader. If a
future document does render it, clamp at the point of rendering rather than in the scorer.

Recorded here so the next person finds the reasoning rather than the artefact.

## 27. The cohort chain, verified end to end from the source files

Every step from the raw index events to the frozen 200 was recomputed from the parquet files, not
read out of a document.

| step | claimed | recomputed |
|---|---|---|
| index events, panel-bearing first positive blood cultures | 9,236 | 9,236 rows, 9,236 distinct specimens |
| gated to the frozen cohort | 7,796 | 7,796 |
| content hash pinned before any model call | `4a4f4f78...3c65d414` | reproduces exactly, by the method the code uses |
| susceptibility panel rows behind the reference standard | 138,513 | 138,513 |
| the evaluated selection | a seeded 200 | the seeded selection reproduces the frozen 200 and overlaps the debate arm 200 of 200 |

That last row is the one that matters most, because it is the check that caught the control arm
running on the wrong cases before it produced a number. It is now asserted inside
`selfrevise_run.py` rather than checked by hand.

## 28. What this night actually taught, separate from what it fixed

Two kinds of thing were learnt and they are worth keeping apart.

### About the system under test

The picture is now complete in a way it was not, because the null arm and the control arm sit at
either end of it.

Asked to reconsider with nothing to react to, the model does not move at all: no case changes, no
error is corrected, one drug in play across the whole cohort. So nothing that follows is drift or
instability. Something has to be said to it.

Say almost anything and it moves. A single challenge carrying no clinical content moves it in the
overwhelming majority of cases, and it corrects an inadequate opening almost as often as the real
susceptibility panel does. That is the uncomfortable part: **it revises at close to the right rate
for none of the right reasons.**

Say it for five turns and the cost appears. Harmful revision runs an order of magnitude above the
one-turn rate and the answer space collapses onto two cephalosporins.

And the counterpart is what does it, not the repetition. Asked three times by itself, the model
keeps its answer and its coverage. The few times it does move unprompted it makes the same
de-escalation the debate makes, and every one of those stays adequate. **Same destination drug,
opposite safety profile, and the variable is what triggered the move.**

### About the project's own integrity, which is the more transferable lesson

**Coherence with yourself is not correctness.** The repository passed its own harness while
containing an exposure counter that skipped every record the endpoints use, a core figure using a
convention no other file used, and four of the supervisor's endpoints reported as not run when they
had been run for a day.

**The dangerous errors were pairs of correct numbers.** Six files put a rate from one arm beside a
coverage change from another, in one row. Every value was canonical. No stale-value sweep can catch
that, which is why the harness now has a sweep that checks pairs.

**A guard that has never fired may simply be broken.** The banned-claim sweep had reported clean for
days. Fault injection showed it caught one planted breach in three: a banned phrase containing a
negation word negated its own ban, and any negation within two hundred characters silenced
everything after it. It catches six of six now.

**Prose can claim what the analysis never computed.** The clinician comparison said the model and
the clinician were indistinguishable on the cases where both can be scored. That set was never
constructed. Both numbers were right and the sentence between them was not.

**A record's own flag can disagree with the data it describes.** The debate records' change flag
reads None on eight runs where the drug did change. Measure from the data, not from the label
someone wrote about the data.

## 29. The idempotence check is only meaningful when no arm is running

Running the green-tick sweep while the control arm was still writing reported the analysis chain as
not idempotent and the working tree as dirty. Both were the arm growing between the two halves of
the check, from 125 cases to 173, not a defect.

Worth stating because it is the obvious way to mislead yourself with this check: re-running the
chain proves nothing about determinism if the inputs are changing underneath it. Run it with the
arms stopped, or the answer is meaningless in the direction that looks like failure, and worse,
could look like success if two changes happened to cancel.

## 30. The control arm ran to completion, and full n changed one of my sentences

It finished at 200 of 200. The result is stronger and one claim I had written is now wrong.

| | five turns, a counterpart arguing | three turns, only its own text |
|---|---|---|
| changed its opening drug | 200 of 200 | 6 of 200 |
| final recommendation adequate | 77.0% | 87.0% |
| harmful revision | 17.0% | 0.6% |

Paired within patient, the debate ends on an inadequate drug where the control ends on an adequate
one in 28 pairs and the reverse in 0. Exact McNemar p = 7.45e-09, four orders of magnitude
stronger than at the partial arm.

**The sentence that was wrong.** At 125 cases the control changed its drug 4 times and all 4 stayed
adequate, and I wrote that. At 200 it changes 6 times, 5 keep their coverage and 1 does not. So the
control's harmful revision rate is 0.6%, not zero.

That is a better claim, not a worse one, and it is worth saying why. "The model never errs on its
own" was always too strong and would have been the first thing attacked. What the control actually
establishes is a rate: the same de-escalation, from the same drug to the same drug, on the same
patients, costs 0.6% when the model makes it alone and 17.0% when a counterpart drives it.

Corrected in the project document, the journey document, the control slide and the contribution
slide's notes. It is also the clearest argument for running an arm to its planned size rather than
stopping at a decisive-looking prefix: the prefix was decisive and one of its sentences was wrong.
