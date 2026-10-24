{{ config(materialized='view') }}

with events as (
    select * from {{ ref('event_log') }}
)

select
    Case_ID,
    min(`Timestamp`)                                                             as visit_start,
    max(`Timestamp`)                                                             as visit_end,
    round(timestamp_diff(max(`Timestamp`), min(`Timestamp`), second) / 60.0, 1) as visit_minutes,
    count(*)                                                                     as event_count,
    countif(Is_Rework)                                                           as rework_count,
    countif(Is_Rework) > 0                                                       as has_loop_back,
    max(if(Is_Last_Event, Activity_Name, null))                                  as final_activity,
    any_value(Department)                                                        as department,
    any_value(Shift)                                                             as shift,
    any_value(Patient_Category)                                                  as patient_category
from events
group by Case_ID