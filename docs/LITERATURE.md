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

## Rules for citing anything above

- Nothing gets cited until it has been read. Tiers 2 items 8 and 9 are explicitly unverified.
- Never write "nobody has done X". Write "none of the items in this list does X".
- Never write that a recommendation *caused* an outcome. MIMIC-IV is observational.
- When a paper reports the opposite of your result, MedCoAct does, say so on the slide.
