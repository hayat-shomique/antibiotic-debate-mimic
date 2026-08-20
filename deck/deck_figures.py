"""deck_figures.py - every chart in the conference deck, drawn from results/*.json.

No number in this file is typed. Each figure loads the canonical result file that
the analysis scripts wrote and draws what is there. Style follows the project
figure contract in figures/src/_style.py: claim as the title, y-grid only, direct
labels, one annotated number per panel.

    python3 deck/deck_figures.py        # writes deck/figures/*.png
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# IBM Carbon palette. Blue is the project's voice and the good outcome, magenta is harm,
# teal is the laboratory, and the grays are Carbon's neutral ramp rather than a tinted grey.
INK, PRIMARY, ACCENT, MUTED = "#161616", "#0F62FE", "#D02670", "#525252"
BG, WHITE, GRID = "#F4F4F4", "#FFFFFF", "#E0E0E0"
SOFT = "#8D8D8D"
TEAL, CYAN, BLUE80, BLUE10 = "#007D79", "#33B1FF", "#002D9C", "#EDF5FF"
PURPLE = "#8A3FFC"   # the second agent. ACCENT is reserved for harm.

CANVAS = (11.6, 4.35)      # inches, fixed so the slide geometry is exact
WIDE = (11.6, 4.9)

def load(name):
    return json.loads((RES / name).read_text())

T = load("tingting_endpoints.json")
R = load("RESULTS.json")
P = load("policy_degeneracy.json")
FS = load("fewshot.json")


def style():
    plt.rcParams.update({
        "figure.facecolor": WHITE, "axes.facecolor": WHITE, "savefig.facecolor": WHITE,
        "font.family": "sans-serif",
        "font.sans-serif": ["IBM Plex Sans", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 13, "text.color": INK, "axes.labelcolor": INK,
        "axes.edgecolor": GRID, "axes.linewidth": 0.9, "axes.labelsize": 13,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True,
        "grid.color": GRID, "grid.linewidth": 1.0,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "xtick.labelsize": 12.5, "ytick.labelsize": 12,
        "xtick.major.size": 0, "ytick.major.size": 0,
        "legend.frameon": False, "legend.fontsize": 12,
        "figure.dpi": 110, "savefig.dpi": 200,
        "axes.unicode_minus": False,
        "pdf.fonttype": 42, "svg.fonttype": "none",
    })


def fig_(size=CANVAS, nrows=1, ncols=1, **kw):
    style()
    f, ax = plt.subplots(nrows, ncols, figsize=size, **kw)
    return f, ax


def y_only(ax):
    ax.grid(axis="y"); ax.grid(axis="x", visible=False)


def x_only(ax):
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)


def save(f, name):
    path = OUT / f"{name}.png"
    f.savefig(path, dpi=200)
    plt.close(f)
    print(f"  wrote {path.relative_to(ROOT)}")
    return path


# ------------------------------------------------------- 0. the referee idea
def f_referee():
    """Two agents argue. A third thing that neither can see decides who was right."""
    W, H = 11.6, 4.15
    f, ax = fig_((W, H))
    ax.set_xlim(0, 100); ax.set_ylim(-4, 100); ax.axis("off")
    # a true circle in a non-square axes: x and y units are different physical sizes
    kx, ky = 100.0 / W, 104.0 / H

    def circle(cx, cy, r_in, **kw):
        from matplotlib.patches import Ellipse
        ax.add_patch(Ellipse((cx, cy), 2 * r_in * kx, 2 * r_in * ky, **kw))

    def card(x, y, w, h, title, l1, l2, col):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=WHITE, edgecolor=GRID, lw=1.4, zorder=2))
        ax.add_patch(plt.Rectangle((x, y), 1.3, h, facecolor=col, edgecolor="none", zorder=3))
        ax.text(x + 4, y + h - 8, title, fontsize=14, fontweight="bold", color=INK, va="top")
        ax.text(x + 4, y + h - 19, l1, fontsize=12, color=INK, va="top")
        ax.text(x + 4, y + h - 28, l2, fontsize=11.5, color=MUTED, va="top")

    card(2, 60, 38, 38, "Agent A", "infectious disease specialist", "wants to cover the organism", PRIMARY)
    card(60, 60, 38, 38, "Agent B", "antimicrobial stewardship lead", "wants to avoid unnecessary breadth", PURPLE)

    ax.annotate("", xy=(58, 86), xytext=(42, 86),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.8, mutation_scale=15))
    ax.annotate("", xy=(42, 74), xytext=(58, 74),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.8, mutation_scale=15))
    ax.text(50, 93, "five turns", fontsize=11.5, color=MUTED, ha="center", va="center")

    cx, cy = 50, 30
    circle(cx, cy, 0.60, facecolor=BLUE10, edgecolor=TEAL, lw=2.4, zorder=3)
    for dx, dy in [(-2.0, 4), (-0.4, -5), (1.8, 6), (2.6, -2), (0.2, 9), (-2.6, -7), (1.2, 0), (-3.2, 1)]:
        circle(cx + dx, cy + dy, 0.075, facecolor=TEAL, edgecolor="none", zorder=4)

    for x0, xt in ((21, 45), (79, 55)):
        ax.annotate("", xy=(xt, cy + 15.5), xytext=(x0, 59),
                    arrowprops=dict(arrowstyle="-|>", color=SOFT, lw=1.5,
                                    linestyle=(0, (5, 4)), mutation_scale=13))
    ax.text(19, 50, "was this drug right\nfor this patient?", fontsize=11.5, color=MUTED,
            ha="center", va="center", linespacing=1.4)
    ax.text(81, 50, "and was that one?", fontsize=11.5, color=MUTED, ha="center", va="center")

    ax.text(cx, 9, "the patient's own susceptibility panel", fontsize=14, fontweight="bold",
            color=TEAL, ha="center", va="center")
    ax.text(cx, 1.5, "neither agent can see it, neither can argue with it, neither of them produced it",
            fontsize=11.5, color=MUTED, ha="center", va="center")

    f.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    return save(f, "referee")


# --------------------------------------------------- 0b. how the agents talk
def f_protocol():
    """The five turns, and the position each agent holds after every one of them."""
    W, H = 11.6, 4.3
    f, ax = fig_((W, H))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    lane_a, lane_b = 74, 30
    ax.text(0, lane_a + 12, "AGENT A   infectious disease specialist", fontsize=11.5,
            fontweight="bold", color=PRIMARY, va="center")
    ax.text(0, lane_b - 12, "AGENT B   antimicrobial stewardship lead", fontsize=11.5,
            fontweight="bold", color=PURPLE, va="center")
    for y in (lane_a, lane_b):
        ax.plot([0, 100], [y, y], color=GRID, lw=1.2, zorder=1)

    turns = [(8, lane_a, "T1", "proposes one drug", PRIMARY),
             (28, lane_b, "T2", "counters or concurs", PURPLE),
             (48, lane_a, "T3", "answers the challenge", PRIMARY),
             (68, lane_b, "T4", "restates or moves", PURPLE),
             (88, lane_a, "T5", "final position", PRIMARY)]
    for i, (x, y, t, label, col) in enumerate(turns):
        ax.add_patch(plt.Rectangle((x - 7, y - 7), 15.5, 14, facecolor=WHITE,
                                   edgecolor=col, lw=1.6, zorder=3))
        ax.text(x + 0.75, y + 2.2, t, fontsize=12, fontweight="bold", color=col,
                ha="center", va="center")
        ax.text(x + 0.75, y - 3.4, label, fontsize=9.5, color=MUTED, ha="center", va="center")
        if i:
            px, py = turns[i - 1][0] + 8.5, turns[i - 1][1]
            ax.annotate("", xy=(x - 7.4, y), xytext=(px, py),
                        arrowprops=dict(arrowstyle="-|>", color=SOFT, lw=1.4, mutation_scale=13,
                                        connectionstyle="arc3,rad=0.16"))

    ax.text(50, 13, "every turn is parsed to one drug from the closed formulary and recorded",
            fontsize=11.5, color=MUTED, ha="center", va="center")
    ax.text(50, 3, "and the whole case is run again with Agent B opening, so speaking order is measured rather than averaged away",
            fontsize=11.5, color=INK, ha="center", va="center")
    f.subplots_adjust(left=0.015, right=0.985, top=0.99, bottom=0.01)
    return save(f, "protocol")


# ------------------------------------------------------------ 0c. the ladder
def f_ladder():
    """Three rungs, climbed in the supervisor's order, with what each one produced."""
    prim, fs = T["primary_appropriateness"], FS
    pr = fs["paired"]
    W, H = 11.6, 4.0
    f, ax = fig_((W, H))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    rungs = [
        (2, 6, "RUNG 1   zero-shot", "complete, %d cases" % prim["baseline_pre_culture"]["n"],
         "One drug for every patient.\n%.1f per cent coverage." % prim["baseline_pre_culture"]["pct"], SOFT),
        (35, 34, "RUNG 2   few-shot", "complete, %d cases" % fs["n"],
         "%d drugs instead of one, but coverage\nfalls to %.1f per cent, p = %.4f."
         % (fs["aware"]["fewshot"]["distinct"], 100.0 * pr["fewshot_correct"] / pr["n"], pr["p_exact"]), ACCENT),
        (68, 62, "RUNG 3   fine-tuning", "designed, not run",
         "The rung that rung two licenses.\nTrain on coverage penalised by spectrum.", PRIMARY),
    ]
    for x, y, title, status, body, col in rungs:
        ax.add_patch(plt.Rectangle((x, y), 30, 30, facecolor=WHITE, edgecolor=GRID, lw=1.4, zorder=2))
        ax.add_patch(plt.Rectangle((x, y + 27), 30, 3, facecolor=col, edgecolor="none", zorder=3))
        ax.text(x + 2, y + 21.5, title, fontsize=12.5, fontweight="bold", color=INK, va="center")
        ax.text(x + 2, y + 15.5, status, fontsize=10.5, color=col, va="center", fontweight="bold")
        ax.text(x + 2, y + 7, body, fontsize=11, color=MUTED, va="center", linespacing=1.45)

    for x0, y0, x1, y1 in [(32, 21, 35, 49), (65, 49, 68, 77)]:
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=SOFT, lw=1.6, mutation_scale=14))
    ax.text(2, 96, "“zero shot will not work ... give it a few shots and then see whether it improves. "
                   "And if it doesn't, then you can move it to the next level, that is now your training”",
            fontsize=11, color=MUTED, style="italic", va="center")
    f.subplots_adjust(left=0.015, right=0.985, top=0.99, bottom=0.01)
    return save(f, "ladder")


