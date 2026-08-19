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

## The one defect that was fixed today

The two generative columns were not comparable. Qwen's 171 cases had been **harvested** from the
debate log to save 200 calls; MedGemma's 54 were **freshly called**. One column reused and one
called is not a controlled contrast, whatever the numbers say. Both columns are now being called
fresh, on the same 200 cases, same prompt, same seed, same quantisation. The harvested rows stay
on disk as an audit trail and are distinguishable by their `source` field.

## Fixed across every model

Temperature 0. Seed 20260818. `num_ctx` 8192. `num_predict` 512. Thinking disabled. Digest
recorded per model and asserted before use, because Ollama exits 0 while printing a pull error.
