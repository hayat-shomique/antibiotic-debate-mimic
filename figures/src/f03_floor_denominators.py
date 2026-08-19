"""F3 - the frequency floor, read against two denominators.

Claim: how good the floor looks depends on which denominator you name.

Reads ONLY floor_reconciled.csv. Primary frame C_sampled_200 (the 200 cases
actually run). Frame D_supervisor_file_N3210_NOT_REPRODUCIBLE is excluded.

Every number on the canvas is computed here from the file. Nothing is typed in.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "/Users/shamzzzh/brain_run/figures/src")
import _style as S  # noqa: E402

import pandas as pd  # noqa: E402

ROOT = Path("/Users/shamzzzh/brain_run")
SRC = ROOT / "floor_reconciled.csv"
FRAME = "C_sampled_200"
EXCLUDED_FRAME = "D_supervisor_file_N3210_NOT_REPRODUCIBLE"


# ----------------------------------------------------------------------------- data
def load() -> pd.DataFrame:
    raw = pd.read_csv(SRC)
    if EXCLUDED_FRAME in set(raw["frame"]):
        raw = raw[raw["frame"] != EXCLUDED_FRAME]
    d = raw[raw["frame"] == FRAME].copy()
    if d.empty:
        raise SystemExit(f"frame {FRAME} not found in {SRC}")

    for c in ("n_cases", "n_adequate", "n_tested", "n_undetermined"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    for c in ("pct_of_all", "pct_of_tested", "pct_undetermined"):
        d[c] = pd.to_numeric(d[c], errors="coerce")

    d["scoreable"] = d["n_tested"] > 0
    d["gap_points"] = d["pct_of_tested"] - d["pct_of_all"]
    d = d.sort_values(["pct_of_all", "agent"], ascending=[False, True]).reset_index(drop=True)
    d["row"] = d.index
    return d


# ----------------------------------------------------------------------------- figure
def build(d: pd.DataFrame) -> dict:
    n_rows = len(d)
    n_cases = int(d["n_cases"].iloc[0])

    unscoreable = d[~d["scoreable"]]
    scoreable = d[d["scoreable"]]
    widest = scoreable.loc[scoreable["gap_points"].idxmax()]

    accent_rows = set(unscoreable["row"]) | {int(widest["row"])}

    fig, (ax, ax2) = S.new_figure(
        size="full", ncols=2,
        gridspec_kw={"width_ratios": [3.6, 1.0]},
    )
    fig.subplots_adjust(top=0.755, bottom=0.115, left=0.196, right=0.925, wspace=0.085)

    # --- left panel: the two denominators, joined -----------------------------
    for _, r in d.iterrows():
        y = r["row"]
        col = S.ACCENT if y in accent_rows else S.PRIMARY
        if r["scoreable"]:
            ax.plot([r["pct_of_all"], r["pct_of_tested"]], [y, y],
                    color=col, lw=2.2, alpha=0.55 if col == S.PRIMARY else 0.85,
                    solid_capstyle="round", zorder=2)
            ax.scatter([r["pct_of_tested"]], [y], s=54, color=col, zorder=4,
                       edgecolors=S.WHITE, linewidths=0.8)
        ax.scatter([r["pct_of_all"]], [y], s=48, facecolors=S.WHITE,
                   edgecolors=col, linewidths=1.7, zorder=3)

    # the unscoreable block, tied together at zero
    uy = sorted(unscoreable["row"])
    ax.plot([0, 0], [min(uy) - 0.42, max(uy) + 0.42], color=S.ACCENT, lw=3.2,
            solid_capstyle="butt", zorder=2)
    S.direct_label(
        ax, 4.0, (min(uy) + max(uy)) / 2,
        f"no isolate was tested\nagainst these {len(uy)}, the rate\n"
        "is undefined, not zero",
        color=S.ACCENT, ha="left", va="center", fontsize=10.5, linespacing=1.35,
    )

    # the one number that matters
    wrow = int(widest["row"])
    mid = (widest["pct_of_all"] + widest["pct_of_tested"]) / 2
    S.annotate_key(
        ax, 46.0, wrow + 2.35,
        f"{widest['gap_points']:.0f}-point swing on {widest['agent']} -\n"
        f"{int(widest['n_tested'])} of {n_cases} cases carried a result",
        arrow_to=(mid, wrow), ha="left", va="center", fontsize=11.5,
    )

    # direct labels for the two marks, on the row with clear separation
    lab = scoreable[scoreable["row"] < wrow]
    lrow = lab.loc[lab["gap_points"].idxmax()]
    S.direct_label(ax, lrow["pct_of_all"] - 2.6, lrow["row"],
                   f"of all {n_cases} cases", color=S.MUTED, ha="right",
                   va="center", fontsize=9.8)
    S.direct_label(ax, lrow["pct_of_tested"] + 2.6, lrow["row"],
                   "of cases with a result", color=S.MUTED, ha="left",
                   va="center", fontsize=9.8)

    ax.set_ylim(n_rows - 0.5, -0.75)
    ax.set_xlim(-2.5, 103)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_yticks(list(d["row"]))
    ax.set_yticklabels(list(d["agent"]))
    ax.tick_params(axis="y", labelcolor=S.INK, pad=6)
    for t, rr in zip(ax.get_yticklabels(), d["row"]):
        if rr in accent_rows:
            t.set_color(S.ACCENT)
    ax.set_xlabel("cases adequate (%)")
    S.grid_x_only(ax)
    ax.spines["left"].set_visible(False)

    # --- right panel: why the two differ --------------------------------------
    bar_cols = [S.ACCENT if rr in accent_rows else S.MUTED for rr in d["row"]]
    ax2.barh(d["row"], d["pct_undetermined"], height=0.5, color=bar_cols,
             alpha=0.75, zorder=2)
    for _, r in d.iterrows():
        ax2.text(130, r["row"], f"{r['pct_undetermined']:.1f}",
                 color=S.ACCENT if r["row"] in accent_rows else S.MUTED,
                 fontsize=9.6, ha="right", va="center", fontfamily="monospace",
                 clip_on=False)
    ax2.set_ylim(n_rows - 0.5, -0.75)
    ax2.set_xlim(0, 100)
    ax2.set_xticks([0, 50, 100])
    ax2.set_yticks([])
    ax2.set_xlabel("no S/I/R result (%)")
    S.grid_x_only(ax2)
    ax2.spines["left"].set_visible(False)

    S.kicker_title(
        fig, "denominator effect",
        "How good the floor looks depends on which denominator you name.",
        f"Frame {FRAME}, the {n_cases} cases actually run. Hollow mark counts every case; "
        "filled mark counts only cases the laboratory tested.",
    )

    return S.save(
        fig, "F3", "floor_denominators", draft=False,
        source=f"floor_reconciled.csv, frame {FRAME}",
        note=f"frame {EXCLUDED_FRAME} excluded",
    )


# ----------------------------------------------------------------------------- main
def main():
    d = load()
    cols = ["agent", "n_cases", "n_adequate", "pct_of_all", "n_tested",
            "pct_of_tested", "n_undetermined", "pct_undetermined", "gap_points"]
    print(f"F3  source: {SRC}")
    print(f"F3  frame plotted: {FRAME}   excluded: {EXCLUDED_FRAME}")
    print()
    print(d[cols].to_string(index=False, na_rep="-"))
    print()

    scoreable = d[d["scoreable"]]
    unscoreable = d[~d["scoreable"]]
    widest = scoreable.loc[scoreable["gap_points"].idxmax()]
    n_cases = int(d["n_cases"].iloc[0])

    print("HEADLINE NUMBERS")
    print(f"  agents on panel                      : {len(d)}")
    print(f"  frame size (cases)                   : {n_cases}")
    print(f"  agents with a zero tested denominator: {len(unscoreable)} "
          f"({', '.join(sorted(unscoreable['agent']))})")
    print(f"  widest denominator gap               : {widest['agent']} "
          f"{widest['pct_of_all']:.1f}% of all -> {widest['pct_of_tested']:.1f}% of tested "
          f"= {widest['gap_points']:.1f} points, on n_tested={int(widest['n_tested'])}")
    print(f"  median gap across scoreable agents   : {scoreable['gap_points'].median():.1f} points")
    print(f"  largest gap excluding {widest['agent']:<14}: "
          f"{scoreable.drop(index=widest.name)['gap_points'].max():.1f} points "
          f"({scoreable.drop(index=widest.name).loc[scoreable.drop(index=widest.name)['gap_points'].idxmax(), 'agent']})")
    print(f"  round-0 agent piperacillin-tazobactam: "
          f"{d.loc[d['agent'] == 'piperacillin-tazobactam', 'pct_of_all'].iat[0]:.1f}% of all vs "
          f"{d.loc[d['agent'] == 'piperacillin-tazobactam', 'pct_of_tested'].iat[0]:.1f}% of tested")
    print()

    row = build(d)
    print(f"F3  wrote {ROOT / row['png']}")
    print(f"F3  wrote {ROOT / row['svg']}")


if __name__ == "__main__":
    main()
