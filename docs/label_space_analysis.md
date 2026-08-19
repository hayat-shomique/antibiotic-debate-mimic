# Label space cardinality: evidence for the 17-to-10 decision

Written 18 August 2026. Companion data file `label_space_analysis.csv`. Nothing in the live
pipeline was changed to produce this; every number below comes from read-only queries against
the frozen inputs and from scripts named at each step.

## What was run

The primary sampling frame reproduces exactly. `_ls_step1_rank.py` calls
`DR.build_frame()` (7,796 frozen cohort rows, hash
`4a4f4f782eb17345e0e9eab1cc596aab9ebf6442890bd1c3b82761ae3c65d414`) and then
`DR.select(frame, 10**9, sample=False, panel=panel)`, which returns 993 rows whose
`micro_specimen_id` set and `index_time` values are identical to `_cc_frame993.parquet`. The
200-case draw from `DR.select(frame, 200, sample=True, panel=panel)` has the same specimen set
as `_cc_sel200.parquet`. [FACT]

Prescription orders come from `_cc2_rx993_post24.parquet`, produced by `_cc2_extract993.py`
directly against `/Users/shamzzzh/Downloads/mimic-iv-3.1/hosp/prescriptions.csv.gz` on the
D-CLINWIN-1 window `[index_time, index_time + 24h]`. `_ls_step1_rank.py` re-checks the bounds
on that file and finds `h_from_index` running from 0.0 to 24.0 inclusive across 20,109 order
rows on 984 of the 993 cases, with 674 distinct free-text drug strings. A second, independently
extracted file, `_t3_rx200.parquet` from `_t3_extract.py`, restricted to the same window and the
same 200 specimens, returns 3,913 rows, exactly matching the 3,913 rows the 993-frame file holds
for those specimens, with identical per-agent case counts. The two extracts are the same data
pulled twice. [FACT]

## 1. Empiric prescribing frequency over the 993-case frame

Two mappers were applied to the free-text `drug` column, both defined in `_cc2_mappers.py`. The
strict mapper is `BS.canon_drug`, exact alias match against the 17-agent formulary in
`inputs/brain_scoring_local.py`, and it is the project's primary instrument for scoring. The
relaxed mapper adds stem matching onto the same 17 canonical names. Counts are distinct cases
with at least one order in the window, denominator 993.

| rank (relaxed) | rank (strict) | agent | cases, relaxed | % of 993 | cases, strict | % of 993 |
|---:|---:|---|---:|---:|---:|---:|
| 1 | 1 | vancomycin | 407 | 40.99 | 404 | 40.68 |
| 2 | 2 | cefepime | 367 | 36.96 | 367 | 36.96 |
| 3 | 3 | piperacillin-tazobactam | 289 | 29.10 | 263 | 26.49 |
| 4 | 4 | ceftriaxone | 138 | 13.90 | 138 | 13.90 |
| 5 | 13 | ciprofloxacin | 135 | 13.60 | 1 | 0.10 |
| 6 | 5 | meropenem | 86 | 8.66 | 86 | 8.66 |
| 7 | 6 | ceftazidime | 37 | 3.73 | 36 | 3.63 |
| 8 | 7 | ampicillin-sulbactam | 27 | 2.72 | 27 | 2.72 |
| 9 | 8 | levofloxacin | 24 | 2.42 | 24 | 2.42 |
| 10 | 11 | gentamicin | 21 | 2.11 | 7 | 0.70 |
| 11 | 9 | linezolid | 14 | 1.41 | 14 | 1.41 |
| 12 | 10 | daptomycin | 7 | 0.70 | 7 | 0.70 |
| 13 | 14 | ampicillin | 6 | 0.60 | 0 | 0.00 |
| 14 | 17 | trimethoprim-sulfamethoxazole | 5 | 0.50 | 0 | 0.00 |
| 15 | 12 | cefazolin | 4 | 0.40 | 4 | 0.40 |
| 16 | 15 | oxacillin | 0 | 0.00 | 0 | 0.00 |
| 17 | 16 | penicillin-g | 0 | 0.00 | 0 | 0.00 |

