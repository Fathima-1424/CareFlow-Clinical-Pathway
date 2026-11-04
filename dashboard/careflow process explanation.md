# CareFlow – ER Patient Flow Dashboard

## 1. Project overview

The CareFlow dashboard is part of the **CareFlow: Clinical Pathway Process Mining** project. It is designed to help understand how patients move through the Emergency Room (ER) workflow, identify delays between activities, and monitor rework/loop-back patterns.

The analysis uses the CareFlow event data and the prepared analytical tables in the project. The report is built in **Microsoft Power BI Desktop using native Power BI visuals**. The separate HTML dashboard is a browser-based reference/companion and is not itself a Power BI report.

## 2. Work completed

1. Opened the existing CareFlow Power BI report (`.pbix`) in Power BI Desktop.
2. Reviewed the available CareFlow data tables, including `event_log`, `fct_visits`, and `int_transition_times`.
3. Used the CareFlow data model as the basis for the report instead of trying to import the local HTML file through Power BI's Web connector.
4. Recreated the CareFlow dashboard layout with native Power BI report visuals.
5. Organized the report around patient volume, loop-back/rework, visit duration, process bottlenecks, and patient outcomes.
6. Saved the Power BI report in `.pbix` format so it can be reopened and edited in Power BI Desktop.

## 3. Dashboard sections and purpose

| Section / visual | What it communicates |
|---|---|
| Total Visits (KPI card) | Number of patient visits represented in the selected data. |
| Total Events (KPI card) | Number of recorded activity events. |
| Loop-back percentage (KPI card) | Share of visits that contain a return/rework pattern. |
| Average visit time (KPI card) | Average elapsed time per visit, based on the report's visit-time calculation. |
| Average visit time comparison | Compares visits with and without a loop-back. |
| Slowest steps / bottlenecks | Highlights transitions with longer average waiting times. |
| How visits end | Shows the split between discharge and admission outcomes. |
| Loop-back by shift | Helps compare rework across Morning, Afternoon, and Night shifts. |
| Filters / slicers | Allows the report to be explored by available dimensions such as shift, patient category, and doctor, where included in the report. |

> Confirm that every listed visual is present and its measure is correct in the saved `.pbix` before treating this table as a final inventory. Remove or edit any item that was not included in the final report.

## 4. Data tables used

- **`event_log`** – event-level patient pathway records used to understand the sequence of activities.
- **`fct_visits`** – visit-level data used for visit counts, outcomes, and visit-level analysis.
- **`int_transition_times`** – transition-level data used to analyze elapsed/waiting time between activities.

The report should be refreshed and checked against the latest project data before presenting results. If any data is embedded or imported as a snapshot, it will not update automatically until the source is refreshed.

## 5. How to open the dashboard

1. Open the `.pbix` report in **Power BI Desktop**.
2. If Power BI asks to refresh the data, verify the configured source and credentials before refreshing.
3. Use the report page tabs and slicers to explore the dashboard.
4. Save the report after any changes.

## 6. HTML reference dashboard

The file `careflow_dashboard.html` is a separate HTML/JavaScript dashboard that can be opened in a web browser. It provides a reference for the CareFlow layout and interactions. It cannot be opened as a native `.pbix` report by using **Get Data → Web page** with a `file:///` local path. The Power BI report is the `.pbix` file; keep the two deliverables clearly identified.

## 7. Validation before sharing or committing

- [ ] The `.pbix` file opens successfully in Power BI Desktop.
- [ ] KPI values match the selected CareFlow data and filters.
- [ ] Charts respond correctly to the available slicers.
- [ ] Waiting-time calculations use the intended units (minutes) and aggregation.
- [ ] Discharge and admission counts reconcile with the underlying visit data.
- [ ] The report has been saved after the final changes.
- [ ] No credentials, private keys, or confidential patient information are included in the repository.


## 8. My contribution

I worked on the CareFlow process-mining and dashboard side. I reviewed the patient event/visit data, used the prepared analytical tables to understand patient flow and transition delays, and developed the dashboard presentation in Power BI to make key workflow measures and bottlenecks easier to explore. The dashboard is intended to support discussion of process performance and possible improvement areas; findings should be interpreted in the context of the project's dataset and business rules.
