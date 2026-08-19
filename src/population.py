"""population.py - primary sampling frame definition (D-POP-1).

Enterobacterales membership by genus. Genus list follows current taxonomy
(order Enterobacterales); matching is on the leading genus token so that
'ENTEROBACTER CLOACAE COMPLEX' matches and 'ENTEROCOCCUS FAECIUM' does not.
Enterococcus is Gram-positive and is NOT Enterobacterales; the two genera share
a five-letter prefix, so the guard below is load-bearing.
"""
from __future__ import annotations

import re

ENTEROBACTERALES_GENERA = {
    "ESCHERICHIA", "KLEBSIELLA", "ENTEROBACTER", "SERRATIA", "PROTEUS",
    "CITROBACTER", "MORGANELLA", "PROVIDENCIA", "SALMONELLA", "SHIGELLA",
    "HAFNIA", "PANTOEA", "RAOULTELLA", "YERSINIA", "EDWARDSIELLA",
    "CRONOBACTER", "KLUYVERA", "LECLERCIA", "EWINGELLA", "CEDECEA",
    "RAHNELLA", "BUTTIAUXELLA", "PLESIOMONAS", "TRABULSIELLA", "OBESUMBACTERIUM",
}

# Explicitly NOT Enterobacterales, listed so the exclusion is auditable.
NOT_ENTEROBACTERALES = {
    "ENTEROCOCCUS",        # Gram-positive coccus
    "PSEUDOMONAS", "ACINETOBACTER", "STENOTROPHOMONAS", "BURKHOLDERIA",
    "HAEMOPHILUS", "NEISSERIA", "MORAXELLA", "AEROMONAS", "VIBRIO",
    "CAMPYLOBACTER", "BACTEROIDES", "FUSOBACTERIUM",
}


def _genus(org_name: str) -> str:
    tok = re.split(r"[^A-Za-z]+", str(org_name).strip().upper())
    return tok[0] if tok and tok[0] else ""


def is_enterobacterales(org_name: str) -> bool:
    g = _genus(org_name)
    if g in NOT_ENTEROBACTERALES:
        return False
    return g in ENTEROBACTERALES_GENERA


def case_is_enterobacterales(org_names) -> bool:
    """A case qualifies when EVERY pathogenic isolate is Enterobacterales.

    'Every' rather than 'any': the scoring config requires all pathogens covered,
    so a mixed Gram-positive/Enterobacterales case inherits the Gram-positive
    panel-coverage problem the frame exists to avoid.
    """
    names = [o for o in org_names if o is not None]
    return bool(names) and all(is_enterobacterales(o) for o in names)


# ---------------------------------------------------------------------------
# Gram class. D-POP-1's mechanism is Gram-negative-vs-positive panel coverage,
# not Enterobacterales-vs-other: the laboratory builds the panel from the Gram
# stain, so no Gram-positive isolate is ever tested against pip-tazo.
# ---------------------------------------------------------------------------
GRAM_POSITIVE_GENERA = {
    "STAPHYLOCOCCUS", "STAPH", "STREPTOCOCCUS", "ENTEROCOCCUS", "LISTERIA",
    "LACTOBACILLUS", "CORYNEBACTERIUM", "BACILLUS", "CLOSTRIDIUM",
    "PROPIONIBACTERIUM", "CUTIBACTERIUM", "MICROCOCCUS", "ABIOTROPHIA",
    "GRANULICATELLA", "GEMELLA", "AEROCOCCUS", "LEUCONOSTOC", "ROTHIA",
    "ACTINOMYCES", "PEPTOSTREPTOCOCCUS", "PEDIOCOCCUS", "VIRIDANS", "BETA",
    "ALPHA", "DIPHTHEROIDS", "LACTOCOCCUS", "STOMATOCOCCUS", "KOCURIA",
}


def gram_class(org_name: str) -> str:
    g = _genus(org_name)
    up = str(org_name).upper()
    if g in GRAM_POSITIVE_GENERA or up.startswith(("STAPH", "STREP", "VIRIDANS",
                                                   "BETA STREP", "ALPHA")):
        return "positive"
    if g in ENTEROBACTERALES_GENERA or g in NOT_ENTEROBACTERALES:
        return "negative"
    return "other"


def case_gram(org_names) -> str:
    cs = {gram_class(o) for o in org_names if o is not None}
    if cs == {"positive"}:
        return "positive"
    if cs == {"negative"}:
        return "negative"
    return "mixed/other"
