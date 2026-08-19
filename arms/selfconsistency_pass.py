#!/usr/bin/env python
"""D-SELFCON-1, the single-agent control at matched compute.

The gap this closes. The study reports that two agents finish with the accuracy of
one. Without a single-agent arm given the SAME compute, that claim is partly entailed
by the 100% abandonment rate rather than independently measured, and it is the first
thing a referee attacks.

The design. The debate spends five model calls per case. This arm spends five model
calls per case on ONE agent, drawing five independent samples and aggregating them by
majority vote. Turn-for-turn compute matched, no counterpart, no conversation.

Oh et al. (JMIR 2026, doi 10.2196/90693) report parallel sampling as the stronger
test-time scaling strategy on easier medical tasks, and specifically a shortest-
majority-vote rule that penalises long solutions. This arm uses PLAIN majority vote,
which is a different and simpler rule; it must not be described as reproducing theirs.

DEVIATION, logged as D-SELFCON-1. Independent samples require temperature > 0, so this
arm runs at temperature 0.7 while every other arm runs at temperature 0. That is a
change of decoding, so this arm is reported beside the frozen arms and never pooled
with them. The round-0 sample-1 drug is reported as its own control: if it matches the
frozen round-0 distribution, the temperature change has not moved the opening.
"""
from __future__ import annotations
import argparse, json, time, collections
from datetime import datetime
from pathlib import Path

import debate_run as DR
import provenance as PV

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
K = 5                 # matched to the five turns the debate spends
TEMPERATURE = 0.7


def persist(rec):
    RUNS.mkdir(exist_ok=True)
    with (RUNS / f"selfcon_{datetime.now():%Y%m%d}.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def done() -> set:
    return {json.loads(l)["case_id"]
            for p in RUNS.glob("selfcon_*.jsonl") for l in p.read_text().splitlines() if l.strip()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("-n", type=int, default=200)
    a = ap.parse_args()
    panel = DR.load_panel(); frame, _ = DR.build_frame()
    sel = DR.select(frame, 200, sample=True, panel=panel)
    cases = DR.assemble_cases(sel, panel)
    skip = done()
    todo = [c for c in cases if c["case_id"] not in skip][: a.n]
    print(f"  self-consistency: {len(cases)} cases; done {len(skip)}; to run {len(todo)}")
    print(f"  k={K} independent samples at temperature {TEMPERATURE}, plain majority vote")
    print(f"  compute-matched to the debate arm's five turns per case\n", flush=True)

    sysA = DR.SCAFFOLD.texts["sys_A_round0"]
    t0 = time.time(); n = adq = 0
    for i, c in enumerate(todo, 1):
        cid, psub = c["case_id"], c["panel"]
        if psub.empty:
            continue
        g = PV.gate_pre_reveal(c["block"].text, [], DR.DRUG_TERMS, c["orgs"],
                               c["rows"], DR.BS.canon_drug)
        if not g["ok"]:
            print(f"  ABORT {cid}: {g['reason']}", flush=True); continue

        user = DR.SCAFFOLD.texts["case_header"] + c["block"].text
        draws, texts = [], []
        for k in range(K):
            r = DR.ollama_chat(sysA, user, temperature=TEMPERATURE, seed=DR.SEED + k)
            draws.append(DR.parse_drug(r["content"])); texts.append(r["content"])
        tally = collections.Counter(draws)
        winner, votes = tally.most_common(1)[0]
        s = DR.score(winner, psub)
        # the single sample, for the temperature control
        s1 = DR.score(draws[0], psub)
        n += 1; adq += (s["outcome"] == "ADEQUATE")

        persist(dict(kind="selfcon", arm="D-SELFCON-1", case_id=cid,
                     micro_specimen_id=int(c["row"]["micro_specimen_id"]),
                     n_isolates=int(len(psub)), k=K, temperature=TEMPERATURE,
                     samples=draws, vote_counts=dict(tally),
                     n_distinct_samples=len(tally),
                     majority_drug=winner, majority_votes=votes,
                     majority_outcome=s["outcome"], majority_reason=s.get("reason"),
                     single_sample_drug=draws[0], single_sample_outcome=s1["outcome"],
                     unanimous=bool(len(tally) == 1),
                     gate_exemption="none - panel never shown in this arm", **g["audit"],
                     texts=texts, model=DR.MODEL_NAME, digest=DR.MODEL_DIGEST,
                     seed_base=DR.SEED, seconds=round(time.time() - t0, 1)))
        el = time.time() - t0
        print(f"  [{i}/{len(todo)}] {winner[:22]:24s} {votes}/{K} votes "
              f"{'UNANIMOUS' if len(tally)==1 else str(len(tally))+' distinct'}"
              f"  ({s['outcome'][:4]})  {el/i:.0f}s/case", flush=True)

    if n:
        print(f"\n  {n} cases. majority-vote adequate {adq}/{n} = {100*adq/n:.1f}%", flush=True)


if __name__ == "__main__":
    main()
