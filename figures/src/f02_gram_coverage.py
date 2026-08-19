#!/usr/bin/env python
"""F2 - ground-truth structure: what the laboratory tests decides what can be scored.

Every number in this figure is computed here, from files on disk. Nothing is
hand-entered. Run it and the stdout block is the audit trail.

Universe: every panel-bearing positive blood-culture specimen in the extract
(inputs/panel_rows.parquet), after removing probable-contaminant and
non-bacterial isolates with the frozen scoring module. Each such specimen is one
case; its Gram class comes from population.case_gram over its surviving isolates.
Coverage for an agent = the case has at least one susceptibility row for that
agent, i.e. the laboratory chose to test it.

Aggregates only. No patient-level identifier appears in any mark or label.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/Users/shamzzzh/brain_run")
sys.path.insert(0, str(ROOT))                    # debate_run, population
sys.path.insert(0, str(ROOT / "figures" / "src"))  # _style

import pandas as pd

import _style as S
import debate_run as DR          # gives us the frozen scoring module as DR.BS
import population as POP         # gram_class(), case_gram() - imported, not reimplemented

BS = DR.BS

PANEL = ROOT / "inputs" / "panel_rows.parquet"
COHORT = ROOT / "inputs" / "cohort_skeleton.parquet"

# Rows on the chart, in the order they are drawn once sorted by the gap.
# The brief fixes the minimum set; gentamicin and trimethoprim-sulfamethoxazole
# are the controls that show the gap is a property of the agent, not of the file.
AGENTS = [
    "piperacillin-tazobactam",
    "meropenem",
    "ceftriaxone",
    "gentamicin",
    "trimethoprim-sulfamethoxazole",
    "oxacillin",
    "vancomycin",
]
HEADLINE = "piperacillin-tazobactam"

GRAM_ORDER = ["positive", "negative", "mixed/other"]


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------
def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(PANEL)
    if "interpretation" not in p.columns and "interp" in p.columns:
        p = p.rename(columns={"interp": "interpretation"})
    return p


def pathogenic(p: pd.DataFrame) -> pd.DataFrame:
    """Drop probable contaminants and non-bacterial isolates, frozen definitions."""
    names = p["org_name"].astype(str).unique()
    bad = {o for o in names
           if BS.is_probable_contaminant(o) or BS.is_non_bacterial(o)}
    return p[~p["org_name"].astype(str).isin(bad)].copy()


def contingency(pp: pd.DataFrame):
    """Returns (case_gram Series indexed by specimen, totals, coverage table)."""
    per_case_orgs = pp.groupby("micro_specimen_id")["org_name"].apply(
        lambda s: sorted(set(s.astype(str))))
    case_gram = per_case_orgs.map(POP.case_gram)

    totals = case_gram.value_counts().reindex(GRAM_ORDER).fillna(0).astype(int)

    q = pp.copy()
    q["canon"] = q["ab_name"].astype(str).map(BS.canon_drug)
    q = q.dropna(subset=["canon"])
    q["gram"] = q["micro_specimen_id"].map(case_gram)
    tested = q.drop_duplicates(["micro_specimen_id", "canon"])

    cov = (tested.pivot_table(index="canon", columns="gram",
                              values="micro_specimen_id", aggfunc="count")
           .reindex(columns=GRAM_ORDER).fillna(0).astype(int))
    return case_gram, totals, cov


def isolate_check(pp: pd.DataFrame) -> pd.Series:
    """Isolate-level Gram split, printed as a cross-check on the case-level split."""
    iso = pp.drop_duplicates(["micro_specimen_id", "org_name"]).copy()
    iso["gram"] = iso["org_name"].astype(str).map(POP.gram_class)
    return iso["gram"].value_counts()


# ---------------------------------------------------------------------------
# figure
# ---------------------------------------------------------------------------
def build(rows, totals, n_cases):
    fig, ax = S.new_figure("full")

    n = len(rows)
    ys = list(range(n - 1, -1, -1))          # first row of `rows` sits at the top

    for y, r in zip(ys, rows):
        head = r["agent"] == HEADLINE
        pos, neg = r["pos_pct"], r["neg_pct"]
        lo, hi = min(pos, neg), max(pos, neg)

        if head:
            ax.axhspan(y - 0.44, y + 0.44, color=S.ACCENT, alpha=0.065,
                       zorder=0, lw=0)
            ax.plot([lo, hi], [y, y], color=S.ACCENT, lw=2.8, alpha=0.85,
                    zorder=2, solid_capstyle="round")
        else:
            ax.plot([lo, hi], [y, y], color=S.MUTED, lw=2.0, alpha=0.32,
                    zorder=2, solid_capstyle="round")

        ax.scatter([neg], [y], s=112, color=S.PRIMARY, zorder=4,
                   edgecolors=S.WHITE, linewidths=1.1)
        ax.scatter([pos], [y], s=112, color=S.INK, zorder=4,
                   edgecolors=S.WHITE, linewidths=1.1)

        lab_col = S.ACCENT if head else S.INK
        weight = "bold" if head else "normal"
        S.direct_label(ax, lo - 2.4, y, r["lo_txt"], color=lab_col, ha="right",
                       fontsize=10.5, fontweight=weight)
        S.direct_label(ax, hi + 2.4, y, r["hi_txt"], color=lab_col, ha="left",
                       fontsize=10.5, fontweight=weight)

    # --- name the two dot colours by labelling the top row's own marks ---
    top = rows[0]
    ty = ys[0]
    for x, col, txt, ha in [
        (top["pos_pct"], S.INK,
         f"Gram-positive cases   n = {totals['positive']:,}", "left"),
        (top["neg_pct"], S.PRIMARY,
         f"Gram-negative cases   n = {totals['negative']:,}", "right"),
    ]:
        ax.plot([x, x], [ty + 0.17, ty + 0.44], color=col, lw=1.0,
                alpha=0.55, zorder=3)
        S.direct_label(ax, x + (1.6 if ha == "left" else -1.6), ty + 0.52, txt,
                       color=col, ha=ha, va="bottom", fontsize=10.2,
                       fontweight="bold")

    # --- the one number that matters ---
    h = rows[0] if rows[0]["agent"] == HEADLINE else \
        next(r for r in rows if r["agent"] == HEADLINE)
    hy = ys[[r["agent"] for r in rows].index(HEADLINE)]
    # text sits in the gap BELOW the row so its leader never runs along the rule
    S.annotate_key(
        ax, 18, hy - 0.62,
        f"tested in {h['pos_n']:,} of {totals['positive']:,} Gram-positive cases, "
        f"{h['neg_n']:,} of {totals['negative']:,} Gram-negative",
        arrow_to=(h["pos_pct"], hy), ha="left", fontsize=11.5)

    ax.set_yticks(ys)
    ax.set_yticklabels([r["agent"] for r in rows], fontsize=11.5)
    for lab, r in zip(ax.get_yticklabels(), rows):
        if r["agent"] == HEADLINE:
            lab.set_color(S.ACCENT)
            lab.set_fontweight("bold")
        else:
            lab.set_color(S.INK)

    ax.set_xlim(-16, 116)
    ax.set_ylim(-0.75, n - 1 + 1.05)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xticklabels(["0", "20", "40", "60", "80", "100%"])
    ax.set_xlabel("cases with the agent on the panel", labelpad=9)
    S.grid_x_only(ax)
    # grid_x_only() toggles rather than sets, and rcParams starts the grid on, so
    # the x-grid lands off. Re-assert it here; _style.py itself is not touched.
    ax.grid(axis="x", which="major", visible=True, color=S.GRID, linewidth=0.7)
    for sp in ax.spines.values():
        sp.set_visible(False)

    S.kicker_title(
        fig, "ground truth structure",
        "The Gram stain decides which drugs the laboratory tests, and so which can be scored at all.",
        f"Every panel-bearing positive blood culture in the extract, {n_cases:,} cases after "
        f"removing probable contaminants and non-bacterial isolates. 19 August 2026.")
    fig.subplots_adjust(top=0.735, left=0.225, right=0.965, bottom=0.155)
    return fig


# ---------------------------------------------------------------------------
def main():
    panel = load_panel()
    pp = pathogenic(panel)
    case_gram, totals, cov = contingency(pp)
    n_cases = int(totals.sum())

    print("=" * 78)
    print("F2  panel coverage by Gram class of the case")
    print("=" * 78)
    print(f"panel_rows.parquet          rows {len(panel):,}   "
          f"specimens {panel['micro_specimen_id'].nunique():,}")
    print(f"after contaminant/non-bacterial drop   rows {len(pp):,}   "
          f"specimens {pp['micro_specimen_id'].nunique():,}")
    print()
    print("case Gram class (population.case_gram over surviving isolates)")
    for g in GRAM_ORDER:
        print(f"   {g:<12} {totals[g]:>7,}   {100 * totals[g] / n_cases:5.1f}%")
    print(f"   {'TOTAL':<12} {n_cases:>7,}")
    print()
    print("isolate-level cross-check (population.gram_class per distinct isolate)")
    for k, v in isolate_check(pp).items():
        print(f"   {k:<12} {v:>7,}")
    print()

    print("FULL CONTINGENCY - cases with >=1 panel row for the agent")
    hdr = (f"{'agent':<32}" + "".join(f"{g:>22}" for g in GRAM_ORDER))
    print(hdr)
    print("-" * len(hdr))
    for agent in cov.index:
        line = f"{agent:<32}"
        for g in GRAM_ORDER:
            k = int(cov.loc[agent, g])
            line += f"{k:>10,} /{totals[g]:>6,} {100 * k / totals[g]:5.1f}%"
        print(line)
    print("-" * len(hdr))
    print(f"{'(all cases in class)':<32}" +
          "".join(f"{totals[g]:>22,}" for g in GRAM_ORDER))
    print()

    rows = []
    for agent in AGENTS:
        pos_n, neg_n = int(cov.loc[agent, "positive"]), int(cov.loc[agent, "negative"])
        pos_pct = 100 * pos_n / totals["positive"]
        neg_pct = 100 * neg_n / totals["negative"]
        fmt = lambda v: f"{v:.0f}%" if v == 0 else f"{v:.1f}%"
        lo_is_pos = pos_pct <= neg_pct
        rows.append(dict(agent=agent, pos_n=pos_n, neg_n=neg_n,
                         pos_pct=pos_pct, neg_pct=neg_pct,
                         gap=neg_pct - pos_pct,
                         lo_txt=fmt(pos_pct if lo_is_pos else neg_pct),
                         hi_txt=fmt(neg_pct if lo_is_pos else pos_pct)))
    rows.sort(key=lambda r: -r["gap"])

    print("PLOTTED ROWS, sorted by (Gram-negative - Gram-positive) coverage")
    for r in rows:
        mark = "  <-- headline" if r["agent"] == HEADLINE else ""
        print(f"   {r['agent']:<32} pos {r['pos_n']:>5,} ({r['pos_pct']:5.1f}%)   "
              f"neg {r['neg_n']:>5,} ({r['neg_pct']:5.1f}%)   "
              f"gap {r['gap']:+6.1f} pts{mark}")
    print()

    h = next(r for r in rows if r["agent"] == HEADLINE)
    print("HEADLINE NUMBERS")
    print(f"   piperacillin-tazobactam on the panel: "
          f"{h['pos_n']:,}/{totals['positive']:,} Gram-positive cases "
          f"({h['pos_pct']:.2f}%) vs {h['neg_n']:,}/{totals['negative']:,} "
          f"Gram-negative ({h['neg_pct']:.2f}%)")
    print(f"   coverage gap: {h['gap']:.1f} percentage points")
    v = next(r for r in rows if r["agent"] == "vancomycin")
    print(f"   mirror image, vancomycin: {v['neg_n']:,}/{totals['negative']:,} "
          f"Gram-negative ({v['neg_pct']:.2f}%) vs {v['pos_n']:,}/"
          f"{totals['positive']:,} Gram-positive ({v['pos_pct']:.2f}%)")
    print(f"   mixed/other cases excluded from the chart: {totals['mixed/other']:,} "
          f"({100 * totals['mixed/other'] / n_cases:.1f}% of cases)")

    # sensitivity: the same structure inside the frozen cohort of 7,796
    coh = set(pd.read_parquet(COHORT)["micro_specimen_id"])
    sub = pp[pp["micro_specimen_id"].isin(coh)]
    _, t2, c2 = contingency(sub)
    print(f"   [sensitivity] frozen cohort only, {int(t2.sum()):,} cases: pip-tazo "
          f"{int(c2.loc[HEADLINE, 'positive']):,}/{t2['positive']:,} Gram-positive vs "
          f"{int(c2.loc[HEADLINE, 'negative']):,}/{t2['negative']:,} Gram-negative")
    print()

    fig = build(rows, totals, n_cases)
    man = S.save(fig, "F2", "gram_coverage", draft=False,
                 source="inputs/panel_rows.parquet via population.case_gram "
                        "+ brain_scoring_local",
                 note=f"{totals['mixed/other']:,} mixed/other cases not shown")
    print(f"wrote {man['png']}")
    print(f"wrote {man['svg']}")
    return man


if __name__ == "__main__":
    main()
