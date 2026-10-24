{{ config(materialized='view') }}

with events as (
    select * from {{ ref('stg_ehr_events') }}
),

numbered as (
    select
        case_id, activity, event_timestamp, resource, department, shift, patient_category,
        row_number() over (partition by case_id order by event_timestamp, activity) as event_number
    from events
),

with_previous as (
    select
        *,
        lag(activity)        over (partition by case_id order by event_number) as previous_activity,
        lag(event_timestamp) over (partition by case_id order by event_number) as previous_timestamp,
        max(event_number)    over (partition by case_id)                       as last_event_number
    from numbered
)

select
    case_id                          as Case_ID,
    activity                         as Activity_Name,
    event_timestamp                  as `Timestamp`,
    resource                         as Resource,
    department                       as Department,
    shift                            as Shift,
    patient_category                 as Patient_Category,
    event_number                     as Event_Number,
    previous_activity                as Previous_Activity,
    round(timestamp_diff(event_timestamp, previous_timestamp, second) / 60.0, 1) as Minutes_Since_Previous,
    activity = 'Return to Triage'    as Is_Rework,
    event_number = 1                 as Is_First_Event,
    event_number = last_event_number as Is_Last_Event
from with_previous