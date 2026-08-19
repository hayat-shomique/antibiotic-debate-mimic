# Positioning: what is novel here and what is not

Written 18 August 2026. Sources are restricted to the 35 rows of
`/Users/shamzzzh/brain_run/verification_log.csv` whose `verification` column reads VERIFIED,
plus the project record's own bibliography. The three FLAGGED-UNRESOLVED rows (n=107 MIT
Technology Review, n=116 Clinical-RLVR, n=125 "LLM can't jump!") are excluded and must not
reach the bibliography. Where the corpus does not support a claim it is marked
UNSUPPORTED-BY-CORPUS rather than filled in.

[SUPERVISOR-DIRECTED] 13 July 2026, Prof. Tingting Zhu: "this is not by all means, this is
all new, meaning that nobody had done it. Does that makes sense? Because do not say that...
you need to be level with yourself as well." This note is written to that instruction. The
failure mode it guards against is a novelty claim broader than the evidence, so the claim
below is deliberately narrow and the list of things already done by other people is longer
than the list of things that are ours.

One structural honesty point before anything else. This corpus can establish that a
particular prior paper did a particular thing. It cannot establish that no paper anywhere
did a thing, because it is a register of 38 items assembled for this project and not a
systematic search. Every statement of the form "nobody has done X" is therefore
UNSUPPORTED-BY-CORPUS. The defensible form is "none of the 35 verified items does X", and
that is the form used throughout. If the report needs a stronger negative it needs a
documented search protocol, which does not exist.

## What is not novel and must be cited as prior art

Putting an LLM on empiric antibiotic choice and comparing it to clinicians is published.
The project record names "Large Language Model Recommendations for Empiric Antibiotics
Versus Clinician Prescribing", Antibiotics 15(4):368, April 2026, as the closest prior work
on the accuracy component. [OPEN] A grep for that title, for "MDPI" and for "Antibiotics 15"
across `/Users/shamzzzh/brain_run` on 18 August returned no match in `verification_log.csv`,
`references.bib` or `corpus.ris`. The item therefore rests on the project record alone and
has not been checked against a primary source by the register. It must be verified before
the report, and until then it should be cited with that status stated, not silently promoted
to the same footing as the register's VERIFIED rows.

Comparing a model both to the final microbiology and to what the clinician actually
prescribed is also published, and it is the group's own work. Yuan K, Luk A, Wei J, Walker
AS, Zhu T, Eyre DW, Journal of Infection, DOI 10.1016/j.jinf.2024.106388 (row n=2, VERIFIED
against PubMed). The register's correction is load-bearing: the publication date is
2024-12-30 online first, not February 2025, so cite the DOI rather than the issue. The
register scores this row MEDIUM novelty risk with the reason stated plainly, that the paper
"already compares model predictions BOTH to final microbiology and to clinician prescribing".
This project borrows the clinician baseline design and the spectrum taxonomy from it. Both
are attributions, not contributions.

Showing that LLMs abandon correct answers under clinical pressure is published, and the
paper that does it already names the gap this project was framed around. Xiao B et al., "When
Correct Beliefs Collapse: Epistemic Resilience of LLMs under Clinical Pressure", arXiv:2605.23932
(row n=1, VERIFIED via the arXiv API). Two corrections matter. It is accepted at ACL 2026 and
should be cited as such rather than as a preprint, and it proposes two mitigations, RBED at
inference time and R-FT as fine-tuning, which the project record does not record at all. The
register's verdict is direct: "Gap itself is not your novelty; laboratory ground truth and EDI
are." A further caution from the same row is that the four attack sub-types and the five
metric acronyms are not in the abstract, so any mapping of this project's C1 sub-types onto
theirs has to come from the full text before it is asserted.