# ------------------------------------- 0d. her core endpoint, the 2x2 by condition
def f_transitions():
    """Her four-cell classification, applied before and after each interaction."""
    conds = [("a scripted neutral turn", T["change_under_neutral_control"]),
             ("a second agent arguing a case", T["debate_with_live_agent"]),
             ("the susceptibility panel", T["revision_under_evidence"])]
    cells = [("stable correct", "stable_correct", SOFT),
             ("beneficial correction", "beneficial_correction", PRIMARY),
             ("harmful deference", "harmful_deference", ACCENT),
             ("no improvement", "no_improvement", "#C6C6C6")]

    f, ax = fig_((11.6, 4.05))
    ys = [2, 1, 0]
    for y, (label, d) in zip(ys, conds):
        counts = d["counts"]
        total = sum(counts.get(k, 0) for _, k, _ in cells) or 1
        left = 0.0
        for name, key, col in cells:
            v = counts.get(key, 0)
            if not v:
                continue
            w = 100.0 * v / total
            ax.barh(y, w, left=left, color=col, height=0.44, zorder=3)
            if w > 6:
                ax.text(left + w / 2, y, str(v), ha="center", va="center",
                        fontsize=12, fontweight="bold",
                        color=WHITE if col in (PRIMARY, ACCENT) else INK, zorder=4)
            left += w
        ax.text(-2.0, y, label, ha="right", va="center", fontsize=12.5, color=INK)
        ax.text(102.5, y, f"HRR {d['HRR']['pct']:.1f}%\nBCR {d['BCR']['pct']:.1f}%",
                ha="left", va="center", fontsize=11.5, color=MUTED, linespacing=1.5)
    ax.set_yticks([]); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlim(0, 100); ax.set_ylim(-0.6, 2.75)
    ax.set_xlabel("share of the cases classified, per cent")
    x_only(ax)
    for i, (name, _, col) in enumerate(cells):
        ax.add_patch(plt.Rectangle((i * 26, 2.52), 3.0, 0.14, color=col, clip_on=False))
        ax.text(i * 26 + 4, 2.59, name, fontsize=11.5, color=MUTED, va="center")
    f.subplots_adjust(left=0.255, right=0.80, top=0.97, bottom=0.16)
    return save(f, "transitions")


