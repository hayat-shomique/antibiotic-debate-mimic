#!/usr/bin/env python
"""model_compare.py - round-0 only, across models. Is the fixed policy a property
of Qwen3-4B, or a property of small open-weight models on this task?

THE QUESTION
The debate arm found that the incumbent qwen3:4b-instruct-2507-q4_K_M returns
piperacillin-tazobactam at round 0 in 224 of 225 ordering-runs, and that its
round-0 verdict is identical to a fixed always-pip-tazo policy on 225 of 225
cases. The recommendation does not vary with the patient. That observation on
its own does not say whether the cause is the model or the task, and the two
readings lead to different papers.

MedGemma-4B is the discriminating comparison because it holds scale fixed and
varies only domain pretraining. If MedGemma conditions on the patient where Qwen
does not, domain pretraining buys patient conditioning at 4B and the finding is
about Qwen. If MedGemma also collapses onto one agent, the finding is about small
open-weight models on this task, and the honest headline names the class rather
than the model. Gemma4-12B is the scale control on the same family: it separates
"4B is too small" from "these models do this".

WHAT COUNTS AS PATIENT CONDITIONING
Not "the model said different things". The test is verdict identity against a
fixed single-drug policy. For each of the 17 formulary agents, a fixed policy that
recommends that agent on every case produces a verdict on every case under the
same scorer. A model that conditions on the patient cannot be verdict-identical
to any of the 17. A model that reaches 17/17 rows with one row at 100 per cent is
reproducible by a constant. That comparison, not the drug histogram, is what
analyse() is built around. The drug histogram is reported alongside because a
model can vary its drug and still be verdict-identical to a fixed policy when the
substitute scores the same way, and that case has to be visible rather than hidden
inside a single agreement number.

PROMPT IDENTITY, AND WHY THE QWEN COLUMN IS NOT RE-RUN
The prompt here is exactly what the debate arm sent at its turn 1 under the
A-first ordering: system is SCAFFOLD.texts["sys_A_round0"], user is
SCAFFOLD.texts["case_header"] + case_block.text with an empty transcript. That is
CaseRunner.round0 in debate_run.py, which calls _assemble("") for the user string
and selects sys_A_round0 when A opens. Nothing about debate, pressure or
confidence enters. Because the string is reconstructed by the same two scaffold
entries, the incumbent's column is harvested from runs/debate_20260818.jsonl
rather than re-run, and harvest() refuses to proceed unless the pinned hash of
sys_A_round0 still matches model_registry.json. The B-first round-0 records are
excluded: they were produced under sys_B_round0, a different system prompt.

The harvest is additionally gated on the C0 determinism check that control_pass.py
already performs. C0 re-sends this same reconstructed round-0 prompt and asserts
the parsed drug equals the debate arm's persisted round0_drug for the same case.
If runs/c0cn_*.jsonl exists and records any determinism_match false, harvest()
stops. Reuse then rests on a measurement rather than on an argument.

MEMORY, AND WHY MODELS ARE EVICTED BETWEEN COLUMNS
This is an Apple M2 with 16 GB unified memory shared between CPU and GPU. Ollama's
resident footprint runs near 1.27x the on-disk size at 8k context, so gemma4:12b
occupies roughly 9.6 GB resident against 7.6 GB on disk. One 12B model fits. A 12B
model alongside anything else does not, and two 4B models co-resident is already
the practical ceiling. Models are therefore loaded one at a time and each column
issues a keep_alive 0 request against the previous model before the next one is
pulled into memory. Left to itself Ollama would evict under pressure, but it does
so mid-request, which lands as a stall inside a timed call and contaminates the
throughput fields this file records.

Eviction is restricted to models this process loaded. LOADED_HERE tracks them. A
model already resident when the process started belongs to something else - most
likely the incumbent, held by the debate chain on a 30m keep_alive - and unloading
it would damage a run this file has no business touching.

SAFETY INTERLOCK
preflight() refuses to make a single call while debate_run.py, control_pass.py,
reveal_pass.py, ablation_pass.py or either chain script is alive. The GPU is
serial; a second consumer does not run in parallel, it interleaves and slows the
arms that matter. --force overrides, and prints what it is overriding.

--analyze-only and --harvest-only never open a socket to Ollama at all, so the
analysis is safe to run against partial data while the GPU is busy. analyse()
takes whatever rows exist, states the n for every model separately, and never
prints a patient-level row.

Post-freeze, separately labelled. This is not part of the frozen primary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

import debate_run as DR

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
DEBATE_LOG = RUNS / "debate_20260818.jsonl"      # explicit: a glob would pick up
                                                 # the _snapshot_ copies alongside it
GRID_CACHE = RUNS / "model_compare_policy_grid.parquet"

OLLAMA_CHAT = "http://localhost:11434/api/chat"
OLLAMA_GEN = "http://localhost:11434/api/generate"
OLLAMA_TAGS = "http://localhost:11434/api/tags"
OLLAMA_PS = "http://localhost:11434/api/ps"

INCUMBENT = "qwen3:4b-instruct-2507-q4_K_M"
# Two models only, matched on size (4B) and quantization (Q4_K_M). That matching is
# what makes the contrast mean anything: any difference is domain tuning, not scale.
# gemma4:12b was in this list and never ran; a 12B model varies size and family
# generation at the same time, so it could not have isolated either.
DEFAULT_MODELS = [INCUMBENT, "medgemma:4b-it-q4_K_M"]

# Held identical across every model. Written as literals rather than taken from
# debate_run so that a drift in either file is a visible assertion failure.
OPTIONS = {"temperature": 0, "seed": 20260818, "num_predict": 512, "num_ctx": 8192}
KEEP_ALIVE = "30m"
THINK = False
assert OPTIONS == DR.OPTIONS, f"options drift: {OPTIONS} vs {DR.OPTIONS}"
assert KEEP_ALIVE == DR.KEEP_ALIVE and THINK == DR.THINK
assert OPTIONS["seed"] == DR.SEED == 20260818

FORMULARY = DR.FORMULARY_KEYS                    # 17 agents
assert len(FORMULARY) == 17, f"formulary is {len(FORMULARY)} agents, expected 17"
OUTCOMES = ("ADEQUATE", "INADEQUATE", "INTERMEDIATE_ONLY", "UNDETERMINED")

BUSY_MARKERS = ["debate_run.py", "control_pass.py", "reveal_pass.py",
                "ablation_pass.py", "chain_passes.sh", "chain_ablation.sh",
                "c1_pressure.py"]

# Resident-footprint guard. 1.27x disk at 8k context, M2 with 16 GB unified.
FOOTPRINT_RATIO = 1.27
FOOTPRINT_CEILING_GB = 12.0

LOADED_HERE: set[str] = set()


# --------------------------------------------------------------------------
# ollama
# --------------------------------------------------------------------------
def _post(url: str, payload: dict, timeout: int) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _get(url: str, timeout: int = 20) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read())


def chat(model: str, system: str, user: str, timeout: int = 600) -> dict:
    """One call. Same body shape as debate_run.ollama_chat, model parameterised."""
    d = _post(OLLAMA_CHAT, {"model": model, "stream": False, "think": THINK,
                            "keep_alive": KEEP_ALIVE, "options": OPTIONS,
                            "messages": [{"role": "system", "content": system},
                                         {"role": "user", "content": user}]},
              timeout=timeout)
    t_ns = d.get("eval_duration") or 0
    return {"content": d.get("message", {}).get("content", ""),
            "thinking": d.get("message", {}).get("thinking"),
            "eval_count": d.get("eval_count"),
            "prompt_eval_count": d.get("prompt_eval_count"),
            "eval_duration_ns": t_ns,
            "eval_duration_s": t_ns / 1e9,
            "wall_s": None}


def timed_chat(model: str, system: str, user: str) -> dict:
    t0 = time.time()
    r = chat(model, system, user)
    r["wall_s"] = time.time() - t0
    return r


def registry() -> dict:
    """tag -> {digest, quantization, size_gb} from /api/tags."""
    out = {}
    for m in _get(OLLAMA_TAGS).get("models", []):
        det = m.get("details") or {}
        out[m["name"]] = {"digest": m.get("digest"),
                          "quantization": det.get("quantization_level"),
                          "parameter_size": det.get("parameter_size"),
                          "size_gb": round(m.get("size", 0) / 1e9, 2)}
    return out


def resident() -> dict:
    """tag -> resident GB from /api/ps."""
    try:
        return {m["name"]: round(m.get("size", 0) / 1e9, 2)
                for m in _get(OLLAMA_PS).get("models", [])}
    except (urllib.error.URLError, OSError):
        return {}


def unload(model: str, wait_s: int = 60) -> bool:
    """keep_alive 0 with no messages. Unloads without generating a token."""
    try:
        _post(OLLAMA_CHAT, {"model": model, "messages": [], "keep_alive": 0}, 60)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        try:
            _post(OLLAMA_GEN, {"model": model, "keep_alive": 0}, 60)
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            print(f"  unload {model}: request failed ({e}); continuing", flush=True)
            return False
    t0 = time.time()
    while time.time() - t0 < wait_s:
        if model not in resident():
            print(f"  unloaded {model} in {time.time()-t0:.0f}s", flush=True)
            return True
        time.sleep(2)
    print(f"  unload {model}: still resident after {wait_s}s", flush=True)
    return False


# --------------------------------------------------------------------------
# prompt
# --------------------------------------------------------------------------
def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def round0_prompt(case) -> tuple[str, str]:
    """Byte-identical to CaseRunner.round0 under the A-first ordering."""
    return (DR.SCAFFOLD.texts["sys_A_round0"],
            DR.SCAFFOLD.texts["case_header"] + case["block"].text)


def assert_scaffold_pinned() -> None:
    reg = json.loads((ROOT / "model_registry.json").read_text())
    for k in ("sys_A_round0", "case_header"):
        want = reg["scaffold_hashes"][k]
        got = DR.SCAFFOLD.pinned[k]
        if want != got:
            sys.exit(f"FATAL scaffold drift on {k}\n  registry {want}\n  live     {got}")


# --------------------------------------------------------------------------
# persistence, resume
# --------------------------------------------------------------------------
def out_path() -> Path:
    return RUNS / f"model_compare_{datetime.now().strftime('%Y%m%d')}.jsonl"


def persist(rec: dict) -> None:
    RUNS.mkdir(exist_ok=True)
    with out_path().open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def load_compare() -> list[dict]:
    rows = []
    for p in sorted(RUNS.glob("model_compare_*.jsonl")):
        if not p.name.startswith("model_compare_"):
            continue
        for line in p.read_text().splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def done_pairs(called_only: bool = False) -> set[tuple[str, str]]:
    """Pairs already on disk. With called_only, harvested rows do not count.

    The incumbent column was originally harvested from the debate log to save 200
    calls. That is fine for a single-model number and wrong for a cross-model
    comparison: one column reused, the other called, is not a controlled contrast.
    Under --no-reuse the harvested rows are ignored so the incumbent is re-called
    under the same conditions as every other model. The harvested rows stay on
    disk as an audit trail and are distinguishable by their source field.
    """
    return {(r["model"], r["case_id"]) for r in load_compare()
            if r.get("model") and r.get("case_id")
            and not (called_only and r.get("source") != "called")}


# --------------------------------------------------------------------------
# harvest of the incumbent column
# --------------------------------------------------------------------------
def determinism_ok() -> tuple[bool, str]:
    """C0 re-sent this exact prompt. Read its verdict on reproducibility."""
    files = [p for p in sorted(RUNS.glob("c0cn_*.jsonl"))
             if p.name.startswith("c0cn_")]
    if not files:
        return True, "no c0cn_*.jsonl on disk; reuse unconfirmed by C0"
    n = bad = 0
    for p in files:
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("debate_round0_drug") is None:
                continue
            n += 1
            if r.get("determinism_match") is False:
                bad += 1
    if n == 0:
        return True, "c0cn present but no overlapping cases; reuse unconfirmed"
    if bad:
        return False, f"C0 determinism mismatches {bad}/{n}"
    return True, f"C0 determinism {n}/{n} match"


def harvest(cases: list, reg: dict | None, allow_unconfirmed: bool) -> int:
    """Write the incumbent's round-0 column from the debate log instead of calling."""
    assert_scaffold_pinned()
    ok, note = determinism_ok()
    print(f"  reuse gate: {note}", flush=True)
    if not ok and not allow_unconfirmed:
        sys.exit("REFUSING to reuse the debate column: C0 reports a determinism "
                 "mismatch. Re-run the incumbent with --no-reuse, or pass "
                 "--reuse-anyway if the mismatch has been explained.")
    if not DEBATE_LOG.exists():
        print(f"  {DEBATE_LOG} absent; nothing to harvest", flush=True)
        return 0

    by_case = {}
    for line in DEBATE_LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("kind") == "round0" and r.get("ordering") == "A-first":
            by_case.setdefault(r["case_id"], r)      # first wins; restarts append

    digest = (reg or {}).get(INCUMBENT, {}).get("digest") or DR.MODEL_DIGEST
    quant = (reg or {}).get(INCUMBENT, {}).get("quantization") or DR.MODEL_QUANT
    have = done_pairs()
    n = 0
    for c in cases:
        cid = c["case_id"]
        if (INCUMBENT, cid) in have or cid not in by_case:
            continue
        r = by_case[cid]
        t = r["turn"]
        system, user = round0_prompt(c)
        persist({
            "kind": "model_compare", "source": "debate_log_A_first_round0",
            "model": INCUMBENT, "digest": digest, "quantization": quant,
            "case_id": cid,
            "micro_specimen_id": int(c["row"]["micro_specimen_id"]),
            "subject_id": int(c["row"]["subject_id"]),
            "n_isolates": int(len(c["panel"])),
            "drug": r["drug"], "outcome": r["outcome"], "reason": r.get("reason"),
            "position_source": t.get("position_source"),
            "n_calls": 1,
            "eval_count": t.get("eval_count"),
            "eval_duration_ns": None,          # not persisted by the debate arm
            "eval_duration_s": None,
            "prompt_eval_count": t.get("prompt_eval_count"),
            "wall_s": t.get("wall_s"),
            "has_think_tag": bool(t.get("has_think_tag")),
            "text": t.get("text"),
            "sys_sha256": sha(system), "user_sha256": sha(user),
            "options": OPTIONS, "keep_alive": KEEP_ALIVE, "think": THINK,
            "seed": OPTIONS["seed"],
            "harvest_note": note,
            "ts": datetime.now().astimezone().isoformat()})
        n += 1
    print(f"  harvested {n} incumbent rows from {DEBATE_LOG.name} "
          f"({len(by_case)} A-first round-0 case ids available)", flush=True)
    return n