Multi-turn pressure-induced medical sycophancy already has a benchmark. Joy SS and Farhan N,
"MedPRESS", arXiv:2608.02520, 3 August 2026 (row n=6, VERIFIED; 600 five-turn dialogues,
three scenario families, 20 models, all confirmed by the register). Risk is scored HIGH. The
register states the differentiator as clinician-authority pressure with laboratory ground
truth rather than patient pressure, which is narrower than "we study sycophancy in medicine".

Single-turn injection of misleading medical context at scale is published, by the local
group. Zhou H et al., MedMisBench, arXiv:2606.12291 v2 (row n=8, VERIFIED): 10,932 items,
48,889 misleading context-option pairs, accuracy falling from 71.1% to 38.0%, 51.5% attack
success, authority-framed falsehoods at 69.5%, and a 14-member clinical panel from seven
countries finding serious potential harm in 38.2% of what they reviewed. The register calls
this a mandatory local citation given the Oxford and Clifton authorship, and states the
differentiator as multi-turn versus single-turn while adding that the differentiator "is
narrow". That last word should be kept.

Challenge-induced answer flipping in general is published. Laban P et al., FlipFlop,
arXiv:2311.08596 v2 (row n=7, VERIFIED): 46% flip rate, 17% accuracy drop, and fine-tuning
cutting deterioration by 60% without resolving it. The register names it the closest
precedent for the Cn neutral control, so the control is an application of an existing idea to
a laboratory-arbitrated clinical task, not a new control.

The observation that strong benchmark scores do not survive perturbation is published, and
with a far larger effect than anything this project will report. Pan J et al., Nature Health,
DOI 10.1038/s44360-026-00152-8 (row n=11, VERIFIED): dynamic red-teaming across 15 LLMs,
median MedQA above 80%, and 94% of previously correct answers failing under dynamic
robustness testing. The register calls this "structurally closest published work to the
dual-agent pressure design" and warns that the 94% figure is more dramatic than anything we
will produce. Fragility under pressure is therefore background, not finding.

Randomised evidence on LLM decision support in care already exists. Agweyu A et al., Nature
Medicine, DOI 10.1038/s41591-026-04503-6 (row n=3, VERIFIED). The register's correction is
explicit and must be respected in every version of this text: raw 14-day treatment failure
was 2.2% versus 2.0%, adjusted OR 0.77 (0.55 to 1.08), P=0.13, and the honest phrasing is
"did not demonstrate benefit", not "capability does not transfer".

Multi-agent debate as a method is published, together with a quantitative prediction of when
it fails. Kim Y et al., Nature Machine Intelligence 8:1157-1172, DOI 10.1038/s42256-026-01268-y
(row n=10, VERIFIED, full text read 18 August 2026 per the register): 260 controlled
configurations, and a capability-saturation threshold near 45% single-agent baseline accuracy
that predicts the sign of the multi-agent gain in 94% of 16 validation configurations, with
cross-validated R-squared 0.373. The authors present it as "a practical selection rule rather
than a universal scaling principle" because the baseline-by-team-size interaction does not
survive cluster-robust correction, and that caveat travels with the citation.

Three more rows bound the surrounding territory. Qin Y et al., "Small language models in
medicine", Nature Biomedical Engineering, DOI 10.1038/s41551-026-01734-3 (row n=105,
VERIFIED), is the subject of the 4B choice and the register says a reviewer will expect it
cited when the scale is justified. Xu Z et al., LongMedBench, arXiv:2607.09322 (row n=112,
VERIFIED), is built on MIMIC-IV admission records and clinical notes and is called the
closest methodological neighbour for cohort construction. Luo Z et al., DTR-Bench,
arXiv:2405.18610 (row n=127, VERIFIED, Zhu as senior author), together with Gao S et al.,
ATHENA-R1, arXiv:2606.28692 (row n=110, VERIFIED), covers treatment-selection agents and the
reinforcement-learning comparator, so "an agent that picks a treatment" is not new either.

## The defensible claim, stated narrowly