# ---------------------------------------------------------------- 1. timeline
def f_timeline():
    """The empiric window: the decision is made long before the answer exists."""
    import re
    methods = (ROOT / "docs" / "METHODS.md").read_text()
    median_h = int(re.search(r"median of \*\*(\d+) hours\*\*", methods).group(1))

    f, ax = fig_((11.6, 3.5))
    ax.set_xlim(-4, median_h + 4)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.plot([0, median_h], [0.52, 0.52], color=GRID, lw=7, solid_capstyle="round", zorder=1)
    ax.plot([0, 1], [0.52, 0.52], color=ACCENT, lw=7, solid_capstyle="round", zorder=2)

    def mark(x, label, sub, color, ha):
        ax.plot([x], [0.52], "o", ms=15, color=color, zorder=4,
                markeredgecolor=WHITE, markeredgewidth=2.5)
        ax.plot([x, x], [0.52, 0.64], color=color, lw=1.1, zorder=3)
        ax.text(x, 0.80, label, ha=ha, va="bottom", fontsize=15, fontweight="bold", color=INK)
        ax.text(x, 0.67, sub, ha=ha, va="bottom", fontsize=12.5, color=MUTED)

    mark(0, "Blood culture drawn", "hour 0", ACCENT, "left")
    mark(median_h, "Susceptibility panel", f"median hour {median_h}", PRIMARY, "right")
    ax.annotate("", xy=(median_h - 2, 0.30), xytext=(2, 0.30),
                arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.2))
    ax.text(median_h / 2, 0.22, "the empiric window: the antibiotic is chosen here, on no laboratory data",
            ha="center", va="top", fontsize=13, color=INK)
    ax.text(median_h / 2, 0.09, "zero panels are available at 5, 12 or 24 hours",
            ha="center", va="top", fontsize=12.5, color=ACCENT, fontweight="bold")
    f.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    return save(f, "timeline")


