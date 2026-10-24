{{ config(materialized='view') }}

select
    Previous_Activity                                                    as from_step,
    Activity_Name                                                        as to_step,
    count(*)                                                             as transitions,
    round(avg(Minutes_Since_Previous), 1)                                as avg_minutes,
    round(approx_quantiles(Minutes_Since_Previous, 100)[offset(50)], 1)  as median_minutes,
    round(max(Minutes_Since_Previous), 1)                                as max_minutes
from {{ ref('event_log') }}
where Previous_Activity is not null
group by from_step, to_step
order by avg_minutes desc