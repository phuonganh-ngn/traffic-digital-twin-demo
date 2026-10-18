"""Run identical arrival input through three policies and export actual logs."""
import hashlib
import pandas as pd
from get_data import ROOT
from simulator import TrafficEnvironment
from digital_twin import DigitalTwin
from controllers import POLICIES, choose


def run_policy(arrivals, policy):
    env = TrafficEnvironment()
    twin = DigitalTwin(service_capacity=env.service_capacity) if policy == 'digital_twin' else None
    rows, decisions, synchronizations = [], [], []

    def sync():
        obs = env.observe()
        twin.synchronize(obs)
        synchronizations.append(dict(time=obs.time, environment_queue_NS=obs.queue_NS,
                                     environment_queue_EW=obs.queue_EW, twin_queue_NS=twin.queues['NS'],
                                     twin_queue_EW=twin.queues['EW'], data_age=0))

    if twin:
        sync()
    for arrival in arrivals.itertuples(index=False):
        if env.signal.needs_plan:
            obs = env.observe()
            # The end of the previous step synchronized this decision boundary.
            green, scores = choose(policy, obs, twin)
            decisions.append(dict(time=env.time, phase=obs.phase, chosen_green=green,
                                  queue_NS=obs.queue_NS, queue_EW=obs.queue_EW,
                                  **(dict(rate_NS=twin.rates['NS'], rate_EW=twin.rates['EW'],
                                          forecast_method=twin.forecast_method,
                                          training_samples=twin.training_samples) if twin else {}), **scores))
            env.signal.choose(green)
        row = env.step(int(arrival.arrivals_NS), int(arrival.arrivals_EW))
        if twin:
            if env.time % 10 == 0 or env.signal.needs_plan:
                sync()
            row.update(twin_queue_NS=twin.queues['NS'], twin_queue_EW=twin.queues['EW'],
                       observation_time=twin.observation_time, data_age=env.time-twin.observation_time)
        rows.append(row)
    logs = pd.DataFrame(rows)
    summary = dict(policy=policy, total_waiting_vehicle_seconds=env.waiting,
                   mean_queue_NS=logs.queue_NS.mean(), mean_queue_EW=logs.queue_EW.mean(),
                   max_queue=int(logs[['queue_NS', 'queue_EW']].max().max()),
                   total_served=sum(env.served.values()), final_backlog=sum(env.queues.values()),
                   final_backlog_NS=env.queues['NS'], final_backlog_EW=env.queues['EW'],
                   arrival_sha256=hashlib.sha256(arrivals.to_csv(index=False).encode()).hexdigest())
    return summary, logs, pd.DataFrame(decisions), pd.DataFrame(synchronizations)


