#!/usr/bin/env python
"""f05_core_endpoint.py - F5, the headline figure.

Final antibiotic appropriateness stratified by AGENT x INTERACTION CONDITION x
COUNTERPART CORRECTNESS, with the two transition rates underneath.

Everything is computed here from files on disk. No hand-entered numbers.
  runs/debate_20260818.jsonl   kind=="full"  ordering-runs, both agents, 5 turns
  runs/c0cn_20260818.jsonl     Cn neutral-turn control (Agent A role)
  runs/canonical_reveal.jsonl  C2, the real panel revealed (Agent A position), 400/400
  inputs/panel_rows.parquet    via debate_run.load_panel / pathogenic_panel / score

Counterpart correctness is scored, not read off a flag: for each agent's FINAL
turn we take the OTHER agent's most recent standing drug before that turn and
score it with DR.score against DR.pathogenic_panel for that specimen.

Appropriateness = final drug ADEQUATE against every pathogenic isolate.
INTERMEDIATE_ONLY and UNDETERMINED stay in the denominator.

Governance: aggregates only, no patient-level identifier anywhere on the canvas.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/shamzzzh/brain_run")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "figures" / "src"))

import _style as S
import debate_run as DR

import matplotlib.transforms as mtransforms

DEBATE = ROOT / "runs" / "debate_20260818.jsonl"
C0CN = ROOT / "runs" / "c0cn_20260818.jsonl"
# The pre-recovery file held 207 of 400 ordering-runs because of the D-GATE-2
# defect, and the dropout was not random. canonical_reveal.jsonl is the deduped
# 400/400 arm produced by gate_recovery.py + canonicalise_c2.py.
REVEAL = ROOT / "runs" / "canonical_reveal.jsonl"
SPEC = ROOT / "protocol" / "tingting_endpoint_spec.md"

ADQ = "ADEQUATE"


# ---------------------------------------------------------------------------
def load(p):
    return [json.loads(l) for l in open(p) if l.strip()]


class Scorer:
    """DR.score against DR.pathogenic_panel, memoised per (drug, specimen)."""

    def __init__(self):
        self.panel = DR.load_panel()
        self._sub = {}
        self._out = {}
        self.calls = 0

    def outcome(self, drug, spec_id):
        key = (drug, spec_id)
        if key not in self._out:
            if spec_id not in self._sub:
                self._sub[spec_id] = DR.pathogenic_panel(self.panel, spec_id)
            self._out[key] = DR.score(drug, self._sub[spec_id])["outcome"]
            self.calls += 1
        return self._out[key]

    def adequate(self, drug, spec_id):
        return self.outcome(drug, spec_id) == ADQ


def rate(k, n):
    """k, n, point estimate and the Wilson interval, all in percent."""
    lo, hi = DR.BS.wilson_ci(k, n) if n else (float("nan"), float("nan"))
    # a proportion interval cannot leave [0, 1]; the closed form returns a
    # negative epsilon at k=0, clamp it so the printed bound is not "-0.0"
    return dict(k=k, n=n, pct=100.0 * k / n if n else float("nan"),
                lo=max(0.0, 100.0 * lo), hi=min(100.0, 100.0 * hi))


def transition(pairs):
    """pairs are (entering_outcome, leaving_outcome).

    correct -> incorrect : entered adequate, left not adequate
    incorrect -> correct : entered not adequate, left adequate
    """
    ent_ok = [(a, b) for a, b in pairs if a == ADQ]
    ent_bad = [(a, b) for a, b in pairs if a != ADQ]
    ci = rate(sum(1 for _, b in ent_ok if b != ADQ), len(ent_ok))
    ic = rate(sum(1 for _, b in ent_bad if b == ADQ), len(ent_bad))
    return ci, ic


# ---------------------------------------------------------------------------
def compute():
    rows = load(DEBATE)
    full = [r for r in rows if r.get("kind") == "full"]
    cn = load(C0CN)
    rv = load(REVEAL)
    sc = Scorer()

    paired = {c for c in {r["case_id"] for r in full}
              if len({r["ordering"] for r in full if r["case_id"] == c}) == 2}

    # ---- upper panel: appropriateness by agent x condition x counterpart ----
    # debate: each agent's final turn, and the counterpart's standing drug at
    # the moment that final turn was produced.
    strat = {("A", True): [0, 0], ("A", False): [0, 0],
             ("B", True): [0, 0], ("B", False): [0, 0]}
    adopted = 0
    n_final_turns = 0
    for r in full:
        spec = r["micro_specimen_id"]
        ts = r["turns"]
        for ag in ("A", "B"):
            fin = [t for t in ts if t["agent"] == ag][-1]
            cp = [t for t in ts if t["agent"] != ag and t["turn"] < fin["turn"]][-1]
            cp_ok = sc.adequate(cp["drug"], spec)
            cell = strat[(ag, cp_ok)]
            cell[1] += 1
            cell[0] += int(r[f"final_{ag}_outcome"] == ADQ)
            adopted += int(fin["drug"] == cp["drug"])
            n_final_turns += 1

    # round 0: the opening position, held only by that run's first speaker,
    # so Agent A's round 0 comes from the A-first runs and B's from B-first.
    r0 = {ag: rate(sum(1 for r in full
                       if r["ordering"] == o and r["round0_outcome"] == ADQ),
                   sum(1 for r in full if r["ordering"] == o))
          for ag, o in (("A", "A-first"), ("B", "B-first"))}

    up = dict(
        r0_A=r0["A"],
        r0_B=r0["B"],
        cn_A=rate(sum(1 for r in cn if r["cn_outcome"] == ADQ), len(cn)),
        deb_A_ok=rate(*strat[("A", True)]),
        deb_B_ok=rate(*strat[("B", True)]),
        deb_A_bad=rate(*strat[("A", False)]),
        deb_B_bad=rate(*strat[("B", False)]),
        c2_A=rate(sum(1 for r in rv if r["reveal_outcome"] == ADQ), len(rv)),
    )

    # ---- lower panel: the two transition rates, per condition -------------
    low = {
        "Cn_A": transition([(r["c0_outcome"], r["cn_outcome"]) for r in cn]),
        "deb_A": transition([(r["round0_outcome"], r["final_A_outcome"])
                             for r in full if r["ordering"] == "A-first"]),
        "deb_B": transition([(r["round0_outcome"], r["final_B_outcome"])
                             for r in full if r["ordering"] == "B-first"]),
        "C2_A": transition([(r["final_A_outcome"], r["reveal_outcome"])
                            for r in rv]),
    }

    meta = dict(n_full=len(full), n_paired=len(paired), n_cn=len(cn), n_rv=len(rv),
                adopted=adopted, n_final_turns=n_final_turns,
                round0_drug=Counter(r["round0_drug"] for r in full).most_common(2),
                score_calls=sc.calls, spec_present=SPEC.exists())
    return up, low, meta


# ---------------------------------------------------------------------------
def report(up, low, meta):
    W = 76
    print("=" * W)
    print("F5 CORE ENDPOINT - every rate and denominator")
    print("=" * W)
    print(f"  ordering-runs (kind=full)      {meta['n_full']}")
    print(f"  paired cases                   {meta['n_paired']}")
    print(f"  Cn records                     {meta['n_cn']}")
    print(f"  C2 reveal records              {meta['n_rv']}")
    print(f"  round-0 drug                   {meta['round0_drug']}")
    print(f"  final turns adopting counterpart's standing drug  "
          f"{meta['adopted']}/{meta['n_final_turns']} = "
          f"{100*meta['adopted']/meta['n_final_turns']:.1f}%")
    print(f"  distinct (drug, specimen) scorings   {meta['score_calls']}")
    print(f"  protocol/tingting_endpoint_spec.md present: {meta['spec_present']}")

    print("\n  UPPER PANEL - final appropriateness (ADEQUATE / all runs in stratum)")
    lbl = {
        "r0_A": "round 0            Agent A   no counterpart yet",
        "r0_B": "round 0            Agent B   no counterpart yet",
        "cn_A": "neutral turn Cn    Agent A   counterpart says nothing",
        "deb_A_ok": "debate             Agent A   counterpart CORRECT",
        "deb_B_ok": "debate             Agent B   counterpart CORRECT",
        "deb_A_bad": "debate             Agent A   counterpart WRONG",
        "deb_B_bad": "debate             Agent B   counterpart WRONG",
        "c2_A": "panel revealed C2  Agent A   counterpart is the laboratory",
    }
    for k in ("r0_A", "r0_B", "cn_A", "deb_A_ok", "deb_B_ok",
              "deb_A_bad", "deb_B_bad", "c2_A"):
        d = up[k]
        print(f"    {lbl[k]:<58} {d['k']:>4}/{d['n']:<4} = {d['pct']:5.1f}%"
              f"   95% CI [{d['lo']:.1f}, {d['hi']:.1f}]")

    print("\n  LOWER PANEL - transition rates within each condition")
    tl = {"Cn_A": "neutral turn Cn   Agent A",
          "deb_A": "debate            Agent A",
          "deb_B": "debate            Agent B",
          "C2_A": "panel revealed C2 Agent A"}
    for k in ("Cn_A", "deb_A", "deb_B", "C2_A"):
        ci, ic = low[k]
        print(f"    {tl[k]:<28} correct -> incorrect "
              f"{ci['k']:>3}/{ci['n']:<4} = {ci['pct']:5.1f}%"
              f"  CI [{ci['lo']:.1f}, {ci['hi']:.1f}]")
        print(f"    {'':<28} incorrect -> correct "
              f"{ic['k']:>3}/{ic['n']:<4} = {ic['pct']:5.1f}%"
              f"  CI [{ic['lo']:.1f}, {ic['hi']:.1f}]")
    print("=" * W)


# ---------------------------------------------------------------------------
def draw(up, low, meta):
    """Two stacked panels, placed by hand so the label stacks under each axis
    have known room and nothing overflows the 12x6in canvas."""
    fig, (axU, axL) = S.new_figure(size="full", nrows=2, ncols=1)
    axU.set_position([0.058, 0.495, 0.930, 0.285])
    axL.set_position([0.058, 0.138, 0.930, 0.128])

    # ---------------- upper panel -----------------------------------------
    # four condition groups; every bar carries an agent letter beneath it and
    # the counterpart state beneath that, so no legend is needed
    bars = [
        # (x, key, agent, counterpart-correct?)
        (0.00, "r0_A", "A", None),
        (0.82, "r0_B", "B", None),
        (2.30, "cn_A", "A", None),
        (3.78, "deb_A_ok", "A", True),
        (4.60, "deb_B_ok", "B", True),
        (5.78, "deb_A_bad", "A", False),
        (6.60, "deb_B_bad", "B", False),
        (8.08, "c2_A", "A", None),
    ]
    BW = 0.62
    blend = mtransforms.blended_transform_factory(axU.transData, axU.transAxes)

    for x, key, ag, cp in bars:
        d = up[key]
        col = S.ACCENT if cp is False else S.PRIMARY
        axU.bar(x, d["pct"], width=BW, color=col, zorder=3, edgecolor="none")
        # a zero bar is a measured zero, not missing data: stub the baseline
        if d["pct"] == 0:
            axU.plot([x - BW / 2, x + BW / 2], [0, 0], color=col, lw=3.0,
                     solid_capstyle="butt", zorder=4)
        axU.plot([x, x], [d["lo"], d["hi"]], color=S.INK, lw=1.6,
                 solid_capstyle="butt", zorder=5)
        top = max(d["pct"], d["hi"])
        axU.text(x, top + 2.6, f"{d['k']}/{d['n']}", ha="center", va="bottom",
                 color=S.MUTED, fontsize=9.0, zorder=6)
        axU.text(x, top + 10.0, f"{d['pct']:.1f}%", ha="center", va="bottom",
                 color=col if cp is False else S.INK, fontsize=12,
                 fontweight="bold", zorder=6)
        axU.text(x, -0.080, ag, ha="center", va="top", color=S.INK,
                 fontsize=11.5, fontweight="bold", transform=blend, clip_on=False)

    # counterpart state, directly under each bar or pair of bars
    cp_labels = [(0.41, "no counterpart yet", S.MUTED),
                 (2.30, "counterpart says nothing", S.MUTED),
                 (4.19, "counterpart correct", S.PRIMARY),
                 (6.19, "counterpart wrong", S.ACCENT),
                 (8.08, "counterpart is the laboratory", S.MUTED)]
    for x, t, c in cp_labels:
        axU.text(x, -0.190, t, ha="center", va="top", color=c, fontsize=10.2,
                 fontweight="bold" if c is not S.MUTED else "normal",
                 transform=blend, clip_on=False)

    # condition group names
    for x, t in [(0.41, "Round 0"), (2.30, "Neutral turn (Cn)"),
                 (5.19, "Debate"), (8.08, "Panel revealed (C2)")]:
        axU.text(x, -0.320, t, ha="center", va="top", color=S.INK,
                 fontsize=12, fontweight="bold", transform=blend, clip_on=False)

    axU.set_xlim(-0.58, 8.72)
    axU.set_ylim(0, 126)
    axU.set_xticks([])
    axU.set_yticks([0, 25, 50, 75, 100])
    axU.set_yticklabels(["0", "25", "50", "75", "100%"])
    S.grid_y_only(axU)
    axU.spines["bottom"].set_color(S.GRID)
    axU.set_ylabel("final drug adequate", color=S.MUTED, fontsize=10.5)

    # the one number that matters: the mechanism behind 100% against 0%
    S.annotate_key(axU, 5.45, 78,
                   f"{meta['adopted']} of {meta['n_final_turns']} final turns\n"
                   f"hold the counterpart's drug.",
                   ha="left", va="center", fontsize=12.5)

    # ---------------- lower panel -----------------------------------------
    rowsL = [(0.00, "Cn_A", "Neutral turn (Cn)", "A"),
             (1.28, "deb_A", "Debate", "A"),
             (2.46, "deb_B", "Debate", "B"),
             (3.86, "C2_A", "Panel revealed (C2)", "A")]
    HW = 0.38
    blendL = mtransforms.blended_transform_factory(axL.transData, axL.transAxes)

    for x, key, cond, ag in rowsL:
        ci, ic = low[key]
        for dx, d, col in ((-0.215, ci, S.ACCENT), (0.215, ic, S.PRIMARY)):
            axL.bar(x + dx, d["pct"], width=HW, color=col, zorder=3,
                    edgecolor="none")
            if d["pct"] == 0:
                axL.plot([x + dx - HW / 2, x + dx + HW / 2], [0, 0], color=col,
                         lw=3.0, solid_capstyle="butt", zorder=4)
            axL.text(x + dx, d["pct"] + 4.0, f"{d['pct']:.1f}%", ha="center",
                     va="bottom", color=col, fontsize=11, fontweight="bold")
            axL.text(x + dx, -0.100, f"{d['k']}/{d['n']}", ha="center", va="top",
                     color=S.MUTED, fontsize=9.0, transform=blendL, clip_on=False)
        axL.text(x, -0.290, cond, ha="center", va="top", color=S.INK,
                 fontsize=11.5, fontweight="bold", transform=blendL, clip_on=False)
        axL.text(x, -0.475, f"Agent {ag}", ha="center", va="top", color=S.MUTED,
                 fontsize=10, transform=blendL, clip_on=False)

    axL.set_xlim(-0.80, 4.55)
    axL.set_ylim(0, 100)
    axL.set_xticks([])
    axL.set_yticks([0, 50, 100])
    axL.set_yticklabels(["0", "50", "100%"])
    S.grid_y_only(axL)
    axL.spines["bottom"].set_color(S.GRID)
    axL.set_ylabel("share of runs\nentering that way", color=S.MUTED, fontsize=9.4)

    # both transition rates defined in plain words, colour-coded, which is what
    # lets the lower panel do without a legend
    fig.text(0.058, 0.318,
             "correct to incorrect      entered the condition holding an "
             "adequate drug, left holding one that was not",
             color=S.ACCENT, fontsize=10.8, va="bottom", ha="left")
    fig.text(0.058, 0.284,
             "incorrect to correct      entered holding a drug that was not "
             "adequate, left holding one that was",
             color=S.PRIMARY, fontsize=10.8, va="bottom", ha="left")

    # ---------------- title block -----------------------------------------
    S.kicker_title(
        fig, "core endpoint",
        "Final appropriateness is inherited from the counterpart, not from the patient.",
        f"Adequate = the final drug covers every pathogenic isolate. "
        f"{meta['n_paired']} paired cases, {meta['n_full']} ordering-runs; "
        f"whiskers are 95% Wilson intervals.")
    fig.text(0.012, 0.838,
             "INTERMEDIATE_ONLY and UNDETERMINED stay in the denominator.",
             color=S.MUTED, fontsize=9.5, va="top", ha="left")

    return S.save(fig, "F5", "core_endpoint", draft=True,
                  source="runs/{debate,c0cn,reveal}_20260818.jsonl + inputs/panel_rows.parquet",
                  note="19 August 2026; endpoint spec pending")


# ---------------------------------------------------------------------------
def main():
    up, low, meta = compute()
    report(up, low, meta)
    row = draw(up, low, meta)
    print(f"\n  wrote {row['png']}")
    print(f"  wrote {row['svg']}")
    if not meta["spec_present"]:
        print("\n  CAVEAT protocol/tingting_endpoint_spec.md is NOT on disk. "
              "Built to the ORDERS_0 description; DRAFT watermark applied.")


if __name__ == "__main__":
    main()
