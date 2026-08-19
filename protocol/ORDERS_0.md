# ORDERS 0 — PROJECT INDEX + FIGURE SYSTEM

Saved verbatim 19 August 2026. Standing order. Re-read at the start of every phase.

---

PROMPT 0 — PROJECT INDEX + FIGURE SYSTEM. Two more prompts follow this one
("ORDERS 1" = the EOD track plan, "ORDERS 2" = the supervisor spec addendum).
Save each verbatim as protocol/ORDERS_1.md and protocol/ORDERS_2.md when
they arrive, and RE-READ BOTH at the start of every phase — they are
standing orders, not one-shot messages.

PART A — MAKE THE PROJECT ACCESSIBLE TO ME (do this first, ~20 min):
Write PROJECT_INDEX.md at the repo root: every artefact in this project —
data files, scripts, protocol docs, deviation log, registries, run outputs,
figures — one line each: path, what it is, status (final/draft/running),
and which claim or slide it supports. Group by: DATA / METHOD / RESULTS /
GOVERNANCE / FIGURES / ORDERS. This is the single door into the project;
keep it current for the rest of the day. Also generate index.html — a plain
self-contained page rendering the same index with links, so I can browse it
in a browser.

PART B — FIGURE SYSTEM (runs parallel to the model tracks; plotting is
CPU-light, never blocks a run):
Style contract, fixed for every figure:
- Palette: ink #12303F, primary #1C7293, accent #C64B3E, muted #6B7C85,
  background #F4F7F8/white. Matches the deck.
- Kicker line in accent caps + short declarative title stating the CLAIM,
  not the topic ("The lab tests what the Gram stain suggests", not "Panel
  coverage analysis").
- Direct labels on marks; legends only when unavoidable. No chartjunk, no
  3D, no default matplotlib look: custom rcParams, light y-grid only,
  generous whitespace, annotation layer for the one number that matters.
- Every figure exports PNG at 200dpi AND SVG, sized for a 16:9 slide half
  (~9x5in) or full (~12x6in).
- REPRODUCIBILITY RULE: each figure has a script figures/src/fXX_name.py
  that reads ONLY from result files on disk. No hand-entered numbers, no
  mock data in any non-watermarked asset. A figure that cannot regenerate
  from disk does not ship.
- FIGURES_MANIFEST.md: one row per figure — id, claim it supports, source
  data path, script path, status.
- Aggregates only. No patient-level values anywhere.

The figure set (build in this order; F5 is the headline):
F1 Cohort flow — restyle the CONSORT waterfall to the style contract.
F2 The ground-truth structure finding — panel testing coverage by Gram
   stain (the 6/6,391 vs 4,549/4,840 pip-tazo fact): dumbbell or matrix,
   claim: the laboratory's own triage shapes what can be scored.
F3 Frequency floor, BOTH denominators, UNDETERMINED shown — slope or
   paired-dot chart making the denominator dependence visible.
F4 Fixed-policy replication — round-0 drug distribution as small multiples
   per model (Qwen3-4B now; MedGemma-4B / Gemma3-4B / Gemma3-12B panels
   fill as Track 3 lands): one dominant bar per panel IS the claim.
F5 TINGTING'S CORE FIGURE, exactly her spec: final antibiotic
   appropriateness stratified by agent x interaction condition x
   counterpart correctness, with correct->incorrect and incorrect->correct
   transition rates underneath. This is the results slide. Draft with
   Track 1 data the moment it exists; refresh when Track 4 adds the seeded
   conditions.
F6 The two-pattern collapse — all ordering-runs drawn as turn-by-turn
   position paths, visually collapsing to the two trajectories (with the
   lone exception visible): the most striking image in the set.
F7 The speaking-order effect — same case, two orders, different final
   drug, with the headline % annotated.
F8 The 2x2 as a transition matrix, HRR and BCR annotated on the arrows,
   stance-change rate alongside (the spectrum-luck dissociation in one
   image).

Watermark any figure containing non-final numbers with DRAFT until its
track completes. Deliver everything into figures/ and keep index.html
current. The deck itself is assembled elsewhere — your deliverable is
figures + index, not slides.

Also write RESURRECT.md at the repo root: the exact read-order a fresh
session needs to rebuild full context if this session is lost or compacts
badly (PROJECT_INDEX.md -> ORDERS_1 -> ORDERS_2 -> tingting_endpoint_spec
-> deviation_log -> protocol_v1 -> latest results). Keep it current. And
treat VERIFY_FINDINGS.md, when it appears, as proposals only: nothing in it
changes code or artefacts without my explicit approval per finding.
