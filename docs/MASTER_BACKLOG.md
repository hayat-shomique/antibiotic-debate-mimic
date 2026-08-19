# Master backlog

Regenerated from disk by `build_backlog.py` at 19:18 on 19 August 2026. Nothing in this file is remembered; every row runs a check against the filesystem. Delete an artefact and its row returns to OPEN on the next build.

**RUNNING** 1  **OPEN** 12  **BLOCKED** 2  **DONE** 23

## RUNNING (1)

| id | commitment | source | evidence on disk |
|---|---|---|---|
| `E7` | Confidence before and after; correct+confident -> wrong+confident | Zhu endpoint spec | confidence_pass.py built; 162/200 run |

## OPEN (12)

| id | commitment | source | evidence on disk |
|---|---|---|---|
| `E6` | DeltaQ compared across Doctor->Pharmacist and Pharmacist->Doctor | Zhu endpoint spec | run and case level only; per-direction split not written |
| `E9` | Time to appropriate therapy | Zhu endpoint spec | specified, not run - declared unrun in the deck |
| `E10` | Treatment failure / deterioration; mortality; LOS | Zhu endpoint spec | specified as secondary/cautious; deliberately not run; stated as such |
| `M4` | Rebuild F4 and F5, stale against their own declared inputs | numbers block | F4 hardcodes the 18 Aug model_compare path; F5 encodes spec_present=False |
| `M5` | F7 footer hard-codes 192 and 200 - the only hand-typed numbers in any asset | numbers block | flagged in FIGURES_MANIFEST; not yet fixed |
| `A1` | Model 2x2 round-0: MedGemma-4B and a scale model to 200 | ORDERS_1 Track 3 | MedGemma 225 model-case pairs; gemma4:12b has 0 records |
| `A4` | C1 scripted pressure, four sub-types - the protocol's PRIMARY arm | protocol_v1 primary arm | smoke test only: 3 cases |
| `A5` | Few-shot arm with disjointness assertion | ORDERS_1 | fewshot_pass.py built, never run |
| `A6` | Self-consistency arm: parallel sampling, length-penalised majority vote | Oh et al. 2026 | not built - closes an obvious referee question |
| `S2` | Drug-matched seeded design: hold the drug fixed, vary only the panel verdict | self-found | the only design that can earn an evidence-discrimination claim; not built |
| `X2` | State the novelty claim, restricted to verified corpus rows | user 19 Aug | positioning.md predates the four-paper integration |
| `D9` | README so a new reader can understand, run and reproduce | user 19 Aug | no README exists |

## BLOCKED (2)

| id | commitment | source | evidence on disk |
|---|---|---|---|
| `D7` | Guideline flags, researcher-supplied only | R3 | guideline_flags_FILLSHEET.csv delivered; awaiting your filled sheet |
| `D8` | Freeze the panel-approved slide sentence | PATCH v3 V11 | the sentence was never included in the message; nothing invented in its place |

## DONE (23)

| id | commitment | source | evidence on disk |
|---|---|---|---|
| `E1` | Susceptibility concordance of the FINAL recommendation, per agent (primary) | Zhu endpoint spec | NUMBERS_BLOCK.md item 2: A and B both 312/400 = 78.0% |
| `E2` | Spectrum appropriateness: under / optimal / over-treated | Zhu endpoint spec | spectrum_results.csv per arm |
| `E3` | Escalation / de-escalation correctness once results arrive | Zhu endpoint spec | clean-context C2: 200/200 |
| `E4` | Same, post-debate reveal arm, all 400 ordering-runs | Zhu endpoint spec | reveal: 400/400 |
| `E5` | HRR and BCR with a closing partition | Zhu endpoint spec | HRR 52/350 = 14.9%; BCR 13/24 = 54.2%; 350+24+26 = 400 |
| `E8` | Core figure: appropriateness by agent x condition x counterpart correctness | Zhu endpoint spec | f5 exists but STALE: encodes spec_present=False, spec landed 289s later |
| `M1` | D-GATE-2: correct the C2 leakage gate to the three-class ruling | self-found | canonical gate_pre_reveal; fault injection 10/10; acceptance 36/36 |
| `M2` | Recover every run the defective gate dropped | self-found | reveal recovery: 400/400 |
| `M3` | One deduped canonical C2 dataset so nothing downstream pools differently | self-found | canonicalise_c2.py; 0 conflicts between base and recovered |
| `A2` | Seeded counterpart correctness, both directions, 4 cells | ORDERS_1 Track 4 / R1 | 172 of an achievable 174; S- cells are capped at 27/60 by panel content, not by a bug |
| `A3` | Cross-model debate, review-gated before any deck use | R2 | 60/60 run; REVIEW GATE still open - needs one annotated transcript plus a ten-line explainer |
| `S1` | Signal-detection metric (d', criterion c) on the seeded arm | prior design review | computed: pooled J +0.433 but CONFOUNDED; drug-matched J = 0.000 on the only two drugs tested in both roles. Reported as a spectrum preference, not discrimination |
| `S3` | Read SycEval and the warmth/sycophancy paper she sent | Zhu 13 Jun email | SYCOPHANCY_CANON.md |
| `S4` | Military-grade completeness sweep of every file | user 19 Aug | COMPLETION_AUDIT.md |
| `X1` | Make the prompting explainable end to end | user 19 Aug | EXPLAINABILITY.md |
| `X3` | Pressure-test every claim against recent literature | user 19 Aug | LITERATURE_PRESSURE_TEST.md |
| `X4` | S.C.O.R.E. - blocked pending a verified corpus entry | ORDERS_1 | verified via PubMed (PMID 42349414, doi 10.1016/j.xcrm.2026.102883); in references.bib and LITERATURE.md tier 2. Safety, Consensus & Context, Objectivity, Reproducibility, Explainability |
| `D1` | Numbers block, every figure recomputed with its command | user 19 Aug | NUMBERS_BLOCK.md, 11 items, 13 agents, 5 of 6 first passes rejected |
| `D2` | Four papers broken down and used entirely | user 19 Aug | PAPERS_INTEGRATION.md; 4 BibTeX entries appended |
| `D3` | Crystallised slide specifics for interns and specialists | user 19 Aug | SLIDE_PLAN.md, 12-slide spine |
| `D4` | Restructure to a clean, neutrally named project with no AI attribution | user 19 Aug | MIGRATION_PLAN.md |
| `D5` | Audit page and kanban rebuilt and republished each turn | standing | republished; 57 cards |
| `D6` | Sequential ledger of every instruction | user 18 Aug | INSTRUCTION_LEDGER.md |
