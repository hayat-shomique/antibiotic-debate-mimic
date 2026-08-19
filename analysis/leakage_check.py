#!/usr/bin/env python3
"""Protocol section 6, challenger constraint: report the evidence leakage rate.

    "The challenger is blinded to the panel and constrained in-prompt from
     introducing new clinical facts. Blinding controls what it knows, not what it
     says. A sample of challenger turns is hand-classified for evidence leakage
     and the leakage rate is reported as a validity check. Evidence-free is a
     measured property, not an assumed one."

The protocol anticipated hand-classifying a sample. That is unnecessary here and a
weaker check than the design allows, because the challenger is not a model. It
emits one of a small closed set of fixed sentences, so the whole population can be
inspected rather than a sample of it, and the leakage rate is exact rather than
estimated.

What counts as leakage: any organism name, any antibiotic name, any susceptibility
term, or any patient-specific clinical assertion. A challenge may express doubt,
authority or urgency; it may not carry information.
"""
import json, glob, os, re
from collections import Counter

BRAIN = os.environ.get("BRAIN_RUNS") or os.path.expanduser("~/brain_run/runs")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ORGANISMS = ["escherichia", "coli", "klebsiella", "pseudomonas", "enterobacter", "proteus",
             "serratia", "staphylococcus", "streptococcus", "enterococcus", "candida",
             "acinetobacter", "citrobacter", "morganella", "bacteroides"]
DRUGS = ["ampicillin", "amoxicillin", "cefazolin", "ceftriaxone", "cefepime", "ceftazidime",
         "meropenem", "imipenem", "ertapenem", "piperacillin", "tazobactam", "vancomycin",
         "gentamicin", "ciprofloxacin", "levofloxacin", "trimethoprim", "sulfamethoxazole",
         "nitrofurantoin", "linezolid", "daptomycin", "colistin", "tigecycline"]
SUSCEPT = ["susceptible", "resistant", "intermediate", "sensitivity", "susceptibility",
           "culture", "gram stain", "gram-negative", "gram-positive", "mic ", "panel",
           "isolate", "organism", "pathogen", "blood culture"]
CLINICAL = ["creatinine", "lactate", "wbc", "white cell", "temperature", "febrile",
            "hypotensive", "renal", "allergy", "allergic"]


def classify(text):
    low = text.lower()
    hits = {"organism": [o for o in ORGANISMS if o in low],
            "drug": [d for d in DRUGS if d in low],
            "susceptibility": [s for s in SUSCEPT if s in low],
            "clinical fact": [c for c in CLINICAL if c in low]}
    return {k: v for k, v in hits.items() if v}


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(BRAIN, "c1_*.jsonl"))):
        for line in open(f):
            line = line.strip()
            if line:
                r = json.loads(line)
                if r.get("condition") == "C1_unsupported_pressure" and r.get("challenge_text"):
                    rows.append(r)
    if not rows:
        print("no challenger turns found")
        return

    pop = Counter(r["challenge_text"] for r in rows)
    print("Protocol section 6, challenger evidence leakage\n")
    print("  %d challenger turns delivered, drawn from %d distinct sentences." % (len(rows), len(pop)))
    print("  The set is closed, so every sentence is inspected. This is a census, not a sample.\n")
    leaked = 0
    detail = {}
    for text, n in pop.most_common():
        hits = classify(text)
        detail[text] = {"turns": n, "leak": bool(hits), "hits": hits}
        if hits:
            leaked += n
        print("  %-6s %3d turns  %s" % ("LEAK" if hits else "clean", n, text))
        if hits:
            print("           flagged: %s" % hits)

    print("\n  leakage rate = %d/%d = %.1f%% of challenger turns" % (leaked, len(rows), 100 * leaked / len(rows)))
    print("  distinct sentences carrying evidence = %d/%d"
          % (sum(1 for v in detail.values() if v["leak"]), len(pop)))

    # the gate is an independent check on the same claim
    q = Counter(str(r.get("gate_quarantine")) for r in rows)
    print("\n  independent check, provenance gate over the same runs:")
    print("    quarantined turns: %s" % dict(q))

    out = {"n_turns": len(rows), "n_distinct_sentences": len(pop),
           "leaked_turns": leaked,
           "leakage_rate_pct": round(100 * leaked / len(rows), 2),
           "method": "census of the closed sentence set, not a sample",
           "gate_quarantine": dict(q),
           "sentences": detail}
    json.dump(out, open(os.path.join(ROOT, "results", "leakage.json"), "w"), indent=2)
    print("\n  written: results/leakage.json")

    print("\n  NOTE ON SCOPE. This covers the scripted-pressure arm only. In the debate arm the")
    print("  counterpart is a live model, so its turns are not a closed set and this census does")
    print("  not apply to them. Agent B is blinded to the panel by construction, but its turns")
    print("  carry no recorded provenance spans, so the leakage rate there is UNMEASURED and is")
    print("  declared as such rather than assumed to be zero.")


if __name__ == "__main__":
    main()
