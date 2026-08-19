# ORDERS 1, EOD PLAN, Wednesday 19 August 2026

Saved verbatim. Standing order. Re-read at the start of every phase.

---

EOD PLAN, Wednesday 19 Aug. Slides freeze tonight; conference tomorrow.
Priority is Tingting's framework computed on real data, then models, then
anything else. Kill rules at the bottom are binding.

TRACK 1, HER ANALYSIS ON EXISTING DATA (start now, no model calls):
Compute from the debate logs, both agents, both orderings:
  a. HRR = N(correct before -> incorrect after)/N(correct before)
     BCR = N(incorrect before -> correct after)/N(incorrect before)
  b. Delta-Q per interaction, compared Doctor->Pharmacist vs
     Pharmacist->Doctor (the both-orderings design exists for this).
  c. Her core figure: final appropriateness stratified by agent x
     interaction condition x counterpart correctness, transition rates
     underneath. This is the results slide; produce it as a figure file.
  d. Report HRR NEXT TO stance-change rate: interim HRR ~0 with 100%
     position abandonment is the spectrum-luck dissociation, that pairing
     is the finding.

TRACK 2, CURRENT QUEUE TO COMPLETION: finish debate to 200, then Cn, then
C2 panel-reveal, as already queued. Spectrum taxonomy (Yuan
under/optimal/over) proceeds, it makes the clinician comparison
commensurable with the group's own paper.

TRACK 3, MODEL 2x2, round-0 ONLY, strictly sequential (never two models
resident with the 12B):
  a. Verify the MedGemma-4B Ollama tag actually pulls; record digest. If no
     working tag, HF GGUF fallback; if neither, report and skip, no
     improvisation.
  b. MedGemma-4B round-0 on the same 200 (domain test vs Gemma3-4B).
  c. Gemma3-4B round-0 (the base-family control).
  d. Gemma3-12B round-0 if time (scale test).
  The question each answers: does the fixed no-patient-conditioning policy
  replicate? That's the slide: case-conditioning across domain and scale.
  e. ONE cross-model debate config on a 60-case subset only if Tracks 1-2
     are done: Qwen3-4B doctor vs MedGemma-4B pharmacist, the genuine
     two-model communication Zhikang originally described.

CUTS, said now: confidence elicitation = next-steps slide (post-freeze arm,
her wording quoted); C1 scripted pressure = smoke-test only, runs only if
everything above lands; label-space sensitivity finishes but is backup
material. S.C.O.R.E.: paste the verified corpus entry before building
anything against it, else drop.

## ORDERS_1 PATCH (append)

P1. C2 STRATIFICATION, mandatory before any headline: split C2 responses by
    round-0 status. Report: moved | round-0 inadequate (appropriate
    escalation rate); and for round-0 adequate: held / narrowed-still-active
    / broke-to-inadequate. The inversion claim is worded from THESE numbers,
    not raw movement.
P2. Reconcile the C2 denominator (207 vs 200 cases vs 400 orderings) and
    state it in one line in the numbers block.
P3. Investigate the 1/200 Cn determinism mismatch; resolve or footnote
    before Cn ships.
P4. Include the instruction-ablation adoption numbers (with vs without the
    clause) in the numbers block, "dispositional" is claimable only with
    them shown.
P5. F8's HRR/BCR definitions are CONFIRMED as implemented.
