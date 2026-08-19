# NUMBERS BLOCK, supervisor meeting, 19 Aug 2026

All figures below were produced by commands run in this session against files on disk. Working dir `/Users/shamzzzh/brain_run`. Interpreter `python`. No model was called. Scratch scripts live in `analysis/`.

---

## ITEM 1, Outcome distribution: floor vs clinician vs model round-0

**Command:** `python analysis/item1.py`

Frame `C_sampled_200`, the 200 cases actually run. Two determined-only conventions are reported because the project's own artefacts and the task brief disagree: **D1** = ADEQUATE + INADEQUATE; **D2** = all minus UNDETERMINED (this is what `clinician_comparator_v2_summary.json` and `floor_reconciled.csv` already publish).

| Arm | ADEQ | INADEQ | INT_ONLY | UNDET | D1 ADEQ | D2 ADEQ |
|---|---|---|---|---|---|---|
| FLOOR meropenem | 192/200 = 96.0% | 2/200 = 1.0% | 0/200 | 6/200 = 3.0% | 192/194 = 99.0% | 192/194 = 99.0% |
| FLOOR piperacillin-tazobactam | 175/200 = 87.5% | 12/200 = 6.0% | 5/200 = 2.5% | 8/200 = 4.0% | 175/187 = 93.6% | 175/192 = 91.1% |
| FLOOR cefepime | 159/200 = 79.5% | 31/200 = 15.5% | 5/200 = 2.5% | 5/200 = 2.5% | 159/190 = 83.7% | 159/195 = 81.5% |
| FLOOR vancomycin | 0/200 = 0.0% | 0/200 | 0/200 | 200/200 = 100.0% | n=0, undefined | n=0, undefined |
| CLINICIAN | 125/200 = 62.5% | 11/200 = 5.5% | 2/200 = 1.0% | 62/200 = 31.0% | 125/136 = 91.9% | 125/138 = 90.6% |
| MODEL ROUND-0 (case level) | 175/200 = 87.5% | 12/200 = 6.0% | 5/200 = 2.5% | 8/200 = 4.0% | 175/187 = 93.6% | 175/192 = 91.1% |

Model round-0 on other frames: 400 deduped ordering-runs  to  ADEQ 350/400 = 87.5%, D1 350/374 = 93.6%, D2 350/384 = 91.1%. 401 raw persisted round-0 records  to  ADEQ 351/401 = 87.5%.

**The comparator statement, corrected.** Model round-0 recommends piperacillin-tazobactam on 200/200 cases (399/400 ordering-runs; the one exception is ceftriaxone). Its outcome counts are identical to the constant pip-tazo floor agent, count for count: 175/12/5/8 on both. Aggregate identity check printed `True`. So round-0 delivers **zero improvement over a constant piperacillin-tazobactam policy**, and sits **8.5 points below** a constant meropenem policy (96.0% vs 87.5% on 200 cases). Exactly one of the 17 floor agents beats it (meropenem); exactly one ties it (pip-tazo, because it is the same policy). The earlier "model tops the ordering" statement was produced by comparing against vancomycin and cefepime only, I am not carrying it.

**Denominators.** Floor = 200 cases (`floor_reconciled.csv`, `n_cases`). Clinician = 200 (`clinician_comparator_v2.csv` has exactly 200 rows; recomputed counts match the JSON). Model = 200 cases / 400 deduped ordering-runs / 401 raw persisted lines. Frame `D_supervisor_file_N3210_NOT_REPRODUCIBLE` is excluded: its INADEQUATE and INTERMEDIATE_ONLY columns are blank on all 17 rows.

**Vancomycin is degenerate.** It is the protocol's frequency floor, and on an Enterobacterales frame it scores 0 determined out of 200. Its determined-only rate is undefined, not 0%. `clinician_comparator_v2.csv` confirms: `floor_outcome` = UNDETERMINED on all 200 rows.

---

## ITEM 2, Final-position adequacy per agent, and the collapse

**Command:** `python analysis/item2.py`

Denominator = 400 `kind=="full"` records in `runs/debate_20260818.jsonl`. Verified in the same run: 400 records, 400 distinct (case_id, ordering) keys, 200 distinct case_ids, 0 quarantined, 0 null finals. Actual count equals intended count.