[DECISION] The claim is this. On an admission-linked Enterobacterales bacteraemia frame drawn
from MIMIC-IV, one open-weight model is asked for an empiric antibiotic and is then subjected
within the same conversation to a challenge carrying no new clinical information and to a
reveal of the patient's actual susceptibility panel, and every answer at every turn is scored
against that patient's own laboratory result by the same instrument that scores the
clinician's recorded order.

Three components carry the weight, and each is narrower than it first looks.

The ground truth is laboratory-derived rather than annotator-assigned. MedPRESS (row n=6)
labels sycophancy by annotation; the project record identifies that as the gap. Scoring a
flip against an S/I/R panel means the arbiter is external to both the model and the
annotator, and it is the same arbiter for the clinician comparator. Of the 35 verified rows,
none scores multi-turn pressure against per-patient culture results. That is the strongest
component of the claim and it should be the sentence that goes on the slide.

The unjustified-pressure and valid-evidence conditions run on the same cases with the same
arbiter, so a single flip rate decomposes into abandoning a correct answer under no evidence
and correcting a wrong answer under real evidence. [LIMITATION] The composite of the two, the
evidence discrimination index, is not the claim. `protocol/protocol_v1.md` line 116 places it
in the appendix, and `protocol/zhikang_reading.md` line 31 gives the reason: a single index
can read as zero for opposite reasons, rigid or pliable, so the three separate indicators come
first and the composite is derived afterwards.

The clinician comparator is scored by the identical rule, stated at `protocol/protocol_v1.md`
lines 70 to 71 as "The identical rule scores the clinician comparator. Any asymmetry
invalidates the comparison." This closes an obvious objection. It does not create novelty,
because Yuan et al. (row n=2) already compares to clinician prescribing.

What is not claimed, in plain terms: not the first LLM evaluation on empiric antibiotics, not
the first comparison against clinicians, not the first demonstration of medical sycophancy or
pressure-induced collapse, not the first use of MIMIC-IV for agent evaluation, not the first
multi-agent clinical debate, and no mitigation is offered, since Med-Stress (row n=1) already
publishes two.

## What supports the claim today

The instrument and the population exist. The frozen cohort is 7,796 with hash
4a4f4f782eb17345e0e9eab1cc596aab9ebf6442890bd1c3b82761ae3c65d414, the sampling frame of
admission-linked Enterobacterales bacteraemia without sustained prior therapy is 993 cases,
and 200 were drawn at seed 20260818. Scoring runs through `score_case` in
`inputs/brain_scoring_local.py` at config fingerprint 04ce311c2b13 with `intermediate_as` set
to separate and `require_all_pathogens_covered` true.

The clinician baseline exists. [FACT] `clinician_comparator_v2_summary.json`, produced by
`_cc2_build_v2.py`, reports 125 of 200 cases ADEQUATE, which is 62.5% of all 200 and 90.6% of
the 138 determined cases, with 11 INADEQUATE, 2 INTERMEDIATE_ONLY and 62 UNDETERMINED.
[LIMITATION] The 31.0% undetermined fraction is large and is not noise: the same file records
178 of 200 cases with a systemic antibacterial order in the window but only 166 mapping to the
closed 17-agent formulary, and the 12-case gap is scored UNDETERMINED under rule R3 rather
than dropped. Any comparison against the clinician has to carry that denominator with it.

The frequency floor exists with the frame named, from `floor_reconciled.csv`. On frame
A_entero_all_cohort_3104, meropenem covers 98.0% of the cohort and 99.6% of tested, and
piperacillin-tazobactam 91.3% and 95.0%. On frame B_primary_frame_993, which is the frame the
200 were actually drawn from, meropenem is 98.0% and 99.5% and piperacillin-tazobactam is
87.8% and 92.0%. The 993-frame numbers are the ones that bound the model.

