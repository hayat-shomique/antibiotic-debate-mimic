#!/usr/bin/env python
"""acceptance.py - pipe-cleaner acceptance checks (a)-(j).

Every check prints PASS or FAIL. A gate never observed firing is presumed dead
code, so (a) deliberately plants real panel content and demands the gate fire.
"""
from __future__ import annotations

import ast
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

import case_assembly as CA
import provenance as PV
import debate_run as DR

ROOT = Path(__file__).resolve().parent
RESULTS: list[tuple[str, bool, str]] = []


def rec(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))
    return ok


def hdr(t):
    print(f"\n{'='*78}\n{t}\n{'='*78}")


# ---------------------------------------------------------------------------
def check_module_isolation():
    """Requirement 4: prompt assembly must have NO code path to panel_rows."""
    hdr("REQUIREMENT 4 - prompt-assembly module isolation")
    src = (ROOT / "case_assembly.py").read_text()
    tree = ast.parse(src)
    imports = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imports |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            imports.add(n.module or "")
    banned_imports = {i for i in imports if "panel" in i.lower() or "brain_scoring" in i.lower()}
    # Strip comments AND docstrings: the module's own docstring legitimately
    # names panel columns to state the prohibition. Only executable code counts.
    doc_nodes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            b = getattr(node, "body", [])
            if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
               and isinstance(b[0].value.value, str):
                doc_nodes.add(id(b[0].value))
    live_strings, live_names = [], []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
           and id(node) not in doc_nodes:
            live_strings.append(node.value)
        elif isinstance(node, ast.Name):
            live_names.append(node.id)
        elif isinstance(node, ast.Attribute):
            live_names.append(node.attr)
    hay = " ".join(live_strings + live_names).lower()
    banned_strings = [t for t in ("panel_rows", "org_name", "ab_name",
                                  "microbiologyevents", "susceptib")
                      if t in hay]
    ok = not banned_imports and not banned_strings
    rec("case_assembly has no panel import", not banned_imports, str(sorted(banned_imports)))
    rec("case_assembly source names no panel column", not banned_strings, str(banned_strings))
    return ok


def check_c_mapping_audit(panel):
    """(c) formulary -> panel ab_name mapping table + UNDETERMINED rate."""
    hdr("(c) MAPPING AUDIT - formulary <-> panel ab_name")
    names = panel["ab_name"].dropna().astype(str).str.strip().unique()
    mapped, unmapped = {}, []
    for n in sorted(names):
        c = DR.BS.canon_drug(n)
        if c:
            mapped.setdefault(c, []).append(n)
        else:
            unmapped.append(n)
    print(f"\n  {'canonical formulary drug':32s} {'panel ab_name(s) it maps from':44s} rows")
    print("  " + "-"*80)
    total = 0
    for k in sorted(DR.BS.FORMULARY):
        src = mapped.get(k, [])
        nrows = int(panel["ab_name"].astype(str).str.strip().isin(src).sum()) if src else 0
        total += nrows
        flag = "" if src else "   <-- NO PANEL ROWS"
        print(f"  {k:32s} {', '.join(src) if src else '(none)':44s} {nrows:>6,}{flag}")
    print("  " + "-"*80)
    print(f"  mapped rows {total:,} / {len(panel):,} = {100*total/len(panel):.1f}%")
    print(f"\n  panel ab_name values NOT in formulary ({len(unmapped)}):")
    for u in unmapped:
        print(f"    - {u}  ({int((panel['ab_name'].astype(str).str.strip()==u).sum()):,} rows)")
    missing = [k for k in DR.BS.FORMULARY if not mapped.get(k)]
    rec("every formulary drug maps to >=1 panel ab_name", not missing, str(missing))

    interp = panel["interpretation"].value_counts(dropna=False).to_dict()
    print(f"\n  interpretation distribution: { {str(k): int(v) for k,v in interp.items()} }")
    n_none = int(panel["interpretation"].isna().sum())
    print(f"  unusable verdicts (P/blank -> None): {n_none:,} ({100*n_none/len(panel):.1f}%)")
    return not missing


