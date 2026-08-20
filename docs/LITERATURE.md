# Reading list

For Shomique, to actually read. Ordered by what pays off soonest, not alphabetically.
Every entry here has been fetched and checked, the identifier resolves and the claim
quoted is in the paper. Anything unverified is marked and must not be cited.

Tick the box when you have read it. `references.bib` has all 44 entries for LaTeX.

---

## Tier 1, read before the talk (4 papers, ~3 hours)

These four change what you say on stage.

### [ ] 1. Kim et al., Capable language models can outgrow the benefits of collaboration
*Nature Machine Intelligence* 8:1157 to 1172 (2026) · [10.1038/s42256-026-01268-y](https://doi.org/10.1038/s42256-026-01268-y)
**PDF is already on your disk** at `articles/10.1038_s42256-026-01268-y.pdf`. Sent by Tingting.

260 configurations: six agentic benchmarks × five coordination topologies × nine models,
holding prompts, tools and compute fixed and varying only coordination structure and model
capability. **Mean multi-agent improvement: 0.0%** (95% CI −58.7% to 77.2%). One coefficient
survives both cluster-robust inference and Holm correction, the single-agent baseline.

**Why you read it:** it is the reason your result is a contribution and not a failed
experiment. Read §Results and Table 2. Skip the coordination-metric regression; it does not
transport, and their own leave-one-dataset-out R² is −2.09.

**The line for your slide** (p. 1159): *"the overall mean MAS improvement is 0.0% (95%
confidence interval (CI) −58.7% to 77.2%)"*.

---

