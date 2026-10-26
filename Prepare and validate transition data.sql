
WITH ordered_events AS (
    SELECT
        case_id,
        activity,
        timestamp,
        department,
        shift,
        patient_category,
        resource,

        LEAD(activity) OVER (
            PARTITION BY case_id
            ORDER BY timestamp
        ) AS next_activity,

        LEAD(timestamp) OVER (
            PARTITION BY case_id
            ORDER BY timestamp
        ) AS next_timestamp

    FROM `polished-trail-511415-r4.careflow.event_log`
),

transitions AS (
    SELECT
        case_id,
        activity AS from_activity,
        next_activity AS to_activity,
        timestamp AS from_timestamp,
        next_timestamp AS to_timestamp,

        TIMESTAMP_DIFF(
            next_timestamp,
            timestamp,
            SECOND
        ) AS transition_seconds

    FROM ordered_events
    WHERE next_activity IS NOT NULL
)

SELECT *
FROM transitions
ORDER BY case_id, from_timestamp
LIMIT 1000;
