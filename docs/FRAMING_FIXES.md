# Framing corrections, and the novelty claim as it can actually be defended

Three framings were wrong or unsupported. Each is corrected below with the reason, so the
correction survives into every artefact rather than being remembered.

---

## FIX 1, WHO AWaRe: "0/400 Access" is not a stewardship failure

**What was written.** "400/400 recommendations sit in the WHO Watch group. Zero from Access -
the first-line agents. The model never recommends a first-line drug."

**Why it is wrong.** Access-group agents are first-line for *common* infections, ampicillin,
cefazolin, amoxicillin. For suspected bloodstream infection, Watch-group empiric therapy
(piperacillin-tazobactam, cefepime, ceftriaxone, meropenem) is what guidance actually recommends
until an organism is known. A model sitting in Watch for suspected bacteraemia is doing the
**clinically expected** thing. Presenting that as a failure is a microbiology error, and it would
be caught immediately in a room that contains people synthesising antibiotics.

**The defensible version.** The interesting number is not the level, it is the *absence of
movement*:

> The debate changes the recommended drug in **400/400** runs and changes the WHO AWaRe class in
> **0/400**. Five turns of conversation reshuffle within a single stewardship class. Whatever the
> exchange is doing, it is not de-escalation.

That claim needs no assumption about which class is correct, and it is the one the data supports.

---

## FIX 2, the clinician comparison: state it on comparable ground

**What was tempting.** Model round-0 87.5% against the clinician's 62.5%. A 25-point margin.

**Why it is wrong.** The two denominators are not the same. The clinician's actual prescription
scores UNDETERMINED in 62 of 200 cases, largely because real prescriptions fall outside the closed
17-drug formulary or were never tested against the isolate. Comparing 87.5% to 62.5% compares a
model that always answers inside the formulary against a clinician who is being penalised for
prescribing outside it.

**The defensible version.**

| | all 200 | determined only |
|---|---|---|
| Clinician's actual empiric choice | 125/200 = 62.5% | 125/138 = **90.6%** |
| Model, round-0 | 175/200 = 87.5% | 175/192 = **91.1%** |

> On the cases where both can be scored, the model and the clinician are indistinguishable:
> **91.1% against 90.6%.** The apparent margin on the full cohort is a denominator artefact.

This directly answers the supervisor's question, *"compare LLM with clinician, see if they agree
or LLM is worse or better?"*, and the answer is **neither is better**. Saying so is stronger
than claiming a win, because the win does not survive its own denominator.

**Context worth stating alongside it.** Susceptibility results become available at a median of
**134 hours** after the culture is drawn, and **zero** results are available at 5, 12 or 24 hours.
The empiric decision is genuinely made without the information, for both the clinician and the
model. That is why the pre-culture window is the right decision point, a design choice that came
from the supervisor: *"it is interesting to see what LLM suggests before the culture result is
out."*

---

## FIX 3, "sycophancy": name what is measured, not what it resembles

**The risk.** A reviewer can say: this is not sycophancy, it is a weak model with a near-constant
policy whose output changes whenever the prompt changes. No social phenomenon is required to
explain any of it.

**Why that objection is serious.** It is consistent with the headline numbers. A model with one
favourite answer will move whenever anything is appended to its context.

**What defeats it, and this is the whole reason the control arms exist.**

| arm | what changes in the prompt | moved |
|---|---|---|
| Neutral re-ask | context grows; no disagreement, no new facts | **0/200** |
| Bare disagreement | context grows by one sentence of pure dissent | 34/60 |
| Reasoned challenge | context grows by an argued counterpart turn | 60/60 |

If context length or prompt perturbation explained the movement, the first row would not be zero.
It is zero. The model moves when it is *contradicted*, not when its prompt changes.

**The wording to use.** Do not lead with the word sycophancy. Lead with what was measured:

> Under a peer contradiction the agent abandons a verifiably correct position, and it adopts the
> counterpart's drug whether that drug is adequate or not. Under the actual laboratory result it
> revises correctly. The gap between those two responses is the finding.

Then name it once: this is the behaviour the sycophancy literature calls harmful deference, and
the four-cell classification here is the supervisor's own.

---

## The novelty claim, as it can be defended

**What already exists, and must be cited rather than claimed.**

| Prior work | What it established | Why this project is not it |
|---|---|---|
| Antonie et al. 2026, *Antibiotics* 15(4):368, doi 10.3390/antibiotics15040368 | LLM empiric antibiotic recommendations scored against susceptibility, compared to clinicians | Single-pass, one model, one turn. **No second agent, no challenge, no revision step.** Romanian single centre, not MIMIC. |
| MedCoAct, arXiv 2510.10461 | A doctor agent and a pharmacist agent collaborating on medication decisions | Arbiter is a **constructed benchmark key**, not a per-patient laboratory result. Reports collaboration *helping* by 7 points. |
| Kim et al. 2026, *Nature Machine Intelligence* 8:1157 to 1172 | Multi-agent coordination gives a mean improvement of 0.0% across 260 configurations | Six **non-clinical** agentic benchmarks. Medical settings appear only as future work. |
| SycEval | A taxonomy of progressive and regressive sycophancy under rebuttal | No external clinical ground truth; correctness is a benchmark key. |
| Mohsin et al. 2026, arXiv 2604.05279 | Separates pressure capitulation from evidence blindness | **Training-based** intervention, general domain, no clinical arbiter. |

**What is unoccupied in everything searched.** Not the arbiter, Antonie has that. Not the
persona pair, MedCoAct has that. Not the sycophancy construct, SycEval has that. The
unoccupied thing is the **conjunction**:

> A two-agent clinical debate in which **the revision step itself** is scored against a
> per-patient laboratory susceptibility panel, with **both speaking orders run on every case**,
> a **null arm** separating being asked again from being contradicted, and **confidence
> elicited against that same arbiter**.

Four elements make that conjunction do work rather than merely be a list:

1. **The revision is the measurement.** Every prior item measures a final answer. Here the object
   is the *change*, what it took to move the model off a verifiably correct position, and what it
   took to move it back.
2. **Speaking order is a measured variable, not a nuisance.** Every case is run both ways, so the
   41% order effect is observed rather than averaged away. None of the five items above reports a
   speaking-order effect.
3. **The null arm licenses the interpretation.** 0/200 under a neutral re-ask is what separates
   "responds to contradiction" from "responds to any prompt change".
4. **Confidence is scored against the laboratory, not against a benchmark.** The state the
   supervisor named, correct and confident becoming wrong and confident, is measured here with
   an external clinical arbiter, which is what the sycophancy literature lacks.

**What would falsify the claim.** Any published study that runs a multi-agent clinical debate,
scores the revision against per-patient microbiology, and reports a speaking-order or null-arm
control. If such a study exists, the contribution reduces to a replication in a new cohort, and
that should be said plainly rather than defended.

**The claim in one sentence, for a slide:**

> Susceptibility-arbitrated evaluation of LLM antibiotic choice exists; two-agent clinical debate
> exists. What has not been done is to put the arbiter *inside* the debate and measure the
> revision, which is where the failure turns out to live.

**And the supervisor's own view, on the record, 13 August:** *"I think the ideas we discussed
about LLM for antibiotics is pretty novel."*
