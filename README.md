# CareFlow - Clinical Pathway Process Mining

Infotact Solutions, Project 3. We use an ER patient event log to find where patients get stuck (bottlenecks) using process mining.

## Objectives
- Find where ER patients get stuck, instead of looking only at average wait time.
- Map each patient's full journey from an event log using process mining.
- Identify bottlenecks and loop-backs that increase waiting time.

## Data
- Synthetic dataset: 5,000 visits, 27,962 events, 18 unique journeys.
- data.csv: small Kaggle sample used to learn data cleaning. Learning sample only.
- simulator/: backup generator script.

## Key findings
- 22.8% of visits loop back from X-Ray to Return to Triage.
- Loop-back visits take about 108 min vs 72 min without loop-back (36 min extra).
- Slowest step: Doctor Consultation to Admission, about 52 min.

## Tech
Python, PM4Py, Graphviz, BigQuery, dbt.

## Folders
- pm4py_maps/: process mining maps and findings
- dbt_careflow/: dbt staging model and tests
- analysis/: stats check script
- simulator/: backup data generator

## Team
Fathima, Suraj, Omkar, Kumar

## Status
Week 1: data generation, BigQuery upload, PM4Py process maps, and dbt staging model (written, run and test in progress).