# --------------------------------------------------------------------------
# preflight
# --------------------------------------------------------------------------
def busy_pids() -> list[str]:
    hits = []
    for marker in BUSY_MARKERS:
        try:
            out = subprocess.run(["pgrep", "-f", marker], capture_output=True,
                                 text=True, timeout=15).stdout.split()
        except (OSError, subprocess.SubprocessError):
            continue
        for pid in out:
            if pid.strip() and pid.strip() != str(os.getpid()):
                hits.append(f"{marker}:{pid.strip()}")
    return hits


def preflight(models: list[str], force: bool) -> dict:
    busy = busy_pids()
    if busy:
        print("  GPU consumers alive: " + ", ".join(busy), flush=True)
        if not force:
            sys.exit("REFUSING to start. The GPU is serial and these runs come "
                     "first. Wait for them, or pass --force.")
        print("  --force given; proceeding anyway", flush=True)

    reg = registry()
    missing = [m for m in models if m not in reg]
    if missing:
        sys.exit(f"FATAL model tag(s) not present in ollama: {missing}\n"
                 f"  available: {sorted(reg)}")
    if INCUMBENT in models and reg[INCUMBENT]["digest"] != DR.MODEL_DIGEST:
        sys.exit(f"FATAL incumbent digest drift\n  expected {DR.MODEL_DIGEST}\n"
                 f"  live     {reg[INCUMBENT]['digest']}")

    res = resident()
    foreign = {k: v for k, v in res.items() if k not in LOADED_HERE}
    biggest = max((reg[m]["size_gb"] for m in models), default=0.0) * FOOTPRINT_RATIO
    projected = biggest + sum(foreign.values())
    print(f"  resident now: {foreign if foreign else 'nothing'}", flush=True)
    print(f"  largest requested model resident estimate {biggest:.1f} GB, "
          f"projected peak {projected:.1f} GB of 16 GB", flush=True)
    if projected > FOOTPRINT_CEILING_GB and not force:
        sys.exit(f"REFUSING to start: projected peak {projected:.1f} GB exceeds the "
                 f"{FOOTPRINT_CEILING_GB} GB ceiling with models this process does "
                 "not own already resident. Wait for them to expire, or --force.")
    for m in models:
        print(f"  {m:34s} {reg[m]['digest'][:16]}  {reg[m]['quantization']}  "
              f"{reg[m]['size_gb']} GB disk", flush=True)
    return reg


