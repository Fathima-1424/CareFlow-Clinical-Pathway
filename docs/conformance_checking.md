# Conformance Checking (Week 4)

## Goal
Compare the real journey of every patient visit with the ideal (mandated) journey and flag the visits that do not follow it.

## Ideal journey (our assumption, to be confirmed with the mentor)
Registration > Triage > (X-Ray and/or Lab Test, optional) > Doctor Consultation > (Treatment, optional) > Discharge or Admission

## Method
1. The ideal journey is written as a PM4Py process tree and converted to a Petri net.
2. Token-based replay checks all 5,000 visits against the model. A visit that replays without missing or remaining tokens is compliant.
3. Alignments on the 18 different journeys show which steps were added or moved (the deviation).
4. Script: `pm4py_maps/conformance_checking.py`. Output: `pm4py_maps/output_conformance/`.

## Result
| Metric | Value |
|---|---|
| Visits | 5,000 |
| Compliant visits | 2,815 (56.3%) |
| Average trace fitness | 0.938 |
| Visits with Return to Triage (rework) | 1,141 (22.8%) |
| Visits with Treatment before Doctor Consultation | 1,389 (27.8%) |

The two deviations are different problems: the loop-back adds extra steps and about 36 minutes, and Treatment before the Doctor Consultation is a step in the wrong place.

## Cross-check
The same 56.3% comes out of three places: the PM4Py model, the dbt flag `is_compliant` in `fct_visits` and the dashboard.

## Limits
- The ideal path is our own rule, not a real hospital protocol.
- The data is synthetic.