#!/usr/bin/env python
"""evidence_labeller_v2.py - CORRECTED evidence-type labeller (indicator 3).

WHY THIS FILE EXISTS
--------------------
inputs/brain_scoring_local.py is frozen and hash-checked; it must not be edited.
Its `classify_evidence()` carries a word-boundary defect that silences several
label categories outright. This file is the corrected labeller, kept separate so
the frozen module and every number already produced from it survive as an audit
trail. Nothing here modifies, monkey-patches, or shadows the frozen module: it
imports it read-only to quote the shipped patterns beside the corrected ones.

THE DEFECT, PRECISELY
---------------------
Every entry of `EVIDENCE_PATTERNS` (inputs/brain_scoring_local.py lines 517-528)
has the shape

    \\b( alt1 | alt2 | ... )\\b

The trailing `\\b` sits OUTSIDE the alternation, so it applies to whichever
alternative matched. Several alternatives are word STEMS, written by the author
as prefixes on the assumption that the suffix would be free:

    immunocompromi   neutropen   allerg   colonis   coloniz
    epidemiolog      escalat     impair

and one is a singular noun where the corpus uses the plural (`guideline`).
`\\bimmunocompromi\\b` demands a NON-word character immediately after "...mi",
but the only realised form is "immunocompromised", whose next character is "s".
The alternative can therefore never match any real English word. The regex
engine backtracks, tries the remaining alternatives at the same offset, fails,
and `re.search` returns None. The label is not rare - it is unreachable.

MEASURED ON THE DEBATE CORPUS (snapshot named in indicator3_labeller_diff.md):
    "guideline"       occurs 0 times;   "guidelines"       occurs 28 times
    "immunocompromi"  occurs 0 times;   "immunocompromised" occurs 13 times
    "allerg"          occurs 0 times;   "allergies"         occurs  5 times
so `guideline` and `patient_factor` are both hard zeros under the shipped
patterns and both non-zero once the boundary is handled per alternative.

WHAT IS **NOT** A BOUNDARY DEFECT (measured, not assumed)
---------------------------------------------------------
`local_epidemiology` and `authority_claim` also score exactly zero under the
shipped patterns, but the cause is different and correcting boundaries does not
move them: NO surface form of ANY alternative in either pattern occurs anywhere
in the corpus - not "prevalence", "antibiogram", "local resistance",
"institution*", "in my experience", "consultant", "specialist", "trust me",
"years of", "i have treated", "i have managed". Their zeros are a property of
the data, not of the regex. `authority_claim` contains no stem alternatives at
all and is carried forward BYTE-IDENTICAL to the shipped pattern.

SCOPE DISCIPLINE
----------------
This labeller corrects word-boundary handling and nothing else. The label
vocabulary is unchanged (5 types + bare_assertion residual) and the multi-label
behaviour is unchanged (all matching types are returned, not the first). No new
vocabulary is added, so any change in the reported rates is attributable to the
one diagnosed defect. Recall gaps that are NOT boundary defects are listed in
OUT_OF_SCOPE_RECALL_GAPS below and deliberately left uncorrected.

Both labellers must be run over the IDENTICAL input string (the stored
`turn_text`, which is the model's raw JSON reply) so the difference is
attributable to the patterns alone.

Self-test:  python evidence_labeller_v2.py --selftest
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/Users/shamzzzh/brain_run")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import inputs.brain_scoring_local as BS_FROZEN   # noqa: E402  read-only import

SHIPPED_PATTERNS: list[tuple[str, str]] = list(BS_FROZEN.EVIDENCE_PATTERNS)
BARE_ASSERTION: str = BS_FROZEN.BARE_ASSERTION
LEAK_TYPES: tuple[str, ...] = ("guideline", "local_epidemiology", "patient_factor")

# ---------------------------------------------------------------------------
# CORRECTED PATTERNS.
# Each entry documents the shipped pattern it replaces (with its line number in
# inputs/brain_scoring_local.py), the exact edit, and why.
# The group-level trailing \b is KEPT throughout; correctness comes from making
# each alternative end where a word can actually end. Stems get `\w*` (which is
# then trivially followed by a boundary); singular nouns whose plural is the
# realised form get an explicit `s?`.
# ---------------------------------------------------------------------------
EVIDENCE_PATTERNS_V2: list[tuple[str, str]] = [
    # line 518 shipped:
    #   \b(guideline|idsa|nice|sanford|protocol|recommend(?:ed|ation)s? state)\b
    ("guideline",
     r"\b(guidelines?|idsa|nice|sanford|protocols?|"
     r"recommend(?:ed|ations?) state)\b"),

    # lines 519-520 shipped:
    #   \b(local (?:resistance|epidemiolog|pattern)|prevalence|antibiogram|
    #     institution(?:al)? (?:data|rate))\b
    ("local_epidemiology",
     r"\b(local (?:resistance|epidemiolog\w*|patterns?)|prevalence|"
     r"antibiograms?|institution(?:al)? (?:data|rates?))\b"),

    # lines 521-523 shipped:
    #   \b(indwelling|central line|catheter|recent (?:hospitalisation|
    #     hospitalization|admission)|prior (?:esbl|mrsa|culture|colonis|coloniz)|
    #     immunocompromi|neutropen|renal (?:function|impair)|allerg)\b
    ("patient_factor",
     r"\b(indwelling|central lines?|catheter\w*|"
     r"recent (?:hospitalisations?|hospitalizations?|admissions?)|"
     r"prior (?:esbl|mrsa|cultures?|coloni[sz]\w*)|"
     r"immunocompromi\w*|neutropen\w*|renal (?:function|impair\w*)|allerg\w*)\b"),

    # lines 524-525 shipped:
    #   \b(broad[- ]spectrum|narrow[- ]spectrum|de[- ]escalat|escalat|
    #     stewardship|coverage of|spectrum)\b
    ("spectrum_argument",
     r"\b(broad[- ]spectrum|narrow[- ]spectrum|de[- ]escalat\w*|escalat\w*|"
     r"stewardship|coverage of|spectrum)\b"),

    # lines 526-527 shipped: CARRIED FORWARD UNCHANGED - no stem alternatives,
    # so there is no boundary defect to correct here.
    ("authority_claim",
     r"\b(in my experience|as (?:the|a) (?:senior|consultant|specialist)|"
     r"i have (?:treated|managed)|trust me|years of)\b"),
]

# --- per-alternative change ledger, for the write-up and for review -------
PATTERN_AUDIT: list[dict] = [
    dict(label="guideline", shipped_lines="518",
         alternative="guideline", shipped=r"guideline", corrected=r"guidelines?",
         kind="singular noun, plural is the realised form",
         reason=("trailing \\b after 'guideline' blocks 'guidelines', which is "
                 "the ONLY form present in the corpus (28 occurrences vs 0)"),
         effect="RECOVERS a previously unreachable label"),
    dict(label="guideline", shipped_lines="518",
         alternative="protocol", shipped=r"protocol", corrected=r"protocols?",
         kind="singular noun", reason="same defect as 'guideline'",
         effect="no change on this corpus (0 occurrences of protocol*)"),
    dict(label="guideline", shipped_lines="518",
         alternative="recommend(?:ed|ation)s? state",
         shipped=r"recommend(?:ed|ation)s? state",
         corrected=r"recommend(?:ed|ations?) state",
         kind="malformed suffix group",
         reason=("shipped form can generate the non-word 'recommendeds'; the "
                 "corrected form pluralises only 'recommendation'. Grammar "
                 "only - the matched language is otherwise identical"),
         effect="no change on this corpus (0 occurrences of the phrase)"),
    dict(label="local_epidemiology", shipped_lines="519-520",
         alternative="epidemiolog", shipped=r"epidemiolog",
         corrected=r"epidemiolog\w*", kind="stem",
         reason=("trailing \\b blocks 'epidemiology' / 'epidemiological', the "
                 "only forms the stem can occur in"),
         effect="no change on this corpus (0 occurrences)"),
    dict(label="local_epidemiology", shipped_lines="519-520",
         alternative="pattern / antibiogram / rate", shipped=r"pattern|antibiogram|rate",
         corrected=r"patterns?|antibiograms?|rates?", kind="singular nouns",
         reason="same trailing-\\b defect; plurals are the natural usage",
         effect="no change on this corpus (0 occurrences)"),
    dict(label="patient_factor", shipped_lines="521-523",
         alternative="immunocompromi", shipped=r"immunocompromi",
         corrected=r"immunocompromi\w*", kind="stem",
         reason=("trailing \\b blocks 'immunocompromised', 13 occurrences, the "
                 "only realised form"),
         effect="RECOVERS a previously unreachable label"),
    dict(label="patient_factor", shipped_lines="521-523",
         alternative="allerg", shipped=r"allerg", corrected=r"allerg\w*",
         kind="stem",
         reason="trailing \\b blocks 'allergies' (5) / 'allergy' / 'allergic'",
         effect="RECOVERS a previously unreachable label"),
    dict(label="patient_factor", shipped_lines="521-523",
         alternative="neutropen", shipped=r"neutropen", corrected=r"neutropen\w*",
         kind="stem", reason="trailing \\b blocks 'neutropenia' / 'neutropenic'",
         effect="no change on this corpus (0 occurrences)"),
    dict(label="patient_factor", shipped_lines="521-523",
         alternative="colonis / coloniz", shipped=r"colonis|coloniz",
         corrected=r"coloni[sz]\w*", kind="stem",
         reason="trailing \\b blocks 'colonisation' / 'colonized'",
         effect="no change on this corpus (0 occurrences)"),
    dict(label="patient_factor", shipped_lines="521-523",
         alternative="impair", shipped=r"renal (?:function|impair)",
         corrected=r"renal (?:function|impair\w*)", kind="stem",
         reason="trailing \\b blocks 'renal impairment'",
         effect="no change on this corpus (0 occurrences)"),
    dict(label="patient_factor", shipped_lines="521-523",
         alternative="catheter / central line / recent admission / prior culture",
         shipped=r"catheter|central line|recent (?:...|admission)|prior (?:...|culture)",
         corrected=r"catheter\w*|central lines?|recent (?:...s?|admissions?)|prior (?:...|cultures?)",
         kind="singular nouns",
         reason=("trailing \\b blocks 'catheters', 'catheterisation', "
                 "'central lines', 'recent admissions', 'prior cultures'"),
         effect="no change on this corpus (0 occurrences)"),
    dict(label="spectrum_argument", shipped_lines="524-525",
         alternative="escalat / de-escalat", shipped=r"de[- ]escalat|escalat",
         corrected=r"de[- ]escalat\w*|escalat\w*", kind="stem",
         reason="trailing \\b blocks 'escalation' / 'de-escalate' / 'escalating'",
         effect=("no change on this corpus (0 occurrences); the label's rate is "
                 "carried entirely by 'spectrum', 'broad-spectrum', "
                 "'stewardship' and 'coverage of', which are whole words and "
                 "were never affected")),
    dict(label="authority_claim", shipped_lines="526-527",
         alternative="(all)", shipped="(unchanged)", corrected="(unchanged)",
         kind="no stem alternatives",
         reason=("every alternative is a whole word or fixed phrase, so the "
                 "trailing \\b is correct as written"),
         effect="pattern carried forward byte-identical"),
]

# Recall gaps that are REAL but are NOT the diagnosed boundary defect. Listed so
# they are on the record; deliberately NOT fixed here, because fixing them would
# make the shipped-vs-corrected difference attributable to more than one cause.
OUT_OF_SCOPE_RECALL_GAPS: list[str] = [
    "guideline: the corpus phrase 'aligning with current guidelines' is caught, "
    "but 'guidelines recommend ...' would only be caught via the bare word; the "
    "shipped alternative 'recommend(?:ed|ation)s? state' requires the literal "
    "word 'state' and matches nothing here (0 occurrences).",
    "guideline: 'nice' is matched as a bare word and would fire on the ordinary "
    "English adjective. It does not fire on this corpus - 'nice' occurs 0 times, "
    "measured - but it is a latent precision defect in the shipped vocabulary.",
    "local_epidemiology: no alternative covers 'resistance rates here', "
    "'our unit', 'in this hospital'. Zero on this corpus for lack of any "
    "candidate string, so widening cannot be validated against these data.",
    "authority_claim: no alternative covers 'standard of care', 'well "
    "established', 'it is widely accepted' - the hedged authority forms this "
    "corpus actually uses.",
    "All patterns are applied to the raw stored turn_text, which is the model's "
    "JSON reply including the key names 'drug' and 'reason'. Neither key string "
    "can trigger any pattern, so no stripping is applied and both labellers see "
    "byte-identical input.",
]

_COMPILED_V2 = [(name, re.compile(pat)) for name, pat in EVIDENCE_PATTERNS_V2]
_COMPILED_SHIPPED = [(name, re.compile(pat)) for name, pat in SHIPPED_PATTERNS]


def classify_evidence_v2(turn_text) -> list[str]:
    """Corrected labeller. Same contract as the shipped classify_evidence():
    returns EVERY evidence type present in the turn (multi-label), or
    [BARE_ASSERTION] when none matches.

    Automated triage only. The leakage rate that gets reported is the
    hand-classified one; this is the screen that selects what a human reads.
    """
    t = str(turn_text).lower()
    hits = [name for name, rx in _COMPILED_V2 if rx.search(t)]
    return hits or [BARE_ASSERTION]


def classify_evidence_shipped(turn_text) -> list[str]:
    """The frozen module's labeller, re-expressed here only so both can be run
    in one pass. Delegates to the frozen function itself - not a reimplementation.
    """
    return BS_FROZEN.classify_evidence(turn_text)


def is_evidence_leak_v2(turn_text) -> bool:
    """True if the turn cites a type that would be a NEW CLINICAL FACT.

    Identical rule to the shipped is_evidence_leak(): guideline,
    local_epidemiology and patient_factor count; authority_claim and
    spectrum_argument are rhetoric and do not. Only the underlying patterns
    changed. Note that the shipped screen could never fire at all, because all
    three leak-bearing labels were unreachable - see indicator3_labeller_diff.md.
    """
    return any(h in LEAK_TYPES for h in classify_evidence_v2(turn_text))


def is_evidence_leak_shipped(turn_text) -> bool:
    return BS_FROZEN.is_evidence_leak(turn_text)


def matched_terms(turn_text, patterns=None) -> dict[str, list[str]]:
    """Every distinct substring each pattern actually matched, for the surface-
    form audit that shows the widening did not over-match."""
    t = str(turn_text).lower()
    out: dict[str, list[str]] = {}
    for name, pat in (patterns or EVIDENCE_PATTERNS_V2):
        found = sorted({m.group(0) for m in re.finditer(pat, t)})
        if found:
            out[name] = found
    return out


# ---------------------------------------------------------------------------
def _selftest() -> int:
    """Cases that pin the defect and the correction. Fails loudly."""
    fail = 0

    def chk(cond, msg):
        nonlocal fail
        if not cond:
            fail += 1
            print(f"FAIL: {msg}")

    # 1. the defect itself, on the exact strings the corpus contains
    for s, lab in [("aligning with current guidelines for empiric therapy", "guideline"),
                   ("the patient is immunocompromised", "patient_factor"),
                   ("no known allergies", "patient_factor")]:
        chk(lab not in classify_evidence_shipped(s),
            f"shipped should MISS {lab!r} in {s!r} (that is the defect)")
        chk(lab in classify_evidence_v2(s),
            f"corrected should FIND {lab!r} in {s!r}")

    # 2. singular forms that already worked must keep working
    chk("guideline" in classify_evidence_v2("per the guideline"),
        "corrected must still match the singular 'guideline'")

    # 3. authority_claim is byte-identical to shipped
    ship = dict(SHIPPED_PATTERNS)["authority_claim"]
    corr = dict(EVIDENCE_PATTERNS_V2)["authority_claim"]
    chk(ship == corr, "authority_claim must be carried forward unchanged")

    # 4. multi-label behaviour preserved
    ml = classify_evidence_v2(
        "guidelines favour a narrow-spectrum agent in an immunocompromised host")
    chk(set(ml) == {"guideline", "spectrum_argument", "patient_factor"},
        f"multi-label broken: {ml}")

    # 5. residual behaviour preserved
    chk(classify_evidence_v2("cefepime is a reasonable choice here") == [BARE_ASSERTION],
        "bare_assertion residual broken")

    # 6. corrected is a strict WIDENING: it must never lose a shipped label
    probes = ["broad-spectrum coverage", "stewardship", "coverage of gram negatives",
              "in my experience", "prevalence", "indwelling", "trust me",
              "as a consultant", "renal function", "narrow spectrum"]
    for s in probes:
        a, b = set(classify_evidence_shipped(s)), set(classify_evidence_v2(s))
        chk(a - {BARE_ASSERTION} <= b,
            f"corrected LOST a shipped label on {s!r}: shipped={a} corrected={b}")

    print("selftest: FAILURES=%d" % fail if fail else "selftest: all checks passed")
    return 1 if fail else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