def check_g_intermediate():
    """(g) explicit statement of the 'I' branch."""
    hdr("(g) INTERMEDIATE ('I') BRANCH")
    cfg = DR.BS.ScoringConfig()
    print(f"  intermediate_as             = {cfg.intermediate_as!r}")
    print(f"  untested_policy             = {cfg.untested_policy!r}")
    print(f"  require_all_pathogens_covered = {cfg.require_all_pathogens_covered}")
    print(f"  combination_rule            = {cfg.combination_rule!r}")
    print(f"  use_intrinsic_resistance    = {cfg.use_intrinsic_resistance}")
    print("\n  BEHAVIOUR: with intermediate_as='separate', an isolate whose best")
    print("  available verdict is I yields state 'intermediate_only' and the case")
    print("  outcome INTERMEDIATE_ONLY. It is reported as its own outcome and is")
    print("  NEVER folded into ADEQUATE or INADEQUATE.")
    print("  Untested agent -> UNDETERMINED (kept out of the binary, not counted wrong).")
    return rec("'I' reported separately, never collapsed", cfg.intermediate_as == "separate")


def check_h_concur():
    """(h) concur rule."""
    hdr("(h) CONCUR RULE")
    print("  If B returns no parsable agent AND the text expresses concurrence")
    print(f"  (regex {DR.CONCUR_RE.pattern!r}),")
    print("  B's position CARRIES FORWARD from A's latest parsed position and the")
    print("  turn is flagged position_source='implicit'. No concurrence language")
    print("  and no parsable agent -> INVALID.")
    t = "I concur with the specialist; no objection to the plan as stated."
    ok1 = bool(DR.CONCUR_RE.search(t))
    ok2 = not DR.CONCUR_RE.search("I disagree entirely and would choose differently.")
    rec("concurrence detected in agreeing text", ok1)
    rec("concurrence NOT detected in disagreeing text", ok2)
    return ok1 and ok2


def check_a_fault_injection(case):
    """(a) plant real panel content; the gate must fire."""
    hdr("(a) FAULT INJECTION - gate must be observed firing")
    if not case["rows"]:
        return rec("fault injection", False, "case has no panel rows to plant")
    org, ab, interp = case["rows"][0]
    canon = DR.BS.canon_drug(ab) or str(ab)
    print(f"  planting real panel row -> org={org!r} ab={ab!r} interp={interp!r}")

    # A1. panel content in the CASE BLOCK -> must ABORT
    poisoned = case["block"].text + f"\nOrganism isolated: {org}"
    v1 = PV.gate_full(poisoned, DR.DRUG_TERMS, case["orgs"])
    rec("A1 organism planted in case block -> gate fires", bool(v1), f"{len(v1)} violation(s)")

    poisoned2 = case["block"].text + f"\nAgent tested: {ab}"
    v2 = PV.gate_full(poisoned2, DR.DRUG_TERMS, case["orgs"])
    rec("A2 panel drug planted in case block -> gate fires", bool(v2), f"{len(v2)} violation(s)")

    # A3. clean block must NOT fire (guards against a gate that always fires)
    v3 = PV.gate_full(case["block"].text, DR.DRUG_TERMS, case["orgs"])
    rec("A3 clean case block -> gate silent", not v3, str(v3))

    # B. panel content inside a FAKE MODEL TURN -> quarantine, not abort
    fake = (f"In my view {canon} is appropriate. Note the isolate {org} was "
            f"reported {interp} to {canon} on the panel.")
    audit = PV.audit_model_span(fake, case["rows"], DR.BS.canon_drug)
    rec("B1 model span mentioning organism is measured", bool(audit.organism_mentions),
        f"mentions={audit.organism_mentions[:3]}")
    rec("B2 drug+interpretation co-occurrence -> QUARANTINE", audit.quarantine,
        f"canary={audit.canary_hits[:2]}")

    # C. the smuggling hole: unregistered text is treated as harness-assembled
    reg = PV.SpanRegistry()
    smuggled = DR.SCAFFOLD.texts["case_header"] + case["block"].text + \
        f"\n\n--- INFECTIOUS DISEASE SPECIALIST ---\nOrganism isolated: {org}"
    r = PV.gate_assembled_prompt(smuggled, reg, DR.SCAFFOLD, DR.DRUG_TERMS,
                                 case["orgs"], case["rows"], DR.BS.canon_drug)
    rec("C1 unregistered 'model turn' is NOT exempt -> abort", r["abort"],
        f"residue violations={len(r['residue_violations'])}")

    # D. genuinely registered model span IS exempt from abort
    reg2 = PV.SpanRegistry()
    real_span = f"I recommend {canon} for empiric cover."
    reg2.register(real_span)
    prompt2 = DR.SCAFFOLD.texts["case_header"] + case["block"].text + \
        DR.SCAFFOLD.texts["hdr_A"] + real_span
    r2 = PV.gate_assembled_prompt(prompt2, reg2, DR.SCAFFOLD, DR.DRUG_TERMS,
                                  case["orgs"], case["rows"], DR.BS.canon_drug)
    rec("D1 registered model span naming a drug -> no abort", not r2["abort"],
        f"spans={r2['n_model_spans']}")
    return True


