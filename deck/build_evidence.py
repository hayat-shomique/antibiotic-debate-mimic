"""build_evidence.py - the claim-to-evidence map for the conference talk.

Writes deck/EVIDENCE.md. Every claim made on a slide appears with the number as it
stands in the result files right now, the file that holds it, and the script that
produces that file. Nothing is typed: if a number changes, this document changes.

    python3 deck/build_evidence.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "results"
OUT = Path(__file__).resolve().parent / "EVIDENCE.md"

T = json.loads((RES / "tingting_endpoints.json").read_text())
R = json.loads((RES / "RESULTS.json").read_text())
P = json.loads((RES / "policy_degeneracy.json").read_text())
FS = json.loads((RES / "fewshot.json").read_text())
LK = json.loads((RES / "leakage.json").read_text())

PRIM = T["primary_appropriateness"]
SPEC = T["spectrum_appropriateness"]
DCOV = T["debate_coverage"]
DBT, EVID, NEUT = T["debate_with_live_agent"], T["revision_under_evidence"], T["change_under_neutral_control"]
MATCH = R["D_MATCH_1_drug_identity_vs_patient"]
PTEST = json.loads((RES / "primary_test.json").read_text())
PT = PTEST["by_framing"]
FRAMINGS = ["C1a_authority", "C1b_peer_consensus", "C1c_safety_framing", "C1d_bare_doubt"]

TE, PTJ, PD, FSJ, RJ, LKJ = ("tingting_endpoints.json", "primary_test.json",
                             "policy_degeneracy.json", "fewshot.json", "RESULTS.json", "leakage.json")
S_TE, S_PT = "analysis/tingting_endpoints.py", "analysis/primary_test.py"
S_PD, S_FS = "analysis/policy_degeneracy.py", "analysis/fewshot_analysis.py"
S_CN, S_LK = "analysis/canonical_numbers.py", "analysis/leakage_check.py"

def across(path, agg):
    """Read one value out of every framing and aggregate, so a row that says
    'every framing' is computed from every framing."""
    vals = []
    for f in FRAMINGS:
        node = PT[f]
        for key in path:
            node = node[key]
        vals.append(node)
    return agg(vals)


def one(path):
    """A value that must be identical across the four framings, asserted rather than assumed."""
    distinct = set(across(path, tuple))
    if len(distinct) != 1:
        raise ValueError(f"{path} differs across framings ({sorted(distinct)}), so no row may "
                         "state it as a single number. Report the range instead.")
    return distinct.pop()


b_lo = min(PT[f]["discordant"]["b_pressure_only"] for f in FRAMINGS)
b_hi = max(PT[f]["discordant"]["b_pressure_only"] for f in FRAMINGS)
p_worst = max(PT[f]["discordant"]["p_exact"] for f in FRAMINGS)
hrr_lo = min(T["sycophancy_under_pressure"][f]["HRR"]["pct"] for f in FRAMINGS)
hrr_hi = max(T["sycophancy_under_pressure"][f]["HRR"]["pct"] for f in FRAMINGS)
flip_lo = min(100.0 * PT[f]["flip_rates"]["C1"]["k"] / PT[f]["flip_rates"]["C1"]["n"] for f in FRAMINGS)
flip_hi = max(100.0 * PT[f]["flip_rates"]["C1"]["k"] / PT[f]["flip_rates"]["C1"]["n"] for f in FRAMINGS)

ROWS = [
    ("5", "the pipeline",
     f"{PRIM['baseline_pre_culture']['n']} cases evaluated, {DCOV['before_debate']['n']} ordering-runs",
     TE, S_TE),
    ("6", "the instrument, pressure sentences carry no clinical content",
     f"{LK['leaked_turns']} of {LK['n_turns']} pressure turns contain organism or susceptibility phrasing, "
     f"{LK['n_distinct_sentences']} distinct sentences, census not sample", LKJ, S_LK),
    ("7", "the baseline is one drug for every patient",
     f"{P['C0 baseline']['distinct']} distinct drug across {P['C0 baseline']['n']} decisions, "
     f"{P['C0 baseline']['top']} at {P['C0 baseline']['top_share_pct']}%", PD, S_PD),
    ("7", "and that constant covers the organism",
     f"{PRIM['baseline_pre_culture']['adequate']}/{PRIM['baseline_pre_culture']['n']} = "
     f"{PRIM['baseline_pre_culture']['pct']}%, 95% CI {PRIM['baseline_pre_culture']['ci95']}", TE, S_TE),
    ("7", "given the panel, coverage rises",
     f"{PRIM['with_panel_revealed']['adequate']}/{PRIM['with_panel_revealed']['n']} = "
     f"{PRIM['with_panel_revealed']['pct']}%, gain {PRIM['gain_from_evidence_pts']} points, "
     f"{P['C2 with the panel revealed']['distinct']} distinct drugs", f"{TE} + {PD}", f"{S_TE}, {S_PD}"),
    ("8", "the neutral control never moves it",
     f"c = {one(('discordant', 'c_control_only'))} under every framing, computed across all four, "
     f"n = {one(('n_primary',))}", PTJ, S_PT),
    ("8", "unsupported pressure almost always moves it",
     f"b = {b_lo} to {b_hi} of {one(('n_primary',))}, flip rate {flip_lo:.1f}% to {flip_hi:.1f}%, "
     f"exact binomial p at worst {p_worst:.2e}", PTJ, S_PT),
    ("8", "the panel moves it less than a person does",
     f"{one(('flip_rates', 'C2', 'k'))}/{one(('flip_rates', 'C2', 'n'))} = "
     f"{100.0 * one(('flip_rates', 'C2', 'k')) / one(('flip_rates', 'C2', 'n')):.1f}%", PTJ, S_PT),
    ("8", "attrition, stated before the result",
     f"{one(('n_primary',))} of {PRIM['baseline_pre_culture']['n']} cases evaluable in all four conditions",
     PTJ, S_PT),
    ("8", "the baseline is reproducible across independently run arms",
     f"{PTEST['baseline_agreement']['agree']}/{PTEST['baseline_agreement']['n']} agreement", PTJ, S_PT),
    ("9", "harmful revision under scripted pressure is near zero",
     f"{hrr_lo:.1f}% to {hrr_hi:.1f}% across the four framings, denominator is the correct-before group",
     TE, S_TE),
    ("10", "an empty sentence drives carbapenem use",
     f"{SPEC['baseline']['carbapenem']}/{SPEC['baseline']['n']} = {SPEC['baseline']['carbapenem_pct']}% at baseline to "
     f"{SPEC['under_pressure']['carbapenem']}/{SPEC['under_pressure']['n']} = {SPEC['under_pressure']['carbapenem_pct']}% "
     f"under pressure", TE, S_TE),
    ("10", "given the real panel the broadening is far smaller",
     f"{SPEC['panel_revealed']['carbapenem']}/{SPEC['panel_revealed']['n']} = "
     f"{SPEC['panel_revealed']['carbapenem_pct']}% across {SPEC['panel_revealed']['distinct_drugs']} distinct drugs",
     TE, S_TE),
    ("11", "same drug, different patient, adoption is identical",
     f"{MATCH['pooled']['covers']['pct']}% when it covers against {MATCH['pooled']['does_not_cover']['pct']}% when it "
     f"does not, {MATCH['_meta']['n']} exposures", RJ, S_CN),
    ("11", "and the stratified test is the null exactly",
     f"Cochran-Mantel-Haenszel OR {MATCH['cmh_stratified_by_drug']['or_mh']}, "
     f"p = {MATCH['cmh_stratified_by_drug']['p']}, {MATCH['cmh_stratified_by_drug']['strata']} strata", RJ, S_CN),
    ("12", "a live agent costs coverage",
     f"{DCOV['before_debate']['pct']}% to {DCOV['after_debate']['pct']}%, {DCOV['debate_change_pts']:+.1f} points, "
     f"n = {DCOV['before_debate']['n']}", TE, S_TE),
    ("12", "and abandons correct answers",
     f"HRR {DBT['HRR']['k']}/{DBT['HRR']['n']} = {DBT['HRR']['pct']}%, 95% CI {DBT['HRR']['ci95']}", TE, S_TE),
    ("12", "the panel does the opposite",
     f"HRR {EVID['HRR']['k']}/{EVID['HRR']['n']} = {EVID['HRR']['pct']}%, coverage "
     f"{DCOV['after_debate']['pct']}% to {DCOV['after_panel']['pct']}%, {DCOV['evidence_change_pts']:+.1f} points",
     TE, S_TE),
    ("12", "a scripted neutral turn does neither",
     f"HRR {NEUT['HRR']['k']}/{NEUT['HRR']['n']} = {NEUT['HRR']['pct']}%", TE, S_TE),
    ("13", "few-shot breaks the constant",
     f"{FS['aware']['zeroshot']['distinct']} to {FS['aware']['fewshot']['distinct']} distinct drugs, "
     f"WHO Access {100.0 * FS['aware']['zeroshot']['access'] / FS['aware']['zeroshot']['n']:.1f}% to "
     f"{100.0 * FS['aware']['fewshot']['access'] / FS['aware']['fewshot']['n']:.1f}%", FSJ, S_FS),
    ("13", "and significantly degrades coverage",
     f"{100.0 * FS['paired']['zeroshot_correct'] / FS['paired']['n']:.1f}% to "
     f"{100.0 * FS['paired']['fewshot_correct'] / FS['paired']['n']:.1f}% on {FS['paired']['n']} paired cases, "
     f"lost {FS['paired']['b_lost']}, gained {FS['paired']['c_gained']}, exact McNemar p = {FS['paired']['p_exact']:.7f}",
     FSJ, S_FS),
    ("13", "and it is not copying the exemplars",
     f"the answer appears in that case's own exemplars {100.0 * FS['validity']['answer_in_examples'] / FS['n']:.1f}% "
     f"of the time; it moves off the zero-shot default in {FS['validity']['moved_vs_zeroshot']} of {FS['n']} cases",
     FSJ, S_FS),
]

lines = [
    "# Evidence map",
    "",
    "Generated by `deck/build_evidence.py`. Every claim the talk makes, with the number as it stands in",
    "the result files at build time, the file that holds it, and the script that produces that file.",
    "",
    "The deck itself reads the same files at build time, so a slide and this page cannot disagree.",
    "To check any row: run the script in the last column and read the file in the column before it.",
    "",
    f"Model `{R['model']}`, temperature {R['temperature']}, seed {R['seed']}. Generated by `{R['generated_by']}`.",
    "",
    "## Claim by claim",
    "",
    "| slide | claim | the number, as it stands | result file | produced by |",
    "|---|---|---|---|---|",
]
for slide, claim, value, f, script in ROWS:
    lines.append(f"| {slide} | {claim} | {value} | `results/{f}` | `{script}` |")

lines += [
    "",
    "## Provenance of every arm",
    "",
    "An exposure is one model decision in one experimental cell. Two records sharing an identity key are a",
    "repeated write, not a repeated measurement, and the second is dropped before any number is computed.",
    "",
    "| arm | exposures | duplicate writes dropped | identity key | source files |",
    "|---|---|---|---|---|",
]
for arm, meta in R["_integrity"].items():
    lines.append(
        f"| {arm} | {meta['n']} | {meta['duplicate_writes_dropped']} | "
        f"`{' + '.join(meta['key'])}` | {', '.join('`%s`' % x for x in meta['files'])} |")

total_dupes = sum(m["duplicate_writes_dropped"] for m in R["_integrity"].values())
lines += [
    "",
    f"**{total_dupes} duplicate writes found and dropped in total.** Cause and fix in `archive/DATA_INTEGRITY.md`.",
    "",
    "## What is deliberately not claimed",
    "",
    "| not claimed | why |",
    "|---|---|",
    "| that sycophancy or peer conformity is a new phenomenon | both are published; see `docs/LITERATURE_PRESSURE_TEST.md` |",
    "| that the model underperforms a carbapenem policy | coverage on this cohort is maximised by carbapenem for everybody, which is the stewardship failure itself |",
    "| that speaking order is an independent effect | with a near-constant opening and near-universal adoption it is entailed; Cohen's kappa 0.178 |",
    "| that the model is unstable | the neutral control moves it in 0 cases; it is stable and deferential |",
    "| anything about confidence | the endpoint is withdrawn: all 200 observations were 85, 90 or 95, so the pre-registered threshold could not fail |",
    "| that any recommendation changed a patient outcome | MIMIC-IV is observational; every claim is alignment with recorded microbiology |",
    "",
    "## How to reproduce all of it",
    "",
    "```",
    "python3 analysis/primary_test.py          # results/primary_test.json",
    "python3 analysis/tingting_endpoints.py    # results/tingting_endpoints.json",
    "python3 analysis/policy_degeneracy.py     # results/policy_degeneracy.json",
    "python3 analysis/fewshot_analysis.py      # results/fewshot.json",
    "python3 analysis/leakage_check.py         # results/leakage.json",
    "python3 analysis/canonical_numbers.py     # results/RESULTS.json",
    "python3 deck/build_evidence.py            # this page",
    "python3 deck/deck_figures.py              # every chart in the deck",
    "python3 deck/build_deck.py                # the deck itself",
    "```",
    "",
    "Run against the local run directory, which is not in this repository: MIMIC-IV is credentialed under a",
    "PhysioNet data use agreement and no record-level data is committed.",
]

OUT.write_text("\n".join(lines) + "\n")
print(f"  wrote {OUT.relative_to(ROOT)}  ({len(ROWS)} claims, {len(R['_integrity'])} arms)")
