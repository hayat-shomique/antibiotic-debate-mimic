"""F8 - the 2x2 read as a transition matrix.

Every ordering-run in runs/debate_20260818.jsonl carries two adequacy verdicts scored
against the same microbiology panel: the fixed round-0 position and agent A's final
position. Cross-tabulating them turns a single accuracy delta into a flow, and the flow
has a direction: runs leaving ADEQUATE outnumber runs arriving at it.

Two conditional rates are fixed here and defined on the figure itself:
    HRR, harmful revision rate      = P(final INADEQUATE | round-0 ADEQUATE)
    BCR, beneficial correction rate = P(final ADEQUATE   | round-0 INADEQUATE)

Every number drawn or written is computed below from the run file. Nothing is typed in
by hand, including the title, which is assembled from the computed counts.

Run:  python figures/src/f08_transition_matrix.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from matplotlib.patches import Rectangle

sys.path.insert(0, "/Users/shamzzzh/brain_run/figures/src")
import _style as S  # noqa: E402

ROOT = Path("/Users/shamzzzh/brain_run")
RUNS = ROOT / "runs" / "debate_20260818.jsonl"

CATS = ["ADEQUATE", "INADEQUATE", "INTERMEDIATE_ONLY", "UNDETERMINED"]
SHORT = {"ADEQUATE": "Adequate", "INADEQUATE": "Inadequate",
         "INTERMEDIATE_ONLY": "Intermediate\nonly", "UNDETERMINED": "Undetermined"}
MONO = S._available(S._MONO_STACK)[0]


# ------------------------------------------------------------------ read + count
def load_full(path: Path) -> list[dict]:
    out = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("kind") == "full" and not rec.get("quarantined", False):
                out.append(rec)
    return out


runs = load_full(RUNS)
N = len(runs)
N_CASES = len({r["case_id"] for r in runs})

M = Counter((r["round0_outcome"], r["final_A_outcome"]) for r in runs)
row_tot = {a: sum(M[(a, b)] for b in CATS) for a in CATS}
col_tot = {b: sum(M[(a, b)] for a in CATS) for b in CATS}

harm = M[("ADEQUATE", "INADEQUATE")]
ben = M[("INADEQUATE", "ADEQUATE")]
hrr = 100 * harm / row_tot["ADEQUATE"]
bcr = 100 * ben / row_tot["INADEQUATE"]

r0_adeq, fin_adeq = row_tot["ADEQUATE"], col_tot["ADEQUATE"]
pct_r0, pct_fin = 100 * r0_adeq / N, 100 * fin_adeq / N
drop = pct_r0 - pct_fin
net_runs = fin_adeq - r0_adeq
off_diag = sum(v for (a, b), v in M.items() if a != b)
stance_changed = sum(1 for r in runs if r["round0_drug"] != r["final_A"])
pct_stance = 100 * stance_changed / N

harm_dest = Counter(r["final_A"] for r in runs
                    if r["round0_outcome"] == "ADEQUATE" and r["final_A_outcome"] == "INADEQUATE")
dest_txt = ", ".join(f"{d} on {n}" for d, n in harm_dest.most_common())

# ------------------------------------------------------------------- stdout log
print(f"F8  source: {RUNS.relative_to(ROOT)}  (kind=='full', not quarantined)")
print(f"  ordering-runs {N}   paired cases {N_CASES}")
print("\n  TRANSITION MATRIX  round-0 outcome (rows) -> final position, agent A (cols)")
head = " ".join(f"{c[:12]:>13}" for c in CATS)
print(f"  {'':<18}{head}{'row n':>10}")
for a in CATS:
    cells = " ".join(f"{M[(a, b)]:>13}" for b in CATS)
    print(f"  {a:<18}{cells}{row_tot[a]:>10}")
print(f"  {'col n':<18}" + " ".join(f"{col_tot[b]:>13}" for b in CATS) + f"{N:>10}")
print(f"\n  diagonal (unchanged class)   {N - off_diag} / {N} = {100*(N-off_diag)/N:.1f}%")
print(f"  off-diagonal (class changed) {off_diag} / {N} = {100*off_diag/N:.1f}%")
print(f"  round-0 ADEQUATE  {r0_adeq}/{N} = {pct_r0:.1f}%")
print(f"  final-A  ADEQUATE {fin_adeq}/{N} = {pct_fin:.1f}%   net {net_runs:+d} runs = {-drop:+.1f} points")
print(f"  HRR  P(final INADEQUATE | round-0 ADEQUATE)   = {harm}/{r0_adeq} = {hrr:.1f}%")
print(f"  BCR  P(final ADEQUATE | round-0 INADEQUATE)   = {ben}/{row_tot['INADEQUATE']} = {bcr:.1f}%")
print(f"  stance-change rate (round0_drug != final_A)   = {stance_changed}/{N} = {pct_stance:.1f}%")
print(f"  harmful revisions land on: {dest_txt}")

# ----------------------------------------------------------------------- geometry
COL_X = [19.0, 39.0, 48.9, 58.8]     # left edge of each column; gap after col 0 = channel
COL_W = 9.0
CH_L, CH_R = 28.0, 39.0              # the channel separating ADEQUATE from the rest
ROW_TOP, ROW_H, ROW_GAP = 92.0, 16.4, 1.5
ROW_Y = [ROW_TOP - i * (ROW_H + ROW_GAP) for i in range(4)]   # top edge of each row
LEDGER_X = 74.0

fig, ax = S.new_figure("full")
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
ax.grid(False)

max_plain = max([M[(a, b)] for a in CATS for b in CATS
                 if a != b and (a, b) != ("ADEQUATE", "INADEQUATE")] + [1])

for i, a in enumerate(CATS):
    ytop = ROW_Y[i]
    for j, b in enumerate(CATS):
        n = M[(a, b)]
        x = COL_X[j]
        if (a, b) == ("ADEQUATE", "INADEQUATE"):
            fc, alpha, tc, tw = S.ACCENT, 1.0, S.WHITE, "bold"
        elif a == b:
            fc, alpha, tc, tw = S.MUTED, 0.16, S.INK, "normal"
        elif n == 0:
            fc, alpha, tc, tw = S.BG, 1.0, S.MUTED, "normal"
        else:
            fc, alpha, tc, tw = S.PRIMARY, 0.10 + 0.38 * (n / max_plain), S.INK, "normal"
        ax.add_patch(Rectangle((x, ytop - ROW_H), COL_W, ROW_H, facecolor=fc,
                               alpha=alpha, edgecolor="none", zorder=2))
        ax.text(x + COL_W / 2, ytop - ROW_H / 2, f"{n}", ha="center", va="center",
                color=tc, fontsize=13.5, fontweight=tw, fontfamily=MONO, zorder=3,
                alpha=0.5 if n == 0 else 1.0)

    # row label: the category, and the denominator the row rate conditions on
    ax.text(17.5, ytop - ROW_H / 2 + 1.6, SHORT[a].replace("\n", " "), ha="right", va="center",
            color=S.INK, fontsize=10.5)
    ax.text(17.5, ytop - ROW_H / 2 - 3.4, f"n = {row_tot[a]}", ha="right", va="center",
            color=S.MUTED, fontsize=9, fontfamily=MONO)

# column labels beneath, carrying the final-position totals
for j, b in enumerate(CATS):
    ax.text(COL_X[j] + COL_W / 2, 16.5, SHORT[b], ha="center", va="top",
            color=S.INK, fontsize=10.5, linespacing=1.25)
    ax.text(COL_X[j] + COL_W / 2, 5.0, f"n = {col_tot[b]}", ha="center", va="top",
            color=S.MUTED, fontsize=9, fontfamily=MONO)

ax.text(43.4, 97.0, "FINAL POSITION, AGENT A", ha="center", va="center",
        color=S.MUTED, fontsize=9, fontfamily=MONO)
ax.text(1.0, ROW_Y[0] - (ROW_TOP - ROW_Y[3] + ROW_H) / 2, "ROUND-0 OUTCOME",
        ha="center", va="center", color=S.MUTED, fontsize=9, fontfamily=MONO, rotation=90)

# ------------------------------------------------- the two rates, drawn as arrows
cx = (CH_L + CH_R) / 2


def flow_arrow(y, n, color, rightward=True):
    lw = 1.1 + 4.4 * (n / max(harm, 1))
    x0, x1 = (CH_L + 1.4, CH_R - 1.4) if rightward else (CH_R - 1.4, CH_L + 1.4)
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=15 + 6 * (n / max(harm, 1)),
                                shrinkA=0, shrinkB=0), zorder=4)


# HRR: adequate at round 0, inadequate at the end. The one number the claim is about.
r0c = ROW_Y[0] - ROW_H / 2
S.annotate_key(ax, cx, r0c + 5.4, f"HRR {hrr:.1f}%", ha="center", va="center", fontsize=12.5)
flow_arrow(r0c + 0.4, harm, S.ACCENT, rightward=True)
ax.text(cx, r0c - 4.8, f"{harm} of {r0_adeq}", ha="center", va="center",
        color=S.MUTED, fontsize=9, fontfamily=MONO)

# BCR: the traffic in the other direction, an order of magnitude thinner
r1c = ROW_Y[1] - ROW_H / 2
S.direct_label(ax, cx, r1c + 5.4, f"BCR {bcr:.1f}%", color=S.PRIMARY, ha="center",
               va="center", fontsize=12.5, fontweight="bold")
flow_arrow(r1c + 0.4, ben, S.PRIMARY, rightward=False)
ax.text(cx, r1c - 4.8, f"{ben} of {row_tot['INADEQUATE']}", ha="center", va="center",
        color=S.MUTED, fontsize=9, fontfamily=MONO)

ax.text(COL_X[0], -3.5, f"Where the harmful revisions land: {dest_txt}.",
        ha="left", va="center", color=S.MUTED, fontsize=9)

# ------------------------------------------------------------------- stat ledger
ax.plot([70.5, 70.5], [21.9, 92.0], color=S.GRID, lw=1.0, zorder=1)

blocks = [
    (f"−{drop:.1f} pts", "net change in the adequate rate",
     [f"{pct_r0:.1f}% at round 0 ({r0_adeq} of {N})",
      f"{pct_fin:.1f}% at the final position ({fin_adeq} of {N})"]),
    (f"{off_diag} of {N}", "runs that changed outcome class",
     [f"a net of \u2212{abs(net_runs)} runs is the residue",
      "of moves in both directions at once"]),
    (f"{pct_stance:.1f}%", "stance-change rate",
     [f"{stance_changed} of {N} ordering-runs left",
      "the round-0 drug behind"]),
]
for k, (big, lab, subs) in enumerate(blocks):
    ytop = 90.0 - k * 25.0
    ax.text(LEDGER_X, ytop, big, ha="left", va="center", color=S.INK,
            fontsize=20, fontweight="bold", fontfamily=MONO)
    ax.text(LEDGER_X, ytop - 7.2, lab, ha="left", va="center", color=S.INK, fontsize=10.5)
    for m, s in enumerate(subs):
        ax.text(LEDGER_X, ytop - 12.6 - 4.6 * m, s, ha="left", va="center",
                color=S.MUTED, fontsize=9.2)

# ----------------------------------------------------------------------- titling
S.kicker_title(
    fig,
    "direction of harm",
    f"A {drop:.1f}-point accuracy drop conceals {harm} harmful revisions and {ben} corrections.",
    "HRR, harmful revision rate = P(final INADEQUATE | round-0 ADEQUATE).   "
    "BCR, beneficial correction rate = P(final ADEQUATE | round-0 INADEQUATE).\n"
    f"{N} ordering-runs over {N_CASES} paired cases; both positions scored against the same "
    "microbiology S/I/R panel. 19 August 2026.",
)
fig.subplots_adjust(left=0.03, right=0.985, top=0.795, bottom=0.10)

row = S.save(fig, "F8", "transition_matrix", draft=True,
             source=f"{RUNS.relative_to(ROOT)} (kind=='full', n={N})",
             note="HRR/BCR definitions provisional pending ORDERS_2")
print(f"\n  wrote {row['png']}")
print(f"  wrote {row['svg']}")
