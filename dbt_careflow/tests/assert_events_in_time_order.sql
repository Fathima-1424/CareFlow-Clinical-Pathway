select * from {{ ref('event_log') }}
where Minutes_Since_Previous < 0