def write_report(summary):
    import json
    metadata = json.loads((ROOT / 'data/source_metadata.json').read_text())
    table = ['| Policy | Waiting (vehicle-seconds) | Served | Final backlog |',
             '|---|---:|---:|---:|']
    for r in summary.itertuples():
        table.append(f'| {r.policy} | {r.total_waiting_vehicle_seconds:,} | {r.total_served:,} | {r.final_backlog} |')
    report = f'''## 2.7. Illustrative Prototype of the Proposed Digital Twin System

This prototype demonstrates observation, synchronization, prediction, and feedback for one intersection with North–South (NS) and East–West (EW) signal groups. A Python queue simulator substitutes for the physical intersection; a separate Digital Twin receives idealized virtual sensor observations.

The published dataset is Exhibit 2-27 of the HCM Guide Shenendehowa Campus case study: {metadata['source_url']}. Acquisition status for this run: **{metadata['acquisition_method']}**. Eight observed 15-minute approach counts cover 07:00–09:00, totaling 3,785 vehicles. Turning movements are aggregated into two signal groups. The small southbound counts are retained. NumPy multinomial allocation with seed 42 generates synthetic per-second arrivals while exactly preserving each interval's totals. These timestamps, queues, and phases are not field observations.

The environment adds arrivals and serves up to one vehicle per second during green, with 3-second yellow and 2-second all-red transitions. Green durations are 15, 30, or 45 seconds. Queue waiting is the sum of end-of-second queues over 7,200 seconds, in vehicle-seconds; vehicles arriving and served within the same second contribute zero. Mean queues use these same samples. Maximum queue is the largest individual signal-group queue. Final backlog remains explicitly reported; no clearance period is added.

The separate Twin synchronizes every 10 seconds and at green decision boundaries. Its stored queue estimate is held between updates, and its data age is logged. A small online Ridge regression (alpha=1) learns next-block NS/EW arrival rates from the combined arrival rates of the previous three completed 10-second blocks. It receives no future arrivals. After six training samples, its nonnegative predictions are blended equally with a trailing observed mean of up to 60 seconds; before that, the mean is used, with zero at initialization. The model is trained only within the Twin policy, without external training data. It is a lightweight illustrative ML component, not a validated traffic forecasting model.

At each green decision, the Twin tests 15, 30, and 45 seconds over the same 120-second horizon, including yellow/all-red and alternating opposing phases. Subsequent green phases use 30 seconds. The blended predicted rates are held constant over this horizon, a simplifying extrapolation of a 10-second forecast. Each candidate uses a temporary queue model, preserving the actual environment. Minimum predicted queued vehicle-seconds selects the action; numerical ties prefer 30 seconds, then the shorter duration.

An additional real-time simulation mode starts from a prepared queue snapshot at 07:00:35 (1 NS and 7 EW vehicles, obtained by simulating only the historical first 35 seconds) and computes the same environment and Twin progressively, at approximately one simulated second per wall-clock second while the page is connected. Virtual sensors synchronize the separate Twin every second; Ridge training still uses completed 10-second blocks. Signal choices are computed at green boundaries and all yellow/all-red intervals remain mandatory. The first signal decision is presented through five visible steps before applying the plan; simulated time is held during this introduction. Subsequent decisions run automatically, with no repeated explanation pauses, approximately at wall-clock speed while cars move. The user can start, pause, resume, or reset this run. This mode uses synthetic arrivals, not a live field feed. The comparison table below is the saved complete experiment, independent of the active interactive session.

All three policies use identical arrivals, initial conditions, service, and transitions. Fixed-time always selects 30 seconds. Direct adaptive selects 45 seconds when the current green group's queue exceeds the opposing queue by at least five vehicles, 15 when it trails by at least five, and 30 otherwise. Executed simulation results follow:

{chr(10).join(table)}

These are simulated comparisons, not observed reductions in real traffic delay. The predictive policy is not guaranteed to outperform the others. Limitations include ideal sensing, a simple aggregate service model, constant forecast rates within each prediction, online training on only two hours, and unvalidated synthetic arrival timing. Video, physical sensors, exact geometry, actual signal phases, pedestrian movements, and real-time deployment are absent. This is an offline illustrative Digital Twin with a small ML forecasting component, not a deployed twin of a real intersection.
'''
    (ROOT / 'docs').mkdir(exist_ok=True)
    (ROOT / 'docs/REPORT_SECTION_2_7.md').write_text(report, encoding='utf-8')


def main():
    arrivals = pd.read_csv(ROOT / 'data/arrivals_by_second.csv')
    if len(arrivals) != 7200 or arrivals.second.tolist() != list(range(7200)):
        raise ValueError('Expected 7,200 consecutive seconds; run prepare_arrivals.py')
    (ROOT / 'results').mkdir(exist_ok=True)
    summaries = []
    for policy in POLICIES:
        summary, logs, decisions, syncs = run_policy(arrivals, policy)
        summaries.append(summary)
        logs.to_csv(ROOT / f'results/timeseries_{policy}.csv', index=False)
        decisions.to_csv(ROOT / f'results/decisions_{policy}.csv', index=False)
        if policy == 'digital_twin':
            syncs.to_csv(ROOT / 'results/synchronizations_digital_twin.csv', index=False)
    summary = pd.DataFrame(summaries)
    summary.to_csv(ROOT / 'results/summary.csv', index=False)
    write_report(summary)
    print(summary.drop(columns='arrival_sha256').to_string(index=False))


if __name__ == '__main__':
    main()
