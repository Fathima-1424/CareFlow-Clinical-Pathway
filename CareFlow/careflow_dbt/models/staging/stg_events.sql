
{{ config(materialized='view') }}

SELECT
    TRIM(case_id) AS case_id,

    CASE
        WHEN LOWER(TRIM(activity)) IN ('xray', 'x ray', 'x-ray')
            THEN 'X-Ray'
        WHEN LOWER(TRIM(activity)) IN ('triage', 'return to triage')
            THEN CASE
                WHEN LOWER(TRIM(activity)) = 'return to triage'
                    THEN 'Return to Triage'
                ELSE 'Triage'
            END
        ELSE TRIM(activity)
    END AS activity,

    timestamp,
    TRIM(department) AS department,
    TRIM(shift) AS shift,
    TRIM(patient_category) AS patient_category,
    TRIM(resource) AS resource

FROM `polished-trail-511415-r4.careflow.clean_events`

WHERE
    case_id IS NOT NULL
    AND TRIM(case_id) != ''
    AND activity IS NOT NULL
    AND TRIM(activity) != ''
    AND timestamp IS NOT NULL