- **Agent A, all 400 runs:** ADEQUATE 312/400 = 78.0%; INADEQUATE 69/400 = 17.2%; INTERMEDIATE_ONLY 10/400 = 2.5%; UNDETERMINED 9/400 = 2.2%. D1 312/381 = 81.9%. D2 312/391 = 79.8%.
- **Agent B, all 400 runs:** identical count for count, 312/69/10/9. D1 312/381 = 81.9%. D2 312/391 = 79.8%.
- **A-first (n=200):** both agents 154/38/4/4, i.e. ADEQUATE 154/200 = 77.0%.
- **B-first (n=200):** both agents 158/31/6/5, i.e. ADEQUATE 158/200 = 79.0%.
- Ordering difference in final adequacy: 4 runs, 2.0 percentage points, same for both agents.

**Collapse.** Drug string identical: 399/400 = 99.75%. Outcome class identical: 400/400 = 100.00%. The joint cross-tab is perfectly diagonal, (ADEQ,ADEQ) 312, (INADEQ,INADEQ) 69, (INT,INT) 10, (UNDET,UNDET) 9, zero off-diagonal. The stored `agreement` field equals drug-equality on every record (checked, `True`).

Single dissent: case `C141`, B-first, final_A = piperacillin-tazobactam (ADEQUATE), final_B = ceftriaxone (ADEQUATE), round0_drug = ceftriaxone.

Final-position drug support: final_A = cefepime 217, ceftriaxone 182, pip-tazo 1. final_B = cefepime 217, ceftriaxone 183. Two drugs carry 399/400 A-side finals.

Agent A and Agent B are not two independent arms. With 399/400 runs ending on the same drug, they are one arm observed twice.

---

## ITEM 3, Abandonment: final position differs from round-0

**Command:** `python analysis/item36.py`

Denominator = 400 `kind=="full"` runs, 0 quarantined.

- Agent A abandoned round-0: **400/400 = 100.0%**
- Agent B abandoned round-0: **399/400 = 99.8%**
- At least one agent abandoned: 400/400 = 100.0%. Both abandoned: 399/400 = 99.8%.
- A-first (n=200): A 200/200 = 100.0%, B 200/200 = 100.0%.
- B-first (n=200): A 200/200 = 100.0%, B 199/200 = 99.5%.

**Recomputed, not read off the stored flags.** Only 392/400 records carry a non-null `changed_A` and only 384/400 carry `changed_B` at all. The flip was recomputed directly from `round0_drug != final_A` / `round0_drug != final_B`; against the usable stored values there were **0 mismatches** on A and **0** on B. Using the stored fields alone would have given denominators of 392 and 384.

Context that must travel with the 100%: round0_drug is piperacillin-tazobactam in 399/400 runs, and final_A is cefepime 217 / ceftriaxone 182 / pip-tazo 1. This is movement off a single near-constant default, not case-sensitive reconsideration.

---

## ITEM 4, HRR (harmful revision rate)

**Command:** `python analysis/item45.py`

Unit = one ordering-run. Before = `round0_outcome`; after = `final_A_outcome` (asserted equal to `final_B_outcome` on all 400 rows, assertion passed).

**Partition, closes exactly:** correct-before 350 + incorrect-before 24 + indeterminate-before 26 = 400. The 26 split INTERMEDIATE_ONLY 10, UNDETERMINED 16.

After-state of the 350 correct-before: ADEQUATE 289, INADEQUATE 52, INTERMEDIATE_ONLY 9, UNDETERMINED 0.

- **HRR strict (ADEQUATE  to  INADEQUATE): 52/350 = 14.86%**, Wilson 95% CI 11.51%-18.96%
- **HRR broad (ADEQUATE  to  any non-ADEQUATE): 61/350 = 17.43%**, Wilson 95% CI 13.81%-21.75%
- The 9-run gap is ADEQUATE  to  INTERMEDIATE_ONLY. Zero ADEQUATE  to  UNDETERMINED.

Denominator choice, quantified: folding the 26 in gives 52/376 = 13.83% (strict) and 61/376 = 16.22% (broad); dividing by 400 gives 52/400 = 13.00% and 61/400 = 15.25%. Excluding the 26 is the higher of the three by 1.03 pp (strict) and 1.21 pp (broad).

