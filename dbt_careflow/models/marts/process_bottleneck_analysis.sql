-- CareFlow: Process Bottleneck Analysis
-- Purpose: Identify slow transitions between clinical activities.
-- Metrics: Average, maximum, and median transition waiting time.

SELECT
    from_step,
    to_step,
    ROUND(AVG(avg_minutes), 2) AS average_waiting_minutes,
    ROUND(MAX(max_minutes), 2) AS maximum_waiting_minutes,
    ROUND(AVG(median_minutes), 2) AS average_median_waiting_minutes,
    COUNT(*) AS transition_records
FROM {{ ref('int_transition_times') }}
GROUP BY
    from_step,
    to_step
ORDER BY
    average_waiting_minutes DESC