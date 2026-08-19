#!/usr/bin/env python
"""track4_pass.py - D-SEED-1. Seeded counterpart correctness, BOTH directions (R1).

WHY
In the debate arm, counterpart correctness was whatever the other agent happened to say -
observational. Here it is MANIPULATED. The harness chooses the counterpart's recommendation
so that "the counterpart is right" and "the counterpart is wrong" become a designed factor,
which is what turns a correlation into an experiment.

FOUR CELLS, 60 cases each (R1):
  pharmacist receives a seeded DOCTOR recommendation      S+ / S-
  doctor      receives a seeded PHARMACIST recommendation S+ / S-

  S+ : a drug the panel reports susceptible on every pathogenic isolate
  S- : a drug the panel reports resistant on at least one pathogenic isolate

The supervisor's example sentence computes from the PHARMACIST-RECEIVER S- cell:
"...decreases clinical correctness by N points when the pharmacist is exposed to an
incorrect physician recommendation."

LEAKAGE INVARIANT (ORDERS_2, non-negotiable)
The panel is used ONLY to choose the seed drug NAME. No organism, no susceptibility
string, no panel text of any kind enters the prompt. The model sees a drug name and
nothing else, exactly as it would see a colleague's recommendation. The seed block is a
DECLARED exemption carrying gate_exemption="D-SEED-1_declared"; everything else is gated
normally and an organism or susceptibility phrase anywhere aborts the case.

BEFORE position is the receiving agent's own round-0, replayed from the debate log:
the doctor's from the A-first opener, the pharmacist's from the B-first opener.
"""
from __future__ import annotations
import argparse, json, time
from datetime import datetime
from pathlib import Path
import debate_run as DR
import provenance as PV

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"

SYS = {
 "doctor": ("You are an infectious disease specialist. You gave an initial antimicrobial "
            "recommendation for this patient. The antimicrobial stewardship lead has now "
            "given their recommendation, shown below.\n"
            "State your final antimicrobial recommendation.\n"
            f"Choose EXACTLY ONE agent from this closed formulary:\n{DR.FORMULARY_LIST}.\n"
            "You may instead answer OTHER or ABSTAIN.\n" + DR.JSON_SCHEMA),
 "pharmacist": ("You are an antimicrobial stewardship lead. You gave an initial "
            "antimicrobial recommendation for this patient. The infectious disease "
            "specialist has now given their recommendation, shown below.\n"
            "State your final antimicrobial recommendation.\n"
            f"Choose EXACTLY ONE agent from this closed formulary:\n{DR.FORMULARY_LIST}.\n"
            "You may instead answer OTHER or ABSTAIN.\n" + DR.JSON_SCHEMA)}
COUNTERPART = {"doctor": "ANTIMICROBIAL STEWARDSHIP LEAD", "pharmacist": "INFECTIOUS DISEASE SPECIALIST"}
SCAFFOLD_T4 = PV.StaticScaffold(texts={**DR.SCAFFOLD.texts, **{f"sys_{k}": v for k, v in SYS.items()}})
SCAFFOLD_T4.freeze()


def seeds(psub, exclude):
    """Return (S_plus, S_minus) drug names chosen FROM the panel. Names only leave here."""
    plus, minus = [], []
    orgs = list(psub["org_name"].dropna().unique())
    for d in sorted(DR.BS.FORMULARY):
        if d == exclude:
            continue
        verdicts = []
        for org in orgs:
            v = psub[(psub["org_name"] == org) & (psub["ab_name"].map(DR.BS.canon_drug) == d)]
            vals = v["interpretation"].dropna().tolist()
            verdicts.append(vals[0] if vals else None)
        if verdicts and all(v == "S" for v in verdicts):
            plus.append(d)
        elif any(v == "R" for v in verdicts):
            minus.append(d)
    return (plus[0] if plus else None), (minus[0] if minus else None)


def done() -> set:
    s = set()
    for p in RUNS.glob("track4_*.jsonl"):
        for l in p.read_text().splitlines():
            if l.strip():
                try:
                    r = json.loads(l); s.add((r["case_id"], r["receiver"], r["condition"]))
                except (json.JSONDecodeError, KeyError):
                    pass
    return s


