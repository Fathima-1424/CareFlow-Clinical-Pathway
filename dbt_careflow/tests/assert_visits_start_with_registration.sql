select Case_ID from {{ ref('event_log') }}
where Is_Last_Event and Activity_Name not in ('Discharge', 'Admission')