
WITH ordered_events AS (
    SELECT
        case_id,
        activity,
        timestamp,

        LEAD(activity) OVER (
            PARTITION BY case_id
            ORDER BY timestamp
        ) AS next_activity,

        LEAD(timestamp) OVER (
            PARTITION BY case_id
            ORDER BY timestamp
        ) AS next_timestamp

    FROM `polished-trail-511415-r4.careflow.event_log`
)

SELECT
    case_id,
    activity AS from_activity,
    next_activity AS to_activity,
    timestamp AS from_timestamp,
    next_timestamp AS to_timestamp,

    ROUND(
        TIMESTAMP_DIFF(
            next_timestamp,
            timestamp,
            SECOND
        ) / 60.0,
        2
    ) AS transition_minutes

FROM ordered_events
WHERE activity = 'Triage'
  AND next_activity = 'Doctor Consultation'
  AND next_timestamp >= timestamp
ORDER BY transition_minutes DESC
LIMIT 20;
