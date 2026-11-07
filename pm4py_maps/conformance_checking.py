"""
CareFlow - Conformance checking with PM4Py (Week 4).
Compares the REAL journey of every visit (BigQuery event_log) with the IDEAL journey.
 
Ideal journey:  Registration > Triage > (X-Ray and/or Lab Test, optional) > Doctor Consultation
                > (Treatment, optional) > Discharge or Admission
Run:  cd pm4py_maps   then   python conformance_checking.py
Output: output_conformance/ (maps PNG + tables CSV)
"""
import os
import traceback
from collections import Counter
import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog, Trace, Event
 
OUT = "output_conformance"
IDEAL = ("->('Registration','Triage',+(X('X-Ray',tau),X('Lab Test',tau)),"
         "'Doctor Consultation',X('Treatment',tau),X('Discharge','Admission'))")
 
 
def run_step(name, func):
    try:
        func()
        print(f"[OK]     {name}")
    except Exception:
        print(f"[FAILED] {name}")
        traceback.print_exc()
 
 
def build_log(df):
    """Plain Python event log (no pandas types, so it also works with pyarrow)."""
    df = df.sort_values(["Case_ID", "Timestamp", "Event_Number"]) if "Event_Number" in df else df.sort_values(["Case_ID", "Timestamp"])
    traces = {}
    for case, act in zip(df["Case_ID"].astype(str), df["Activity_Name"].astype(str)):
        traces.setdefault(case, []).append(act)
    log = EventLog()
    for case, acts in traces.items():
        t = Trace()
        t.attributes["concept:name"] = case
        for a in acts:
            t.append(Event({"concept:name": a}))
        log.append(t)
    return log, traces
 
 
def save_map(traces, case_ids, path):
    sub = pd.DataFrame([(c, a, i) for c in case_ids for i, a in enumerate(traces[c])],
                       columns=["case:concept:name", "concept:name", "n"])
    sub["time:timestamp"] = pd.Timestamp("2026-01-01", tz="UTC") + pd.to_timedelta(sub["n"], unit="m")
    sub["concept:name"] = sub["concept:name"].astype(object)
    sub["case:concept:name"] = sub["case:concept:name"].astype(object)
    dfg, s, e = pm4py.discover_dfg(sub)
    pm4py.save_vis_dfg(dfg, s, e, path)
 
 
def analyse(df):
    os.makedirs(OUT, exist_ok=True)
    log, traces = build_log(df)
    n = len(log)
    tree = pm4py.parse_process_tree(IDEAL)
    net, im, fm = pm4py.convert_to_petri_net(tree)
    print(f"Visits: {n} | Ideal model: {len(net.places)} places, {len(net.transitions)} transitions")
 
    diag = pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)
    fit = [bool(d["trace_is_fit"]) for d in diag]
    fitness = [float(d["trace_fitness"]) for d in diag]
    ids = [t.attributes["concept:name"] for t in log]
    visit = pd.DataFrame({"case_id": ids, "is_compliant": fit, "trace_fitness": [round(x, 3) for x in fitness]})
    visit.to_csv(f"{OUT}/1_visit_compliance.csv", index=False)
 
    def ideal_picture():
        pm4py.save_vis_petri_net(net, im, fm, f"{OUT}/2_ideal_model.png")
 
    def variants_table():
        counts = Counter(" > ".join(a) for a in traces.values())
        vlog = EventLog()
        paths = list(counts)
        for p in paths:
            t = Trace()
            for a in p.split(" > "):
                t.append(Event({"concept:name": a}))
            vlog.append(t)
        ali = pm4py.conformance_diagnostics_alignments(vlog, net, im, fm)
        rows = []
        for p, al in zip(paths, ali):
            extra = [l for l, m in al["alignment"] if m == ">>" and l != ">>"]
            missing = [m for l, m in al["alignment"] if l == ">>" and m not in (">>", None)]
            rows.append({"visits": counts[p], "percent": round(counts[p] * 100 / n, 1),
                         "deviation_cost": al["cost"] // 10000,
                         "extra_steps_in_real_journey": ", ".join(extra), "missing_steps": ", ".join(missing), "path": p})
        out = pd.DataFrame(rows).sort_values("visits", ascending=False)
        out.to_csv(f"{OUT}/3_conformance_by_journey.csv", index=False)
        print(out[["visits", "percent", "deviation_cost", "extra_steps_in_real_journey", "path"]].head(8).to_string(index=False))
 
    def maps():
        ok = [c for c, f in zip(ids, fit) if f]
        bad = [c for c, f in zip(ids, fit) if not f]
        save_map(traces, ok, f"{OUT}/4_compliant_visits_map.png")
        save_map(traces, bad, f"{OUT}/5_noncompliant_visits_map.png")
 
    def summary():
        loop = sum("Return to Triage" in a for a in traces.values())
        tb = sum(("Treatment" in a and "Doctor Consultation" in a and a.index("Treatment") < a.index("Doctor Consultation")) for a in traces.values())
        s = pd.DataFrame({"metric": ["visits", "compliant_visits", "compliance_percent", "average_trace_fitness",
                                     "visits_with_return_to_triage", "visits_with_treatment_before_consultation"],
                          "value": [n, sum(fit), round(sum(fit) * 100 / n, 1), round(sum(fitness) / n, 3), loop, tb]})
        s.to_csv(f"{OUT}/6_conformance_summary.csv", index=False)
        print("\n===== CONFORMANCE SUMMARY =====")
        print(s.to_string(index=False))
 
    run_step("Ideal model picture", ideal_picture)
    run_step("Conformance by journey (alignments)", variants_table)
    run_step("Compliant / non-compliant maps", maps)
    run_step("Summary", summary)
    print(f"\nFiles in '{OUT}':", sorted(os.listdir(OUT)))
 
 
if __name__ == "__main__":
    from process_discovery_bq import load_events
    analyse(load_events())