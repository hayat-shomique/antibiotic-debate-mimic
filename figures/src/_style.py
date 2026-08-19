"""_style.py - the figure style contract from ORDERS_0. Every figure imports this.

Palette, rcParams, the kicker/claim-title block, the single-number annotation
layer, the DRAFT watermark, and the dual PNG+SVG export. Nothing here reads data;
figures read their own data from disk and hand it in.

Rules this file enforces so individual figures cannot drift:
  - the title states the CLAIM, not the topic
  - light y-grid only, no top or right spine, no chartjunk
  - direct labels preferred; a legend is opt-in and deliberate
  - PNG at 200 dpi and SVG, both, every time
  - a figure whose numbers are not final carries a DRAFT watermark
"""
from __future__ import annotations

import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

FIG_DIR = Path(__file__).resolve().parent.parent          # brain_run/figures
ROOT = FIG_DIR.parent                                      # brain_run

INK      = "#12303F"
PRIMARY  = "#1C7293"
ACCENT   = "#C64B3E"
MUTED    = "#6B7C85"
BG       = "#F4F7F8"
WHITE    = "#FFFFFF"
GRID     = "#DCE4E8"
PALETTE  = dict(ink=INK, primary=PRIMARY, accent=ACCENT, muted=MUTED, bg=BG, white=WHITE, grid=GRID)

# a sequence for the rare case where more than two marks must be distinguished,
# built by desaturating toward the muted tone rather than adding new hues
SEQ = [PRIMARY, ACCENT, MUTED, "#4A93AC", "#D98276", "#95A5AC"]

HALF = (9.0, 5.0)     # 16:9 slide half
FULL = (12.0, 6.0)    # 16:9 slide full

_FONT_STACK = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]
_MONO_STACK = ["SF Mono", "Menlo", "DejaVu Sans Mono"]


def _available(stack):
    have = {f.name for f in font_manager.fontManager.ttflist}
    return [f for f in stack if f in have] or ["DejaVu Sans"]


def apply():
    """Custom rcParams. Called by new_figure; call directly only if you need it early."""
    plt.rcParams.update({
        "figure.facecolor": WHITE,
        "axes.facecolor": WHITE,
        "savefig.facecolor": WHITE,
        "font.family": "sans-serif",
        "font.sans-serif": _available(_FONT_STACK),
        "font.size": 11.5,
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": GRID,
        "axes.linewidth": 0.9,
        "axes.labelsize": 11.5,
        "axes.titlesize": 13,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "grid.alpha": 1.0,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
        "legend.fontsize": 10.5,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.28,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    })


def new_figure(size="half", nrows=1, ncols=1, **kw):
    """Returns (fig, ax|axes). size is 'half' (9x5) or 'full' (12x6), or a tuple."""
    apply()
    fs = HALF if size == "half" else FULL if size == "full" else size
    fig, ax = plt.subplots(nrows, ncols, figsize=fs, **kw)
    return fig, ax


def grid_y_only(ax):
    ax.grid(axis="y", which="major")
    ax.grid(axis="x", visible=False)


def grid_x_only(ax):
    ax.grid(axis="x", which="major")
    ax.grid(axis="y", visible=False)


def kicker_title(fig, kicker: str, claim: str, sub: str | None = None, y=0.985):
    """Kicker in accent caps, then a declarative sentence stating the claim.

    The claim is the title. 'The lab tests what the Gram stain suggests', not
    'Panel coverage analysis'. If you find yourself writing a noun phrase, the
    figure does not yet know what it is arguing.
    """
    fig.text(0.012, y, kicker.upper(), color=ACCENT, fontsize=10,
             fontweight="bold", va="top", ha="left",
             fontfamily=_available(_MONO_STACK)[0], linespacing=1.0)
    fig.text(0.012, y - 0.055, claim, color=INK, fontsize=16.5,
             fontweight="bold", va="top", ha="left", wrap=True)
    if sub:
        fig.text(0.012, y - 0.115, sub, color=MUTED, fontsize=11, va="top", ha="left")


def annotate_key(ax, x, y, text, color=ACCENT, ha="left", va="center",
                 arrow_to=None, fontsize=12, weight="bold"):
    """The annotation layer for the ONE number that matters. Use once per figure."""
    if arrow_to is not None:
        ax.annotate(text, xy=arrow_to, xytext=(x, y), color=color, fontsize=fontsize,
                    fontweight=weight, ha=ha, va=va,
                    arrowprops=dict(arrowstyle="-", color=color, lw=1.2,
                                    shrinkA=2, shrinkB=4,
                                    connectionstyle="angle3,angleA=0,angleB=70"))
    else:
        ax.text(x, y, text, color=color, fontsize=fontsize, fontweight=weight,
                ha=ha, va=va, transform=ax.transData)


def direct_label(ax, x, y, text, color=INK, ha="left", va="center", fontsize=10.5, **kw):
    """Label a mark directly. Preferred over any legend."""
    ax.text(x, y, text, color=color, ha=ha, va=va, fontsize=fontsize, **kw)


def watermark_draft(fig, note="DRAFT"):
    """Diagonal watermark for any figure whose numbers are not final."""
    fig.text(0.5, 0.5, note, fontsize=86, color=ACCENT, alpha=0.10,
             ha="center", va="center", rotation=28, fontweight="bold", zorder=1000)


def footer(fig, text):
    fig.text(0.012, 0.012, text, color=MUTED, fontsize=8.6, va="bottom", ha="left")


def save(fig, fid: str, name: str, draft: bool = False, source: str = "",
         note: str = "") -> dict:
    """Export PNG at 200 dpi and SVG. Returns a manifest row."""
    if draft:
        watermark_draft(fig)
    stamp = time.strftime("%d %b %Y %H:%M")
    foot = f"{fid} · generated {stamp} from {source}" if source else f"{fid} · generated {stamp}"
    if note:
        foot += f" · {note}"
    if draft:
        foot += " · DRAFT, numbers not final"
    footer(fig, foot)
    FIG_DIR.mkdir(exist_ok=True)
    stem = f"{fid.lower()}_{name}"
    png = FIG_DIR / f"{stem}.png"
    svg = FIG_DIR / f"{stem}.svg"
    fig.savefig(png, dpi=200)
    fig.savefig(svg)
    plt.close(fig)
    return dict(id=fid, name=name, png=str(png.relative_to(ROOT)),
                svg=str(svg.relative_to(ROOT)), draft=draft, source=source)


def selftest():
    """Renders a swatch so the contract can be eyeballed without any data."""
    fig, ax = new_figure("half")
    for i, (k, c) in enumerate([("ink", INK), ("primary", PRIMARY), ("accent", ACCENT),
                                ("muted", MUTED), ("grid", GRID)]):
        ax.barh(i, 1, color=c, height=0.62)
        direct_label(ax, 1.03, i, f"{k}  {c}", color=INK)
    ax.set_yticks([]); ax.set_xticks([]); ax.set_xlim(0, 2.1)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    kicker_title(fig, "style contract", "The palette, fixed for every figure in the set.",
                 "ORDERS_0. Kicker in accent caps, claim as the title, direct labels, y-grid only.")
    fig.subplots_adjust(top=0.72)
    return save(fig, "F0", "style_swatch", draft=False, source="no data, contract check")


if __name__ == "__main__":
    r = selftest()
    print(f"  style contract OK -> {r['png']} and {r['svg']}")
    print(f"  fonts available: {_available(_FONT_STACK)[0]} / {_available(_MONO_STACK)[0]}")
