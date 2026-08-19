# Questions for Tingting

Twelve questions, each with the number or quote that raises it and what I will do if there is
no answer. Nothing is blocked on a reply; the defaults are already in place, so an answer
changes a choice rather than unblocking one. Compiled 18 August 2026.

1. Does the pressure and trustworthiness framing interest you, or would you rather this were
a clean accuracy study? I cannot settle this by looking at the data because both readings are
supportable and the choice determines which number leads the report. Default if there is no
answer before 20 August: lead on the pressure result and carry accuracy as context, because
accuracy has almost no headroom on this frame. [FACT] On the 200 sampled cases a fixed
"always meropenem" policy scores ADEQUATE on 192 of 200 (96.0%; 99.0% of the 194 with a
tested denominator), per `floor_reconciled.csv` frame `C_sampled_200`, so a model that beats
that bar has demonstrated very little.

2. Should the closed antibiotic label set be the top N agents by empiric frequency, or
clinically grouped by class, and at what cardinality? This is a specification choice with no
internal criterion to decide it, and it is frozen in `protocol_freeze.json`, so changing it
invalidates the runs already completed. Default: keep the 17-agent formulary as frozen.
[FACT] Five of the 17 have a tested denominator of exactly zero on the primary frame
(vancomycin, penicillin-g, oxacillin, daptomycin, linezolid), and levofloxacin has 14 of 993,
per `floor_reconciled.csv` frame `B_primary_frame_993`, so the effective label set is already
12 agents, or 11 if levofloxacin goes with them. [OPEN] Whether to present the set as 17 with
five degenerate, or to respecify it at 12, is your call.

3. ICU-only or hospital-wide? Your instruction on 29 July 2026 was
[SUPERVISOR-DIRECTED] "You cannot just look at everyone going into ICU", which rules out an
unrestricted ICU population but does not say whether the narrowed population should itself be
ICU-only. Default: stay hospital-wide, which is what the `hosp` module supports.
[FACT] 246 of the 993 frame cases (24.8%) are in an ICU at index time, and 43 of the 200
sampled, computed by `_q_icu_fraction.py` against `icu/icustays.csv.gz`. An ICU-only
restriction therefore cuts the sample from 200 to 43 and would need a fresh draw.

4. Is MIMIC-IV-Note needed, or do the structured tables suffice? I have excluded Note on a
leakage argument, but that argument does not address whether what remains is enough to decide
on an antibiotic, and you are better placed than I am to say whether it is.
Default: structured tables only, with the thinness stated as a limitation.
[FACT] The case block the model sees carries eight fields and none of them is a clinical
finding: age, sex, admission type, admission source, insurance, hours from admission,
prior antibiotic exposure, and a literal "Laboratory results: not available at this decision
point"; prior antibiotic exposure takes one distinct value across all 200 cases because the
frame excludes prior therapy by construction, per `_q_case_block_content.py` over
`_t4c_cases.json`. [HYPOTHESIS] There is no site of infection, no vital sign, no laboratory
value and no Gram stain in the prompt, so the model may have nothing case-specific to
condition on, which would explain question 10 without invoking any property of the model.

5. Is the clinician comparison fair, given that clinician choices are themselves imperfect?
You raised this on 13 July 2026: [SUPERVISOR-DIRECTED] "we're also assuming the doctor makes
the right decision... Obviously, that's a huge assumption you make." I cannot resolve it from
the data because the question is what the clinician number means, not what it is.
Default: report the clinician as a reference point rather than a ceiling, with both
denominators shown. [FACT] Clinicians reach ADEQUATE on 125 of 200 sampled cases (62.5% of
all 200; 90.6% of the 138 with a determined outcome), per
`clinician_comparator_v2_summary.json`, against 192 of 200 (96.0%) for "always meropenem"
from `floor_reconciled.csv` frame `C_sampled_200`. A fixed single agent outscores the
clinicians on this frame under this scoring rule, which is a result about the scoring rule at
least as much as about the clinicians.

6. What is the citation for the group's earlier nurse and specialist reinforcement-learning
paper? You referred to it but did not name it, and I cannot cite an unnamed paper because
`verification_log.csv` admits only rows resolved against a primary source.
Default: cite nothing and drop the lineage claim from the related-work section.
[OPEN] The only reinforcement-learning item in the shared reading on disk is the
Clinical-RLVR link in `teams_chat.txt`, "Open-Ended Clinical Text Generation for Acute Care:
Applying Reinforcement Learning with Clinically Grounded Rewards" from rajpurkarlab, which is
an external group and does not match a nurse and specialist framing.

