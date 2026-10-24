"""Compare E008 reports across CPU runners without masking discrete changes."""
import json
import math
import sys


def compare(expected, actual, path='$', tolerance=1e-10):
    if type(expected) is not type(actual):
        raise AssertionError(f'{path}: type changed')
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            raise AssertionError(f'{path}: keys changed')
        # Observed cross-run sensitivity: weighted forest only, <0.017 seats.
        forest = (expected.get('ablation') == 'poll_metadata_weighted'
                  and expected.get('method') == 'forest_3_5')
        for key in expected:
            tol = .02 if forest and key in ('continuous_prediction', 'continuous_error') else tolerance
            if key == 'fraction':
                tol = 0
            compare(expected[key], actual[key], f'{path}/{key}', tol)
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise AssertionError(f'{path}: length changed')
        for i, (a, b) in enumerate(zip(expected, actual)):
            compare(a, b, f'{path}/{i}', tolerance)
    elif isinstance(expected, float):
        if not math.isclose(expected, actual, rel_tol=0, abs_tol=tolerance):
            raise AssertionError(f'{path}: {expected} != {actual} (absolute tolerance {tolerance})')
    elif expected != actual:
        raise AssertionError(f'{path}: {expected!r} != {actual!r}')


if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as f:
        expected = json.load(f)
    with open(sys.argv[2], encoding='utf-8') as f:
        actual = json.load(f)
    compare(expected, actual)
    print('E008 reference matches: discrete outputs exact; bounded continuous tolerance.')
