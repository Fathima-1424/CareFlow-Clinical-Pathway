-- Staging model: cleans the raw ER event log (one row = one event)

with source as (

    select * from {{ source('careflow_raw', 'raw_ehr_events') }}

),

cleaned as (

    select
        trim(case_id)                          as case_id,
        trim(activity)                         as activity,
        cast(`timestamp` as timestamp)         as event_timestamp,
        trim(department)                       as department,
        trim(shift)                            as shift,
        trim(patient_category)                 as patient_category,
        nullif(trim(resource), '')             as resource
    from source
    where case_id is not null
      and activity is not null
      and `timestamp` is not null

),

deduplicated as (

    select distinct * from cleaned

)

select * from deduplicated
