
SELECT
    COUNT(*) AS total_events,
    COUNT(DISTINCT case_id) AS total_visits,
    COUNTIF(case_id IS NULL) AS missing_case_ids,
    COUNTIF(activity IS NULL) AS missing_activities,
    COUNTIF(timestamp IS NULL) AS missing_timestamps
FROM `polished-trail-511415-r4.careflow.raw_events`;



SELECT *
FROM `polished-trail-511415-r4.careflow.raw_events`
LIMIT 10;
