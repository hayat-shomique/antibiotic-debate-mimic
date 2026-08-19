"""Fault injection for the corrected pre-reveal gate (D-GATE-2).

The fix must do two things at once:
  (a) still ABORT when real case data or a reconstructed panel appears, and
  (b) stop aborting on the model's own vocabulary.
A fix that only did (b) would be a weakened gate, not a corrected one.
"""
import debate_run as DR, provenance as PV

DRUGS, ORGS = DR.DRUG_TERMS, ["ESCHERICHIA COLI"]
ROWS = [("ESCHERICHIA COLI", "MEROPENEM", "S"),
        ("ESCHERICHIA COLI", "CEFAZOLIN", "R")]
CANON = DR.BS.canon_drug
CLEAN_BLOCK = ("Age 64. Male. Admitted from home. Temperature 38.4 C, heart rate 112, "
               "white cell count 16.2. No antimicrobial therapy in the preceding 48 hours.\n")

def g(block, spans):
    return PV.gate_pre_reveal(block, spans, DRUGS, ORGS, ROWS, CANON)

CASES = [
    # ---- MUST ABORT: real leakage in the dynamic case-data class ----
    ("case block names the organism", CLEAN_BLOCK + "Blood culture grew Escherichia coli.", [], False),
    ("case block carries an interpretation", CLEAN_BLOCK + "Isolate susceptible to meropenem.", [], False),
    ("case block says resistant", CLEAN_BLOCK + "Organism resistant to cefazolin.", [], False),
    ("case block leaks an S/I/R code", CLEAN_BLOCK + "MEROPENEM S", [], False),

    # ---- MUST PASS: model vocabulary, the false positives that caused the dropout ----
    ("model says 'culture results'", CLEAN_BLOCK,
     ['I will narrow once culture results are available.'], True),
    ("model says 'resistance'", CLEAN_BLOCK,
     ['Local resistance patterns favour piperacillin-tazobactam.'], True),
    ("model says 'susceptibility'", CLEAN_BLOCK,
     ['Await susceptibility data before de-escalating.'], True),
    ("model names a drug", CLEAN_BLOCK,
     ['{"drug": "meropenem", "reason": "broad empiric cover"}'], True),
    ("both agents use the vocabulary", CLEAN_BLOCK,
     ['Pending culture results.', 'Resistance risk is low; I would use cefepime.'], True),

    # ---- MUST ABORT: model span reconstructing the panel (the real canary) ----
    ("model reconstructs a panel row", CLEAN_BLOCK,
     ['Escherichia coli is susceptible to meropenem and resistant to cefazolin.'], False),
]

fails = 0
for name, block, spans, want_ok in CASES:
    got = g(block, spans)["ok"]
    ok = (got == want_ok)
    fails += not ok
    print(f"  {'PASS' if ok else 'FAIL'}  want_ok={str(want_ok):5s} got={str(got):5s}  {name}")
    if not ok:
        print(f"        reason: {g(block, spans)['reason']}")

print(f"\n  {len(CASES)-fails}/{len(CASES)} fault-injection checks passed")
raise SystemExit(1 if fails else 0)