The debate arm has produced results. [FACT] `indicator2_summary.json`, produced by
`_cc_indicator2.py`, records at a snapshot of 157 debates a round-0 outcome distribution of
139 ADEQUATE, 4 INTERMEDIATE_ONLY, 4 INADEQUATE and 10 UNDETERMINED, so 88.5% adequate at
round 0 with n=157. The same file gives final outcomes of 121 ADEQUATE, 23 INADEQUATE, 7
INTERMEDIATE_ONLY and 6 UNDETERMINED, with 24 cases degraded from ADEQUATE (15.3%), 2 improved
(1.3%) and a net change of minus 18 adequate cases across those 157 debates.

The negative control has run. `indicator2_negative_control_summary.json`, produced by
`_z5_negcontrol.py` over 196 debates on 98 cases, puts 588 turns into the 2x2: 295 changes,
293 holds, 100.0% of changes classified uncritical, 0% reasoned revision, 0% reasoned
resistance among holds, and convergence to the opponent in 196 of 196 debates. [LIMITATION]
The counter-argument detector fires on 4 of 980 turns overall and 0 of the 588 in the 2x2,
with a rule-of-three upper bound of 0.51%, and the only firing entry is the token "but ". A
detector that almost never fires makes "uncritical acceptance" close to definitionally true,
so the 100% figure is as much a statement about the lexicon as about the model and must be
reported that way.

The evidence-leak screen has run but is not finished. `evidence_leak_assessment.md` states
that the automated screen's raw rate of 46 of 975 turns, 4.72%, is a selection device and not
the leakage rate, that the shipped screen fires on 0 of 975, and that the hand classification
in `evidence_leak_assessment_prelim.csv` is a first pass with `human_verdict` still blank.

## What is still required

The primary numbers do not exist yet. Section 5.6 puts them in the scripted-pressure arm, and
that arm has only just started writing. A listing of `/Users/shamzzzh/brain_run/runs` taken at
06:39 on 18 August shows `runs/c1_20260818.jsonl` holding a single record, whose `kind` is
`c1_c0` and whose `condition` is `C0_pre_culture_baseline`, alongside `debate_20260818.jsonl`
at 484 records and four snapshot files. The globs `runs/c0cn_*.jsonl` written by
`control_pass.py` line 80 and `runs/reveal_*.jsonl` written by `reveal_pass.py` line 116 match
nothing at that listing, and `chain_passes.sh` is still waiting on the debate process, which
`run_stageD2.log` shows at case 112 of 192. One C0 record is not a condition, so there is as
yet no unjustified flip rate, no correct-answer collapse rate, no evidence-responsive revision
rate, no retention at C2 and no value for the evidence discrimination index. The index is
implemented, in `brain_scoring_local.py` at `paired_pressure_analysis` around line 482 and
`bootstrap_edi` at line 491, but implemented is not computed. Everything in this note that
rests on the scripted arm is provisional on those files filling.

The C1 sub-types are not reconciled and not implemented. The specification names authority,
peer consensus, safety framing and bare doubt. `protocol/protocol_v1.md` line 79 names a
different four: authority, persistence, logical trap, safety pressure. A grep for "C1a", "peer
consensus", "bare doubt" and "counterbalanc" across `protocol/protocol_v1.md`, `debate_run.py`,
`control_pass.py` and `reveal_pass.py` returned nothing. [OPEN] Which four sub-types are being
run, and whether they are counterbalanced, is unresolved.

C3 does not exist. The same grep found no "C3" and no "fabricat" in `protocol/protocol_v1.md`,
`debate_run.py` or `reveal_pass.py`. This is the condition that would separate this project
most sharply from the prior art, because none of the 35 verified rows tests whether a model
distinguishes evidence that exists in the record from evidence merely asserted, with the
laboratory record available to adjudicate. It is not implemented, so it cannot be claimed. It
belongs in future work, phrased as future work.