The gap between the two columns is not a modelling choice, it is an alias-coverage defect that
would corrupt any ranking built on the strict mapper. `_ls_step1_rank.py` prints the 253 order
rows that the strict mapper misses and the relaxed mapper catches: 131 rows of
`Ciprofloxacin IV`, 42 of `Piperacillin-Tazobactam Na`, 39 of `Ciprofloxacin HCl`, 16 of
`Gentamicin Sulfate`, 6 of `Ampicillin Sodium`, 7 of `Sulfameth/Trimethoprim` variants. The
formulary alias set holds only the bare token `CIPROFLOXACIN`, which appears in MIMIC as a
prescription string exactly once in this frame. [FACT] Ranking ciprofloxacin 13th of 17 would
be an artefact of the alias table, so the relaxed column is the correct instrument for a
frequency ranking even though the strict mapper stays primary for scoring. [INFERENCE]

Cases with at least one order of any kind in the window: 984 of 993. With at least one systemic
antibacterial: 889. With at least one order mapping into the formulary: 877 relaxed, 832 strict.
[FACT]

The tail of this ranking is unstable. Recomputed on the 200 sampled cases alone, the top ten
swaps gentamicin out for cefazolin; the top six are the same six agents in both. [FACT] Any cut
placed at rank 9, 10 or 11 is therefore sitting inside sampling noise, and should not be
defended as if the ordering there were solid. [INFERENCE]

## 2. Candidate cardinalities on the 200 sampled cases

Sets are the top N of the relaxed ranking above, ties broken alphabetically. Clinician order
share is over the 449 formulary-mapped order rows on these 200 cases. Panel share is over 2,472
pathogenic panel rows, of which 2,180 map into the 17-agent formulary. The UNDETERMINED columns
come from `_ls_step2_cardinality.py`, which scores every one of the 17 agents against every one
of the 200 panels with `DR.BS.score_case([d], DR.pathogenic_panel(panel, sid))`, a 200 by 17
grid saved to `_ls_outcome_grid200.parquet`.

| N | label set | clinician order rows in set | cases whose whole regimen is in set | panel rows in set | panel rows in set, of formulary rows | UNDETERMINED, mean over set | UNDETERMINED, floor | best-agent ADEQUATE |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5 | vanco, cefepime, pip-tazo, ceftriaxone, cipro | 86.19% | 75.71% | 34.22% | 38.81% | 21.60% | 0.0% | 96.5% |
| 8 | + meropenem, ceftazidime, amp-sulbactam | 95.55% | 90.96% | 58.09% | 65.87% | 16.94% | 0.0% | 99.0% |
| 10 | + levofloxacin, gentamicin | 97.55% | 95.48% | 66.87% | 75.83% | 23.55% | 0.0% | 99.5% |
| 12 | + linezolid, daptomycin | 98.89% | 97.74% | 66.87% | 75.83% | 36.29% | 0.0% | 99.5% |
| 17 | full formulary | 100.00% | 100.00% | 88.19% | 100.00% | 40.88% | 0.0% | 99.5% |

"UNDETERMINED, mean over set" is the rate a model would incur if it drew uniformly from the set;
"floor" is the share of cases on which every agent in the set returns UNDETERMINED, which is
zero everywhere. The equivalent table built on the strict ranking is in the CSV under section
`2_cardinality_sweep_200`; it behaves worse, reaching 43.20% mean UNDETERMINED at N=10 because
the strict ranking pushes ciprofloxacin and gentamicin out and pulls daptomycin and linezolid in.

The UNDETERMINED column does not fall as the set shrinks, which is the finding that matters
here. It is driven by which agents are in the set, not how many. [FACT]

## The per-agent scoreability cliff

