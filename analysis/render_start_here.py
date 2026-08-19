#!/usr/bin/env python3
"""Render START_HERE.md. The prose is fixed; the state table is generated.

The state table is the part that goes stale, so it is read from
results/RESULTS.json and the run directory rather than typed. The rest of the page
is stable guidance and lives in this file.
"""
import json, glob, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.expanduser("~/brain_run/runs")
HEAD = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "start_here_head.md"), encoding="utf-8").read()

LABELS = {"debate": "debate", "reveal": "panel reveal", "clean_context": "clean context",
          "C1_pressure": "C1 pressure", "C0_baseline": "C0 baseline (pressure arm)",
          "D_MATCH_1": "drug-matched", "D_CALIB_1": "calibration",
          "cross_model": "cross-model", "self_consistency": "self-consistency",
          "plausible": "plausible-wrong seed", "track4": "support arm"}


def main():
    integ = json.load(open(os.path.join(ROOT, "results", "RESULTS.json")))["_integrity"]
    counts = {LABELS.get(k, k): v["n"] for k, v in integ.items()}
    fs = sum(1 for f in glob.glob(os.path.join(RUNS, "fewshot_2*.jsonl")) for _ in open(f))
    if fs:
        counts["few-shot"] = fs

    running = []
    for p in ("matched_pass", "calibration_pass", "fewshot_pass"):
        if os.popen("pgrep -f %s 2>/dev/null" % p).read().strip():
            running.append(p)

    rows = "\n".join("| %s | %d |" % (k, v) for k, v in sorted(counts.items(), key=lambda x: -x[1]))
    stamp = datetime.datetime.now().strftime("%d %B %Y, %H:%M")
    tail = """## State as of %s

%s Repository at `%s`.

| arm | exposures |
|---|---|
%s

Counts are deduplicated exposures, not lines on disk. Regenerate this page with
`python3 analysis/render_start_here.py`, or regenerate everything with `rebuild`.

## The conference deliverables

| artefact | what it is |
|---|---|
| `deck/Shomique_Hayat_UNIQ_antibiotic_agents.pptx` | the talk, generated from `results/*.json` by `deck/build_deck.py`, speaker notes on every slide |
| `deck/deck_figures.py` | every chart in the deck, drawn from the same result files |
| `deck/EVIDENCE.md` | every claim in the talk mapped to its number, its result file and the script that produces it |
| `BRIEFING.md` and `deck/brief.html` | the talk brief: the argument out loud, the ten numbers, the question drill |

Rebuild the whole deck with `python3 deck/deck_figures.py && python3 deck/build_deck.py`.

Slot: MPLS 2 of 3, Kloppenburg room, 12:15 to 12:30 on 20 August 2026, chaired by Dr Tim Hageman.
Ten minutes of talk, five of questions, aimed at a general audience.
""" % (
        stamp,
        ("Arms running: " + ", ".join(running) + ".") if running
        else "All experiments complete. Nothing running.",
        os.popen("git -C %s log --oneline -1" % ROOT).read().strip() or "unknown",
        rows,
    )
    open(os.path.join(ROOT, "START_HERE.md"), "w", encoding="utf-8").write(HEAD + tail)
    print("wrote START_HERE.md")


if __name__ == "__main__":
    main()
