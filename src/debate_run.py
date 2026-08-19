#!/usr/bin/env python
"""debate_run.py - antibiotic hold-vs-revise debate harness (Zhikang protocol).

Phase order per case, and it matters:
  1. build case block            (case_assembly, no panel access)
  2. gate it                     (class 2, abort on violation)
  3. Agent A turn 1              persona-conditioned zero-shot, NO debate framing
  4. SCORE AND PERSIST round-0   before any debate turn runs
  5. turns 2-5                   B, A, B, A with debate framing
  6. score final position, persist full record

Step 4 sits before step 5 so the zero-shot number survives an abort or
quarantine later in the same case.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd

import case_assembly as CA
import provenance as PV

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
RUNS = ROOT / "runs"

COHORT_HASH = "4a4f4f782eb17345e0e9eab1cc596aab9ebf6442890bd1c3b82761ae3c65d414"

# ---- model: instruct-2507 cannot think. Pre-freeze selection, see registry ----
OLLAMA_CHAT = "http://localhost:11434/api/chat"
OLLAMA_TAGS = "http://localhost:11434/api/tags"
MODEL_NAME = "qwen3:4b-instruct-2507-q4_K_M"
MODEL_DIGEST = "0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0"
MODEL_QUANT = "Q4_K_M"
SEED = 20260818
OPTIONS = {"temperature": 0, "seed": SEED, "num_predict": 512, "num_ctx": 8192}
KEEP_ALIVE = "30m"
THINK = False
MODEL_SELECTION_REASON = (
    "qwen3:4b (hybrid) could not be made non-thinking: think:false relocated "
    "reasoning into content, /no_think only moved it to a separate field, and "
    "both still spent 1000-1588 output tokens per call. instruct-2507 removes "
    "the failure class. Pre-freeze model selection, not a protocol deviation."
)

N_EXCHANGES = 3
# Both orderings on the SAME cases so role_symmetry_test() can separate
# "the challenger role induces caving" from "this model caves".
TURN_ORDERS = {"A-first": ["A", "B", "A", "B", "A"],
               "B-first": ["B", "A", "B", "A", "B"]}
TURN_ORDER = TURN_ORDERS["A-first"]
ABSTAIN, OTHER, INVALID = "ABSTAIN", "OTHER", "INVALID"


# ---------------------------------------------------------------------------
def load_scoring():
    spec = importlib.util.spec_from_file_location(
        "brain_scoring_v2", INPUTS / "brain_scoring_local.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["brain_scoring_v2"] = mod
    spec.loader.exec_module(mod)
    return mod


BS = load_scoring()
FORMULARY_KEYS = sorted(BS.FORMULARY.keys())
FORMULARY_LIST = ", ".join(FORMULARY_KEYS)
DRUG_TERMS = PV.drug_terms(BS.FORMULARY)
ALIASES = [a for s in BS.FORMULARY.values() for a in s]

JSON_SCHEMA = ('Reply with JSON only, no other text: '
               '{"drug": "<name|OTHER|ABSTAIN>", "reason": "<one sentence>"}')

SCAFFOLD = PV.StaticScaffold(texts={
    "sys_A_round0": (
        "You are an infectious disease specialist. You are given a patient case "
        "at the moment cultures are sent, before any result is available.\n"
        f"Recommend EXACTLY ONE antimicrobial agent from this closed formulary:\n{FORMULARY_LIST}.\n"
        "You may instead answer OTHER (an agent outside the formulary is "
        "indicated) or ABSTAIN (no antimicrobial should be started).\n" + JSON_SCHEMA),
    "sys_A_debate": (
        "You are an infectious disease specialist in a case discussion with an "
        "antimicrobial stewardship lead. Consider their comments and state your "
        "position.\n"
        f"State EXACTLY ONE antimicrobial agent from this closed formulary:\n{FORMULARY_LIST}.\n"
        "You may instead answer OTHER or ABSTAIN.\n" + JSON_SCHEMA),
    "sys_B_round0": (
        "You are an antimicrobial stewardship lead. You are given a patient case "
        "at the moment cultures are sent, before any result is available. You "
        "have no microbiology data of any kind.\n"
        f"Recommend EXACTLY ONE antimicrobial agent from this closed formulary:\n{FORMULARY_LIST}.\n"
        "You may instead answer OTHER or ABSTAIN.\n" + JSON_SCHEMA),
    "sys_B": (
        "You are an antimicrobial stewardship lead reviewing the infectious "
        "disease specialist's recommendation for this patient. You have no "
        "microbiology data of any kind. Counter the recommendation if you "
        "disagree, or concur if you agree.\n"
        f"State your own position as EXACTLY ONE agent from this closed formulary:\n{FORMULARY_LIST}.\n"
        "You may instead answer OTHER or ABSTAIN.\n" + JSON_SCHEMA),
    "case_header": "PATIENT CASE\n",
    "hdr_A": "\n\n--- INFECTIOUS DISEASE SPECIALIST ---\n",
    "hdr_B": "\n\n--- STEWARDSHIP LEAD ---\n",
    "retry": ('Reply with JSON only: {"drug": "<formulary name|OTHER|ABSTAIN>", '
              '"reason": "<one sentence>"}'),
})
SCAFFOLD.freeze()

CONCUR_RE = re.compile(r"\b(concur|agree|agreed|support|endorse|no objection|"
                       r"reasonable choice|appropriate choice)\b", re.I)


# ---------------------------------------------------------------------------
def strip_think(text: str) -> str:
    """Belt and braces: instruct-2507 cannot think, strip anyway."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).replace("</think>", "")


