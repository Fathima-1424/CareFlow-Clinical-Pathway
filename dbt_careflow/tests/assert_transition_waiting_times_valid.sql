SELECT *
FROM {{ ref('int_transition_times') }}
WHERE avg_minutes < 0
   OR median_minutes < 0
   OR max_minutes < 0
   OR avg_minutes IS NULL
   OR median_minutes IS NULL
   OR max_minutes IS NULL