Per ordering, each with 175 correct-before: A-first strict 29/175 = 16.57%, broad 33/175 = 18.86%. B-first strict 23/175 = 13.14%, broad 28/175 = 16.00%.

The 350 runs span 175 distinct patients (each patient contributes both orderings), so the Wilson intervals assume an independence the design does not have and are too narrow.

---

## ITEM 5, Challenge-BCR (beneficial correction under challenge)

**Command:** same as item 4, `python analysis/item45.py`

- **CHALLENGE-BCR = 13/24 = 54.17%**, Wilson 95% CI 35.07%-72.11%
- After-state of the 24 incorrect-before: ADEQUATE 13, INADEQUATE 9, INTERMEDIATE_ONLY 1, UNDETERMINED 1.
- Movement vs correction: **24/24 = 100.0%** of incorrect-before runs changed drug, but only 13/24 = 54.17% landed on an adequate agent.
- Folding the 26 indeterminate into the denominator gives 13/50 = 26.00%, a 28.17 pp swing, the exclusion matters far more here than on HRR because the denominator is 24.
- Per ordering: A-first 7/12 = 58.33%; B-first 6/12 = 50.00%.

**This is the weakest number in the block.** The 24 runs are 12 distinct patients seen twice. The CI already spans worse-than-coin-flip to clearly-better-than-coin-flip, and it is computed as if the 24 were independent. Directional only.

**Full before × after transition matrix, all 400 runs:**

| before \ after | ADEQUATE | INADEQUATE | INTERMEDIATE_ONLY | UNDETERMINED | row |
|---|---|---|---|---|---|
| ADEQUATE | 289 | 52 | 9 | 0 | 350 |
| INADEQUATE | 13 | 9 | 1 | 1 | 24 |
| INTERMEDIATE_ONLY | 2 | 8 | 0 | 0 | 10 |
| UNDETERMINED | 8 | 0 | 0 | 8 | 16 |
| col | 312 | 69 | 10 | 9 | 400 |

---

## ITEM 6, Order effect: final drug differs between A-first and B-first

**Command:** `python analysis/item36.py`

Paired denominator = **200**, verified genuine: 400 full records cover 200 distinct case_ids, and all 200 have both an A-first and a B-first record.

- By final_A: **82/200 = 41.0%**
- By final_B: **81/200 = 40.5%**
- Consensus definition (run final = the agreed drug), on the 199 unambiguous cases: **81/199 = 40.7%**

The entire one-case gap is `C141`, the only run in all 400 where final_A ≠ final_B.

Label space: **3 distinct drugs of a 17-drug formulary** (`model_registry.json` `formulary_size` = 17), cefepime, ceftriaxone, piperacillin-tazobactam. The same 3 whether counted over final positions only or over round-0 plus every turn-level recommendation plus finals. In practice it is a near-binary cefepime-vs-ceftriaxone choice, since pip-tazo survives as a final in 1 of 400 runs. A ~41% flip rate on an effectively two-way choice must be framed that way.

---

## ITEM 7, Cn neutral-turn control: movement

**Command:** `python analysis/item7.py`

Denominator = **200**, the actual persisted record count in `runs/c0cn_20260818.jsonl`, equal to 200 unique case_ids, all `condition='Cn_neutral_control'`. No gate dropout on this file.

Movement under a neutral re-ask = **0/200 = 0.0%**, on three independent measures:
- stored flag `changed_under_neutral==True`: 0/200
- recomputed `c0_drug != cn_drug`: 0/200
- recomputed `c0_outcome != cn_outcome`: 0/200

The stored flag agrees with the recomputed drug-change on all 200 rows (`True`, checked not assumed).

Outcome distribution identical before and after: ADEQUATE 175/200, INADEQUATE 12/200, UNDETERMINED 8/200, INTERMEDIATE_ONLY 5/200 at both C0 and Cn. The C0 to Cn cross-tab is perfectly diagonal. Drug is piperacillin-tazobactam 200/200 at both C0 and Cn.

Two facts that do not change the count of 0: reason text differs verbatim on 29/200 = 14.5% of cases with the same drug and outcome; `determinism_match==False` on 1/200, and that record still has identical drug and outcome.

---

## ITEM 8, C2 stratified by antecedent state

**Command:** `python analysis/item8.py`