# --------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------
def run_model(model: str, cases: list, reg: dict, deadline: float | None,
              called_only: bool = False) -> int:
    have = done_pairs(called_only)
    todo = [c for c in cases if (model, c["case_id"]) not in have]
    print(f"\n  {model}: {len(cases)} cases, {len(cases)-len(todo)} already on disk, "
          f"{len(todo)} to call", flush=True)
    if not todo:
        return 0
    if model not in resident():
        LOADED_HERE.add(model)

    t0 = time.time()
    for i, c in enumerate(todo, 1):
        if deadline and time.time() > deadline:
            print(f"  deadline reached after {i-1} calls for {model}", flush=True)
            break
        system, user = round0_prompt(c)
        r = timed_chat(model, system, user)
        text, calls, source = r["content"], 1, "explicit"
        drug = DR.parse_drug(text)
        if drug == DR.INVALID:
            # Mirrors the debate arm's single retry so the incumbent column
            # harvested from the log and any freshly called column were produced
            # under the same recovery rule. Call one is still byte-identical.
            r2 = timed_chat(model, system, user + "\n\n" + DR.SCAFFOLD.texts["retry"])
            text = text + "\n---RETRY---\n" + r2["content"]
            drug = DR.parse_drug(r2["content"])
            calls, source = 2, "retry"
            for k in ("eval_count", "prompt_eval_count", "eval_duration_ns", "wall_s"):
                r[k] = (r[k] or 0) + (r2[k] or 0)
            r["eval_duration_s"] = r["eval_duration_ns"] / 1e9
        s = DR.score(drug, c["panel"])
        persist({
            "kind": "model_compare", "source": "called",
            "model": model, "digest": reg[model]["digest"],
            "quantization": reg[model]["quantization"],
            "case_id": c["case_id"],
            "micro_specimen_id": int(c["row"]["micro_specimen_id"]),
            "subject_id": int(c["row"]["subject_id"]),
            "n_isolates": int(len(c["panel"])),
            "drug": drug, "outcome": s["outcome"], "reason": s.get("reason"),
            "position_source": source, "n_calls": calls,
            "eval_count": r["eval_count"],
            "eval_duration_ns": r["eval_duration_ns"],
            "eval_duration_s": round(r["eval_duration_s"], 3),
            "prompt_eval_count": r["prompt_eval_count"],
            "wall_s": round(r["wall_s"], 2),
            "has_think_tag": ("<think>" in text or "</think>" in text),
            "text": text,
            "sys_sha256": sha(system), "user_sha256": sha(user),
            "options": OPTIONS, "keep_alive": KEEP_ALIVE, "think": THINK,
            "seed": OPTIONS["seed"],
            "ts": datetime.now().astimezone().isoformat()})
        el = time.time() - t0
        print(f"  [{i}/{len(todo)}] {model} {drug:32s} {s['outcome']:18s} "
              f"{el/i:.1f}s/call  ETA {(len(todo)-i)*el/i/60:.0f} min", flush=True)
    return len(todo)


