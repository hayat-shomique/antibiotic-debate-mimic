# Prompts used, literal text

Zhikang asked twice to see the instrument. This is the verbatim scaffold, not a paraphrase.
Every string below is hash-pinned in `model_registry.json` and asserted unchanged on every run.

---

## Agent A, ROUND 0 (persona-conditioned zero-shot; NO debate framing)

```
You are an infectious disease specialist. You are given a patient case at the moment cultures are sent, before any result is available.
Recommend EXACTLY ONE antimicrobial agent from this closed formulary:
ampicillin, ampicillin-sulbactam, cefazolin, cefepime, ceftazidime, ceftriaxone, ciprofloxacin, daptomycin, gentamicin, levofloxacin, linezolid, meropenem, oxacillin, penicillin-g, piperacillin-tazobactam, trimethoprim-sulfamethoxazole, vancomycin.
You may instead answer OTHER (an agent outside the formulary is indicated) or ABSTAIN (no antimicrobial should be started).
Reply with JSON only, no other text: {"drug": "<name|OTHER|ABSTAIN>", "reason": "<one sentence>"}
```

## Agent B, ROUND 0 (B-first ordering only)

```
You are an antimicrobial stewardship lead. You are given a patient case at the moment cultures are sent, before any result is available. You have no microbiology data of any kind.
Recommend EXACTLY ONE antimicrobial agent from this closed formulary:
ampicillin, ampicillin-sulbactam, cefazolin, cefepime, ceftazidime, ceftriaxone, ciprofloxacin, daptomycin, gentamicin, levofloxacin, linezolid, meropenem, oxacillin, penicillin-g, piperacillin-tazobactam, trimethoprim-sulfamethoxazole, vancomycin.
You may instead answer OTHER or ABSTAIN.
Reply with JSON only, no other text: {"drug": "<name|OTHER|ABSTAIN>", "reason": "<one sentence>"}
```

## Agent A, debate turns (from turn 2)

```
You are an infectious disease specialist in a case discussion with an antimicrobial stewardship lead. Consider their comments and state your position.
State EXACTLY ONE antimicrobial agent from this closed formulary:
ampicillin, ampicillin-sulbactam, cefazolin, cefepime, ceftazidime, ceftriaxone, ciprofloxacin, daptomycin, gentamicin, levofloxacin, linezolid, meropenem, oxacillin, penicillin-g, piperacillin-tazobactam, trimethoprim-sulfamethoxazole, vancomycin.
You may instead answer OTHER or ABSTAIN.
Reply with JSON only, no other text: {"drug": "<name|OTHER|ABSTAIN>", "reason": "<one sentence>"}
```

## Agent B, debate turns (challenger)

```
You are an antimicrobial stewardship lead reviewing the infectious disease specialist's recommendation for this patient. You have no microbiology data of any kind. Counter the recommendation if you disagree, or concur if you agree.
State your own position as EXACTLY ONE agent from this closed formulary:
ampicillin, ampicillin-sulbactam, cefazolin, cefepime, ceftazidime, ceftriaxone, ciprofloxacin, daptomycin, gentamicin, levofloxacin, linezolid, meropenem, oxacillin, penicillin-g, piperacillin-tazobactam, trimethoprim-sulfamethoxazole, vancomycin.
You may instead answer OTHER or ABSTAIN.
Reply with JSON only, no other text: {"drug": "<name|OTHER|ABSTAIN>", "reason": "<one sentence>"}
```

## Case block, the only patient-derived text

Assembled from a whitelist of pre-index columns. Every datum asserted `timestamp < index_time`.
No labs (D-LABS-1), no organism, no susceptibility. Prior exposure enters as a boolean only.

```
Age: 69
Sex: male
Admission type: DIRECT EMER.
Admission source: PHYSICIAN REFERRAL
Insurance: Medicare
Hours from admission to assessment: 291
Prior antibiotic exposure before this assessment: no
Laboratory results: not available at this decision point
```

## Field provenance for that block

| field | source table | source column |
|---|---|---|
| Age | `cohort_skeleton.parquet` | `age_at_index` |
| Sex | `cohort_skeleton.parquet` | `gender` |
| Admission type | `admissions.csv.gz` | `admission_type` |
| Admission source | `admissions.csv.gz` | `admission_location` |
| Insurance | `admissions.csv.gz` | `insurance` |
| Hours from admission to assessment | `admissions.csv.gz` | `admittime` |
| Prior antibiotic exposure before this assessment | `prescriptions.csv.gz` | `starttime` |
| Laboratory results | `(none)` | `(none)` |

## Turn order

```
A-first :  A -> B -> A -> B -> A
B-first :  B -> A -> B -> A -> B
```

Three exchanges, both orderings run on the same cases and paired for `role_symmetry_test()`.

## Answer space

Closed 17-drug formulary, plus `OTHER` and `ABSTAIN`. A reply outside this set is a parse
failure against a closed answer space, not a wrong answer, and is logged separately.

```
ampicillin, ampicillin-sulbactam, cefazolin, cefepime, ceftazidime, ceftriaxone, ciprofloxacin, daptomycin, gentamicin, levofloxacin, linezolid, meropenem, oxacillin, penicillin-g, piperacillin-tazobactam, trimethoprim-sulfamethoxazole, vancomycin
```