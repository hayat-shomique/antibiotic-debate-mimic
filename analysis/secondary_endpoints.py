#!/usr/bin/env python
"""Tingting's remaining endpoints: 3, 6, 7, 8. Computed, then interpreted honestly.

She specified a hierarchy and put four measures at the bottom of it:

  3. Time to appropriate therapy   "where timestamps permit it"
  6. Treatment failure             "if these can be defined reliably in your MIMIC-IV cohort"
  7. Mortality 7/14/30 day         "useful as a secondary... but I'd be cautious about
                                    interpreting it causally"
  8. Length of stay / ICU-free     "again with substantial confounding"

Every one carries a condition. Computing them is how you find out whether the condition is
met - and reporting a confounded number alongside the reason it is confounded is a stronger
answer than leaving the row blank. That is the whole point of her hierarchy: the endpoints
nearest the decision carry the argument, and the distal ones are shown to demonstrate why
they cannot.

Read-only against ~/Downloads/mimic-iv-3.1. Aggregates only.
"""
from __future__ import annotations
import json, glob
import os
from pathlib import Path
import duckdb, pandas as pd

# This script reads the run directory, so it is executed from a copy inside it. That made
# __file__ an unreliable way to find the repository, which is why the repo copy of these
# endpoints went missing. Both locations are resolved explicitly.
ROOT = Path(os.environ.get("BRAIN_DIR") or Path(__file__).resolve().parent)
REPO = Path(os.environ.get("BRAIN_REPO")
            or "/Users/shamzzzh/Desktop/antibiotic-debate-mimic")
MIMIC = Path.home() / "Downloads" / "mimic-iv-3.1"
HOSP, ICU = MIMIC / "hosp", MIMIC / "icu"
con = duckdb.connect()
OUT = {}


def cohort_200() -> pd.DataFrame:
    """The 200 cases actually run, with their index times."""
    import debate_run as DR
    panel = DR.load_panel(); frame, _ = DR.build_frame()
    sel = DR.select(frame, 200, sample=True, panel=panel)
    keep = [c for c in ["subject_id", "hadm_id", "micro_specimen_id", "index_time"]
            if c in sel.columns]
    df = sel[keep].copy()
    df["case_id"] = (df["subject_id"].astype(int).astype(str) + "_" +
                     df["micro_specimen_id"].astype(int).astype(str))
    return df


def final_positions() -> pd.DataFrame:
    """Each case's final recommendation and whether it was adequate."""
    rs = [json.loads(l) for l in open(ROOT / "runs" / "debate_20260818.jsonl") if l.strip()]
    rs = [r for r in rs if r.get("kind") == "full" and r.get("ordering") == "A-first"]
    return pd.DataFrame([{"case_id": r["case_id"], "final_drug": r["final_A"],
                          "final_outcome": r["final_A_outcome"],
                          "round0_drug": r["round0_drug"],
                          "round0_outcome": r["round0_outcome"]} for r in rs])