Three smaller gaps. The spectrum distribution over under-treated, optimally treated and
over-treated is the taxonomy borrowed from Yuan et al., and while
`runs/_spectrum_snapshot_debate_20260818.jsonl` exists, a listing of the working directory on
18 August shows no summary artefact reporting the three-way split. The hand-confirmed leakage
rate is outstanding. And only one model has been run, which row n=105 says a reviewer will
ask about.

## What the case-invariant round-0 does to all of this

[FACT] `indicator2_summary.json` records `round0_opening_drug_counts` as
`{"piperacillin-tazobactam": 157}` and `round0_is_case_invariant` as true, with the file's own
note reading "A single value means the pre-debate position ignores the case entirely." The
established debate-arm figures agree at a larger snapshot: round-0 is piperacillin-tazobactam
in 224 of 225 ordering-runs and is case-wise identical to a fixed always-piperacillin-tazobactam
policy on 225 of 225 cases.

A recommendation that does not vary with the patient is not conditioned on the patient. That
has three consequences for the positioning, and they pull in different directions.

It removes the accuracy claim. The 88.5% round-0 adequacy at n=157 is not evidence that the
model chooses well. On frame B_primary_frame_993, `floor_reconciled.csv` gives a fixed
piperacillin-tazobactam policy 87.8% of all cases and 92.0% of tested. The model's round-0
figure sits inside that band and is produced by the same mechanism, because the model's
round-0 is that policy. The project therefore cannot report how accurately a small
open-weight model selects empiric therapy on this frame, because on this frame it did not
select. Every accuracy number must appear next to the floor for its named frame, and the
honest reading is that the two are not distinguishable.

It changes what the pressure result means, and arguably strengthens it. If the opening
position is a constant, then every later change is a departure from a default rather than the
abandonment of a case-specific judgement. Med-Stress (row n=1) frames the phenomenon as
correct beliefs collapsing. On this evidence the 4B model had no case-specific belief to
collapse, and saying so is more accurate than importing their framing. The finding to report
is instability of a default under challenge, which is a weaker claim about cognition and a
sharper claim about deployment risk.

It is itself a reportable result, and the corpus supports reporting it. Row n=105, small
language models in medicine, is the natural frame for a negative result at 4B scale. Row n=11
establishes that fragility findings at this magnitude are publishable. Row n=102, Ruhrberg
Estevez S et al., "How to benchmark medical AI agents", PLOS Medicine, DOI
10.1371/journal.pmed.1005170 (VERIFIED), argues that benchmarks should assess clinical
reasoning, process safety and resource stewardship rather than task accuracy, and the gap
between choosing piperacillin-tazobactam and always saying piperacillin-tazobactam is exactly
that argument with a number attached. Row n=10 adds a prediction that fits: at 88.5%
single-agent adequacy the model sits far above the roughly 45% capability-saturation
threshold, so debate is predicted not to improve on the single-agent baseline, and the net
change of minus 18 adequate cases across 157 debates in `indicator2_summary.json` is
consistent with that prediction. The authors' own caveat about a practical selection rule
rather than a universal principle should be quoted alongside it.

Two things follow procedurally. The degenerate-policy comparison has to be a first-class
reported result rather than a footnote, since it is the test that decides whether any accuracy
number means anything, and the per-case identity check at 225 of 225 already exists. And
[OPEN] whether the case-invariance is a property of the model, of the prompt, or of the closed
label set is not established by anything on disk. Attributing it to the model alone requires a
prompt-variation arm that has not been run, so until then the finding should be stated as
case-invariance under this prompt and this label set.

## The one-sentence version

None of the 35 verified items scores multi-turn clinical pressure against the individual
patient's own susceptibility panel, and that is the contribution; the accuracy comparison, the
sycophancy phenomenon, the clinician comparator, the MIMIC-IV cohort and the debate mechanism
are all prior art, and on the current evidence the model's opening answer is a constant, so
what this project can report today is a measurement instrument, a clinician baseline of 125 of
200 adequate from `clinician_comparator_v2_summary.json`, and a negative result about a 4B
model that does not condition on the patient.
