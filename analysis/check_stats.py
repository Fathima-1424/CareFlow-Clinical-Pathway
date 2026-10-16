import pandas as pd

CSV_PATH = 'careflow_raw_events_5000_visits.csv'
CASE, ACT, TS = 'case_id', 'activity', 'timestamp'
TRIAGE_RETURN = 'Return to Triage'
CONSULT = 'Doctor Consultation'
TREATMENT = 'Treatment'

df = pd.read_csv(CSV_PATH)
df[ACT] = df[ACT].astype(str).str.strip()
df[TS] = pd.to_datetime(df[TS])
df = df.drop_duplicates().sort_values([CASE, TS]).reset_index(drop=True)

print('Activities:', sorted(df[ACT].unique()))
visits = df[CASE].nunique()

g = df.groupby(CASE)[TS]
dur = (g.max() - g.min()).dt.total_seconds() / 60
loop_cases = set(df.loc[df[ACT] == TRIAGE_RETURN, CASE])
is_loop = dur.index.isin(loop_cases)

loop_pct = len(loop_cases) / visits * 100
avg_loop = dur[is_loop].mean()
avg_noloop = dur[~is_loop].mean()

first = df.groupby([CASE, ACT])[TS].min().unstack()
tb = (first[TREATMENT] < first[CONSULT]).sum() / visits * 100
variants = df.groupby(CASE)[ACT].apply(tuple).nunique()

checks = [
    ('Visits', 5000, visits, 0),
    ('Events', 27962, len(df), 0),
    ('Variants', 18, variants, 0),
    ('Loop-back %', 22.8, loop_pct, 0.1),
    ('Avg min with loop-back', 108, avg_loop, 2),
    ('Avg min without loop-back', 72, avg_noloop, 2),
    ('Extra min', 36, avg_loop - avg_noloop, 2),
    ('Treatment before Consult %', 27.8, tb, 0.1),
]
print()
for name, exp, act, tol in checks:
    ok = 'OK' if abs(exp - act) <= tol else 'MISMATCH'
    print(f'{name:30}{exp:>10}{round(act, 1):>10}  {ok}')