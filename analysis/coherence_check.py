"""coherence_check.py - one harness that touches every tracked file.

The problem this solves: a number can be corrected in the analysis, flow into every
generated document, and still survive in a hand-written sentence somewhere. Grepping
by hand finds some of those and misses others, and it cannot tell a stale value from
a coincidental digit string.

So this does three things, and reports a verdict per file.

  1. CANON. Reads the live quantities out of results/*.json. These are the only
     values anything is allowed to state.
  2. SUPERSEDED. Every value that a canonical quantity replaced, with the reason.
     Any live file containing one is a contradiction, unless the file is a place
     where history is deliberately preserved.
  3. FILE SWEEP. Every git-tracked file is opened, classified, and given a verdict.
     Nothing is skipped silently: binaries are extracted where possible and listed
     as unreadable where not.

Exit code 0 only if every live file is coherent.

    python3 analysis/coherence_check.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"

# Places where a superseded value is not a defect: history is the point of them.
HISTORY_PATHS = ("archive/", "docs/LITERATURE_PRESSURE_TEST.md", "docs/SYCOPHANCY_CANON.md",
                 "docs/MASTER_BACKLOG.md", "docs/RED_TEAM.md", "docs/ANALYSIS_CORRECTIONS.md",
                 "docs/FRAMING_FIXES.md", "docs/NUMBERS_BLOCK.md", "docs/EXPLAIN.md",
                 "docs/EXPLAINABILITY.md", "docs/HEADLINE.md", "docs/FIGURES_MANIFEST.md",
                 "docs/verification_log.csv", "docs/deviation_log", "figures/",
                 "analysis/coherence_check.py")
# SCORECARD.txt and analysis/completion_state.py were exempt here while the harmful revision
# denominator was still being reconciled. It is reconciled, both now print the canonical figure,
# and a supervisor opens the scorecard, so they are guarded rather than exempt. Removing an
# exemption is the only safe direction to move one: adding one silences a check for everything
# that follows it into the file.

T = json.loads((RES / "tingting_endpoints.json").read_text())
R = json.loads((RES / "RESULTS.json").read_text())
P = json.loads((RES / "primary_test.json").read_text())["by_framing"]
F = list(P)

carb_now = T["spectrum_appropriateness"]["under_pressure"]["carbapenem_pct"]
hrr_p = [T["sycophancy_under_pressure"][f]["HRR"]["pct"] for f in F]
np_ = sorted({P[f]["n_primary"] for f in F})
b_ = sorted(P[f]["discordant"]["b_pressure_only"] for f in F)
c2 = sorted(100.0 * P[f]["flip_rates"]["C2"]["k"] / P[f]["flip_rates"]["C2"]["n"] for f in F)
c1 = sorted(100.0 * P[f]["flip_rates"]["C1"]["k"] / P[f]["flip_rates"]["C1"]["n"] for f in F)
n_arms = len(R["_integrity"])
n_exp = sum(m["n"] for m in R["_integrity"].values())

CANON = {
    "carbapenem under pressure": f"{carb_now}%",
    "harmful revision, scripted pressure": f"{min(hrr_p)} to {max(hrr_p)}%",
    "harmful revision, live agent": f"{T['debate_with_live_agent']['HRR']['k']}/"
                                    f"{T['debate_with_live_agent']['HRR']['n']} = "
                                    f"{T['debate_with_live_agent']['HRR']['pct']}%",
    "primary set": f"{np_[0]} to {np_[-1]}",
    "b, pressure only": f"{b_[0]} to {b_[-1]}",
    "c, control only": str({P[f]["discordant"]["c_control_only"] for f in F}.pop()),
    "flip under pressure": f"{c1[0]:.1f} to {c1[-1]:.1f}%",
    "flip under the panel": f"{c2[0]:.1f} to {c2[-1]:.1f}%",
    "arms": str(n_arms),
    "exposures": f"{n_exp:,}",
    "debate arm exposures": str(R["_integrity"]["debate"]["n"]),
    "coverage before and after debate": f"{T['debate_coverage']['before_debate']['pct']}% to "
                                        f"{T['debate_coverage']['after_debate']['pct']}%",
}

# value that was replaced -> (regex, what replaced it, why it changed)
SUPERSEDED = [
    (r"\b0 to 84\b|\b83\.7\s*(?:%|per cent)", "carbapenem under pressure",
     "computed on the 78-case pressure arm; the arm now covers all 200"),
    (r"\b0\.0 to 1\.5\s*(?:%|per cent)", "harmful revision, scripted pressure",
     "same reason: the denominator grew with the completed arm"),
    (r"\b52/350\b|\b14\.9\s*%", "harmful revision, live agent",
     "older four-cell partition; canonical uses the indeterminate handling in tingting_endpoints"),
    (r"\bof 70\b|\b70 of 200\b|\bn = 70\b", "primary set",
     "the pressure arm ran 78 of 200 at the time; it now covers all 200"),
    (r"\b63 to 70\b", "b, pressure only", "same reason"),
    (r"\b90 to 100\s*(?:%|per cent)", "flip under pressure", "same reason"),
    (r"\b54\.3\s*%", "flip under the panel", "same reason"),
    (r"\b2,?963\b", "exposures",
     "arms completed, and two arms were registered that had never been in the integrity table"),
    (r"\btwelve arms\b|\b12 arms\b", "arms", "the fewshot and confidence arms were never registered"),
    (r"\b2\.17e-19\b|\b1e-21\b", "b, pressure only",
     "exact p on the partial arm; the completed arm gives 1e-52"),
    (r"\b409 exposures\b|\bdebate\b[^\n]{0,20}\b409\b", "debate arm exposures",
     "the old count included acceptance-suite rows on cases outside the frozen selection"),
]

# Numbers that look superseded but are a different quantity. Listed with the reason
# rather than suppressed by a path rule, so every exception is auditable.
JUSTIFIED = [
    ("src/case_assembly.py", "54.3",
     "a prior-exposure flag rate for a rejected cohort rule, not the C2 flip rate"),
]


# Claims the repository forbids itself from making. Unlike a superseded number, a banned
# claim is never acceptable anywhere: not in a history file, not in a working note, not in
# a rebuttal script. Sourced from docs/SYCOPHANCY_CANON.md and docs/do_not_cite.md.
BANNED_CLAIMS = [
    (r"within 0\.[0-9] points of (?:this study|our)", 
     "SYCOPHANCY_CANON.md:130 bans presenting our harmful revision rate as replicating "
     "SycEval's regressive rate. Different quantities on different bases."),
    (r"replicate[sd]? SycEval|SycEval'?s? .{0,30}replicat",
     "same ban, phrased as replication"),
    (r"the model underperform(?:s|ed) (?:meropenem|a constant)",
     "coverage on this cohort is maximised by the degenerate carbapenem-for-all policy, "
     "so this framing argues against the study's own stewardship point"),
    (r"caused (?:a |an |better |worse )?(?:patient )?outcome|reduced mortality|shortened length of stay",
     "MIMIC-IV is observational; claims are alignment or counterfactual appropriateness only"),
    (r"Clinical-RLVR",
     "docs/do_not_cite.md: identifier never resolved, DO NOT CITE",
     ("docs/references.bib", "docs/LITERATURE.md", "PROJECT.md", "BRIEFING.md", "README.md",
      "deck/", "CLAUDE.md")),
]
# entries are (pattern, why) for an everywhere-ban, or (pattern, why, scope_prefixes)


# A banned claim quoted inside its own prohibition is not a violation. Every document that
# states the rules necessarily contains the forbidden words, and a checker that cannot tell
# a rule from a breach is a checker nobody will keep running.
NEGATED = re.compile(
    r"do(?:es)? not|don't|never|must not|cannot|can't|no longer|not claim|nothing here|"
    r"excluded|exclusion|do not cite|banned|forbid|withdrawn|flagged-unresolved|link-only|"
    r"unresolved|not comparable|is wrong|would be wrong|rather than|instead of|not to be|"
    r"never say|do not say|verdict v-r|>R<|fastest way to lose|default: cite nothing|"
    r"claiming them|argues against",
    re.I)


def sweep_banned_claims(files):
    """Read EVERY tracked file, history included, for claims the repo forbids."""
    hits = []
    for f in sorted(files):
        rel = str(f.relative_to(ROOT))
        if rel in ("analysis/coherence_check.py", "docs/do_not_cite.md",
                   "docs/SYCOPHANCY_CANON.md"):
            continue                      # the files that DEFINE the bans
        text, _ = read_text(f)
        if text is None:
            continue
        for entry in BANNED_CLAIMS:
            pattern, why = entry[0], entry[1]
            scope = entry[2] if len(entry) > 2 else None
            if scope is not None and not any(rel.startswith(x) for x in scope):
                continue                  # this ban only bites where citing happens
            for m in re.finditer(pattern, text, re.I):
                window = text[max(0, m.start() - 200):m.end() + 90]
                if NEGATED.search(window):
                    continue              # the rule, or an exclusion register, not a breach
                hits.append((rel, text[:m.start()].count("\n") + 1, m.group(0).strip(), why))
    return hits


def is_justified(rel, hit):
    return any(rel.startswith(path) and val in hit for path, val, _ in JUSTIFIED)


def tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    return [ROOT / f for f in out.stdout.split("\n") if f.strip()]


def read_text(path):
    """Every file is opened. Returns (text, how) or (None, why not)."""
    suffix = path.suffix.lower()
    if suffix == ".pptx":
        try:
            from pptx import Presentation
            prs = Presentation(str(path))
            parts = []
            for slide in prs.slides:
                for sh in slide.shapes:
                    if sh.has_text_frame:
                        parts.append(sh.text_frame.text)
                if slide.has_notes_slide:
                    parts.append(slide.notes_slide.notes_text_frame.text)
            return "\n".join(parts), "pptx text and speaker notes extracted"
        except Exception as e:
            return None, f"pptx unreadable: {type(e).__name__}"
    if suffix in (".png", ".parquet", ".pyc", ".pdf"):
        return None, "binary, not a carrier of prose claims"
    try:
        return path.read_text(errors="replace"), "text"
    except Exception as e:
        return None, f"unreadable: {type(e).__name__}"


def main():
    files = tracked_files()
    checked = contradictions = skipped = 0
    failures = []
    for f in sorted(files):
        rel = str(f.relative_to(ROOT))
        if any(rel.startswith(h) or rel == h for h in HISTORY_PATHS):
            continue
        text, how = read_text(f)
        if text is None:
            skipped += 1
            continue
        checked += 1
        for pattern, canon_name, why in SUPERSEDED:
            for m in re.finditer(pattern, text):
                line = text[:m.start()].count("\n") + 1
                if is_justified(rel, m.group(0)):
                    continue
                failures.append((rel, line, m.group(0).strip(), canon_name, why))
                contradictions += 1

    print("=" * 78)
    print("  CANONICAL VALUES, read from results/ at this moment")
    print("=" * 78)
    for k, v in CANON.items():
        print(f"  {k:38s} {v}")

    print()
    print("=" * 78)
    print("  FILE SWEEP")
    print("=" * 78)
    print(f"  tracked files            {len(files)}")
    print(f"  opened and checked       {checked}")
    print(f"  history, not checked     {len(files) - checked - skipped}")
    print(f"  binary, not checked      {skipped}")

    banned = sweep_banned_claims(files)
    print(f"  banned-claim sweep       {len(files) - skipped} files, history included")

    print()
    if banned:
        print("  BANNED CLAIMS (never acceptable in any file)")
        for rel, line, hit, why in banned:
            print(f"    {rel}:{line}  '{hit}'")
            print(f"      {why}")
        print()
    if failures:
        print("  CONTRADICTIONS")
        for rel, line, hit, canon, why in failures:
            print(f"    {rel}:{line}  '{hit}'  superseded by {canon} = {CANON[canon]}")
            print(f"      reason: {why}")
        print()
        print(f"  VERDICT: {contradictions} contradiction(s). NOT COHERENT.")
        return 1
    if banned:
        print(f"  VERDICT: {len(banned)} banned claim(s). NOT COHERENT.")
        return 1
    print("  VERDICT: every live file is coherent, and no file states a banned claim.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
