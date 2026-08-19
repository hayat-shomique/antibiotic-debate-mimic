"""F7 - the speaking-order effect.

Claim: the same patient gets a different final drug depending on who speaks first.

Reads ONLY runs/debate_20260818.jsonl. Records with kind=="full" are ordering-runs;
each case_id appears twice, once as "A-first" and once as "B-first". The two runs are
identical but for who opens. The figure is an alluvial flow of Agent A's final drug
under A-first (left) against the same agent's final drug under B-first (right).

PROVENANCE NOTE. The ORDERS brief quotes 384 ordering-runs / 192 paired cases. The file
on disk now carries 400 / 200: chain_topup.log records a top-up run that completed the
8 cases the 08:15 deadline had cut. This script ships the disk truth (200 pairs) and,
as a self-check, re-derives the frozen 192-pair numbers by excluding the topped-up
case ids parsed out of chain_topup.log. Both are printed. Nothing is typed in.

Governance: counts and rates only. No case_id, subject_id or micro_specimen_id is
drawn, labelled or otherwise placed on the canvas.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "/Users/shamzzzh/brain_run/figures/src")
import _style as S  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path("/Users/shamzzzh/brain_run")
SRC = ROOT / "runs" / "debate_20260818.jsonl"
TOPUP_LOG = ROOT / "chain_topup.log"

ORDER_A = "A-first"
ORDER_B = "B-first"
ADEQUATE = "ADEQUATE"


# ----------------------------------------------------------------------------- data
def load_full() -> list[dict]:
    """Every kind=='full' ordering-run in the debate file."""
    rows = [json.loads(l) for l in open(SRC) if l.strip()]
    return [r for r in rows if r.get("kind") == "full"]


def pair_up(full: list[dict]) -> pd.DataFrame:
    """One row per case that completed BOTH orderings. Case ids are dropped."""
    by_case: dict[str, dict] = defaultdict(dict)
    for r in full:
        by_case[r["case_id"]][r["ordering"]] = r

    recs = []
    for runs in by_case.values():
        if ORDER_A not in runs or ORDER_B not in runs:
            continue
        a, b = runs[ORDER_A], runs[ORDER_B]
        recs.append(dict(
            a_first_drug=a["final_A"],
            b_first_drug=b["final_A"],
            a_first_adequate=a["final_A_outcome"] == ADEQUATE,
            b_first_adequate=b["final_A_outcome"] == ADEQUATE,
            round0_drug=a["round0_drug"],
        ))
    d = pd.DataFrame(recs)
    d["discordant"] = d["a_first_drug"] != d["b_first_drug"]
    return d


def topup_case_ids() -> list[str]:
    """Case ids the top-up run added, parsed from chain_topup.log. [] if absent."""
    if not TOPUP_LOG.exists():
        return []
    txt = TOPUP_LOG.read_text()
    return re.findall(r"\[\d+/\d+\]\s+(\S+)\s+done", txt)


# ----------------------------------------------------------------------------- layout
def node_layout(counts: list[tuple[str, int]], gap: float, span: float):
    """Stack nodes top-to-bottom, centred on `span`. Returns name -> (y0, y1)."""
    total = sum(c for _, c in counts) + gap * (len(counts) - 1)
    y = (span - total) / 2.0
    out = {}
    for name, c in counts:
        out[name] = (y, y + c)
        y += c + gap
    return out


def ribbon(ax, xl, xr, y0l, y1l, y0r, y1r, color, alpha, zorder=2):
    """A flow band from the left node edge to the right node edge, smoothstepped."""
    t = np.linspace(0.0, 1.0, 256)
    s = 3.0 * t ** 2 - 2.0 * t ** 3
    x = xl + (xr - xl) * t
    top = y0l + (y0r - y0l) * s
    bot = y1l + (y1r - y1l) * s
    ax.fill_between(x, top, bot, color=color, alpha=alpha, lw=0, zorder=zorder)
    # boundary strokes: define the edge, and keep a 1-case ribbon visible at true scale
    for edge in (top, bot):
        ax.plot(x, edge, color=color, alpha=min(1.0, alpha + 0.28), lw=0.55,
                zorder=zorder + 0.1, solid_capstyle="round")


def order_columns(d: pd.DataFrame):
    """Right nodes by size; left nodes by barycentre over the right order. Planar here."""
    right = [(k, int(v)) for k, v in d["b_first_drug"].value_counts().items()]
    ridx = {name: i for i, (name, _) in enumerate(right)}

    left_counts = d["a_first_drug"].value_counts()
    bary = {}
    for name in left_counts.index:
        sub = d[d["a_first_drug"] == name]
        w = sub["b_first_drug"].map(ridx)
        bary[name] = float(w.mean())
    left = sorted(((k, int(left_counts[k])) for k in left_counts.index),
                  key=lambda kv: (bary[kv[0]], -kv[1]))
    return left, right


# ----------------------------------------------------------------------------- figure
def build(d: pd.DataFrame, ct: pd.DataFrame) -> dict:
    n_pairs = len(d)
    n_disc = int(d["discordant"].sum())
    pct_disc = 100.0 * n_disc / n_pairs

    ad_a = int(d["a_first_adequate"].sum())
    ad_b = int(d["b_first_adequate"].sum())
    pa, pb = 100.0 * ad_a / n_pairs, 100.0 * ad_b / n_pairs

    left, right = order_columns(d)
    GAP = 6.0
    span = max(sum(c for _, c in left) + GAP * (len(left) - 1),
               sum(c for _, c in right) + GAP * (len(right) - 1))
    ly = node_layout(left, GAP, span)
    ry = node_layout(right, GAP, span)
    lidx = {n: i for i, (n, _) in enumerate(left)}
    ridx = {n: i for i, (n, _) in enumerate(right)}

    XL, XR, BARW = 0.0, 1.0, 0.020

    fig, (ax, ax2) = S.new_figure(size="full", ncols=2,
                                  gridspec_kw={"width_ratios": [4.3, 1.0]})
    fig.subplots_adjust(top=0.735, bottom=0.115, left=0.028, right=0.972, wspace=0.30)

    # --- ribbons, laid out so neither side crosses itself ----------------------
    # Left cursors are consumed in left-node order, right cursors in right-node
    # order; with the barycentre column ordering above this leaves no crossings.
    flows = [(a, b, int(ct.loc[a, b])) for a in ct.index for b in ct.columns
             if int(ct.loc[a, b]) > 0]
    biggest_disc = max((f for f in flows if f[0] != f[1]), key=lambda f: f[2])

    lcur = {n: ly[n][0] for n, _ in left}
    rcur = {n: ry[n][0] for n, _ in right}
    placed = []
    for a, b, k in sorted(flows, key=lambda f: (lidx[f[0]], ridx[f[1]])):
        y0l, y1l = lcur[a], lcur[a] + k
        lcur[a] = y1l
        placed.append((a, b, k, y0l, y1l))
    for a, b, k, y0l, y1l in sorted(placed, key=lambda f: (ridx[f[1]], lidx[f[0]])):
        y0r, y1r = rcur[b], rcur[b] + k
        rcur[b] = y1r
        disc = a != b
        ribbon(ax, XL, XR, y0l, y1l, y0r, y1r,
               color=S.ACCENT if disc else S.MUTED,
               alpha=0.70 if disc else 0.26,
               zorder=3 if disc else 2)
        if (a, b, k) == biggest_disc:
            S.direct_label(ax, 0.5, (y0l + y1l + y0r + y1r) / 4.0, f"{k} cases",
                           color=S.WHITE, ha="center", va="center",
                           fontsize=12, fontweight="bold")

    # --- node bars and their labels -------------------------------------------
    NUMPAD, NAMEPAD = 0.015, 0.150   # counts hug the bar; names sit clear of them
    for name, c in left:
        y0, y1 = ly[name]
        ax.add_patch(Rectangle((XL - BARW, y0), BARW, y1 - y0, color=S.INK,
                               lw=0, zorder=5))
        S.direct_label(ax, XL - BARW - NUMPAD, (y0 + y1) / 2, f"{c}", color=S.INK,
                       ha="right", va="center", fontsize=11, fontweight="bold",
                       fontfamily="monospace")
        S.direct_label(ax, XL - BARW - NAMEPAD, (y0 + y1) / 2, name, color=S.INK,
                       ha="right", va="center", fontsize=11.5)
    for name, c in right:
        y0, y1 = ry[name]
        ax.add_patch(Rectangle((XR, y0), BARW, y1 - y0, color=S.INK, lw=0, zorder=5))
        S.direct_label(ax, XR + BARW + NUMPAD, (y0 + y1) / 2, f"{c}", color=S.INK,
                       ha="left", va="center", fontsize=11, fontweight="bold",
                       fontfamily="monospace")
        S.direct_label(ax, XR + BARW + NAMEPAD, (y0 + y1) / 2, name, color=S.INK,
                       ha="left", va="center", fontsize=11.5)

    # --- column headers --------------------------------------------------------
    S.direct_label(ax, XL - BARW, -18, "when A opens", color=S.INK, ha="right",
                   va="center", fontsize=12, fontweight="bold")
    S.direct_label(ax, XR + BARW, -18, "when B opens", color=S.INK, ha="left",
                   va="center", fontsize=12, fontweight="bold")

    # --- the one number that matters -------------------------------------------
    S.annotate_key(
        ax, XL - BARW - NAMEPAD, span + 48,
        f"{n_disc} of {n_pairs} cases, {pct_disc:.1f}%, land on a different drug when the\n"
        "other agent opens. Nothing about the patient changed, and the\n"
        f"adequacy rate moves only {pb - pa:+.1f} points.",
        ha="left", va="center", fontsize=12.5,
    )

    ax.set_xlim(-0.52, 1.82)
    ax.set_ylim(span + 90, -34)
    ax.set_xticks([]); ax.set_yticks([])
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)

    # --- right panel: the flip buys almost nothing -----------------------------
    ax2.barh([0, 1], [pa, pb], height=0.40, color=S.PRIMARY, alpha=0.80, zorder=2)
    for y, v, k in ((0, pa, ad_a), (1, pb, ad_b)):
        ax2.text(v + 3.0, y, f"{v:.1f}", color=S.INK, ha="left", va="center",
                 fontsize=11, fontweight="bold", fontfamily="monospace")
    ax2.set_ylim(1.72, -0.95)
    ax2.set_xlim(0, 100)
    ax2.set_xticks([0, 50, 100])
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["A opens", "B opens"])
    ax2.tick_params(axis="y", labelcolor=S.INK, pad=4)
    ax2.set_xlabel("final position adequate (%)")
    S.grid_x_only(ax2)
    ax2.spines["left"].set_visible(False)
    S.direct_label(ax2, 0, -0.72, "the drug moves, the rate does not",
                   color=S.MUTED, ha="left", va="center", fontsize=10.5)
    S.direct_label(ax2, 0, 1.46, f"{pb - pa:+.1f} points", color=S.MUTED,
                   ha="left", va="center", fontsize=10.5)

    S.kicker_title(
        fig, "positional deference",
        "The same patient gets a different final drug depending on who speaks first.",
        f"{n_pairs} cases, each run twice and identical but for who opens. Ribbons carry "
        "Agent A's final drug, weighted by cases; coloured ribbons are the cases the two runs decide differently.",
    )

    return S.save(
        fig, "F7", "speaking_order", draft=False,
        source=f"runs/debate_20260818.jsonl, kind=full, {2 * n_pairs} ordering-runs -> {n_pairs} paired cases",
        note="supersedes the 192-pair freeze; file topped up to 200 pairs (chain_topup.log)",
    )


# ----------------------------------------------------------------------------- checks
def freeze_check(full: list[dict]) -> None:
    """Re-derive the frozen 192-pair numbers by removing the topped-up cases."""
    ids = topup_case_ids()
    print("FREEZE CHECK  (logic validation only, the figure ships the full file)")
    if not ids:
        print(f"  {TOPUP_LOG.name} absent, check skipped")
        return
    pre = [r for r in full if r["case_id"] not in set(ids)]
    d = pair_up(pre)
    n = len(pre)
    print(f"  topped-up cases parsed from {TOPUP_LOG.name} : {len(ids)}")
    print(f"  pre-top-up ordering-runs                  : {n}          (brief says 384)")
    print(f"  pre-top-up paired cases                   : {len(d)}          (brief says 192)")
    print(f"  pre-top-up discordant by ordering         : {int(d['discordant'].sum())}/{len(d)} = "
          f"{100 * d['discordant'].mean():.1f}%   (brief says 76/192 = 39.6%)")
    k0 = sum(1 for r in pre if r["round0_outcome"] == ADEQUATE)
    kA = sum(1 for r in pre if r["final_A_outcome"] == ADEQUATE)
    print(f"  pre-top-up round-0 adequate               : {k0}/{n} = {100 * k0 / n:.1f}%   (brief says 87.0%)")
    print(f"  pre-top-up final-A adequate               : {kA}/{n} = {100 * kA / n:.1f}%   (brief says 78.6%)")


# ----------------------------------------------------------------------------- main
def main():
    full = load_full()
    d = pair_up(full)
    n_pairs, n_runs = len(d), len(full)

    ct = pd.crosstab(d["a_first_drug"], d["b_first_drug"])
    # square the table so every drug appears on both axes
    drugs = sorted(set(ct.index) | set(ct.columns))
    ct = ct.reindex(index=drugs, columns=drugs, fill_value=0)

    print(f"F7  source: {SRC}")
    print(f"F7  kind=full ordering-runs: {n_runs}   paired cases: {n_pairs}")
    print()
    print("CROSS-TABULATION  rows = A-first final drug, cols = B-first final drug (cases)")
    print(ct.to_string())
    print(f"  row totals    {dict(ct.sum(axis=1))}")
    print(f"  column totals {dict(ct.sum(axis=0))}")
    print(f"  grand total   {int(ct.values.sum())}")
    print()

    n_disc = int(d["discordant"].sum())
    ad_a, ad_b = int(d["a_first_adequate"].sum()), int(d["b_first_adequate"].sum())
    pa, pb = 100.0 * ad_a / n_pairs, 100.0 * ad_b / n_pairs

    print("HEADLINE NUMBERS")
    print(f"  paired cases                              : {n_pairs}")
    print(f"  concordant (same final drug both ways)    : {n_pairs - n_disc}/{n_pairs} = "
          f"{100 * (n_pairs - n_disc) / n_pairs:.1f}%")
    print(f"  DISCORDANT (different final drug)         : {n_disc}/{n_pairs} = "
          f"{100 * n_disc / n_pairs:.1f}%   <- the claim")
    print(f"  final-A adequate, A-first                 : {ad_a}/{n_pairs} = {pa:.1f}%")
    print(f"  final-A adequate, B-first                 : {ad_b}/{n_pairs} = {pb:.1f}%")
    print(f"  adequacy difference B-first minus A-first : {pb - pa:+.1f} points")
    print(f"  held the round-0 drug, A-first            : "
          f"{int((d['a_first_drug'] == d['round0_drug']).sum())}/{n_pairs}")
    print(f"  held the round-0 drug, B-first            : "
          f"{int((d['b_first_drug'] == d['round0_drug']).sum())}/{n_pairs}")
    print()

    print("FLOWS  (every route with at least one case)")
    for a in ct.index:
        for b in ct.columns:
            k = int(ct.loc[a, b])
            if k:
                tag = "DISCORDANT" if a != b else "concordant"
                print(f"  {a:26s} -> {b:26s} {k:>4}  {100 * k / n_pairs:5.1f}%  {tag}")
    print()

    print("ADEQUACY WITHIN EACH GROUP")
    for lab, sub in (("concordant", d[~d["discordant"]]), ("discordant", d[d["discordant"]])):
        print(f"  {lab:11s} n={len(sub):>4}  A-first adequate "
              f"{int(sub['a_first_adequate'].sum()):>4}/{len(sub)} = "
              f"{100 * sub['a_first_adequate'].mean():5.1f}%   B-first adequate "
              f"{int(sub['b_first_adequate'].sum()):>4}/{len(sub)} = "
              f"{100 * sub['b_first_adequate'].mean():5.1f}%")
    print()
    print(f"  round-0 drug across pairs: {dict(Counter(d['round0_drug']))}")
    print()

    freeze_check(full)
    print()

    row = build(d, ct)
    print(f"F7  wrote {ROOT / row['png']}")
    print(f"F7  wrote {ROOT / row['svg']}")


if __name__ == "__main__":
    main()