def run_pass(cases, label):
    print(f"\n  --- run pass '{label}' ---")
    out = []
    for c in cases:
        for full, runner in DR.run_case(c):        # BOTH orderings
            out.append({"full": full, "runner": runner, "secs": full["seconds"]})
            print(f"    {c['case_id']:>18} [{full['ordering']:>7}] "
                  f"r0={full['round0_drug']}/{full['round0_outcome']}"
                  f"  A={full['final_A']}/{full['final_A_outcome']}"
                  f"  B={full['final_B']}/{full['final_B_outcome']}  {full['seconds']}s")
    return out


def check_d_determinism(p1, p2):
    hdr("(d) DETERMINISM - same inputs twice")
    allok = True
    for a, b in zip(p1, p2):
        ta = [(t["agent"], t["drug"], t["text"]) for t in a["full"]["turns"]]
        tb = [(t["agent"], t["drug"], t["text"]) for t in b["full"]["turns"]]
        pos = [x[:2] for x in ta] == [x[:2] for x in tb]
        txt = ta == tb
        lbl = f"{a['full']['case_id']}[{a['full']['ordering']}]"
        allok &= rec(f"{lbl} parsed positions identical", pos)
        allok &= rec(f"{lbl} transcripts byte-identical", txt,
                     "" if txt else "text differs between runs")
    return allok


def check_e_think(passes):
    hdr("(e) THINK-OFF VERIFIED IN OUTPUT")
    hits = []
    for p in passes:
        for r in p:
            for t in r["full"]["turns"]:
                if "<think>" in t["text"] or "</think>" in t["text"]:
                    hits.append((r["full"]["case_id"], t["turn"]))
    return rec("zero '<think>' in any raw output", not hits, f"{len(hits)} hit(s)")


