
{{ config(materialized='table') }}

SELECT
    case_id,
    activity,
    timestamp,
    department,
    shift,
    patient_category,
    resource
FROM {{ ref('stg_events') }}
ORDER BY case_id, timestamp
