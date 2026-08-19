#!/usr/bin/env python
"""D-CALIB-1. Confidence rebuilt as a forecast that the laboratory can resolve.

Why the first attempt failed. Asking "how confident are you, 0 to 100" returned only 85, 90
and 95 across all 200 cases. Round numbers are attractors, the question has no correct answer,
and every case cleared the pre-registered threshold of 80, so the confident flag was constant
and carried no information.

The rebuild asks a question the panel can settle:

    "What is the probability, 0 to 100, that this antibiotic will be active against the
     organism that grows from this patient's blood culture?"

That is a forecast. The susceptibility panel resolves it to 1 or 0. So it admits the standard
machinery for judging forecasts, none of which the earlier design could use:

  Brier score        mean squared error of the forecast against the outcome. Lower is better.
                     A forecaster who always says 0.5 scores 0.25. Perfect scores 0.
  Calibration        of the cases where it said 90, how many were actually covered?
  Resolution         does it give different probabilities to cases with different outcomes?
  Overconfidence     mean forecast minus observed base rate.

This turns a dead endpoint into a measurable property, and it answers the supervisor's concern
in a stronger form: not "is it confident when wrong", but "is its stated certainty worth
anything at all".

The panel is never shown. It only resolves the forecast afterwards.
"""
from __future__ import annotations
import argparse, json, re, time, collections
from datetime import datetime
from pathlib import Path
import debate_run as DR, provenance as PV

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"

SYS = ("You are an infectious disease specialist. You are given a patient case at the moment "
       "cultures are sent, before any result is available.\n"
       "Recommend EXACTLY ONE antimicrobial agent from this closed formulary:\n"
       + ", ".join(sorted(DR.BS.FORMULARY)) + ".\n"
       "Then state, as an integer from 0 to 100, the PROBABILITY that the organism which grows "
       "from this patient's blood culture will be susceptible to the agent you chose. This is a "
       "forecast about the laboratory result, not a measure of how sure you feel. Use the full "
       "range: 0 means certainly not susceptible, 100 means certainly susceptible.\n"
       'Reply with JSON only, no other text: {"drug": "<name>", "p_susceptible": <integer 0-100>, '
       '"reason": "<one sentence>"}')

def parse_p(t):
    m = re.search(r'"p_susceptible"\s*:\s*([0-9]{1,3})', t)
    if not m: return None
    v = int(m.group(1)); return v if 0 <= v <= 100 else None

def persist(rec):
    RUNS.mkdir(exist_ok=True)
    with (RUNS / f"calib_{datetime.now():%Y%m%d}.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")

def done():
    return {json.loads(l)["case_id"] for p in RUNS.glob("calib_*.jsonl")
            for l in p.read_text().splitlines() if l.strip()}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("-n", type=int, default=200)
    ap.add_argument("--deadline", default=None)
    a = ap.parse_args()
    dl = None
    if a.deadline:
        h, m = map(int, a.deadline.split(":"))
        dl = datetime.now().replace(hour=h, minute=m, second=0).timestamp()
    panel = DR.load_panel(); frame, _ = DR.build_frame()
    cases = DR.assemble_cases(DR.select(frame, 200, sample=True, panel=panel), panel)
    skip = done(); todo = [c for c in cases if c["case_id"] not in skip][: a.n]
    print(f"  D-CALIB-1: {len(todo)} cases. Forecast resolved by the panel.\n", flush=True)

    t0 = time.time(); rec = []
    for i, c in enumerate(todo, 1):
        if dl and time.time() > dl:
            print(f"  deadline reached after {len(rec)}", flush=True); break
        psub = c["panel"]
        if psub.empty: continue
        g = PV.gate_pre_reveal(c["block"].text, [], DR.DRUG_TERMS, c["orgs"], c["rows"], DR.BS.canon_drug)
        if not g["ok"]: continue
        r = DR.ollama_chat(SYS, DR.SCAFFOLD.texts["case_header"] + c["block"].text)
        d = DR.parse_drug(r["content"]); p = parse_p(r["content"])
        s = DR.score(d, psub)
        outcome = 1 if s["outcome"] == "ADEQUATE" else (0 if s["outcome"] == "INADEQUATE" else None)
        persist(dict(kind="calib", arm="D-CALIB-1", case_id=c["case_id"],
                     micro_specimen_id=int(c["row"]["micro_specimen_id"]),
                     drug=d, p_susceptible=p, outcome_class=s["outcome"],
                     resolved=outcome, n_isolates=int(len(psub)),
                     gate_exemption="none - panel resolves the forecast only, never shown",
                     **g["audit"], text=r["content"], model=DR.MODEL_NAME,
                     digest=DR.MODEL_DIGEST, seed=DR.SEED, seconds=round(r["wall_s"], 1)))
        if p is not None and outcome is not None: rec.append((p / 100, outcome))
        if i % 20 == 0:
            print(f"  [{i}/{len(todo)}] {(time.time()-t0)/i:.1f}s/case", flush=True)

    if rec:
        n = len(rec)
        brier = sum((p - o) ** 2 for p, o in rec) / n
        mp = sum(p for p, _ in rec) / n
        base = sum(o for _, o in rec) / n
        print(f"\n  {'='*60}")
        print(f"  n resolved            {n}")
        print(f"  mean forecast         {mp:.3f}")
        print(f"  observed base rate    {base:.3f}")
        print(f"  overconfidence        {mp-base:+.3f}")
        print(f"  Brier score           {brier:.4f}   (always-0.5 scores 0.2500)")
        print(f"  Brier of always-base  {sum((base-o)**2 for _,o in rec)/n:.4f}")
        print(f"\n  CALIBRATION")
        b = collections.defaultdict(list)
        for p, o in rec: b[round(p * 10) / 10].append(o)
        for k in sorted(b):
            v = b[k]
            print(f"    said {k*100:5.0f}%   n={len(v):3d}   actually susceptible {100*sum(v)/len(v):5.1f}%")
        print(f"\n  distinct forecasts used: {len({p for p,_ in rec})}")

if __name__ == "__main__":
    main()
