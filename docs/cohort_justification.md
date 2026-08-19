# Cohort and specification justification

Every choice below names what justifies it: a supervisor's verbatim words, a protocol line, a
deviation entry, or a measurement with its producing file. Written 18 August 2026.

---

## 1. Cohort — the restriction chain

**Gate ordering matters for the narrative, not the arithmetic.** The two large gates are
applied as linkage-then-organism in `debate_run.select()`, and `enterobacterales_ids()` itself
pre-filters to linked cases, so the organism gate is never applied to the full cohort. The gates
are commutative — both orderings land on the same 993 — but quoting "Enterobacterales 1,087"
without saying "after linkage" tells a false causal story.

### Marginal effect of each gate, applied alone to the frozen cohort

| gate applied alone | n | % of cohort |
|---|---|---|
| frozen cohort | 7,796 | 100% |
| Enterobacterales (organism gate itself) | **3,104** | 39.8% |
| admission-linked | **3,107** | 39.9% |
| no sustained prior therapy | 7,390 | 94.8% |

The two big gates each remove about 60% and are close to independent; their intersection is
1,087 rather than the 1,241 that exact independence would predict.

### Applied order, as `debate_run.select()` executes

| step | before | after | removed | deviation |
|---|---|---|---|---|
| 1. admission linkage | 7,796 | 3,107 | 4,689 | D-COHORT-2 |
| 2. Enterobacterales | 3,107 | 1,087 | 2,020 | D-POP-1 |
| 3. no sustained prior therapy | 1,087 | **993** | 94 | D-PRIORABX-1 |
| 4. sampled, seed 20260818 | 993 | 200 | — | largest N under the cap |

Counterfactual ordering (organism first, then linkage) gives 7,796 → 3,104 → 1,087 → 993 —
the identical final set.

**Final frame 993 = 12.7% of the frozen cohort.**

### Upstream waterfall (`cohort_gates_skeleton.csv`)

| gate | n | excluded |
|---|---|---|
| index events (panel-bearing first positive blood culture) | 9,236 | — |
| bacterial pathogen (not contaminant, not fungal) | 7,799 | −1,437 |
| adults 18+ at index | 7,799 | −0 |
| at least one formulary agent tested | 7,796 | −3 |

`index_classified.parquet` holds 9,236 rows because it records index **events**, before the
bacterial-pathogen and formulary gates; `cohort_skeleton.parquet` holds the 7,796 that survive.

**Index event.** Earliest panel-bearing positive blood culture per patient,
`min(COALESCE(charttime, chartdate))` then
`row_number() OVER (PARTITION BY subject_id ORDER BY index_time, micro_specimen_id) = 1`
(`build_index.py` lines 22–31). Specimen filter is `spec_type_desc = 'BLOOD CULTURE'` exactly,
not `ILIKE '%BLOOD%'` — D-SPEC-1.

### Selection effect, quantified

| frame | n | median age | % female | in-hospital mortality |
|---|---|---|---|---|
| frozen cohort | 7,796 | 66 | 43.1% | 19.4% |
| admission-linked | 3,107 | 65 | 40.8% | 19.4% |
| Enterobacterales | 1,087 | 67 | 43.3% | 16.7% |
| final frame | 993 | 67 | 44.1% | 16.3% |

Age and sex are stable. Mortality falls 3.1 points, expected because Enterobacterales bacteraemia
carries lower mortality than a mix containing *S. aureus* and *Enterococcus*.

**Honesty note.** The 19.4% figure is computed on the 3,107 cases with a linked admission; the
4,689 unlinked cases have no `hospital_expire_flag`. It is not a whole-cohort mortality.

### Scope of any claim
Results apply to **admission-linked Enterobacterales bacteraemia without sustained prior
therapy**, never to "bacteraemia". The majority of the frozen cohort — 6,391 Gram-positive cases —
is excluded because the external arbiter does not exist there. That is the principal limitation
and simultaneously a finding about how clinical LLMs can be evaluated.

---

## 2. Protocol freeze (`protocol_freeze.json`, read-only)

| field | value |
|---|---|
| frozen at | 2026-08-18T03:37:17.416781+01:00 |
| cohort content hash | `4a4f4f782eb17345e0e9eab1cc596aab9ebf6442890bd1c3b82761ae3c65d414` |
| model checkpoint digest | `0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0` |
| seed | 20260818 |
| ScoringConfig fingerprint | `04ce311c2b13` |
| brain_scoring SHA-256 | `6f298a53925b244e65c9687fce80e9a826694fdb0e99c49fa42f011ceb6b20bb` |

`brain_scoring_local.py` v3 was compared against the frozen copy with docstrings stripped: AST
behaviour hashes identical, so the v3 corrections are comment-only and the run stands.

---

## 3. Model

| parameter | value | justified by |
|---|---|---|
| model | `qwen3:4b-instruct-2507-q4_K_M` | D-MODEL-2 |
| quantization | Q4_K_M | as specified |
| temperature | 0 | determinism; transcripts byte-identical across repeat runs |
| seed | 20260818 | pre-registered |
| num_predict | 512 | caps runaway generation |
| num_ctx | 8192 | max observed `prompt_eval_count` 573 = 7% of window |
| think | False | belt-and-braces; the checkpoint cannot think |

