"""
CareFlow - Process discovery on the dbt event_log (read from BigQuery).
Needs: pip install pm4py google-cloud-bigquery db-dtypes pandas
Login: gcloud auth application-default login
Output: output_bq/ folder (maps PNG + tables CSV)
"""
import os
import pandas as pd
import pm4py
 
PROJECT = "polished-trail-511415-r4"
EVENT_LOG_TABLE = "polished-trail-511415-r4.careflow_dbt.event_log"
LOCATION = "asia-south1"
OUT = "output_bq"
 
 
def load_events():
    """Read the event_log view that dbt created in BigQuery."""
    from google.cloud import bigquery
    client = bigquery.Client(project=PROJECT, location=LOCATION)
    sql = f"""
        SELECT Case_ID, Activity_Name, `Timestamp`, Resource, Shift, Patient_Category
        FROM `{EVENT_LOG_TABLE}`
        ORDER BY Case_ID, `Timestamp`, Event_Number
    """
    return client.query(sql).to_dataframe(create_bqstorage_client=False)
 
 
def analyse(df):
    os.makedirs(OUT, exist_ok=True)
 
    # 1. Rename to PM4Py column names
    df = df.rename(columns={
        "Case_ID": "case:concept:name",
        "Activity_Name": "concept:name",
        "Timestamp": "time:timestamp",
        "Resource": "org:resource"})
    log = pm4py.format_dataframe(df, case_id="case:concept:name",
                                 activity_key="concept:name",
                                 timestamp_key="time:timestamp")
    n_cases = log["case:concept:name"].nunique()
    print(f"Events: {len(log)} | Visits: {n_cases}")
 
    # 2. Frequency map (how many patients take each path)
    dfg, start_acts, end_acts = pm4py.discover_dfg(log)
    pm4py.save_vis_dfg(dfg, start_acts, end_acts, f"{OUT}/1_frequency_map.png")
 
    # 3. Performance map (average time between steps) + bottleneck table
    perf_dfg, ps, pe = pm4py.discover_performance_dfg(log)
    pm4py.save_vis_performance_dfg(perf_dfg, ps, pe, f"{OUT}/2_performance_map.png")
    rows = []
    for (a, b), secs in perf_dfg.items():
        if isinstance(secs, dict):
            secs = secs.get("mean", 0)
        rows.append({"from_step": a, "to_step": b,
                     "patients": dfg.get((a, b), 0),
                     "avg_wait_minutes": round(secs / 60, 1)})
    bottlenecks = pd.DataFrame(rows).sort_values("avg_wait_minutes", ascending=False)
    bottlenecks.to_csv(f"{OUT}/3_bottlenecks_avg_wait.csv", index=False)
    print("\nTop 5 slowest steps (avg minutes):")
    print(bottlenecks.head(5).to_string(index=False))
 
    # 4. Main paths only (top 5 journeys)
    top_log = pm4py.filter_variants_top_k(log, 5)
    t_dfg, t_s, t_e = pm4py.discover_dfg(top_log)
    pm4py.save_vis_dfg(t_dfg, t_s, t_e, f"{OUT}/4_main_paths_top5.png")
 
    # 5. All patient journeys (variants)
    variants = pm4py.get_variants(log)
    vdf = pd.DataFrame([{"visits": cnt, "percent": round(cnt * 100 / n_cases, 1),
                         "path": " > ".join(v)} for v, cnt in variants.items()])
    vdf = vdf.sort_values("visits", ascending=False)
    vdf.to_csv(f"{OUT}/5_variants.csv", index=False)
    print(f"\nDifferent patient journeys: {len(vdf)}")
 
    # 6. Key findings (same numbers as the CSV version should come out)
    loop_ids = set(log.loc[log["concept:name"] == "Return to Triage", "case:concept:name"])
    dur = log.groupby("case:concept:name")["time:timestamp"].agg(
        lambda s: (s.max() - s.min()).total_seconds() / 60)
    with_loop = dur[dur.index.isin(loop_ids)].mean()
    without_loop = dur[~dur.index.isin(loop_ids)].mean()
    findings = pd.DataFrame({
        "metric": ["events", "visits", "loop_back_visits", "loop_back_percent",
                   "avg_minutes_with_loop", "avg_minutes_without_loop"],
        "value": [len(log), n_cases, len(loop_ids), round(len(loop_ids) * 100 / n_cases, 1),
                  round(with_loop, 1), round(without_loop, 1)]})
    findings.to_csv(f"{OUT}/6_key_findings.csv", index=False)
    print("\n===== KEY FINDINGS (from BigQuery) =====")
    print(findings.to_string(index=False))
    print("\nExpected from the CSV version: 27962 events, 5000 visits, 1141 loop-backs (22.8%), 108 vs 72 min")
    print(f"All files saved in the '{OUT}' folder.")
 
 
if __name__ == "__main__":
    analyse(load_events())