| agent | cases with a panel verdict, of 200 | UNDETERMINED % | ADEQUATE % | INADEQUATE % |
|---|---:|---:|---:|---:|
| trimethoprim-sulfamethoxazole | 200 | 0.0 | 74.0 | 26.0 |
| ceftriaxone | 199 | 0.5 | 76.0 | 22.5 |
| ciprofloxacin | 198 | 1.0 | 65.0 | 31.5 |
| cefepime | 195 | 2.5 | 79.5 | 15.5 |
| ceftazidime | 195 | 2.5 | 79.5 | 13.0 |
| gentamicin | 195 | 2.5 | 85.5 | 11.0 |
| meropenem | 194 | 3.0 | 96.0 | 1.0 |
| piperacillin-tazobactam | 193 | 4.0 | 87.5 | 6.0 |
| ampicillin-sulbactam | 158 | 22.0 | 40.5 | 27.5 |
| cefazolin | 157 | 22.5 | 50.5 | 27.0 |
| ampicillin | 131 | 37.0 | 25.5 | 36.5 |
| levofloxacin | 5 | 97.5 | 2.0 | 0.0 |
| daptomycin | 0 | 100.0 | 0.0 | 0.0 |
| linezolid | 0 | 100.0 | 0.0 | 0.0 |
| oxacillin | 0 | 100.0 | 0.0 | 0.0 |
| penicillin-g | 0 | 100.0 | 0.0 | 0.0 |
| vancomycin | 0 | 100.0 | 0.0 | 0.0 |

Five agents have zero panel rows anywhere in the 200 cases, and a sixth, levofloxacin, has seven
rows across five cases, so six of the seventeen labels are effectively unscoreable in this
population.
`_ls_step2_cardinality.py` produced this table. [FACT] The cause is D-POP-1: the frame is
Enterobacterales bacteraemia, and laboratories do not run Gram-positive agents against
Enterobacterales isolates. [INFERENCE]

This is why the frequency ranking and the scoreability ranking disagree at the very top.
Vancomycin is the most frequently ordered agent in the frame at 407 of 993 cases and is
simultaneously the least scoreable agent in the label set at 0 of 200 cases. It appears in the
prescribing record as Gram-positive cover added while the organism is still unknown, not as a
proposed treatment for the Enterobacterales isolate the panel later reports. [INFERENCE]

## An alternative basis: rank by scoreability, not frequency

Taking the eleven agents that both appear in the frame's prescribing record and are tested on at
least half the 200 panels gives ampicillin, ampicillin-sulbactam, cefazolin, ceftriaxone,
cefepime, ceftazidime, meropenem, piperacillin-tazobactam, ciprofloxacin, gentamicin and
trimethoprim-sulfamethoxazole. Dropping ampicillin, the weakest on both counts at 6 ordering
cases and 37.0% UNDETERMINED, leaves ten. `_ls_step4_proposed.py` scores these:

| set | N | clinician order rows in set | cases whose whole regimen is in set | panel rows in set, of formulary rows | UNDETERMINED, mean over set | UNDETERMINED, worst agent | best-agent ADEQUATE |
|---|---:|---:|---:|---:|---:|---:|---:|
| scoreable 8 | 8 | 67.04% | 44.63% | 77.61% | 2.00% | 5.0% | 99.5% |
| scoreable 10 | 10 | 69.71% | 48.02% | 93.26% | 6.05% | 22.5% | 99.5% |
| scoreable 11 | 11 | 69.71% | 48.02% | 99.68% | 8.86% | 40.0% | 99.5% |
| frequency top 10 | 10 | 97.55% | 95.48% | 75.83% | 23.55% | 100.0% | 99.5% |
| formulary 17 | 17 | 100.00% | 100.00% | 100.00% | 40.88% | 100.0% | 99.5% |

