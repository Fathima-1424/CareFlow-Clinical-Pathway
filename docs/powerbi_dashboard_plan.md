# Power BI Dashboard Plan

Source: BigQuery project polished-trail-511415-r4, dataset careflow_dbt.
Tables: fct_visits (one row per visit), event_log (one row per event), int_transition_times (average wait between steps).

## Relationship
fct_visits[Case_ID] to event_log[Case_ID], one to many, single direction.
This lets slicers on fct_visits filter both tables.

## Page 1: Overview
KPI cards:
- Total visits (expected 5,000)
- Loop-back % (expected 22.8%)
- Average visit minutes (expected about 80)
- Extra minutes from loop-back (expected about 36)

Charts:
- Column chart: average visit time with loop-back vs no loop-back (about 108 vs 72 min)
- Bar chart: slowest steps by average wait, top 8 (Doctor Consultation to Admission at the top, about 52 min)
- Donut chart: how visits end (Discharge or Admission)

Slicers: shift, patient_category.

## Page 2: Process map and bottlenecks
- PM4Py main paths image: pm4py_maps/output_bq/4_main_paths_top5.png
- PM4Py performance map image: pm4py_maps/output_bq/2_performance_map.png
- Table of int_transition_times: from_step, to_step, transitions, avg_minutes
- Insight: 22.8% of visits loop back to Triage and take about 36 minutes longer.

## Calculated columns
Visit type (fct_visits) = IF(fct_visits[has_loop_back], "With loop-back", "No loop-back")
Step (event_log) = IF(ISBLANK(event_log[Previous_Activity]), BLANK(), event_log[Previous_Activity] & " > " & event_log[Activity_Name])

## Measures
Total Visits = DISTINCTCOUNT(fct_visits[Case_ID])
Loop-back Visits = CALCULATE(DISTINCTCOUNT(fct_visits[Case_ID]), fct_visits[has_loop_back] = TRUE())
Loop-back % = DIVIDE([Loop-back Visits], [Total Visits])
Avg Visit Minutes = AVERAGE(fct_visits[visit_minutes])
Avg Minutes With Loop-back = CALCULATE(AVERAGE(fct_visits[visit_minutes]), fct_visits[has_loop_back] = TRUE())
Avg Minutes No Loop-back = CALCULATE(AVERAGE(fct_visits[visit_minutes]), fct_visits[has_loop_back] = FALSE())
Extra Minutes From Loop-back = [Avg Minutes With Loop-back] - [Avg Minutes No Loop-back]
Avg Wait Between Steps = AVERAGE(event_log[Minutes_Since_Previous])

## Number check
With all slicers cleared, the dashboard must show 5,000 visits and 22.8% loop-back. These match the dbt tables and the PM4Py results.
Shift and patient category do not change the average visit time much, so we do not claim differences between them.