select Case_ID from {{ ref('event_log') }}
where Is_First_Event and Activity_Name != 'Registration'