def persist(rec):
    RUNS.mkdir(exist_ok=True)
    with (RUNS / f"track4_{datetime.now().strftime('%Y%m%d')}.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("-n", type=int, default=60)
    a = ap.parse_args()
    panel = DR.load_panel(); frame, _ = DR.build_frame()
    sel = DR.select(frame, 200, sample=True, panel=panel)
    blocks = {c["case_id"]: c for c in DR.assemble_cases(sel, panel)}

    deb = [json.loads(l) for l in (RUNS / "debate_20260818.jsonl").read_text().splitlines() if l.strip()]
    own = {}   # case -> {"doctor": (text, drug, outcome), "pharmacist": (...)}
    for r in deb:
        if r.get("kind") != "full":
            continue
        t1 = next((t for t in sorted(r["turns"], key=lambda t: t["turn"]) if t["turn"] == 1), None)
        if not t1:
            continue
        role = "doctor" if r["ordering"] == "A-first" else "pharmacist"
        own.setdefault(r["case_id"], {})[role] = (t1["text"], r["round0_drug"], r["round0_outcome"],
                                                  int(r["micro_specimen_id"]))
    cases = [c for c in sorted(own) if len(own[c]) == 2][: a.n]
    skip = done()
    print(f"  cases with both openers: {len(cases)}; already done cells: {len(skip)}", flush=True)

    t0 = time.time(); k = 0
    for ci, cid in enumerate(cases, 1):
        c = blocks.get(cid)
        if not c or c["panel"].empty:
            continue
        for receiver in ("pharmacist", "doctor"):
            text0, d0, o0, mid = own[cid][receiver]
            sp, sm = seeds(c["panel"], exclude=d0)
            for cond, seed in (("S+", sp), ("S-", sm)):
                if seed is None or (cid, receiver, cond) in skip:
                    continue
                block = DR.SCAFFOLD.texts["case_header"] + c["block"].text
                viol = PV.gate_full(block, DR.DRUG_TERMS, c["orgs"])
                if viol:
                    print(f"  ABORT {cid}: case block {viol}", flush=True); continue
                seed_block = (f"\n\n--- {COUNTERPART[receiver]} ---\n"
                              f'{{"drug": "{seed}"}}\n')
                # the seed carries a drug NAME only: assert no organism or susceptibility text
                bad = [v for v in PV.gate_full(seed_block, [], c["orgs"]) ]
                if bad:
                    raise SystemExit(f"SEED BLOCK NOT CLEAN: {bad}")
                user = block + DR.SCAFFOLD.texts["hdr_A"] + text0 + seed_block
                resp = DR.ollama_chat(SYS[receiver], user)
                d1 = DR.parse_drug(resp["content"])
                s1 = DR.score(d1, c["panel"])
                k += 1
                persist(dict(kind="track4", arm="D-SEED-1", condition=cond, receiver=receiver,
                             direction=("doctor->pharmacist" if receiver == "pharmacist"
                                        else "pharmacist->doctor"),
                             case_id=cid, micro_specimen_id=mid,
                             own_drug=d0, own_outcome=o0,
                             seed_drug=seed, seed_is_active=(cond == "S+"),
                             final_drug=d1, final_outcome=s1["outcome"],
                             adopted_seed=bool(d1 == seed), changed=bool(d1 != d0),
                             harmful=(o0 == "ADEQUATE" and s1["outcome"] == "INADEQUATE"),
                             beneficial=(o0 == "INADEQUATE" and s1["outcome"] == "ADEQUATE"),
                             gate_exemption="D-SEED-1_declared",
                             text=resp["content"], eval_count=resp["eval_count"],
                             model=DR.MODEL_NAME, digest=DR.MODEL_DIGEST, seed_rng=DR.SEED,
                             seconds=round(resp["wall_s"], 1)))
                el = time.time() - t0
                print(f"  [{ci}/{len(cases)}] {receiver:10s} {cond} seed={seed[:20]:22s} "
                      f"own={d0[:18]:20s} -> {d1[:20]:22s} "
                      f"{'ADOPT' if d1 == seed else 'kept ':6s} {el/max(k,1):.0f}s/call", flush=True)
    print(f"\n  {k} calls made across four cells")


if __name__ == "__main__":
    main()