# --------------------------------------------------------------------------
# fixed-policy grid
# --------------------------------------------------------------------------
def policy_grid(cases: list, refresh: bool = False) -> pd.DataFrame:
    """case_id x 17 agents -> outcome a fixed always-that-agent policy would score.

    CPU only. The scorer is DR.score, the same function that scored every arm.
    """
    if GRID_CACHE.exists() and not refresh:
        g = pd.read_parquet(GRID_CACHE)
        if set(g["case_id"]) >= {c["case_id"] for c in cases}:
            return g
    rows = []
    for c in cases:
        for d in FORMULARY:
            rows.append({"case_id": c["case_id"], "policy_drug": d,
                         "outcome": DR.score(d, c["panel"])["outcome"]})
    g = pd.DataFrame(rows)
    RUNS.mkdir(exist_ok=True)
    g.to_parquet(GRID_CACHE, index=False)
    return g


def grid_lookup(g: pd.DataFrame) -> dict:
    out = defaultdict(dict)
    for cid, d, o in zip(g["case_id"], g["policy_drug"], g["outcome"]):
        out[cid][d] = o
    return out


# --------------------------------------------------------------------------
# analysis
# --------------------------------------------------------------------------
def wilson(k: int, n: int) -> tuple[float, float]:
    return DR.BS.wilson_ci(k, n) if n else (float("nan"), float("nan"))


