
-- CareFlow: Part 4 - Bottleneck Ranking

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
        ) / 60.0 AS transition_minutes
    FROM ordered_events
    WHERE next_activity IS NOT NULL
      AND next_timestamp >= timestamp
),

transition_summary AS (
    SELECT
        from_activity,
        to_activity,
        COUNT(*) AS transition_count,
        ROUND(AVG(transition_minutes), 2) AS avg_minutes,
        ROUND(APPROX_QUANTILES(
            transition_minutes, 100
        )[OFFSET(50)], 2) AS median_minutes,
        ROUND(MAX(transition_minutes), 2) AS max_minutes
    FROM transitions
    GROUP BY from_activity, to_activity
)

SELECT
    from_activity,
    to_activity,
    transition_count,
    avg_minutes,
    median_minutes,
    max_minutes,
    ROUND(
        avg_minutes * transition_count,
        2
    ) AS total_wait_minutes,
    DENSE_RANK() OVER (
        ORDER BY avg_minutes DESC
    ) AS average_delay_rank,
    DENSE_RANK() OVER (
        ORDER BY avg_minutes * transition_count DESC
    ) AS total_time_impact_rank
FROM transition_summary
ORDER BY total_time_impact_rank;
