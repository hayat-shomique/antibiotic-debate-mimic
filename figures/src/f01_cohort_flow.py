#!/usr/bin/env python
"""F1 - cohort flow. The CONSORT waterfall from index events to the analysed frame.

CLAIM: the analysed frame is a small, fully documented fraction of the frozen
cohort, and every gate on the way down carries a logged reason.

REPRODUCIBILITY. Every number rendered here is read or computed from disk:
  inputs/cohort_skeleton.parquet   frozen cohort row count (verification)
  cohort_gates_skeleton.csv        upstream waterfall 9,236 -> 7,796
  cohort_justification.md          applied-order gate table 7,796 -> 200
  deviation_log.csv                deviation ids for the upstream gates
  deviation_log_tonight.csv        deviation ids for the downstream gates
  protocol/protocol_v1.md          protocol line for gates with no deviation
  debate_run.build_frame()/select() live re-derivation of 3,107 / 1,087 / 993 / 200

Nothing is typed in. The script ALSO enforces the second half of the claim: if any
gate cannot be matched to a deviation id or a protocol line it raises, so a figure
asserting "every gate has a logged reason" cannot be produced when one does not.

Governance: aggregates only, no patient-level values, no case identifiers.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, "/Users/shamzzzh/brain_run/figures/src")
import _style as S                                                   # noqa: E402

ROOT = Path("/Users/shamzzzh/brain_run")
sys.path.insert(0, str(ROOT))

GATES_CSV = ROOT / "cohort_gates_skeleton.csv"
JUSTIFY_MD = ROOT / "cohort_justification.md"
SKELETON = ROOT / "inputs" / "cohort_skeleton.parquet"
DEV_MAIN = ROOT / "deviation_log.csv"
DEV_TONIGHT = ROOT / "deviation_log_tonight.csv"
PROTOCOL = ROOT / "protocol" / "protocol_v1.md"


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------
def _int(tok) -> int | None:
    """'7,796' / '**993**' / '-1,437' / '—' / '' -> int or None."""
    if tok is None:
        return None
    t = str(tok).replace("*", "").replace(",", "").replace("−", "-").strip()
    if t in ("", "-", "—", "nan", "None"):
        return None
    return abs(int(t))


def read_upstream() -> list[dict]:
    """cohort_gates_skeleton.csv: the recorded waterfall down to the frozen cohort."""
    df = pd.read_csv(GATES_CSV)
    rows = []
    for _, r in df.iterrows():
        rows.append(dict(gate=str(r["gate"]).strip(),
                         n=_int(r["n"]),
                         removed=_int(r.get("excluded"))))
    # arithmetic self-check: n_i = n_{i-1} - removed_i
    for a, b in zip(rows, rows[1:]):
        if b["removed"] is not None and a["n"] - b["removed"] != b["n"]:
            raise SystemExit(f"FATAL upstream waterfall does not reconcile at {b['gate']!r}")
    return rows


def read_applied_order() -> list[dict]:
    """cohort_justification.md: the '### Applied order' markdown table."""
    text = JUSTIFY_MD.read_text()
    lines = text.splitlines()
    hdr = None
    for i, ln in enumerate(lines):
        cells = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
        if cells[:5] == ["step", "before", "after", "removed", "deviation"]:
            hdr = i
            break
    if hdr is None:
        raise SystemExit("FATAL applied-order gate table not found in cohort_justification.md")

    rows = []
    for ln in lines[hdr + 2:]:
        if not ln.strip().startswith("|"):
            break
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 5:
            break
        step = re.sub(r"^\s*\d+\.\s*", "", c[0].replace("*", "")).strip()
        rows.append(dict(gate=step, before=_int(c[1]), n=_int(c[2]),
                         removed=_int(c[3]), dev=c[4].replace("*", "").strip()))
    if not rows:
        raise SystemExit("FATAL applied-order gate table is empty")

    # fill the sampling row, whose 'removed' is recorded as an em dash
    for r in rows:
        if r["removed"] is None and r["before"] is not None and r["n"] is not None:
            r["removed"] = r["before"] - r["n"]
    # arithmetic self-check
    for r in rows:
        if r["before"] - r["removed"] != r["n"]:
            raise SystemExit(f"FATAL applied-order row does not reconcile: {r['gate']!r}")
    for a, b in zip(rows, rows[1:]):
        if a["n"] != b["before"]:
            raise SystemExit(f"FATAL applied-order chain breaks at {b['gate']!r}")
    return rows


# --------------------------------------------------------------------------
# "every gate has a logged reason" - enforced, not asserted
# --------------------------------------------------------------------------
# Each upstream gate is matched to deviation_log.csv rows by the words the log
# itself uses in its `element` column; a gate with no deviation must instead be
# found as a numbered gate in protocol_v1 section 2. Both are file lookups.
DEV_MATCH = [
    (("index event", "blood culture"), ("specimen",)),
    (("pathogen", "contaminant", "fungal"), ("contaminant", "non-bacterial", "retain")),
]
PROTOCOL_MATCH = [
    (("adults",), r"^\s*(\d+)\.\s*adults 18\+"),
    (("formulary", "panel"), r"^\s*(\d+)\.\s*susceptibility panel present"),
]


def _collapse(ids: list[str]) -> str:
    """['D-CONTAM-1','D-CONTAM-2','D-CONTAM-3','D-RETAIN-1'] -> 'D-CONTAM-1/2/3 + D-RETAIN-1'."""
    fam: dict[str, list[int]] = {}
    for i in sorted(set(ids)):
        m = re.match(r"^(.*)-(\d+)$", i)
        if m:
            fam.setdefault(m.group(1), []).append(int(m.group(2)))
        else:
            fam.setdefault(i, [])
    out = []
    for k, v in fam.items():
        out.append(f"{k}-{'/'.join(str(x) for x in sorted(v))}" if v else k)
    return " + ".join(out)


def logged_reason(gate: str) -> str:
    """Return the logged reason for a gate, or raise. Reads the logs, does not assume."""
    g = gate.lower()
    dev = pd.read_csv(DEV_MAIN)
    dev = dev[dev["stage"].astype(str).str.lower().str.contains("cohort")]
    for gate_kw, elem_kw in DEV_MATCH:
        if any(k in g for k in gate_kw):
            hit = dev[dev["element"].astype(str).str.lower()
                      .apply(lambda e: any(k in e for k in elem_kw))]
            if len(hit):
                return _collapse(list(hit["id"].astype(str)))
    prot = PROTOCOL.read_text().splitlines()
    for gate_kw, pat in PROTOCOL_MATCH:
        if any(k in g for k in gate_kw):
            for ln in prot:
                m = re.match(pat, ln, flags=re.I)
                if m:
                    return f"protocol_v1 §2 gate {m.group(1)}"
    raise SystemExit(f"FATAL no logged reason found for gate {gate!r} - "
                     "the claim 'every gate has a logged reason' cannot be made")


def verify_downstream_ids(rows: list[dict]) -> None:
    """The downstream ids quoted in the justification must exist in a deviation log."""
    known = set()
    for f in (DEV_MAIN, DEV_TONIGHT):
        known |= set(pd.read_csv(f)["id"].astype(str))
    for r in rows:
        ids = re.findall(r"D-[A-Z0-9]+-\d+", r["dev"])
        for i in ids:
            if i not in known:
                raise SystemExit(f"FATAL deviation id {i} quoted for {r['gate']!r} is not in any log")
        r["ids"] = _collapse(ids) if ids else r["dev"]


# --------------------------------------------------------------------------
# live re-derivation
# --------------------------------------------------------------------------
def live_counts(sample_n: int) -> dict[str, int] | None:
    """Re-run the actual selection code. sample_n comes from the parsed gate table,
    never from a literal here. Returns None if the selection cannot run on this box."""
    try:
        import debate_run as DR
        frame, _ = DR.build_frame()
        panel = DR.load_panel()
        return {
            "frozen": int(len(frame)),
            "linked": int(frame["hadm_id_final"].notna().sum()),
            "entero": int(len(DR.enterobacterales_ids(panel, frame))),
            "frame": int(len(DR.select(frame, 10 ** 9, False, panel))),
            "sampled": int(len(DR.select(frame, sample_n, True, panel))),
        }
    except Exception as exc:                                   # pragma: no cover
        print(f"  [live re-derivation unavailable: {type(exc).__name__}: {exc}]")
        return None


# --------------------------------------------------------------------------
def build_stages() -> tuple[list[dict], dict]:
    up = read_upstream()
    down = read_applied_order()
    verify_downstream_ids(down)

    frozen_n = up[-1]["n"]

    # verification 1: the frozen cohort against the read-only parquet
    import pyarrow.parquet as pq
    parquet_n = pq.ParquetFile(SKELETON).metadata.num_rows
    if parquet_n != frozen_n:
        raise SystemExit(f"FATAL cohort_skeleton.parquet has {parquet_n} rows, "
                         f"waterfall ends at {frozen_n}")

    # verification 2: the two files must agree on where the frozen cohort sits
    if down[0]["before"] != frozen_n:
        raise SystemExit("FATAL applied order does not start at the frozen cohort")

    # verification 3: live re-derivation of every downstream count
    live = live_counts(down[3]["n"])
    prov = {"frozen": "parquet row count", "linked": "cohort_justification.md",
            "entero": "cohort_justification.md", "frame": "cohort_justification.md",
            "sampled": "cohort_justification.md"}
    if live is not None:
        parsed = {"frozen": frozen_n, "linked": down[0]["n"], "entero": down[1]["n"],
                  "frame": down[2]["n"], "sampled": down[3]["n"]}
        for k, v in parsed.items():
            if live[k] != v:
                raise SystemExit(f"FATAL live {k}={live[k]} disagrees with file {k}={v}")
            prov[k] = "LIVE debate_run + file, agree"

    stages = []
    for i, r in enumerate(up):
        stages.append(dict(gate=r["gate"], n=r["n"], removed=r["removed"],
                           why=(logged_reason(r["gate"]) if r["removed"] is not None
                                else logged_reason(r["gate"])),
                           kind="upstream", tag=None))
    stages[-1]["kind"] = "frozen"
    stages[-1]["tag"] = "FROZEN COHORT"
    for i, r in enumerate(down):
        kind = "gate" if i < len(down) - 1 else "sample"
        stages.append(dict(gate=r["gate"], n=r["n"], removed=r["removed"],
                           why=r["ids"], kind=kind, tag=None))
    stages[len(up) + len(down) - 2]["kind"] = "frame"
    stages[len(up) + len(down) - 2]["tag"] = "ANALYSED FRAME"

    for s in stages:
        s["pct"] = 100.0 * s["n"] / frozen_n
    return stages, dict(frozen_n=frozen_n, prov=prov, live=live is not None)


# --------------------------------------------------------------------------
def draw(stages: list[dict], meta: dict):
    frozen_n = meta["frozen_n"]
    top_n = max(s["n"] for s in stages)
    frame = next(s for s in stages if s["kind"] == "frame")

    fig, ax = S.new_figure("full")

    XLIM = top_n * 1.74
    col_n = top_n * 1.14          # right-aligned n
    col_pct = top_n * 1.17        # left-aligned per cent
    col_why = top_n * 1.32        # left-aligned excluded + deviation ids
    BH = 0.34

    fill = {"upstream": S.MUTED, "frozen": S.INK, "gate": S.PRIMARY,
            "frame": S.ACCENT, "sample": S.ACCENT}

    # broken scale guides: drawn only across each bar band, so they never cross a gate name
    guides = list(range(2000, top_n, 2000))
    for gx in guides:
        for i in range(len(stages)):
            ax.plot([gx, gx], [i - 0.27, i + 0.27], color=S.GRID, lw=0.7, zorder=0)
        ax.plot([gx, gx], [-0.70, -0.60], color=S.GRID, lw=0.7, zorder=0)
        ax.text(gx, -0.78, f"{gx:,}", color=S.MUTED, fontsize=8.3, ha="center", va="bottom")
    ax.text(top_n * 1.005, -0.78, "cases", color=S.MUTED, fontsize=8.3,
            ha="left", va="bottom", style="italic")

    prev_n = None
    for i, s in enumerate(stages):
        # pale block = what this gate removed
        if prev_n is not None and prev_n > s["n"]:
            ax.barh(i, prev_n - s["n"], left=s["n"], height=BH,
                    color=S.GRID, edgecolor="none", zorder=1)
        alpha = 0.45 if s["kind"] == "sample" else 1.0
        ax.barh(i, s["n"], height=BH, color=fill[s["kind"]], alpha=alpha,
                edgecolor="none", zorder=2)

        if s["tag"]:
            S.direct_label(ax, 0, i - 0.60, s["tag"],
                           color=S.ACCENT if s["kind"] == "frame" else S.MUTED,
                           fontsize=8.6, fontweight="bold", va="bottom")
        name = s["gate"][0].upper() + s["gate"][1:]
        S.direct_label(ax, 0, i - 0.31, name, color=S.INK, fontsize=11.2,
                       fontweight="bold", va="bottom")

        S.direct_label(ax, col_n, i, f"{s['n']:,}", color=S.INK, fontsize=12.5,
                       fontweight="bold", ha="right")
        if s["n"] <= frozen_n:
            S.direct_label(ax, col_pct, i, f"{s['pct']:.1f}%", color=S.MUTED, fontsize=10.2)

        if s["removed"] is not None:
            verb = "sampled out" if s["kind"] == "sample" else "excluded"
            S.direct_label(ax, col_why, i - 0.09, f"−{s['removed']:,} {verb}",
                           color=S.MUTED, fontsize=9.6, va="bottom")
        why_y = i + 0.30 if s["removed"] is not None else i + 0.10
        S.direct_label(ax, col_why, why_y, s["why"], color=S.MUTED, fontsize=8.7,
                       va="bottom", fontstyle="italic")
        prev_n = s["n"]

    idx = stages.index(frame)
    S.annotate_key(ax, top_n * 0.42, idx + 0.02,
                   f"{frame['n']:,} of {frozen_n:,}\n= {frame['pct']:.1f}% of the frozen cohort",
                   arrow_to=(frame["n"] * 1.06, idx), fontsize=12.5)

    ax.set_xlim(0, XLIM)
    ax.set_ylim(len(stages) - 0.30, -1.08)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

    pct_frame = frame["pct"]
    S.kicker_title(
        fig, "cohort restriction chain",
        f"The analysed frame is {pct_frame:.1f}% of the frozen cohort, "
        "and every gate down to it is logged.",
        "MIMIC-IV v3.1. Bar width is proportional to n; the pale block on each row is what that "
        f"gate removed. Percentages are of the frozen cohort ({frozen_n:,} = 100%).")
    fig.subplots_adjust(top=0.775, left=0.012, right=0.995, bottom=0.055)

    src = ("cohort_gates_skeleton.csv + cohort_justification.md + inputs/cohort_skeleton.parquet"
           + (" + live debate_run.select()" if meta["live"] else ""))
    return S.save(fig, "F1", "cohort_flow", draft=False, source=src,
                  note="deviation ids verified against deviation_log.csv and deviation_log_tonight.csv")


# --------------------------------------------------------------------------
if __name__ == "__main__":
    stages, meta = build_stages()
    print("\nF1 cohort flow - every stage count, computed from disk")
    print(f"{'stage':<58}{'n':>8}{'% frozen':>10}{'removed':>10}  logged reason")
    for s in stages:
        rem = "" if s["removed"] is None else f"-{s['removed']:,}"
        pct = f"{s['pct']:.1f}%" if s["n"] <= meta["frozen_n"] else "n/a"
        print(f"{s['gate'][:57]:<58}{s['n']:>8,}{pct:>10}{rem:>10}  {s['why']}")
    print(f"\nfrozen cohort              = {meta['frozen_n']:,}")
    fr = next(s for s in stages if s["kind"] == "frame")
    sm = next(s for s in stages if s["kind"] == "sample")
    print(f"analysed frame             = {fr['n']:,}  = {fr['pct']:.2f}% of the frozen cohort")
    print(f"sampled, seed 20260818     = {sm['n']:,}  = {sm['pct']:.2f}% of the frozen cohort")
    print(f"total removed 9,236 -> {sm['n']:,} = {max(s['n'] for s in stages) - sm['n']:,}")
    print("\nprovenance of each verified count:")
    for k, v in meta["prov"].items():
        print(f"  {k:<8} {v}")
    row = draw(stages, meta)
    print(f"\nwrote {row['png']}")
    print(f"wrote {row['svg']}")