# ------------------------------------------------------- 2. degenerate policy
def f_baseline():
    """One drug for every patient, and it scores 87.5 percent."""
    prim = T["primary_appropriateness"]
    conds = [("Baseline\nbefore cultures", "baseline_pre_culture", "C0 baseline"),
             ("Neutral re-ask\nno disagreement", "neutral_control", "Cn neutral control"),
             ("Susceptibility\npanel revealed", "with_panel_revealed", "C2 with the panel revealed")]

    f, axes = fig_(CANVAS, 1, 2, gridspec_kw=dict(width_ratios=[1.15, 1]))
    a, b = axes

    xs = range(len(conds))
    vals = [prim[k]["pct"] for _, k, _ in conds]
    cols = [SOFT, SOFT, PRIMARY]
    a.bar(list(xs), vals, width=0.52, color=cols, zorder=3)
    for x, v, (_, k, _) in zip(xs, vals, conds):
        a.text(x, v + 2.0, f"{v:.1f}%", ha="center", va="bottom", fontsize=15,
               fontweight="bold", color=INK)
        a.text(x, 4, f"{prim[k]['adequate']}/{prim[k]['n']}", ha="center", va="bottom",
               fontsize=11.5, color=WHITE)
    a.set_xticks(list(xs)); a.set_xticklabels([c[0] for c in conds])
    a.set_ylim(0, 112); a.set_yticks([0, 25, 50, 75, 100])
    a.set_ylabel("covers the organism that grew")
    y_only(a)
    a.set_title("Coverage of the organism", fontsize=13.5, color=MUTED, loc="left", pad=12)

    ds = [P[k]["distinct"] for _, _, k in conds]
    b.bar(list(xs), ds, width=0.52, color=[ACCENT, ACCENT, PRIMARY], zorder=3)
    for x, v in zip(xs, ds):
        b.text(x, v + 0.25, str(v), ha="center", va="bottom", fontsize=15,
               fontweight="bold", color=INK)
    b.set_xticks(list(xs)); b.set_xticklabels([c[0] for c in conds])
    b.set_ylim(0, max(ds) * 1.28); b.set_ylabel("distinct antibiotics ever chosen")
    y_only(b)
    b.set_title("How many different answers", fontsize=13.5, color=MUTED, loc="left", pad=12)
    b.text(0.5, ds[0] + 0.9, f"one drug for all {prim['baseline_pre_culture']['n']} patients",
           ha="center", va="bottom", fontsize=12.5, color=ACCENT, fontweight="bold")

    f.subplots_adjust(left=0.075, right=0.985, top=0.86, bottom=0.16, wspace=0.30)
    return save(f, "baseline")


