import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from get_data import ROOT, PUBLISHED, validate, extract
from prepare_arrivals import prepare
from simulator import TrafficEnvironment, Observation, Signal
from digital_twin import DigitalTwin
from run_demo import run_policy
from controllers import POLICIES


def test_source_counts():
    counts = validate(pd.read_csv(ROOT / 'data/traffic_counts.csv'))
    pd.testing.assert_frame_equal(counts, pd.read_csv(io.StringIO(PUBLISHED)))
    assert counts.intersection_total.sum() == 3785
    broken = counts.copy()
    broken.loc[0, 'eastbound'] += 1
    with pytest.raises(ValueError):
        validate(broken)


def test_extraction_ignores_movements_and_pm():
    frame = pd.read_csv(io.StringIO(PUBLISHED))
    rows = []
    for r in frame.itertuples():
        cells = [r.start_time.lstrip('0')]
        for total in (r.eastbound, r.westbound, r.northbound, r.southbound):
            cells += ['0', str(total), '0', str(total)]
        cells += [str(r.intersection_total)]
        rows.append('<tr>' + ''.join(f'<td>{x}</td>' for x in cells) + '</tr>')
    pd.testing.assert_frame_equal(extract('<table>'+''.join(rows)+'</table>'), frame)


def test_arrival_conservation():
    counts = pd.read_csv(ROOT / 'data/traffic_counts.csv')
    arrivals = pd.read_csv(ROOT / 'data/arrivals_by_second.csv')
    assert len(arrivals) == 7200
    assert arrivals.second.tolist() == list(range(7200))
    pd.testing.assert_frame_equal(arrivals, prepare(counts))
    for i, row in counts.iterrows():
        block = arrivals.iloc[i*900:(i+1)*900]
        for g in ('NS', 'EW'):
            assert block[f'arrivals_{g}'].sum() == row[f'arrivals_{g}']


@pytest.mark.parametrize('policy', POLICIES)
def test_logged_physics(policy):
    frame = pd.read_csv(ROOT / f'results/timeseries_{policy}.csv')
    arrivals = pd.read_csv(ROOT / 'data/arrivals_by_second.csv')
    for g in ('NS', 'EW'):
        assert (frame[f'queue_{g}'] >= 0).all()
        assert (frame[f'arrivals_{g}'].cumsum() == frame[f'served_{g}'].cumsum()+frame[f'queue_{g}']).all()
        np.testing.assert_array_equal(frame[f'arrivals_{g}'], arrivals[f'arrivals_{g}'])
        assert (frame.loc[frame.phase != f'{g}_GREEN', f'served_{g}'] == 0).all()
        assert (frame[f'served_{g}'] <= 1).all()
    assert not ((frame.served_NS > 0) & (frame.served_EW > 0)).any()
    assert (frame.accumulated_waiting == (frame.queue_NS+frame.queue_EW).cumsum()).all()
    # Every complete phase, including both all-red transitions, has exact duration.
    segments = [(name, len(part)) for _, part in frame.groupby(frame.phase.ne(frame.phase.shift()).cumsum())
                for name in [part.phase.iloc[0]]]
    cycle = ['NS_GREEN', 'NS_YELLOW', 'ALL_RED', 'EW_GREEN', 'EW_YELLOW', 'ALL_RED']
    for i, (phase, length) in enumerate(segments):
        assert phase == cycle[i % 6]
        if i < len(segments)-1:
            assert length in (15, 30, 45) if phase.endswith('GREEN') else length == (3 if phase.endswith('YELLOW') else 2)
    summary = pd.read_csv(ROOT / 'results/summary.csv').set_index('policy').loc[policy]
    assert summary.total_waiting_vehicle_seconds == frame.accumulated_waiting.iloc[-1]
    assert summary.total_served == frame[['served_NS', 'served_EW']].sum().sum()
    assert summary.final_backlog == frame[['queue_NS', 'queue_EW']].iloc[-1].sum()


