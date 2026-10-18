"""Exactly three simple policies with a common action interface."""
POLICIES = ('fixed_time', 'direct_adaptive', 'digital_twin')


def choose(policy, observation, twin=None):
    if policy == 'fixed_time':
        return 30, {}
    if policy == 'direct_adaptive':
        current, opposite = ((observation.queue_NS, observation.queue_EW)
                             if observation.phase == 'NS_GREEN'
                             else (observation.queue_EW, observation.queue_NS))
        imbalance = current - opposite
        return (45 if imbalance >= 5 else 15 if imbalance <= -5 else 30), {}
    if policy == 'digital_twin' and twin is not None:
        return twin.decide()
    raise ValueError(f'Unknown or unconfigured policy: {policy}')
