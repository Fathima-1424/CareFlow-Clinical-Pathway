import os
import pandas as pd
import pm4py
 
INPUT_CSV = 'careflow_raw_events_5000_visits.csv'
OUT = 'output'
os.makedirs(OUT, exist_ok=True)
 
# 1. LOAD + CLEAN

df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()
for col in ['case_id', 'activity', 'resource']:
    df[col] = df[col].astype(str).str.strip()
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.dropna(subset=['case_id', 'activity', 'timestamp'])
df = df.drop_duplicates()
df = df.sort_values(['case_id', 'timestamp'], kind='stable')
 
# Visit-level info (shift, patient category) for later analysis
case_info = df.groupby('case_id')[['shift', 'patient_category']].first()
 
df = df.rename(columns={'case_id': 'case:concept:name', 'activity': 'concept:name',
                        'timestamp': 'time:timestamp', 'resource': 'org:resource'})
log = pm4py.format_dataframe(df, case_id='case:concept:name',
                             activity_key='concept:name',
                             timestamp_key='time:timestamp')
 
n_cases = log['case:concept:name'].nunique()
print(f"Events: {len(log)} | Visits: {n_cases}")

# 2. MAP 1 - FREQUENCY MAP (how many patients take each path)

dfg, start_acts, end_acts = pm4py.discover_dfg(log)
pm4py.save_vis_dfg(dfg, start_acts, end_acts, f'{OUT}/1_frequency_map.png')
 
# 3. MAP 2 - PERFORMANCE MAP (average time between steps)

perf_dfg, ps, pe = pm4py.discover_performance_dfg(log)
pm4py.save_vis_performance_dfg(perf_dfg, ps, pe, f'{OUT}/2_performance_map.png')
 
# Bottleneck table: average wait for every step-to-step transition
rows = []
for (a, b), secs in perf_dfg.items():
    if isinstance(secs, dict):      
        secs = secs.get('mean', 0)
    rows.append({'from_step': a, 'to_step': b,
                 'patients': dfg.get((a, b), 0),
                 'avg_wait_minutes': round(secs / 60, 1)})
bottlenecks = pd.DataFrame(rows).sort_values('avg_wait_minutes', ascending=False)
bottlenecks.to_csv(f'{OUT}/3_bottlenecks_avg_wait.csv', index=False)
print("\nTop 5 slowest transitions (avg wait, min):")
print(bottlenecks.head(5).to_string(index=False))
 

# 4. MAP 3 - MAIN PATHS ONLY (top 5 variants = easy to read)

top_log = pm4py.filter_variants_top_k(log, 5)
t_dfg, t_s, t_e = pm4py.discover_dfg(top_log)
pm4py.save_vis_dfg(t_dfg, t_s, t_e, f'{OUT}/4_main_paths_top5.png')
 

# 5. MAP 4 - PROCESS MODEL (Petri net, inductive miner)

net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.2)
pm4py.save_vis_petri_net(net, im, fm, f'{OUT}/5_process_model_petri_net.png')

# 6. VARIANTS (the different journeys patients take)

variants = pm4py.get_variants(log)
vrows = [{'visits': cnt, 'percent': round(cnt * 100 / n_cases, 1),
          'path': ' > '.join(v)} for v, cnt in variants.items()]
vdf = pd.DataFrame(vrows).sort_values('visits', ascending=False)
vdf.to_csv(f'{OUT}/6_variants.csv', index=False)
print(f"\nDifferent patient journeys: {len(vdf)}")
print(vdf.head(5)[['visits', 'percent', 'path']].to_string(index=False))
 

# 7. KEY FINDINGS (report / demo)

loop_cases = log[log['concept:name'] == 'Return to Triage']['case:concept:name'].nunique()
dur = pm4py.get_all_case_durations(log)
dur_min = pd.Series(dur) / 60
case_dur = log.groupby('case:concept:name')['time:timestamp'].agg(lambda s: (s.max() - s.min()).total_seconds() / 60)
case_dur = case_dur.to_frame('minutes').join(case_info)
case_dur['has_loop'] = case_dur.index.isin(
    log[log['concept:name'] == 'Return to Triage']['case:concept:name'])
 
print("\n===== KEY FINDINGS =====")
print(f"Visits with loop-back (Return to Triage): {loop_cases} ({loop_cases*100/n_cases:.1f}%)")
print(f"Average visit duration: {case_dur['minutes'].mean():.0f} min")
print("Average duration WITH loop-back   :", round(case_dur[case_dur.has_loop]['minutes'].mean()), "min")
print("Average duration WITHOUT loop-back:", round(case_dur[~case_dur.has_loop]['minutes'].mean()), "min")
print("\nAverage duration by shift (min):")
print(case_dur.groupby('shift')['minutes'].mean().round(0).to_string())
print("\nAverage duration by patient category (min):")
print(case_dur.groupby('patient_category')['minutes'].mean().round(0).to_string())
 
summary = pd.DataFrame({
    'metric': ['visits', 'loop_back_visits', 'loop_back_percent', 'avg_visit_minutes',
               'avg_minutes_with_loop', 'avg_minutes_without_loop'],
    'value': [n_cases, loop_cases, round(loop_cases * 100 / n_cases, 1),
              round(case_dur['minutes'].mean(), 1),
              round(case_dur[case_dur.has_loop]['minutes'].mean(), 1),
              round(case_dur[~case_dur.has_loop]['minutes'].mean(), 1)]})
summary.to_csv(f'{OUT}/7_key_findings.csv', index=False)
print(f"\nAll files saved in the '{OUT}' folder.")