def test_twin_separate_and_prediction_read_only():
    env = TrafficEnvironment()
    twin = DigitalTwin()
    twin.synchronize(env.observe())
    env.signal.choose(30)
    env.step(5, 8)
    assert twin.queues == {'NS': 0, 'EW': 0}
    twin.synchronize(env.observe())
    assert twin.queues == env.queues
    assert twin.queues is not env.queues
    before = (env.queues.copy(), env.time, twin.queues.copy(), twin.rates.copy())
    twin.decide()
    assert before == (env.queues, env.time, twin.queues, twin.rates)


def test_no_future_leakage_and_ml_warmup():
    # Change only the unseen suffix: all decisions before its boundary must match.
    original = pd.read_csv(ROOT / 'data/arrivals_by_second.csv').iloc[:300].copy()
    altered = original.copy()
    altered.loc[altered.second >= 180, ['arrivals_NS', 'arrivals_EW']] = 10
    left = run_policy(original, 'digital_twin')[2]
    right = run_policy(altered, 'digital_twin')[2]
    pd.testing.assert_frame_equal(left[left.time < 180].reset_index(drop=True),
                                  right[right.time < 180].reset_index(drop=True))
    assert left.iloc[0].training_samples == 0
    assert left.iloc[0].rate_NS == 0
    assert 'online_ridge_blended' in left.forecast_method.values
    twin = DigitalTwin()
    for t in range(10, 121, 10):
        twin.synchronize(Observation(t, 0, 0, 'NS_GREEN', tuple([(1, 2)] * min(t, 60))))
    assert twin.training_samples == 9
    assert twin.rates['EW'] > twin.rates['NS'] > 0


def test_signal_plan_guard_and_candidate_scores():
    signal = Signal()
    with pytest.raises(ValueError):
        signal.choose(20)
    signal.choose(15)
    with pytest.raises(ValueError):
        signal.choose(30)
    decisions = pd.read_csv(ROOT / 'results/decisions_digital_twin.csv')
    for row in decisions.itertuples():
        scores = {g: getattr(row, f'score_{g}') for g in (15, 30, 45)}
        assert scores[row.chosen_green] == pytest.approx(min(scores.values()))
    twin = DigitalTwin()
    assert twin.decide()[0] == 30


def test_sync_logs_and_identical_input():
    syncs = pd.read_csv(ROOT / 'results/synchronizations_digital_twin.csv')
    assert set(range(0, 7201, 10)).issubset(set(syncs.time))
    for g in ('NS', 'EW'):
        assert (syncs[f'environment_queue_{g}'] == syncs[f'twin_queue_{g}']).all()
    logs = pd.read_csv(ROOT / 'results/timeseries_digital_twin.csv')
    assert (logs.data_age == logs.time-logs.observation_time).all()
    assert logs.data_age.max() <= 9
    assert pd.read_csv(ROOT / 'results/summary.csv').arrival_sha256.nunique() == 1


def test_dashboard_loads_saved_logs():
    from app import load_artifacts
    counts, metadata, summary, logs, decisions = load_artifacts()
    assert len(counts) == 8 and len(summary) == 3 and len(decisions) > 0
    assert metadata['acquisition_method'] in ('web_extracted', 'fallback_from_published_table')
    assert all(len(frame) == 7200 for frame in logs.values())
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT / 'app.py')).run(timeout=30)
    assert not app.exception
    assert len(app.header) == 3
    displayed = app.dataframe[0].value
    assert displayed['Tổng chờ (xe·giây)'].tolist() == summary.total_waiting_vehicle_seconds.tolist()
    assert displayed['Xe còn chờ cuối buổi'].tolist() == summary.final_backlog.tolist()
    assert app.dataframe[1].value.equals(counts)
    assert len(app.slider) == 0  # A single play button inside the replay replaces manual navigation.
    from dashboard_player import player_html
    html = player_html(logs['digital_twin'], decisions)
    assert '__DATA__' not in html
    assert 'Bắt đầu demo' in html
    assert 'Xe đi & phản hồi' in html
