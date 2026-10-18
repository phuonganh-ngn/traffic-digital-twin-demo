## 2.7. Illustrative Prototype of the Proposed Digital Twin System

This prototype demonstrates observation, synchronization, prediction, and feedback for one intersection with North–South (NS) and East–West (EW) signal groups. A Python queue simulator substitutes for the physical intersection; a separate Digital Twin receives idealized virtual sensor observations.

The published dataset is Exhibit 2-27 of the HCM Guide Shenendehowa Campus case study: https://hcmguide.com/Case2/techprob03/subproblem03a/prob3a2.htm. Acquisition status for this run: **web_extracted**. Eight observed 15-minute approach counts cover 07:00–09:00, totaling 3,785 vehicles. Turning movements are aggregated into two signal groups. The small southbound counts are retained. NumPy multinomial allocation with seed 42 generates synthetic per-second arrivals while exactly preserving each interval's totals. These timestamps, queues, and phases are not field observations.

The environment adds arrivals and serves up to one vehicle per second during green, with 3-second yellow and 2-second all-red transitions. Green durations are 15, 30, or 45 seconds. Queue waiting is the sum of end-of-second queues over 7,200 seconds, in vehicle-seconds; vehicles arriving and served within the same second contribute zero. Mean queues use these same samples. Maximum queue is the largest individual signal-group queue. Final backlog remains explicitly reported; no clearance period is added.

The separate Twin synchronizes every 10 seconds and at green decision boundaries. Its stored queue estimate is held between updates, and its data age is logged. A small online Ridge regression (alpha=1) learns next-block NS/EW arrival rates from the combined arrival rates of the previous three completed 10-second blocks. It receives no future arrivals. After six training samples, its nonnegative predictions are blended equally with a trailing observed mean of up to 60 seconds; before that, the mean is used, with zero at initialization. The model is trained only within the Twin policy, without external training data. It is a lightweight illustrative ML component, not a validated traffic forecasting model.

At each green decision, the Twin tests 15, 30, and 45 seconds over the same 120-second horizon, including yellow/all-red and alternating opposing phases. Subsequent green phases use 30 seconds. The blended predicted rates are held constant over this horizon, a simplifying extrapolation of a 10-second forecast. Each candidate uses a temporary queue model, preserving the actual environment. Minimum predicted queued vehicle-seconds selects the action; numerical ties prefer 30 seconds, then the shorter duration.

An additional real-time simulation mode starts from empty queues at 07:00 and computes the same environment and Twin progressively, at approximately one simulated second per wall-clock second while the page is connected. Virtual sensors synchronize the separate Twin every second; Ridge training still uses completed 10-second blocks. Signal choices are computed at green boundaries and all yellow/all-red intervals remain mandatory. The user can start, pause, resume, or reset this run. This mode uses synthetic arrivals, not a live field feed. The comparison table below is the saved complete experiment, independent of the active interactive session.

All three policies use identical arrivals, initial conditions, service, and transitions. Fixed-time always selects 30 seconds. Direct adaptive selects 45 seconds when the current green group's queue exceeds the opposing queue by at least five vehicles, 15 when it trails by at least five, and 30 otherwise. Executed simulation results follow:

| Policy | Waiting (vehicle-seconds) | Served | Final backlog |
|---|---:|---:|---:|
| fixed_time | 1,197,927 | 3,416 | 369 |
| direct_adaptive | 82,447 | 3,778 | 7 |
| digital_twin | 42,973 | 3,781 | 4 |

These are simulated comparisons, not observed reductions in real traffic delay. The predictive policy is not guaranteed to outperform the others. Limitations include ideal sensing, a simple aggregate service model, constant forecast rates within each prediction, online training on only two hours, and unvalidated synthetic arrival timing. Video, physical sensors, exact geometry, actual signal phases, pedestrian movements, and real-time deployment are absent. This is an offline illustrative Digital Twin with a small ML forecasting component, not a deployed twin of a real intersection.
