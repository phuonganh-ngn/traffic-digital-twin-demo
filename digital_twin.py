"""Separate observation-based state and deterministic what-if predictions."""
import numpy as np
from simulator import Signal


class DigitalTwin:
    def __init__(self, service_capacity=1):
        self.service_capacity = service_capacity
        self.queues = {'NS': 0, 'EW': 0}
        self.observation_time = None
        self.phase = 'NS_GREEN'
        self.rates = {'NS': 0.0, 'EW': 0.0}
        self.blocks = []
        self.last_block_time = 0
        self.gram = np.eye(4)  # Ridge regularization alpha=1, including intercept.
        self.targets = np.zeros((4, 2))
        self.training_samples = 0
        self.forecast_method = 'past_mean_warmup'

    def synchronize(self, observation):
        self.queues = {'NS': observation.queue_NS, 'EW': observation.queue_EW}
        self.observation_time = observation.time
        self.phase = observation.phase
        history = observation.recent_arrivals
        # No observations at t=0: assume zero; otherwise use all available past
        # seconds up to 60. Never divide early history by an artificial full minute.
        baseline = np.array([sum(x[i] for x in history) / len(history) if history else 0.0
                             for i in range(2)])
        # Synchronization every 10s supplies a completed block, never its future.
        if observation.time > self.last_block_time and observation.time % 10 == 0 and len(history) >= 10:
            block = np.mean(history[-10:], axis=0)
            if len(self.blocks) >= 3:
                features = np.r_[1.0, np.asarray(self.blocks[-3:]).sum(axis=1)]
                self.gram += np.outer(features, features)
                self.targets += np.outer(features, block)
                self.training_samples += 1
            self.blocks.append(block)
            self.last_block_time = observation.time
        if self.training_samples >= 6:
            features = np.r_[1.0, np.asarray(self.blocks[-3:]).sum(axis=1)]
            prediction = np.maximum(0.0, features @ np.linalg.solve(self.gram, self.targets))
            # Blend with the observed mean to stabilize this tiny online model.
            baseline = 0.5 * baseline + 0.5 * prediction
            self.forecast_method = 'online_ridge_blended'
        self.rates = dict(zip(('NS', 'EW'), baseline))

    def score(self, green_seconds, horizon=120):
        if not self.phase.endswith('_GREEN'):
            raise ValueError('Prediction is evaluated at start of green')
        queues = self.queues.copy()
        signal = Signal()
        signal.group = self.phase.split('_')[0]
        signal.choose(green_seconds)
        waiting = 0.0
        for _ in range(horizon):
            if signal.needs_plan:
                signal.choose(30)
            for group in queues:
                capacity = self.service_capacity if signal.phase == f'{group}_GREEN' else 0
                queues[group] = max(0.0, queues[group] + self.rates[group] - capacity)
            waiting += sum(queues.values())
            signal.advance()
        return waiting

    def decide(self):
        scores = {g: self.score(g) for g in (15, 30, 45)}
        # Prefer 30 in a numerical tie, then the shorter duration.
        best = min(scores.values())
        tied = [g for g, value in scores.items() if abs(value - best) < 1e-9]
        selected = min(tied, key=lambda g: (g != 30, g))
        return selected, {f'score_{g}': score for g, score in scores.items()}
