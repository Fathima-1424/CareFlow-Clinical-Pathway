CREATE OR REPLACE TABLE
`polished-trail-511415-r4.careflow.actual_patient_journeys`
AS

SELECT
    case_id,

    ARRAY_AGG(
        activity ORDER BY timestamp
    ) AS activity_sequence,

    STRING_AGG(
        activity,
        ' → '
        ORDER BY timestamp
    ) AS actual_journey,

    COUNT(*) AS total_events,

    MIN(timestamp) AS journey_start,

    MAX(timestamp) AS journey_end,

    ARRAY_AGG(
        activity ORDER BY timestamp LIMIT 1
    )[OFFSET(0)] AS first_activity,

    ARRAY_AGG(
        activity ORDER BY timestamp DESC LIMIT 1
    )[OFFSET(0)] AS last_activity

FROM
    `polished-trail-511415-r4.careflow.event_log`

GROUP BY
    case_id;



SELECT
    case_id,
    actual_journey,
    total_events,
    first_activity,
    last_activity
FROM
    `polished-trail-511415-r4.careflow.actual_patient_journeys`
ORDER BY case_id
LIMIT 20;


SELECT
    actual_journey,
    COUNT(*) AS patient_count,
    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM
    `polished-trail-511415-r4.careflow.actual_patient_journeys`
GROUP BY
    actual_journey
ORDER BY
    patient_count DESC;


SELECT
    COUNT(*) AS total_patients,

    SUM(
        CASE
            WHEN actual_journey IS NULL THEN 1
            ELSE 0
        END
    ) AS missing_journeys,

    SUM(
        CASE
            WHEN first_activity IS NULL THEN 1
            ELSE 0
        END
    ) AS missing_first_activity,

    SUM(
        CASE
            WHEN last_activity IS NULL THEN 1
            ELSE 0
        END
    ) AS missing_last_activity,

    SUM(
        CASE
            WHEN total_events = 0 THEN 1
            ELSE 0
        END
    ) AS empty_journeys

FROM
    `polished-trail-511415-r4.careflow.actual_patient_journeys`;