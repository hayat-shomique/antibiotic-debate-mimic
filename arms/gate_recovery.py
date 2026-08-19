#!/usr/bin/env python
"""Recover the C2 runs dropped by a provenance-gate regression.

THE DEFECT
----------
reveal_pass.py and clean_c2_pass.py both build a pre-reveal string by concatenating
the case block with the debate transcript, then run PV.gate_full over the whole thing:

    pre_reveal_text = case_block + transcript
    viol = PV.gate_full(pre_reveal_text, DR.DRUG_TERMS, orgs)

The transcript is MODEL-AUTHORED text. Under the three-provenance-class ruling a model
span is hashed at the inference boundary and MEASURED - it is never a gate abort, because
the model writing "the culture result may show resistance" is the model reasoning aloud,
not case data leaking in. debate_run.py already implements this correctly: gate_full runs
on the case block alone (line ~338) and assembled prompts go through gate_assembled_prompt
with the span registry (line ~185). The two downstream pass scripts kept the naive pattern.

CONSEQUENCE
-----------
  reveal arm    177 of 384 ordering-runs dropped   (persisted 207)
  clean C2       43 of 200 cases dropped           (persisted 157)

Every one of those aborts fired on a phrase inside a model turn: 'resistan', 'culture
result', 'suscept'. The dropout is NOT random - it removes precisely the runs where the
model was already reasoning about microbiology at round 0, which is plausibly correlated
with how it responds when the panel arrives. Any C2 rate computed on the survivors is
computed on a biased subsample, and clean_c2 additionally divided by len(todo)=200 rather
than by the number of records it actually wrote.

The 400-run main result is NOT affected: debate_run.py gates correctly.

WHAT THIS SCRIPT DOES
---------------------
Re-runs ONLY the dropped runs, under the correct policy, and appends them to NEW files:
    runs/reveal_recovered_<date>.jsonl
    runs/cleanc2_recovered_<date>.jsonl
Nothing existing is edited, overwritten or deleted. The original files stay exactly as
they are so the before/after comparison is auditable. Same model, same digest, same seed,
same system prompts and panel rendering - imported from the original modules rather than
retyped, so the recovered runs cannot drift from the originals.
"""
from __future__ import annotations
import argparse, json, time
from datetime import datetime
from pathlib import Path

import debate_run as DR
import provenance as PV
import reveal_pass as RP
import clean_c2_pass as CC

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"


# --------------------------------------------------------------------------- gate
def correct_gate(case_block: str, model_turns: list[str], orgs, panel_rows):
    """The ruling, applied properly.

    case block  -> dynamic case data   -> gate_full, abort on any hit
    model turns -> model spans         -> audit_model_span, measure; abort only on the
                                          canary condition (the model reconstructing
                                          panel rows), never on its own vocabulary
    Returns (ok, reason, audit_summary).
    """
    viol = [v for v in PV.gate_full(case_block, DR.DRUG_TERMS, orgs)
            if not v.startswith("drug term")]
    if viol:
        return False, f"case-block leakage {viol}", {}

    mentions, canary, rowmatch, quarantine = set(), set(), 0, False
    for span in model_turns:
        au = PV.audit_model_span(span, panel_rows, DR.BS.canon_drug)
        mentions |= set(au.organism_mentions)
        canary |= set(au.canary_hits)
        rowmatch = max(rowmatch, au.panel_row_matches)
        quarantine = quarantine or au.quarantine
        if au.abort:
            return False, f"model span reconstructed {au.panel_row_matches} panel rows", {}
    return True, "", {
        "span_organism_mentions": sorted(mentions),
        "span_canary_hits": sorted(canary),
        "span_panel_row_matches": rowmatch,
        "span_quarantine": bool(quarantine),
    }


