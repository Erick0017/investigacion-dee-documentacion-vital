"""One fixed peripheral environmental consequence channel, not credit A/B.

Explicit candidate feedback timing. Ordinary R3P0 sensory operations are not
modified; this separate declared environmental protocol deliberately tests the
R15 sensitive window. The calendar never reads cost, choice, target or RAW.
"""
from capacidades import mente_unificada_01 as mu
from capacidades import mente_acumulativa_r02 as ma
from capacidades import selector_acrecion_nativo as sel

VERSION = 'APD01.common_cost_391.candidate.R1'
S = (14, 15, 16)
SHAM = (14, 15, 20)
A = (14, 14, 15)
B = (16, 14, 15)


def window(tick, parity):
    if parity not in ('even', 'odd'):
        raise ValueError('Two declared phase parities only')
    k = (int(tick) + 12 + 390) // 391
    if k % 2 != (0 if parity == 'even' else 1):
        k += 1
    return {'boundary': 391 * k, 'boundary_multiplier': k, 'parity': parity,
            'query_tick': 391 * k - 4, 'datum_tick': 391 * k - 1,
            'selection_information': 'Integer calendar only, fixed before consequence value or response'}


def refs(a):
    return [mu.observation(a, site) for site in (A, B)]


def deliver(a, cost, *, parity='even', mode='real'):
    timing = window(a.tick, parity)
    m = mu.get(a)
    if not m.get('current_frontend'):
        raise ValueError('Existing current frontend required; no new anatomy')
    if type(cost) is not int or not 0 <= cost <= 32:
        raise ValueError('One literal environmental consequence scalar0..32')
    if mode not in ('real', 'none', 'sham'):
        raise ValueError('Fixed consequence/control modalities')
    q = timing['query_tick']
    before = refs(a)
    data_pre = {name: mu.observation(a, site) for name, site in [('S', S), ('sham', SHAM)]}
    requests = []
    if mode != 'none':
        site = S if mode == 'real' else SHAM
        # SAME direction0, state1 semantic1 scalar codec as mu.current/R15.
        # This is neither A nor B credit selection and never encodes an action.
        ma.submit(a, 'APD.cost391.' + ('S' if mode == 'real' else 'sham'),
                  site, (0, 0, 0), cost, timing['datum_tick'], requests)
    query = sel.query(a.world, q, 5, 'MU.selector')
    frames = []
    for tick in range(q - 1, q + 9):
        a.run_until(tick)
        frames.append({'tick': a.tick, 'references': refs(a),
                       'E': mu.observation(a, (15,15,15)),
                       'S': mu.observation(a, S), 'sham': mu.observation(a, SHAM),
                       'A_back': mu.observation(a, (14,14,14)),
                       'B_back': mu.observation(a, (16,14,14))})
        if tick == q + 6:
            choice = mu.current_read(a)
    return {'version': VERSION, 'kind': 'fixed_common_environmental_consequence',
            'cost_observation': cost, 'mode': mode, 'timing': timing,
            'references_before': before, 'references_after': refs(a),
            'peripheral_sites_before': data_pre, 'reader': choice,
            'requests': ma.receipts(a, requests) + [sel.receipt(a.world,r) for r in query],
            'frames': frames,
            'scope': 'Prepared environmental query cadence plus one fixed literal-cost '
                     'channel independent of action/optimal answer. Does not select A/B '
                     'credit. A state/response difference is not yet useful policy learning.'}