7. Is the Bio+Clinical BERT antibiotic-indication work from the group the lineage you meant
on 29 July 2026? Your words were [SUPERVISOR-DIRECTED] "maybe it would be interesting to
compare with some medical bert models which previously trained on EHR data already. See how
well they perform without fine-tuning. Smith like Med Bert or ClinicalBert etc.", and I asked
which specific work you had in mind and did not get a reply. Default: report the encoder as
an accuracy baseline only and make no claim about lineage. [FACT] Bio_ClinicalBERT run
zero-shot over the 200 case blocks returns ceftriaxone as its top-1 agent on 200 of 200 cases
(19,000 forward sequences, 419 s), per
`_t4c_pred_emilyalsentzer_Bio_ClinicalBERT.json`, so the encoder is as case-invariant as the
decoder is and the comparison currently contrasts two constants.

8. Do you accept a sampling frame that is 12.7% of the frozen cohort? The restriction is what
makes the external arbiter exist, but it is large enough that the scope of every claim changes
with it, and that is a supervisory judgement rather than a data question.
Default: keep the restriction and state the scope as admission-linked Enterobacterales
bacteraemia without sustained prior therapy, never as bacteraemia. [FACT] The final frame is
993 of the frozen 7,796 (12.7%), and the Enterobacterales organism gate alone retains 3,104
of 7,796 (39.8%), per the gate table in `cohort_justification.md` section 1.
[LIMITATION] The Gram-positive cases are excluded because laboratories build the panel from
the Gram stain, so the agents that would treat them are never tested and no ground truth
exists there.

9. How should the mandated most-frequent-agent floor be reported when it is degenerate on this
frame? You required a baseline, and the baseline as specified returns nothing, so I need a
ruling on whether to substitute or to report the failure. Default under D-FLOOR-1: report the
mandated floor with its degeneracy stated and carry cefepime alongside as the interpretable
one. [FACT] Vancomycin is the most-frequently-ordered formulary agent on the frame, 404 of the
993 cases on the approved 24-hour window, and scores UNDETERMINED on 200 of 200 sampled cases
with a determined denominator of zero, per `clinician_comparator_v2_summary.json`; cefepime
on the same 200 gives 159 ADEQUATE, 81.5% of the 195 tested.

10. Given that the model's first answer does not depend on the case, is the accuracy
comparison meaningful at all? This is the question I most need answered, because it decides
whether the accuracy table belongs in the report or belongs in an appendix as a negative
result. Default: keep the accuracy number but state the fixed-policy equivalence in the same
sentence every time it appears, and let the flip and revision measures carry the report.
[FACT] Round-0 is piperacillin-tazobactam in 224 of 225 ordering-runs and is case-wise
identical to a fixed "always piperacillin-tazobactam" policy on 225 of 225 cases, from the
debate arm. [INFERENCE] An accuracy figure computed on a constant policy measures the
prevalence of susceptibility in the frame, not the model.

11. Should Qwen3-8B rather than 4B carry the experiments, as the project record specifies?
The record puts 4B on pipeline development and 8B on the experiments, but the 8B checkpoint
reintroduces a failure class that stopped the project once already, and whether that is worth
paying is your decision rather than mine. Default: 4B carries the experiments and the size
question goes in the limitations. [FACT] There is no `qwen3:8b-instruct-2507` in the Ollama
library; the 8B tags are `qwen3:8b`, `8b-fp16`, `8b-q4_K_M`, `8b-q8_0`, all of them the hybrid
thinking checkpoint, and the only non-thinking instruct-2507 sizes are 4b, 30b-a3b and
235b-a22b, from `https://ollama.com/library/qwen3/tags` read on 18 August 2026.
[FACT] `model_registry.json` records that the hybrid 4B could not be made non-thinking:
`think:false` moved the reasoning into the content field, `/no_think` moved it to a separate
field, and both still spent 1,000 to 1,588 output tokens per call against the 64 the current
checkpoint spends. Moving to 8B means fighting that again on a 16 GB machine with two days
left.

12. Section 5.6 says the primary numbers come from scripted pressure, but the only pressure
arm that will have run is the agent-generated one, so which do you want to lead? I cannot
choose this myself because it is the difference between the internal-validity claim the
specification makes and the ecological-validity claim the runs support.
Default: lead on the agent-generated arm, label it secondary as specified, and report the
evidence discrimination index as not computed rather than computed with a substituted term.
[FACT] No scripted C1 condition exists in the code: `reveal_pass.py` accepts only
`--mode reveal` and `--mode neutral`, and D-PRESSURE-1 in `deviation_log.csv` froze the four
sub-types to authority only. [FACT] In the arm that did run, Agent A adopts Agent B's standing
drug on 450 of 450 turns and Agent B adopts A's on 224 of 450 (49.8%).

One note on what will exist. At 06:38 on 18 August the debate run is at 112 of 192
case-orderings at 89 s each against an 08:15 deadline, per `run_stageD2.log`, and
`chain_passes.sh` then starts the neutral control with a 07:00 deadline that will already have
passed and the C2 evidence pass with a 09:00 deadline. The C2 revision rate is therefore the
number most at risk, and it is the half of the evidence discrimination index that cannot be
recovered from the debate transcripts.