### [ ] 2. Oh, Kim, Park & Kim, Test-Time Scaling Strategies for LLMs and VLMs in Medicine
*JMIR* 28:e90693 (2026) · [10.2196/90693](https://doi.org/10.2196/90693) · PDF on your Desktop

~30 open models, five text benchmarks (5,578 items), two multimodal (7,000 items), five
scaling configurations. They inject a misleading answer **framed as another physician's
opinion** and watch models abandon correct reasoning.

**Why you read it:** this is the closest published thing to your finding, in a peer-reviewed
medical venue, and it settles your title question. Read the Discussion first (pp. 13 to 14),
then Figure 7.

**Two lines that matter.** p. 1: *"Test-time scaling rules from general domains do not
perfectly translate to medical AI. Longer reasoning is not universally beneficial."*
p. 13: *"models are particularly sensitive to the expertise level of the physician providing
the additional input"*, that sentence licenses your whole doctor-versus-pharmacist design.

**The catch you must state:** scaling *does* recover baseline on easy tasks and fails only on
hard ones (p. 13 and p. 14). Say both halves or you will be corrected.

---

### [ ] 3. Zheng, Shi & Yi, MedCoAct: Confidence-Aware Multi-Agent Collaboration
arXiv [2510.10461](https://arxiv.org/abs/2510.10461)

**This is your closest prior art and you need to have read it.** A doctor agent and a
pharmacist agent, collaborating, with confidence-awareness. Exactly your personas.

**But:** it runs on DrugCareQA, a constructed benchmark, not on real patient records. Its
arbiter is a benchmark key, not a laboratory result. And it reports collaboration **helping** -
67.58% accuracy, +7.04 points over a single agent.

**Why you read it:** so that when someone says "hasn't this been done?", you can answer
precisely. Your differences are the arbiter (susceptibility panel vs benchmark key), the
data (MIMIC-IV cases vs constructed QA), the paired both-orders design, and the fact that
you report the opposite sign. Do not hide that they found a gain, engage with it.

---

### [ ] 4. Mohsin, Bilal, Umer & Fox, Pressure, What Pressure?
arXiv [2604.05279](https://arxiv.org/abs/2604.05279)

Separates two failure modes that get conflated: **pressure capitulation** (changing a correct
answer under social pressure) and **evidence blindness** (ignoring the provided context).
Fixes them by training, with a five-term GRPO reward.

**Why you read it:** they give you the vocabulary your three-arm ladder already measures.
Your neutral re-ask (0/200), bare disagreement (34/60) and reasoned challenge (60/60) is an
operationalisation of their *pressure independence*. Your seeded-counterpart arm is their
*evidence responsiveness*. They intervene by training; you measure it training-free in a
clinical setting. Use their terms, a referee who knows this paper will recognise them.

---

## Tier 2, read this week (5 papers)

### [ ] 5. Tan et al., A S.C.O.R.E. framework for evaluating open-ended LLM responses in healthcare
*Cell Reports Medicine* 7(7):102883 (2026) · [10.1016/j.xcrm.2026.102883](https://doi.org/10.1016/j.xcrm.2026.102883)
Sent by Tingting. Retrieved via PubMed (PMID 42349414, PMC13400166).

**S**afety, **C**onsensus & Context, **O**bjectivity, **R**eproducibility, **E**xplainability.
Validated against BLEU, ROUGE and BERTScore on GPT-4o, Claude 4 Sonnet and DeepSeek across
ophthalmology, medication and anaesthesia. Cronbach's α 0.745; Cliff's δ 0.68 to 0.92.

**The finding you want:** quantitative metrics *"frequently misclassified clinically
appropriate responses as inaccurate"*. That is an independent, clinical argument for why you
built an external arbiter instead of trusting a similarity score. Note the pharmacy author
(Jasmine Ong, Division of Pharmacy, SGH), the pharmacist role is taken seriously in this
literature.

### [ ] 6. Schmidgall et al., AgentClinic
arXiv [2405.07960](https://arxiv.org/abs/2405.07960)

Sequential clinical decision-making rather than static QA. **Diagnostic accuracy drops to
below a tenth of the static-QA figure.** Read it for the framing that benchmark accuracy and
sequential clinical performance are different things, which is your slide 4.

### [ ] 7. Chen, Cui, Ye, Zhang, Bian & Zhu, EBM-CoT
arXiv [2511.07124](https://arxiv.org/abs/2511.07124)

**Zhikang's and Tingting's own paper.** Energy-based calibration of latent reasoning
trajectories. General reasoning, not healthcare. Read the abstract and intro at minimum -
knowing what your collaborator actually works on changes how you pitch to him. His interest
is reasoning consistency; frame your order-effect result in those terms.

### [ ] 8. Lessons from deploying the ChatEHR system at Stanford Medicine
*Nature Medicine* · sent by Tingting · [s41591-026-04574-5](https://www.nature.com/articles/s41591-026-04574-5)

Benchmark-based evaluation is insufficient for monitoring a deployed system. Directly supports
your benchmark-versus-safety framing. **Not yet fetched and verified, do not cite until read.**

### [ ] 9. How to benchmark medical AI agents
*PLOS Medicine* Perspective · sent by Tingting

Why benchmarking multimodal LLM agents for clinical workflows is hard. **Not yet fetched and
verified, do not cite until read.**

---

## Tier 3, know they exist, read if asked

From Tingting's lab chat, all sent between June and August 2026. These map the space she is
thinking in, which is worth knowing before you present to her.

| paper | one line | why it might matter |
|---|---|---|
| GenAI CDS in Kenyan primary care, *Nature Medicine* | cluster-randomised trial; GPT-4o support did **not** significantly reduce 14-day treatment failure | the strongest negative RCT for clinical LLM support |
| Toward a test of medical AI superintelligence, *Nature Medicine* | existing benchmarks are misleading | benchmark critique |
| Dynamic red-teaming for health LLMs, *Nature Health* | adversarial agents find safety gaps benchmarks miss | Tingting's comment: *"out of date already...."* |
| GraphDx, arXiv 2607.15280 | cost-aware knowledge-enhanced multi-agent sequential diagnosis | already in your bib |
| PatientAgentBench, arXiv 2607.25485 | benchmark for patient-facing agentic systems | agentic medical benchmarks |
| LongMedBench, arXiv 2607.09322 | EHR-based long-horizon clinical decision-making | long-horizon evaluation |
| Small language models in medicine, *Nat. Biomed. Eng.* | the case for small models clinically | you used a 4B model, this is your justification |
| AI in drug discovery, *Nat. Rev. Drug Discov.* | Tingting quoted it: *"evidence of their clinically relevant impact is, so far, disappointingly limited"* | her stated view on AI hype |

---

## Read only if someone brings it up

### [ ] Zahavy, Position: LLMs can't jump
PMLR 306 (2026) · PDF on your Desktop · sent by Tingting

Induction, deduction, abduction; Einstein's route to General Relativity as the case study.
**Carries almost no evidential weight for you.** It is a position paper with no data, no models
run, no metrics, and both figures are AI-generated. Zero occurrences of sycophancy, deference,
debate, multi-agent, clinical, medical or patient across the whole text.

Use it for one framing line in Q&A, never as related work. If you do cite it, know that the
author is at DeepMind, co-authors the AlphaProof paper he uses as evidence, and the remedy he
proposes is his own institution's product line.

### [ ] Stürenburg et al., Tracking funding disparities in global health aid
medRxiv [10.1101/2025.06.20.25329993](https://doi.org/10.1101/2025.06.20.25329993), **preprint, not peer reviewed**

Off-topic for this project: no agent, no antibiotic task, no susceptibility arbiter. It earns
exactly one borrowed move, they demote their metric where they define it (p. 27: *"This metric
is designed to capture relative disparities, rather than absolute funding adequacy"*) rather
than in a limitations paragraph. Do the same for susceptibility concordance in your Methods.

---

## Clinical evidence, added 20 August 2026

These are not machine-learning papers. They are the clinical literature the interpretation slide
and the limitations section stand on. Every identifier was resolved against PubMed on 20 August
2026 and every figure below was read from the retrieved abstract. They are in `references.bib`
under the keys given.

### [x] SIMPLIFY. Lopez-Cortes et al., Lancet Infect Dis 2024;24(4):375-385

`lopezcortes2024simplify`, doi 10.1016/S1473-3099(23)00686-2, PMID 38215770.

Open-label pragmatic randomised trial, 21 Spanish hospitals, Enterobacterales bacteraemia treated
empirically with an antipseudomonal beta-lactam. Patients were randomised to de-escalate by a
predefined susceptibility-ordered rule, with ceftriaxone among the options, or to continue.
Clinical cure 148/164 (90%) against 148/167 (89%), risk difference 1.6 percentage points, 95% CI
minus 5.0 to 8.2, non-inferior against a minus 10% margin.

**Why it is the strongest addition available.** It separates the move from the reason for the
move. De-escalating piperacillin-tazobactam to a narrower cephalosporin is trial-supported when
susceptibility guides it. This study performs that same move for a reason that is not
susceptibility, and the two have opposite safety profiles: harmful revision under a content-free
argument against harmful revision when the panel triggers it. Same destination drug, opposite
outcome, and the trigger is the variable. Cite it as the positive control for the move, never as
support for what the debate does.

### [x] Rhee et al., JAMA Netw Open 2020;3(4):e202899

`rhee2020`, doi 10.1001/jamanetworkopen.2020.2899, PMID 32297949.

17,430 adults, 104 US hospitals, culture-positive community-onset sepsis. Inadequate empiric
therapy adjusted OR 1.19, 95% CI 1.03 to 1.37. Unnecessarily broad empiric therapy adjusted OR
1.22, 95% CI 1.06 to 1.40.

**Why it matters here.** It is what makes the spectrum endpoint more than bookkeeping: too broad
carries an adjusted odds ratio slightly higher than too narrow, so the carbapenem shift moves
along an axis with published outcome associations.

**What must be written beside it.** Community-onset sepsis across all culture sites, urine 52.1%
and blood 40.0%, not a bloodstream-only cohort. Cite for the existence and direction of the
overtreatment harm axis, never for a prevalence number carried across to this cohort. ESBL
prevalence there is 0.8%, so do not lean on ESBL as the mechanism.

### [x] Tamma et al., Clin Infect Dis 2019;69(8):1446-1455

`tamma2019ampc`, doi 10.1093/cid/ciz173, PMID 30838380.

The AmpC primer. Avoid expanded-spectrum third-generation cephalosporins for the organisms at
greatest risk of induction, best described for *Enterobacter cloacae*; the likelihood of induction
by other Enterobacteriaceae is less clear.

**Why it matters here.** This grading is implemented directly in `analysis/ampc_exposure.py`, which
is why the limitation now separates the 9 *E. cloacae* specimens from the other 27 AmpC-capable
ones instead of pooling all 36 behind one percentage.

### [x] Saleh et al., Int J Infect Dis 2026;167:108563

`saleh2026ampc`, doi 10.1016/j.ijid.2026.108563, PMID 41864271.

17 studies, AmpC-producing Enterobacterales. No significant difference in 30-day mortality between
carbapenems and noncarbapenems, OR 1.29, 95% CI 0.91 to 1.82. Carbapenems associated with more
adverse drug reactions, OR 4.32, 95% CI 1.73 to 10.79. Supports guidance recommending cefepime at
a minimum inhibitory concentration of 2 or below.

**Why it matters here.** It does two jobs. It gives the carbapenem shift a documented harm axis,
and it distinguishes the two destination drugs: cefepime is guideline-endorsed for AmpC producers,
ceftriaxone is the one the primer warns against.

### [x] Onorato et al., Infection 2024;53(3):1141-1153

`onorato2024ampc`, doi 10.1007/s15010-024-02447-y, PMID 39630396.

20 studies, 2,834 patients, bloodstream infections only, which is this cohort's site.
Piperacillin-tazobactam against cefepime or a carbapenem: no mortality difference, RR 1.1, 95% CI
0.76 to 1.58, but higher microbiological failure, RR 1.80, 95% CI 1.15 to 2.82, and higher clinical
failure, RR 1.54, 95% CI 1.00 to 2.40. Cefepime against carbapenems: lower mortality, RR 0.74, 95%
CI 0.59 to 0.94.

**Why it matters here, and it cuts both ways.** This study's baseline drug is
piperacillin-tazobactam and one of its two destinations is cefepime. For AmpC producers
specifically, this meta-analysis says the baseline drug is the weaker choice and cefepime is the
better one. So the AmpC concern does not simply make the debate look worse: on the 23 harmful
revisions that land on cefepime it does not apply at all. Do not use this to argue the debate is
doing something clinically sensible. It is not selecting cefepime because the organism is an AmpC
producer; it selects the same two drugs regardless of organism, which is exactly the finding.

### [x] Cheo et al., Open Forum Infect Dis 2025;12(7):ofaf413

`cheo2025cefepime`, doi 10.1093/ofid/ofaf413, PMID 40718546.

Seven bloodstream-infection studies, 1,099 patients, 479 cefepime and 620 carbapenem. No
significant mortality difference, log OR 0.15, 95% CI minus 0.33 to 0.64. PROSPERO CRD42025634449.
Corroborates Saleh on bloodstream infections specifically. Hold it in reserve; one meta-analysis on
this point is enough for a ten-minute talk.

---

## Rules for citing anything above

- Nothing gets cited until it has been read. Tiers 2 items 8 and 9 are explicitly unverified.
- Never write "nobody has done X". Write "none of the items in this list does X".
- Never write that a recommendation *caused* an outcome. MIMIC-IV is observational.
- When a paper reports the opposite of your result, MedCoAct does, say so on the slide.
