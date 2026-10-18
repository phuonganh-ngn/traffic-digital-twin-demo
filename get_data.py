"""Acquire only Exhibit 2-27; preserve honest provenance on fallback."""
from datetime import datetime, timezone
from pathlib import Path
import io
import json
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
URL = 'https://hcmguide.com/Case2/techprob03/subproblem03a/prob3a2.htm'
PRINT_URL = 'https://hcmguide.com/case2/techprob03/problem_3printablev3.htm'
PUBLISHED = '''start_time,duration_minutes,eastbound,westbound,northbound,southbound,arrivals_EW,arrivals_NS,intersection_total
07:00,15,132,151,34,0,283,34,317
07:15,15,145,184,48,0,329,48,377
07:30,15,161,210,32,1,371,33,404
07:45,15,236,253,24,0,489,24,513
08:00,15,282,239,87,2,521,89,610
08:15,15,248,233,126,2,481,128,609
08:30,15,220,148,68,3,368,71,439
08:45,15,213,201,88,14,414,102,516
'''


def validate(df):
    expected = pd.read_csv(io.StringIO(PUBLISHED))
    if list(df.columns) != list(expected.columns) or len(df) != 8:
        raise ValueError('Expected exactly eight intervals with the specified columns')
    if df.start_time.tolist() != expected.start_time.tolist():
        raise ValueError('Expected 07:00–08:45 at 15-minute intervals')
    numeric = df.drop(columns='start_time')
    if not ((numeric >= 0) & (numeric % 1 == 0)).all().all():
        raise ValueError('Counts must be nonnegative integers')
    if not (df.duration_minutes == 15).all():
        raise ValueError('Intervals must be 15 minutes')
    if not (df.arrivals_EW == df.eastbound + df.westbound).all():
        raise ValueError('EW aggregation mismatch')
    if not (df.arrivals_NS == df.northbound + df.southbound).all():
        raise ValueError('NS aggregation mismatch')
    if not (df.intersection_total == df.arrivals_EW + df.arrivals_NS).all():
        raise ValueError('Intersection total mismatch')
    if not numeric.equals(expected.drop(columns='start_time')):
        raise ValueError('Values differ from the source-checked Exhibit 2-27')
    return df


def extract(html):
    soup = BeautifulSoup(html, 'html.parser')
    # The first AM table has 17 values: four LT/TH/RT/Tot groups + total.
    for table in soup.find_all('table'):
        rows = []
        for tr in table.find_all('tr'):
            cells = [' '.join(c.stripped_strings) for c in tr.find_all(['td', 'th'], recursive=False)]
            if len(cells) != 18 or not re.fullmatch(r'[78]:(?:00|15|30|45)', cells[0]):
                continue
            try:
                values = [int(c.replace(',', '')) for c in cells[1:]]
            except ValueError:
                continue
            e, w, n, s = [values[i] for i in (3, 7, 11, 15)]
            rows.append([cells[0].zfill(5), 15, e, w, n, s, e+w, n+s, values[16]])
        if len(rows) == 8:
            return validate(pd.DataFrame(rows, columns=pd.read_csv(io.StringIO(PUBLISHED)).columns))
    raise ValueError('Could not identify the eight AM Exhibit 2-27 rows')


def main():
    error = None
    try:
        response = requests.get(URL, timeout=25, headers={'User-Agent': 'TrafficDT-EducationalDemo/1.0'})
        response.raise_for_status()
        df = extract(response.text)
        method, detail = 'web_extracted', 'AM table approach Tot columns'
    except (requests.RequestException, ValueError) as exc:
        error = str(exc)
        local = ROOT / 'traffic_intersection_8_intervals_real.csv'
        df = validate(pd.read_csv(local) if local.exists() else pd.read_csv(io.StringIO(PUBLISHED)))
        method = 'fallback_from_published_table'
        detail = str(local.name) if local.exists() else 'Embedded source-checked published values'
    (ROOT / 'data').mkdir(exist_ok=True)
    df.to_csv(ROOT / 'data/traffic_counts.csv', index=False)
    metadata = dict(source_url=URL, printable_url=PRINT_URL,
                    retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                    acquisition_method=method, extraction_method=detail, retrieval_error=error)
    (ROOT / 'data/source_metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(f'Data: {method}; {len(df)} intervals; {df.intersection_total.sum()} vehicles')
    if error:
        print(f'Retrieval error: {error}')


if __name__ == '__main__':
    main()
