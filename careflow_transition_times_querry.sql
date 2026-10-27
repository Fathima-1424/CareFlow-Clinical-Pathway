
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
),

transitions AS (
    SELECT
        activity AS from_activity,
        next_activity AS to_activity,

        TIMESTAMP_DIFF(
            next_timestamp,
            timestamp,
            SECOND
        ) AS transition_seconds

    FROM ordered_events
    WHERE next_activity IS NOT NULL
      AND next_timestamp >= timestamp
)

SELECT
    from_activity,
    to_activity,
    COUNT(*) AS transition_count,

    ROUND(AVG(transition_seconds) / 60, 2)
        AS avg_minutes,

    ROUND(
        APPROX_QUANTILES(transition_seconds, 100)[OFFSET(50)] / 60,
        2
    ) AS median_minutes,

    ROUND(MIN(transition_seconds) / 60, 2)
        AS min_minutes,

    ROUND(MAX(transition_seconds) / 60, 2)
        AS max_minutes

FROM transitions
GROUP BY from_activity, to_activity
ORDER BY avg_minutes DESC;
