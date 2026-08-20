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
                 # A ledger of corrections has to be able to name what was corrected.
                 # Numbers are exempt here for the same reason they are exempt in the
                 # other history files; the banned-claim sweep still reads it, because
                 # a banned claim is never acceptable in any file.
                 "docs/OVERNIGHT_LEDGER.md",
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

TRIG = json.loads((RES / "trigger_comparison.json").read_text())
TRIG_REV = TRIG["after_the_debate_does_the_panel_repair_it"]
TRIG_DEB = TRIG["trigger_a_counterpart_with_no_evidence"]
_one = [v["harmful_revision_rate_pct"] for v in TRIG["trigger_one_content_free_challenge"].values()]
TRIG_ONE_LO, TRIG_ONE_HI = min(_one), max(_one)

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
    "panel repair rate": f"{TRIG_REV['beneficial_corrections']}/{TRIG_REV['entered_inadequate']}"
                         f" = {TRIG_REV['beneficial_correction_rate_pct']}%",
    "harmful revision, one turn against five": f"{TRIG_ONE_LO} to {TRIG_ONE_HI}% against "
                                               f"{TRIG_DEB['harmful_revision_rate_pct']}%",
}

# value that was replaced -> (regex, what replaced it, why it changed)
SUPERSEDED = [
    (r"\b0 to 84\b|\b83\.7\s*(?:%|per cent)", "carbapenem under pressure",
     "computed on the 78-case pressure arm; the arm now covers all 200"),
    (r"\b0\.0 to 1\.5\s*(?:%|per cent)", "harmful revision, scripted pressure",
     "same reason: the denominator grew with the completed arm"),
    (r"\b52/350\b|\b14\.9\s*%", "harmful revision, live agent",
     "older four-cell partition; canonical uses the indeterminate handling in tingting_endpoints"),
    (r"\b33/175\b|\b18\.9\s*%|\b28/175\b|\b16\.0\s*%", "harmful revision, live agent",
     "the core figure once split on 'not adequate', which folded INTERMEDIATE_ONLY and "
     "UNDETERMINED into the incorrect side. The supervisor's classification has four cells and "
     "no cell for undetermined, so those runs are excluded. Per agent the canonical figures are "
     "29/171 for Agent A and 23/170 for Agent B, which sum to the pooled 52"),
    (r"\b12/25\b|\b48\.0\s*%|\b11/25\b|\b44\.0\s*%", "beneficial correction",
     "same convention change on the other direction of the transition"),
    (r"\b57/69\b|\b82\.6\s*%|\b311/312\b", "panel repair rate",
     "the escalation row filtered only the entering side for determinacy, so runs whose "
     "post-panel answer cannot be scored sat in the denominator as failures to repair. Both "
     "ends determinate gives 57/65 = 87.7% repaired and 311/311 held, which is what the core "
     "figure and results/trigger_comparison.json compute from the same runs"),
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
    # docs/do_not_cite.md carries three unresolved identifiers and this sweep enforced one of
    # them. All three are enforced now, in the files where citing actually happens.
    (r"Clinical-RLVR",
     "docs/do_not_cite.md: identifier never resolved, DO NOT CITE",
     ("docs/references.bib", "docs/LITERATURE.md", "PROJECT.md", "BRIEFING.md", "README.md",
      "deck/", "CLAUDE.md", "AUDIT.md", "docs/HEADLINE.md", "docs/SUPERVISOR_ASKS.md")),
    (r"fundamental flaw leaves LLMs strikingly vulnerable|MIT Technology Review",
     "docs/do_not_cite.md: trade press, no DOI and no retrievable author, DO NOT CITE. "
     "Cite the primary paper the article reports on instead",
     ("docs/references.bib", "docs/LITERATURE.md", "PROJECT.md", "BRIEFING.md", "README.md",
      "deck/", "CLAUDE.md", "AUDIT.md", "docs/HEADLINE.md", "docs/SUPERVISOR_ASKS.md")),
    (r"LLMs? can'?t jump|klU4737opt",
     "docs/do_not_cite.md: OpenReview forum id with no indexed record, venue unverified. "
     "Do not cite it as a paper until the venue resolves",
     ("docs/references.bib", "docs/LITERATURE.md", "PROJECT.md", "BRIEFING.md", "README.md",
      "deck/", "CLAUDE.md", "AUDIT.md", "docs/HEADLINE.md", "docs/SUPERVISOR_ASKS.md")),
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


def _plain(t):
    """Markdown and HTML emphasis splits a negation in two: "Do **not** say" does not match a
    pattern looking for "do not". Emphasis is removed before the negation test."""
    return re.sub(r"</?[a-zA-Z][^>]*>", " ", t).replace("**", "").replace("__", "") \
             .replace("*", "").replace("_", "").replace("`", "")


_SENT_END = re.compile(r"[.!?]\s|\n\s*\n|\n\s*[-*|#]")


def _sentence_is_negated(text, m):
    """True when the match sits in a sentence that forbids it rather than states it.

    The window is the sentence containing the match, with the match itself removed. Sentence
    boundaries are full stops, blank lines, and the start of a markdown list row, table row or
    heading, because a register of forbidden items is written as a list and each row is its own
    statement."""
    starts = [x.end() for x in _SENT_END.finditer(text, 0, m.start())]
    lo = starts[-1] if starts else max(0, m.start() - 400)
    nxt = _SENT_END.search(text, m.end())
    hi = nxt.start() if nxt else min(len(text), m.end() + 400)
    before, after = text[lo:m.start()], text[m.end():hi]
    # A forbidden item is usually written inside a list whose header carries the prohibition:
    # a "never say" block, a do-not register. The item's own row does not repeat the negation,
    # so the row alone reads as a breach. Look back to the line that opened the list.
    line_start = text.rfind("\n", 0, m.start()) + 1
    if re.match(r"\s*(?:[-*+]|\d+[.)]|<li|\|)", text[line_start:m.start()] or " "):
        head_lo = max(0, line_start - 300)
        header = text[head_lo:line_start]
        before = header + before
    return bool(NEGATED.search(_plain(before)) or NEGATED.search(_plain(after)))


# Two values can each be canonical and still be wrong together. The panel arrives in this study
# in two ways: in the clean-context arm it REPLACES the debate, measured from the round-0 position
# over 200 runs; in the reveal arm it FOLLOWS the debate, measured from the post-debate position
# over 400 runs. Six files paired a harmful revision rate from the first with a coverage change
# from the second, in one row, describing an experiment nobody ran. Every number in those rows was
# canonical, so the sweep above passed them all.
#
# Each entry is (pattern A, pattern B, how close is too close, why). A and B appearing within that
# many characters of each other is the defect, because that is the width of a table row or a
# sentence.
PAIR_BANS = [
    (r"\b2/174\b|\b1\.1\s*%", r"\b95\.2\s*%|\+?17\.2 points", 220,
     "the clean-context arm's harmful revision rate beside the reveal arm's coverage change. "
     "They are different arms on different denominators from different starting positions. Use "
     "the reveal arm's own rate, 0 of 311, when the row is about the panel following the debate"),
    (r"\b15\.2\s*%|\b52/341\b", r"\b1\.1 to 3\.5\s*%", 200,
     "the five-turn debate rate beside the one-turn pressure band, with nothing saying the "
     "number of turns differs. Name the turns on both sides or the comparison reads as a "
     "framing effect"),
]


def sweep_pair_bans(files):
    """Values that are each canonical and wrong when placed together."""
    hits = []
    for f in sorted(files):
        rel = str(f.relative_to(ROOT))
        if rel in ("analysis/coherence_check.py",) or rel.startswith(HISTORY_PATHS):
            continue
        text, _ = read_text(f)
        if text is None:
            continue
        for pa, pb, span, why in PAIR_BANS:
            for ma in re.finditer(pa, text, re.I):
                lo, hi = max(0, ma.start() - span), ma.end() + span
                mb = re.search(pb, text[lo:hi], re.I)
                if not mb:
                    continue
                window = text[lo:hi]
                # A row that names both arms is doing the right thing, not the wrong one.
                if re.search(r"after the debate|replac|different arm|following it|reveal arm|"
                             r"clean.context|five turns|one turn|per framing", window, re.I):
                    continue
                hits.append((rel, text[:ma.start()].count("\n") + 1,
                             f"{ma.group(0).strip()} near {mb.group(0).strip()}", why))
                break
    return hits


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
                # Two faults were found here by fault injection, and both made the sweep
                # report clean on real breaches.
                #
                # First, the window used to include the matched text, so a banned phrase
                # containing a negation word negated its own ban. The entry for the position
                # paper whose title contains "can't" never fired once.
                #
                # Second, and worse, the window was 200 characters of surrounding text, so a
                # negation anywhere nearby silenced the ban. One "does not" earlier in a
                # paragraph switched off every ban after it. Planting three banned citations
                # in README.md caught one of the three.
                #
                # The guard is now the sentence the match sits in, which is what "the rule
                # rather than a breach" actually means: a file that states the rule states it
                # in the same sentence as the thing it forbids.
                if _sentence_is_negated(text, m):
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
    pairs = sweep_pair_bans(files)
    print(f"  mismatched-pair sweep    {len(PAIR_BANS)} rules over the live files")

    print()
    if pairs:
        print("  MISMATCHED PAIRS (each value canonical, wrong together)")
        for rel, line, hit, why in pairs:
            print(f"    {rel}:{line}  {hit}")
            print(f"      {why}")
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
    if banned or pairs:
        bits = []
        if banned:
            bits.append(f"{len(banned)} banned claim(s)")
        if pairs:
            bits.append(f"{len(pairs)} mismatched pair(s)")
        print(f"  VERDICT: {' and '.join(bits)}. NOT COHERENT.")
        return 1
    print("  VERDICT: every live file is coherent, no file states a banned claim, and no file "
          "pairs two arms in one row.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
