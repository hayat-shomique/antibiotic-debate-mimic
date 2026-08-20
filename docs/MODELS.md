# Models, the simple version

What was committed to the supervisor on Teams: *"I'm using Ollama Qwen3:4b, medgemma:4b and
I am going to add in my bert encoder results too."* She then asked for two more things: a
medical BERT compared **without fine-tuning** ("like Med Bert or ClinicalBert"), and DeepSeek,
because its chain of thought is visible. This is what is actually built against that.

## Three tiers, three different questions

| tier | model | size / quant | the question it answers |
|---|---|---|---|
| **1. Study model** | `qwen3:4b-instruct-2507-q4_K_M` | 4B, Q4_K_M | Every debate arm runs on this. It is the subject, not a comparison. |
| **2. Domain comparison** | `medgemma:4b-it-q4_K_M` | 4B, Q4_K_M | Does medical domain tuning change the behaviour? |
| **3. Encoder baseline** | four BERT models, no fine-tuning | 110M | How well does a small domain encoder do at all, with no dialogue? |

**Why tiers 1 and 2 are both 4B and both Q4_K_M.** That matching is the whole point. If one were
12B, any difference would confound domain tuning with scale and the comparison would answer
neither question. Size and quantisation held fixed, the only thing that varies is the training
corpus.

## Tier 3 is already done, and it is a strong result

Her ask was medical BERT with no fine-tuning. Masked-token prediction over the 17-drug
formulary, 200 cases, scored against the same susceptibility panels as everything else.

| encoder | distinct predictions across 200 cases | most frequent | adequate |
|---|---|---|---|
| `emilyalsentzer/Bio_ClinicalBERT` | **1** | vancomycin ×200 | 0/200, every case UNDETERMINED |
| `dmis-lab/biobert-base-cased-v1.2` | 2 | linezolid ×177 | 22/200 |
| `google-bert/bert-base-uncased` (general, control) | 2 | ampicillin ×198 | 50/200 |
| `microsoft/BiomedNLP-BiomedBERT` | 2 | ceftazidime ×159 | **169/200 = 84.5%** |

Two things to say about this table:

1. **All four encoders are near-constant too.** One to two distinct predictions across 200
   different patients. The fixed-policy behaviour is not a quirk of the generative model, it
   appears in a 110M encoder as well.
2. **BiomedBERT reaches 84.5% against Qwen's 87.5%.** A 110M-parameter encoder with no
   fine-tuning and no dialogue lands within three points of a 4B generative model. That is the
   sharpest way to say the task is not discriminating what people think it discriminates.

Bio_ClinicalBERT scoring 0/200 is not a failure to answer, it answers vancomycin every time,
and vancomycin is a Gram-positive agent that the laboratory does not test against the
Gram-negative organisms in this cohort. It is UNDETERMINED, not wrong. That distinction is the
whole reason the scorer has four outcome classes.

## What was dropped, and why

- **`gemma4:12b`**, was in the code's default model list and never ran a single case. Removed.
  A 12B model varies size *and* family generation at once, so it could not have isolated either.
- **MedGemma-12B**, she said "there is 12B as well, 27B is not necessary". Not used, for the
  same size-matching reason. It is the right model for a *scale* question, which is a different
  experiment.
- **DeepSeek-R1-8B**, installed and unused. Her reason for suggesting it was visible chain of
  thought, which is an interpretability question, not an accuracy comparison. It is 8B, so it
  cannot join the size-matched contrast. If it is used, it must be framed as reading the
  reasoning, never as a fourth accuracy column.
- **`gemma3:4b`, `gemma3:12b`, `deepseek-llm:7b`, `qwen3:4b` (base)**, installed during
  exploration, in no analysis. Left on disk; removed from every code path.

## The mixed-source column, stated as it actually is

An earlier version of this file said both generative columns were being called fresh. **They are
not, and the claim is withdrawn.** What is on disk, counted by `analysis/model_tiers.py` and
recorded in `results/model_tiers.json`:

| column | n | source |
|---|---|---|
| `medgemma:4b-it-q4_K_M` | 200 | 200 freshly called |
| `qwen3:4b-instruct-2507-q4_K_M` | 200 | **171 harvested** from round 0 of the debate log, 29 freshly called |

Harvesting was done to save 200 model calls. One column reused and one called is not, in general, a
controlled contrast, so the question is whether the mixture can bias this particular comparison. It
cannot, and that is measured rather than argued:

- **The two sources agree on a single drug.** All 171 harvested rows and all 29 freshly called rows
  return piperacillin-tazobactam. The column has no variance for the source to bias.
- The harvested rows come from round 0 of the debate arm, which uses the same system prompt, the
  same temperature 0, the same seed and the same quantisation as a fresh call.
- The column's outcome distribution, 175 adequate of 200, matches the canonical baseline in
  `results/tingting_endpoints.json` exactly.

The honest reading: the comparison stands, and the correct claim is that the Qwen column is
reproducible rather than that it was freshly called. If a reviewer wants the stronger version, the
fix is 171 model calls, which is roughly three hours of local inference and changes no number
unless determinism fails.

**What the comparison shows.** MedGemma-4B is also near-constant, on a *different* drug: cefazolin
in 198 of 200 cases, reaching 102/200 = 51.0% adequate against Qwen's 175/200 = 87.5%. Holding the
prompt fixed and getting two different constants localises the choice of drug to the weights rather
than to the prompt.

## Fixed across every model

Temperature 0. Seed 20260818. `num_ctx` 8192. `num_predict` 512. Thinking disabled. Digest
recorded per model and asserted before use, because Ollama exits 0 while printing a pull error.
