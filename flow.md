CODEX TASK - Build a Simple Traffic Digital Twin Demo (A-Z)
Implement the complete project in the current directory. This is a small university IoT/AIoT final-assignment demo. Do the work: fetch data, implement the simulator and Digital Twin, run tests, generate actual outputs, and launch-check the dashboard. Do not stop at a plan or pseudocode.

0. Goal and boundaries
Title: A Data-Driven Digital Twin Demonstrator for Adaptive Traffic Signal Control
Show why Digital Twin adds value beyond direct adaptive control: it maintains a digital state based on observations from a traffic environment and performs what-if predictions before selecting signal timings.
Keep the project deliberately small:
- One intersection with two opposing signal groups: North-South (NS) and East-West (EW).
- One small, real, published traffic-count table: 8 records, one every 15 minutes (07:00-09:00).
- A simple Python queue simulator acts as the physical-environment substitute; a separate Digital Twin object observes it.
- Three traffic-light policies: fixed-time, direct adaptive, and Digital-Twin-assisted predictive.
- One Streamlit dashboard, 3 sections, using saved simulation logs.
- CPU only, a few small Python files; no database server or background services.
Use: Python 3.11+, requests, beautifulsoup4, numpy, pandas, streamlit, pytest (optional charts via Streamlit's built-in chart functions).
Do NOT use: SUMO, YOLO, computer vision, camera video, MQTT, IoT hardware/emulators, reinforcement learning, Docker, large datasets, 3D visualization, paid services, or real traffic-light equipment.
1. Exact end-to-end flow
PUBLIC TRAFFIC DATA: HCM Guide Exhibit 2-27
       |  (fetch once; fallback if inaccessible)
       v
8 x 15-minute counts: East, West, North, South
       |  (validate, combine to EW/NS)
       v
traffic_counts.csv
       |  (seeded distribution within each 15-min bin)
       v
arrivals_by_second.csv  [2 hours = 7,200 seconds]
       |
       v
TRAFFIC ENVIRONMENT  [simulated physical intersection]
Cars arrive -> wait at red -> leave on green
       |                       ^
       | observed queues,      | control action
       | counts and phase      |
       v                       |
DIGITAL TWIN [separate model + synchronized state]
Update state -> predict future queues for green=15/30/45s
       |                       |
       v                       |
DECISION CONTROLLER -----------+
       |
       v
RUN LOGS + COMPARISON OF 3 POLICIES
       |
       v
STREAMLIT DASHBOARD + ENGLISH REPORT PARAGRAPH
Non-negotiable distinction: The environment is the physical-system substitute; the Digital Twin is a separate synchronized model and decision-support layer. A simulator alone is NOT a Digital Twin. This is an offline illustrative Digital Twin prototype, not a live, bidirectional twin of a real intersection.
2. DATA - crawl a tiny real table, with a robust fallback
Source: HCM Guide, Case Study 2 / Problem 3 / Sub-problem 3a / Exhibit 2-27: Shenendehowa Campus AM peak hour volumes.
- Focused page: https://hcmguide.com/Case2/techprob03/subproblem03a/prob3a2.htm
- Printable page: https://hcmguide.com/case2/techprob03/problem_3printablev3.htm
Step 2A - get_data.py
1. Request the focused page once (reasonable timeout and user-agent; no crawling beyond these pages).
2. Find Exhibit 2-27 and extract the eight approach Tot values for each interval from 07:00 to 08:45. Do not confuse them with LT/TH/RT movements, the AM Peak summary, or the PM data.
3. Save one tidy file with columns:
   start_time,duration_minutes,eastbound,westbound,northbound,southbound,arrivals_EW,arrivals_NS,intersection_total.
4. Validate: exactly 8 rows; 15 minutes each; nonnegative integers; EW = east+west; NS = north+south; row totals agree.
5. Save data/source_metadata.json, including URLs, timestamp, extraction method, and any retrieval error.
IMPORTANT FALLBACK: The project must work if Codex cannot fetch the page. If network/parsing fails, look for traffic_intersection_8_intervals_real.csv in the project directory. If absent, use the following published, source-checked values, embedded directly as the fallback. Record the acquisition method as fallback_from_published_table - NEVER claim a successful crawl if it failed. Do not invent data.
start_time,duration_minutes,eastbound,westbound,northbound,southbound,arrivals_EW,arrivals_NS,intersection_total
07:00,15,132,151,34,0,283,34,317
07:15,15,145,184,48,0,329,48,377
07:30,15,161,210,32,1,371,33,404
07:45,15,236,253,24,0,489,24,513
08:00,15,282,239,87,2,521,89,610
08:15,15,248,233,126,2,481,128,609
08:30,15,220,148,68,3,368,71,439
08:45,15,213,201,88,14,414,102,516
These are observed 15-minute approach volumes from an educational traffic-engineering case study. They are not observed queue lengths, measured delay, individual arrival timestamps, or measured signal phases. Keep the unusually small southbound volume: it is in the source. Aggregating turning movements into NS/EW is an explicit demo simplification.
Step 2B - prepare per-second arrivals
Create a deterministic prepare_arrivals.py:
- For each interval, allocate its exact total NS and EW arrivals across 900 seconds using numpy.random.default_rng(42).multinomial(...) (or an equally reproducible method).
- Produce data/arrivals_by_second.csv with second,arrivals_NS,arrivals_EW and exactly 7,200 rows.
- Test conservation: every 900-second block must sum to the original 15-minute counts, with no changes.
- Generate the sequence once and reuse the identical file for all three control policies.
- Label per-second arrival times synthetic disaggregation, not observed timestamps.
3. TRAFFIC ENVIRONMENT - extremely simple queue simulation
Create TrafficEnvironment in simulator.py:
- Maintain queue_NS, queue_EW, current signal phase, phase elapsed time, served counts, and cumulative waiting (vehicle-seconds).
- Simulate in 1-second steps for the 7,200-second arrival window.
- At every step: add new arrivals; serve up to 1 vehicle/second from the green group (configurable); serve zero during yellow or all-red; record queues and served vehicles.
- Queues must never become negative; mass balance must hold: arrived = served + queued for each group.
- Use a valid phase cycle: NS_GREEN -> NS_YELLOW (3s) -> ALL_RED (2s) -> EW_GREEN -> EW_YELLOW (3s) -> ALL_RED (2s) -> ....
- Green duration may be chosen at the start of that green phase, from 15s / 30s / 45s. The controller must never skip yellow/all-red or show simultaneous NS/EW green.
- Keep the environment self-contained. It receives chosen signal plans but does NOT contain the Digital Twin logic.
- Define all metrics consistently. Clearly report any backlog remaining at the end; do not silently assume everyone has exited.
No vehicle-by-vehicle 2D/3D animation is required. Two queues and traffic-light indicators are enough.
4. DIGITAL TWIN - the essential educational feature
Create DigitalTwin separately in digital_twin.py.
Observation interface: At each observation update, pass only current queue counts, current phase, timestamp, and past/recent arrival counts from the environment. Treat these as idealized virtual sensor readings. The real dataset only provides 15-minute entry counts; simulated queues are not field measurements.
Synchronize: Update the twin's own state every 10 simulated seconds, and also at signal decision points as needed. Log observation time, environment queue, twin estimated queue, and data age. Keep these states separate even if they match closely when synchronized.
What-if prediction (no ML): At every start-of-green decision:
1. Estimate future NS/EW arrival rates using past observations only, e.g., a trailing 60-second average. During initial periods with too little history, use a documented conservative default from available history, never future values.
2. Copy the Digital Twin state into a temporary prediction model; do not change the actual environment while testing.
3. Evaluate current-phase green candidates 15, 30, and 45 seconds, using the same 120-second future horizon for each candidate.
4. Include yellow/all-red transitions and realistic red waiting. After the current candidate green, use a common default 30-second green for subsequent phases.
5. Use a simple forecast queue update: Q(t+1) = max(0, Q(t) + predicted_arrivals(t) - allowable_departures(t)).
6. Compute predicted cumulative queued vehicle-seconds, NS+EW, as the score; select the minimum, deterministic tie-break to 30s or shorter green.
7. Save each candidate's score and selected plan for dashboard visualization.
No information leakage: Never use future realized arrivals in the Twin's prediction, even though the simulator already loaded a CSV for reproducibility. Give the Twin only past observations.
5. THREE controllers - compare fairly
Implement exactly three policies in controllers.py:
Policy	Rule
fixed_time	Every green phase = 30s.
direct_adaptive	Use only current observed NS/EW queue imbalance to choose 15s/30s/45s via a simple, documented rule. No what-if model.
digital_twin	Select 15s/30s/45s using the Digital Twin's what-if scores.


All policies use identical arrivals, service capacity, yellow/all-red time, and initial conditions. Do not assume the Digital Twin policy wins. If it loses, show honest results and explain the model's limits.
6. OUTPUTS - only a few useful metrics
Create run_demo.py to run all three policies and export genuine simulator logs:
- results/summary.csv: one row per policy; include total queue waiting (vehicle-seconds), mean queue NS/EW, maximum queue, total served, and final backlog.
- results/timeseries_<policy>.csv: time, NS/EW queues, light phase, arrivals, served, accumulated waiting.
- results/decisions_<policy>.csv: decision timestamp, chosen green duration, observed state; for the DT controller, candidate scores.
Optionally create one comparison PNG, but the dashboard charts are sufficient.
All comparisons are simulated, not observed reductions in real traffic delay.
7. STREAMLIT dashboard - ONLY 3 SECTIONS
Create app.py, reading the saved CSV/log files rather than running a fragile live simulation process.
Section A - Dataset
- Source URL and actual acquisition method (web_extracted vs fallback_from_published_table).
- Table of 8 intervals and a bar/line chart of NS/EW arrival volumes.
- Notice: real 15-minute totals, synthetic within-bin arrival times.
Section B - Digital Twin Walkthrough
- A slider to choose simulation time for the DT policy.
- Simple signal indicators (NS/EW red or green) and two queue bars.
- Show environment queue and the separate Digital Twin estimate at that time, observation timestamp, and last synchronization.
- At nearest decision point, show a small table: 15s / 30s / 45s and the predicted cumulative waiting score; highlight chosen decision.
- One line of text: Observation → Synchronization → What-if → Decision → Feedback.
Section C - Controller Comparison
- A three-row metrics table comparing Fixed-Time / Direct Adaptive / Digital Twin.
- At most two charts: queue over time and total simulated waiting by controller.
- Label every result as simulated. No fabricated live data, photos, or performance numbers.
Use title: Traffic Digital Twin - Illustrative Prototype. Keep the UI readable and presentation-ready, without unnecessary pages or animations.
8. Minimal file layout
traffic_dt_demo/
  README.md
  requirements.txt
  get_data.py
  prepare_arrivals.py
  simulator.py
  digital_twin.py
  controllers.py
  run_demo.py
  app.py
  data/                     # original observations + transformed arrivals
  results/                  # actual generated run outputs
  docs/
    ARCHITECTURE.md         # short Mermaid diagram + explanation
    REPORT_SECTION_2_7.md  # English text for the final assignment
  tests/
    test_demo.py
Do not create more files unless necessary. Keep functions short and code easy to understand.
9. Simple final-assignment documentation
In docs/REPORT_SECTION_2_7.md, write formal but concise English suitable for insertion after the conceptual system architecture in Question 2:
2.7. Illustrative Prototype of the Proposed Digital Twin System
Cover: objective, published dataset and acquisition status, synthetic per-second arrival generation, traffic environment, observation-based Digital Twin synchronization, what-if signal decisions, actual three-policy simulation results, and limitations. Include the official source URL and a small results table computed from results/summary.csv. No invented results or research claims.
In docs/ARCHITECTURE.md, add one Mermaid flowchart covering the pipeline above. Explain why this is a Digital Twin demonstration rather than just a direct adaptive controller.
Required honesty: A Python simulator substitutes for a physical intersection; queues are generated by the simulator and observed through an idealized interface; video, real-time sensor integration, exact intersection geometry, and actual signal phases are absent. The system illustrates the principles of a Digital Twin, not a deployed real-time twin.
10. Run and verify (mandatory)
The user should need only these commands after cloning/opening the project:
python -m pip install -r requirements.txt
python get_data.py
python prepare_arrivals.py
python run_demo.py
streamlit run app.py
Include equivalent Windows PowerShell guidance if different.
Tests must verify:
1. Eight real source intervals with correct 4-approach totals and correct aggregation.
2. 7,200 generated seconds and exact per-bin total preservation.
3. Queue non-negativity, mass conservation, no signal conflict, mandatory yellow/all-red.
4. The three policies see the same arrival sequence.
5. Twin state really is separate, updated by observations, and what-if does not look ahead into future arrivals.
6. The dashboard loads generated CSVs; all displayed numbers originate from logs.
Run pytest. Actually run the data-preparation and experiment scripts. Fix issues. Attempt a Streamlit launch smoke test. If any task is blocked, disclose the blocker precisely and do not claim it was verified.
11. Definition of done
The project is done only when:
- [ ] The tiny published dataset is retrieved OR the fallback is used with correct provenance.
- [ ] End-to-end scripts run and produce actual outputs.
- [ ] Three controllers work and a Digital Twin makes what-if decisions.
- [ ] The dashboard shows source, state synchronization, prediction candidates, and comparisons.
- [ ] Tests pass and the academic Section 2.7 accurately describes the executed prototype.
Final Codex reply: state what was implemented and tested, data retrieval status, real simulation metrics, exact run commands, and any known limitations. Start coding now, not planning. Prefer working simplicity over complexity