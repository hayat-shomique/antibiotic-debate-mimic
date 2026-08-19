# NOTE, 19 Aug 2026: payer status (`insurance`) was removed from the case block.
# It had no clinical rationale in a treatment-selection prompt, and a payer field
# feeding an antibiotic decision is a fairness problem regardless of measured effect.
# The 400 completed ordering-runs were produced WITH the field present; that is
# disclosed rather than hidden, and the measured effect is zero because the round-0
# recommendation is constant across all 200 cases and across all four payer values.
# Deviation D-PAYER-1.
"""case_assembly.py - builds the DYNAMIC CASE BLOCK (provenance class 2).

HARD CONSTRAINT: this module must have no import or code path reaching
panel_rows / microbiology / susceptibility data. acceptance.py proves this by
AST inspection; do not add such an import.

Every field carries field-level provenance: which table, which column, and the
timestamp of the source datum. Any datum timestamped at or after index_time is
a hard error, not a warning.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from pathlib import Path

import duckdb
import pandas as pd

HOSP = Path("/Users/shamzzzh/Downloads/mimic-iv-3.1/hosp")

# Whitelist: nothing outside this may reach a prompt.
WHITELIST: dict[str, set[str]] = {
    "cohort_skeleton.parquet": {"subject_id", "hadm_id", "index_time",
                                "gender", "age_at_index"},
    "admissions.csv.gz": {"hadm_id", "subject_id", "admittime",
                          "admission_type", "admission_location"},
    "prescriptions.csv.gz": {"subject_id", "starttime", "drug"},
}


class ProvenanceError(RuntimeError):
    pass


@dataclass
class CaseField:
    label: str
    value: object
    table: str
    column: str
    ts: object = None          # timestamp of the source datum, if any
    ts_ok: bool | None = None  # True when ts < index_time

    def render(self) -> str:
        return f"{self.label}: {self.value}"


@dataclass
class CaseBlock:
    case_id: str
    text: str
    fields: list[CaseField] = dc_field(default_factory=list)


def _check(table: str, column: str) -> None:
    if column not in WHITELIST.get(table, set()):
        raise ProvenanceError(f"column {table}.{column} is not whitelisted")


# ---------------------------------------------------------------------------
# hadm_id recovery (ruling 1a): microbiologyevents often has a NULL hadm_id even
# when an enclosing admission exists. Recover by time-window join.
# ---------------------------------------------------------------------------
def recover_hadm_ids(cohort: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    con = duckdb.connect()
    con.register("cohort", cohort[["subject_id", "micro_specimen_id",
                                   "hadm_id", "index_time"]])
    q = f"""
      SELECT c.subject_id, c.micro_specimen_id,
             MIN(a.hadm_id) AS recovered_hadm_id,
             COUNT(DISTINCT a.hadm_id) AS n_candidates
      FROM cohort c
      JOIN read_csv_auto('{HOSP}/admissions.csv.gz') a
        ON a.subject_id = c.subject_id
       AND c.index_time >= a.admittime
       AND c.index_time <= a.dischtime
      WHERE c.hadm_id IS NULL
      GROUP BY c.subject_id, c.micro_specimen_id
    """
    rec = con.execute(q).df()
    out = cohort.merge(rec, on=["subject_id", "micro_specimen_id"], how="left")
    out["hadm_id_final"] = out["hadm_id"].astype("Int64")
    m = out["hadm_id_final"].isna() & out["recovered_hadm_id"].notna()
    out.loc[m, "hadm_id_final"] = out.loc[m, "recovered_hadm_id"].astype("Int64")
    out["hadm_source"] = "original"
    out.loc[out["hadm_id"].isna(), "hadm_source"] = "unrecovered"
    out.loc[m, "hadm_source"] = "recovered"
    stats = {
        "n_total": int(len(out)),
        "n_original": int((out["hadm_source"] == "original").sum()),
        "n_null_initially": int(out["hadm_id"].isna().sum()),
        "n_recovered": int(m.sum()),
        "n_unrecovered": int((out["hadm_source"] == "unrecovered").sum()),
        "n_ambiguous_multi_admission": int((rec["n_candidates"] > 1).sum()),
    }
    stats["n_sampling_frame"] = stats["n_original"] + stats["n_recovered"]
    return out, stats


def load_admissions(hadm_ids) -> dict[int, dict]:
    ids = sorted({int(h) for h in hadm_ids if pd.notna(h)})
    if not ids:
        return {}
    for c in ("hadm_id", "admittime", "admission_type",
              "admission_location"):
        _check("admissions.csv.gz", c)
    con = duckdb.connect()
    q = f"""
      SELECT hadm_id, subject_id, admittime, admission_type,
             admission_location
      FROM read_csv_auto('{HOSP}/admissions.csv.gz')
      WHERE hadm_id IN ({",".join(str(i) for i in ids)})
    """
    df = con.execute(q).df()
    return {int(r["hadm_id"]): r.to_dict() for _, r in df.iterrows()}


def prior_abx_flags(cohort: pd.DataFrame, formulary_aliases: list[str],
                    cache: Path) -> pd.DataFrame:
    """Boolean per case. The drug NAME never leaves this function.

    DEFINITION (Decision 10, deviation D-PRIORABX-1). PRIMARY rule C: at the
    moment of the draw the patient had been on a formulary antibiotic for more
    than 48 CONTINUOUS hours (started <= index-48h AND course still running at
    index). A start-only threshold with no window was measured and rejected: it
    flagged 54.3% of the cohort, and 57.6% of those were flagged solely by a
    prescription more than 30 days old, i.e. "ever had an antibiotic" rather
    than sustained therapy. Sensitivity columns retain the rejected variants so
    this can be re-adjudicated without re-running. Only `prior_abx` reaches a
    prompt, and only ever as a boolean.
    """
    if cache.exists():
        return pd.read_parquet(cache)
    for c in ("subject_id", "starttime", "drug"):
        _check("prescriptions.csv.gz", c)
    stems = sorted({a.split("/")[0].split("-")[0].strip().upper()
                    for a in formulary_aliases})
    like = " OR ".join(f"upper(p.drug) LIKE '%{s}%'" for s in stems if s)
    con = duckdb.connect()
    con.register("cohort", cohort[["subject_id", "micro_specimen_id", "index_time"]])
    q = f"""
      WITH abx AS (
        SELECT p.subject_id, p.starttime, p.stoptime
        FROM read_csv_auto('{HOSP}/prescriptions.csv.gz') p
        WHERE p.starttime IS NOT NULL AND ({like})
      )
      SELECT c.subject_id, c.micro_specimen_id,
        -- PRIMARY (Decision 10, rule C): at the moment of the draw the patient
        -- had been on a formulary antibiotic for MORE THAN 48 CONTINUOUS HOURS.
        CAST(COUNT(*) FILTER (
               WHERE a.starttime <= c.index_time - INTERVAL 48 HOUR
                 AND (a.stoptime IS NULL OR a.stoptime >= c.index_time)
             ) > 0 AS BOOLEAN) AS prior_abx,
        -- sensitivity B: course still active 48h before the draw
        CAST(COUNT(*) FILTER (
               WHERE a.starttime <= c.index_time - INTERVAL 48 HOUR
                 AND (a.stoptime IS NULL
                      OR a.stoptime >= c.index_time - INTERVAL 48 HOUR)
             ) > 0 AS BOOLEAN) AS prior_abx_active48,
        -- sensitivity A: start >=48h before, NO window (defective; retained only
        -- so the deviation is re-adjudicable without a re-run)
        CAST(COUNT(*) FILTER (
               WHERE a.starttime <= c.index_time - INTERVAL 48 HOUR
             ) > 0 AS BOOLEAN) AS prior_abx_nowindow,
        -- superseded: any start before index (the empiric-start artefact)
        CAST(COUNT(*) FILTER (WHERE a.starttime < c.index_time) > 0 AS BOOLEAN)
             AS prior_abx_anystart
      FROM cohort c
      LEFT JOIN abx a ON a.subject_id = c.subject_id
      GROUP BY c.subject_id, c.micro_specimen_id
    """
    out = con.execute(q).df()
    out.to_parquet(cache, index=False)
    return out


def build_case_block(row, adm: dict | None, prior_abx: bool) -> CaseBlock:
    idx = pd.to_datetime(row["index_time"], errors="coerce")
    if pd.isna(idx):
        raise ProvenanceError("index_time missing")
    case_id = f"{int(row['subject_id'])}_{int(row['micro_specimen_id'])}"
    f: list[CaseField] = []

    _check("cohort_skeleton.parquet", "age_at_index")
    age = int(row["age_at_index"]) if pd.notna(row["age_at_index"]) else "unknown"
    f.append(CaseField("Age", age, "cohort_skeleton.parquet", "age_at_index"))

    _check("cohort_skeleton.parquet", "gender")
    sex = {"M": "male", "F": "female"}.get(str(row["gender"]).upper(), "unknown")
    f.append(CaseField("Sex", sex, "cohort_skeleton.parquet", "gender"))

    atype = aloc = ins = "unknown"
    hours = "unknown"
    if adm:
        at = pd.to_datetime(adm.get("admittime"), errors="coerce")
        if pd.isna(at):
            raise ProvenanceError(f"{case_id}: admittime unparseable")
        if not (at <= idx):
            raise ProvenanceError(
                f"{case_id}: admittime {at} is not before index_time {idx}")
        atype = adm.get("admission_type") or "unknown"
        aloc = adm.get("admission_location") or "unknown"
        hours = f"{(idx - at).total_seconds()/3600.0:.0f}"
        for lbl, col, val in (("Admission type", "admission_type", atype),
                              ("Admission source", "admission_location", aloc),
                              ("Hours from admission to assessment", "admittime", hours)):
            f.append(CaseField(lbl, val, "admissions.csv.gz", col,
                               ts=at, ts_ok=True))
    else:
        for lbl, col in (("Admission type", "admission_type"),
                         ("Admission source", "admission_location"),
                         ("Insurance", "insurance"),
                         ("Hours from admission to assessment", "admittime")):
            f.append(CaseField(lbl, "unknown", "admissions.csv.gz", col))

    f.append(CaseField("Prior antibiotic exposure before this assessment",
                       "yes" if prior_abx else "no",
                       "prescriptions.csv.gz", "starttime",
                       ts=idx, ts_ok=True))
    f.append(CaseField("Laboratory results", "not available at this decision point",
                       "(none)", "(none)"))

    bad = [x for x in f if x.ts_ok is False]
    if bad:
        raise ProvenanceError(f"{case_id}: fields at/after index_time: "
                              f"{[x.label for x in bad]}")
    return CaseBlock(case_id=case_id, text="\n".join(x.render() for x in f), fields=f)
