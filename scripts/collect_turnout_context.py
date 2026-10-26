"""Collect a dated World Bank population snapshot; never infer historical availability."""
import argparse
import base64
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

INDICATORS = ('SP.POP.2024.FE.5Y', 'SP.POP.2024.MA.5Y',
              'SP.POP.2529.FE.5Y', 'SP.POP.2529.MA.5Y',
              'SP.POP.TOTL.FE.ZS', 'SP.POP.65UP.TO.ZS')


def collect(out):
    out.mkdir(parents=True, exist_ok=True)
    manifest = {'retrieved_at': datetime.now(timezone.utc).isoformat(),
                'historical_availability_verified': False,
                'usage': 'Retrospective revised-vintage sensitivity only; not real-time backtest data.',
                'sources': []}
    for indicator in INDICATORS:
        for kind, url in (
            ('observations', f'https://api.worldbank.org/v2/country/ISR/indicator/{indicator}?format=json&per_page=20000'),
            ('metadata', f'https://api.worldbank.org/v2/indicator/{indicator}?format=json')):
            for attempt in range(3):
                try:
                    with urlopen(Request(url, headers={'User-Agent': 'israel-election-forecast-source-audit/1.0'}), timeout=60) as response:
                        raw = response.read()
                    parsed = json.loads(raw)
                    if not isinstance(parsed, list) or len(parsed) != 2 or not parsed[1]:
                        raise ValueError(f'Unexpected/empty response: {url}')
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(2 ** attempt)
            name = f'{indicator}-{kind}.json'
            # Preserve response bytes, including the provider update/version fields.
            (out / name).write_bytes(raw)
            manifest['sources'].append({'indicator': indicator, 'kind': kind, 'url': url,
                'file': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    files = {p.name: p.read_text(encoding='utf-8-sig') for p in sorted(out.iterdir()) if p.is_file()}
    encoded = base64.b64encode(gzip.compress(json.dumps(files).encode())).decode()
    print('E016_SOURCE_BASE64_BEGIN')
    for i in range(0, len(encoded), 8000):
        print(encoded[i:i+8000])
    print('E016_SOURCE_BASE64_END')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=Path('output/turnout-context-source'))
    collect(parser.parse_args().out_dir)