def check_f_state_isolation(p1):
    hdr("(f) STATE ISOLATION between cases")
    if len(p1) < 2:
        return rec("state isolation", False, "need 2 cases")
    byc = {}
    for r in p1:
        byc.setdefault(r["full"]["case_id"], r)
    ks = list(byc)
    if len(ks) < 2:
        return rec("state isolation", False, "need 2 distinct cases")
    c1r, c2r = byc[ks[0]], byc[ks[1]]
    c1_block = c1r["runner"].block
    c2_block = c2r["runner"].block
    c2_prompts = " ".join(x["user"] for x in c2r["runner"].prompts)
    # Two different patients can legitimately share a field VALUE ("Insurance:
    # Medicare"). Only case-DISTINGUISHING lines can evidence state bleed.
    c2_lines = set(c2_block.splitlines())
    distinguishing = [l for l in c1_block.splitlines()
                      if l.strip() and l not in c2_lines]
    bleed = [l for l in distinguishing if l in c2_prompts]
    ok0 = rec("case 1 block does not appear whole in case 2 prompts",
              c1_block not in c2_prompts)
    ok1 = ok0 and rec(f"no case-1-distinguishing line in case 2 prompts "
                      f"({len(distinguishing)} distinguishing)", not bleed, str(bleed[:2]))
    c1_texts = [t["text"] for t in c1r["full"]["turns"]]
    bleed2 = [t[:40] for t in c1_texts if t and t in c2_prompts]
    ok2 = rec("case 2 prompts contain no case 1 model output", not bleed2, str(bleed2[:1]))
    return ok1 and ok2


def check_b_join_integrity(p1, panel):
    hdr("(b) JOIN INTEGRITY")
    day = time.strftime("%Y%m%d")
    path = ROOT / "runs" / f"debate_{day}.jsonl"
    lines = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    ok1 = rec("every JSONL line carries case_id", all("case_id" in l for l in lines),
              f"{len(lines)} line(s)")
    ok2 = True
    for r in p1:
        f = r["full"]
        want = int(f["micro_specimen_id"])
        sub = DR.pathogenic_panel(panel, want)
        same = len(sub) == f["n_isolates"]
        ok2 &= rec(f"{f['case_id']} scored panel belongs to its micro_specimen_id", same,
                   f"panel rows {len(sub)} vs recorded {f['n_isolates']}")
        cid_ok = f["case_id"].endswith(str(want))
        ok2 &= rec(f"{f['case_id']} case_id encodes micro_specimen_id", cid_ok)
    return ok1 and ok2


def check_i_hand_verify(p1, panel):
    hdr("(i) HAND RECOMPUTATION of one round-0 verdict")
    r = p1[0]["full"]
    drug, spec = r["round0_drug"], int(r["micro_specimen_id"])
    sub = DR.pathogenic_panel(panel, spec)
    print(f"  case {r['case_id']}  round-0 recommendation = {drug!r}")
    print(f"  machine outcome = {r['round0_outcome']}")
    if drug in (DR.ABSTAIN, DR.OTHER, DR.INVALID):
        print(f"  BY HAND: {drug} is not a formulary agent, so no S/I/R verdict can")
        print("  be looked up. Expected UNDETERMINED.")
        return rec("hand verdict matches machine", r["round0_outcome"] == "UNDETERMINED")
    print(f"\n  panel rows for micro_specimen_id={spec} (pathogenic only):")
    print(f"    {'org_name':44s} {'ab_name':30s} interp")
    for _, x in sub.iterrows():
        mark = "  <== recommended" if DR.BS.canon_drug(x["ab_name"]) == drug else ""
        print(f"    {str(x['org_name'])[:44]:44s} {str(x['ab_name'])[:30]:30s} "
              f"{x['interpretation']}{mark}")
    isolates = sub["org_name"].dropna().unique().tolist()
    print(f"\n  BY HAND, config require_all_pathogens_covered=True:")
    verdicts = {}
    for org in isolates:
        rows = sub[(sub["org_name"] == org) & (sub["ab_name"].map(DR.BS.canon_drug) == drug)]
        v = rows["interpretation"].dropna().tolist()
        verdicts[org] = v[0] if v else None
        print(f"    {str(org)[:50]:52s} verdict for {drug} = {verdicts[org]}")
    if any(v is None for v in verdicts.values()):
        expect = "UNDETERMINED"; why = "at least one isolate never tested this agent"
    elif all(v == "S" for v in verdicts.values()):
        expect = "ADEQUATE"; why = "every pathogenic isolate S"
    elif any(v == "I" for v in verdicts.values()):
        expect = "INTERMEDIATE_ONLY"; why = "best verdict on some isolate is I"
    else:
        expect = "INADEQUATE"; why = "at least one isolate R"
    print(f"  -> hand expectation: {expect}  ({why})")
    return rec("hand verdict matches machine", expect == r["round0_outcome"],
               f"hand={expect} machine={r['round0_outcome']}")


