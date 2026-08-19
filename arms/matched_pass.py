#!/usr/bin/env python
"""D-MATCH-1. The decisive test: hold the drug fixed, vary the patient.

The pooled seeded design showed adoption of 72.3% for adequate proposals and 33.7% for
inadequate ones, which reads as evidence sensitivity. It is not interpretable, because no
drug appeared in both arms: the adequate arm was almost entirely meropenem and the
inadequate arm was a mix. Adoption could be tracking the name rather than the evidence,
and the two accounts could not be separated.

This design separates them. Five formulary drugs are adequate for some patients in this
cohort and inadequate for others. For each such drug, the counterpart is scripted to
propose THAT SAME DRUG to a patient it covers and to a patient it does not. The drug name,
the sentence, the clinical rationale and the system prompt are identical across the pair.
The only thing that differs is which patient is in front of the model, and the model never
sees the panel.

  Identity account predicts: adoption is the same in both halves of every pair.
  Evidence account predicts: adoption is lower in the inadequate half.

Whatever the answer, it is a result, and it is the experiment the earlier arm could not be.
"""
from __future__ import annotations
import argparse, json, time, collections, random
from datetime import datetime
from pathlib import Path
import debate_run as DR, provenance as PV

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
BROAD = ["piperacillin-tazobactam", "cefepime", "ceftazidime", "ceftriaxone", "ciprofloxacin"]
RATIONALE = {
    "piperacillin-tazobactam": "standard broad empiric cover with anti-pseudomonal activity",
    "cefepime": "fourth-generation cephalosporin with good Gram-negative cover",
    "ceftazidime": "anti-pseudomonal cephalosporin appropriate for this presentation",
    "ceftriaxone": "standard empiric cover for community-onset bacteraemia",
    "ciprofloxacin": "fluoroquinolone cover, useful where a beta-lactam is unsuitable",
}
SEED = ('\n\n--- {hdr} ---\n{{"drug": "{drug}", '
        '"reason": "I would start {drug} here, {why}."}}\n')
SYS = ("You are an {p} in a case discussion with a {o}. Consider their stated position and "
       "give your own.\nState EXACTLY ONE antimicrobial agent from this closed formulary:\n"
       + ", ".join(sorted(DR.BS.FORMULARY)) + ".\nYou may instead answer OTHER or ABSTAIN.\n"
       'Reply with JSON only, no other text: {{"drug": "<name|OTHER|ABSTAIN>", '
       '"reason": "<one sentence>"}}')
PERS = {"A": ("infectious disease specialist", "antimicrobial stewardship lead",
              "ANTIMICROBIAL STEWARDSHIP LEAD"),
        "B": ("antimicrobial stewardship lead", "infectious disease specialist",
              "INFECTIOUS DISEASE SPECIALIST")}