At the same cardinality of ten, the scoreability-ranked set covers 93.26% of formulary-mapped
panel rows against 75.83% for the frequency-ranked set, and carries a mean UNDETERMINED rate of
6.05% against 23.55%. It pays for that with clinician order coverage, 69.71% against 97.55%,
and with the share of cases whose entire recorded regimen sits inside the set, 48.02% against
95.48%. Almost all of that loss is vancomycin. [FACT]

One further result from `_ls_step4_proposed.py` bears on the comparator rather than the model.
Restricting the clinician's extracted regimen to the scoreable ten and rescoring the 200 cases
moves ADEQUATE 138 to 138, INADEQUATE 13 to 22, INTERMEDIATE_ONLY 2 to 4, and UNDETERMINED 47 to
36. Eleven cases change outcome, every one of them out of UNDETERMINED and into a real verdict,
and no case moves in the other direction. [FACT] Under `require_all_pathogens_covered=True` an
agent with no verdict on an isolate forces the `indeterminate` state and sends the whole case to
UNDETERMINED unless some other agent in the regimen already covers it, so the never-tested
agents are not neutral padding in the regimen, they are actively destroying comparator
information. [INFERENCE]

## 3. What changes if the label set becomes the top 10 rather than 17

Under the frequency ranking the seven agents that drop are ampicillin, cefazolin, daptomycin,
linezolid, oxacillin, penicillin-g and trimethoprim-sulfamethoxazole. Under the strict-alias
ranking the seven that drop are ampicillin, cefazolin, ciprofloxacin, gentamicin, oxacillin,
penicillin-g and trimethoprim-sulfamethoxazole; the strict ranking discards ciprofloxacin, the
fifth most prescribed agent in the frame, which is on its own sufficient reason not to build the
cut on it. [INFERENCE]

The debate arm is unaffected. `_ls_step3_impact.py` reads a copy of `runs/debate_20260818.jsonl`
taken on 18 August while the run was still live, holding 237 ordering-runs over 119 unique cases,
none quarantined. Round-0 recommendations are piperacillin-tazobactam on 236 runs and
ceftriaxone on 1. Final Agent A positions are cefepime on 133, ceftriaxone on 103 and
piperacillin-tazobactam on 1; final Agent B positions are cefepime on 133 and ceftriaxone on 104.
Every one of those agents sits inside the top ten under both the frequency ranking and the
strict-alias ranking, so 0 of 237 round-0 recommendations and 0 of 237 final recommendations
would fall outside a ten-agent answer space and become parse failures. [FACT] The same holds for
the scoreable-ten set proposed above, which also contains all three agents. [FACT]

Harm cases, defined as round-0 ADEQUATE collapsing to final Agent A INADEQUATE, number 25 of 237
runs. They are piperacillin-tazobactam to ceftriaxone on 15 runs and piperacillin-tazobactam to
cefepime on 10. All three agents survive every candidate set of size 5 or larger, so no harm case
involves a drug that narrowing would exclude, and the harm count is unchanged by the decision.
[FACT] This snapshot is larger than the 225-run figure in the project record because the run has
continued since that count was taken.

## 4. The trade-off

A smaller label set makes the classification problem cleaner and matches the 13 July direction,
and on this cohort it does so at close to zero cost in model behaviour, because the model's
realised answer distribution occupies only three of the seventeen labels. Cutting to ten changes
nothing about what has already been run. What it does change is what could have been run: any
agent removed from the answer space cannot be proposed, so it cannot be scored, so a systematic
error of that kind becomes invisible rather than observable. Removing vancomycin, linezolid,
daptomycin, oxacillin and penicillin-g means the study can no longer detect a model that reaches
for Gram-positive cover in Gram-negative bacteraemia, which is a real and clinically meaningful
failure mode; the counter is that the current design already cannot detect it, since all five of
those agents return UNDETERMINED on 200 of 200 cases. [LIMITATION]

