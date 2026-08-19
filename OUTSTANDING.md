# Outstanding supervisor asks

Built by sweeping every saved transcript, note file, protocol document and standing-order file
on this machine for anything Prof. Zhu, Zhikang or the frozen protocol asked for, then checking each
one against what is on disk. 147 asks were recovered: 62 done, 29 partial, 40 outstanding, 7
superseded, 9 not actually asks.

This file lists the 69 that are not finished. Each entry quotes the ask, says what it requires, and
records what was checked to decide the status.

Entries concerning personal supervision arrangements are held in the local working copy only and
are not reproduced here.


## Outstanding (39)

### Outs.1  Chen

*23 July 2026, 09:16*

> I recommand you could start from Qwen family, because you could use them freely. And then we can transfer the test process to GPT and other LLM.

**What it requires.** Transfer the test process to GPT and other hosted models, or, per the project's own reconciliation, show it as a sequenced next step on a slide.

**Checked.** deviation_log_proposed.csv row D-TRANSFER-1, status "PROPOSED - deferred, awaiting ruling". Its rationale states the commitment explicitly: "skipping the second half would drop a supervisor instruction ... Belongs on the next-steps slide so it reads as sequenced rather than abandoned." There is no next-steps slide. SLIDE_PLAN.md (19 Aug, the current plan) has a 12-slide spine, `grep -n "^\*\*[0-9]" SLIDE_PLAN.md` gives slides 1-12 ending at "Limitations", plus slide 4b, and `grep -i "transfer|GPT|synthetic" thursday_deck.md SLIDE_PLAN.md` returns exactly one unrelated hit ("the transferable  [...]

**Effort.** 5 minutes. One bullet on a next-steps slide, in his own framing: the harness transfers, the data does not; GPT and other hosted models run on synthetic non-MIMIC cases. The sentence already exists inside D-TRANSFER-1 and only needs lifting onto a slide.

### Outs.2  Chen

*23 July 2026, 09:16*

> evaluate which agent's final recommendation aligns better with actual clinical outcomes (e.g., subsequent resistance)

**What it requires.** Ground the comparison in subsequent resistance, not only the index-culture panel.

**Checked.** protocol/zhikang_aims_coverage.csv row 11 records it as "OUT OF SCOPE TONIGHT, say so" with the action "A next-steps slide with the design named, not a rushed arm". protocol/protocol_v1.md:199-200 repeats it: "Not in the pilot: it requires repeat cultures...". corrected/project_status.md §8 lists "the subsequent-resistance outcome" under "Deferred with reasons recorded". The per-agent half of his ask IS done, SCORECARD.txt endpoint 1 gives Agent A 312/400 and Agent B 312/400 separately, but the resistance grounding is not, and the "say so" instruction has no home: no next-steps slide exists [...]

**Effort.** 5 minutes, no compute. One line on the same next-steps slide as the GPT transfer, naming the design (repeat cultures after the index event, a second index-time definition, a survivorship correction) so he can see it was costed rather than ignored.

### Outs.3  Zhu

*31 July 2026, 1:1 (teams_chat.txt line 120, reported speech)*

> She said to me that, The inventions that really are successful are successful because they thought about the user and they consulted with the users. The user users of that particular thing. So, for example, clinicians, you got to make sure that the clinicians are going to obviously be doing it with their patients, right? So you got to find out what their patient's looking for in their data.

**What it requires.** Consult the intended users, clinicians, about what the tool would need to be, rather than inferring it. As stated it is a general design principle, but she gave it as advice on how to make work land.

**Checked.** I grepped docs/ and all top-level *.md for 'clinician review', 'clinician panel', 'clinician consult', 'clinician input', 'clinician feedback', 'clinician interview', 'consulted a clinician', 'user needs', 'end user', zero hits across the whole repository. The word clinician appears constantly but only in one role: as a retrospective comparator computed from MIMIC prescribing records. results/clinician_comparator_v2_summary.json supplies the number quoted in docs/questions_for_supervisor.md Q5, 'Clinicians reach ADEQUATE on 125 of 200 sampled cases (62.5% of all 200; 90.6% of the 138 with a  [...]

**Effort.** Cannot be closed before tomorrow's conference and should not be attempted. The right move is a single honest limitations line, no clinician was consulted on the interface or on what a stewardship lead would actually want from such a system, plus one bullet in future work. If she raises it in the Q&A, the truthful answer is that the eight-field case block was built from the data available under t [...]

### Outs.4  Zhu

*Undated in export; window 27 Jun, 15 Aug 2026 (teams_chat.txt line 81)*

> Many workshops at neurips, you can submit your work!!!

**What it requires.** A suggestion, not an instruction, but a pointed one, posted alongside four workshop links she shared in the same stretch: WMHS (World Models for High-Stakes Health, NeurIPS 2026 Atlanta, line 78), RCMLR (Responsible Communication of Machine Learning Research in Biomedicine, line 79), GenAI4Health third workshop (line 80), and ASCI (line 81). She also posted AI4GOOD @ NeurIPS 2026 Trustworthy AI for Good with a personal note (line 66: 'neurips conference workshop in paris!!! if u are like me and dont have money and not the best neurips scores, come to paris'). Three of the five are squarely on this project's topic.

**Checked.** No submission plan exists anywhere. I grepped docs/*.md and top-level *.md for 'submit to', 'submission', 'venue', 'target journal', 'workshop deadline', 'abstract deadline'. Every hit is about OTHER papers' venues, docs/do_not_cite.md 'Claimed venue: MIT Technology Review', docs/LITERATURE_PRESSURE_TEST.md line 151 'Venue correction: ICML MAS Workshop 2025, not ICML 2025 main track', docs/EXPLAIN.md 'Venue / year: Journal of Infection (2024)'. The two NeurIPS hits in docs/LITERATURE_PRESSURE_TEST.md are citations of MedAgentBoard (NeurIPS 2025 D&B), not venue targets. Nothing names a worksho [...]

**Effort.** Nothing before tomorrow. But this is the highest-leverage item on the list for what Shomique actually wants, because the same memo records her saying he needs a publication. The work has a computed result, a 62 KB pressure-test of its own claims, and a registered literature corpus, it is closer to a workshop submission than most. Post-conference: check the WMHS and GenAI4Health deadlines, pick on [...]

### Outs.5  Zhu

*Undated in export (teams_chat.txt line 28)*

> GitHub - rajpurkarlab/Clinical-RLVR: Code for "Open-Ended Clinical Text Generation for Acute Care: Applying Reinforcement Learning with Clinically Grounded Rewards" · GitHub https://share.google/fGGn17S1GZcLoYU3G MIMIC LLM Judge

**What it requires.** Separated from the bulk paper-dump because she appended her own two-word tag, 'MIMIC LLM Judge', she was pointing at a specific mechanism, not just forwarding a link. It also became a live question back to her.

**Checked.** docs/verification_log.csv row 116: 'Clinical-RLVR: Open-Ended Clinical Text Generation for Acute Care, (unresolved), FLAGGED-UNRESOLVED, share.google redirect will not expand; no exact match found. DO NOT CITE.' It is correspondingly listed in docs/do_not_cite.md. It then resurfaces as an unanswered question, docs/questions_for_supervisor.md Q6 asks 'What is the citation for the group's earlier nurse and specialist reinforcement-learning paper? You referred to it but did not name it', and records: 'The only reinforcement-learning item in the shared reading on disk is the Clinical-RLVR link in [...]

**Effort.** One question, in person, tomorrow: 'the Clinical-RLVR link you tagged MIMIC LLM Judge, is that the nurse-and-specialist RL paper you meant, or a different one?' The default is already set (cite nothing, drop the lineage claim), so nothing is blocked.

### Outs.6  Zhu

*31 July 2026, 1:1 (teams_chat.txt line 120, reported speech)*

> she said, you need to make sure you have, like, a reference letter now." and earlier: "she said to me, you need publication and you need a reference here. She said to me that she, I need a reference from somebody. She didn't say herself, but she said, I need a reference from somebody that can, uh, give me a stat, like top one% of this, top 5% of this, whatever whatnot.

**What it requires.** A career instruction, outside the repository's scope: secure a referee who can rank him in percentile terms, and produce a publication. Included because it is one of the most consequential things she said all summer and it has no owner.

**Checked.** Nothing in either directory addresses it, and nothing could, this is not a code artefact. I checked docs/questions_for_supervisor.md (twelve questions, all technical, none about a reference) and found no career item anywhere. The same memo records his own conclusion that it is unsolved and that he believes she will decline: 'I thought she was gonna give me a reference letter. She is not gonna give me a reference letter. She doesn't even know who I am.' He also writes off Zhikang: 'Zikang can't also give me a reference because the guy's busy with his own work.'

**Effort.** His pessimism is doing more work here than the evidence supports, and this is worth pushing back on. Since 31 July the position has changed materially: there is now a completed 14-endpoint scorecard against her own specification, a 400-run debate arm, encoder baselines, a second generative model, and a documented literature register. She is seeing the talk on 20 August. A referee needs something t [...]

### Outs.7  Zhu

*29 July 2026, ~17:40*

> What about Medgemma and Deepseek?

**What it requires.** Run the harness on DeepSeek as well as MedGemma, or get a ruling that it is dropped.

**Checked.** Quoted with this date in /Users/shamzzzh/brain_run/corrected/thursday_replan.md §1 cost table ("~8 (EXTRAPOLATED) | DeepSeek debate replication, 200 cases | Tingting: 'What about Medgemma and Deepseek?'"). DeepSeek was never run: `grep -l "deepseek" runs/*.jsonl` returns nothing across all 26 run files. model_pilot_results.md §2 shows deepseek-r1:8b failed 3/3 pilot calls (512-token budget burned on reasoning, zero characters of content). MODELS.md line 54: "DeepSeek-R1-8B, installed and unused." The rejection is recorded in model_digests.json as "REJECTED by D-MODEL-2", but I read D-MODEL-2 [...]

**Effort.** Zero compute. Either (a) 10 minutes: add one honest sentence to MODELS.md and one deviation row saying DeepSeek was declined because every 8B DeepSeek is a reasoning checkpoint and the harness parser rejects it 3/3, with the pilot numbers already in model_pilot_results.md §2; or (b) fix model_digests.json to stop attributing the rejection to D-MODEL-2.

### Outs.8  Zhu

*29 July 2026, ~18:08*

> There is 12B as well for MedGemma, 27B is not necessary.

**What it requires.** MedGemma at 12B. The checkpoint does not exist, so this requires her ruling between 4B, 27B and gemma3:12b, which the project itself committed in writing to obtain.

**Checked.** deviation_log_proposed.csv row D-MODEL-1, status "PROPOSED - awaiting ruling", rationale ends: "The 4B-vs-27B decision changes what the arm measures ... and is Tingting's to make. Recorded here and put to her rather than resolved unilaterally." model_pilot_results.md §6 next-step 1: "Put the MedGemma size question back to Tingting with the fact that 12B does not exist. Do not substitute silently." §1 documents seven independent checks (Ollama tags, HF API by publisher and by search, five fail-fast pulls, Google HAI-DEF card) confirming no 12B exists. The question was then never asked: `grep -i [...]

**Effort.** 15 minutes of writing, no compute. Add one paragraph to summary_for_tingting.md's "What I need your answer on": 12B does not exist (seven checks, cite model_pilot_results.md §1); 4B was run size-matched so the arm isolates domain pretraining; her options are keep 4B, move to the 27B she excluded, or use general-purpose gemma3:12b at the size she named. The MedGemma-4B result is already on disk eit [...]

### Outs.9  Zhu

*13 July 2026*

> up to 10 drugs or whatsoever

**What it requires.** Cut the closed antibiotic label set from 17 agents to about 10.

**Checked.** Quoted as "the direction as recorded" in /Users/shamzzzh/brain_run/label_space_analysis.md:241-242, a file whose title is literally "Label space cardinality: evidence for the 17-to-10 decision". This is the ONLY occurrence of the verbatim string anywhere on either disk (`grep -rn whatsoever` returns one hit), so the primary record is off-disk and I am quoting the project's own transcription. Not implemented: model_registry.json still records "formulary_size": 17 and inputs/brain_scoring_local.py FORMULARY still holds 17 keys. The analysis found six of the 17 labels unscoreable on this populat [...]

**Effort.** Zero compute, the analysis is complete and the change would invalidate completed runs, so this is presentation only. 10 minutes: add her 13 July wording to the summary_for_tingting question so she can see her own direction was received, costed and deliberately deferred rather than missed, and say the 17-set is frozen for the 20 Aug numbers with the 11-agent respecification as the post-conference  [...]

### Outs.10  Zhu

*31 July 2026 (in-person meeting, recorded as a voice memo)*

> She told me of her work that she did on... Basically, survival. Survival probably survival psychophancy or something. Basically. There's a model that has a psychophancy, so then you basically have to get another model to try and like give a probability on how, like, likely is it that it's psychophantic or something. But anyway, she was working on that.

**What it requires.** A second model that estimates a probability that a given output is sycophantic, a judge/verifier layer over the debate transcripts.

**Checked.** This is the ONE project-relevant item in 220KB of meeting/voice transcript in teams_chat.txt (line 120, the 31 July meeting memo). I checked whether anything like it was built: `grep -ri "judge model|LLM judge|llm-as-judge|probability of sycophan|sycophancy score|verifier model"` across all .md and .py on both disks returns two hits, both in LITERATURE_PRESSURE_TEST.md and SYCOPHANCY_CANON.md discussing OTHER papers' judges (SycEval's LLM judge with Beta calibration), never an implementation here. The project deliberately scores externally against S/I/R rather than by any model judgement, whic [...]

**Effort.** Not for tomorrow. But it is worth 30 seconds in the talk or the report: she works on this, and the design's deliberate refusal to use a model judge (because the arbiter must not be a product of the system under measurement, the argument already written in D-GUIDELINE-1) is a direct, informed answer to her own method rather than an omission. Naming it converts a gap into a defended choice.

### Outs.11  Zhu

*13 July 2026 (recorded in D-FEWSHOT-1)*

> supervisor-directed escalation ladder, 13 July 2026: zero-shot, then few-shot with worked examples, and only if both fail consider training

**What it requires.** Climb rung two of her ladder, run the few-shot arm, now that zero-shot has demonstrably failed to condition on the patient.

**Checked.** The instruction is preserved only inside deviation_log_proposed.csv row D-FEWSHOT-1, status "PROPOSED - awaiting ruling; post-freeze escalation arm". Its trigger states the precondition is met: round-0 is piperacillin-tazobactam in 224 of 225 ordering-runs and is verdict-identical to a fixed policy on 225 of 225, so rung one has failed and rung two is the specified response. The arm is fully built with six hard assertions and a pool check (_fs_pool_check.py: 792 of 793 non-evaluation cases eligible) but never ran: `ls runs/ | grep -i fewshot` returns nothing. MASTER_BACKLOG.md A5 does track it [...]

**Effort.** The run itself is cheap (one call per case, same seed, harness built and gated). But if it does not run tonight, the 2-minute version is to fix the attribution: change MASTER_BACKLOG A5's source from "ORDERS_1" to the 13 July supervisor ladder, so that when she asks why there is no few-shot result the answer is "your rung two, built and gated, not yet run" rather than "an item from my own order fi [...]

### Outs.12  Zhu

*undated, she referred to it in conversation and never named it*

> What is the citation for the group's earlier nurse and specialist reinforcement-learning paper? You referred to it but did not name it

**What it requires.** The identity of the group's prior nurse/specialist RL paper, so it can be cited as lineage.

**Checked.** Raised as questions_for_supervisor.md Q6 and again in summary_for_tingting.md's answer list ("Which paper is the group's earlier nurse and specialist reinforcement-learning work? Nothing on disk matches that framing and I will not cite it unnamed"). I checked the corpus: `grep -ri nurse` across all .md/.csv on both disks returns hits ONLY in those two files, no candidate paper anywhere. The only RL item in the shared reading is the Clinical-RLVR link in teams_chat.txt from rajpurkarlab, an external group with no nurse/specialist framing, and verification_log.csv carries it as FLAGGED-UNRESOLV [...]

**Effort.** Zero work, and it should stay unresolved rather than be guessed at. Worth 15 seconds of the Q&A: if she names it, the related-work paragraph gains a lineage sentence; if she does not, verification_log.csv's rule forbids citing it. Keep it on the question list.

### Outs.13  Zhu

*18 Aug 2026 (questions_for_supervisor.md, compiled 06:41)*

> 1. Does the pressure and trustworthiness framing interest you, or would you rather this were a clean accuracy study?

**What it requires.** Her ruling on which number leads the report. Default already in place: lead on the pressure result.

**Checked.** NO REPLY EXISTS ON DISK. teams_chat.txt is headed 'Teams Chat from 27/06 to 15th Aug 2026', it ENDS THREE DAYS BEFORE the questions were compiled. protocol/tingting_endpoint_spec.md is dated 17 Aug, also before. No file anywhere in brain_run postdates 18 Aug 06:41 and contains a supervisor answer. The evidence has however hardened the default: NUMBERS_BLOCK item 1 shows a constant meropenem policy at 192/200 = 96.0% against the model's 87.5%, so accuracy has negative headroom, and SLIDE_PLAN slide 4 is built on that ('So accuracy is the wrong measure. That is the pivot of the talk').

**Effort.** Needs her, and she has not replied. The default is already implemented, so nothing is blocked, SLIDE_PLAN's whole spine pivots off accuracy at slide 4. Ask her in person tomorrow.

### Outs.14  Zhu

*18 Aug 2026*

> 2. Should the closed antibiotic label set be the top N agents by empiric frequency, or clinically grouped by class, and at what cardinality?

**What it requires.** Her ruling on presenting the set as 17-with-five-degenerate or respecifying at 12. Default: keep 17 as frozen.

**Checked.** No reply on disk. The supporting work is done and available: label_space_analysis.md (indexed FINAL, 'What changes at 5/8/10/12/17 drugs'), held as backup material per the ORDERS_1 cut. The observed label space is far narrower than either option: NUMBERS_BLOCK item 6 finds only 3 distinct drugs used across all final positions, round-0 and every turn-level recommendation, 'In practice it is a near-binary cefepime-vs-ceftriaxone choice'.

**Effort.** Needs her. The default is safe: the set is frozen in protocol_freeze.json and changing it would invalidate every completed run, which is the correct answer whatever she prefers. label_space_analysis.md is the backup material if she asks.

### Outs.15  Zhu

*18 Aug 2026*

> 3. ICU-only or hospital-wide? Your instruction on 29 July 2026 was "You cannot just look at everyone going into ICU"

**What it requires.** Her ruling. Default: stay hospital-wide.

**Checked.** No reply on disk. The question's own numbers still stand: 246/993 frame cases (24.8%) in an ICU at index, 43 of the 200 sampled, computed by _q_icu_fraction.py against icu/icustays.csv.gz. Nothing since has changed the frame, cohort_justification.md is still the 993 Enterobacterales frame.

**Effort.** Needs her, but the decision is effectively closed by cost: an ICU-only restriction cuts the sample from 200 to 43 and needs a fresh draw, which is not available before the conference.

### Outs.16  Zhu

*18 Aug 2026*

> 4. Is MIMIC-IV-Note needed, or do the structured tables suffice?

**What it requires.** Her judgement on whether eight non-clinical fields suffice to decide an antibiotic. Default: structured tables only, thinness stated as a limitation.

**Checked.** No reply on disk. The evidence for the question's own hypothesis has STRENGTHENED considerably. prompts_used.md confirms the case block carries exactly eight fields, none of them a clinical finding, ending in the literal 'Laboratory results: not available at this decision point'. Since 18 Aug, three more systems have shown the same case-invariance on that block: MedGemma-4B emits cefazolin on ~98% of cases (a DIFFERENT constant, so the constancy is per-checkpoint, not an artefact of the shared prompt), and every one of the four encoders is near-constant (Bio_ClinicalBERT vancomycin ×200, BioBE [...]

**Effort.** Needs her, but this is the question most worth asking tomorrow, because it is the leading candidate explanation for the whole result and it is a design fix rather than a model finding.

### Outs.17  Zhu

*18 Aug 2026*

> 5. Is the clinician comparison fair, given that clinician choices are themselves imperfect? You raised this on 13 July 2026: "we're also assuming the doctor makes the right decision... Obviously, that's a huge assumption you make."

**What it requires.** Her ruling on what the clinician number means. Default: report the clinician as a reference point, not a ceiling, with both denominators shown.

**Checked.** No reply on disk. The default is in force and the numbers are unchanged: NUMBERS_BLOCK item 1 reports the clinician at 125/200 = 62.5% and 125/138 = 90.6% determined-only, side by side with constant meropenem at 96.0%, with both denominators shown for every arm under two explicit conventions (D1 and D2). The uncomfortable fact the question raises is stated in the numbers block rather than buried: a fixed single agent outscores the clinicians on this frame under this scoring rule.

**Effort.** Needs her. The default is implemented and is the defensible one.

### Outs.18  Zhu

*18 Aug 2026*

> 6. What is the citation for the group's earlier nurse and specialist reinforcement-learning paper? You referred to it but did not name it

**What it requires.** A citable reference, or the lineage claim drops. Default: cite nothing and drop it.

**Checked.** No reply on disk. The default is enforced by machinery rather than by memory: verification_log.csv admits only rows resolved against a primary source (38 rows, 35 VERIFIED, 3 FLAGGED-UNRESOLVED, two states only per PROJECT_INDEX), and do_not_cite.md carries three prohibited items with 'No third state'. The only RL item in the shared reading is still the Clinical-RLVR link in teams_chat.txt from an external group (rajpurkarlab), which does not match a nurse-and-specialist framing.

**Effort.** One question to her, 30 seconds of her time. Until answered, verification_log.csv's two-state rule forbids the citation, so the default holds automatically and nothing is at risk.

### Outs.19  Zhu

*18 Aug 2026*

> 8. Do you accept a sampling frame that is 12.7% of the frozen cohort?

**What it requires.** Her acceptance of the restriction, since it changes the scope of every claim. Default: keep it and scope every claim as admission-linked Enterobacterales bacteraemia.

**Checked.** No reply on disk. The default is in force and instrumented: F1 is built to the claim 'The analysed frame is 12.7% of the frozen cohort, and every gate down to it is logged', and per FIGURES_MANIFEST its script re-derives every gate count live and asserts equality with the file (7,796 / 3,107 / 1,087 / 993 / 200), raising if any gate has no logged reason. cohort_justification.md carries every restriction with its deviation and measured trigger. SLIDE_PLAN slide 12 states 'The frame is Enterobacterales' as a stated limitation.

**Effort.** Needs her. The default is implemented and F1 makes the restriction visible rather than hiding it, so the exposure is low.

### Outs.20  Zhu

*18 Aug 2026*

> 11. Should Qwen3-8B rather than 4B carry the experiments, as the project record specifies?

**What it requires.** Her decision on paying the thinking-suppression cost for 8B. Default: 4B carries the experiments, size goes in limitations.

**Checked.** No reply on disk. The default is in force and the reasoning is now reinforced by a logged deviation: model_digests.json records deepseek-r1:8b as 'REJECTED by D-MODEL-2, reasoning model, reintroduces think tags', and qwen3:4b (hybrid) as 'SUPERSEDED, hybrid checkpoint, thinking could not be suppressed'. The incumbent qwen3:4b-instruct-2507-q4_K_M carries every arm. SLIDE_PLAN slide 12 states 'A 4B model is not a frontier model' as a limitation, which is the default's second half.

**Effort.** Needs her, but the decision is closed in practice: there is no non-thinking instruct-2507 checkpoint at 8B, and re-fighting thinking suppression on a 16 GB machine the day before the conference is not available. The default is the only feasible answer.

### Outs.21  Zhu

*2026-07-29 17:29 to 17:38 (Teams, [VERBATIM]), logged as E3 "OPEN LOOP" in the ledger and still open in HANDOVER_2026-08-13.md §7.4*

> Why do you need to access the machine? I thought you are doing promting / I think you need to download open LLMs and run API for testing them / I think doing prompting doesn't need intense resources? You can access to IBME cluster as well, can you run mimic data on cluster?

**What it requires.** A definite yes/no back to her on whether the GPU asset 33112 ticket is needed, with a memory-footprint number and whether the desktop or the IBME cluster covers it. He told her he would confirm "tomorrow morning" (30 Jul); the ledger records no confirmation was ever sent.

**Checked.** Grepped both trees for gpu / cluster / 33112. The only hit is /Users/shamzzzh/Desktop/antibiotic-debate-mimic/docs/EXPLAIN.md row 16, which mentions "16 GB with no GPU" in passing as the secondary reason for omitting vital signs. No compute justification, no footprint figure, no message to Zhu, no ticket status anywhere in the repo, brain_run, or the source folder. LAB_NOTEBOOK 2026-07-24 records IT confirming the Dell Precision 3650 is CPU-only, which is the answer, it was just never given to her.

**Effort.** Two sentences, and the answer is now free because the project settled it empirically: everything ran on a 16 GB CPU-only machine at ~15 s/case, so the GPU ticket was not needed and should be withdrawn. Worth closing explicitly rather than letting a raised ticket sit unanswered after she twice questioned it, she asked a direct question three weeks ago and has had no reply.

### Outs.22  Zhu

*2026-07-13 (first supervisor meeting, [RECON]), logged as C2 in the ledger, V10 in Claims-To-Verify, A10 in the Action-Register*

> I want to replace those 2 RL models [with] 2 LLMs.

**What it requires.** The citation for the group's earlier nurse/specialist reinforcement-learning paper, which she referenced but never named. He cannot position against a lineage he cannot read.

**Checked.** Never obtained. docs/questions_for_supervisor.md Q6 is exactly this ask, still unanswered: "You referred to it but did not name it, and I cannot cite an unnamed paper because verification_log.csv admits only rows resolved against a primary source." His default is recorded as "cite nothing and drop the lineage claim from the related-work section". Grep of docs/references.bib finds Luo et al. 2024 (luo2024, Zhiyao Luo … Tingting Zhu) but the source folder's LAB_NOTEBOOK 2026-07-23 already records that the AI4SG-2023 nurse/specialist paper "could NOT be located" and that DTR-Bench 2405.18610 is a [...]

**Effort.** One line to her or Zhikang: "which paper is the nurse/specialist RL work you mentioned on 13 July?" It has been open for five weeks across three separate files. If no answer arrives before the report, his default (drop the lineage claim) is correct and should be stated as a deliberate omission rather than left as a silent gap, a related-work section that gestures at an unnamed in-group paper is w [...]

### Outs.23  Zhu

*2026-07-29 18:34, he asked; the ledger records "She did not answer. Ask again."*

> [Such] like Med Bert or ClinicalBert etc.

**What it requires.** Confirmation of whether the group's own Bio+Clinical BERT antibiotic-indication work is the lineage she meant by the encoder-baseline suggestion.

**Checked.** Still unanswered. docs/questions_for_supervisor.md Q7 re-asks it verbatim and records "I asked which specific work you had in mind and did not get a reply", with the default "report the encoder as an accuracy baseline only and make no claim about lineage". The encoder work itself is complete (see the Med-BERT ask above), so nothing is blocked, only the positioning is.

**Effort.** One line, ideally bundled with the nurse/specialist citation ask. The baseline stands on its own without it; the only cost of never getting an answer is that a related-work paragraph stays thinner than it could be.

### Outs.24  Zhu

*2026-07-13 (first supervisor meeting, [RECON]), C2 third lineage item, V11 in Claims-To-Verify*

> [a] deep prescribing project [with Zhikang that] was getting really good result already

**What it requires.** The citation or detail for the group's deep-prescribing project, to build on or deliberately differentiate from.

**Checked.** No trace anywhere. Grepped both trees for "deep prescrib", zero hits in /Users/shamzzzh/Desktop/antibiotic-debate-mimic and /Users/shamzzzh/brain_run. It appears in the source folder only, as an unresolved item in the ledger (C2), Claims-To-Verify (V11), and Action-Register (A10). It was also on his own 22 Jul question list to Zhikang (accountability/research_log/archive/sent/2026-07-22_zhikang_update.md, Q4) and never came back.

**Effort.** One line to Zhikang, who is the named collaborator on it. Lowest-value of the three lineage questions, nothing in the current design depends on it. Ask it once, and if nothing comes, say nothing about it in the report.

### Outs.25  Zhu

*2026-07-22 11:20 (Teams, [VERBATIM]); she then added him to the group meetings herself on 30/07 12:34*

> You have been missing our group meetings, it would be very useful for you to attend to get a feel about research since you are interested in PhDs

**What it requires.** Attend the lab group meetings.

**Checked.** /Users/shamzzzh/brain_run/summary_for_tingting.md opens: "The summary I owed you after missing the 11:00 group meeting and the 12:00 supervision." So the 18 August group meeting was missed as well, the same failure she raised on 22 July, repeated on the single most important day of the internship. The source folder itself records the precedent (2026-07-30_OXF_Package-Audit §1 quotes her Teams message of 14/07 10:14: "Hi Shomique, are you at the IBME? We have started the meeting.") and DAILY_RHYTHM.md names oversleeping past a Zhu meeting as "the single most expensive failure of this internshi [...]

**Effort.** Nothing to build. This is the one item on the list that is purely about conduct, and it is the one most likely to damage the reference the whole project exists to earn. The mitigation is already drafted, summary_for_tingting.md is a genuinely strong document, but I found no evidence in either tree that it was actually sent. Confirm it went to her, and if it did not, send it before the conference [...]

### Outs.26  Zhu

*ledger E6, ~2026-08-20; confirmed in email_evidence/EVIDENCE_DIGEST.md from the 19 Jun corrected UNIQ+ timetable*

> UNIQ+ programme presentation | You | ~20 August 2026, separate from E5. She was unsure of the date; confirm with the programme team.

**What it requires.** A 10-minute talk plus 5 minutes Q&A to a general audience, Cohen Quad, Exeter College, on 20 August, a different talk from the lab one: less method, more why-it-matters.

**Checked.** Date is confirmed and distinct (email_evidence/EVIDENCE_DIGEST.md; INDEX.md resolves the 19th-vs-20th contradiction, he is MPLS, so the 20th). A separate general-audience deck exists: /Users/shamzzzh/brain_run/conference_deck.html, 18,091 bytes, written 19 Aug 19:37, deliberately smaller than the 455 KB lab deck. The event itself is tomorrow.

**Effort.** The deck is built; what is not verifiable from disk is whether it has been rehearsed against a 10-minute clock. The turnaround finding and the laboratory-as-referee idea both work for a lay audience; the fixed-policy result needs one plain sentence, not the SDT apparatus. Three arms are still writing to disk (C1, plausible-wrong, drug-matched), so any number quoted from them tomorrow must be quote [...]

### Outs.27  Zhu

*Undated in export; window 27 Jun, 15 Aug 2026 (teams_chat.txt line 84)*

> Everyone FYI, I have removed Dr Yu Liu from our chat due to a recent incident. […] I would ask you be caution to share information with people from now on. Please read the terms and conditions (if any) regarding your position at Oxford. As an example, a visitor is not an employee of Oxford and cannot use the affiliation without permission. Postdocs are hired for a funded project; any work or activities outside the fu [...]

**What it requires.** Three obligations: (a) no Oxford affiliation on any output without her permission; (b) do not share lab information onward; (c) acknowledge the post. The only unambiguous instruction in the export.

**Checked.** UPGRADED from the claimed PARTIAL. The first reader found half of it. (a) protocol/protocol_v1.md:135 under '## 8. Governance, not negotiable' reads '- No Oxford affiliation on any output without Prof Zhu's permission.' README.md:8-9 carries 'UNIQ+ research internship, University of Oxford, Institute of Biomedical Engineering'. git remote -v = https://github.com/hayat-shomique/antibiotic-debate-mimic.git; git status -sb reports '## master...origin/master' with no ahead marker at be63097 (the first reader saw c9b9523; the repo has since moved on and is still pushed). git log --reverse shows th [...]

**Effort.** ~20 minutes of work, but do it before the talk, not after. (1) Set the GitHub repo private, or delete the remote, one click. (2) Strip README.md:8-9 to name and dates only. (3) Remove protocol/tingting_endpoint_spec.md, protocol/zhikang_reading.md and protocol/zhikang_requirements_map.csv from the tree, redact the [SUPERVISOR-DIRECTED] blocks in docs/questions_for_supervisor.md and docs/positioni [...]

### Outs.28  Zhu

*31 July 2026, 1:1 (teams_chat.txt line 120, reported speech)*

> She said to me that, The inventions that really are successful are successful because they thought about the user and they consulted with the users. The user users of that particular thing. So, for example, clinicians, you got to make sure that the clinicians are going to obviously be doing it with their patients, right? So you got to find out what their patient's looking for in their data.

**What it requires.** Consult the intended users, clinicians, about what the tool would need to be, rather than inferring it. Stated as a general design principle, given as advice on how to make work land.

**Checked.** Confirmed OUTSTANDING, and worse than claimed. I re-ran the search across BOTH directories, the first reader appears to have searched only the repo. Grep for 'clinician (review|panel|consult|input|feedback|interview)', 'consulted a/with clinician|doctor|pharmacist|user', 'user need', 'end user', 'user-centred', 'user-centered', 'showed it to a' returns ZERO hits in the repo excluding .git, and ZERO hits across brain_run *.md. The word clinician appears constantly but only as the retrospective MIMIC comparator: results/clinician_comparator_v2_summary.json feeds docs/questions_for_supervisor.md [...]

**Effort.** Two halves, different clocks. The honesty half is 5 minutes tonight: one line under LIMITATIONS.md '## Clinical' saying no practising clinician has reviewed the personas, the formulary or the adequacy rule, and that the design decisions attributed to clinical reasoning in METHODS.md come from the supervisor rather than from a treating clinician. Say it on the limitations slide too, specialists re [...]

### Outs.29  Zhu

*Undated in export; window 27 Jun, 15 Aug 2026 (teams_chat.txt line 81)*

> Many workshops at neurips, you can submit your work!!!

**What it requires.** A suggestion, not an instruction, but a pointed one, posted alongside four workshop links in the same stretch: WMHS (World Models for High-Stakes Health, NeurIPS 2026 Atlanta, line 78), RCMLR (Responsible Communication of Machine Learning Research in Biomedicine, line 79), GenAI4Health third workshop (line 80) and ASCI (line 81), plus AI4GOOD @ NeurIPS Paris at line 66. Three of the five are squarely on this project's topic.

**Checked.** Confirmed OUTSTANDING, checked harder. NeurIPS appears in exactly four places across BOTH directories and every one is a citation of someone else's paper: brain_run/SYCOPHANCY_CANON.md:398 (Turpin et al., NeurIPS 2023, arXiv:2305.04388v2) and :1001 (the matching BibTeX booktitle), and LITERATURE_PRESSURE_TEST.md:18 and :161 (MedAgentBoard, NeurIPS 2025 D&B). grep -rli neurips over *.md in brain_run returns those two files and nothing else. In the repo, grep for neurips|workshop|submit|submission|venue|deadline returns only other papers' venues (docs/do_not_cite.md 'Claimed venue: MIT Technolog [...]

**Effort.** 15 minutes for the version that matters before tomorrow: a closing 'where this goes' slide naming ONE workshop. RCMLR (Responsible Communication of Machine Learning Research in Biomedicine, teams_chat line 79) is the sharpest fit, because the contribution as stated in docs/LITERATURE_PRESSURE_TEST.md:55 is a measurement-validity and communication result, 'the contribution is measurement validity, [...]

### Outs.30  Zhu

*31 July 2026, 1:1 (teams_chat.txt line 120, reported speech)*

> she said, you need to make sure you have, like, a reference letter now." and earlier: "she said to me, you need publication and you need a reference here. She said to me that she, I need a reference from somebody. She didn't say herself, but she said, I need a reference from somebody that can, uh, give me a stat, like top one% of this, top 5% of this, whatever whatnot.

**What it requires.** A career instruction outside the repository's scope: secure a referee who can rank him in percentile terms, and produce a publication. One of the most consequential things she said all summer, and it has no owner.

**Checked.** Confirmed OUTSTANDING, with one correction. The first reader wrote that nothing in either directory addresses it. /Users/shamzzzh/brain_run/HANDOFF_PROMPT.md:10 does: 'Presentation to the lab group 18 Aug; MPLS/UNIQ+ conference 20 Aug; written report early September. The supervisor's reference is the primary DPhil asset.' So it IS registered, but only as a statement of stakes explaining why the work matters, with no action, no plan and no owner attached. Everything else confirms the gap. I read docs/questions_for_supervisor.md in full: twelve questions, all technical (framing, label set, ICU  [...]

**Effort.** 5 minutes to prepare, and the window is tomorrow, after the talk, in person, while the work is fresh and she has just watched him present it. Nothing on disk can close this and no code artefact will. Two asks, both one sentence. (i) The reference: 'Would you be willing to write a reference for DPhil applications in October, and if you would rather see the September report first, may I send it an [...]

### Outs.31  standing orders and protocol

*18 August 2026, 03:05*

> ### STEP 5, the message to Zhikang\nStill unwritten. Three points: his debate design ran at 200 cases with his personas, indicators and role alternation; the single-model stability arm is your addition and is proposed, not agreed; GPT transfer happens via harness on synthetic cases only. Your prose, not anyone else's.

**What it requires.** Send Zhikang a message covering those three points.

**Checked.** This is a commitment written into a status update, /Users/shamzzzh/brain_run/corrected/verification_and_next_steps.md §7 STEP 5, and it was never converted into a task. The same commitment is repeated in three other places, which is why I am confident it is real and not a stray line: corrected/project_status.md §9 ("The debate arm is Zhikang's design; the single-model stability arm is yours. He has not yet agreed to the reordering, put it to him as a proposal, not as settled."); audit_report.md §4 ("the single-model arm is an addition that must be put to him as a proposal, not presented as  [...]

**Effort.** 20 minutes of the researcher's own prose. All three points are already evidenced: the debate arm ran 400/400 at 6.7x his specified 30-case demonstration; the single-model arms are labelled as the researcher's addition throughout; the GPT/DUA reconciliation text exists verbatim inside D-TRANSFER-1.

### Outs.32  standing orders and protocol

*19 August 2026 (ORDERS_1, standing order)*

> CUTS, said now: confidence elicitation = next-steps slide (post-freeze arm, her wording quoted)

**What it requires.** A next-steps slide carrying the confidence arm with Zhu's own wording quoted.

**Checked.** The order is in /Users/shamzzzh/brain_run/protocol/ORDERS_1.md, which its own header calls a standing order to be "re-read at the start of every phase". Her wording exists and is authoritative: protocol/tingting_endpoint_spec.md, "Record confidence before and after communication if the design permits. The particularly concerning state: correct + confident -> sees other agent -> wrong + confident." The arm ran and produced a real number (SCORECARD.txt endpoint 12: 27/200 = 13.5% correct+confident to wrong+confident, flagged NULL because only 85/90/95 are ever emitted). But there is no next-ste [...]

**Effort.** 10 minutes, no compute. One next-steps slide holding three items already evidenced: her confidence endpoint quoted verbatim plus the 27/200 figure and why the threshold is inert; the GPT-transfer sequencing (ask #5); subsequent resistance (ask #6). That single slide closes three separate deferred commitments at once.

### Outs.33  standing orders and protocol

*18 August 2026*

> One further stale artefact, flagged not renamed. `clinician_comparator_drugmap_audit.csv` (timestamped 18 Aug 03:52) was produced on the **pre-draw** window and is stale for the same reason, but it was not part of the approved D-CLINWIN-1 rename so it has been left untouched. Its post-draw replacement is `clinician_comparator_v2_drugmap_audit.csv`. Use the v2 file.

**What it requires.** Do not read the stale pre-draw drugmap audit into any slide, table or figure; use the v2 file.

**Checked.** This is the item the brief predicted, a live instruction sitting inside a file whose own name says SUPERSEDED: /Users/shamzzzh/brain_run/clinician_comparator_SUPERSEDED_README.md, final section. Nothing else on either disk carries this warning. Both files are still present and the trap is live: `ls -la` confirms clinician_comparator_drugmap_audit.csv (2,950 bytes, 18 Aug 03:52, pre-draw, stale) sits beside clinician_comparator_v2_drugmap_audit.csv (1,867 bytes, 18 Aug 05:22, post-draw, current), and the stale one sorts FIRST alphabetically and is the one a glob or a tab-complete lands on. The [...]

**Effort.** 2 minutes, and it is pure downside protection before a deadline. Either add the filename to a do-not-read list in the numbers block, or note it in FIGURES_MANIFEST.md. Do not delete it, the README states nothing was deleted and both superseded files remain auditable, which is the correct governance posture.

### Outs.34  standing orders and protocol

*19 Aug 2026*

> Two more prompts follow this one ("ORDERS 1" = the EOD track plan, "ORDERS 2" = the supervisor spec addendum). Save each verbatim as protocol/ORDERS_1.md and protocol/ORDERS_2.md when they arrive, and RE-READ BOTH at the start of every phase

**What it requires.** protocol/ORDERS_1.md AND protocol/ORDERS_2.md, both saved verbatim.

**Checked.** `ls -la /Users/shamzzzh/brain_run/protocol/` returns exactly 7 files: ORDERS_0.md, ORDERS_1.md, protocol_v1.md, tingting_endpoint_spec.md and the three zhikang files. No ORDERS_2.md. Same in the mirror at /Users/shamzzzh/Desktop/antibiotic-debate-mimic/protocol/. `grep -rl ORDERS_2` finds it referenced in PROJECT_INDEX.md:13 (PENDING), RESURRECT.md:12-15, COMPLETION_AUDIT.md I13, VERIFY_FINDINGS.md V-001, INSTRUCTION_LEDGER.md rows 27-29 and FIGURES_MANIFEST.md, six documents depend on a file that was never written. ORDERS_1 was saved.

**Effort.** Two minutes if the ORDERS_2 text is still in the source thread: paste it to protocol/ORDERS_2.md. If tingting_endpoint_spec.md IS the ORDERS_2 payload, its own header says 'Saved verbatim per ORDERS_2', then one line in each of tingting_endpoint_spec.md, RESURRECT.md and PROJECT_INDEX.md saying so, and clear F8's status. Cannot be done from disk: the text is not on this machine.

### Outs.35  standing orders and protocol

*19 Aug 2026*

> c. Gemma3-4B round-0 (the base-family control).

**What it requires.** 200 round-0 calls with gemma3:4b. Without it, MedGemma's difference cannot be separated from its Gemma3 base, the comparison's whole interpretability rests on this arm.

**Checked.** Read-only python over both runs/model_compare_*.jsonl: only qwen3 and medgemma appear. gemma3 has ZERO records. `grep -rln gemma3` across brain_run *.jsonl/*.json/*.csv/*.md/*.log hits only model_pilot_results, model_digests.json, MODELS.md, model_pilot_results.json and COMPLETION_AUDIT, never a run file. model_digests.json has the digest a2af6cc3eb7f and role 'BASE-FAMILY CONTROL, MedGemma is built on Gemma3, so this isolates domain', verified_present true. INSTRUCTION_LEDGER row 42 marks it DONE, but that row tracks THE PULL, not the run. COMPLETION_AUDIT I7 documents this exact gap and re [...]

**Effort.** The model is pulled and verified present. Two changes: add the tag to DEFAULT_MODELS at model_compare.py:115, run round-0 on the same 200. At MedGemma's observed throughput that is roughly 1-1.5 h of unattended compute, but it competes with the calibration and drug-matched runs currently holding the machine. If it is not run, it needs a logged deviation naming the two-model design, because D-MODEL [...]

### Outs.36  standing orders and protocol

*19 Aug 2026*

> d. Gemma3-12B round-0 if time (scale test).

**What it requires.** 200 round-0 calls with gemma3:12b, explicitly conditional on time.

**Checked.** model_digests.json still records gemma3:12b-it-q4_K_M with digest null, verified_present false, status PULLING, although COMPLETION_AUDIT I7 records `cat chain_pulls.log` showing both gemma3 pulls succeeded and `ollama list` showing gemma3:12b-it-q4_K_M f4031aab637d. Zero records in any model_compare file. Separately: MASTER_BACKLOG A1 and NUMBERS_BLOCK:248 both still track `gemma4:12b`, which model_digests.json marks 'NOT IN THE SET, different family generation, kept but unused'. That is a roster inconsistency in supervisor-facing documents.

**Effort.** Conditional by its own wording, and the condition has expired: the conference is tomorrow and 3c has priority over 3d. The cheap close is to fill the digest from `ollama list` and mark the arm not run. ~5 min.

### Outs.37  standing orders and protocol

*Frozen 18 Aug 2026 03:37 (stamp in the 19 Aug addendum)*

> **Primary test:** exact binomial (McNemar) on cases that change recommendation under exactly one of Cn and C1. Report b, c, and d, not only percentages.

**What it requires.** The PRE-SPECIFIED PRIMARY TEST of the frozen protocol: a paired McNemar of Cn against C1 on the same cases, with the b, c and d cell counts printed.

**Checked.** `grep -rni mcnemar` across brain_run *.py/*.md/*.json returns McNemar for: the degraded-control bare-vs-reasoned pair (b=0, c=26, p=2.980e-08, NUMBERS_BLOCK item 9); within-C1 sub-type pairs (c1_analysis.py `def mcnemar(k1,k2)` loops only over the four SUB keys); fewshot_analyze.py:304 for an arm that has never run; and literature citations. NO Cn-vs-C1 test anywhere. MIGRATION_PLAN.md:614 states it plainly: 'The pre-specified primary test (McNemar, Cn vs C1) has no data'. That was written at 18:34 when it was true for lack of C1 data; C1 has since produced 312 exposures over 78 cases, so the  [...]

**Effort.** ~30 min of read-only analysis, no model calls. Both arms are on disk and share case_ids: runs/c0cn_20260818.jsonl (200 cases, 0 moved) and runs/c1_20260819.jsonl (78 cases and climbing). Restrict to the C1 case set, cross-tabulate moved-under-Cn against moved-under-C1, print b, c, d. Cn's 0/200 makes b = 0 by construction, so the test is one-directional and the p-value will be tiny, but the proto [...]

### Outs.38  standing orders and protocol

*Frozen 18 Aug 2026*

> A sample of challenger turns is hand-classified for evidence leakage and the **leakage rate is reported** as a validity check. "Evidence-free" is a measured property, not an assumed one.

**What it requires.** A HUMAN-classified leakage rate over a sample of challenger turns. The protocol's own wording makes this the thing that licenses calling the challenge evidence-free.

**Checked.** evidence_leak_handcheck.csv: read-only python counts 46 rows and 0 non-blank human_verdict values. evidence_leak_assessment.md:17 confirms the file was extracted with 'human_verdict and human_note blank as specified'; :169-170 says both that file and the companion prelim CSV leave those columns 'blank and ... for a human to fill'. :6-10 states the rule in bold: 'The reported leakage rate must be the hand-classified one. The automated screen is a [pre-filter] ... and must not be quoted as one.' MIGRATION_PLAN.md:614 lists it among what is NOT done: 'human adjudication of the leak sample is 0/46 [...]

**Effort.** 46 rows to read and mark. The extract, the columns and an agent's preliminary verdicts already exist, so this is adjudication, not analysis, perhaps 45-60 min. It cannot be delegated to a model: evidence_leak_assessment.md quotes the frozen module's own docstring saying the automated screen is a pre-filter and 'the leakage rate you report is the hand-classified one'.

### Outs.39  standing orders and protocol

*UNIQ+ programme; CLAUDE.md §3 and REFERENCE.md §D; deadline recorded in HANDOVER_2026-08-13.md §1 as Fri 4 Sept*

> End-of-project report due → uniqplus@admin.ox.ac.uk | Canvas template

**What it requires.** The written end-of-project report, on the programme's template, by ~4 September.

**Checked.** No report draft in either tree, `find` for *report*/*draft* returns only preflight_report.md, audit_report.md and two .py utilities. No .tex or .docx manuscript skeleton anywhere, which HANDOVER_2026-08-13.md §5 also recorded as missing on 13 August.

**Effort.** Not yet due, and the runway is real (Oxford access runs to 11 Sept). The components are unusually far along, METHODS.md, RESULTS.md, LIMITATIONS.md, cohort_justification.md, FINDING.md, HEADLINE_RESULT.md and the F1, F8 figure set with a manifest. This is an assembly job against the Canvas template, not a writing-from-scratch job, and it should start the day after the conference while the runs are [...]


## Partial (29)

### Part.1  Chen

*23 July 2026*

> the prescriptions table, which captures real physician orders from clinical practice, including drug names, doses, routes, and timing

**What it requires.** Use the prescriptions table as the physician-order comparator, his enumeration includes doses and routes.

**Checked.** /Users/shamzzzh/brain_run/z11_prescriptions_provenance.md is a dedicated note on exactly this, and it is candid: "the compliance is partial and the gap should be visible to him rather than discovered later." Two of his four named fields are used. §3: "Dose is not used anywhere", a grep across all .py under brain_run returns 0 hits for dose_val_rx, dose_unit_rx, prod_strength, form_rx, form_val_disp, form_unit_disp, doses_per_24_hrs. Route is carried into intermediate extracts and used as a filter in one diagnostic scan (_cc2_recon.py:18) but "enters no scored comparator and no reported figure [...]

**Effort.** Zero, it is a deliberate, well-argued scope limit and should NOT be closed by doing work. 2 minutes: add one line to LIMITATIONS.md so the scope note is visible outside z11_prescriptions_provenance.md, since z11 itself says the point is that Zhikang can see which part is met.

### Part.2  Chen

*Undated in the source; the map is dated 18 Aug 2026 03:52, and indicator3_aware.json attributes the request to 'Zhikang Chen, 23 July 2026'*

> how far its final recommendation deviates from evidence-based guidelines

**What it requires.** Indicator 3. protocol_v1 §7 pins the implementation: 'guideline-deviation rate (against `guideline_flags.csv`, from a named published source)'. The requirements map flags it MISSING with the reason: 'this is a different yardstick, not a synonym ... A drug can be guideline-concordant AND resistant, or off-guideline AND active, that dissociation is a finding, not noise.'

**Checked.** `guideline_flags.csv`, THE FILE protocol_v1 §7 NAMES, DOES NOT EXIST. `find` across brain_run and the repo returns only guideline_flags_FILLSHEET.csv, guideline_flags_TEMPLATE.csv and guideline_flags_validator.py. I read both CSVs: every one of the 17 drug rows has in_empiric_guideline and source_citation BLANK. The FILLSHEET header pins the definition and states 'Researcher-supplied only (D-GUIDELINE-1). Never model-generated.' MASTER_BACKLOG D7 is BLOCKED, 'awaiting your filled sheet'; PROJECT_INDEX.md marks the template BLOCKED, 'BLOCKS indicator 3'. WHAT WAS DELIVERED INSTEAD: indicator3 [...]

**Effort.** BLOCKED ON THE RESEARCHER, NOT ON COMPUTE, AND D-GUIDELINE-1 FORBIDS FILLING IT ANY OTHER WAY. 17 rows, each needing Y/N plus a resolvable DOI/PMID/ISBN/URL. Perhaps 45-90 min with a guideline document open. If it will not be filled before the conference, the honest move is to say on the slide that indicator 3 was answered with WHO AWaRe as a substitute yardstick, that the substitute returns 400/4 [...]

### Part.3  Chen

*Map dated 18 Aug 2026 03:52*

> After each round, record both agents' position shifts and the types of evidence they cite.

**What it requires.** Per-round position shifts (turn-of-first-change) AND per-turn citation-type labels. Logged PARTIAL in zhikang_requirements_map.csv and GAP/MISSING in zhikang_aims_coverage.csv rows 6 and 7.

**Checked.** BUILT AND COMPUTED, BUT ON MID-RUN SNAPSHOTS. brain_scoring_local.py:593 implements turn_of_first_change; indicator2_summary.json:410-418 carries it with median_first_change_round_among_movers = 3.0; indicator2_turn_of_first_change.csv, indicator3_evidence_types_v2.csv and indicator3_turns_annotated.csv all exist. PROJECT_INDEX.md:64-65 marks the indicator CSVs FINAL. COMPLETION_AUDIT I2 shows the coverage: the CSVs hold 785 turns over 79 case_ids and 975 turns over 98 case_ids, matching runs/_snapshot_indicator2_debate_20260818.jsonl (157 full over 79 cases) and runs/_z7_snapshot_debate_20260 [...]

**Effort.** Re-run _cc_indicator2.py and evidence_labeller_v2.py against the complete 400-run debate file, read-only over existing logs, no model calls, ~20-30 min. Alternative: demote both PROJECT_INDEX rows from FINAL to INTERIM and state 79/200 and 98/200 in the row. These two CSVs are the collaborator-facing deliverable; shipping them at 40-49% coverage labelled FINAL is the exposure.

### Part.4  Zhikang

*2026-07-30 08:59 (salvaged, HANDOVER_2026-08-13.md §6.1)*

> If you want to ground this in MIMIC data, you can feed real de-identified case summaries (including microbiology cultures and susceptibility results) as the discussion input

**What it requires.** Real MIMIC case summaries, including cultures and susceptibilities, as debate input.

**Checked.** Deliberately reframed rather than followed, and the reframing is documented. Real de-identified MIMIC case summaries are the debate input (src/case_assembly.py), but the panel is withheld at round 0 and revealed only as an experimental condition, the C2 reveal arm, 400/400 runs (runs/canonical_reveal.jsonl) plus a clean-context reveal at 200/200. protocol/zhikang_requirements_map.csv records the deviation as "DIVERGENT, but reconcilable" with the instruction to say it out loud: "you did not ignore it, you turned it into an experimental arm." Feeding the panel in as baseline input would have d [...]

**Effort.** No work outstanding, this is a communication item. Say the sentence to Zhikang explicitly rather than letting the divergence look like an oversight. The reveal arm is a stronger design than his suggestion and it produced endpoint 5 (escalation/de-escalation correctness: 82.6% repaired, 99.7% held), which is one of the better results in the project.

### Part.5  Zhikang

*2026-07-23 (Teams reply, LAB_NOTEBOOK 2026-07-23 entry)*

> I recommand you could start from Qwen family, because you could use them freely. And then we can transfer the test process to GPT and other LLM.

**What it requires.** Qwen first; later transfer the test process to GPT and other models.

**Checked.** Qwen first: DONE, qwen3:4b-instruct-2507-q4_K_M, digest 0edcdef34593, temperature 0, seed 20260818, carries every arm (protocol/model_digests.json, docs/MODELS.md). GPT transfer: NOT DONE, and correctly so. protocol/zhikang_requirements_map.csv flags it: "his sequencing assumes hosted models later, which your DUA forbids for MIMIC content. Worth raising with him early, not on the day." The harness is model-agnostic and swaps checkpoints (crossmodel_pass.py, model_compare.py), so the capability exists; the data-governance boundary is what stops it.

**Effort.** Raise the DUA constraint with Zhikang rather than leaving the second half of his instruction silently unexecuted, he may not know MIMIC content cannot go to a consumer API under the agreement. Note the source folder itself corrects an earlier overstatement here (LAB_NOTEBOOK 2026-07-22): PhysioNet's Sep-2025 guidance does permit compliant cloud pathways (Azure OpenAI with opt-out, Bedrock, Vertex [...]

### Part.6  Zhikang

*2026-07-22 (from his Teams history, LAB_NOTEBOOK 2026-07-22 entry: "Owes Zhikang a doc by end of day today")*

> we could use documents to interact

**What it requires.** A shared written document he can mark up asynchronously, as the working channel between them.

**Checked.** Documents that answer his brief exist and are structured for exactly this, protocol/zhikang_requirements_map.csv (11 rows, his words against the current design, each with a verdict and an action) and protocol/zhikang_aims_coverage.csv (13 asks, each costed in hours). accountability/research_log/archive/sent/2026-07-22_zhikang_update.md is the drafted doc from that day. But nothing in either tree evidences that any of these were shared with him, and no collaborative or commented artefact exists.

**Effort.** The hard part is already written. Sending zhikang_requirements_map.csv to him would close a commitment open since 22 July and would show him his own brief taken seriously line by line, including the two places where the design deliberately diverges from it, which is better said by him than discovered by Zhikang.

### Part.7  Zhikang

*2026-07-30 08:59 (salvaged brief; itemised as row 10 and row 11 of protocol/zhikang_aims_coverage.csv)*

> evaluate which agent's final recommendation aligns better with actual clinical outcomes (e.g., subsequent resistance)

**What it requires.** Per-agent scoring of the final recommendation, and grounding in downstream outcomes such as subsequent resistance.

**Checked.** Per-agent scoring: DONE, SCORECARD.txt endpoint 1 reports Agent A 312/400 = 78.0% and Agent B 312/400 = 78.0% separately, which was flagged MISSING in zhikang_aims_coverage.csv row 10 and is now closed. Subsequent resistance: NOT BUILT, results/secondary_endpoints.json carries persistent bacteraemia 13/200 = 6.5% as the nearest available proxy and states plainly why it is not "failure": attribution would require crediting a therapy the agent never gave. zhikang_aims_coverage.csv row 11 had already ruled this OUT OF SCOPE with reasons (needs repeat cultures after the index event, a second ind [...]

**Effort.** Correctly deferred, do not attempt it now. The instruction from his own coverage table is the right one: a next-steps slide naming the design, rather than a rushed arm. The reason it is out of scope is itself a good methodological answer to give if asked.

### Part.8  Zhu

*Undated in export; window 27 Jun, 15 Aug 2026 (teams_chat.txt line 84)*

> Everyone FYI, I have removed Dr Yu Liu from our chat due to a recent incident. […] I would ask you be caution to share information with people from now on. Please read the terms and conditions (if any) regarding your position at Oxford. As an example, a visitor is not an employee of Oxford and cannot use the affiliation without permission. Postdocs are hired for a funded project; any work or activities outside the fu [...]

**What it requires.** An instruction, and the only unambiguous one in the whole export. Three separate obligations: (a) do not put the Oxford affiliation on any output without her permission; (b) do not share lab information onward; (c) acknowledge the post. This is the governance item the task brief asked me to watch for.

**Checked.** The rule is encoded in the project's own protocol. /Users/shamzzzh/Desktop/antibiotic-debate-mimic/protocol/protocol_v1.md line 135, under a section headed '## 8. Governance, not negotiable', reads: '- No Oxford affiliation on any output without Prof Zhu's permission.' So the instruction was received and written down. BUT: README.md line 8 reads '**Shomique Hayat** · UNIQ+ research internship, University of Oxford, Institute of Biomedical Engineering · supervised by **Prof. Tingting Zhu** · 6 July, 20 August 2026'. That is the Oxford affiliation on an output. `git remote -v` shows origin = ht [...]

**Effort.** Two minutes to ask her, before the 20 August talk, whether the Oxford affiliation on a public GitHub README is authorised, and log the answer next to protocol_v1.md line 135. If the answer is no, the fix is a one-line README edit. Note the honest caveat: her post scopes the restriction to visitors and postdocs, and a UNIQ+ intern is arguably neither, but the project wrote itself a stricter rule a [...]

### Part.9  Zhu

*31 July 2026, 1:1 (teams_chat.txt line 120, reported speech)*

> Now, she gave these key terms to me that she said she's really, like, passionate about, which is antibiotics, sepsis, um, and obviously, like, verification, psychophancy, and stuff is what she was working on as well.

**What it requires.** Not an instruction, a statement of her interests, which functions as a steer on topic selection. Four terms: antibiotics, sepsis, verification, sycophancy.

**Checked.** Antibiotics: the entire project. Sycophancy: docs/SYCOPHANCY_CANON.md is 85,320 bytes; SCORECARD.txt reports HRR 52/350 = 14.9% and BCR 13/24 = 54.2% as computed endpoints. Verification: docs/verification_log.csv is a 38-row citation register with a two-state rule and docs/do_not_cite.md for failures, that is verification of the literature, which is not the sense she meant (see the next row on her sycophancy-probability model). Sepsis is the weak leg: the cohort is bloodstream infection defined by a positive blood culture with an interpretable susceptibility panel, not by any sepsis criterion [...]

**Effort.** Low, and worth doing for the talk rather than the code: one sentence in the deck saying explicitly that the cohort is culture-confirmed bacteraemia and not a sepsis cohort, so that the difference is stated by you rather than raised by her. No re-run needed.

### Part.10  Zhu

*31 July 2026, 1:1 (teams_chat.txt line 120, reported speech)*

> But the biggest obstacle in healthcare yet is cost. The tech might be amazing. She said to me that she was creating this 4D ECG scan. But then the 4D ECG scan was like mathematically and technologically an amazing invention that she was working on. But then it was her startup, but then she had to stop it and end it because the doctors basically said, it's too expensive. One, two, it's not worth it. and 3 value. It do [...]

**What it requires.** A worked example from her own failed startup, offered as a lesson: whatever is built has to survive a cost-benefit test. Advice rather than an instruction on this project, but she spent real time on it.

**Checked.** Compute cost is measured; deployment cost-benefit is not. results/throughput_measured.csv records seconds_per_ordering_run_mean 59.95, seconds_per_case_both_orderings 119.9, model_calls_per_ordering_run 5 and generation_tok_per_s_single_call 24.6, real measurements taken at 2026-08-18T03:36. The compute-matched single-agent self-consistency arm exists precisely as a cost control, and docs/PAPERS_INTEGRATION.md quotes Kim et al. on 'matched per-system compute ceilings' as the recognised fairness control. The repo also registers the cost-aware literature: docs/verification_log.csv row 113 carri [...]

**Effort.** Half a slide, and it is nearly free because the numbers already exist. The debate arm costs 5 model calls and ~120 seconds per case to deliver a 9.5-point LOSS in susceptibility concordance against a single agent. That is a cost-benefit statement of exactly the shape she described, computed from throughput_measured.csv and SCORECARD.txt item 2, and it makes her own point for her. Recommend adding  [...]

### Part.11  Zhu

*Undated in export (teams_chat.txt line 101; she quoted the passage at length)*

> Tingting Zhu https://www.nature.com/articles/s41573-026-01496-2 "Artificial intelligence (AI) in drug discovery has attracted increasing interest over the past decade. It is now time for a critical review of progress in the field: where did we advance, and where are we yet to see impact, when it comes to what matters in drug discovery, which is to deliver safer and more efficacious medicines to patients faster? Alt [...]

**What it requires.** She did not just link this one, she pasted the paragraph. Separated out because Shomique then built his talk's opening on it, teams_chat.txt line 114: 'a paper was released and this is going to be the paper that was sent from Munib and Ting Ting, showing the drug discovery review saying that medical AI superintelligence is not showing any improvements… We're going to use that paper and cite that and say, this is what Stanford is thinking here. However, we at Oxford have a different idea'. So this is a Zhu-sourced item with a Shomique commitment attached.

**Checked.** Registered but not used where he said he would use it. docs/verification_log.csv row 109 has it VERIFIED with all 16 authors from Crossref, annotated 'This is the review Munib quoted', and it is in docs/references.bib. But grepping docs/EXPLAIN.md, docs/positioning.md and docs/HEADLINE.md for '01496', 'drug discovery' or 'Bender' returns nothing, it is not in the framing documents. And it is not in the talk: I grepped all five decks in /Users/shamzzzh/brain_run (thursday_deck.md, SLIDE_PLAN.md, deck.html, journey_deck.html, conference_deck.html) for 'drug discovery', 'superintelligence', 'rob [...]

**Effort.** Ten minutes if he still wants it, and I would push for it: it is a citation-backed opening, it credits a paper his supervisor personally pasted into the channel, and the pivot he scripted ('this is what Stanford is thinking… however, we at Oxford have a different idea') is a clean setup for a null result. The verified reference is already in references.bib, so only the slide is missing. If he has  [...]

### Part.12  Zhu

*29 July 2026*

> maybe it would be interesting to compare with some medical bert models which previously trained on EHR data already. See how well they perform without fine-tuning. Smith like Med Bert or ClinicalBert etc.

**What it requires.** Encoders that were PRETRAINED ON EHR DATA, scored zero-shot.

**Checked.** Four encoders were run 200/200 (MODELS.md table; encoder_baseline.md), which satisfies "without fine-tuning" and satisfies "ClinicalBert" via emilyalsentzer/Bio_ClinicalBERT. But only ONE of the four meets her stated criterion of prior EHR training. dmis-lab/biobert and microsoft/BiomedNLP-BiomedBERT are pretrained on PubMed abstracts/full text, and google-bert/bert-base-uncased is a general control. The headline number the deck leads with, BiomedBERT 169/200 = 84.5%, SLIDE_PLAN.md slide 4b, called "the strongest single slide in the deck", comes from a model that was NOT trained on EHR data, [...]

**Effort.** 20 minutes, no compute, and it makes the slide stronger rather than weaker. Add one column to the MODELS.md and slide-4b encoder tables labelling each checkpoint's pretraining corpus (EHR notes / PubMed / general), and say out loud that the only EHR-pretrained encoder is the one that scores 0.0%, that IS the finding she asked for, and it currently reads as an accident. Add one line noting Med-BER [...]

### Part.13  Zhu

*17 Aug 2026*

> LOS / ICU-free days as confounded secondaries.

**What it requires.** Length of stay AND ICU-free days.

**Checked.** secondary_endpoints.json los: n_linked 185, median_los_days 11.9, n_with_icu 99. completion_state.json item 8 DONE reads 'median LOS 11.9 d (185 linked); 99 with an ICU stay, median ICU LOS 5.0 d'. That is ICU length of stay, NOT ICU-free days, they are different quantities and hers names the latter. grep for 'icu_free'/'ICU-free' across brain_run *.py *.json *.csv *.md returned nothing outside the endpoint spec itself.

**Effort.** ICU-free days is one derivation from icustays (28 or 30 minus ICU LOS, deaths coded 0). ~20 min against existing joins; 99 cases already linked. Or state in one line that ICU-free days was not computed and why.

### Part.14  Zhu

*18 Aug 2026*

> 7. Is the Bio+Clinical BERT antibiotic-indication work from the group the lineage you meant on 29 July 2026? Your words were "maybe it would be interesting to compare with some medical bert models which previously trained on EHR data already. See how well they perform without fine-tuning."

**What it requires.** Her confirmation of the lineage. Default: report the encoder as an accuracy baseline only, no lineage claim.

**Checked.** No reply on disk, so the LINEAGE question is unanswered. But the INSTRUCTION she gave has been executed well beyond what the question describes, and the question's own premise is now outdated. It says Bio_ClinicalBERT 'is as case-invariant as the decoder is and the comparison currently contrasts two constants'. Since then encoder_baseline.csv covers four encoders and SLIDE_PLAN slide 4b reports BiomedBERT at 169/200 = 84.5%, not the 0.0% of Bio_ClinicalBERT, against Qwen3-4B zero-shot 87.5% and post-debate 77.0%. So the comparison is now informative, and the slide plan calls it 'the supervis [...]

**Effort.** The lineage half still needs her, ask tomorrow. The instruction half is done and is now the strongest slide in the deck.

### Part.15  Zhu

*18 Aug 2026*

> 10. Given that the model's first answer does not depend on the case, is the accuracy comparison meaningful at all? This is the question I most need answered

**What it requires.** Her ruling on whether the accuracy table belongs in the report or in an appendix as a negative result. Default: keep the number but state the fixed-policy equivalence in the same sentence every time.

**Checked.** No reply on disk, so the ruling is unanswered, but the evidence has moved decisively and the default is already the spine of the talk. The question cited round-0 pip-tazo on 224/225 ordering-runs; NUMBERS_BLOCK item 1 now confirms 200/200 cases (399/400 ordering-runs) with outcome counts IDENTICAL count-for-count to a constant pip-tazo policy (175/12/5/8 on both, aggregate identity check printed True). It goes further than the question anticipated: the model does not merely tie a constant, it LOSES to one, 8.5 points below constant meropenem. SLIDE_PLAN slides 3 and 4 build the talk on exact [...]

**Effort.** The presentational default is implemented; only her formal ruling for the REPORT (due ~4 Sep) is open. Ask tomorrow, it is the highest-value 60 seconds of the conversation.

### Part.16  Zhu

*2026-07-13 (first supervisor meeting, [ASR-CLEAR])*

> make sure that you 1st start with... zero shot will not work, we can [take] something ready made and say like, look, this is already trained... And then... I'm going to use some example of how it look like. If you have this sort of observation or this patient, this are the drug you prescribe as an example. And then so you give it, like, a few shots and then see whether it improves. And it doesn't, then you can move i [...]

**What it requires.** Run the ladder in order: zero-shot, then few-shot, then (only on failure) small-model training. The few-shot rung is a required step, not an optional extra.

**Checked.** Zero-shot rung: DONE, round-0 is a persona-conditioned zero-shot call with no debate framing (docs/prompts_used.md, separate sys_A_round0/sys_B_round0 strings), 400 ordering-runs in runs/debate_20260818.jsonl. Few-shot rung: NOT RUN. /Users/shamzzzh/brain_run/fewshot_pass.py (39,310 bytes) and fewshot_analyze.py (18,646 bytes) exist, both dated 18 Aug 07:37, and arms/fewshot_pass.py is committed to the repo, but `find` over both trees returns no runs/fewshot*.jsonl and no few-shot result file of any kind. /Users/shamzzzh/brain_run/chain_fewshot.log is 0 bytes; chain_fewshot.sh blocks on `whi [...]

**Effort.** The harness is written and the gate is a wait-loop, so it is compute time, not build time: the two arms it waits on need ~50 and ~55 minutes at their logged 15.5 s/case, then few-shot runs. The real risk is that it silently never starts before the 20 Aug talk, worth checking chain_fewshot.log has content before presenting the ladder as complete, and saying "few-shot is running / not yet run" rath [...]

### Part.17  Zhu

*2026-07-29, 17:36 to 18:10 (Teams, [VERBATIM])*

> What about Medgemma and Deepseek?

**What it requires.** Add MedGemma and DeepSeek to the model comparison.

**Checked.** MedGemma DONE: medgemma:4b-it-q4_K_M, digest 9fe4e9a6c9bd verified before use (protocol/model_digests.json), run fresh on the same 200 cases in runs/model_compare_20260819.jsonl. DeepSeek NOT RUN: docs/MODELS.md §"What was dropped, and why" states plainly that DeepSeek-R1-8B is "installed and unused", with the reason given, her stated interest was its visible chain of thought, which is an interpretability question, and at 8B it cannot join the size-matched 4B contrast without confounding domain tuning with scale. deepseek-llm:7b is also on disk and in no analysis.

**Effort.** The decision is defensible and already written down, so this is a communication task, not a compute one: say out loud on the 20th that DeepSeek was installed and deliberately not used, and give the size-matching reason. Left unsaid it reads as an ignored supervisor suggestion; said, it reads as a controlled comparison. If she wants it, it is a reading exercise over the CoT of a handful of cases, n [...]

### Part.18  Zhu

*2026-07-13 (first supervisor meeting, [ASR-CLEAR]), the ledger calls this "a must-do design decision"*

> we need to narrow down to like maybe up to 10 drugs or whatsoever. It's not necessary to say, like, we just give whatever in the world, because that sounds like a very hard problem, because if you want to compare the accuracy of the LM, you need to actually treat it as by, you know, like classification problems.

**What it requires.** A closed antibiotic label set of roughly ten agents, derived from the cohort, so accuracy is scorable as classification.

**Checked.** A closed formulary exists and is frozen, 17 agents, listed verbatim in docs/prompts_used.md and pinned in protocol/protocol_freeze.json, with OTHER and ABSTAIN as escapes. That is 17, not ~10. He has measured the gap himself: docs/questions_for_supervisor.md Q2 records that five of the 17 (vancomycin, penicillin-g, oxacillin, daptomycin, linezolid) have a tested denominator of exactly zero on the primary frame and levofloxacin has 14/993, so the effective set is 12, or 11. brain_run/label_space_analysis.md and _ls_step4_proposed.py show restricting the clinician's regimen to the ten scoreable [...]

**Effort.** The analysis is already done; what is missing is her ruling, and Q2 is written and waiting. Do not re-cut the formulary, it is frozen and re-cutting invalidates every completed run. Present it as "17 as frozen, of which 12 are scoreable, and here is why five are structurally untestable" (the laboratory builds the panel from the Gram stain, so Gram-positive agents are never tested against an Enter [...]

### Part.19  Zhu

*2026-07-29 18:34, he flagged it and said he would request the separate DUA; ledger E4 records "Unconfirmed", HANDOVER_2026-08-13.md §7.3 records "no evidence it happened"*

> [C3, ledger] MIMIC-IV-Note access. You flagged on 29/07 18:34 that notes are a separate DUA and you would request it. No confirmation in the chat that you did. If your case representation needs free text, this is a blocker; if structured tables suffice, it is not. Decide and state which.

**What it requires.** Either request the MIMIC-IV-Note DUA as he told her he would, or state to her that structured tables suffice and why.

**Checked.** The decision is made and written, but it was made unilaterally and has not been put to her. docs/questions_for_supervisor.md Q4 states "I have excluded Note on a leakage argument" and sets the default as "structured tables only, with the thinness stated as a limitation". No evidence anywhere of a Note DUA being requested. Critically, the same Q4 documents how thin the remaining representation is: the case block carries eight fields, none of them a clinical finding, age, sex, admission type, admission source, insurance, hours from admission, prior antibiotic exposure, and a literal "Laboratory [...]

**Effort.** This is the single most consequential open item in the audit, and it is not really about the DUA. If the prompt contains no site of infection, no vital sign, no laboratory value and no Gram stain, then the headline finding (round-0 is piperacillin-tazobactam on 224/225 runs) may be a property of the input, not of the model. Q4 is written and needs her answer, but he should not wait for it to prese [...]

### Part.20  Zhu

*2026-07-30 12:34 (Teams, [VERBATIM]); confirmed twice, also in the 13 Jul transcript*

> FYI - you are presenting your work on 18 AUG

**What it requires.** Present the work to Zhu and the lab group on 18 August.

**Checked.** The material exists and is strong: /Users/shamzzzh/brain_run/deck.html (455 KB, rebuilt 19 Aug 21:32), SLIDE_PLAN.md, the eight-figure set F1, F8 with a style contract, and summary_for_tingting.md written for the day. But the 12:00 supervision on 18 August was missed, per that file's own opening line, so the presentation as scheduled did not happen. The source folder's PRESENTATION_2026-08-18_BRIEF.md is now two days stale and describes a project state (no model ever run) that the disk contradicts.

**Effort.** Treat the 20 August conference talk as carrying both jobs, and make sure Zhu has the written summary in hand regardless. The deck is in far better shape than the source folder's brief implies, the 13/17 Aug documents describe a design-and-instrumentation talk with n=6 admissions, and what is actually on disk is 400 ordering-runs on a 993-case frame with nine arms and a red-teamed fix list. Do not [...]

### Part.21  Zhu

*2026-07-13 (first supervisor meeting; Action-Register A11)*

> keep a live research notebook; synthesise each relevant paper; record prompts, datasets, decisions, failures, and results; draft report material while the work is fresh

**What it requires.** A running notebook of decisions, prompts, data versions, failures and results, and report prose written as the work happens, not afterwards.

**Checked.** Notebook side is exemplary and exceeds the ask: docs/deviation_log.csv (9 rows, each with as_specified / as_implemented / reason / effect / decided_by / ISO timestamp), docs/verification_log.csv (38 citation rows), docs/prompts_used.md (verbatim, hash-pinned in model_registry.json), protocol/protocol_freeze.json, CHANGELOG.md, FIXES.md (19 findings, all closed), plus the source folder's own LAB_NOTEBOOK.md. Report side is missing: `find` over both trees for *report* / *draft* returns only preflight_report.md, audit_report.md and two .py files. There is no end-of-project report draft.

**Effort.** The raw material for the report is unusually complete, METHODS.md, RESULTS.md, LIMITATIONS.md, cohort_justification.md and FINDING.md already exist and between them cover most of a paper. What is missing is the assembly into the UNIQ+ report template. Deadline is ~4 Sep with Oxford access to 11 Sep, so the runway is real, but note that HANDOVER_2026-08-13.md §1 also records a "Wed 19 Aug, draft  [...]

### Part.22  Zhu

*31 July 2026, 1:1 (teams_chat.txt line 120, reported speech)*

> Now, she gave these key terms to me that she said she's really, like, passionate about, which is antibiotics, sepsis, um, and obviously, like, verification, psychophancy, and stuff is what she was working on as well.

**What it requires.** Not an instruction, a statement of her interests functioning as a steer on topic selection. Four terms: antibiotics, sepsis, verification, sycophancy.

**Checked.** Confirmed PARTIAL, with one correction to the first reader. Antibiotics: the whole project. Sycophancy: docs/SYCOPHANCY_CANON.md is 85,320 bytes; SCORECARD.txt items 10 and 5 print HRR 52/350 = 14.9% and BCR 13/24 = 54.2% with the partition closing 350+24+26 = 400. Verification: docs/verification_log.csv is a 38-row register (35 VERIFIED, 3 FLAGGED-UNRESOLVED) with docs/do_not_cite.md as the failure list, literature verification, not the model-verification sense. CORRECTION: the first reader wrote that no sepsis engagement exists. METHODS.md:22-23 addresses it head-on, 'Bacteraemia is not se [...]

**Effort.** Do not try to close the sepsis leg before tomorrow. A Sepsis-3 subgroup needs SOFA components pulled from chartevents and labevents for all 200 cases and re-scored, a day of work minimum, and it would fracture an already-small n. The 30-second close is rhetorical and already written: say METHODS.md:22-23 out loud when someone asks why this is bacteraemia and not sepsis. That converts the weakest  [...]

### Part.23  Zhu

*31 July 2026, 1:1 (teams_chat.txt line 120, reported speech)*

> But the biggest obstacle in healthcare yet is cost. The tech might be amazing. She said to me that she was creating this 4D ECG scan. But then the 4D ECG scan was like mathematically and technologically an amazing invention that she was working on. But then it was her startup, but then she had to stop it and end it because the doctors basically said, it's too expensive. One, two, it's not worth it. and 3 value. It do [...]

**What it requires.** A worked example from her own failed startup, offered as a lesson: whatever is built has to survive a cost-benefit test. Advice rather than a project instruction, but she spent real time on it.

**Checked.** Confirmed PARTIAL. Compute cost is measured and the cost-aware literature is registered; deployment cost-benefit does not exist. results/throughput_measured.csv exists (578 bytes, written 19 Aug 21:05) and docs/EXPLAIN.md row 14 carries the measurements in full, 59.95 s per ordering run, SD 10.69, range 50.4 to 82.2 over 8 measured runs, 5 model calls each, 119.9 s per case for both orderings, 141.29 s as the conservative planning figure. The compute-matched single-agent self-consistency arm exists as a cost control (SCORECARD.txt: self-consistency 200/200 COMPLETE) and docs/PAPERS_INTEGRATIO [...]

**Effort.** 10 minutes, and it is one of the strongest slides available because every number is already on disk and no run is needed. The arithmetic: a debate costs 119.9 s per case (5 model calls) against roughly 24 s for a single call, so five times the compute, and it returns MINUS 9.5 points of susceptibility concordance (87.5% before, 78.0% after, SCORECARD.txt item 2). Meanwhile a constant 'always mero [...]

### Part.24  Zhu

*Undated in export (teams_chat.txt line 101; she quoted the passage at length)*

> Tingting Zhu https://www.nature.com/articles/s41573-026-01496-2 "Artificial intelligence (AI) in drug discovery has attracted increasing interest over the past decade. It is now time for a critical review of progress in the field: where did we advance, and where are we yet to see impact, when it comes to what matters in drug discovery, which is to deliver safer and more efficacious medicines to patients faster? Alt [...]

**What it requires.** She did not just link it, she pasted the paragraph. Shomique then built his talk's opening on it, teams_chat.txt line 114: 'a paper was released and this is going to be the paper that was sent from Munib and Ting Ting, showing the drug discovery review saying that medical AI superintelligence is not showing any improvements… We're going to use that paper and cite that and say, this is what Stanford is thinking here. However, we at Oxford have a different idea'. A Zhu-sourced item with a Shomique commitment attached.

**Checked.** Confirmed PARTIAL, with one correction and one caveat that changes what closing it means. Registered and verified: docs/verification_log.csv row 109 is VERIFIED with all 16 authors from Crossref, annotated 'This is the review Munib quoted'; docs/references.bib:173-178 carries it as bender2026, DOI 10.1038/s41573-026-01496-2, Nature Reviews Drug Discovery; docs/LITERATURE.md:145 records it with her quote attributed to her. Absent from every framing document and every deck: I grepped eight files, not the first reader's five, thursday_deck.md, SLIDE_PLAN.md, deck.html, journey_deck.html, confere [...]

**Effort.** 10 minutes when the deck is built, and both citations are ready to paste from references.bib. Use the superintelligence test (s41591-026-04539-8) for the benchmark-critique line, it is the closer fit to his own 'gap between benchmarks and safety' framing, and the drug-discovery review (s41573-026-01496-2) for the clinical-impact line, which is the one she personally quoted, so cite it in her hea [...]

### Part.25  standing orders and protocol

*19 Aug 2026*

> Write PROJECT_INDEX.md at the repo root: every artefact in this project ... one line each: path, what it is, status (final/draft/running), and which claim or slide it supports. ... This is the single door into the project; keep it current for the rest of the day. Also generate index.html

**What it requires.** An index and a browsable HTML mirror, kept CURRENT.

**Checked.** PROJECT_INDEX.md and index.html both exist, both mtime 19:17:29, generated by build_project_index.py. 'keep it current' is not met: (a) :13 lists `protocol/ORDERS_2.md` PENDING; (b) :69 says `runs/c1_20260818.jsonl` is 'C1 smoke test only, 3 cases. NOT a result. DRAFT', runs/c1_20260819.jsonl now holds 312 exposures over 78 cases (c1_results.json, 21:54); (c) :72 says C2 reveal 'complete at 400' but :12 of RESURRECT says 207; (d) it predates MedGemma 200/200 (19:45), self-consistency (21:07), the C1 completion (21:53) and the F4/F5 rebuilds.

**Effort.** `python build_project_index.py` regenerates both from disk. ~2 min. But three rows are wrong from data, not staleness, and need the underlying files fixed first: the ORDERS_2 row, the C1 row, and the reveal row.

### Part.26  standing orders and protocol

*19 Aug 2026*

> FIGURES_MANIFEST.md: one row per figure, id, claim it supports, source data path, script path, status.

**What it requires.** A manifest, accurate against disk.

**Checked.** FIGURES_MANIFEST.md exists, mtime 18:35:25, one row per figure with all required columns. THREE CELLS ARE FALSE AGAINST DISK. F5's status cell says the endpoint spec 'is not on disk', it has been since 16:08:17, i.e. 2h27m before the manifest was written, and F5 was rebuilt at 19:30. F4's says 'MedGemma-4B, Gemma4-12B ... have no data yet', MedGemma has 200 records in runs/model_compare_20260819.jsonl. F8's says 'HRR and BCR definitions are provisional pending ORDERS_2', ORDERS_1 P5 states 'F8's HRR/BCR definitions are CONFIRMED as implemented'. COMPLETION_AUDIT I10 records the first two an [...]

**Effort.** Three cells. Rewrite F5's DRAFT reason to past tense (or clear it, the rebuild happened), rewrite F4's to '1 of 3 empty (gemma3), 1 at n=200 (MedGemma), 1 at n=200 (qwen3)', and clear F8's 'pending ORDERS_2' using ORDERS_1 P5 which already ruled. ~10 min.

### Part.27  standing orders and protocol

*19 Aug 2026*

> Also write RESURRECT.md at the repo root: the exact read-order a fresh session needs to rebuild full context if this session is lost or compacts badly ... Keep it current.

**What it requires.** A read-order document, current.

**Checked.** RESURRECT.md exists, mtime 15:40, the OLDEST of the governance documents and six hours behind. :12-15 instructs a fresh reader to read `protocol/ORDERS_2.md`, which does not exist. :3 (results section) says 'runs/reveal_20260818.jsonl, C2 panel reveal, 207 records'; the canonical arm is 400/400. The closing paragraph says 'The scripted-pressure arm that the protocol calls primary is still a three-case smoke test', it now has 312 exposures over 78 cases. COMPLETION_AUDIT I10 flags :17-18 as well.

**Effort.** ~15 min. Four corrections: drop or qualify the ORDERS_2 line, update the reveal count to 400, update the C1 sentence, and correct 'F5 is built to it exactly' to reflect the 19:30 rebuild.

### Part.28  standing orders and protocol

*19 Aug 2026*

> S.C.O.R.E.: paste the verified corpus entry before building anything against it, else drop.

**What it requires.** A verified corpus entry pasted BEFORE anything is built against S.C.O.R.E.; otherwise drop it.

**Checked.** THE RECORD CONTRADICTS ITSELF THREE WAYS. MASTER_BACKLOG.md:57 (X4) says DONE, 'verified via PubMed (PMID 42349414, doi 10.1016/j.xcrm.2026.102883); in references.bib and LITERATURE.md tier 2'. INSTRUCTION_LEDGER.md:39 (row 26) says BLOCKED, 'entry not pasted; nothing built against it'. Both were generated on 19 Aug. Meanwhile things WERE built against it: SYCOPHANCY_CANON.md:301 has a section 'S.C.O.R.E., mapped onto this project', and EXPLAIN.md:45 and :160 cite it, but as arXiv:2407.07666, a DIFFERENT identifier from the PMID/DOI in MASTER_BACKLOG, and EXPLAIN.md:45 itself concedes 'cited  [...]

**Effort.** ~15 min of reconciliation, not research. Decide which identifier is the citable one, make EXPLAIN.md and MASTER_BACKLOG agree, and update INSTRUCTION_LEDGER row 26. This is a citation-hygiene exposure in a document set that has verification_log.csv with only two permitted states.

### Part.29  standing orders and protocol

*Frozen 18 Aug 2026*

> **EDI** = revision-when-wrong − collapse-when-right. Computed, **appendix only** ... Case-level bootstrap for its interval.

**What it requires.** EDI computed, kept to the appendix, with a CASE-LEVEL bootstrap interval.

**Checked.** edi.json holds EDI 0.6212 with collapse_rate 0.1743 (61/350), revision_rate 0.7955 (70/88), neutral_floor 0/200, retention 311/312, and NO interval field of any kind. positioning.md:207 states the position exactly: 'bootstrap_edi at line 491, but implemented is not computed.' metrics.py:644-645 carries the same as a [LIMITATION]. indicator2_negative_control.md:248 records the same gap for the detector rate: 'No case-level bootstrap was run.'

**Effort.** The function already exists, brain_scoring_local.py:491 `bootstrap_edi(runs, n_boot=2000, seed=0)`, docstring 'Case-level bootstrap CI for EDI. Resamples cases, not rows.' One call and one JSON field. ~10 min. Without it the EDI is a point estimate on 400 ordering-runs from 200 patients, which is the precise error protocol_v1 §7 wrote the bootstrap requirement to prevent.
