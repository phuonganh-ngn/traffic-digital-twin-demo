"""Session-local simulation, computed one second at a time while the UI runs."""
from collections import deque
import time
import uuid

from digital_twin import DigitalTwin
from simulator import TrafficEnvironment


class RealtimeSimulation:
    def __init__(self, arrivals):
        self._arrivals = tuple((int(ns), int(ew)) for ns, ew in arrivals)
        self.duration = len(self._arrivals)
        self.environment = TrafficEnvironment()
        self.twin = DigitalTwin()
        self.twin.synchronize(self.environment.observe())
        self.running = False
        self.last_tick = None
        self.epoch = uuid.uuid4().hex
        self.decision = None
        self.decision_count = 0
        self.recent_frames = deque(maxlen=60)
        self.events = deque(maxlen=8)
        self.current = dict(time=0, phase='ALL_RED', queue_NS=0, queue_EW=0,
                            arrivals_NS=0, arrivals_EW=0, served_NS=0, served_EW=0,
                            accumulated_waiting=0, twin_queue_NS=0, twin_queue_EW=0,
                            observation_time=0)
        self.recent_frames.append(self.current.copy())

    def reset(self):
        self.__init__(self._arrivals)

    @property
    def finished(self):
        return self.environment.time >= self.duration

    def start(self, now=None):
        if not self.finished:
            self.running = True
            self.last_tick = time.monotonic() if now is None else now

    def pause(self):
        self.running = False
        self.last_tick = None

    def poll(self, now=None):
        """Follow the monotonic clock without skipping any arrival rows.

        Preserve fractional seconds so UI timer jitter does not halve playback
        speed. Catch up at most five seconds; a long suspension freezes the
        remaining time rather than fast-forwarding a whole disconnected period.
        """
        now = time.monotonic() if now is None else now
        if not self.running or self.last_tick is None:
            return
        elapsed = now-self.last_tick
        due = min(5, max(0, int(elapsed)))
        for _ in range(due):
            self.advance()
            if self.finished:
                return
        self.last_tick += due
        if elapsed > 5:
            self.last_tick = now

    def advance(self):
        """One genuine environment step; the Twin receives observations only."""
        if self.finished:
            self.pause()
            return
        env, twin = self.environment, self.twin
        if env.signal.needs_plan:
            obs = env.observe()
            twin.synchronize(obs)
            green, scores = twin.decide()
            self.decision_count += 1
            self.decision = dict(time=env.time, phase=obs.phase, chosen_green=green,
                                 queue_NS=obs.queue_NS, queue_EW=obs.queue_EW,
                                 rate_NS=float(twin.rates['NS']), rate_EW=float(twin.rates['EW']),
                                 forecast_method=twin.forecast_method,
                                 training_samples=twin.training_samples, **scores)
            env.signal.choose(green)
            name = 'Bắc–Nam' if env.signal.group == 'NS' else 'Đông–Tây'
            self.events.append(dict(time=env.time, text=f'Twin chọn đèn xanh cho {name}: {green} giây.'))
        # Only this completed second is exposed to sensors/model, never the suffix.
        ns, ew = self._arrivals[env.time]
        previous_phase = self.current['phase']
        row = env.step(ns, ew)
        twin.synchronize(env.observe())  # Virtual sensor packet every simulated second.
        row.update(twin_queue_NS=twin.queues['NS'], twin_queue_EW=twin.queues['EW'],
                   observation_time=twin.observation_time)
        self.current = row
        self.recent_frames.append(row.copy())
        if ns or ew:
            self.events.append(dict(time=env.time, text=f'Xe mới đến: Bắc–Nam +{ns}, Đông–Tây +{ew}.'))
        if row['phase'] != previous_phase:
            phase_names = {'NS_GREEN': 'Bắc–Nam xanh', 'EW_GREEN': 'Đông–Tây xanh',
                           'NS_YELLOW': 'Bắc–Nam vàng', 'EW_YELLOW': 'Đông–Tây vàng',
                           'ALL_RED': 'Hai hướng cùng đỏ, chuẩn bị đổi hướng'}
            self.events.append(dict(time=env.time, text=phase_names[row['phase']]+'.'))
        if self.finished:
            self.pause()

    def snapshot(self):
        env = self.environment
        return dict(epoch=self.epoch, running=self.running, finished=self.finished,
                    duration=self.duration, current=self.current.copy(),
                    frames=list(self.recent_frames), decision=self.decision,
                    decision_count=self.decision_count, total_arrived=env.arrived.copy(),
                    total_served=env.served.copy(), events=list(self.events),
                    training_samples=self.twin.training_samples)