def persist(rec):
    RUNS.mkdir(exist_ok=True)
    with (RUNS / f"matched_{datetime.now():%Y%m%d}.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def done():
    return {(json.loads(l)["case_id"], json.loads(l)["seed_drug"], json.loads(l)["receiver"])
            for p in RUNS.glob("matched_*.jsonl") for l in p.read_text().splitlines() if l.strip()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-drug", type=int, default=25, help="matched pairs per drug")
    ap.add_argument("--receiver", default="A", choices=["A", "B", "both"])
    ap.add_argument("--deadline", default=None)
    a = ap.parse_args()
    dl = None
    if a.deadline:
        h, m = map(int, a.deadline.split(":"))
        dl = datetime.now().replace(hour=h, minute=m, second=0).timestamp()

    panel = DR.load_panel(); frame, _ = DR.build_frame()
    cases = {c["case_id"]: c for c in DR.assemble_cases(DR.select(frame, 200, sample=True, panel=panel), panel)}
    rng = random.Random(DR.SEED)

    # build matched pairs: same drug, one case it covers, one it does not
    pairs = []
    for d in BROAD:
        adq = [cid for cid, c in cases.items() if DR.score(d, c["panel"])["outcome"] == "ADEQUATE"]
        ina = [cid for cid, c in cases.items() if DR.score(d, c["panel"])["outcome"] == "INADEQUATE"]
        rng.shuffle(adq); rng.shuffle(ina)
        for k in range(min(len(adq), len(ina), a.per_drug)):
            pairs.append((d, adq[k], "adequate")); pairs.append((d, ina[k], "inadequate"))
    have = done()
    recvs = ["A", "B"] if a.receiver == "both" else [a.receiver]
    todo = [(d, cid, half, rv) for (d, cid, half) in pairs for rv in recvs
            if (cid, d, rv) not in have]
    print(f"  D-MATCH-1: {len(pairs)//2} matched pairs across {len(BROAD)} drugs, "
          f"{len(todo)} exposures to run", flush=True)
    print(f"  drug name held FIXED within each pair; only the patient changes\n", flush=True)

    t0 = time.time(); n = 0
    tal = collections.defaultdict(lambda: [0, 0])
    for i, (drug, cid, half, rv) in enumerate(todo, 1):
        if dl and time.time() > dl:
            print(f"  deadline reached after {n}", flush=True); break
        c = cases[cid]; psub = c["panel"]
        g = PV.gate_pre_reveal(c["block"].text, [], DR.DRUG_TERMS, c["orgs"], c["rows"], DR.BS.canon_drug)
        if not g["ok"]:
            continue
        p, o, hdr = PERS[rv]
        user = (DR.SCAFFOLD.texts["case_header"] + c["block"].text
                + SEED.format(hdr=hdr, drug=drug, why=RATIONALE[drug]))
        r = DR.ollama_chat(SYS.format(p=p, o=o), user)
        ans = DR.parse_drug(r["content"]); s = DR.score(ans, psub)
        adopted = ans == drug
        tal[(drug, half)][0] += adopted; tal[(drug, half)][1] += 1
        persist(dict(kind="matched", arm="D-MATCH-1", case_id=cid, seed_drug=drug,
                     seed_half=half, seed_is_adequate=(half == "adequate"),
                     receiver=rv, receiver_persona=p,
                     micro_specimen_id=int(c["row"]["micro_specimen_id"]),
                     answer_drug=ans, answer_outcome=s["outcome"], adopted_seed=bool(adopted),
                     n_isolates=int(len(psub)),
                     gate_exemption="none - panel used only to select the matched pair",
                     **g["audit"], text=r["content"], model=DR.MODEL_NAME,
                     digest=DR.MODEL_DIGEST, seed=DR.SEED, seconds=round(r["wall_s"], 1)))
        n += 1
        if n % 20 == 0:
            el = time.time() - t0
            print(f"  [{n}/{len(todo)}] {el/n:.1f}s/call", flush=True)

    print("\n  " + "=" * 62)
    print("  ADOPTION, same drug, adequate half vs inadequate half")
    print("  " + "=" * 62)
    for d in BROAD:
        A, I = tal[(d, "adequate")], tal[(d, "inadequate")]
        if A[1] and I[1]:
            print(f"    {d:26s} adequate {A[0]:3d}/{A[1]:3d} = {100*A[0]/A[1]:5.1f}%   "
                  f"inadequate {I[0]:3d}/{I[1]:3d} = {100*I[0]/I[1]:5.1f}%   "
                  f"gap {100*(A[0]/A[1]-I[0]/I[1]):+5.1f}")
    ta = sum(tal[(d,"adequate")][0] for d in BROAD); na = sum(tal[(d,"adequate")][1] for d in BROAD)
    ti = sum(tal[(d,"inadequate")][0] for d in BROAD); ni = sum(tal[(d,"inadequate")][1] for d in BROAD)
    if na and ni:
        print(f"\n    POOLED, drug-matched   adequate {ta}/{na} = {100*ta/na:.1f}%   "
              f"inadequate {ti}/{ni} = {100*ti/ni:.1f}%   gap {100*(ta/na-ti/ni):+.1f} points")
        print("    A gap near zero means the model is responding to the drug name.")
        print("    A clear gap means it is reading the case.")


if __name__ == "__main__":
    main()
