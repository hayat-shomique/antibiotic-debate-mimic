"""provenance.py - the three-class leakage gate.

Class 1  STATIC SCAFFOLD  personas, instructions, JSON schema, the 17-drug
                          formulary list. Drug names are legal HERE AND ONLY
                          HERE. Verified clean once, hashed, hash asserted on
                          every run.
Class 2  DYNAMIC CASE BLOCK  built by case_assembly.py from whitelisted
                          pre-index columns. Full gate. Any violation ABORTS.
Class 3  MODEL SPANS      verified, not trusted. Every model output is hashed
                          at the inference-call boundary. At prompt assembly a
                          span is treated as model-generated only if it byte-
                          matches a stored hash; EVERYTHING ELSE is presumed
                          harness-assembled and gets the full gate. That is
                          what closes the hole where a harness bug smuggles
                          panel content in under the label of a "model turn".

On verified model spans we never abort for an organism name or the word
'susceptible' - a clinician persona may say either. Instead we measure them,
and escalate only on the canary conditions.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

SENTINEL = "\x00\x00SPAN\x00\x00"

PHRASE_SUBSTR = ["suscept", "sensitiv", "resistan", "culture result", "s/i/r"]
PHRASE_WORD = [r"\bmic\b", r"\bmics\b"]
INTERP_TERMS = ["susceptible", "resistant", "intermediate", "s/i/r"]
# Raw MIMIC codes too: a model may write "E. coli was R to meropenem".
INTERP_CODES = [r"\bS\b", r"\bI\b", r"\bR\b"]

CANARY_WINDOW = 120       # chars; panel-drug + interp term co-occurring within
AUTO_ABORT_ROWS = 2       # >= this many distinct panel rows matched -> abort


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# vocabulary
# ---------------------------------------------------------------------------
def spellings(name: str) -> set[str]:
    b = re.sub(r"\s+", " ", str(name).strip().lower())
    if not b:
        return set()
    return {b, b.replace("-", "/"), b.replace("/", "-"), b.replace("-", " "),
            b.replace("/", " "), b.replace(" ", "-"), b.replace(" ", "/")}


def drug_terms(formulary: dict[str, set[str]]) -> list[str]:
    """Every canonical name, every alias, hyphen AND slash AND space spellings,
    plus every component token >= 5 chars.

    The shipped gate tested only canon.split('-')[0], so 'ampicillin-sulbactam'
    guarded 'ampicillin' and let 'sulbactam' straight through. Components are
    included here precisely to close that.
    """
    terms: set[str] = set()
    for canon, aliases in formulary.items():
        for n in {canon, *aliases}:
            terms |= spellings(n)
    comps = {p for t in list(terms) for p in re.split(r"[-/ ]+", t) if len(p) >= 5}
    return sorted(terms | comps, key=len, reverse=True)


def organism_terms(org_names) -> list[str]:
    out: set[str] = set()
    for org in org_names:
        if org is None:
            continue
        low = re.sub(r"\s+", " ", str(org).strip().lower())
        if not low or low == "nan":
            continue
        out.add(low)
        out |= {t for t in re.split(r"[^a-z]+", low) if len(t) >= 4}
    return sorted(out, key=len, reverse=True)


# ---------------------------------------------------------------------------
# class 1 - static scaffold
# ---------------------------------------------------------------------------
@dataclass
class StaticScaffold:
    """Hash-pinned prompt furniture. Drug names legal here only."""
    texts: dict[str, str]
    pinned: dict[str, str] = field(default_factory=dict)

    def freeze(self) -> dict[str, str]:
        self.pinned = {k: sha(v) for k, v in self.texts.items()}
        return dict(self.pinned)

    def assert_unchanged(self) -> None:
        for k, v in self.texts.items():
            if self.pinned.get(k) != sha(v):
                raise RuntimeError(f"STATIC SCAFFOLD '{k}' changed since freeze")

    def verify_no_case_data(self, org_names, forbidden_case_strings) -> list[str]:
        """Run ONCE. The scaffold may name drugs; it may not name a patient's
        organisms or carry any case-specific string."""
        bad = []
        for k, v in self.texts.items():
            low = v.lower()
            for t in organism_terms(org_names):
                if t in low:
                    bad.append(f"scaffold '{k}' contains organism term '{t}'")
            for s in forbidden_case_strings:
                if s and str(s).lower() in low:
                    bad.append(f"scaffold '{k}' contains case string '{s}'")
        return sorted(set(bad))

    def all_texts(self) -> list[str]:
        return list(self.texts.values())


# ---------------------------------------------------------------------------
# class 3 - model span registry
# ---------------------------------------------------------------------------
class SpanRegistry:
    """Hashes every model output at the inference-call boundary."""

    def __init__(self) -> None:
        self._by_hash: dict[str, str] = {}

    def register(self, text: str) -> str:
        h = sha(text)
        self._by_hash[h] = text
        return h

    def known(self) -> list[str]:
        # longest first so a short span cannot shadow a longer containing one
        return sorted(self._by_hash.values(), key=len, reverse=True)

    def carve(self, prompt: str, also_exempt: list[str]) -> tuple[str, list[str]]:
        """Remove verified model spans and verified scaffold text.

        Returns (residue, found_model_spans). The residue is by definition
        harness-assembled and gets the full gate.
        """
        residue = prompt
        found: list[str] = []
        for span in self.known():
            if span and span in residue:
                residue = residue.replace(span, SENTINEL)
                found.append(span)
        for s in sorted(also_exempt, key=len, reverse=True):
            if s and s in residue:
                residue = residue.replace(s, SENTINEL)
        return residue, found


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
def gate_full(text: str, drugs: list[str], orgs: list[str]) -> list[str]:
    """Class-2 gate. Any hit aborts."""
    low = text.lower()
    bad = []
    for t in drugs:
        if t in low:
            bad.append(f"drug term '{t}'")
    for t in organism_terms(orgs):
        if t in low:
            bad.append(f"organism term '{t}'")
    for p in PHRASE_SUBSTR:
        if p in low:
            bad.append(f"phrase '{p}'")
    for p in PHRASE_WORD:
        if re.search(p, low):
            bad.append(f"phrase {p}")
    return sorted(set(bad))


@dataclass
class SpanAudit:
    organism_mentions: list[str]
    matches_panel: bool
    canary_hits: list[str]
    panel_row_matches: int
    quarantine: bool
    abort: bool


def audit_model_span(span: str, panel_rows, canon_drug) -> SpanAudit:
    """Measure, do not abort - except on the canary conditions.

    panel_rows: iterable of (org_name, ab_name, interpretation) for THIS case.
    """
    low = span.lower()
    orgs = {str(r[0]) for r in panel_rows if r[0] is not None}
    mentions = [t for t in organism_terms(orgs) if t in low]

    canary: list[str] = []
    rows_matched = 0
    for org, ab, interp in panel_rows:
        c = canon_drug(ab) if ab is not None else None
        if not c:
            continue
        drug_pos = [m.start() for m in re.finditer(re.escape(c.split("-")[0]), low)]
        if not drug_pos:
            continue
        for term in INTERP_TERMS:
            for m in re.finditer(re.escape(term), low):
                if any(abs(m.start() - p) <= CANARY_WINDOW for p in drug_pos):
                    canary.append(f"'{c}' within {CANARY_WINDOW} chars of '{term}'")
        for pat in INTERP_CODES:
            for m in re.finditer(pat, span):          # case-SENSITIVE: S/I/R codes
                if any(abs(m.start() - q) <= CANARY_WINDOW for q in drug_pos):
                    canary.append(f"'{c}' within {CANARY_WINDOW} chars of code "
                                  f"'{m.group(0)}'")
        otoks = [t for t in organism_terms([org]) if t in low]
        if otoks and drug_pos:
            rows_matched += 1

    return SpanAudit(
        organism_mentions=sorted(set(mentions)),
        matches_panel=bool(mentions),
        canary_hits=sorted(set(canary)),
        panel_row_matches=rows_matched,
        quarantine=bool(canary),
        abort=rows_matched >= AUTO_ABORT_ROWS,
    )


def gate_assembled_prompt(prompt: str, registry: SpanRegistry,
                          scaffold: StaticScaffold, drugs: list[str],
                          orgs: list[str], panel_rows, canon_drug) -> dict:
    """The whole thing, at every assembly point.

    1. carve out verified model spans and verified scaffold
    2. full gate on the residue  -> abort on any hit
    3. audit each model span     -> measure, quarantine, or abort on canary
    """
    scaffold.assert_unchanged()
    residue, spans = registry.carve(prompt, scaffold.all_texts())
    residue_violations = gate_full(residue.replace(SENTINEL, " "), drugs, orgs)
    audits = [audit_model_span(s, panel_rows, canon_drug) for s in spans]
    return {
        "residue_violations": residue_violations,
        "abort": bool(residue_violations) or any(a.abort for a in audits),
        "quarantine": any(a.quarantine for a in audits),
        "span_audits": audits,
        "n_model_spans": len(spans),
        "residue_chars": len(residue.replace(SENTINEL, "")),
    }


# ---------------------------------------------------------------------------
# Canonical pre-reveal gate for the C2 arms.
#
# A C2 prompt is a concatenation of three provenance classes:
#   static scaffold  - hash-pinned; drug names are legal in it
#   dynamic case data - the case block; FULL gate, abort on any organism or
#                       susceptibility phrasing, because that would be leakage
#   model spans       - the agents' own turns; hashed at the inference boundary
#                       and MEASURED. The model writing "the culture result may
#                       show resistance" is the model reasoning aloud. It is not
#                       case data leaking in, and it must never abort the run.
#
# Before this function existed, reveal_pass.py and clean_c2_pass.py ran
# gate_full() over case_block + transcript together. That aborted 177 of 384
# reveal ordering-runs and 43 of 200 clean-context cases on the model's own
# vocabulary ('resistan', 'culture result', 'suscept'), and the dropout was not
# random: it removed precisely the runs where the model was already reasoning
# about microbiology. See deviation D-GATE-2.
# ---------------------------------------------------------------------------
def gate_pre_reveal(case_block: str, model_spans, drugs: list[str], orgs,
                    panel_rows, canon_drug) -> dict:
    """Returns {'ok': bool, 'reason': str, 'audit': dict}.

    ok=False only when the CASE BLOCK leaks, or when a model span reconstructs
    enough panel rows to trip the canary auto-abort. Model vocabulary alone
    never fails the gate.
    """
    viol = [v for v in gate_full(case_block, drugs, orgs)
            if not v.startswith("drug term")]
    # gate_full does not test the bare interpretation CODES (S / I / R), and the
    # caller drops drug-term hits because a drug name is legal in a recommendation.
    # Between those two facts a case block reading "MEROPENEM S" would pass. It
    # cannot arise from case_assembly (whitelisted pre-index columns, no path to
    # panel data) but the gate should not depend on that. Abort when an
    # interpretation code sits within the canary window of a drug name.
    low_cb = case_block.lower()
    dpos = [m.start() for t in drugs for m in re.finditer(re.escape(t), low_cb)]
    if dpos:
        for pat in INTERP_CODES:
            for m in re.finditer(pat, case_block):        # case-SENSITIVE
                if any(abs(m.start() - q) <= CANARY_WINDOW for q in dpos):
                    viol.append(f"interpretation code '{m.group(0)}' within "
                                f"{CANARY_WINDOW} chars of a drug name in the case block")
    if viol:
        return {"ok": False, "reason": f"case-block leakage {sorted(set(viol))}", "audit": {}}

    mentions, canary, rowmatch, quarantine = set(), set(), 0, False
    for span in model_spans:
        au = audit_model_span(span, panel_rows, canon_drug)
        mentions |= set(au.organism_mentions)
        canary |= set(au.canary_hits)
        rowmatch = max(rowmatch, au.panel_row_matches)
        quarantine = quarantine or au.quarantine
        if au.abort:
            return {"ok": False,
                    "reason": f"model span reconstructed {au.panel_row_matches} panel rows",
                    "audit": {}}
    return {"ok": True, "reason": "", "audit": {
        "span_organism_mentions": sorted(mentions),
        "span_canary_hits": sorted(canary),
        "span_panel_row_matches": rowmatch,
        "span_quarantine": bool(quarantine),
    }}
