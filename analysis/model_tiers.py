"""model_tiers.py - the three model tiers, aggregated into results/model_tiers.json.

The tier numbers previously lived only in prose and in the run directory, so the
repository could not stand on its own. This writes aggregates, never case-level
rows, so nothing credentialed is committed.

    python3 analysis/model_tiers.py
"""
from __future__ import annotations

import collections
import glob
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = Path(os.path.expanduser("~/brain_run/runs"))
BRAIN = Path(os.path.expanduser("~/brain_run"))


def read(pat):
    return [json.loads(l) for f in sorted(glob.glob(str(RUNS / pat))) for l in open(f) if l.strip()]


mc = read("model_compare_*.jsonl")
tiers = {}
for model in sorted({r["model"] for r in mc}):
    rows = [r for r in mc if r["model"] == model]
    outcomes = collections.Counter(r["outcome"] for r in rows)
    drugs = collections.Counter(r["drug"] for r in rows)
    top, top_n = drugs.most_common(1)[0]
    src = collections.Counter(r.get("source", "unknown") for r in rows)
    tiers[model] = {
        "n": len(rows),
        "adequate": outcomes.get("ADEQUATE", 0),
        "adequate_pct": round(100.0 * outcomes.get("ADEQUATE", 0) / len(rows), 1),
        "outcomes": dict(outcomes),
        "distinct_drugs": len(drugs),
        "top_drug": top,
        "top_drug_share_pct": round(100.0 * top_n / len(rows), 1),
        "row_source": dict(src),
    }

# The Qwen column mixes freshly called rows with rows harvested from the debate log.
# That is only a defect if the two sources can differ. They cannot here: record it.
qwen = [r for r in mc if r["model"].startswith("qwen3")]
by_src = collections.defaultdict(collections.Counter)
for r in qwen:
    by_src[r.get("source", "unknown")][r["drug"]] += 1
tiers["_row_source_check"] = {
    "why": ("docs/MODELS.md once claimed both generative columns were freshly called. They are not. "
            "This records what is on disk and whether the mixture can bias the comparison."),
    "qwen_drugs_by_source": {k: dict(v) for k, v in by_src.items()},
    "sources_agree_on_a_single_drug": len({d for v in by_src.values() for d in v}) == 1,
}

tiers["_medbert"] = {
    "her_ask": ("Prof. Tingting Zhu, 29 July 2026, twice in one minute: 'compare with some medical "
                "bert models which previously trained on EHR data already. See how well they perform "
                "without fine-tuning' and 'Smith like Med Bert or ClinicalBert etc.'"),
    "clinicalbert": "run, see the encoder table",
    "med_bert_original": {
        "identifier_probed": "Rasmy/Med-BERT",
        "probed_on": "20 August 2026",
        "result": "not a valid model identifier on the HuggingFace Hub",
        "why_it_would_not_apply_anyway": (
            "the original Med-BERT of Rasmy et al. is pretrained on sequences of structured "
            "diagnosis codes, not free clinical text. Its vocabulary is codes, so a masked-token "
            "cloze over antibiotic names has nothing to predict into. Substituting it would require "
            "building a code-sequence representation of every case, which is a different study."),
        "what_was_run_instead": ["Charangan/MedBERT", "medicalai/ClinicalBERT"],
        "declared_before_the_numbers": (
            "both substitutes were chosen and launched before their results were seen, to answer her "
            "ask rather than to improve a column, and are reported whatever they show"),
    },
}

enc_path = BRAIN / "encoder_baseline_summary.json"
if enc_path.exists():
    enc = json.loads(enc_path.read_text())
    tiers["_encoder_baseline"] = {
        "produced_by": enc.get("produced_by"),
        "cohort_hash": enc.get("cohort_hash"),
        "seed": enc.get("seed"),
        "frame": enc.get("frame"),
        "primary_variant": enc.get("primary_variant"),
        "models": {},
    }

    for name, d in (enc.get("models") or {}).items():
        v = d.get("all_masked_PRIMARY") or next(iter(d.values()), {})
        outcomes = v.get("outcomes") or {}
        top1 = v.get("top1_distribution") or {}
        top_pred, top_n = (max(top1.items(), key=lambda kv: kv[1]) if top1 else ("unknown", 0))
        tiers["_encoder_baseline"]["models"][name] = {
            "n": v.get("n_cases"),
            "adequate": outcomes.get("ADEQUATE", 0),
            "adequate_pct_of_all": v.get("adequate_pct_of_all"),
            "distinct_predictions": v.get("n_distinct_top1"),
            "top_prediction": top_pred,
            "top_prediction_n": top_n,
            "outcomes": outcomes,
        }

out = ROOT / "results" / "model_tiers.json"
out.write_text(json.dumps(tiers, indent=2, sort_keys=False))
print(f"wrote results/model_tiers.json ({len(mc)} cross-model exposures, "
      f"{len(tiers.get('_encoder_baseline', {}).get('models', {}))} encoders)")
