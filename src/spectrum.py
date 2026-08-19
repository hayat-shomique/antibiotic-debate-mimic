#!/usr/bin/env python
"""spectrum.py - three-way spectrum taxonomy (Yuan et al.) over the 17-drug formulary.

Coverage scoring answers one question: was the recommended agent active against
every pathogenic isolate. It cannot separate an agent that was active and no
broader than it needed to be from an agent that was active because it covers
almost everything. Yuan et al. split active treatment into optimal and excessive,
and the group's own prior work reports that three-way split, so a comparison that
reports coverage alone is not commensurable with it.

Labels returned:
  UNDER_TREATED       the agent (or regimen) is not active against the isolates
  OPTIMALLY_TREATED   active, and no narrower agent in the formulary was shown
                      active on this case's panel
  OVER_TREATED        active, but a strictly narrower agent was shown active
  UNDETERMINED        the panel cannot decide it (agent untested on >=1 isolate,
                      best verdict Intermediate, or no parsable formulary agent)

Design rules, so the label can be audited rather than trusted:

1. Activity is NOT re-derived here. It is taken from brain_scoring_local.score_case
   with the frozen ScoringConfig (intermediate_as='separate',
   require_all_pathogens_covered=True, combination_rule='any', fingerprint
   04ce311c2b13). The spectrum label is a refinement of the coverage outcome and
   never contradicts it:
       ADEQUATE          -> OPTIMALLY_TREATED or OVER_TREATED
       INADEQUATE        -> UNDER_TREATED
       INTERMEDIATE_ONLY -> UNDETERMINED
       UNDETERMINED      -> UNDETERMINED

2. "Narrowest active agent" is resolved against SPECTRUM_RANK, an explicit
   ordinal ranking of the 17 formulary agents written out in spectrum_ranking.md.
   The ranking is a project decision awaiting clinical sign-off, not established
   fact. Equal ranks mean the two agents were judged comparable in breadth, not
   that an ordering was unavailable.

3. The reference set is the set of formulary agents that the laboratory actually
   tested on every pathogenic isolate of this case AND that scored ADEQUATE.
   An agent that was never tested cannot enter the reference set, so the
   reference rank is an upper bound on the true narrowest active agent and the
   OPTIMALLY_TREATED count is an upper bound. See spectrum_ranking.md.

4. A multi-agent regimen (the clinician arm) takes its activity from the frozen
   any-covers rule. Its breadth is the pair (rank of its broadest component,
   number of ranked agents in it), compared lexicographically. A combination is
   at least as broad as its widest agent, and strictly broader than that agent
   alone, because the extra agent extends the spectrum by whatever it adds.
   Vancomycin plus ceftriaxone is therefore broader than ceftriaxone alone even
   though vancomycin sits lower on the ranking. A regimen is over-treatment when
   some strictly narrower alternative was shown active, where the alternatives
   considered are every single formulary agent and every proper subset of the
   regimen itself.

Not modified by this module: brain_scoring_local.py, debate_run.py, or any
frozen artefact. This file only reads.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"


def _load_scoring():
    """Load the frozen scorer from inputs/ the same way debate_run.py does."""
    spec = importlib.util.spec_from_file_location(
        "brain_scoring_spectrum", INPUTS / "brain_scoring_local.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["brain_scoring_spectrum"] = mod
    spec.loader.exec_module(mod)
    return mod


BS = _load_scoring()

UNDER_TREATED = "UNDER_TREATED"
OPTIMALLY_TREATED = "OPTIMALLY_TREATED"
OVER_TREATED = "OVER_TREATED"
UNDETERMINED = "UNDETERMINED"

LABELS = (UNDER_TREATED, OPTIMALLY_TREATED, OVER_TREATED, UNDETERMINED)

# ---------------------------------------------------------------------------
# The ranking. Narrow (1) to broad (9). Equal integers = judged comparable.
# Justifications, the ordering principle and the sign-off caveat are in
# spectrum_ranking.md. Do not edit one without editing the other.
# ---------------------------------------------------------------------------
SPECTRUM_RANK: dict[str, int] = {
    "penicillin-g":                   1,
    "oxacillin":                      1,
    "ampicillin":                     2,
    "cefazolin":                      2,
    "vancomycin":                     3,
    "daptomycin":                     4,
    "linezolid":                      4,
    "ampicillin-sulbactam":           5,
    "trimethoprim-sulfamethoxazole":  5,
    "ceftriaxone":                    6,
    "ciprofloxacin":                  7,
    "levofloxacin":                   7,
    "gentamicin":                     7,
    "ceftazidime":                    7,
    "cefepime":                       8,
    "piperacillin-tazobactam":        8,
    "meropenem":                      9,
}

TIER_LABEL: dict[int, str] = {
    1: "no Enterobacterales activity",
    2: "limited Enterobacterales activity",
    3: "Gram-positive reserve, no Gram-negative activity",
    4: "Gram-positive reserve including VRE, no Gram-negative activity",
    5: "moderate Enterobacterales activity, not antipseudomonal",
    6: "broad Enterobacterales activity, not antipseudomonal",
    7: "broad Enterobacterales activity, antipseudomonal",
    8: "antipseudomonal with extended beta-lactamase stability",
    9: "carbapenem",
}

# Agents whose place on a single breadth axis is a convention rather than a
# spectrum fact: they have no Gram-negative activity at all, so they are not
# comparable in organism range with anything from rank 5 upward. Flagged in the
# audit output so a reviewer can find every row that depends on the convention.
OFF_AXIS_AGENTS = frozenset({"vancomycin", "daptomycin", "linezolid"})

# The beta-lactam subset, for the secondary analysis that is comparable with Yuan
# et al., who report "active beta-lactam" and split only beta-lactam prescribing.
BETA_LACTAMS = frozenset({
    "penicillin-g", "oxacillin", "ampicillin", "cefazolin", "ampicillin-sulbactam",
    "ceftriaxone", "ceftazidime", "cefepime", "piperacillin-tazobactam", "meropenem",
})

FROZEN_CFG = BS.ScoringConfig()   # intermediate_as='separate', require_all=True


def _cfg(cfg):
    return FROZEN_CFG if cfg is None else cfg


def rank_of(drug: str) -> int | None:
    """Ordinal breadth rank of one agent, or None if it is not in the formulary."""
    canon = BS.canon_drug(drug) if drug is not None else None
    return SPECTRUM_RANK.get(canon) if canon else None


def _as_list(recommended) -> list[str]:
    if recommended is None:
        return []
    if isinstance(recommended, str):
        parts = [p for p in recommended.replace("|", ";").split(";")]
        return [p.strip() for p in parts if p and p.strip()]
    if isinstance(recommended, (list, tuple, set, pd.Series)):
        out = []
        for r in recommended:
            out.extend(_as_list(r))
        return out
    return [str(recommended)]


def narrowest_active(panel: pd.DataFrame, cfg=None,
                     candidates: Iterable[str] | None = None) -> dict:
    """Every formulary agent shown active on this panel, and the narrowest of them.

    Active means score_case([agent], panel) == ADEQUATE, i.e. the laboratory
    tested the agent on every pathogenic isolate and every verdict was S. An
    untested agent cannot qualify, which is the main limitation of the whole
    taxonomy as applied to MIMIC-IV.

    candidates restricts the reference pool, e.g. BETA_LACTAMS for the analysis
    that is comparable with Yuan et al. Default is the whole formulary.

    Returns {'rank': int|None, 'agents': [...], 'n_active': int,
             'active': {agent: rank}}.
    """
    cfg = _cfg(cfg)
    pool = list(SPECTRUM_RANK) if candidates is None else [
        a for a in SPECTRUM_RANK if a in set(candidates)]
    if panel is None or len(panel) == 0:
        return {"rank": None, "agents": [], "n_active": 0, "active": {}}
    active = {}
    for agent in pool:
        if BS.score_case([agent], panel, cfg)["outcome"] == BS.ADEQUATE:
            active[agent] = SPECTRUM_RANK[agent]
    if not active:
        return {"rank": None, "agents": [], "n_active": 0, "active": {}}
    best = min(active.values())
    return {"rank": best,
            "agents": sorted(a for a, r in active.items() if r == best),
            "n_active": len(active),
            "active": active}


def _breadth_key(agents: Sequence[str]) -> tuple[int, int]:
    """(rank of the broadest agent, number of ranked agents). Lower = narrower."""
    ranks = [SPECTRUM_RANK[a] for a in agents]
    return (max(ranks), len(ranks))


def _narrower_alternatives(parsed: list[str], panel, cfg, ref: dict
                           ) -> tuple[tuple[int, int] | None, list[str]]:
    """Narrowest ADEQUATE alternative strictly narrower than `parsed`, if any.

    Alternatives = every single formulary agent shown active on this panel, plus
    every proper non-empty subset of the recommendation itself. Subsets matter
    only for multi-agent regimens; for a single agent the subset set is empty and
    this reduces to "is any active agent narrower than the one recommended".
    """
    rec_key = _breadth_key(parsed)
    best_key, best_agents = None, []
    for agent, r in ref["active"].items():
        k = (r, 1)
        if k < rec_key and (best_key is None or k < best_key):
            best_key, best_agents = k, [agent]
        elif k == best_key and agent not in best_agents:
            best_agents.append(agent)
    if len(parsed) > 1:
        from itertools import combinations
        for n in range(1, len(parsed)):
            for sub in combinations(sorted(set(parsed)), n):
                k = _breadth_key(sub)
                if best_key is not None and k >= best_key:
                    continue
                if k >= rec_key:
                    continue
                if BS.score_case(list(sub), panel, cfg)["outcome"] == BS.ADEQUATE:
                    best_key, best_agents = k, ["+".join(sub)]
    return best_key, sorted(best_agents)


def classify_detail(recommended, panel: pd.DataFrame, cfg=None,
                    reference: dict | None = None) -> dict:
    """Spectrum label plus the evidence for it, so a disputed case is re-adjudicable.

    recommended : one agent, or a sequence / ';'-joined string for a regimen
    panel       : this case's PATHOGENIC isolate rows, columns
                  ['org_name','isolate_num','ab_name','interpretation']
    reference   : optional precomputed narrowest_active(panel) result, for reuse
                  across many recommendations scored on the same case
    """
    cfg = _cfg(cfg)
    raw = _as_list(recommended)
    canon = [BS.canon_drug(d) for d in raw]
    parsed = [c for c in canon if c is not None]
    unparsed = [d for d, c in zip(raw, canon) if c is None]

    out = {"label": UNDETERMINED, "reason": "", "coverage_outcome": None,
           "recommended_canonical": ";".join(parsed), "unparsed": ";".join(unparsed),
           "rec_rank": None, "rec_n_agents": len(parsed), "reference_rank": None,
           "reference_agents": "", "n_active_agents_tested": 0, "off_axis": False,
           "cfg_fingerprint": cfg.fingerprint()}

    if not parsed:
        out["reason"] = "no parsable formulary agent"
        return out

    out["rec_rank"] = max(SPECTRUM_RANK[c] for c in parsed)
    out["off_axis"] = any(c in OFF_AXIS_AGENTS for c in parsed)

    sc = BS.score_case(parsed, panel, cfg)
    out["coverage_outcome"] = sc["outcome"]

    if sc["outcome"] == BS.INADEQUATE:
        out["label"] = UNDER_TREATED
        out["reason"] = "inactive: " + sc["reason"]
        return out
    if sc["outcome"] != BS.ADEQUATE:
        out["label"] = UNDETERMINED
        out["reason"] = sc["reason"]
        return out

    ref = narrowest_active(panel, cfg) if reference is None else reference
    out["reference_rank"] = ref["rank"]
    out["reference_agents"] = ";".join(ref["agents"])
    out["n_active_agents_tested"] = ref["n_active"]

    alt_key, alt_agents = _narrower_alternatives(parsed, panel, cfg, ref)
    if alt_key is None:
        out["label"] = OPTIMALLY_TREATED
        if ref["rank"] is None:
            out["reason"] = ("active; no single formulary agent shown active on "
                             "this panel, so no narrower alternative exists")
        else:
            out["reason"] = ("active at rank %d, no narrower alternative shown active"
                             % out["rec_rank"])
    else:
        out["label"] = OVER_TREATED
        out["reason"] = ("active at breadth (%d,%d); narrower active alternative at "
                         "(%d,%d): %s" % (out["rec_rank"], len(parsed),
                                          alt_key[0], alt_key[1],
                                          ";".join(alt_agents)))
        out["reference_rank"] = alt_key[0]
        out["reference_agents"] = ";".join(alt_agents)
    return out


def classify(recommended, panel: pd.DataFrame, cfg=None,
             reference: dict | None = None) -> str:
    """UNDER_TREATED | OPTIMALLY_TREATED | OVER_TREATED | UNDETERMINED."""
    return classify_detail(recommended, panel, cfg, reference)["label"]


def ranking_table() -> pd.DataFrame:
    """The ranking as a frame, for printing next to spectrum_ranking.md."""
    rows = [{"rank": r, "tier": TIER_LABEL[r], "drug": d,
             "off_axis": d in OFF_AXIS_AGENTS}
            for d, r in sorted(SPECTRUM_RANK.items(), key=lambda kv: (kv[1], kv[0]))]
    return pd.DataFrame(rows)


def self_check() -> None:
    """Cheap invariants. Run with: python spectrum.py"""
    assert set(SPECTRUM_RANK) == set(BS.FORMULARY), (
        "ranking must cover exactly the formulary: "
        f"missing {set(BS.FORMULARY) - set(SPECTRUM_RANK)}, "
        f"extra {set(SPECTRUM_RANK) - set(BS.FORMULARY)}")
    assert len(SPECTRUM_RANK) == 17, len(SPECTRUM_RANK)
    assert set(SPECTRUM_RANK.values()) == set(TIER_LABEL), "tier labels out of step"
    assert FROZEN_CFG.fingerprint() == "04ce311c2b13", FROZEN_CFG.fingerprint()

    # Synthetic panel: one E. coli isolate, ampicillin R, ceftriaxone S,
    # pip-tazo S, meropenem S, cefazolin untested.
    p = pd.DataFrame([
        dict(org_name="ESCHERICHIA COLI", isolate_num=1, ab_name="AMPICILLIN", interpretation="R"),
        dict(org_name="ESCHERICHIA COLI", isolate_num=1, ab_name="CEFTRIAXONE", interpretation="S"),
        dict(org_name="ESCHERICHIA COLI", isolate_num=1, ab_name="PIPERACILLIN/TAZO", interpretation="S"),
        dict(org_name="ESCHERICHIA COLI", isolate_num=1, ab_name="MEROPENEM", interpretation="S"),
        dict(org_name="ESCHERICHIA COLI", isolate_num=1, ab_name="GENTAMICIN", interpretation="I"),
    ])
    assert classify("ampicillin", p) == UNDER_TREATED
    assert classify("ceftriaxone", p) == OPTIMALLY_TREATED
    assert classify("piperacillin-tazobactam", p) == OVER_TREATED
    assert classify("meropenem", p) == OVER_TREATED
    assert classify("cefazolin", p) == UNDETERMINED          # never tested
    assert classify("gentamicin", p) == UNDETERMINED         # Intermediate only
    assert classify("vancomycin", p) == UNDETERMINED         # never tested
    assert classify("ceftriaxone;vancomycin", p) == OVER_TREATED  # extra agent widens
    assert classify("banana", p) == UNDETERMINED
    d = classify_detail("piperacillin-tazobactam", p)
    assert d["reference_rank"] == 6 and d["rec_rank"] == 8, d

    # Polymicrobial case where no single agent covers both isolates but the pair
    # does: the combination is then the narrowest active option, not over-treatment.
    q = pd.DataFrame([
        dict(org_name="ESCHERICHIA COLI", isolate_num=1, ab_name="CEFTRIAXONE", interpretation="S"),
        dict(org_name="ESCHERICHIA COLI", isolate_num=1, ab_name="VANCOMYCIN", interpretation="R"),
        dict(org_name="ENTEROCOCCUS FAECIUM", isolate_num=2, ab_name="CEFTRIAXONE", interpretation="R"),
        dict(org_name="ENTEROCOCCUS FAECIUM", isolate_num=2, ab_name="VANCOMYCIN", interpretation="S"),
    ])
    assert classify("ceftriaxone", q) == UNDER_TREATED
    assert classify("vancomycin", q) == UNDER_TREATED
    assert classify("ceftriaxone;vancomycin", q) == OPTIMALLY_TREATED
    assert BETA_LACTAMS <= set(SPECTRUM_RANK)
    assert narrowest_active(p, candidates=BETA_LACTAMS)["rank"] == 6
    assert narrowest_active(p)["rank"] == 6

    print("spectrum.py self_check OK: 17 agents ranked, cfg %s"
          % FROZEN_CFG.fingerprint())


if __name__ == "__main__":
    self_check()
    print(ranking_table().to_string(index=False))