def pct(k: int, n: int) -> str:
    return f"{k}/{n} = {100*k/n:.1f}%" if n else f"{k}/0 = n/a"


def analyse(cases: list | None = None, models: list[str] | None = None,
            refresh_grid: bool = False) -> dict:
    """Runs on partial data. Every figure states its own n."""
    rows = load_compare()
    if not rows:
        print("  no rows in runs/model_compare_*.jsonl yet")
        return {}
    by_model = defaultdict(dict)
    for r in rows:
        by_model[r["model"]][r["case_id"]] = r     # last write wins
    order = [m for m in (models or DEFAULT_MODELS) if m in by_model]
    order += [m for m in by_model if m not in order]

    lut = {}
    if cases is not None:
        lut = grid_lookup(policy_grid(cases, refresh=refresh_grid))

    W = 78
    def hdr(t):
        print("\n" + "=" * W + f"\n{t}\n" + "=" * W)

    hdr("ROUND-0 MODEL COMPARISON, PARTIAL-DATA SAFE")
    print(f"  log            {out_path().name} and siblings")
    print(f"  prompt         sys_A_round0 + case_header + case block, no debate frame")
    print(f"  options        {OPTIONS}, keep_alive {KEEP_ALIVE}, think {THINK}")
    print(f"  policy grid    {'loaded' if lut else 'NOT AVAILABLE (pass cases)'}")
    for m in order:
        src = Counter(r.get("source") for r in by_model[m].values())
        print(f"  {m:34s} n={len(by_model[m]):4d}  sources {dict(src)}")

    summary = {}
    for m in order:
        recs = by_model[m]
        n = len(recs)
        drugs = Counter(r["drug"] for r in recs.values())
        outs = Counter(r["outcome"] for r in recs.values())

        hdr(f"{m}   n = {n}")
        print(f"  distinct positions recommended   {len(drugs)}")
        for d, k in drugs.most_common():
            print(f"    {d:34s} {pct(k, n)}")

        print()
        for k in OUTCOMES:
            lo, hi = wilson(outs[k], n)
            print(f"  {k:18s} {pct(outs[k], n):>18}   95% CI [{100*lo:.1f}, {100*hi:.1f}]")
        n_eval = outs["ADEQUATE"] + outs["INADEQUATE"]
        lo, hi = wilson(outs["ADEQUATE"], n_eval)
        print(f"  adequacy on evaluable cases      {pct(outs['ADEQUATE'], n_eval)}"
              f"   95% CI [{100*lo:.1f}, {100*hi:.1f}]"
              f"   (denominator excludes INTERMEDIATE_ONLY and UNDETERMINED)")

        modal_d, modal_k = drugs.most_common(1)[0]
        lo, hi = wilson(modal_k, n)
        print(f"  modal position share             {modal_d} {pct(modal_k, n)}"
              f"   95% CI [{100*lo:.1f}, {100*hi:.1f}]")

        ent = {"model": m, "n": n, "n_distinct_drugs": len(drugs),
               "drugs": dict(drugs), "outcomes": dict(outs),
               "modal_drug": modal_d, "modal_share": [modal_k, n, wilson(modal_k, n)],
               "adequacy_all": [outs["ADEQUATE"], n, wilson(outs["ADEQUATE"], n)],
               "adequacy_evaluable": [outs["ADEQUATE"], n_eval, wilson(outs["ADEQUATE"], n_eval)]}

        if not lut:
            summary[m] = ent
            continue

        usable = [cid for cid in recs if cid in lut]
        nu = len(usable)
        print(f"\n  FIXED SINGLE-DRUG POLICY TEST, n = {nu} cases with a policy grid")
        print("  a model that conditions on the patient is verdict-identical to none of the 17")
        print(f"  {'policy':34s} {'drug match':>14s} {'verdict match':>16s}")
        pol = {}
        for d in FORMULARY:
            dm = sum(1 for cid in usable if recs[cid]["drug"] == d)
            vm = sum(1 for cid in usable if recs[cid]["outcome"] == lut[cid][d])
            pol[d] = {"drug_match": dm, "verdict_match": vm, "n": nu}
            print(f"    {d:32s} {pct(dm, nu):>14s} {pct(vm, nu):>16s}")
        # ties on verdict_match are broken by drug_match so the policy named is the
        # one the model is actually imitating, not the first alphabetically
        best = max(pol, key=lambda d: (pol[d]["verdict_match"], pol[d]["drug_match"])) if nu else None
        exact = [d for d in FORMULARY if nu and pol[d]["verdict_match"] == nu]

        # How much separating power does the scorer have on these cases at all?
        # If the 17 policies collapse into a handful of distinct verdict vectors,
        # verdict identity is weak evidence and must not be read as absent
        # conditioning on its own.
        vecs = {tuple(lut[cid][d] for cid in usable) for d in FORMULARY} if nu else set()
        print()
        if nu:
            b = pol[best]
            lo, hi = wilson(b["verdict_match"], nu)
            print(f"  best fixed policy                {best}  "
                  f"{pct(b['verdict_match'], nu)}  95% CI [{100*lo:.1f}, {100*hi:.1f}]")
        print(f"  policies reaching verdict identity  {exact if exact else 'none'}")
        print(f"  distinct verdict vectors among the 17 policies   {len(vecs)}/17"
              f"   (separating power of the scorer on these {nu} cases)")

        # The headline finding rests on two things jointly: one position on every
        # case, AND verdict identity. Verdict identity alone is necessary, not
        # sufficient - several broad-spectrum agents score alike on a susceptible
        # panel, so a model that varies its drug can still match a fixed policy's
        # outcome vector. The branches below keep those apart.
        if nu and exact and len(drugs) == 1:
            reading = ("one position on every case AND verdict-identical to a fixed "
                       "policy. Reproducible by a constant; no patient conditioning "
                       f"at n={nu}.")
        elif nu and exact:
            reading = (f"verdict-identical to {len(exact)} fixed policies, but the model "
                       f"names {len(drugs)} distinct agents across {nu} cases. The scorer "
                       "cannot separate those agents on this panel, so verdict identity "
                       "here is NOT evidence against conditioning. Read the drug "
                       "distribution and the modal share instead.")
        elif nu:
            reading = ("no fixed single-drug policy reproduces every verdict. The "
                       "round-0 output varies with the case.")
        else:
            reading = "no cases with a policy grid; nothing to read."
        print(f"  READING: {reading}")
        ent["policy"] = pol
        ent["best_policy"] = best
        ent["verdict_identical_policies"] = exact
        ent["n_distinct_policy_verdict_vectors"] = len(vecs)
        ent["reading"] = reading
        summary[m] = ent

    if len(order) > 1:
        hdr("PAIRWISE CASE-WISE AGREEMENT, ON CASES BOTH MODELS HAVE")
        print(f"  {'pair':56s} {'n':>4s} {'drug':>14s} {'verdict':>14s}")
        pairs = {}
        for i, a in enumerate(order):
            for b in order[i + 1:]:
                common = sorted(set(by_model[a]) & set(by_model[b]))
                n = len(common)
                dm = sum(1 for c in common if by_model[a][c]["drug"] == by_model[b][c]["drug"])
                vm = sum(1 for c in common if by_model[a][c]["outcome"] == by_model[b][c]["outcome"])
                lo, hi = wilson(dm, n)
                print(f"  {a + ' vs ' + b:56s} {n:>4d} {pct(dm, n):>14s} {pct(vm, n):>14s}")
                if n:
                    print(f"    drug agreement 95% CI [{100*lo:.1f}, {100*hi:.1f}]")
                pairs[f"{a}|{b}"] = {"n": n, "drug_match": dm, "verdict_match": vm,
                                     "drug_ci": wilson(dm, n)}
        summary["_pairwise"] = pairs

    hdr("THROUGHPUT AND FORMAT HYGIENE")
    print(f"  {'model':34s} {'n':>4s} {'tok/call':>9s} {'tok/s':>8s} "
          f"{'s/call':>8s} {'retries':>8s} {'think':>6s}")
    for m in order:
        recs = list(by_model[m].values())
        ec = [r["eval_count"] for r in recs if r.get("eval_count")]
        ws = [r["wall_s"] for r in recs if r.get("wall_s")]
        ed = [r["eval_duration_s"] for r in recs if r.get("eval_duration_s")]
        rt = sum(1 for r in recs if r.get("position_source") == "retry")
        th = sum(1 for r in recs if r.get("has_think_tag"))
        tps = (sum(ec) / sum(ed)) if ed and sum(ed) else float("nan")
        print(f"  {m:34s} {len(recs):>4d} "
              f"{(sum(ec)/len(ec) if ec else float('nan')):>9.1f} "
              f"{tps:>8.1f} {(sum(ws)/len(ws) if ws else float('nan')):>8.2f} "
              f"{rt:>8d} {th:>6d}")
    print("  tok/s is generation only, from eval_duration; blank for harvested rows, "
          "which the debate arm did not persist.")

    hdr("WHAT THIS ANSWERS")
    print("  The criterion is joint: a model shows no patient conditioning when it names")
    print("  one agent on every case AND no verdict distinguishes it from that fixed")
    print("  policy. Either half alone is not enough.")
    print("  MedGemma-4B holds scale fixed and varies domain pretraining. If it spreads")
    print("  across agents where the incumbent does not, domain pretraining buys patient")
    print("  conditioning at 4B and the finding is about Qwen. If it collapses onto one")
    print("  agent too, the finding is about small open-weight models on this task and")
    print("  the headline must name the class. Gemma4-12B separates scale from domain")
    print("  within the same family.")
    return summary


