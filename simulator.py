"""A physical-intersection substitute; contains no twin or policy logic.

Timestamp t describes the boundary before arrivals for second t. A step logs
its end boundary t+1, after arrivals, service, and waiting accumulation.
"""
from dataclasses import dataclass

GROUPS = ('NS', 'EW')


@dataclass(frozen=True)
class Observation:
    time: int
    queue_NS: int
    queue_EW: int
    phase: str
    # Only completed seconds, at most 60, supplied as immutable readings.
    recent_arrivals: tuple


class Signal:
    def __init__(self):
        self.group = 'NS'
        self.stage = 'GREEN'
        self.elapsed = 0
        self.green_seconds = None

    @property
    def phase(self):
        return 'ALL_RED' if self.stage == 'ALL_RED' else f'{self.group}_{self.stage}'

    @property
    def needs_plan(self):
        return self.stage == 'GREEN' and self.green_seconds is None

    def choose(self, seconds):
        if not self.needs_plan or seconds not in (15, 30, 45):
            raise ValueError('Choose 15/30/45 at the start of green only')
        self.green_seconds = seconds

    def advance(self):
        if self.needs_plan:
            raise ValueError('Green duration has not been selected')
        self.elapsed += 1
        duration = self.green_seconds if self.stage == 'GREEN' else (3 if self.stage == 'YELLOW' else 2)
        if self.elapsed == duration:
            self.elapsed = 0
            if self.stage == 'GREEN':
                self.stage = 'YELLOW'
            elif self.stage == 'YELLOW':
                self.stage = 'ALL_RED'
            else:
                self.group = 'EW' if self.group == 'NS' else 'NS'
                self.stage = 'GREEN'
                self.green_seconds = None


class TrafficEnvironment:
    def __init__(self, service_capacity=1):
        if service_capacity <= 0:
            raise ValueError('Service capacity must be positive')
        self.service_capacity = service_capacity
        self.queues = dict.fromkeys(GROUPS, 0)
        self.arrived = dict.fromkeys(GROUPS, 0)
        self.served = dict.fromkeys(GROUPS, 0)
        self.waiting = 0
        self.time = 0
        self.signal = Signal()
        self.history = []

    def observe(self):
        return Observation(self.time, self.queues['NS'], self.queues['EW'],
                           self.signal.phase, tuple(self.history[-60:]))

    def step(self, arrivals_NS, arrivals_EW):
        if self.signal.needs_plan:
            raise ValueError('Controller must choose a green duration')
        phase = self.signal.phase
        arrivals = dict(zip(GROUPS, (arrivals_NS, arrivals_EW)))
        departures = dict.fromkeys(GROUPS, 0)
        for group, count in arrivals.items():
            if count < 0 or int(count) != count:
                raise ValueError('Arrivals must be nonnegative integers')
            self.arrived[group] += int(count)
            self.queues[group] += int(count)
            if phase == f'{group}_GREEN':
                departures[group] = min(self.service_capacity, self.queues[group])
            self.queues[group] -= departures[group]
            self.served[group] += departures[group]
        self.waiting += sum(self.queues.values())
        self.history.append((int(arrivals_NS), int(arrivals_EW)))
        self.time += 1
        row = dict(time=self.time, phase=phase, queue_NS=self.queues['NS'], queue_EW=self.queues['EW'],
                   arrivals_NS=arrivals_NS, arrivals_EW=arrivals_EW,
                   served_NS=departures['NS'], served_EW=departures['EW'], accumulated_waiting=self.waiting)
        self.signal.advance()
        return row