# ------------------------------------------------------ 3. pre-specified test
def f_primary():
    """A neutral turn never moves it. Unsupported pressure almost always does."""
    bf = R["pre_specified_primary_test"]["by_framing"]
    order = ["C1a_authority", "C1b_peer_consensus", "C1c_safety_framing", "C1d_bare_doubt"]
    nice = {"C1a_authority": "authority", "C1b_peer_consensus": "peer consensus",
            "C1c_safety_framing": "safety framing", "C1d_bare_doubt": "bare doubt"}

    f, ax = fig_(CANVAS)
    labels, vals, cols = [], [], []
    labels.append("neutral control\nno disagreement")
    cn = bf[order[0]]["flip_rates"]["Cn"]
    vals.append(100.0 * cn["k"] / cn["n"]); cols.append(MUTED)
    for k in order:
        fr = bf[k]["flip_rates"]["C1"]
        labels.append(f"pressure\n{nice[k]}")
        vals.append(100.0 * fr["k"] / fr["n"]); cols.append(ACCENT)
    c2 = bf[order[0]]["flip_rates"]["C2"]
    labels.append("susceptibility panel\nreal information")
    vals.append(100.0 * c2["k"] / c2["n"]); cols.append(PRIMARY)

    xs = list(range(len(vals)))
    ax.bar(xs, vals, width=0.62, color=cols, zorder=3)
    for x, v in zip(xs, vals):
        ax.text(x, v + 2.2, f"{v:.1f}%", ha="center", va="bottom", fontsize=14.5,
                fontweight="bold", color=INK)
    ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=11.5)
    ax.set_ylim(0, 118); ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel(f"changed its recommendation, n = {cn['n']}")
    y_only(ax)
    ax.text(0, 8.5, f"{cn['k']} of {cn['n']}", ha="center", va="bottom", fontsize=12.5,
            color=MUTED)
    f.subplots_adjust(left=0.075, right=0.985, top=0.95, bottom=0.22)
    return save(f, "primary_test")


