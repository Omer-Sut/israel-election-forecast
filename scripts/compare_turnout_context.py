"""Compare context experiment outputs at the prespecified turnout tolerance."""
import csv
import json
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.compare_turnout_models import compare


def directory(left, right):
    def cell(value):
        try:
            return float(value)
        except ValueError:
            return value
    for name in ('results.json', 'predictions.csv', 'analysis.md', 'inputs-manifest.json', 'chronological-errors.svg'):
        a = (Path(left)/name).read_text(encoding='utf-8')
        b = (Path(right)/name).read_text(encoding='utf-8')
        if name.endswith('.json'):
            compare(json.loads(a), json.loads(b), name)
        elif name.endswith('.csv'):
            compare([[cell(v) for v in r] for r in csv.reader(a.splitlines())],
                    [[cell(v) for v in r] for r in csv.reader(b.splitlines())], name)
        elif a != b:
            raise AssertionError(name+' text differs')


if __name__ == '__main__':
    directory(*sys.argv[1:3])