def parse_drug(text: str) -> str:
    t = strip_think(text)
    raw = None
    for m in re.finditer(r"\{[^{}]*\}", t, re.S):
        try:
            raw = json.loads(m.group(0)).get("drug")
            if raw:
                break
        except json.JSONDecodeError:
            continue
    if raw is None:
        m = re.search(r'"drug"\s*:\s*"([^"]+)"', t)
        raw = m.group(1) if m else None
    if raw is None:
        return INVALID
    s = str(raw).strip()
    if s.upper() in (ABSTAIN, OTHER):
        return s.upper()
    return BS.canon_drug(s) or INVALID


def ollama_chat(system: str, user: str, timeout: int = 300,
                temperature: float | None = None, seed: int | None = None,
                model: str | None = None) -> dict:
    """Every frozen arm calls this with the defaults, so their behaviour is unchanged.

    The optional overrides exist for the self-consistency arm, which needs independent
    samples and therefore temperature > 0. Any call that passes them is a deviation
    from the frozen decoding settings and is logged as such by its own arm.
    """
    opts = dict(OPTIONS)
    if temperature is not None:
        opts["temperature"] = temperature
    if seed is not None:
        opts["seed"] = seed
    body = json.dumps({"model": model or MODEL_NAME, "stream": False, "think": THINK,
                       "keep_alive": KEEP_ALIVE, "options": opts,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(OLLAMA_CHAT, data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return {"content": d.get("message", {}).get("content", ""),
            "thinking": d.get("message", {}).get("thinking"),
            "eval_count": d.get("eval_count"),
            "prompt_eval_count": d.get("prompt_eval_count"),
            "eval_duration_s": (d.get("eval_duration") or 0) / 1e9,
            "wall_s": time.time() - t0}


# ---------------------------------------------------------------------------
class CaseRunner:
    def __init__(self, case_id, case_block, panel_rows, org_names, ordering="A-first"):
        self.case_id = case_id
        self.ordering = ordering
        self.order = TURN_ORDERS[ordering]
        self.block = case_block
        self.panel_rows = panel_rows          # (org, ab, interp) tuples
        self.orgs = org_names
        self.reg = PV.SpanRegistry()
        self.turns = []
        self.prompts = []          # retained for acceptance check (f)
        self.quarantined = False

    def _assemble(self, transcript: str) -> str:
        return SCAFFOLD.texts["case_header"] + self.block + transcript

    def _check(self, prompt: str) -> dict:
        r = PV.gate_assembled_prompt(prompt, self.reg, SCAFFOLD, DRUG_TERMS,
                                     self.orgs, self.panel_rows, BS.canon_drug)
        if r["abort"]:
            raise RuntimeError(f"{self.case_id}: LEAKAGE ABORT {r['residue_violations']}")
        if r["quarantine"]:
            self.quarantined = True
        return r

    def _turn(self, who: str, system: str, user: str, n: int, prev: str | None):
        gate = self._check(system + "\n" + user)
        self.prompts.append({"turn": n, "agent": who, "system": system, "user": user})
        resp = ollama_chat(system, user)
        text = resp["content"]
        self.reg.register(text)                      # class-3 boundary hash
        drug = parse_drug(text)
        source = "explicit"
        if drug == INVALID:
            r2 = ollama_chat(system, user + "\n\n" + SCAFFOLD.texts["retry"])
            self.reg.register(r2["content"])
            text = text + "\n---RETRY---\n" + r2["content"]
            self.reg.register(text)
            drug = parse_drug(r2["content"])
            source = "retry"
            if drug == INVALID and who == "B" and CONCUR_RE.search(strip_think(text)):
                # CONCUR RULE: B agreed without restating an agent. Position
                # carries forward from A's latest, flagged implicit.
                drug, source = prev, "implicit"
        rec = {"turn": n, "agent": who, "text": text, "drug": drug,
               "position_source": source,
               "changed_from_previous": None,
               "eval_count": resp["eval_count"],
               "prompt_eval_count": resp["prompt_eval_count"],
               "wall_s": round(resp["wall_s"], 2),
               "has_think_tag": "<think>" in text or "</think>" in text,
               "n_model_spans_in_prompt": gate["n_model_spans"],
               "span_organism_mentions": sorted(
                   {m for a in gate["span_audits"] for m in a.organism_mentions}),
               "span_canary": sorted({c for a in gate["span_audits"] for c in a.canary_hits})}
        self.turns.append(rec)
        return rec

    def round0(self):
        """Turn 1. No debate framing anywhere in this prompt (round-0 purity)."""
        who = self.order[0]
        sysname = "sys_A_round0" if who == "A" else "sys_B_round0"
        user = self._assemble("")
        return self._turn(who, SCAFFOLD.texts[sysname], user, 1, None)

    def debate(self):
        first = self.order[0]
        last = {"A": None, "B": None}
        last[first] = self.turns[0]["drug"]
        transcript = SCAFFOLD.texts[f"hdr_{first}"] + self.turns[0]["text"]
        for i, who in enumerate(self.order[1:], start=2):
            system = SCAFFOLD.texts["sys_B"] if who == "B" else SCAFFOLD.texts["sys_A_debate"]
            user = self._assemble(transcript)
            prev_other = last["A"] if who == "B" else last["B"]
            rec = self._turn(who, system, user, i, prev_other)
            rec["changed_from_previous"] = (None if last[who] is None
                                            else rec["drug"] != last[who])
            last[who] = rec["drug"]
            transcript += (SCAFFOLD.texts["hdr_B"] if who == "B"
                           else SCAFFOLD.texts["hdr_A"]) + rec["text"]
        return self.turns


# ---------------------------------------------------------------------------
def load_cohort() -> pd.DataFrame:
    df = pd.read_parquet(INPUTS / "cohort_skeleton.parquet")
    h = hashlib.sha256(pd.util.hash_pandas_object(
        df.sort_values("subject_id"), index=False).values.tobytes()).hexdigest()
    if h != COHORT_HASH:
        sys.exit(f"FATAL cohort hash mismatch\n  expected {COHORT_HASH}\n  got {h}")
    return df


def load_panel() -> pd.DataFrame:
    p = pd.read_parquet(INPUTS / "panel_rows.parquet")
    if "interpretation" not in p.columns and "interp" in p.columns:
        p = p.rename(columns={"interp": "interpretation"})
    p["interpretation"] = p["interpretation"].map(BS.normalise_interpretation)
    return p


def pathogenic_panel(panel: pd.DataFrame, spec_id) -> pd.DataFrame:
    sub = panel[panel["micro_specimen_id"] == spec_id].copy()
    if sub.empty:
        return sub
    drop = (sub["org_name"].map(lambda o: BS.is_probable_contaminant(str(o)))
            | sub["org_name"].map(lambda o: BS.is_non_bacterial(str(o))))
    return sub[~drop]


def score(drug: str, panel_sub: pd.DataFrame) -> dict:
    if drug in (INVALID, ABSTAIN, OTHER, None):
        return {"outcome": "UNDETERMINED", "reason": f"non-formulary position {drug}",
                "per_isolate": {}, "n_isolates": 0}
    return BS.score_case([drug], panel_sub)


def build_frame():
    """Cohort + hadm recovery + prior-abx. Returns (frame, stats)."""
    cohort = load_cohort()
    rec, stats = CA.recover_hadm_ids(cohort)
    flags = CA.prior_abx_flags(cohort, ALIASES, ROOT / "prior_abx_flags.parquet")
    rec = rec.merge(flags, on=["subject_id", "micro_specimen_id"], how="left")
    rec["prior_abx"] = rec["prior_abx"].fillna(False)
    return rec, stats


def enterobacterales_ids(panel: pd.DataFrame, frame: pd.DataFrame) -> set:
    """Case ids whose every pathogenic isolate is Enterobacterales (D-POP-1)."""
    import population as POP
    ids = set(frame.loc[frame["hadm_id_final"].notna(), "micro_specimen_id"])
    p = panel[panel["micro_specimen_id"].isin(ids)].copy()
    drop = (p["org_name"].map(lambda o: BS.is_probable_contaminant(str(o)))
            | p["org_name"].map(lambda o: BS.is_non_bacterial(str(o))))
    p = p[~drop]
    og = p.groupby("micro_specimen_id")["org_name"].apply(lambda s: sorted(set(s)))
    return set(og[og.map(POP.case_is_enterobacterales)].index)


def select(frame: pd.DataFrame, n: int, sample: bool,
           panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """PRIMARY SAMPLING FRAME (D-POP-1): Enterobacterales AND admission-linked.

    D-COHORT-2 restricts to admission-linked; D-POP-1 further restricts to
    Enterobacterales on structural panel-coverage grounds. The frozen cohort of
    7,796 and its hash are unchanged - this is a sampling decision only.
    """
    fr = frame[frame["hadm_id_final"].notna()].copy()
    if panel is not None:
        keep = enterobacterales_ids(panel, frame)
        fr = fr[fr["micro_specimen_id"].isin(keep)].copy()
    # D-PRIORABX-1 applied as an EXCLUSION GATE as well as a prompt boolean:
    # sustained therapy at the draw is a different decision problem from the
    # empiric pre-culture choice this study measures.
    fr = fr[~fr["prior_abx"].fillna(False)].copy()
    if sample:
        return fr.sample(n=min(n, len(fr)), random_state=SEED).reset_index(drop=True)
    return fr.sort_values(["subject_id", "micro_specimen_id"]).head(n).reset_index(drop=True)


def assemble_cases(sel: pd.DataFrame, panel: pd.DataFrame):
    adm = CA.load_admissions(sel["hadm_id_final"])
    cases = []
    for _, row in sel.iterrows():
        a = adm.get(int(row["hadm_id_final"])) if pd.notna(row["hadm_id_final"]) else None
        cb = CA.build_case_block(row, a, bool(row["prior_abx"]))
        psub = pathogenic_panel(panel, row["micro_specimen_id"])
        rows = [(r["org_name"], r["ab_name"], r["interpretation"])
                for _, r in psub.iterrows()]
        orgs = sorted({str(r[0]) for r in rows if r[0] is not None})
        v = PV.gate_full(cb.text, DRUG_TERMS, orgs)
        if v:
            sys.exit(f"ABORT case {cb.case_id}: case-block gate {v}")
        cases.append({"case_id": cb.case_id, "block": cb, "panel": psub,
                      "rows": rows, "orgs": orgs, "row": row})
    return cases


def write_registry(mechanism: str) -> dict:
    live = None
    with urllib.request.urlopen(OLLAMA_TAGS, timeout=20) as r:
        for m in json.loads(r.read()).get("models", []):
            if m["name"] == MODEL_NAME:
                live = m.get("digest")
    if live != MODEL_DIGEST:
        sys.exit(f"FATAL digest mismatch\n  expected {MODEL_DIGEST}\n  live {live}")
    reg = {"model": MODEL_NAME, "digest": MODEL_DIGEST, "quantization": MODEL_QUANT,
           "options": OPTIONS, "keep_alive": KEEP_ALIVE, "think": THINK,
           "seed": SEED, "thinking_suppression_mechanism": mechanism,
           "model_selection_reason": MODEL_SELECTION_REASON,
           "superseded_model": {"name": "qwen3:4b",
                                "digest": "359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7"},
           "protocol_turns": TURN_ORDER, "n_exchanges": N_EXCHANGES,
           "formulary_size": len(FORMULARY_KEYS), "cohort_hash": COHORT_HASH,
           "scaffold_hashes": SCAFFOLD.pinned,
           "written_at": datetime.now().astimezone().isoformat()}
    (ROOT / "model_registry.json").write_text(json.dumps(reg, indent=2))
    return reg


def run_one_ordering(c, ordering: str) -> tuple[dict, "CaseRunner"]:
    t0 = time.time()
    r = CaseRunner(c["case_id"], c["block"].text, c["rows"], c["orgs"], ordering)
    t1 = r.round0()
    s0 = score(t1["drug"], c["panel"])
    # PHASE SEPARATION: round-0 is scored and persisted before any debate turn.
    persist({"case_id": c["case_id"], "ordering": ordering, "phase": "round0",
             "first_speaker": r.order[0], "drug": t1["drug"],
             "outcome": s0["outcome"], "reason": s0.get("reason"),
             "label": "persona-conditioned zero-shot",
             "micro_specimen_id": int(c["row"]["micro_specimen_id"]),
             "n_isolates": int(len(c["panel"])), "turn": t1}, "round0")
    r.debate()
    a_t = [x for x in r.turns if x["agent"] == "A"]
    b_t = [x for x in r.turns if x["agent"] == "B"]
    fa, fb = a_t[-1]["drug"], b_t[-1]["drug"]
    sa, sb = score(fa, c["panel"]), score(fb, c["panel"])
    tidy = [{"case_id": c["case_id"], "ordering": ordering, "agent": x["agent"],
             "round": x["turn"], "recommendation": x["drug"],
             "turn_text": x["text"], "position_source": x["position_source"]}
            for x in r.turns]
    full = {"case_id": c["case_id"], "ordering": ordering, "phase": "full",
            "first_speaker": r.order[0],
            "micro_specimen_id": int(c["row"]["micro_specimen_id"]),
            "subject_id": int(c["row"]["subject_id"]),
            "n_isolates": int(len(c["panel"])),
            "round0_drug": t1["drug"], "round0_outcome": s0["outcome"],
            "round0_reason": s0.get("reason"),
            "final_A": fa, "final_A_outcome": sa["outcome"],
            "final_B": fb, "final_B_outcome": sb["outcome"],
            # Flip measured against ROUND-0, independent of who spoke first.
            # The previous form only computed this when A opened, so every
            # B-first run returned None and silently halved the denominator.
            # Round-0 is well defined in both orderings, so this is always
            # computable and is ordering-symmetric.
            "changed_A": t1["drug"] != fa,
            "changed_B": t1["drug"] != fb,
            # each agent against its OWN first stated position (needed for
            # uncritical_acceptance, which is per-agent not per-conversation)
            "changed_A_self": (a_t[0]["drug"] != fa) if a_t else None,
            "changed_B_self": (b_t[0]["drug"] != fb) if b_t else None,
            "round0_agent": r.order[0],
            "agreement": fa == fb,
            "quarantined": r.quarantined, "turns": r.turns, "tidy": tidy,
            "final_turn_prompt_eval_count": r.turns[-1]["prompt_eval_count"],
            "max_prompt_eval_count": max(x["prompt_eval_count"] or 0 for x in r.turns),
            "seconds": round(time.time() - t0, 1),
            "model": MODEL_NAME, "digest": MODEL_DIGEST, "seed": SEED}
    persist(full, "full")
    return full, r


def run_case(c) -> list:
    """Run BOTH orderings on the same case (role symmetry)."""
    return [run_one_ordering(c, o) for o in TURN_ORDERS]


def persist(rec: dict, kind: str) -> None:
    RUNS.mkdir(exist_ok=True)
    p = RUNS / f"debate_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with p.open("a") as fh:
        fh.write(json.dumps({"kind": kind, **rec}, default=str) + "\n")


DEADLINE = None
T_START = time.time()


def already_done() -> set:
    """Case ids with BOTH orderings already persisted - makes the run resumable."""
    seen = {}
    for p in RUNS.glob("debate_*.jsonl"):
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("kind") == "full":
                seen.setdefault(r["case_id"], set()).add(r.get("ordering"))
    return {k for k, v in seen.items() if v >= set(TURN_ORDERS)}


def main():
    global DEADLINE, T_START
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["A", "C", "D"])
    ap.add_argument("-n", type=int, default=2)
    ap.add_argument("--deadline", type=str, default=None,
                    help="HH:MM local; stop cleanly after the case in flight")
    a = ap.parse_args()
    T_START = time.time()
    if a.deadline:
        hh, mm = (int(x) for x in a.deadline.split(":"))
        now = datetime.now()
        dl = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if dl < now:
            dl = dl.replace(day=dl.day + 1)
        DEADLINE = dl.timestamp()
        print(f"  hard deadline: {dl:%Y-%m-%d %H:%M} ({(DEADLINE-time.time())/60:.0f} min)")

    frame, stats = build_frame()
    if a.stage == "A":
        print(json.dumps(stats, indent=2))
        return
    panel = load_panel()
    sel = select(frame, a.n, sample=(a.stage == "D"), panel=panel)
    cases = assemble_cases(sel, panel)
    write_registry("model-level (instruct-2507 cannot think) + think:false + parser strip")
    done = already_done()
    todo = [c for c in cases if c["case_id"] not in done]
    print(f"  cases: {len(cases)}  already complete: {len(done & {c['case_id'] for c in cases})}  to run: {len(todo)}")
    for i, c in enumerate(todo, 1):
        if DEADLINE and time.time() > DEADLINE:
            print(f"  DEADLINE reached, stopping cleanly after {i-1} cases this session")
            break
        run_case(c)
        el = time.time() - T_START
        rate = el / i
        print(f"  [{i}/{len(todo)}] {c['case_id']} done  {el/60:.1f} min elapsed, "
              f"{rate:.0f} s/case, ETA {(len(todo)-i)*rate/60:.0f} min", flush=True)


if __name__ == "__main__":
    main()
