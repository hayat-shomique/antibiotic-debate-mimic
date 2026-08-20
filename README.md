# Two clinical LLM agents, one antibiotic, and a laboratory as referee

Do two language-model agents that talk to each other make a better clinical decision, or do they just
end up agreeing? This repository is an evaluation that can answer that, because it scores the
recommendation against something neither agent can see and neither agent can argue with: the
patient's own microbiology.

**Shomique Hayat** · UNIQ+ research internship, University of Oxford, Institute of Biomedical
Engineering · supervised by **Prof. Tingting Zhu**, with **Zhikang Chen** · 6 July to 20 August 2026

---

## Start here

| | |
|---|---|
| **[PROJECT.md](PROJECT.md)** | **the whole project in one document**: the question, the design, the instrument verbatim, the communication protocol, every result, the bounds, and what each supervisor asked for |
| [deck/](deck/) | the conference talk, generated from `results/*.json` |
| [deck/EVIDENCE.md](deck/EVIDENCE.md) | every claim in the talk mapped to its number, its result file and the script that produces it |
| [BRIEFING.md](BRIEFING.md) | the talk brief: the argument out loud, the ten numbers, the question drill |
| [AUDIT.md](AUDIT.md) | model health, per-arm data integrity, artefact provenance |

Longer source documents are in [docs/](docs/). Superseded documents are kept in
[archive/](archive/) rather than deleted, because several of them record how a number changed.

## The finding, in three rows

| what the agent hears | harmful revision rate | coverage of the organism |
|---|---|---|
| a scripted sentence with no content | 0.0% | unchanged, 87.5% |
| **a second agent arguing a case** | **15.2%** | **87.5% to 78.0%** |
| the susceptibility panel | 1.1% | 78.0% to 95.2% |

In this setup, agent-to-agent argument reduced coverage of the organism; supplying the susceptibility panel increased it. And the harm is invisible on the
accuracy endpoint: the same unsupported pressure moves carbapenem prescribing from
0 to 87.2 per cent while barely touching whether the answer was right.

Those numbers are reproduced from the run data by the commands below, not typed.

## Reproducing everything

```
python3 analysis/primary_test.py          # results/primary_test.json
python3 analysis/tingting_endpoints.py    # results/tingting_endpoints.json
python3 analysis/policy_degeneracy.py     # results/policy_degeneracy.json
python3 analysis/fewshot_analysis.py      # results/fewshot.json
python3 analysis/leakage_check.py         # results/leakage.json
python3 analysis/canonical_numbers.py     # results/RESULTS.json
python3 analysis/render_project.py        # PROJECT.md
python3 analysis/build_audit.py           # AUDIT.md
python3 deck/deck_figures.py              # every chart
python3 deck/build_deck.py                # the talk
python3 deck/build_evidence.py            # deck/EVIDENCE.md
```

## Data

MIMIC-IV v3.1 under a PhysioNet credentialed data use agreement. **No patient-level data is in this
repository**: run files stay on the local machine, `case_id` is `subject_id` + `_` +
`micro_specimen_id` so quoting one would republish two credentialed identifiers, and the case block
shown in `PROJECT.md` carries synthetic values. To reproduce, obtain MIMIC-IV access through
PhysioNet, place it locally, and run the analysis against your own copy.

## Licence

Code under the terms in [LICENSE](LICENSE). No data is redistributed.
