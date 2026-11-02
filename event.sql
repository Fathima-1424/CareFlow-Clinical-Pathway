SELECT
    activity,
    COUNT(*) AS event_count
FROM `polished-trail-511415-r4.careflow.event_log`
GROUP BY activity
ORDER BY event_count DESC;