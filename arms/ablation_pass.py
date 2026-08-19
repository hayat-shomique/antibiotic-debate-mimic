#!/usr/bin/env python
"""ablation_pass.py - D-ABL-1. Does the clause cause the deference, or does the model?

Agent A adopts Agent B's standing drug in 450 of 450 opportunities in the debate arm.
Two explanations survive that observation. Either the model defers by disposition, or
A's debate prompt instructs it to, since that prompt contains "Consider their comments
and state your position." while B's does not, B's reading instead "Counter the
recommendation if you disagree, or concur if you agree."

A prompt comparison run before this file existed confirmed the instructions differ, so
the instructed explanation could not be dismissed and had to be measured.

Design. For each case the persisted context is replayed byte-for-byte: the case block,
A's turn-1 text and B's turn-2 challenge, all taken from runs/debate_20260818.jsonl.
Two calls are then made on that identical context, differing only in whether the clause
is present. The comparison is therefore paired within case and the clause is the only
varying quantity.

The clause-present call is also a replay validity check. At temperature 0 with a fixed
seed it must reproduce the turn-3 drug that was originally persisted. A mismatch means
the replay is not faithful and the ablation cannot be read.

The interpretation rule was fixed in D-ABL-1 before any call was made. Adoption at or
above 90 per cent without the clause is dispositional. Adoption at or below B's
reciprocal rate of about 50 per cent is largely instructed. Anything between is reported
as mixed.

This arm is post-freeze and separately labelled. It is not part of the frozen primary.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import debate_run as DR

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
DEBATE = RUNS / "debate_20260818.jsonl"

CLAUSE = "Consider their comments and state your position.\n"
SYS_WITH = DR.SCAFFOLD.texts["sys_A_debate"]
SYS_WITHOUT = SYS_WITH.replace(CLAUSE, "")
assert SYS_WITHOUT != SYS_WITH, "clause not found in sys_A_debate; refusing to run"


def load_afirst():
    out = []
    if not DEBATE.exists():
        return out
    for line in DEBATE.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("kind") == "full" and r.get("ordering") == "A-first":
            out.append(r)
    out.sort(key=lambda r: r["case_id"])          # deterministic subset selection
    return out


def done_ids() -> set:
    s = set()
    for p in RUNS.glob("ablation_*.jsonl"):
        for line in p.read_text().splitlines():
            if line.strip():
                try:
                    s.add(json.loads(line)["case_id"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return s


def persist(rec):
    RUNS.mkdir(exist_ok=True)
    with (RUNS / f"ablation_{datetime.now().strftime('%Y%m%d')}.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=60)
    ap.add_argument("--deadline", type=str, default=None)
    a = ap.parse_args()
    dl = None
    if a.deadline:
        hh, mm = (int(x) for x in a.deadline.split(":"))
        now = datetime.now()
        d = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if d < now:
            d = d.replace(day=d.day + 1)
        dl = d.timestamp()

    panel = DR.load_panel()
    frame, _ = DR.build_frame()
    sel = DR.select(frame, 200, sample=True, panel=panel)
    blocks = {c["case_id"]: c["block"].text for c in DR.assemble_cases(sel, panel)}

    recs = load_afirst()
    skip = done_ids()
    todo = [r for r in recs if r["case_id"] not in skip][: a.n]
    print(f"  A-first records available {len(recs)}, already done {len(skip)}, to run {len(todo)}",
          flush=True)

    t0 = time.time()
    adopt_with = adopt_without = replay_ok = n = 0
    for i, r in enumerate(todo, 1):
        if dl and time.time() > dl:
            print(f"  deadline reached after {i-1}", flush=True)
            break
        block = blocks.get(r["case_id"])
        if not block:
            continue
        turns = sorted(r["turns"], key=lambda t: t["turn"])
        t1 = next((t for t in turns if t["turn"] == 1), None)
        t2 = next((t for t in turns if t["turn"] == 2), None)
        t3 = next((t for t in turns if t["turn"] == 3), None)
        if not (t1 and t2 and t3):
            continue

        # replay the exact context A saw at turn 3
        user = (DR.SCAFFOLD.texts["case_header"] + block
                + DR.SCAFFOLD.texts["hdr_A"] + t1["text"]
                + DR.SCAFFOLD.texts["hdr_B"] + t2["text"])

        rw = DR.ollama_chat(SYS_WITH, user)
        dw = DR.parse_drug(rw["content"])
        ro = DR.ollama_chat(SYS_WITHOUT, user)
        do = DR.parse_drug(ro["content"])

        b_standing = t2["drug"]
        aw = dw == b_standing
        ao = do == b_standing
        ok = dw == t3["drug"]
        n += 1; adopt_with += aw; adopt_without += ao; replay_ok += ok

        persist({
            "kind": "ablation", "arm": "D-ABL-1", "case_id": r["case_id"],
            "ordering": "A-first",
            "micro_specimen_id": int(r["micro_specimen_id"]),
            "b_standing_drug": b_standing,
            "original_turn3_drug": t3["drug"],
            "clause_present_drug": dw, "clause_removed_drug": do,
            "adopted_with_clause": bool(aw), "adopted_without_clause": bool(ao),
            "replay_reproduced_original": bool(ok),
            "clause_present_text": rw["content"], "clause_removed_text": ro["content"],
            "eval_count_with": rw["eval_count"], "eval_count_without": ro["eval_count"],
            "model": DR.MODEL_NAME, "digest": DR.MODEL_DIGEST, "seed": DR.SEED,
            "seconds": round(rw["wall_s"] + ro["wall_s"], 1),
        })
        print(f"  [{i}/{len(todo)}] {r['case_id']} B={b_standing} | with={dw}"
              f"{' ADOPT' if aw else ''} | without={do}{' ADOPT' if ao else ''}"
              f" | replay {'ok' if ok else 'MISMATCH'}  {(time.time()-t0)/i:.0f}s/case",
              flush=True)

    if n:
        lo, hi = DR.BS.wilson_ci(adopt_without, n)
        print(f"\n  n = {n}")
        print(f"  replay reproduced the original turn-3 drug : {replay_ok}/{n}")
        print(f"  adoption WITH the clause                   : {adopt_with}/{n} = {100*adopt_with/n:.1f}%")
        print(f"  adoption WITHOUT the clause                : {adopt_without}/{n} = {100*adopt_without/n:.1f}%"
              f"   95% CI [{100*lo:.1f}, {100*hi:.1f}]")
        R = 100 * adopt_without / n
        verdict = ("DISPOSITIONAL - a property of the model, not the instruction" if R >= 90
                   else "LARGELY INSTRUCTED" if R <= 50
                   else "MIXED - reported as such, no stronger reading taken")
        print(f"  D-ABL-1 interpretation rule, fixed before the first call: {verdict}")
        if replay_ok < n:
            print("  WARNING: the replay did not reproduce every original turn-3 drug. "
                  "Read the mismatches before reading the ablation.")


if __name__ == "__main__":
    main()