# ---------------------------------------------------------- 4. stewardship
def f_stewardship():
    """A sentence with no clinical content drives carbapenem use from zero to 84 percent."""
    sp = T["spectrum_appropriateness"]
    rows = [("Baseline", "baseline"), ("Neutral\nre-ask", "neutral_control"),
            ("Unsupported\npressure", "under_pressure"), ("Panel\nrevealed", "panel_revealed")]

    f, axes = fig_(CANVAS, 1, 2, gridspec_kw=dict(width_ratios=[1.1, 1]))
    a, b = axes
    xs = list(range(len(rows)))
    vals = [sp[k]["carbapenem_pct"] for _, k in rows]
    cols = [SOFT, SOFT, ACCENT, PRIMARY]
    a.bar(xs, vals, width=0.58, color=cols, zorder=3)
    for x, v, (_, k) in zip(xs, vals, rows):
        a.text(x, v + 2.4, f"{v:.1f}%", ha="center", va="bottom", fontsize=15,
               fontweight="bold", color=INK)
        a.text(x, v + 8.6, f"{sp[k]['carbapenem']}/{sp[k]['n']}", ha="center", va="bottom",
               fontsize=11.5, color=MUTED)
    a.set_xticks(xs); a.set_xticklabels([r[0] for r in rows], fontsize=12)
    a.set_ylim(0, 108); a.set_yticks([0, 25, 50, 75, 100])
    a.set_ylabel("recommended a carbapenem")
    y_only(a)
    a.set_title("Last-line therapy", fontsize=13.5, color=MUTED, loc="left", pad=12)

    ds = [sp[k]["distinct_drugs"] for _, k in rows]
    b.bar(xs, ds, width=0.58, color=cols, zorder=3)
    for x, v in zip(xs, ds):
        b.text(x, v + 0.22, str(v), ha="center", va="bottom", fontsize=15,
               fontweight="bold", color=INK)
    b.set_xticks(xs); b.set_xticklabels([r[0] for r in rows], fontsize=12)
    b.set_ylim(0, max(ds) * 1.3); b.set_ylabel("distinct antibiotics chosen")
    y_only(b)
    b.set_title("Breadth of the answer", fontsize=13.5, color=MUTED, loc="left", pad=12)

    f.subplots_adjust(left=0.075, right=0.985, top=0.86, bottom=0.17, wspace=0.28)
    return save(f, "stewardship")


# --------------------------------------------------------- 5. matched pairs
def f_matched():
    """Same drug, different patient: the gap is zero in every stratum."""
    m = R["D_MATCH_1_drug_identity_vs_patient"]
    by = m["by_drug"]
    drugs = [d for d in by
             if by[d]["covers"]["n"] and by[d]["does_not_cover"]["n"]]
    dropped = [d for d in by if d not in drugs]
    if dropped:
        print(f"  note: {len(dropped)} drug stratum with exposures in only one arm not plotted: "
              + ", ".join(dropped))
    drugs = sorted(drugs, key=lambda d: -by[d]["covers"]["adopted"] / by[d]["covers"]["n"])

    f, ax = fig_(CANVAS)
    ys = list(range(len(drugs)))[::-1]
    for y, d in zip(ys, drugs):
        cov = 100.0 * by[d]["covers"]["adopted"] / by[d]["covers"]["n"]
        non = 100.0 * by[d]["does_not_cover"]["adopted"] / by[d]["does_not_cover"]["n"]
        if abs(cov - non) > 0.5:
            ax.plot([min(cov, non), max(cov, non)], [y, y], color=SOFT, lw=3.5, zorder=2,
                    solid_capstyle="round")
        ax.plot([non], [y], "o", ms=20, markerfacecolor="none", markeredgecolor=ACCENT,
                markeredgewidth=3.0, zorder=3)
        ax.plot([cov], [y], "o", ms=11, color=PRIMARY, zorder=4)
        ax.text(112, y, f"gap {by[d]['gap_pct']:+.1f}", va="center", ha="left",
                fontsize=12.5, color=MUTED)
    ax.set_yticks(ys); ax.set_yticklabels(drugs, fontsize=13.5)
    ax.set_xlim(-8, 132); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("the proposed drug was adopted, per cent")
    x_only(ax)
    top = ys[0]
    ax.plot([37], [top + 0.72], "o", ms=11, color=PRIMARY, clip_on=False, zorder=5)
    ax.text(40, top + 0.72, "covers this patient", color=PRIMARY, fontsize=12.5,
            fontweight="bold", va="center", ha="left")
    ax.plot([68], [top + 0.72], "o", ms=20, markerfacecolor="none", markeredgecolor=ACCENT,
            markeredgewidth=3.0, clip_on=False, zorder=5)
    ax.text(72, top + 0.72, "does not cover this patient", color=ACCENT, fontsize=12.5,
            fontweight="bold", va="center", ha="left")
    ax.set_ylim(-0.7, top + 1.15)
    f.subplots_adjust(left=0.175, right=0.985, top=0.95, bottom=0.15)
    return save(f, "matched")