The narrowing also discards agents the laboratory actually tests. Cutting from 17 to a
frequency-derived top 10 drops panel coverage from 88.19% to 66.87% of all pathogenic panel rows.
`_ls_step3_impact.py` shows the formulary was already missing agents the panel reports:
tobramycin appears on 210 panel rows across 195 of the 200 cases, piperacillin alone on 23 cases,
cefuroxime on 22, amikacin on 20, ertapenem on 4, imipenem on 3, tetracycline on 3, together
11.81% of all pathogenic panel rows. [FACT] Tobramycin is tested on 97.5% of these cases and
cannot currently be recommended or scored, which is a larger coverage gap than anything the
17-to-10 cut would create. [INFERENCE]

A second cost is comparability. The clinician comparator, the spectrum taxonomy and the
UNDETERMINED denominators in `clinician_comparator_v2_summary.json` were all computed against
the 17-agent formulary. Changing the label space means either regenerating those or carrying two
label spaces, one for the model and one for the comparator, and the second option needs to be
written down explicitly or the numbers will drift apart. [OPEN]

## Recommendation

Adopt the eleven scoreable agents, or the ten with ampicillin removed, rather than the top ten by
prescribing frequency. [INFERENCE] The reasoning is that the directive asks for a cleaner
classification problem, and a classification problem is only clean if every class has a
resolvable ground truth. Six of the seventeen current labels have no ground truth at all in this
population, and a frequency-derived top ten keeps two of them, vancomycin and levofloxacin,
while the strict-alias top ten keeps four, adding linezolid and daptomycin. The frequency top ten
would carry a mean
UNDETERMINED rate of 23.55% against 6.05% for the scoreability-ranked ten of the same size, cover
75.83% of formulary panel rows against 93.26%, and contain one label, vancomycin, that returns
UNDETERMINED on 200 of 200 cases while ranking first by frequency. Restricting the clinician
comparator to the same set converts 11 of 200 cases out of UNDETERMINED and loses no ADEQUATE
case, so the narrowing improves the comparator as well as the model's answer space.

Ampicillin is the marginal call. It is the eleventh agent by scoreability at 131 of 200 cases
tested and 37.0% UNDETERMINED, and it is the only agent in the set with real intrinsic-resistance
structure against Enterobacterales, which makes it informative about whether the model knows
basic Gram-negative pharmacology. Keeping it costs 2.81 percentage points of mean UNDETERMINED,
from 6.05% to 8.86%, and buys 6.42 points of formulary panel row coverage, from 93.26% to 99.68%.
Eleven is one over the number named on 13 July, and the direction as recorded said "up to 10
drugs or whatsoever", which does not read as a hard bound. [INFERENCE]

The decision is the supervisor's. [OPEN] The three things that need her ruling are whether the
cut is ten or eleven, whether the answer space is allowed to differ from the comparator's
formulary or both must move together, and whether losing the ability to observe Gram-positive
misfires is acceptable given that the current design cannot observe them either.

## Provenance

`_ls_step1_rank.py`, `_ls_step2_cardinality.py`, `_ls_step3_impact.py`, `_ls_step4_proposed.py`
and `_ls_step5_write.py` in `/Users/shamzzzh/brain_run` produced everything above. Intermediates:
`_ls_rank993.parquet`, `_ls_outcome_grid200.parquet`, `_ls_sweep.parquet`,
`_ls_perdrug200.parquet`, `_ls_proposed.parquet`, `_ls_step1.json`, `_ls_step2.json`,
`_ls_step3.json`, `_ls_step4.json`. The debate snapshot read is a copy of
`runs/debate_20260818.jsonl` at 237 ordering-runs. No file under `inputs/`, `corrected/`,
`protocol/` or the MIMIC-IV directory was written to, and no code the live runs depend on was
touched. Scoring throughout uses `ScoringConfig` fingerprint `04ce311c2b13`,
`intermediate_as='separate'`, `require_all_pathogens_covered=True`. No patient-level rows appear
in any output.