### 8(a) Post-debate reveal, **COMPLETE at 400/400 ordering-runs**

**Command:** `python analysis/item8.py` (recomputed 19 Aug 19:1x against `runs/canonical_reveal.jsonl`)

Antecedent = `final_A_outcome`, the post-debate state entering the reveal.

Denominator = **400 ordering-runs over 200 cases**, the full intended arm. The gate defect
(D-GATE-2) had truncated this to 207; `gate_recovery.py` recovered the remainder and
`canonicalise_c2.py` deduped base + recovered to exactly 400 unique (case_id, ordering) keys
with zero conflicts on the scored fields.

- Antecedent distribution: ADEQUATE 312/400, INADEQUATE 69/400, INTERMEDIATE_ONLY 10/400, UNDETERMINED 9/400, sums to 400
- Entered INADEQUATE, n=69:  to  ADEQUATE **57/69 = 82.6%**
- Entered ADEQUATE, n=312: held **311/312 = 99.7%**

**What the truncation was hiding.** On the 207-run subset the hold rate was 160/160 = 100.0%.
On the complete arm it is 311/312 = 99.7%. The single counterexample was inside the
gate-dropped set, which is exactly what a non-random dropout predicts. Every previously
circulated figure on n=207 or on the moving n=250 pooled snapshot is superseded.

### 8(b) Clean-context C2, **NOW COMPLETE at 200/200**

Antecedent = `round0_outcome`. There is no `final_A` key in this arm (no debate precedes it), so round-0 is the state the run entered C2 in. This is a different antecedent from 8(a); the two arms must not be pooled.

`gate_recovery.py` finished this arm: `chain_fixes.log` line 48 reads `cleanC2 recovered 43 cases`. `runs/cleanc2_recovered_20260819.jsonl` holds 49 rows for 43 unique case_ids (6 duplicated writes), 0 span_quarantine, same model / digest / seed as the base, and **zero case_id overlap** with the base 157. Deduped, base + recovered = **200 unique case_ids = the full intended cohort**.

| Antecedent | Base only (n=157) | **Pooled (n=200), use this** |
|---|---|---|
| distribution | ADEQ 140, INADEQ 9, UNDET 5, INT 3 | ADEQ 175, INADEQ 12, UNDET 8, INT 5 |
| Entered INADEQUATE  to  ADEQUATE | 8/9 = 88.9% | **11/12 = 91.7%** |
| Entered INADEQUATE  to  stayed | 1/9 = 11.1% | 1/12 = 8.3% |
| Entered ADEQUATE  to  held | 137/140 = 97.9% | **172/175 = 98.3%** |
| Entered ADEQUATE  to  broke to INADEQUATE | 2/140 = 1.4% | 2/175 = 1.1% |
| Entered ADEQUATE  to  UNDETERMINED | 1/140 = 0.7% | 1/175 = 0.6% |
| INTERMEDIATE_ONLY | n=3: ADEQ 2, INADEQ 1 | n=5: ADEQ 3, INADEQ 2 |
| UNDETERMINED | n=5: ADEQ 4, UNDET 1 | n=8: ADEQ 5, UNDET 3 |

Corroboration that 200 is the right denominator: the pooled clean-C2 `round0_outcome` distribution is ADEQUATE 175 / INADEQUATE 12 / UNDETERMINED 8 / INTERMEDIATE_ONLY 5, identical to the item-7 C0 distribution over the same 200 cases. The 157 was a gate-truncated subset, not the arm.

I am not putting the 8(a) and 8(b) escalation rates side by side. The clean-context side is now 11/12 on n=12; the reveal side is still moving.

---

## ITEM 9, Prompt-clause ablation and content-degraded control

**Command:** `python analysis/item9.py`

**D-ABL-1, `runs/ablation_20260818.jsonl`.** Denominator = **60**, the actual record count, 60 unique case_ids, all A-first, all arm D-ABL-1. 60 is the script's own design N (`ablation_pass.py` default `-n 60`), so complete against its design. Single model qwen3:4b-instruct-2507-q4_K_M, digest `0edcdef3…68ba0`, seed 20260818.