def main():
    print("=" * 78)
    print("  TINGTING'S ENDPOINTS 3, 6, 7, 8, the deprioritised tier, computed")
    print("=" * 78)
    coh = cohort_200(); fin = final_positions()
    df = coh.merge(fin, on="case_id", how="inner")
    con.register("coh", df)
    print(f"\n  {len(df)} cases with a final recommendation and an index time")
    n_hadm = int(df["hadm_id"].notna().sum())
    print(f"  {n_hadm}/{len(df)} carry a linked hospital admission id "
          f"({100*n_hadm/len(df):.0f}%), admission-level endpoints are limited to these")

    # ---------------- 7. MORTALITY ----------------
    print("\n" + "-" * 78)
    print("  ENDPOINT 7, mortality at 7, 14 and 30 days from the index culture")
    pat = con.execute(f"""
        SELECT subject_id, dod FROM read_csv_auto('{HOSP}/patients.csv.gz')
    """).df()
    m = df.merge(pat, on="subject_id", how="left")
    m["index_time"] = pd.to_datetime(m["index_time"])
    m["dod"] = pd.to_datetime(m["dod"])
    m["days_to_death"] = (m["dod"] - m["index_time"]).dt.total_seconds() / 86400
    OUT["mortality"] = {}
    for d in (7, 14, 30):
        dead = int(((m["days_to_death"] >= 0) & (m["days_to_death"] <= d)).sum())
        OUT["mortality"][f"{d}d"] = {"deaths": dead, "n": len(m),
                                     "rate": round(100 * dead / len(m), 1)}
        print(f"    {d:2d}-day mortality   {dead:3d}/{len(m)} = {100*dead/len(m):5.1f}%")
    # stratified by whether the model's final recommendation was adequate
    print("\n    Split by whether the agent's FINAL recommendation was adequate:")
    for lab, sub in [("adequate", m[m.final_outcome == "ADEQUATE"]),
                     ("not adequate", m[m.final_outcome != "ADEQUATE"])]:
        if len(sub):
            d30 = int(((sub["days_to_death"] >= 0) & (sub["days_to_death"] <= 30)).sum())
            print(f"      {lab:14s} n={len(sub):3d}   30-day mortality "
                  f"{d30}/{len(sub)} = {100*d30/len(sub):5.1f}%")
    OUT["mortality"]["note"] = ("The agent's recommendation was never given to anyone. Any "
                                "difference across these strata reflects which patients get "
                                "which organisms, not the effect of a recommendation.")

    # ---------------- 8. LOS and ICU ----------------
    print("\n" + "-" * 78)
    print("  ENDPOINT 8, length of stay and ICU exposure")
    adm = con.execute(f"""
        SELECT hadm_id, subject_id, admittime, dischtime, hospital_expire_flag
        FROM read_csv_auto('{HOSP}/admissions.csv.gz')
    """).df()
    icu = con.execute(f"""
        SELECT hadm_id, SUM(los) AS icu_los, COUNT(*) AS n_icu_stays
        FROM read_csv_auto('{ICU}/icustays.csv.gz') GROUP BY hadm_id
    """).df()
    l = df.dropna(subset=["hadm_id"]).copy()
    l["hadm_id"] = l["hadm_id"].astype("int64")
    l = l.merge(adm, on="hadm_id", how="left", suffixes=("", "_a")).merge(icu, on="hadm_id", how="left")
    l["los_days"] = (pd.to_datetime(l["dischtime"]) - pd.to_datetime(l["admittime"])).dt.total_seconds() / 86400
    ok = l["los_days"].notna()
    print(f"    linked admissions: {int(ok.sum())}/{len(df)}")
    if ok.sum():
        print(f"    hospital length of stay   median {l.loc[ok,'los_days'].median():.1f} d   "
              f"IQR {l.loc[ok,'los_days'].quantile(.25):.1f}-{l.loc[ok,'los_days'].quantile(.75):.1f}")
        ni = int(l["icu_los"].notna().sum())
        print(f"    of those, {ni} had an ICU stay; median ICU LOS "
              f"{l['icu_los'].median():.1f} d" if ni else "    no ICU stays linked")
        print(f"    in-hospital death flag    {int(l['hospital_expire_flag'].fillna(0).sum())}/{int(ok.sum())}")
        OUT["los"] = {"n_linked": int(ok.sum()), "median_los_days": round(float(l.loc[ok,'los_days'].median()), 1),
                      "n_with_icu": int(l["icu_los"].notna().sum())}

    # ---------------- 3. TIME TO APPROPRIATE THERAPY ----------------
    print("\n" + "-" * 78)
    print("  ENDPOINT 3, time to appropriate therapy, observed vs counterfactual")
    import debate_run as DR
    panel = DR.load_panel()
    subj = tuple(int(x) for x in df["subject_id"].unique())
    rx = con.execute(f"""
        SELECT subject_id, hadm_id, drug, starttime
        FROM read_csv_auto('{HOSP}/prescriptions.csv.gz')
        WHERE subject_id IN {subj} AND starttime IS NOT NULL
    """).df()
    print(f"    {len(rx):,} prescription rows for the {len(subj)} patients in the cohort")
    rx["canon"] = rx["drug"].map(DR.BS.canon_drug)
    rx = rx.dropna(subset=["canon"])
    rx["starttime"] = pd.to_datetime(rx["starttime"])
    print(f"    {len(rx):,} map to the 17-drug formulary")

    recs = []
    for _, r in df.iterrows():
        idx = pd.to_datetime(r["index_time"])
        psub = DR.pathogenic_panel(panel, int(r["micro_specimen_id"]))
        mine = rx[rx.subject_id == int(r["subject_id"])]
        # observed: first administered drug the panel calls adequate, at or after index
        after = mine[(mine.starttime >= idx - pd.Timedelta(hours=24))]
        first_active = None
        for _, p in after.sort_values("starttime").iterrows():
            if DR.score(p["canon"], psub)["outcome"] == "ADEQUATE":
                first_active = (p["starttime"] - idx).total_seconds() / 3600
                break
        recs.append({"case_id": r["case_id"],
                     "observed_hours_to_active": first_active,
                     "agent_would_be_active": r["final_outcome"] == "ADEQUATE",
                     "agent_hours": 0.0 if r["final_outcome"] == "ADEQUATE" else None})
    t = pd.DataFrame(recs)
    obs = t["observed_hours_to_active"].dropna()
    print(f"\n    observed: {len(obs)}/{len(t)} cases reached an active drug in the record")
    if len(obs):
        print(f"      median {obs.median():.1f} h   IQR {obs.quantile(.25):.1f}-{obs.quantile(.75):.1f} h")
    both = t[(t["observed_hours_to_active"].notna()) & (t["agent_would_be_active"])]
    if len(both):
        earlier = int((both["observed_hours_to_active"] > 0).sum())
        print(f"    counterfactual: the agent's choice is active at t=0 by construction, so it")
        print(f"      would be earlier in {earlier}/{len(both)} = {100*earlier/len(both):.1f}% of the")
        print(f"      cases where BOTH are defined (n={len(both)})")
        OUT["time_to_therapy"] = {"n_observed": int(len(obs)),
                                  "median_hours_observed": round(float(obs.median()), 1) if len(obs) else None,
                                  "n_both_defined": int(len(both)),
                                  "agent_earlier_pct": round(100 * earlier / len(both), 1)}
    OUT.setdefault("time_to_therapy", {})["note"] = (
        "The comparison is structurally unfair to the clinician: the agent is asked once, at "
        "the index moment, and its answer is timeless. A clinician prescribes, observes, and "
        "revises. 'The agent would have been faster' is an artefact of being asked at t=0, "
        "not a finding.")

    # ---------------- 6. TREATMENT FAILURE ----------------
    print("\n" + "-" * 78)
    print("  ENDPOINT 6, treatment failure, tested against her condition")
    micro = con.execute(f"""
        SELECT subject_id, micro_specimen_id, charttime, spec_type_desc, org_name
        FROM read_csv_auto('{HOSP}/microbiologyevents.csv.gz')
        WHERE subject_id IN {subj} AND org_name IS NOT NULL
    """).df()
    micro["charttime"] = pd.to_datetime(micro["charttime"])
    persist = 0
    for _, r in df.iterrows():
        idx = pd.to_datetime(r["index_time"])
        later = micro[(micro.subject_id == int(r["subject_id"])) &
                      (micro.charttime > idx + pd.Timedelta(hours=48)) &
                      (micro.charttime <= idx + pd.Timedelta(days=14)) &
                      (micro.spec_type_desc.astype(str).str.contains("BLOOD", case=False, na=False))]
        persist += int(len(later) > 0)
    print(f"    persistent positive blood culture, 48 h to 14 d after index: "
          f"{persist}/{len(df)} = {100*persist/len(df):.1f}%")
    OUT["treatment_failure"] = {"persistent_bacteraemia": persist, "n": len(df),
                                "rate": round(100 * persist / len(df), 1),
                                "note": ("Persistence is definable. 'Failure' is not: it needs "
                                         "attribution to the therapy given, and the therapy "
                                         "given was chosen by a clinician who saw information "
                                         "the agent never had. Reported as a cohort "
                                         "characteristic, never as an outcome of a recommendation.")}

    blob = json.dumps(OUT, indent=2, default=str)
    Path(ROOT / "secondary_endpoints.json").write_text(blob)
    # Also into the repository. These are aggregates over 200 specimens with no case-level rows,
    # so they carry nothing the data use agreement protects, and a supervisor should be able to
    # check four of her own endpoints without the run directory. The status file said these were
    # NOT RUN for a day after they were run, purely because it lived where the file did not.
    repo = REPO / "results"
    if repo.is_dir():
        (repo / "secondary_endpoints.json").write_text(blob + "\n")
    print("\n" + "=" * 78)
    print("  -> secondary_endpoints.json, and results/secondary_endpoints.json")
    print("  All four computed. Each carries the reason it stays a secondary.")


if __name__ == "__main__":
    main()
