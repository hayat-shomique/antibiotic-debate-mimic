#!/usr/bin/env python
"""fewshot_pass.py - the few-shot arm. Step two of the escalation ladder.

WHY THIS ARM EXISTS
[SUPERVISOR-DIRECTED, 13 July 2026] The escalation ladder is zero-shot, then
few-shot with worked examples, and only if both fail consider training. Zero-shot
is complete. [FACT, runs/debate_20260818.jsonl, kind='full' records] its round-0
recommendation is piperacillin-tazobactam in 224 of 225 ordering-runs and is
verdict-identical to a fixed always-piperacillin-tazobactam policy on 225 of 225
cases. A recommendation that does not vary with the patient is not conditioned on
the patient, so the zero-shot arm did not select. That is the measured reason to
climb one rung: does showing the model worked examples make it attend to the case?

The arm answers one question and is built so that a negative answer is as readable
as a positive one. If the few-shot output is again a single drug on every case, the
ladder's second rung has failed under the same test that the first rung failed, and
the result is stronger than either rung alone because the two share a prompt, a
seed, a scoring rule and a case set.

WHAT IS HELD FIXED AGAINST C0
The system prompt is DR.SCAFFOLD.texts['sys_A_round0'] byte for byte - the same
text control_pass.py uses for C0 and debate_run.py uses for round 0. The options,
the seed, the digest and the scoring call are the same. The single difference is
that the user turn carries k worked examples before the evaluation case. Because
nothing else moves, a difference in the answer is attributable to the examples.
No zero-shot re-run is needed: every case already has a zero-shot answer on disk
from the debate arm and from control_pass.py, and each record here carries it, so
the comparison is paired within case at zero additional model calls.

THE TRAP, AND HOW IT IS CLOSED
The worked examples carry answers derived from susceptibility panels. That is the
whole point of a worked example and it is also the obvious way to ruin the arm. It
is legitimate only if the panels in question belong to OTHER patients, and it is
only demonstrably legitimate if the code refuses to run otherwise.

  1. Examples are drawn from the 993-case primary sampling frame MINUS the 200
     sampled evaluation cases, from a fixed exemplar seed. Both sets are rebuilt
     from debate_run.select in this process rather than read from a cached file.
  2. Disjointness is asserted on case_id AND on subject_id, and a violation raises
     rather than warns. Sharing a patient across the two sets would put one
     patient's demographics in the prompt next to an answer derived from that same
     patient's laboratory work, which is a weaker leak than sharing a case but is
     still a leak.
  3. An example carries exactly one panel-derived token: the canonical drug name.
     The case-block half of every example is gated with provenance.gate_full
     against the WHOLE 261-organism vocabulary and the whole 41-term drug
     vocabulary, not merely against that example's own organisms. The answer half
     must equal a rendered constant template character for character. The set of
     drug terms occurring anywhere in an example must equal the spellings and
     components of that example's own chosen agent and nothing else.
  4. The evaluation case block still receives the full class-2 gate. The example
     text is exempted from that gate by being registered in a frozen scaffold, so
     the exemption is explicit, hashed and recorded, not a hole. The evaluation
     block is asserted to appear in the assembled prompt exactly once and to be
     distinct from every example block, so no example can shadow it.
  5. Every run writes a manifest naming the example case_ids, their chosen agents,
     the seed that drew them, and the hash of the assembled few-shot prefix. Every
     persisted row repeats the example case_ids.

Logged as deviation D-FEWSHOT-1 in deviation_log_proposed.csv.

THE ANSWER RULE, AND WHY IT IS NOT ARBITRARY
An example's correct answer must be an agent the laboratory reports Susceptible on
every pathogenic isolate of that case. On the 793-case pool most cases have several
such agents - a median of 8, range 1 to 12, measured over the 792 eligible cases by
_fs_pool_check.py on 18 August 2026 - so a tie-break rule is unavoidable and it
determines what the examples teach.

  --answer-rule narrowest  (default) the narrowest active agent by spectrum.py's
      SPECTRUM_RANK. Over the eligible pool this rule picks 11 distinct agents,
      the commonest being cefazolin 255, trimethoprim-sulfamethoxazole 217 and
      ampicillin 177. The examples therefore demonstrate an answer that varies
      with the case, which is the demonstration the arm needs to make.
  --answer-rule broadest   the broadest active agent. Over the same pool this
      picks meropenem on 781 of 792. It is a control, not an alternative primary:
      its examples demonstrate a constant answer. If the model copies the
      demonstration rather than reading the case, the two rules diverge in the
      output distribution in the same way they diverge in the examples. If the
      output is a single drug under both rules and that drug is the same one
      zero-shot produced, the model is ignoring the examples as well as the case.

[LIMITATION] SPECTRUM_RANK is a project decision awaiting clinical sign-off, stated
as such at the head of spectrum.py. The narrowest rule inherits that caveat. It also
inherits the taxonomy's main limitation: an agent the laboratory never tested cannot
qualify, so the chosen agent is the narrowest agent SHOWN active, not the narrowest
agent that is active.

[LIMITATION] Every example's reason field is the same contentless constant. A
researcher-written rationale would be an unauditable second channel into the prompt
and a model-written one would make the stimulus a product of the system under
measurement, which this project has already refused elsewhere. The cost is that the
examples teach a format for the reason field and no rationale, and reason-field text
from this arm should not be fed to the indicator-3 evidence labeller.

[DECISION] One example set is drawn and shared by every evaluation case. The
stimulus is then identical across cases for the same reason c1_pressure.py scripts
its challenge: any variation in the output is attributable to the evaluation case
rather than to variation in what was shown. --per-case-examples draws a fresh set
per case, seeded by case_id, as a sensitivity condition.

[DECISION] When k >= 2 the drawn set is required to contain at least two distinct
answers, by drawing further candidates until it does. A set whose k answers are all
the same agent demonstrates case-invariance, which is the thing being tested for,
and would confound the arm. The number of extra draws is logged. --no-vary disables
the requirement and gives a plain seeded draw.

Run the broadest control WITH --no-vary. Under that rule the requirement fights the
rule's whole purpose: a seeded k=4 draw at exemplar seed 20260819 has to reject 13
candidates before it finds a second agent, and the resulting set no longer
demonstrates the constant answer the control is supposed to demonstrate. Checked by
_fs_gate_check.py on 18 August 2026, which draws under both rules without making a
model call.

Nothing here writes to any frozen artefact. This file reads inputs/ and runs/ and
appends only to its own JSONL and manifest under runs/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import time
from datetime import datetime
from pathlib import Path

import duckdb as _duckdb
import pandas as pd

# Machine-sharing courtesy, not a protocol matter. The debate arm and the chained
# passes are live and the GPU is serial. case_assembly.py is read-only and opens
# its own connections, so the two-thread cap is applied by wrapping duckdb.connect
# in THIS process rather than by editing that module.
_DUCKDB_CONNECT = _duckdb.connect


def _capped_connect(*args, **kwargs):
    con = _DUCKDB_CONNECT(*args, **kwargs)
    try:
        con.execute("SET threads TO 2")
    except Exception:
        pass
    return con


_duckdb.connect = _capped_connect

import debate_run as DR
import provenance as PV
import spectrum as SP

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"

CANONICAL_N = 200            # the frozen evaluation selection; see reveal_pass.py
FRAME_N_EXPECTED = 993       # established: the primary sampling frame
EXEMPLAR_SEED = 20260819     # distinct from DR.SEED so the example draw can be
                             # varied without touching the model seed
DEFAULT_K = 4

ANSWER_RULES = ("narrowest", "broadest")

# ---------------------------------------------------------------------------
# few-shot scaffold. Class-1 furniture: no organism, no laboratory value, no
# drug name. Gated at import and again in --selftest against the whole panel
# vocabulary. The DRUG NAME enters only through the rendered answer template.
# ---------------------------------------------------------------------------
FS_PREAMBLE = (
    "WORKED EXAMPLES\n"
    "Below are solved cases from other patients. Each one is followed by the "
    "agent that was correct for that patient. Use them to see how the answer "
    "depends on the case.\n")
FS_EXAMPLE_HDR = "\n\nEXAMPLE {i}\nPATIENT CASE\n"
FS_ANSWER_HDR = "\nCORRECT ANSWER\n"
FS_FINAL_HDR = "\n\nNOW ANSWER FOR THIS NEW PATIENT, in the same format.\n\n"
FS_REASON = "Chosen for this patient."

# The answer half of an example is this template and nothing else. Rendering is
# the ONLY route by which a panel-derived token reaches the prompt.
ANSWER_TEMPLATE = '{{"drug": "{drug}", "reason": "%s"}}' % FS_REASON

# a laboratory value is a number, a unit, or an S/I/R code (same test c1_pressure
# applies to its challenge texts)
LAB_VALUE_RE = re.compile(
    r"\d|\b(mg|g|ml|l|mmol|mcg|ug|units?|cfu|mic|titre|titer|count|level|"
    r"[sir])\b|/l\b|%", re.I)


def render_answer(drug: str) -> str:
    if drug not in DR.BS.FORMULARY:
        raise SystemExit(f"FATAL: example answer {drug!r} is not a formulary key")
    return ANSWER_TEMPLATE.format(drug=drug)


def permitted_drug_terms(canon: str) -> set:
    """Every spelling and every >=5-char component of ONE canonical agent.

    Mirrors provenance.drug_terms so the whitelist is built the same way the
    vocabulary it is checked against is built.
    """
    terms: set = set()
    for n in {canon, *DR.BS.FORMULARY[canon]}:
        terms |= PV.spellings(n)
    comps = {p for t in list(terms) for p in re.split(r"[-/ ]+", t) if len(p) >= 5}
    return terms | comps


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
def all_panel_organisms(panel) -> list:
    return sorted({str(o) for o in panel["org_name"].dropna().unique()})


def assert_scaffold_clean(orgs: list) -> None:
    """The fixed few-shot furniture names no organism, no drug, no lab value."""
    # The example header is checked with a NON-DIGIT placeholder standing in for
    # the index. The index is an ordinal this file generates, not a datum, and it
    # is the only digit any piece of this furniture can carry.
    for name, text in (("FS_PREAMBLE", FS_PREAMBLE),
                       ("FS_EXAMPLE_HDR", FS_EXAMPLE_HDR.format(i="N")),
                       ("FS_ANSWER_HDR", FS_ANSWER_HDR),
                       ("FS_FINAL_HDR", FS_FINAL_HDR),
                       ("FS_REASON", FS_REASON)):
        viol = PV.gate_full(text, DR.DRUG_TERMS, orgs)
        if viol:
            raise SystemExit(f"ABORT scaffold/{name}: class-2 gate {viol}")
        m = LAB_VALUE_RE.search(text)
        if m:
            raise SystemExit(f"ABORT scaffold/{name}: laboratory-value token "
                             f"{m.group(0)!r}")


def assert_example_clean(chunk: str, block: str, drug: str, orgs: list,
                         where: str) -> None:
    """An example carries exactly one panel-derived token: the drug name.

    chunk : the whole example, header + case block + answer header + answer
    block : the case-block text alone
    drug  : the canonical agent the answer names
    orgs  : organism vocabulary to check against (pass the WHOLE panel's)
    """
    answer = render_answer(drug)
    if chunk.count(answer) != 1:
        raise SystemExit(f"ABORT {where}: example does not carry the rendered "
                         f"answer template exactly once")
    # (a) the case-block half is gated in full, drugs included
    non_answer = chunk.replace(answer, "")
    viol = PV.gate_full(non_answer, DR.DRUG_TERMS, orgs)
    if viol:
        raise SystemExit(f"ABORT {where}: example body failed the class-2 gate {viol}")
    # (b) the whole chunk carries no organism and no interpretation vocabulary,
    #     drugs excepted because the answer legitimately names one
    viol = PV.gate_full(chunk, [], orgs)
    if viol:
        raise SystemExit(f"ABORT {where}: example carries organism or "
                         f"interpretation vocabulary {viol}")
    # (b2) bare S/I/R codes. gate_full does not test these - provenance.py applies
    #      INTERP_CODES only inside audit_model_span - and an example whose body
    #      carried one would be handing over a verdict a letter at a time. No
    #      whitelisted case-block field can produce a standalone S, I or R:
    #      checked against the 200 assembled evaluation blocks, 0 hits, 18 August
    #      2026. The check is case-SENSITIVE, as provenance.py's is.
    for pat in PV.INTERP_CODES:
        m = re.search(pat, non_answer)
        if m:
            raise SystemExit(f"ABORT {where}: example body carries a bare "
                             f"interpretation code {m.group(0)!r}")
    # (c) the ONLY drug terms anywhere in the chunk belong to the chosen agent
    allowed = permitted_drug_terms(drug)
    low = chunk.lower()
    stray = sorted({t for t in DR.DRUG_TERMS if t in low and t not in allowed})
    if stray:
        raise SystemExit(f"ABORT {where}: example carries drug terms other than "
                         f"{drug!r}: {stray}")
    # (d) the answer half is the template and nothing else
    tail = chunk.split(FS_ANSWER_HDR)
    if len(tail) != 2 or tail[1] != answer:
        raise SystemExit(f"ABORT {where}: answer half is not the rendered "
                         f"template verbatim")
    # (e) the block half is intact and is what we think it is
    if block not in chunk:
        raise SystemExit(f"ABORT {where}: example does not contain its own case block")


# ---------------------------------------------------------------------------
# example selection
# ---------------------------------------------------------------------------
def choose_answer(panel_sub, rule: str):
    """The example's correct answer, or None when the panel supplies none.

    Activity is NOT re-derived here: spectrum.narrowest_active calls the frozen
    brain_scoring_local.score_case with the frozen ScoringConfig and keeps an
    agent only when the outcome is ADEQUATE, which under
    require_all_pathogens_covered=True and intermediate_as='separate' means the
    laboratory tested the agent on every pathogenic isolate and every verdict
    was S. That is the definition the arm requires.
    """
    na = SP.narrowest_active(panel_sub)
    if na["rank"] is None:
        return None, na
    if rule == "narrowest":
        return sorted(na["agents"])[0], na
    worst = max(na["active"].values())
    return sorted(a for a, r in na["active"].items() if r == worst)[0], na


def build_pool(frame, panel, eval_cases):
    """The 993-case primary frame minus the evaluation cases and their patients."""
    full = DR.select(frame, 10 ** 9, sample=False, panel=panel)
    if len(full) != FRAME_N_EXPECTED:
        raise SystemExit(f"FATAL: primary sampling frame is {len(full)}, expected "
                         f"{FRAME_N_EXPECTED}. The frame moved; stop and find out why.")
    eval_ids = {c["case_id"] for c in eval_cases}
    eval_subj = {int(c["row"]["subject_id"]) for c in eval_cases}
    full = full.copy()
    full["case_id"] = [f"{int(r.subject_id)}_{int(r.micro_specimen_id)}"
                       for r in full.itertuples()]
    if not eval_ids <= set(full["case_id"]):
        raise SystemExit("FATAL: the evaluation selection is not a subset of the "
                         "primary frame; the two were not built from the same pool")
    pool = full[~full["case_id"].isin(eval_ids)]
    n_after_case = len(pool)
    pool = pool[~pool["subject_id"].astype(int).isin(eval_subj)]
    return pool.reset_index(drop=True), {
        "frame_n": int(len(full)),
        "eval_n": len(eval_ids),
        "pool_after_case_id_exclusion": int(n_after_case),
        "pool_after_subject_exclusion": int(len(pool)),
        "dropped_for_subject_overlap": int(n_after_case - len(pool)),
    }


def draw_examples(pool, panel, adm: dict, k: int, rule: str, seed: int,
                  require_vary: bool, eval_blocks: set):
    """Draw k usable examples from a seeded shuffle of the pool.

    A candidate is skipped, with the reason logged, when the panel supplies no
    agent that is Susceptible on every pathogenic isolate, when it has no
    pathogenic isolate rows at all, or when its case block is byte-identical to
    an evaluation case block (which would let the exemption shadow the
    evaluation case in the gate).
    """
    order = list(range(len(pool)))
    random.Random(seed).shuffle(order)
    chosen, skipped = [], []
    for idx in order:
        row = pool.iloc[idx]
        cid = f"{int(row['subject_id'])}_{int(row['micro_specimen_id'])}"
        psub = DR.pathogenic_panel(panel, row["micro_specimen_id"])
        if len(psub) == 0:
            skipped.append({"case_id": cid, "reason": "no pathogenic isolate rows"})
            continue
        drug, na = choose_answer(psub, rule)
        if drug is None:
            skipped.append({"case_id": cid,
                            "reason": "no formulary agent Susceptible on every "
                                      "pathogenic isolate"})
            continue
        a = (adm.get(int(row["hadm_id_final"]))
             if pd.notna(row["hadm_id_final"]) else None)
        cb = DR.CA.build_case_block(row, a, bool(row["prior_abx"]))
        if cb.text in eval_blocks:
            skipped.append({"case_id": cid,
                            "reason": "case block byte-identical to an evaluation case"})
            continue
        cand = {"case_id": cid,
                "subject_id": int(row["subject_id"]),
                "micro_specimen_id": int(row["micro_specimen_id"]),
                "block": cb.text, "drug": drug,
                "spectrum_rank": SP.SPECTRUM_RANK[drug],
                "n_active_agents": na["n_active"],
                "n_pathogenic_isolates": int(psub["org_name"].nunique())}
        chosen.append(cand)
        if len(chosen) < k:
            continue
        if not require_vary or k < 2 or len({c["drug"] for c in chosen}) >= 2:
            break
        # k drawn but all the same agent: replace the last and keep drawing
        chosen.pop()
        skipped.append({"case_id": cid,
                        "reason": "would leave the example set on a single agent "
                                  "(--no-vary disables this requirement)"})
    if len(chosen) < k:
        raise SystemExit(f"FATAL: only {len(chosen)} usable examples in a pool of "
                         f"{len(pool)}; cannot draw k={k}")
    chosen.sort(key=lambda c: c["case_id"])          # deterministic prompt order
    return chosen, skipped


def build_prefix(examples, orgs_all):
    """The assembled few-shot prefix, plus the per-example exempt strings."""
    chunks = []
    for i, ex in enumerate(examples, 1):
        chunk = (FS_EXAMPLE_HDR.format(i=i) + ex["block"] + FS_ANSWER_HDR
                 + render_answer(ex["drug"]))
        assert_example_clean(chunk, ex["block"], ex["drug"], orgs_all,
                             f"example/{ex['case_id']}")
        ex["chunk"] = chunk
        ex["chunk_sha"] = PV.sha(chunk)
        chunks.append(chunk)
    prefix = FS_PREAMBLE + "".join(chunks) + FS_FINAL_HDR
    return prefix


# ---------------------------------------------------------------------------
# persistence, resume, cross-arm zero-shot lookup
# ---------------------------------------------------------------------------
def outpath() -> Path:
    return RUNS / f"fewshot_{datetime.now().strftime('%Y%m%d')}.jsonl"


def manifest_path() -> Path:
    return RUNS / f"fewshot_manifest_{datetime.now().strftime('%Y%m%d')}.json"


def persist(rec: dict) -> None:
    RUNS.mkdir(exist_ok=True)
    with outpath().open("a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def _read_runs(prefix: str):
    for p in sorted(RUNS.glob(f"{prefix}_*.jsonl")):
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def zeroshot_answers() -> dict:
    """case_id -> (drug, source). The zero-shot answer already on disk.

    Both sources use DR.SCAFFOLD.texts['sys_A_round0'] byte for byte at the same
    seed and options, so either is the same measurement. control_pass.py's C0 is
    preferred because it is a single call under exactly this file's call pattern;
    the debate arm's round-0 is the fallback.
    """
    out = {}
    for r in _read_runs("debate"):
        if r.get("kind") == "full" and r.get("round0_drug"):
            out[r["case_id"]] = (r["round0_drug"], "debate_round0")
    for r in _read_runs("c0cn"):
        if r.get("kind") == "c0cn" and r.get("c0_drug"):
            out[r["case_id"]] = (r["c0_drug"], "control_pass_C0")
    return out


def arm_fingerprint(k: int, rule: str, exemplar_seed: int, per_case: bool,
                    require_vary: bool, sys_prompt: str) -> str:
    """Identifies the ARM CONFIGURATION, not one assembled prompt.

    Resume has to key on this rather than on the prefix hash. Under
    --per-case-examples every case gets its own prefix by design, so a
    prefix-keyed resume would read every prior row as a foreign arm and refuse.
    The per-row prefix hash is still persisted, for audit.
    """
    return PV.sha(json.dumps({
        "k": k, "answer_rule": rule, "exemplar_seed": exemplar_seed,
        "per_case_examples": bool(per_case),
        "require_two_distinct_answers": bool(require_vary),
        "sys_prompt_sha": PV.sha(sys_prompt),
        "fs_preamble_sha": PV.sha(FS_PREAMBLE),
        "fs_example_hdr_sha": PV.sha(FS_EXAMPLE_HDR),
        "fs_answer_hdr_sha": PV.sha(FS_ANSWER_HDR),
        "fs_final_hdr_sha": PV.sha(FS_FINAL_HDR),
        "answer_template_sha": PV.sha(ANSWER_TEMPLATE),
        "model": DR.MODEL_NAME, "digest": DR.MODEL_DIGEST, "seed": DR.SEED,
    }, sort_keys=True))


def done_ids(arm_sha: str) -> set:
    """Case ids already run UNDER THIS EXACT ARM CONFIGURATION.

    A resumed run under different parameters is not the same arm, so its records
    must not be silently mixed. Rows written under a different fingerprint are
    reported and refused rather than skipped.
    """
    same, other = set(), set()
    for r in _read_runs("fewshot"):
        if r.get("kind") != "fewshot":
            continue
        (same if r.get("fewshot_arm_sha") == arm_sha else other).add(r["case_id"])
    if other:
        raise SystemExit(
            f"FATAL: {len(other)} rows in runs/fewshot_*.jsonl were written under a "
            f"different arm configuration than the one just built. Put --exemplar-seed, "
            f"--k, --answer-rule, --per-case-examples and --no-vary back, or move the "
            f"old file aside. Refusing to mix arms.")
    return same


# ---------------------------------------------------------------------------
def selftest(panel) -> None:
    DR.SCAFFOLD.assert_unchanged()
    orgs = all_panel_organisms(panel)
    print(f"  organism vocabulary: {len(orgs)} distinct org_name values", flush=True)
    print(f"  drug vocabulary:     {len(DR.DRUG_TERMS)} terms", flush=True)
    assert_scaffold_clean(orgs)
    print("  CLEAN  few-shot scaffold carries no organism, drug or laboratory value",
          flush=True)
    # a well-formed example must pass
    good_block = ("Age: 61\nSex: male\nAdmission type: SURGICAL SAME DAY ADMISSION\n"
                  "Prior antibiotic exposure before this assessment: no\n"
                  "Laboratory results: not available at this decision point")
    chunk = (FS_EXAMPLE_HDR.format(i=1) + good_block + FS_ANSWER_HDR
             + render_answer("cefazolin"))
    assert_example_clean(chunk, good_block, "cefazolin", orgs, "selftest/positive")
    print("  PASSES a well-formed example naming exactly one agent", flush=True)
    # negative controls: the example gate must fire on things that ARE dirty
    probes = [
        ("second drug name in the body",
         FS_EXAMPLE_HDR.format(i=1) + good_block + "\nMeropenem was also active."
         + FS_ANSWER_HDR + render_answer("cefazolin"), good_block, "cefazolin"),
        ("organism named in the body",
         FS_EXAMPLE_HDR.format(i=1) + good_block + "\nEscherichia coli grew."
         + FS_ANSWER_HDR + render_answer("cefazolin"), good_block, "cefazolin"),
        ("interpretation word in the body",
         FS_EXAMPLE_HDR.format(i=1) + good_block + "\nThe isolate was susceptible."
         + FS_ANSWER_HDR + render_answer("cefazolin"), good_block, "cefazolin"),
        ("answer half not the template",
         FS_EXAMPLE_HDR.format(i=1) + good_block + FS_ANSWER_HDR
         + '{"drug": "cefazolin", "reason": "the E. coli was S to it"}',
         good_block, "cefazolin"),
    ]
    for label, chunk, block, drug in probes:
        fired = False
        try:
            assert_example_clean(chunk, block, drug, orgs, "selftest/negative")
        except SystemExit:
            fired = True
        print(f"  {'FIRES ' if fired else 'MISSED'} negative control: {label}", flush=True)
        if not fired:
            raise SystemExit(f"FATAL: example gate did not fire on {label!r}")
    print("  SELFTEST PASSED", flush=True)


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="few-shot arm - worked examples from "
                                             "outside the evaluation sample")
    ap.add_argument("-n", type=int, default=CANONICAL_N,
                    help="evaluation cases to run (cases, one model call each)")
    ap.add_argument("--k", type=int, default=DEFAULT_K,
                    help="worked examples per prompt (default 4)")
    ap.add_argument("--answer-rule", choices=ANSWER_RULES, default="narrowest",
                    help="narrowest = primary; broadest = the constant-answer control")
    ap.add_argument("--exemplar-seed", type=int, default=EXEMPLAR_SEED,
                    help="seed for the example draw only; the model seed is fixed")
    ap.add_argument("--per-case-examples", action="store_true",
                    help="draw a fresh example set per evaluation case (sensitivity)")
    ap.add_argument("--no-vary", action="store_true",
                    help="do not require the example set to name two distinct agents")
    ap.add_argument("--deadline", type=str, default=None, help="HH:MM local")
    ap.add_argument("--selftest", action="store_true",
                    help="run the gate assertions and exit; makes no model call")
    a = ap.parse_args()

    panel = DR.load_panel()
    if a.selftest:
        selftest(panel)
        return
    if a.k < 1:
        raise SystemExit("FATAL: --k must be at least 1")

    dl = None
    if a.deadline:
        hh, mm = (int(x) for x in a.deadline.split(":"))
        now = datetime.now()
        d = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if d < now:
            d = d.replace(day=d.day + 1)
        dl = d.timestamp()
        print(f"  deadline {d:%d %b %H:%M}", flush=True)

    DR.SCAFFOLD.assert_unchanged()
    orgs_all = all_panel_organisms(panel)
    assert_scaffold_clean(orgs_all)

    frame, _ = DR.build_frame()

    # The canonical evaluation selection, rebuilt twice and checked rather than
    # assumed, as reveal_pass.py and c1_pressure.py do.
    sel_all = DR.select(frame, CANONICAL_N, sample=True, panel=panel)
    e1 = DR.assemble_cases(sel_all, panel)
    e2 = DR.assemble_cases(sel_all, panel)
    if ({c["case_id"]: c["block"].text for c in e1}
            != {c["case_id"]: c["block"].text for c in e2}):
        raise SystemExit("FATAL: case-block reconstruction is not deterministic")
    eval_cases = e1
    eval_blocks = {c["block"].text for c in eval_cases}

    pool, pool_stats = build_pool(frame, panel, eval_cases)
    print(f"  primary frame {pool_stats['frame_n']}, evaluation {pool_stats['eval_n']}, "
          f"example pool {pool_stats['pool_after_subject_exclusion']} "
          f"({pool_stats['dropped_for_subject_overlap']} dropped for subject overlap)",
          flush=True)

    # admissions for the whole pool, fetched once: --per-case-examples redraws
    # 200 times and must not hit prescriptions/admissions once per draw
    pool_adm = DR.CA.load_admissions(pool["hadm_id_final"])
    examples, skipped = draw_examples(pool, panel, pool_adm, a.k, a.answer_rule,
                                      a.exemplar_seed, not a.no_vary, eval_blocks)
    prefix = build_prefix(examples, orgs_all)
    prefix_sha = PV.sha(prefix)

    # ---- the disjointness assertions, hard failures, stated in the log ----
    ex_ids = {e["case_id"] for e in examples}
    ex_subj = {e["subject_id"] for e in examples}
    eval_ids = {c["case_id"] for c in eval_cases}
    eval_subj = {int(c["row"]["subject_id"]) for c in eval_cases}
    if ex_ids & eval_ids:
        raise SystemExit(f"FATAL D-FEWSHOT-1: example case_ids appear in the "
                         f"evaluation set: {sorted(ex_ids & eval_ids)}")
    if ex_subj & eval_subj:
        raise SystemExit(f"FATAL D-FEWSHOT-1: example subjects appear in the "
                         f"evaluation set: {sorted(ex_subj & eval_subj)}")
    if len(ex_ids) != len(examples):
        raise SystemExit("FATAL: the example set repeats a case")
    print(f"  examples k={a.k} rule={a.answer_rule} seed={a.exemplar_seed}: "
          f"{', '.join(e['case_id'] + '->' + e['drug'] for e in examples)}", flush=True)
    print(f"  disjoint from the evaluation set on case_id and on subject_id: yes",
          flush=True)
    print(f"  candidates skipped while drawing: {len(skipped)}", flush=True)
    for s in skipped:
        print(f"      skip {s['case_id']}: {s['reason']}", flush=True)

    # The few-shot text is exempted from the class-2 gate by being registered in
    # a frozen scaffold. DR.SCAFFOLD itself is untouched.
    scaffold_fs = PV.StaticScaffold(texts={
        **DR.SCAFFOLD.texts,
        "fs_preamble": FS_PREAMBLE,
        "fs_final_hdr": FS_FINAL_HDR,
        **{f"fs_example_{e['case_id']}": e["chunk"] for e in examples},
    })
    scaffold_fs.freeze()

    sys_prompt = DR.SCAFFOLD.texts["sys_A_round0"]        # byte-identical to C0
    arm_sha = arm_fingerprint(a.k, a.answer_rule, a.exemplar_seed,
                              a.per_case_examples, not a.no_vary, sys_prompt)
    zs = zeroshot_answers()
    done = done_ids(arm_sha)
    cases = eval_cases[: a.n]
    todo = [c for c in cases if c["case_id"] not in done]

    manifest = {
        "arm": "few-shot", "deviation": "D-FEWSHOT-1",
        "written_at": datetime.now().astimezone().isoformat(),
        "k": a.k, "answer_rule": a.answer_rule, "exemplar_seed": a.exemplar_seed,
        "per_case_examples": bool(a.per_case_examples),
        "require_two_distinct_answers": not a.no_vary,
        "examples": [{kk: e[kk] for kk in ("case_id", "subject_id",
                                           "micro_specimen_id", "drug",
                                           "spectrum_rank", "n_active_agents",
                                           "n_pathogenic_isolates", "chunk_sha")}
                     for e in examples],
        "n_distinct_example_answers": len({e["drug"] for e in examples}),
        "skipped_candidates": skipped,
        "n_skipped": len(skipped),
        "pool": pool_stats,
        "disjoint_case_id": True, "disjoint_subject_id": True,
        "fewshot_arm_sha": arm_sha,
        "fewshot_prefix_sha": prefix_sha,
        "fewshot_prefix_chars": len(prefix),
        "sys_prompt_sha": PV.sha(sys_prompt),
        "sys_prompt_identical_to_debate_round0": sys_prompt == DR.SCAFFOLD.texts["sys_A_round0"],
        "scaffold_pinned_debate": DR.SCAFFOLD.pinned,
        "scaffold_pinned_fewshot": scaffold_fs.pinned,
        "evaluation_case_ids_sha": hashlib.sha256(
            "\n".join(sorted(eval_ids)).encode()).hexdigest(),
        "n_evaluation_cases": len(cases),
        "model": DR.MODEL_NAME, "digest": DR.MODEL_DIGEST, "seed": DR.SEED,
        "options": DR.OPTIONS, "keep_alive": DR.KEEP_ALIVE, "think": DR.THINK,
        "cohort_hash": DR.COHORT_HASH,
    }
    RUNS.mkdir(exist_ok=True)
    manifest_path().write_text(json.dumps(manifest, indent=2, default=str))
    print(f"  manifest {manifest_path()}", flush=True)
    print(f"  arm sha {arm_sha[:16]}   prefix sha {prefix_sha[:16]}  "
          f"{len(prefix)} chars", flush=True)
    print(f"  cases {len(cases)}, already done {len(done)}, to run {len(todo)}, "
          f"{len(todo)} model calls", flush=True)
    print(f"  writing {outpath()}", flush=True)

    t0 = time.time()
    for i, c in enumerate(todo, 1):
        if dl and time.time() > dl:
            print(f"  deadline reached after {i-1} cases", flush=True)
            break
        cid = c["case_id"]

        ex_here, pre_here, sha_here, sc_here = examples, prefix, prefix_sha, scaffold_fs
        sk_here = skipped
        if a.per_case_examples:
            seed_here = (a.exemplar_seed
                         + int(hashlib.sha256(cid.encode()).hexdigest()[:8], 16))
            ex_here, sk_here = draw_examples(pool, panel, pool_adm, a.k,
                                             a.answer_rule, seed_here,
                                             not a.no_vary, eval_blocks)
            if {e["case_id"] for e in ex_here} & eval_ids:
                raise SystemExit(f"FATAL D-FEWSHOT-1: per-case examples for {cid} "
                                 f"intersect the evaluation set")
            if {e["subject_id"] for e in ex_here} & eval_subj:
                raise SystemExit(f"FATAL D-FEWSHOT-1: per-case examples for {cid} "
                                 f"intersect the evaluation subjects")
            pre_here = build_prefix(ex_here, orgs_all)
            sha_here = PV.sha(pre_here)
            sc_here = PV.StaticScaffold(texts={
                **DR.SCAFFOLD.texts, "fs_preamble": FS_PREAMBLE,
                "fs_final_hdr": FS_FINAL_HDR,
                **{f"fs_example_{e['case_id']}": e["chunk"] for e in ex_here}})
            sc_here.freeze()

        block = DR.SCAFFOLD.texts["case_header"] + c["block"].text
        user = pre_here + block

        # the evaluation block must be present exactly once and must not be
        # shadowed by an exempt example string
        if user.count(c["block"].text) != 1:
            raise SystemExit(f"ABORT {cid}: evaluation case block occurs "
                             f"{user.count(c['block'].text)} times in the prompt")

        gate = PV.gate_assembled_prompt(sys_prompt + "\n" + user, PV.SpanRegistry(),
                                        sc_here, DR.DRUG_TERMS, c["orgs"],
                                        c["rows"], DR.BS.canon_drug)
        if gate["abort"]:
            raise SystemExit(f"ABORT {cid}: few-shot prompt gate "
                             f"{gate['residue_violations']}")

        r = DR.ollama_chat(sys_prompt, user)
        text = r["content"]
        drug = DR.parse_drug(text)
        source = "explicit"
        ev, pe = r["eval_count"], r["prompt_eval_count"]
        if drug == DR.INVALID:
            r2 = DR.ollama_chat(sys_prompt, user + "\n\n" + DR.SCAFFOLD.texts["retry"])
            text = text + "\n---RETRY---\n" + r2["content"]
            drug = DR.parse_drug(r2["content"])
            source = "retry"
            ev = (ev or 0) + (r2["eval_count"] or 0)
            pe = max(pe or 0, r2["prompt_eval_count"] or 0)
        s = DR.score(drug, c["panel"])
        z_drug, z_src = zs.get(cid, (None, None))

        persist({
            "kind": "fewshot", "condition": "FS_worked_examples",
            "arm": "few-shot", "deviation": "D-FEWSHOT-1",
            "case_id": cid,
            "micro_specimen_id": int(c["row"]["micro_specimen_id"]),
            "subject_id": int(c["row"]["subject_id"]),
            "n_isolates": int(len(c["panel"])),
            # the arm's own parameters, on every row
            "k": a.k, "answer_rule": a.answer_rule,
            "exemplar_seed": a.exemplar_seed,
            "per_case_examples": bool(a.per_case_examples),
            "example_case_ids": [e["case_id"] for e in ex_here],
            "example_subject_ids": [e["subject_id"] for e in ex_here],
            "example_drugs": [e["drug"] for e in ex_here],
            "example_spectrum_ranks": [e["spectrum_rank"] for e in ex_here],
            "n_distinct_example_answers": len({e["drug"] for e in ex_here}),
            "n_candidates_skipped_drawing": len(sk_here),
            "fewshot_arm_sha": arm_sha,
            "fewshot_prefix_sha": sha_here,
            "fewshot_prefix_chars": len(pre_here),
            # the answer
            "fs_drug": drug, "fs_outcome": s["outcome"], "fs_reason": s.get("reason"),
            "fs_position_source": source, "fs_text": text,
            "answer_in_examples": drug in {e["drug"] for e in ex_here},
            # the paired zero-shot answer already on disk, no extra call
            "zeroshot_drug": z_drug, "zeroshot_source": z_src,
            "changed_vs_zeroshot": (None if z_drug is None else z_drug != drug),
            # everything C0 records
            "has_think_tag": "<think>" in text or "</think>" in text,
            "eval_count": ev, "prompt_eval_count": pe,
            "gate_residue_chars": gate["residue_chars"],
            "gate_n_model_spans": gate["n_model_spans"],
            "gate_quarantine": gate["quarantine"],
            "sys_prompt_sha": PV.sha(sys_prompt),
            "model": DR.MODEL_NAME, "digest": DR.MODEL_DIGEST, "seed": DR.SEED,
            "seconds": round(r["wall_s"], 1),
        })
        el = time.time() - t0
        flag = "" if z_drug is None else (" SAME-AS-ZEROSHOT" if z_drug == drug
                                          else f" MOVED from {z_drug}")
        print(f"  [{i}/{len(todo)}] {cid} fs={drug} {s['outcome']}{flag}  "
              f"{el/i:.0f}s/case, ETA {(len(todo)-i)*el/i/60:.0f} min", flush=True)

    print(f"\n  done. analyse with:  python fewshot_analyze.py", flush=True)


if __name__ == "__main__":
    main()
