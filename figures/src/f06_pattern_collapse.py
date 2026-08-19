"""F6 - the two-pattern collapse.

Every ordering-run in runs/debate_20260818.jsonl is reduced to its SHAPE: walk the
five turns, map the first distinct drug seen to slot X, the next distinct drug to
slot Y, a third to slot Z. Runs that argue about different antibiotics but move in
the same way collapse onto the same symbolic string.

Everything drawn or written on this figure is computed below from the run file.
No number is typed in by hand. The only quantity not read from disk is the visual
jitter used to spread 400 overlapping polylines, which is a rendering device on a
fixed seed and carries no information.

Run:  python figures/src/f06_pattern_collapse.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, "/Users/shamzzzh/brain_run/figures/src")
import _style as S  # noqa: E402

ROOT = Path("/Users/shamzzzh/brain_run")
RUNS = ROOT / "runs" / "debate_20260818.jsonl"
SLOTS = "XYZWV"
JITTER_SEED = 20260819          # rendering only, affects no reported number


# ---------------------------------------------------------------- read + reduce
def load_runs(path: Path) -> list[dict]:
    out = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("kind") == "full":
                out.append(rec)
    return out


def drug_sequence(rec: dict) -> list[str]:
    return [t["drug"] for t in sorted(rec["turns"], key=lambda t: t["turn"])]


def agent_sequence(rec: dict) -> str:
    return "".join(t["agent"] for t in sorted(rec["turns"], key=lambda t: t["turn"]))


def to_pattern(seq: list[str]) -> str:
    """First-appearance symbolic reduction: 1st distinct drug -> X, 2nd -> Y, ..."""
    seen: list[str] = []
    out = []
    for d in seq:
        if d not in seen:
            seen.append(d)
        out.append(SLOTS[seen.index(d)])
    return "".join(out)


def has_reversal(pat: str) -> bool:
    """A slot is re-entered after a different slot intervened."""
    return any(pat[i] != pat[i - 1] and pat[i] in pat[: i - 1] for i in range(1, len(pat)))


runs = load_runs(RUNS)
n_runs = len(runs)
n_cases = len({r["case_id"] for r in runs})
n_turns = len(drug_sequence(runs[0]))
turns = list(range(1, n_turns + 1))

for r in runs:
    r["_seq"] = drug_sequence(r)
    r["_pat"] = to_pattern(r["_seq"])

pat_counts = Counter((r["ordering"], r["_pat"]) for r in runs)
ranked = pat_counts.most_common()

order_counts = Counter(r["ordering"] for r in runs)
agent_by_order = {o: Counter(agent_sequence(r) for r in runs if r["ordering"] == o).most_common(1)[0][0]
                  for o in order_counts}

max_slots = max(len(set(r["_seq"])) for r in runs)
n_three_plus = sum(1 for r in runs if len(set(r["_seq"])) >= 3)
n_reversal = sum(1 for r in runs if has_reversal(r["_pat"]))
slot_x_drug, slot_x_n = Counter(r["_seq"][0] for r in runs).most_common(1)[0]

# the two modal trajectories, and the lone exception, all identified from the counts
(mod1_key, mod1_n), (mod2_key, mod2_n) = ranked[0], ranked[1]
exception_key, exception_n = ranked[-1]
n_patterns = len(ranked)

MODALS = [(mod1_key, mod1_n), (mod2_key, mod2_n)]
exc_turn = next(i + 1 for i in range(1, n_turns)
                if exception_key[1][i] != exception_key[1][i - 1]
                and exception_key[1][i] in exception_key[1][: i - 1])


def settle_turn(pat: str) -> int:
    """First turn from which the pattern never changes again."""
    return next(i + 1 for i in range(len(pat)) if len(set(pat[i:])) == 1)


# the later of the two modal settle points: the turn by which both shapes have fixed
sat_turn = max(settle_turn(pat) for (_o, pat), _n in MODALS)
n_saturated = sum(1 for r in runs if len(set(r["_seq"][sat_turn - 1:])) == 1)

# ------------------------------------------------------------------- stdout log
print(f"F6  source: {RUNS.relative_to(ROOT)}")
print(f"  ordering-runs (kind=='full')      {n_runs}")
print(f"  distinct cases                    {n_cases}  ({n_runs // max(n_cases,1)} orderings each)")
print(f"  turns per run                     {n_turns}")
print(f"  distinct symbolic patterns        {n_patterns}")
for (order, pat), n in ranked:
    speak = agent_by_order[order]
    shape = "  ".join(f"{a}:{s}" for a, s in zip(speak, pat))
    print(f"    {order:<8} {pat}   n = {n:>3}  of {order_counts[order]:>3}   [{shape}]")
print(f"  max distinct drugs within one run {max_slots}  -> slot Z never reached")
print(f"  runs reaching a third slot        {n_three_plus}")
print(f"  both shapes settled by turn       {sat_turn}")
print(f"  runs unchanged from turn {sat_turn} on     {n_saturated} / {n_runs}")
print(f"  runs containing a reversal        {n_reversal}")
print(f"  slot-X drug modal identity        {slot_x_drug} on {slot_x_n} / {n_runs} runs")
print(f"  exception: {exception_key[0]} {exception_key[1]}, re-enters slot X at turn {exc_turn}")

# ----------------------------------------------------------------------- figure
Y_OF = {"X": 1.0, "Y": 0.0, "Z": -1.0}
OFFSET = {mod1_key[0]: 0.052, mod2_key[0]: -0.052}
EXC_OFFSET = -0.135

fig, ax = S.new_figure("full")
rng = np.random.default_rng(JITTER_SEED)

# saturation band: from the turn after which nothing but the exception moves
ax.axvspan(sat_turn, n_turns + 0.55, color=S.BG, ymin=0.0, ymax=1.0, zorder=0, lw=0)

# every run, faint, jittered so the overplotting itself is the evidence
for r in runs:
    ys = np.array([Y_OF[s] for s in r["_pat"]], dtype=float)
    ys = ys + rng.normal(0.0, 0.036, size=ys.shape)
    ax.plot(turns, ys, color=S.MUTED, alpha=0.065, lw=1.4,
            solid_capstyle="round", zorder=2)

# the two modal trajectories, boldly, over the top
for (order, pat), n in MODALS:
    ys = [Y_OF[s] + OFFSET[order] for s in pat]
    ax.plot(turns, ys, color=S.PRIMARY, lw=3.4, solid_capstyle="round",
            marker="o", ms=8.5, mfc=S.PRIMARY, mec=S.WHITE, mew=1.6, zorder=5)

# the single exception, in accent, so the eye finds it
exc_ys = [Y_OF[s] + EXC_OFFSET for s in exception_key[1]]
ax.plot(turns, exc_ys, color=S.ACCENT, lw=2.4, solid_capstyle="round",
        marker="o", ms=6.5, mfc=S.ACCENT, mec=S.WHITE, mew=1.4, zorder=6)

# --- direct labels, each hugging the flat segment unique to that trajectory:
#     A-first is alone on slot Y across turns 2-3, B-first alone on slot X across turns 1-2
label_xy = {mod1_key[0]: (2.06, -0.18), mod2_key[0]: (1.22, 1.22)}
for (order, pat), n in MODALS:
    lx, ly = label_xy[order]
    S.direct_label(ax, lx, ly,
                   f"{order}\n{n} of {order_counts[order]} runs",
                   color=S.PRIMARY, fontsize=13, fontweight="bold",
                   ha="left", va="center", linespacing=1.45, zorder=7)

# --- the one annotation this figure is allowed
S.annotate_key(
    ax, 4.88, 1.14,
    f"{exception_n} run of {n_runs} re-enters\nslot {exception_key[1][-1]} at turn {exc_turn}",
    arrow_to=(n_turns, Y_OF[exception_key[1][-1]] + EXC_OFFSET),
    ha="right", va="center", fontsize=12.5,
)

# --- axes
ax.set_xticks(turns)
ax.set_xticklabels([f"turn {t}" for t in turns])
slots_used = sorted({s for r in runs for s in r["_pat"]}, key=SLOTS.index)
ax.set_yticks([Y_OF[s] for s in reversed(slots_used)])
ax.set_yticklabels([f"slot {s}" for s in reversed(slots_used)])
ax.set_ylabel("position slot", labelpad=12)
ax.set_xlim(0.42, n_turns + 0.55)
ax.set_ylim(-0.62, 1.38)
S.grid_y_only(ax)
ax.tick_params(axis="y", labelsize=12)
ax.tick_params(axis="x", labelsize=11.5, pad=7)
ax.spines["left"].set_visible(False)

# saturation caption, muted, low in the empty band
S.direct_label(ax, sat_turn + 0.06, -0.45,
               f"dialogue saturates at turn {sat_turn}  ·  {n_saturated} of {n_runs} runs never move again",
               color=S.MUTED, fontsize=10.5, ha="left", va="center", zorder=7)

# who is speaking, one row per ordering, keyed to the trajectories above
blend = ax.get_xaxis_transform()
for row, ((order, pat), n) in enumerate(MODALS):
    y = -0.155 - row * 0.085
    ax.text(0.46, y, f"{order}, speaker", transform=blend, color=S.MUTED,
            fontsize=9.8, ha="left", va="center", clip_on=False)
    for t, agent in zip(turns, agent_by_order[order]):
        ax.text(t, y, agent, transform=blend, color=S.MUTED, fontsize=9.8,
                ha="center", va="center", clip_on=False)

S.kicker_title(
    fig, "two-pattern collapse",
    f"{n_runs} separate conversations collapse into two trajectories.",
    sub=(f"Slot X is the drug a run names first, slot Y the next distinct drug to appear. "
         f"No run ever reaches a third slot; two shapes cover {mod1_n + mod2_n} of the {n_runs} runs."),
)
fig.subplots_adjust(top=0.775, bottom=0.235, left=0.105, right=0.975)

row = S.save(fig, "F6", "pattern_collapse", draft=False,
             source="runs/debate_20260818.jsonl (kind=='full')",
             note=f"{n_runs} ordering-runs, {n_cases} cases")
print(f"  wrote {row['png']}")
print(f"  wrote {row['svg']}")