def persist(rec: dict, stem: str) -> None:
    RUNS.mkdir(exist_ok=True)
    with (RUNS / f"{stem}_{datetime.now().strftime('%Y%m%d')}.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def loaded(stem: str) -> set:
    out = set()
    for p in RUNS.glob(f"{stem}_*.jsonl"):
        for l in p.read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                out.add((r["case_id"], r.get("ordering", "-")))
    return out


# ----------------------------------------------------------------- reveal recovery
def recover_reveal(limit=None):
    panel = DR.load_panel()
    frame, _ = DR.build_frame()
    sel = DR.select(frame, 200, sample=True, panel=panel)
    b1 = {c["case_id"]: c["block"].text for c in DR.assemble_cases(sel, panel)}
    b2 = {c["case_id"]: c["block"].text for c in DR.assemble_cases(sel, panel)}
    if b1 != b2:
        raise SystemExit("FATAL: case-block reconstruction is not deterministic")
    BLOCKS = b1

    recs = RP.load_completed()
    have = RP.already_revealed("reveal")          # what the ORIGINAL pass persisted
    have |= loaded("reveal_recovered")            # what THIS pass already persisted
    todo = [r for r in recs if (r["case_id"], r["ordering"]) not in have]
    if limit:
        todo = todo[:limit]
    print(f"  reveal: completed debate runs {len(recs)}; already have {len(have)}; "
          f"dropped-and-to-recover {len(todo)}", flush=True)

    t0 = time.time(); n = ok = 0
    for i, r in enumerate(todo, 1):
        spec = int(r["micro_specimen_id"])
        psub = DR.pathogenic_panel(panel, spec)
        if psub.empty:
            continue
        turns = sorted(r["turns"], key=lambda t: t["turn"])
        transcript = "".join(
            (DR.SCAFFOLD.texts["hdr_A"] if t["agent"] == "A" else DR.SCAFFOLD.texts["hdr_B"])
            + t["text"] for t in turns)
        case_block = r.get("case_block_text") or BLOCKS.get(r["case_id"])
        if not case_block:
            print(f"  SKIP {r['case_id']}: case block unavailable", flush=True)
            continue

        orgs = sorted({str(o) for o in psub["org_name"].dropna().unique()})
        rows = [(x["org_name"], x["ab_name"], x["interpretation"]) for _, x in psub.iterrows()]
        good, why, audit = correct_gate(case_block, [t["text"] for t in turns], orgs, rows)
        if not good:
            print(f"  GENUINE ABORT {r['case_id']}[{r['ordering']}]: {why}", flush=True)
            continue

        user = (DR.SCAFFOLD.texts["case_header"] + case_block + transcript
                + "\n\n--- MICROBIOLOGY RESULT NOW AVAILABLE ---\n" + RP.render_panel(psub))
        resp = DR.ollama_chat(RP.SYS_REVEAL, user)
        drug = DR.parse_drug(resp["content"]); sc = DR.score(drug, psub)
        prior = r["final_A"]
        rec = dict(kind="reveal_recovered", condition="C2_evidence",
                   case_id=r["case_id"], ordering=r["ordering"],
                   micro_specimen_id=spec, subject_id=r["subject_id"],
                   n_isolates=int(len(psub)),
                   round0_drug=r["round0_drug"], round0_outcome=r["round0_outcome"],
                   final_A=prior, final_A_outcome=r["final_A_outcome"],
                   reveal_drug=drug, reveal_outcome=sc["outcome"],
                   reveal_reason=sc.get("reason"),
                   changed_under_pressure=r["round0_drug"] != prior,
                   changed_under_evidence=prior != drug,
                   recovered_to_round0=drug == r["round0_drug"],
                   corrected_to_adequate=(r["final_A_outcome"] != "ADEQUATE"
                                          and sc["outcome"] == "ADEQUATE"),
                   gate_exemption="C2_reveal_declared",
                   recovered_from_gate_defect=True, **audit,
                   text=resp["content"], eval_count=resp["eval_count"],
                   prompt_eval_count=resp["prompt_eval_count"],
                   has_think_tag=("<think>" in resp["content"]),
                   model=DR.MODEL_NAME, digest=DR.MODEL_DIGEST, seed=DR.SEED,
                   seconds=round(resp["wall_s"], 1))
        persist(rec, "reveal_recovered"); n += 1; ok += (sc["outcome"] == "ADEQUATE")
        el = time.time() - t0
        print(f"  [{i}/{len(todo)}] {r['case_id']}[{r['ordering'][:1]}] {prior[:20]:22s}"
              f"({r['final_A_outcome'][:4]}) -> {drug[:20]:22s}({sc['outcome'][:4]})"
              f"  {el/i:.0f}s/run", flush=True)
    print(f"\n  reveal recovered {n} runs; {ok} adequate after the panel", flush=True)


# --------------------------------------------------------------- clean C2 recovery
def recover_cleanc2(limit=None):
    panel = DR.load_panel(); frame, _ = DR.build_frame()
    sel = DR.select(frame, 200, sample=True, panel=panel)
    blocks = {c["case_id"]: c for c in DR.assemble_cases(sel, panel)}
    deb = [json.loads(l) for l in (RUNS / "debate_20260818.jsonl").read_text().splitlines()
           if l.strip()]
    a1 = {}
    for r in deb:
        if r.get("kind") == "full" and r.get("ordering") == "A-first":
            t1 = next((t for t in sorted(r["turns"], key=lambda t: t["turn"])
                       if t["turn"] == 1), None)
            if t1:
                a1[r["case_id"]] = (t1["text"], r["round0_drug"], r["round0_outcome"],
                                    int(r["micro_specimen_id"]), int(r["subject_id"]))
    have = CC.done() | {c for c, _ in loaded("cleanc2_recovered")}
    todo = [c for c in sorted(a1) if c not in have][:limit] if limit else \
           [c for c in sorted(a1) if c not in have]
    print(f"  cleanC2: A-first round-0 for {len(a1)}; already have {len(have)}; "
          f"dropped-and-to-recover {len(todo)}", flush=True)

    t0 = time.time(); n = 0
    for i, cid in enumerate(todo, 1):
        c = blocks.get(cid)
        if not c:
            continue
        text0, d0, o0, mid, sid = a1[cid]
        psub = c["panel"]
        if psub.empty:
            continue
        good, why, audit = correct_gate(c["block"].text, [text0], c["orgs"], c["rows"])
        if not good:
            print(f"  GENUINE ABORT {cid}: {why}", flush=True)
            continue
        user = (DR.SCAFFOLD.texts["case_header"] + c["block"].text
                + DR.SCAFFOLD.texts["hdr_A"] + text0
                + "\n\n--- MICROBIOLOGY RESULT NOW AVAILABLE ---\n" + CC.render_panel(psub))
        resp = DR.ollama_chat(CC.SYS_CLEAN_C2, user)
        d1 = DR.parse_drug(resp["content"]); s1 = DR.score(d1, psub)
        persist(dict(kind="cleanc2_recovered", arm="D-CLEANC2-1",
                     condition="C2_clean_context", case_id=cid, micro_specimen_id=mid,
                     subject_id=sid, n_isolates=int(len(psub)),
                     round0_drug=d0, round0_outcome=o0,
                     c2_drug=d1, c2_outcome=s1["outcome"], c2_reason=s1.get("reason"),
                     changed=bool(d1 != d0),
                     applied_results_correctly=bool(s1["outcome"] == "ADEQUATE"),
                     gate_exemption="D-CLEANC2-1_declared",
                     recovered_from_gate_defect=True, **audit,
                     text=resp["content"], eval_count=resp["eval_count"],
                     prompt_eval_count=resp["prompt_eval_count"],
                     has_think_tag=("<think>" in resp["content"]),
                     model=DR.MODEL_NAME, digest=DR.MODEL_DIGEST, seed=DR.SEED,
                     seconds=round(resp["wall_s"], 1)), "cleanc2_recovered")
        n += 1
        el = time.time() - t0
        print(f"  [{i}/{len(todo)}] {cid} {d0[:20]:22s}({o0[:4]}) -> {d1[:20]:22s}"
              f"({s1['outcome'][:4]}) {el/i:.0f}s/case", flush=True)
    print(f"\n  cleanC2 recovered {n} cases", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["reveal", "cleanc2", "both", "dryrun"])
    ap.add_argument("-n", type=int, default=None)
    a = ap.parse_args()
    if a.mode == "dryrun":
        print("  dry run: gate policy only, no model calls")
    if a.mode in ("cleanc2", "both"):
        recover_cleanc2(a.n)
    if a.mode in ("reveal", "both"):
        recover_reveal(a.n)
