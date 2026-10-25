"""
CareFlow - Process discovery on the dbt event_log (read from BigQuery).   (version 3)
Needs: pip install pm4py google-cloud-bigquery db-dtypes pandas
Login: gcloud auth application-default login
Output: output_bq/ folder (maps PNG + tables CSV)
Each step runs on its own: if one step fails, the error is printed and the next steps still run.
"""
import os
import traceback
from collections import Counter
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
 
 
def run_step(name, func):
    """Run one step. If it fails, print the error and go on."""
    try:
        func()
        print(f"[OK]     {name}")
    except Exception:
        print(f"[FAILED] {name}")
        traceback.print_exc()
 
 
def analyse(df):
    os.makedirs(OUT, exist_ok=True)
 
    # Make sure the column types are simple (text and UTC time)
    df = df.copy()
    for col in ["Case_ID", "Activity_Name", "Resource", "Shift", "Patient_Category"]:
        df[col] = df[col].astype(str)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], utc=True)
 
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
 
    dfg, start_acts, end_acts = pm4py.discover_dfg(log)
 
    def frequency_map():
        pm4py.save_vis_dfg(dfg, start_acts, end_acts, f"{OUT}/1_frequency_map.png")
 
    def performance_map():
        perf_dfg, ps, pe = pm4py.discover_performance_dfg(log)
        pm4py.save_vis_performance_dfg(perf_dfg, ps, pe, f"{OUT}/2_performance_map.png")
        rows = []
        for (a, b), secs in perf_dfg.items():
            if isinstance(secs, dict):
                secs = secs.get("mean", 0)
            rows.append({"from_step": a, "to_step": b,
                         "patients": dfg.get((a, b), 0),
                         "avg_wait_minutes": round(secs / 60, 1)})
        table = pd.DataFrame(rows).sort_values("avg_wait_minutes", ascending=False)
        table.to_csv(f"{OUT}/3_bottlenecks_avg_wait.csv", index=False)
        print("\nTop 5 slowest steps (avg minutes):")
        print(table.head(5).to_string(index=False))
 
    def main_paths():
        # Find the 5 most common journeys ourselves (pm4py's own top-k filter fails with pyarrow)
        journeys = {}
        for case, act in zip(log["case:concept:name"], log["concept:name"]):
            journeys.setdefault(case, []).append(act)
        counts = Counter(tuple(v) for v in journeys.values())
        top5 = {path for path, _ in counts.most_common(5)}
        keep = [case for case, v in journeys.items() if tuple(v) in top5]
        top_log = log[log["case:concept:name"].isin(keep)]
        t_dfg, t_s, t_e = pm4py.discover_dfg(top_log)
        pm4py.save_vis_dfg(t_dfg, t_s, t_e, f"{OUT}/4_main_paths_top5.png")
        print(f"Top-5 journeys cover {len(keep)} of {n_cases} visits")
 
    def variants_table():
        variants = pm4py.get_variants(log)
        vdf = pd.DataFrame([{"visits": cnt, "percent": round(cnt * 100 / n_cases, 1),
                             "path": " > ".join(v)} for v, cnt in variants.items()])
        vdf = vdf.sort_values("visits", ascending=False)
        vdf.to_csv(f"{OUT}/5_variants.csv", index=False)
        print(f"\nDifferent patient journeys: {len(vdf)}")
 
    def key_findings():
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
        print("Expected: 27962 events, 5000 visits, 1141 loop-backs (22.8%), about 108 vs 72 min")
 
    run_step("1 Frequency map", frequency_map)
    run_step("2 Performance map + bottleneck table", performance_map)
    run_step("3 Main paths (top 5)", main_paths)
    run_step("4 Variants table", variants_table)
    run_step("5 Key findings", key_findings)
 
    print(f"\nFiles in '{OUT}':", sorted(os.listdir(OUT)))
 
 
if __name__ == "__main__":
    analyse(load_events())