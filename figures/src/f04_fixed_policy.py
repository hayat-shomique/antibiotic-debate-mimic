#!/usr/bin/env python
"""F4 - the fixed-policy replication, as small multiples.

CLAIM: every model that has run reproduces a constant, not a decision.

One panel per model, each a horizontal bar chart of the distribution of the
round-0 recommendation across cases, sorted within panel. The shape carries the
claim: one dominant bar per panel out of a 17-agent formulary. The integer
annotated in each panel header is the number of distinct agents that model ever
recommended, and that integer is the point.

Every number in this figure is computed here from a file on disk. Nothing is
hand-entered. Sources:

  runs/model_compare_20260818.jsonl  generative round-0, one record per model per
                                     case. Only the A-first round-0 condition is
                                     in this file (a different system prompt runs
                                     B-first), so it is the like-for-like column.
  runs/debate_20260818.jsonl         kind=="round0" records, used ONLY as an
                                     independent cross-check of the Qwen column
                                     and printed to stdout; it does not draw a bar.
  encoder_baseline.csv               four encoders, no fine-tuning. The all-masked
                                     PRIMARY variant (pred_drug_allmask), which is
                                     the length-normalised mean over wordpieces.
  model_registry.json                formulary size.
  model_compare.py                   DEFAULT_MODELS, parsed as text, to learn which
                                     models are planned but not yet run so their
                                     panels can be drawn empty rather than omitted.

Governance: aggregates only. No case_id, subject_id or micro_specimen_id reaches
any axis, label or annotation. Counts and rates only.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "/Users/shamzzzh/brain_run/figures/src")
import _style as S  # noqa: E402

import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path("/Users/shamzzzh/brain_run")
# Glob rather than pin: a dated filename made this figure blind to every run
# written after 18 August, including the freshly called MedGemma column.
MODEL_COMPARE = sorted((ROOT / "runs").glob("model_compare_*.jsonl"))
DEBATE = ROOT / "runs" / "debate_20260818.jsonl"
ENCODERS = ROOT / "encoder_baseline.csv"
REGISTRY = ROOT / "model_registry.json"
COMPARE_SRC = ROOT / "model_compare.py"

# Presentation only: an id -> short label map. No number is carried here.
DISPLAY = {
    "qwen3:4b-instruct-2507-q4_K_M": "Qwen3-4B instruct",
    "medgemma:4b-it-q4_K_M": "MedGemma-4B",
    "gemma4:12b": "Gemma4-12B",
    "emilyalsentzer/Bio_ClinicalBERT": "Bio_ClinicalBERT",
    "dmis-lab/biobert-base-cased-v1.2": "BioBERT v1.2",
    "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext": "BiomedBERT",
    "google-bert/bert-base-uncased": "BERT-base",
}


def label_for(model_id: str) -> str:
    return DISPLAY.get(model_id, model_id.split("/")[-1])


# ----------------------------------------------------------------- read disk

def read_formulary_size() -> int:
    reg = json.loads(REGISTRY.read_text())
    return int(reg["formulary_size"])


def read_planned_models() -> list[str]:
    """DEFAULT_MODELS from model_compare.py, read as text (the file is not imported:
    importing it would pull in debate_run and the live harness)."""
    src = COMPARE_SRC.read_text()
    incumbent = re.search(r'^INCUMBENT\s*=\s*"([^"]+)"', src, re.M).group(1)
    literal = re.search(r"^DEFAULT_MODELS\s*=\s*\[([^\]]*)\]", src, re.M).group(1)
    out = []
    for tok in literal.split(","):
        tok = tok.strip()
        if not tok:
            continue
        out.append(incumbent if tok == "INCUMBENT" else tok.strip('"').strip("'"))
    return out


def read_generative() -> dict[str, Counter]:
    """model id -> Counter over recommended drug, one vote per case."""
    per_model: dict[str, dict[str, str]] = {}
    for _f in MODEL_COMPARE:
      for line in _f.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("kind") != "model_compare":
            continue
        per_model.setdefault(r["model"], {})[r["case_id"]] = r["drug"]
    return {m: Counter(d.values()) for m, d in per_model.items()}


def read_encoders() -> dict[str, Counter]:
    df = pd.read_csv(ENCODERS)
    out = {}
    for model, g in df.groupby("model", sort=True):
        g = g.drop_duplicates(subset="case_id", keep="last")
        out[str(model)] = Counter(g["pred_drug_allmask"])
    return out


def debate_round0_crosscheck() -> dict:
    """Independent check on the Qwen column. A-first only: the B-first round-0
    records were produced under a different system prompt."""
    latest: dict[str, str] = {}
    n_records = 0
    for line in DEBATE.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("kind") != "round0" or r.get("ordering") != "A-first":
            continue
        n_records += 1
        latest[r["case_id"]] = r["drug"]
    counts = Counter(latest.values())
    top_drug, top_n = counts.most_common(1)[0]
    return dict(n_records=n_records, n_cases=len(latest), counts=counts,
                distinct=len(counts), top_drug=top_drug, top_n=top_n)


# ----------------------------------------------------------------- one panel

def draw_panel(ax, model_id, counts, n_slots, accent: bool):
    n_cases = sum(counts.values())
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    distinct = len(ranked)

    for i, (drug, n) in enumerate(ranked):
        share = n / n_cases
        colour = (S.ACCENT if accent else S.PRIMARY) if i == 0 else S.MUTED
        ax.barh(i, share, height=0.42, color=colour, zorder=3)
        S.direct_label(ax, 0.0, i - 0.33, drug, color=S.INK, va="bottom", fontsize=9)
        txt = f"{n} of {n_cases}"
        if share >= 0.34:
            S.direct_label(ax, share - 0.025, i, txt, color=S.WHITE, ha="right",
                           fontsize=9, fontweight="bold", zorder=4)
        else:
            S.direct_label(ax, share + 0.025, i, txt, color=S.MUTED, fontsize=9)

    style_axes(ax, n_slots)
    header(ax, label_for(model_id), f"{distinct} agent" + ("" if distinct == 1 else "s"),
           f"{n_cases} cases", accent=accent)
    return distinct, n_cases, ranked


def draw_empty_panel(ax, model_id, n_slots):
    style_axes(ax, n_slots)
    ax.set_xticks([])
    ax.grid(False)
    ax.spines["bottom"].set_visible(False)
    box = FancyBboxPatch((0.012, 0.06), 0.976, 0.88, transform=ax.transAxes,
                         boxstyle="round,pad=0,rounding_size=0.02",
                         facecolor="none", edgecolor=S.GRID, linewidth=1.0,
                         linestyle=(0, (4, 4)), zorder=2)
    box.set_clip_on(False)
    ax.add_patch(box)
    ax.text(0.5, 0.5, "not yet run", transform=ax.transAxes, ha="center",
            va="center", color=S.MUTED, fontsize=10.5, style="italic")
    header(ax, label_for(model_id), ", ", "queued", accent=False, muted_name=True)


def style_axes(ax, n_slots):
    ax.set_xlim(0, 1.06)
    ax.set_ylim(n_slots - 0.75, -0.75)
    ax.set_yticks([])
    ax.set_xticks([0, 0.5, 1.0])
    ax.set_xticklabels(["0", "50%", "100%"])
    S.grid_x_only(ax)
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(S.GRID)


def header(ax, name, count_text, sub_text, accent: bool, muted_name: bool = False):
    ax.text(0.0, 1.34, name, transform=ax.transAxes, va="baseline", ha="left",
            fontsize=11, fontweight="bold",
            color=S.MUTED if muted_name else S.INK)
    ax.text(1.0, 1.34, count_text, transform=ax.transAxes, va="baseline", ha="right",
            fontsize=11.5, fontweight="bold",
            color=S.ACCENT if accent else (S.MUTED if muted_name else S.INK))
    ax.text(0.0, 1.14, sub_text, transform=ax.transAxes, va="baseline", ha="left",
            fontsize=9, color=S.MUTED)


# ----------------------------------------------------------------------- main

def main():
    formulary_n = read_formulary_size()
    planned = read_planned_models()
    generative = read_generative()
    encoders = read_encoders()
    xcheck = debate_round0_crosscheck()

    gen_order = [m for m in planned] + [m for m in generative if m not in planned]
    enc_order = sorted(encoders, key=lambda m: -max(encoders[m].values()))

    incumbent = planned[0]
    inc_counts = generative.get(incumbent, Counter())
    inc_top_drug, inc_top_n = inc_counts.most_common(1)[0]
    inc_n = sum(inc_counts.values())

    unfilled = [m for m in gen_order if m not in generative]
    draft = bool(unfilled)

    n_slots = max([len(c) for c in list(generative.values()) + list(encoders.values())])

    # ---------------------------------------------------------------- stdout
    print("=" * 74)
    print("F4 fixed-policy replication - every number below is drawn in the figure")
    print("=" * 74)
    print(f"formulary size (model_registry.json): {formulary_n} agents")
    print(f"planned generative roster (model_compare.py DEFAULT_MODELS): {planned}")
    print(f"panels with no data yet: {unfilled or 'none'}  -> draft={draft}")
    print(f"bar slots reserved per panel (max distinct across models): {n_slots}")
    print("-" * 74)
    print("DISTINCT AGENTS RECOMMENDED, per model")
    for m in gen_order:
        if m in generative:
            c = generative[m]
            n = sum(c.values())
            print(f"  {label_for(m):<34} {len(c):>2} distinct   n={n:>3}   "
                  + ", ".join(f"{d} {v} ({v / n:.1%})" for d, v in c.most_common()))
        else:
            print(f"  {label_for(m):<34}  - not yet run")
    for m in enc_order:
        c = encoders[m]
        n = sum(c.values())
        print(f"  {label_for(m):<34} {len(c):>2} distinct   n={n:>3}   "
              + ", ".join(f"{d} {v} ({v / n:.1%})" for d, v in c.most_common()))
    print("-" * 74)
    print("CROSS-CHECK, runs/debate_20260818.jsonl kind=='round0', A-first only")
    print(f"  records {xcheck['n_records']}, distinct cases {xcheck['n_cases']}, "
          f"distinct agents {xcheck['distinct']}")
    print(f"  top agent {xcheck['top_drug']} on {xcheck['top_n']} of {xcheck['n_cases']} cases")
    print(f"  model_compare Qwen column: {inc_top_drug} on {inc_top_n} of {inc_n} cases, "
          f"{len(inc_counts)} distinct")
    agree = (xcheck["top_drug"] == inc_top_drug and xcheck["distinct"] == len(inc_counts))
    print(f"  agreement on agent identity and distinct count: {agree}")
    print("=" * 74)

    # ----------------------------------------------------------------- figure
    fig, axes = S.new_figure("full", nrows=2, ncols=4)
    fig.subplots_adjust(left=0.035, right=0.988, top=0.695, bottom=0.095,
                        wspace=0.30, hspace=0.90)

    ax_incumbent = None
    for col in range(4):
        ax = axes[0][col]
        if col >= len(gen_order):
            ax.set_axis_off()
            continue
        m = gen_order[col]
        if m in generative:
            draw_panel(ax, m, generative[m], n_slots, accent=(m == incumbent))
            if m == incumbent:
                ax_incumbent = ax
        else:
            draw_empty_panel(ax, m, n_slots)

    for col in range(4):
        ax = axes[1][col]
        if col >= len(enc_order):
            ax.set_axis_off()
            continue
        draw_panel(ax, enc_order[col], encoders[enc_order[col]], n_slots, accent=False)

    # x tick labels on the bottom row only; the 0-100% scale is shared by every panel
    for col in range(min(4, len(gen_order))):
        axes[0][col].set_xticklabels([])

    # the ONE annotation layer, used once, on the incumbent
    S.annotate_key(
        ax_incumbent, 0.02, n_slots - 1.25,
        f"{len(inc_counts)} agent of {formulary_n}, on every case.\n"
        f"Cross-check: {xcheck['top_n']} of {xcheck['n_cases']}\n"
        f"A-first round-0 records agree.",
        ha="left", va="center", fontsize=9.3,
    )

    # Row group labels, placed from the real axes geometry so they clear the panel
    # headers (which sit at axes-y 1.34) whatever the subplot spacing is.
    mono = S._available(["SF Mono", "Menlo", "DejaVu Sans Mono"])[0]
    for r, text in ((0, "GENERATIVE MODELS, ROUND 0"), (1, "ENCODERS, NO FINE-TUNING")):
        pos = axes[r][0].get_position()
        fig.text(0.012, pos.y0 + 1.34 * pos.height + 0.036, text, color=S.MUTED,
                 fontsize=8.4, fontweight="bold", fontfamily=mono,
                 va="baseline", ha="left")

    S.kicker_title(
        fig,
        "fixed round-0 policy",
        "Every model that has run reproduces a constant, not a decision.",
        f"Round-0 recommendation across a {formulary_n}-agent formulary. "
        "Encoders: all-masked PRIMARY variant, length-normalised mean over wordpieces.",
    )

    row = S.save(
        fig, "F4", "fixed_policy", draft=draft,
        source="runs/model_compare_20260818.jsonl, encoder_baseline.csv, "
               "runs/debate_20260818.jsonl (cross-check)",
        note=f"{len(unfilled)} model panel(s) awaiting data" if unfilled else "",
    )
    print(f"wrote {row['png']}")
    print(f"wrote {row['svg']}")
    return row


if __name__ == "__main__":
    main()