# --------------------------------------------------------------------------
def build_cases(n: int, pilot: int | None) -> list:
    frame, _ = DR.build_frame()
    panel = DR.load_panel()
    sel = DR.select(frame, n, sample=True, panel=panel)
    cases = DR.assemble_cases(sel, panel)
    if pilot:
        # strict subset of the same 200, deterministic by case id
        cases = sorted(cases, key=lambda c: c["case_id"])[:pilot]
    return cases


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("-n", type=int, default=200, help="sampling frame draw size")
    ap.add_argument("--pilot", type=int, default=None,
                    help="run only the first K of the 200 by case id")
    ap.add_argument("--no-reuse", action="store_true",
                    help="call the incumbent instead of harvesting its debate column")
    ap.add_argument("--reuse-anyway", action="store_true",
                    help="harvest even though C0 reports a determinism mismatch")
    ap.add_argument("--harvest-only", action="store_true")
    ap.add_argument("--analyze-only", action="store_true")
    ap.add_argument("--refresh-grid", action="store_true")
    ap.add_argument("--no-evict", action="store_true",
                    help="skip the keep_alive 0 eviction between columns")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--deadline", type=str, default=None, help="HH:MM local")
    a = ap.parse_args()

    if a.analyze_only:
        cases = None
        try:
            cases = build_cases(a.n, a.pilot)
        except Exception as e:                       # grid is optional
            print(f"  policy grid unavailable ({e}); reporting without it")
        analyse(cases, a.models, refresh_grid=a.refresh_grid)
        return

    deadline = None
    if a.deadline:
        hh, mm = (int(x) for x in a.deadline.split(":"))
        now = datetime.now()
        d = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if d < now:
            d = d.replace(day=d.day + 1)
        deadline = d.timestamp()
        print(f"  deadline {d:%Y-%m-%d %H:%M}", flush=True)

    cases = build_cases(a.n, a.pilot)
    print(f"  cases assembled: {len(cases)}", flush=True)

    if a.harvest_only:
        assert_scaffold_pinned()
        harvest(cases, None, a.reuse_anyway)
        analyse(cases, a.models, refresh_grid=a.refresh_grid)
        return

    reg = preflight(a.models, a.force)
    models = list(a.models)
    if INCUMBENT in models and not a.no_reuse:
        harvest(cases, reg, a.reuse_anyway)

    prev = None
    for m in models:
        if prev and prev in LOADED_HERE and not a.no_evict:
            unload(prev)
            LOADED_HERE.discard(prev)
        elif prev and prev in resident():
            print(f"  leaving {prev} resident: this process did not load it", flush=True)
        run_model(m, cases, reg, deadline, called_only=a.no_reuse)
        prev = m
    if prev and prev in LOADED_HERE and not a.no_evict:
        unload(prev)
        LOADED_HERE.discard(prev)

    analyse(cases, a.models, refresh_grid=a.refresh_grid)


if __name__ == "__main__":
    main()