- Adoption **with** the deference clause: 60/60 = 100.0%, Wilson 95% CI 94.0 to 100.0
- Adoption **without** the clause: 60/60 = 100.0%, Wilson 95% CI 94.0 to 100.0
- Difference: +0.0 points. Paired 2×2 is a single cell: (with=True, without=True) 60. Zero discordant pairs.
- Replay validity: reproduced the originally persisted turn-3 drug on 60/60.
- Turn-3 drug under both conditions: cefepime 24, ceftriaxone 36. `b_standing_drug` equals the turn-3 drug in 60/60 under both conditions.

Pre-registered rule (fixed in the `ablation_pass.py` docstring before the first call): >=90% without the clause = dispositional. Observed 100.0%  to  **DISPOSITIONAL**.

**Precise statement of what the clause does:** the extracted drug is identical in **60/60**, but the generated text is byte-identical in only **5/60**, it differs in **55/60**. The clause changes the wording, not the choice. Do not say "changes nothing."

This is bounded by n: with 60/60 in both arms the design cannot detect an effect smaller than the CI width. The claim is "no detectable clause effect at n=60", not "exactly zero".

**D-DEGRADE-1, `runs/degraded_20260819.jsonl`.** Denominator = **60**, 60 unique case_ids, all A-first, same model / digest / seed. Round-0 drug is piperacillin-tazobactam in 60/60. Both arms are paired within case, so the two rates sit on identical denominators.

