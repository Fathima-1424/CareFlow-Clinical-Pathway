Algorithm Check: process discovery on the dbt event log

Goal: prove that PM4Py can build a directed graph (process map) from our cleaned event log and show the main paths patients take through the ER.

Data source

1.BigQuery view careflow_dbt.event_log, created by dbt from the raw table careflow.raw_events.
2.27,962 events, 5,000 visits, 18 different patient journeys.
3.Columns used: Case_ID, Activity_Name, Timestamp (plus Resource, Shift, Patient_Category).

What we ran

pm4py_maps/process_discovery_bq.py reads event_log from BigQuery and builds the maps.
Output folder: pm4py_maps/output_bq/
1_frequency_map.png: how many patients take each path
2_performance_map.png: average time between steps
3_bottlenecks_avg_wait.csv: waiting time for every step-to-step transition
4_main_paths_top5.png: the 5 most common journeys only (easy to read)
5_variants.csv: all 18 journeys with counts
6_key_findings.csv: summary numbers

Result

PM4Py builds a directed graph from BigQuery data
Every visit starts with Registration	
Every visit ends with Discharge or Admission	
Time never goes backwards inside a visit	
Loop-back (X-Ray to Return to Triage) is visible	
Visits with a loop-back
Visits without a loop-back	
Slowest step	

Cross-check

The numbers from BigQuery (dbt + PM4Py) are the same as the numbers we got earlier from the CSV file. This shows that the pipeline (generator, BigQuery, dbt, PM4Py) does not change the data.

Limits

1.The data is synthetic and very clean.
2.Waiting time is almost the same in all shifts, so we do not claim a shift effect.
3.About 28% of visits have Treatment before Doctor Consultation. We are checking whether this is on purpose.