**Why this checkpoint.** `qwen3:4b` (hybrid) could not be made non-thinking: `think:false`
relocated reasoning into `content`; `/no_think` moved it to a separate field; both still spent
1,000–1,588 output tokens per call. `instruct-2507` gives 64 output tokens and zero `<think>`.

**Comparison set** (D-MODEL-2): `qwen3:4b-instruct-2507-q4_K_M` (incumbent) /
`medgemma:4b-it-q4_K_M` (size-matched, domain) / `gemma4:12b` (scale). MedGemma has no 12B
(D-MODEL-1). Qwen 3.8 27B rejected: Q3_K_M confounds quantisation with scale; 11.5 GB collides
with a live run on 16 GB; it reintroduces `<think>` tags.

---

## 4. Debate protocol

| choice | value | justified by |
|---|---|---|
| Agent A | infectious disease specialist | Zhikang, verbatim: *"assign Agent A the identity of an infectious disease specialist and Agent B the role of antimicrobial stewardship lead — so that each has a clear, potentially conflicting incentive"* |
| Agent B | antimicrobial stewardship lead | same quote |
| exchanges | 3 (5 turns) | `protocol_v1.md` D1 |
| orderings | A-first and B-first, paired on case | Zhikang: *"they alternate roles over several rounds"*; D2 |
| B sees panel | never | D1, challenger blinded |
| round-0 framing | none | round-0 purity; "persona-conditioned zero-shot" |

## 5. Scoring

| parameter | value | consequence |
|---|---|---|
| `intermediate_as` | `'separate'` | I is its own outcome, never folded into the binary |
| `untested_policy` | `'category'` | untested agent → UNDETERMINED, not counted wrong |
| `require_all_pathogens_covered` | True | polymicrobial adequate only if every isolate covered |
| `combination_rule` | `'any'` | covered if any recommended agent covers |
| `use_intrinsic_resistance` | False | off; enabling needs clinical sign-off |

Answer space is the closed 17-drug formulary plus OTHER and ABSTAIN. A reply outside it is a
**parse failure against a closed answer space, not a wrong answer**, logged separately.

## 6. Leakage gate — three provenance classes

1. **Static scaffold** — personas, instructions, JSON schema, the 17-drug list. Drug names legal
   here and only here. Hash-pinned, asserted every run.
2. **Dynamic case block** — whitelisted pre-index columns, every datum asserted
   `timestamp < index_time`. Any violation aborts.
3. **Model spans** — hashed at the inference-call boundary. Exempt only on byte-match to a stored
   hash; everything else is presumed harness-assembled and fully gated. That closes the hole
   where a harness bug could smuggle panel content in under the label of a model turn.

Proven by fault injection: planting a real organism in the case block fires the gate; the same
content inside an *unregistered* "model turn" still aborts; a clean block stays silent.

The C2 reveal arm supplies the panel **by design** and carries
`gate_exemption="C2_reveal_declared"` on every record, so it can never be mistaken for a failure.

## 7. Windows and comparators

| item | value | justified by |
|---|---|---|
| clinician comparator window | `[index_time, index_time + 24h]`, inclusive at lower bound | D-CLINWIN-1 |
| first antibiotic order | median 4.74 h after draw, IQR 1.44–12.08 h, n=178 | `clinician_comparator_v2` |
| binding margin | 39 − 24 = 15 h | earliest possible S/I/R result 39 h |
| prior-antibiotic definition | started ≤ index−48h **and** still running at index | D-PRIORABX-1, Decision 10 |
| physician-order source | `prescriptions.csv.gz` | Zhikang named it (Z11); agent identity and `starttime` only, not dose or route |

All floor figures come from `floor_reconciled.csv` **with the frame named**. Enterobacterales
frame: meropenem 98.0% of cohort / 99.6% of tested; pip-tazo 91.3% / 95.0%; gentamicin
87.4% / 88.5%. Every earlier floor figure is superseded.

The mandated frequency floor (most-ordered agent = vancomycin) is **degenerate on this frame**:
tested denominator zero, because the laboratory builds the panel from the Gram stain and never
tests vancomycin against Enterobacterales. D-FLOOR-1 — the same mechanism as D-POP-1, reported
rather than worked around.

---

## 8. Open limitations, stated rather than found

1. **The debate arm confounds challenge with re-asking.** The system prompt differs between
   round-0 and the debate turns, so a position change may be a response to being asked
   differently. The Cn neutral-turn control (`control_pass.py`, `protocol_v1.md` line 78)
   separates them and has not yet reported. Until it does, the abandonment rate is not evidence
   of sycophancy.
2. **Guideline deviation (Zhikang's third indicator) is unmeasurable** until
   `guideline_flags.csv` is populated; the loader rejects blank citations by design.
3. **Labs omitted** from case presentations (D-LABS-1), contradicting D-VITALS-1's wording.
4. **The evidence-leak screen fires on 38 turns (4.8%)**; the reported rate must be the
   hand-classified one, not the automated screen.
5. **Hosted-model transfer deferred** (D-TRANSFER-1); can only run on synthetic non-MIMIC cases
   under the data use agreement.
6. **Indicator 2 reports 100% (235/235)**, which requires the negative control to show the
   measure discriminates rather than always firing.
