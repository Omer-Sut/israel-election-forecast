"""Exact vote-count allocator: Knesset Election Law sections 81–82.

Input must enumerate ALL valid votes by individual electoral list. Seat estimates
and pooled 'other' votes are not valid substitutes. Tied quotients require the
CEC lottery; this implementation stops rather than inventing its outcome.
"""
from fractions import Fraction


class UnresolvedLottery(ValueError):
    """The statutory lottery must resolve equal highest quotients."""


def _complete(votes, seats, target, trace):
    total_votes = sum(votes.values())
    while sum(seats.values()) < target:
        available = {k: Fraction(v, seats[k]+1) for k, v in votes.items()
                     if not (2*v <= total_votes and 2*seats[k] == target)}
        if not available:
            raise ValueError('No eligible remainder recipient')
        highest = max(available.values())
        winners = [k for k, q in available.items() if q == highest]
        if len(winners) != 1:
            raise UnresolvedLottery(f'Equal highest quotients: {winners}')
        winner = winners[0]
        seats[winner] += 1
        trace.append({'recipient': list(winner), 'quotient': str(highest)})
    return seats


def _initial(votes, target):
    quota = sum(votes.values()) // target
    if quota == 0:
        raise ValueError('Counts too small for the statutory integer quota')
    seats = {k: v//quota for k, v in votes.items()}
    if sum(seats.values()) > target:
        raise ValueError('Integer quota overallocates; use actual-scale vote counts')
    return quota, seats


def allocate(votes, *, total_valid_votes, agreements=()):
    """Allocate 120 seats at the inclusive 325/10000 valid-vote threshold.

    Agreement pairs must use individual input IDs; both must pass separately.
    All comparisons use exact rational arithmetic. No random tie policy.
    """
    if (not votes or any(not isinstance(k, str) or not k for k in votes)
            or any(type(v) is not int or v < 0 for v in votes.values())
            or type(total_valid_votes) is not int or total_valid_votes <= 0
            or sum(votes.values()) != total_valid_votes):
        raise ValueError('Require complete nonnegative integer counts summing to total valid votes')
    seen = set()
    pairs = []
    for pair in agreements:
        if (len(pair) != 2 or len(set(pair)) != 2 or
                any(k not in votes or k in seen for k in pair)):
            raise ValueError('Agreements require two distinct known, unpaired lists')
        seen.update(pair)
        pairs.append(tuple(sorted(pair)))
    eligible = {k: v for k, v in votes.items() if v*10000 >= total_valid_votes*325}
    if not eligible:
        raise ValueError('No qualifying lists')
    quota, initial = _initial(eligible, 120)
    active_pairs = [p for p in pairs if all(k in eligible for k in p)]
    paired = {k for p in active_pairs for k in p}
    entities = active_pairs + [(k,) for k in sorted(eligible) if k not in paired]
    entity_votes = {p: sum(eligible[k] for k in p) for p in entities}
    entity_seats = {p: sum(initial[k] for k in p) for p in entities}
    trace = []
    _complete(entity_votes, entity_seats, 120, trace)
    result = {k: 0 for k in votes}
    internal = []
    for p in entities:
        if len(p) == 1:
            result[p[0]] = entity_seats[p]
            continue
        pv = {(k,): eligible[k] for k in p}
        pq, ps = _initial(pv, entity_seats[p])
        pt = []
        _complete(pv, ps, entity_seats[p], pt)
        result.update({k[0]: s for k, s in ps.items()})
        internal.append({'pair': list(p), 'quota': pq, 'remainders': pt})
    if sum(result.values()) != 120 or any(0 < v < 3 for v in result.values()):
        raise ValueError('Invalid final allocation')
    return {'seats': result, 'quota': quota, 'eligible_votes': sum(eligible.values()),
            'initial_seats': initial, 'active_agreements': [list(p) for p in active_pairs],
            'remainder_trace': trace, 'internal_allocations': internal}


def validate_active_forecast(seats, turnout, contract, *, other_lists):
    """Strict current export gate, applied before aggregating other qualifiers."""
    from scripts import baseline
    baseline.validate_forecast(seats, turnout, contract)
    if any(type(v) is not int or v < 0 or v in (1, 2)
           for v in list(seats.values()) + list(other_lists.values())):
        raise ValueError('Individual lists and the combined field cannot have 1 or 2 seats')
    if sum(other_lists.values()) != seats['other_qualifying_lists']:
        raise ValueError('Other qualifying lists require individual allocations before aggregation')