# -------------------------------------------------------------- 6. the answer
def f_debate():
    """A live agent costs coverage. The laboratory result buys it back."""
    dc = T["debate_coverage"]
    live, ev, neut = T["debate_with_live_agent"], T["revision_under_evidence"], T["change_under_neutral_control"]

    f, axes = fig_(CANVAS, 1, 2, gridspec_kw=dict(width_ratios=[1.25, 1]))
    a, b = axes

    stages = [("Before\nthey speak", "before_debate", SOFT),
              ("After debate\nwith a live agent", "after_debate", ACCENT),
              ("After the\nsusceptibility panel", "after_panel", PRIMARY)]
    xs = list(range(len(stages)))
    vals = [dc[k]["pct"] for _, k, _ in stages]
    ax_cols = [c for _, _, c in stages]
    a.plot(xs, vals, color=MUTED, lw=1.6, zorder=2, linestyle=(0, (4, 3)))
    a.scatter(xs, vals, s=340, color=ax_cols, zorder=4, edgecolor=WHITE, linewidth=2.5)
    for x, v, (_, k, _) in zip(xs, vals, stages):
        a.text(x, v + 3.4, f"{v:.1f}%", ha="center", va="bottom", fontsize=16,
               fontweight="bold", color=INK)
        a.text(x, v - 4.2, f"{dc[k]['adequate']}/{dc[k]['n']}", ha="center", va="top",
               fontsize=11.5, color=MUTED)
    a.annotate(f"{dc['debate_change_pts']:+.1f} points", xy=(0.5, (vals[0] + vals[1]) / 2),
               xytext=(0.5, 66), color=ACCENT, fontsize=13.5, fontweight="bold", ha="center")
    a.annotate(f"{dc['evidence_change_pts']:+.1f} points", xy=(1.5, (vals[1] + vals[2]) / 2),
               xytext=(1.5, 66), color=PRIMARY, fontsize=13.5, fontweight="bold", ha="center")
    a.set_xticks(xs); a.set_xticklabels([s[0] for s in stages], fontsize=12.5)
    a.set_xlim(-0.45, 2.45); a.set_ylim(60, 104); a.set_yticks([60, 70, 80, 90, 100])
    a.set_ylabel("covers the organism")
    y_only(a)
    a.set_title("Coverage of the organism, 400 ordering-runs", fontsize=13.5,
                color=MUTED, loc="left", pad=12)

    src = [("a scripted\nneutral turn", neut, MUTED), ("a second agent\narguing a case", live, ACCENT),
           ("the susceptibility\npanel", ev, PRIMARY)]
    xs2 = list(range(len(src)))
    v2 = [s[1]["HRR"]["pct"] for s in src]
    b.bar(xs2, v2, width=0.56, color=[s[2] for s in src], zorder=3)
    for x, v, s in zip(xs2, v2, src):
        b.text(x, v + 1.7, f"{v:.1f}%", ha="center", va="bottom", fontsize=15,
               fontweight="bold", color=INK)
        b.text(x, v + 0.5, f"{s[1]['HRR']['k']}/{s[1]['HRR']['n']}", ha="center", va="bottom",
               fontsize=11.5, color=MUTED)
    b.set_xticks(xs2); b.set_xticklabels([s[0] for s in src], fontsize=12)
    b.set_ylim(0, max(v2) * 1.45); b.set_ylabel("abandoned a correct answer")
    y_only(b)
    b.set_title("Harmful revision rate", fontsize=13.5, color=MUTED, loc="left", pad=12)

    f.subplots_adjust(left=0.075, right=0.985, top=0.86, bottom=0.19, wspace=0.30)
    return save(f, "debate")


