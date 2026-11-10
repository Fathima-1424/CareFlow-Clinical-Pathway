
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
        case_id,
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
),

summary AS (
    SELECT
        from_activity,
        to_activity,
        COUNT(*) AS transition_count,
        AVG(transition_seconds) / 60 AS avg_minutes,
        APPROX_QUANTILES(
            transition_seconds, 100
        )[OFFSET(50)] / 60 AS median_minutes,
        MAX(transition_seconds) / 60 AS max_minutes
    FROM transitions
    GROUP BY from_activity, to_activity
)

SELECT
    from_activity,
    to_activity,
    transition_count,
    ROUND(avg_minutes, 2) AS avg_minutes,
    ROUND(median_minutes, 2) AS median_minutes,
    ROUND(max_minutes, 2) AS max_minutes
FROM summary
WHERE transition_count >= 10
ORDER BY avg_minutes DESC
LIMIT 10;
