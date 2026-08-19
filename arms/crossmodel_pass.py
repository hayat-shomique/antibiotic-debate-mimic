#!/usr/bin/env python
"""crossmodel_pass.py - D-CROSS-1. Two DIFFERENT models in the two chairs (R2).

Qwen3-4B is the infectious disease specialist. MedGemma-4B is the antimicrobial
stewardship lead. Everything else is held identical to the same-model debate arm: the
same 5-turn A-first protocol, the same personas, the same scaffold strings, the same
options, the same 60 cases.

WHY IT MATTERS
In the same-model arm both chairs are one checkpoint, so a deference asymmetry cannot be
a capability difference, it has to be persona or position. Putting a different model in
the pharmacist's chair asks whether the deference survives when the counterpart is
genuinely a different system, and whether a medically pretrained counterpart changes what
the specialist does.

MEMORY
Both are 4B. Measured resident footprint is about 3.9 GB for Qwen and about 5 GB for
MedGemma, roughly 9 GB together, inside 16 GB with the OS. Neither is evicted mid-case;
alternating turns would otherwise reload a model ten times per case.

REVIEW GATE (R2): nothing from this arm reaches a slide until the human has seen one
complete annotated transcript and the ten-line explainer, and has said yes.
"""
from __future__ import annotations
import argparse, json, time, urllib.request
from datetime import datetime
from pathlib import Path
import debate_run as DR
import provenance as PV

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
DOCTOR = "qwen3:4b-instruct-2507-q4_K_M"
PHARM = "medgemma:4b-it-q4_K_M"
ORDER = ["A", "B", "A", "B", "A"]


def chat(model, system, user, timeout=300):
    body = json.dumps({"model": model, "stream": False, "think": DR.THINK,
                       "keep_alive": DR.KEEP_ALIVE, "options": DR.OPTIONS,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request("http://localhost:11434/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return {"content": d.get("message", {}).get("content", ""),
            "eval_count": d.get("eval_count"),
            "prompt_eval_count": d.get("prompt_eval_count"),
            "wall_s": time.time() - t0}


def done() -> set:
    s = set()
    for p in RUNS.glob("crossmodel_*.jsonl"):
        for l in p.read_text().splitlines():
            if l.strip():
                try:
                    s.add(json.loads(l)["case_id"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return s


def persist(rec):
    RUNS.mkdir(exist_ok=True)
    with (RUNS / f"crossmodel_{datetime.now().strftime('%Y%m%d')}.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("-n", type=int, default=60)
    a = ap.parse_args()
    tags = json.loads(urllib.request.urlopen("http://localhost:11434/api/tags", timeout=20).read())
    have = {m["name"]: m.get("digest") for m in tags.get("models", [])}
    for m in (DOCTOR, PHARM):
        if m not in have:
            raise SystemExit(f"model not present: {m}")
    print(f"  doctor     {DOCTOR}  {have[DOCTOR][:20]}")
    print(f"  pharmacist {PHARM}  {have[PHARM][:20]}", flush=True)

    panel = DR.load_panel(); frame, _ = DR.build_frame()
    sel = DR.select(frame, 200, sample=True, panel=panel)
    cases = DR.assemble_cases(sel, panel)[: a.n]
    skip = done()
    todo = [c for c in cases if c["case_id"] not in skip]
    print(f"  cases {len(cases)}, done {len(skip)}, to run {len(todo)}", flush=True)

    t0 = time.time()
    for i, c in enumerate(todo, 1):
        reg = PV.SpanRegistry()
        transcript = ""
        turns = []
        for n, who in enumerate(ORDER, 1):
            if who == "A":
                model = DOCTOR
                sysname = "sys_A_round0" if n == 1 else "sys_A_debate"
            else:
                model = PHARM
                sysname = "sys_B"
            system = DR.SCAFFOLD.texts[sysname]
            user = DR.SCAFFOLD.texts["case_header"] + c["block"].text + transcript
            g = PV.gate_assembled_prompt(system + "\n" + user, reg, DR.SCAFFOLD,
                                         DR.DRUG_TERMS, c["orgs"], c["rows"], DR.BS.canon_drug)
            if g["abort"]:
                raise SystemExit(f"{c['case_id']} turn {n}: LEAKAGE {g['residue_violations']}")
            r = chat(model, system, user)
            reg.register(r["content"])
            drug = DR.parse_drug(r["content"])
            turns.append(dict(turn=n, agent=who, model=model, drug=drug, text=r["content"],
                              eval_count=r["eval_count"], wall_s=round(r["wall_s"], 2)))
            transcript += (DR.SCAFFOLD.texts["hdr_A"] if who == "A"
                           else DR.SCAFFOLD.texts["hdr_B"]) + r["content"]

        at = [t for t in turns if t["agent"] == "A"]; bt = [t for t in turns if t["agent"] == "B"]
        fa, fb, r0 = at[-1]["drug"], bt[-1]["drug"], at[0]["drug"]
        sa, sb, s0 = (DR.score(x, c["panel"]) for x in (fa, fb, r0))
        adopt = sum(1 for j, t in enumerate(turns) if t["agent"] == "A" and j > 0
                    and t["drug"] == next((u["drug"] for u in reversed(turns[:j])
                                           if u["agent"] == "B"), None))
        persist(dict(kind="crossmodel", arm="D-CROSS-1", case_id=c["case_id"],
                     micro_specimen_id=int(c["row"]["micro_specimen_id"]),
                     doctor_model=DOCTOR, pharmacist_model=PHARM,
                     doctor_digest=have[DOCTOR], pharmacist_digest=have[PHARM],
                     round0_drug=r0, round0_outcome=s0["outcome"],
                     final_A=fa, final_A_outcome=sa["outcome"],
                     final_B=fb, final_B_outcome=sb["outcome"],
                     agreement=bool(fa == fb), changed_A=bool(r0 != fa),
                     doctor_adopted_pharmacist_count=adopt,
                     turns=turns, seed=DR.SEED,
                     seconds=round(sum(t["wall_s"] for t in turns), 1)))
        el = time.time() - t0
        print(f"  [{i}/{len(todo)}] r0={r0[:20]:22s} A={fa[:20]:22s}({sa['outcome'][:4]}) "
              f"B={fb[:20]:22s}({sb['outcome'][:4]}) {'agree' if fa == fb else 'DIFFER':6s} "
              f"{el/i:.0f}s/case", flush=True)


if __name__ == "__main__":
    main()