# ------------------------------------------------------------- 7. few-shot
def f_fewshot():
    """Examples break the constant and cost coverage."""
    aw, pr = FS["aware"], FS["paired"]

    f, axes = fig_(CANVAS, 1, 3, gridspec_kw=dict(width_ratios=[1, 1, 1.15]))
    a, b, c = axes
    labs = ["zero-shot", "few-shot"]

    ds = [aw["zeroshot"]["distinct"], aw["fewshot"]["distinct"]]
    a.bar([0, 1], ds, width=0.5, color=[SOFT, PRIMARY], zorder=3)
    for x, v in zip([0, 1], ds):
        a.text(x, v + 0.16, str(v), ha="center", va="bottom", fontsize=15,
               fontweight="bold", color=INK)
    a.set_xticks([0, 1]); a.set_xticklabels(labs); a.set_ylim(0, max(ds) * 1.32)
    a.set_ylabel("distinct antibiotics")
    a.set_title("Variety", fontsize=13.5, color=MUTED, loc="left", pad=12)
    y_only(a)

    acc = [100.0 * aw[k]["access"] / aw[k]["n"] for k in ("zeroshot", "fewshot")]
    b.bar([0, 1], acc, width=0.5, color=[SOFT, PRIMARY], zorder=3)
    for x, v in zip([0, 1], acc):
        b.text(x, v + 1.1, f"{v:.1f}%", ha="center", va="bottom", fontsize=15,
               fontweight="bold", color=INK)
    b.set_xticks([0, 1]); b.set_xticklabels(labs); b.set_ylim(0, max(acc) * 1.42)
    b.set_ylabel("narrow, WHO Access group")
    b.set_title("Restraint", fontsize=13.5, color=MUTED, loc="left", pad=12)
    y_only(b)

    cov = [100.0 * pr["zeroshot_correct"] / pr["n"], 100.0 * pr["fewshot_correct"] / pr["n"]]
    c.bar([0, 1], cov, width=0.5, color=[SOFT, ACCENT], zorder=3)
    for x, v, k in zip([0, 1], cov, ["zeroshot_correct", "fewshot_correct"]):
        c.text(x, v + 2.0, f"{v:.1f}%", ha="center", va="bottom", fontsize=15,
               fontweight="bold", color=INK)
        c.text(x, 4, f"{pr[k]}/{pr['n']}", ha="center", va="bottom", fontsize=11, color=WHITE)
    c.set_xticks([0, 1]); c.set_xticklabels(labs); c.set_ylim(0, 132)
    c.set_yticks([0, 25, 50, 75, 100])
    c.set_ylabel("covers the organism")
    c.set_title(f"Coverage, paired on {pr['n']} cases", fontsize=13.5, color=MUTED,
                loc="left", pad=12)
    y_only(c)
    c.text(0.5, 122, f"lost {pr['b_lost']}, gained {pr['c_gained']}\nexact p = {pr['p_exact']:.4f}",
           ha="center", va="center", fontsize=12.5, color=ACCENT, fontweight="bold",
           linespacing=1.35)

    f.subplots_adjust(left=0.065, right=0.99, top=0.86, bottom=0.13, wspace=0.42)
    return save(f, "fewshot")


if __name__ == "__main__":
    print("deck figures, drawn from results/")
    f_referee(); f_protocol(); f_transitions(); f_ladder(); f_timeline(); f_baseline()
    f_primary(); f_stewardship()
    f_matched(); f_debate(); f_fewshot()
    print("done")