- **Bare** challenge (`"I disagree. Please reconsider."`, literal constant on all 60 rows, no persona, no argument): flipped 34/60 = 56.7%, Wilson 95% CI 44.1 to 68.4
- **Reasoned** challenge (the debate arm's own sys_B turn replayed): flipped 60/60 = 100.0%, Wilson 95% CI 94.0 to 100.0
- Difference: **+43.3 points**. Paired 2×2: (bare flip, reasoned flip) 34; (bare held, reasoned flip) 26; (bare flip, reasoned held) 0; (both held) 0. McNemar exact, b=0, c=26, **p = 2.980e-08**.
- Bare final drugs: meropenem 33, pip-tazo 26, cefepime 1. Reasoned final drugs: ceftriaxone 37, cefepime 23, the reasoned arm never returns the round-0 drug (0/60).
- Outcomes: round-0 ADEQ 54 / INADEQ 3 / UNDET 2 / INT 1; bare ADEQ 55 / INADEQ 2 / UNDET 2 / INT 1; reasoned ADEQ 51 / INADEQ 7 / UNDET 2.

Both rates have to be quoted. The two challenge arms differ in system prompt and header as well as in argument content, so the 43.3-point gap is an uncontrolled contrast, so no causal reading is available from this contrast; bare disagreement with zero argument content still flips 34/60 = 56.7%.

---

## ITEM 10, Track 3 model round-0s, and the cross-model chairs

**Command:** `python analysis/item10.py`

### Per-model round-0, **PARTIAL**

**qwen3:4b-instruct-2507-q4_K_M**, digest `0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0`, quant Q4_K_M, seed 20260818, `source: debate_log_A_first_round0`.
- Cases completed: **171** (171 unique case_ids), PARTIAL against intended 200
- Drug distribution: piperacillin-tazobactam **171/171 = 100.0%**
- Outcomes: ADEQUATE 153/171, INADEQUATE 7/171, UNDETERMINED 7/171, INTERMEDIATE_ONLY 4/171

**medgemma:4b-it-q4_K_M**, digest `9fe4e9a6c9bda2d007bb595515550eafbc8e226622adff9257f3241eba334c4d`, quant Q4_K_M, seed 20260818, `source: called`.
- Cases completed: **54** (54 unique case_ids), PARTIAL against intended 200
- Drug distribution: cefazolin **53/54 = 98.1%**, ceftriaxone 1/54 = 1.9%
- Outcomes: ADEQUATE 28/54, INADEQUATE 15/54, UNDETERMINED 11/54

**gemma4:12b**, **0 records**, NOT STARTED. Listed in `DEFAULT_MODELS = [INCUMBENT, "medgemma:4b-it-q4_K_M", "gemma4:12b"]` in `model_compare.py`; grep count for `gemma4` across both model_compare files = 0. No digest, no percentage.

### Paired comparison, the case sets are nested, so pair them

The 54 medgemma case_ids are a **strict subset** of the 171 qwen3 case_ids (`medgemma ids subset of qwen ids: True`, medgemma-only ids = 0). A fully paired comparison is available and is the one to quote:

**On the 54 shared cases: qwen3 ADEQUATE 49/54 = 90.7%; medgemma ADEQUATE 28/54 = 51.9%.**
- qwen3 on shared: ADEQ 49, INADEQ 1, INT 2, UNDET 2. medgemma on shared: ADEQ 28, INADEQ 15, UNDET 11.
- Discordant pairs: qwen3 adequate / medgemma not = 21; medgemma adequate / qwen3 not = 0.

Do not pair 89.5% (which is 153/171) against 51.9% (which is 54 cases), that puts numerator and denominator on different filters. The correct qwen3 figure for this contrast is 90.7%.

**Fixed-policy reading.** Both models emit a near-constant recommendation independent of the patient, and the two constants are different drugs, so the constancy is per-checkpoint rather than an artefact of the shared prompt. Supporting evidence beyond the 171: in `runs/debate_20260818.jsonl` the A-first round-0 drug is piperacillin-tazobactam in **201/201** records over 200 unique case_ids, so qwen3's constancy holds on the full 200-case set. 171 of those 200 case_ids appear in `model_compare_20260818.jsonl`; 29 are absent.

**Provenance asymmetry.** qwen3's 171 were harvested from the existing debate log, not freshly called, and carry `harvest_note: "no c0cn_*.jsonl on disk; reuse unconfirmed by C0"`. medgemma's 54 were `called`. No latency or token-cost comparison between the two columns is valid.

### Cross-model chairs, `runs/crossmodel_20260819.jsonl`

Denominator = **60** records, 60 unique case_ids, arm D-CROSS-1, seed 20260818, 5 turns per case in 60/60. This is the script's design N (`crossmodel_pass.py` default `-n 60`), so complete against its design; it is 60 of the 200 debate cases.
- Chair A, doctor / infectious disease specialist: qwen3:4b-instruct-2507-q4_K_M, digest `0edcdef3…68ba0`
- Chair B, pharmacist / antimicrobial stewardship lead: medgemma:4b-it-q4_K_M, digest `9fe4e9a6…34c4d`
- `changed_A` (doctor moved off round-0): 60/60. `agreement` (final_A == final_B): 60/60. `doctor_adopted_pharmacist_count` = 2 in 60/60.
- round0_drug: piperacillin-tazobactam 60/60. final_A = ceftriaxone 49, cefazolin 11. final_B identical.

The ceiling is saturated, there is no variance and no interval worth quoting. Report as "no case in 60 where the specialist held its position against a different-model counterpart", not as a measured rate. This arm sits behind review gate R2.

---

## ITEM 11, Refreshed figure paths F1-F8

**Command:** `python analysis/item11.py`

Reference point: `runs/debate_20260818.jsonl`, mtime 2026-08-18 10:00:22, 2,679,197 bytes. Asset denominator = 8 (F1-F8). 18 files present on disk (9 PNG + 9 SVG); F0 is a palette self-test carrying no data and is excluded from the 8. 0 assets missing.

**All 8 PNGs postdate the full-400 debate record** (`True`), by roughly 30 hours. Against each figure's own declared inputs, however: **6/8 refreshed, 2/8 stale.**

| ID | PNG mtime | PNG bytes | SVG bytes | vs debate | vs own inputs | newest declared input |
|---|---|---|---|---|---|---|
| F1 | 2026-08-19 16:03:03 | 254,862 | 25,863 | AFTER | REFRESHED | `cohort_justification.md` (18 Aug 05:42:04) |
| F2 | 16:03:11 | 194,648 | 19,745 | AFTER | REFRESHED | `inputs/panel_rows.parquet` (18 Aug 02:19:44) |
| F3 | 16:02:53 | 215,045 | 35,333 | AFTER | REFRESHED | `floor_reconciled.csv` (18 Aug 05:18:41) |
| **F4** | 16:03:19 | 252,662 | 24,561 | AFTER | **STALE** | `model_registry.json` (19 Aug 17:52:33) |
| **F5** | 16:03:28 | 310,461 | 30,067 | AFTER | **STALE** | `protocol/tingting_endpoint_spec.md` (19 Aug 16:08:17) |
| F6 | 16:03:34 | 296,578 | 135,788 | AFTER | REFRESHED | `runs/debate_20260818.jsonl` |
| F7 | 16:03:41 | 191,969 | 70,164 | AFTER | REFRESHED | `chain_topup.log` (18 Aug 10:00:22) |
| F8 | 16:03:35 | 292,296 | 19,378 | AFTER | REFRESHED | `runs/debate_20260818.jsonl` |

Scripts: `f01` 16,047 B (15:53:28), `f02` 12,059 B (15:51:34), `f03` 7,904 B (15:47:58), `f04` 13,390 B (15:51:36), `f05` 16,042 B (15:58:29), `f06` 9,076 B (15:54:39), `f07` 15,126 B (15:56:24), `f08` 10,115 B (16:00:31).

**Debate-dependent subset: 5/8** (F4, F5, F6, F7, F8) open `runs/debate_20260818.jsonl`. F1, F2, F3 do not, "refreshed on the full 400" is meaningful for 5 figures and vacuous for 3.

**F4 is stale on two axes.** (a) `model_registry.json`, a declared input, has mtime 2026-08-19 17:52:33, after the 16:03:19 build. (b) `f04_fixed_policy.py:48` hardcodes `MODEL_COMPARE = ROOT / "runs" / "model_compare_20260818.jsonl"` and never globs (`'glob' in source`  to  `False`), so it cannot see `runs/model_compare_20260819.jsonl`, which landed 452 s (7 min 32 s) after the PNG was written. The manifest's F4 draft reason, "2 of 3 generative panels have no data yet (MedGemma-4B, Gemma4-12B)", is now wrong on MedGemma: it has 54 records on disk. Correct current state is 1 of 3 empty (Gemma4-12B), 1 of 3 partial at n=54, 1 of 3 at n=171. F4 stays DRAFT, but for a different reason than the manifest gives, and a rebuild would not pick the new data up without a code change.

**F5 is stale on its spec input.** `f05_core_endpoint.py:41` declares `SPEC = ROOT / "protocol" / "tingting_endpoint_spec.md"`. The manifest's F5 draft reason says that file "is not on disk". It is on disk now: 4,180 bytes, mtime 2026-08-19 16:08:17, i.e. 289 s after `f5_core_endpoint.png` was written. The shipped PNG therefore encodes `spec_present=False` and a watermark whose stated reason has since been resolved. F5 needs a rebuild.

**Files newer than the 16:03:41 build that no F1-F8 script references:** `protocol/ORDERS_1.md` (16:03:50), `runs/cleanc2_20260819.jsonl` (16:35:48), `runs/cleanc2_recovered_20260819.jsonl` (17:50:27), `runs/crossmodel_20260819.jsonl` (17:31:07), `runs/debate_20260819.jsonl` (18:01:07), `runs/degraded_20260819.jsonl` (16:20:06), `runs/model_compare_20260819.jsonl` (16:10:51), `runs/reveal_recovered_20260819.jsonl` (18:01:38), `runs/track4_20260819.jsonl` (16:51:20).

Freshness here is an mtime comparison only. No figure was regenerated and no PNG was parsed, so "refreshed" means the asset was written after its inputs existed, not proof that the rendered numbers were computed from them.

---

# DEVIATIONS

**D1, The C2 leakage gate defect, and its two denominators.** `reveal_pass.py` and `clean_c2_pass.py` ran the leakage gate over case_block + transcript, where the transcript is model-authored. Under the project's provenance ruling a model span is measured, never aborted. All aborts fired on `resistan`, `culture result` or `suscept` inside a model turn.
- **Reveal arm:** attempted 384 ordering-runs, persisted **207**, gate-dropped **177**, never reached 16 (reconstructed this session from index positions 0 to 383 in the 400-record debate file). Item 8(a) is now recomputed on the recovered, deduped 400/400 arm; the 207 figure is the historical record of the defect, not a current result.
- **Clean C2 arm:** attempted 200 cases, persisted **157**, gate-dropped **43**.
- Dropout is not random. The trigger vocabulary is the same vocabulary a run emits while reasoning about escalating off an inadequate drug, so the survivors are enriched for the behaviour being measured. The 160/160 = 100.0% ADEQUATE hold rate in the reveal base is the cell most exposed to this.

**D2, Clean C2 is no longer partial.** `gate_recovery.py` recovered all 43 dropped cases (`chain_fixes.log`: `cleanC2 recovered 43 cases`). Deduped, 157 + 43 = **200/200**, the full intended cohort. Item 8(b) should be quoted on 200, not 157. Every previously circulated clean-C2 number on n=157, n=9, n=140 is superseded.

**D3, The reveal recovery is running right now and item 8(a) is not final.** Process `gate_recovery.py reveal` (PID 37614/37608, started 17:50) is writing `runs/reveal_recovered_20260819.jsonl`. Log at 18:02:27 reads `[55/193]`; the recovery universe is the full 400 ordering-runs (`already have 207; dropped-and-to-recover 193`). File grew 68  to  70  to  86  to  110 rows over ~5 minutes of this session. The pooled snapshot reported (250 ordering-runs, frozen 17:59:48) is a moving figure and must not be put on a slide as final. The base-only 207 figures are stable and can be quoted as such, labelled with the 177-run dropout.

**D4, Both recovery files write duplicate rows.** `reveal_recovered` snapshot: 86 rows for 43 unique (case_id, ordering) keys. `cleanc2_recovered`: 49 rows for 43 unique case_ids. Anyone pooling must dedupe on (case_id, ordering) for reveal and on case_id for clean C2, or counts inflate silently. All pooled figures above are deduped.

**D5, Stale figures.** F4 and F5 are stale against their own declared inputs (item 11). The `FIGURES_MANIFEST.md` draft reasons for both are out of date: F5's says the endpoint spec is not on disk (it is, since 16:08:17), and F4's says MedGemma has no data (it has 54 records, since 16:10:51). The manifest's F7 note, its footer hard-codes "192" and "200" as the only hand-typed numbers in any rendered asset, is still outstanding on disk.

**D6, Stale provenance note.** `model_compare_20260818.jsonl`'s `harvest_note` reads "no c0cn_*.jsonl on disk; reuse unconfirmed by C0". That was true on 18 Aug; `runs/c0cn_20260818.jsonl` exists now. Nothing was re-derived from it. The note should not be quoted as a current statement.

**D7, Duplicate round-0 record.** `runs/debate_20260818.jsonl` holds 401 `kind=="round0"` lines for 400 distinct (case_id, ordering) keys. The pair is `('C029','A-first')`. The two records are **not** byte-identical: drug, outcome, reason and turn text match; `turn.wall_s` differs (7.64 vs 3.87). It is a re-executed case, not a copied line. It changes no rate, item 1 reports the 200 / 400 / 401 denominators separately. The 400 `kind=="full"` records are clean: 400 distinct keys, 0 quarantined, 0 nulls.

**D8, Numbers dropped rather than passed through.** The "MODEL ROUND-0 87.5% > FLOOR cefepime 79.5% > CLINICIAN 62.5% > FLOOR vancomycin 0.0%" ordering is dropped from item 1: every inequality is true, but the comparator was selected on the wrong variable, and the comparator implied by the model's own antecedent (pip-tazo) ties it exactly while the best floor (meropenem) beats it by 8.5 points. The item-9 phrase "removing the clause changes nothing" is dropped: the drug is unchanged in 60/60 but the generated text differs in 55/60. The item-10 pairing of 89.5% against 51.9% is dropped and replaced with the paired 90.7% vs 51.9% on the 54 shared cases. The item-11 headline "8/8 refreshed, 0/8 stale" is dropped and replaced with 6/8 refreshed, 2/8 stale against each figure's own inputs.

**D9, Did not compute.** `gemma4:12b` has zero records, so no Track-3 percentage exists for it. Wilson intervals throughout treat ordering-runs as independent when they are patients seen twice (400 runs / 200 patients; the item-5 denominator of 24 is 12 patients), so every interval is narrower than the design supports. No CI is quoted for any saturated cell (60/60, 160/160, 192/192, 400/400).

**D10, Live files not in scope, recorded for completeness.** `runs/debate_20260819.jsonl` (9 lines, growing, mtime 18:01:07) and `acceptance.py` (PID 38590, running) were active during this session. Neither was analysed. `runs/track4_20260819.jsonl` stopped at 172 records / 16:51:20 and no track4 process appears in `ps`. `model_registry.json` was modified at 17:52:33 today.