def check_j_timing(p1, p2):
    hdr("(j) TIMING AND 40-CASE PROJECTION")
    secs = [r["full"]["seconds"] for r in p1 + p2]
    mean = sum(secs) / len(secs)
    print(f"  per-case seconds observed : {[round(s,1) for s in secs]}")
    print(f"  mean                      : {mean:.1f}s")
    print(f"  PROJECTION for 40 cases   : {40*mean/60:.1f} min ({40*mean:.0f}s)")
    pe = [t["prompt_eval_count"] for r in p1 for t in r["full"]["turns"] if t["prompt_eval_count"]]
    finals = [r["full"]["final_turn_prompt_eval_count"] for r in p1]
    print(f"\n  prompt_eval_count, final turn of each case: {finals}")
    print(f"  max prompt_eval_count seen: {max(pe) if pe else 'n/a'}  vs num_ctx={DR.OPTIONS['num_ctx']}")
    hi = max(pe) if pe else 0
    return rec(f"final-turn context comfortably below num_ctx ({DR.OPTIONS['num_ctx']})",
               hi < 0.5 * DR.OPTIONS["num_ctx"],
               f"max {hi} = {100*hi/DR.OPTIONS['num_ctx']:.0f}% of window")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    hdr("SETUP")
    frame, stats = DR.build_frame()
    print("  hadm_id recovery / D-COHORT-2 :", json.dumps(stats))
    panel = DR.load_panel()
    sel = DR.select(frame, n, sample=False)
    cases = DR.assemble_cases(sel, panel)
    print(f"  cases assembled: {[c['case_id'] for c in cases]}")
    DR.write_registry("model-level (instruct-2507 cannot think) + think:false + parser strip")

    check_module_isolation()
    check_c_mapping_audit(panel)
    check_g_intermediate()
    check_h_concur()
    check_a_fault_injection(cases[0])

    hdr("PIPE-CLEANER RUN")
    p1 = run_pass(cases, "first")
    cases2 = DR.assemble_cases(sel, panel)
    p2 = run_pass(cases2, "second")

    check_d_determinism(p1, p2)
    check_e_think([p1, p2])
    check_f_state_isolation(p1)
    check_b_join_integrity(p1, panel)
    check_i_hand_verify(p1, panel)
    check_j_timing(p1, p2)

    hdr("SCORED ROWS")
    print(f"  {'case_id':>18} {'order':>8} {'iso':>4} {'round-0 (zero-shot)':>34} "
          f"{'final A':>26} {'final B':>26} {'agree':>6}")
    print("  " + "-"*130)
    for r in p1:
        f = r["full"]
        print(f"  {f['case_id']:>18} {f['ordering']:>8} {f['n_isolates']:>4} "
              f"{f['round0_drug']+' / '+f['round0_outcome']:>34} "
              f"{f['final_A']+' / '+f['final_A_outcome']:>26} "
              f"{f['final_B']+' / '+f['final_B_outcome']:>26} {str(f['agreement']):>6}")

    hdr("ACCEPTANCE SUMMARY")
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, d in RESULTS:
        if not ok:
            print(f"  FAILED: {name}  {d}")
    print(f"\n  {npass}/{len(RESULTS)} checks passed")
    print("  " + ("ALL ACCEPTANCE CHECKS PASSED - ready for your go on stage D"
                  if npass == len(RESULTS) else "NOT READY - see failures above"))


if __name__ == "__main__":
    main()
