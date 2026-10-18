"""Synthetic arrival timestamps conserving every observed 15-minute total."""
import numpy as np
import pandas as pd
from get_data import ROOT, validate


def prepare(counts, seed=42):
    validate(counts)
    rng = np.random.default_rng(seed)
    chunks = []
    for row in counts.itertuples():
        chunks.append(pd.DataFrame({
            'arrivals_NS': rng.multinomial(int(row.arrivals_NS), np.full(900, 1/900)),
            'arrivals_EW': rng.multinomial(int(row.arrivals_EW), np.full(900, 1/900)),
        }))
    out = pd.concat(chunks, ignore_index=True)
    out.insert(0, 'second', np.arange(len(out)))
    return out


if __name__ == '__main__':
    frame = prepare(pd.read_csv(ROOT / 'data/traffic_counts.csv'))
    frame.to_csv(ROOT / 'data/arrivals_by_second.csv', index=False)
    print(f'Saved {len(frame)} synthetic seconds (seed 42).')
