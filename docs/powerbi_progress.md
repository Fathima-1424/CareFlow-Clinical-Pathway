# Power BI Dashboard Progress

Source: BigQuery project polished-trail-511415-r4, dbt dataset careflow_dbt.
Tables used: fct_visits (one row per visit), event_log (one row per event), int_transition_times (average wait between steps).

## Done
- Power BI connected to the BigQuery dbt tables.
- Relationship fct_visits[Case_ID] to event_log[Case_ID], one to many, single direction.
- First KPI cards: total visits, total events, loop-back visits, loop-back %.
- Bar chart of average transition time by step.

## In progress
- Page 1 overview: 5 KPI cards, loop-back vs no loop-back chart, how visits end, shift and patient category slicers.
- Page 2 bottlenecks: slowest steps, heatmap by shift and patient category.
- Page 3 journeys and Page 4 time and resources.

## Numbers the dashboard must match
- 5,000 visits and 27,962 events.
- 22.8% of visits loop back to Triage.
- About 108 min with loop-back vs about 72 min without.
- Slowest step: Doctor Consultation to Admission, about 52 min.
- 18 unique patient journeys.

## Next
Finish the 4 pages, check the numbers above, add screenshots to docs, and update the README.