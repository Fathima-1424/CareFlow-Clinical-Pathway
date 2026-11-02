SELECT
    from_step,
    to_step,
    COUNT(*) AS transition_count,
    ROUND(AVG(avg_minutes), 2) AS average_waiting_minutes,
    ROUND(MAX(max_minutes), 2) AS maximum_waiting_minutes,
    CASE
        WHEN AVG(avg_minutes) >= 30 THEN 'High Bottleneck'
        WHEN AVG(avg_minutes) >= 15 THEN 'Moderate Bottleneck'
        ELSE 'Low Bottleneck'
    END AS bottleneck_category
FROM {{ ref('int_transition_times') }}
GROUP BY
    from_step,
    to_step
ORDER BY
    average_waiting_minutes DESC