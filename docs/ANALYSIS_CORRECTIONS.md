# Corrections to a circulated analysis of the encoder log

The framing of Tingting's four pillars in that analysis is sound and worth keeping. Four factual
statements in it are wrong against what is on disk, and one of them reverses the conclusion.

| claim | status | what disk says |
|---|---|---|
| "the marginal gain from your entire multi-agent dialogue system is a mere 3.0 percentage points" | **WRONG, and the sign flips** | 87.5% is the ZERO-SHOT round-0 figure, before any interaction. The post-debate final is 77.0% (A-first) / 78.0% (all 400 runs). Against BiomedBERT's 84.5%, the single agent is +3.0 and the **two-agent system is −7.5**. |
| BiomedBERT guesses "cefepime or piperacillin-tazobactam" | **WRONG** | ceftazidime ×159, meropenem ×41. It predicts neither of the named drugs. |
| "Qwen (an advanced MoE model)" | **WRONG** | `qwen3:4b-instruct-2507-q4_K_M` is a dense 4B model, not mixture-of-experts. |
| the four classes are "Adequate, Inadequate, Undetermined, and Error" | **WRONG** | ADEQUATE, INADEQUATE, **INTERMEDIATE_ONLY**, UNDETERMINED. There is no Error class. A parse failure is recorded separately and is never scored as a wrong answer. |
| "Day 3 re-evaluation correctness" | **NOT HERS** | She wrote "once additional information becomes available". No day-3 window was specified by her or implemented here. |

Correct in the analysis and worth keeping: the diagnosis that the task rewards knowing the
high-prevalence empiric default rather than personalised synthesis; the vindication of the
four-class scorer by the Bio_ClinicalBERT vancomycin case; and the reading of high agreement as
diversity collapse.
