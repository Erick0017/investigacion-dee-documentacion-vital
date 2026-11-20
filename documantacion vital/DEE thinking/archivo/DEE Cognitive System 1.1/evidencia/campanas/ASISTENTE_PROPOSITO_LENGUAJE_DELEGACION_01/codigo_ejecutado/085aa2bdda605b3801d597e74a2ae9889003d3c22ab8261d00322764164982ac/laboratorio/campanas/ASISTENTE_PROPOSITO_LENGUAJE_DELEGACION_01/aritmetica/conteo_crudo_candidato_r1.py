"""APD01 prepared count of two/three independently sensed presences.

No host count is an answer. Each presence0/1 enters one fixed raw channel;
the actual native aggregate is the numeric answer. No Runtime is constructed.
"""
from capacidades import percepcion_cruda_fi01 as raw

VERSION = 'APD01.native_presence_count.candidate.R1'


def native_count(adapter, presences, *, detailed=False):
    if not isinstance(presences, list) or len(presences) not in (2, 3):
        raise ValueError('Initial domain is two or three independent presence samples')
    if any(type(v) is not int or v not in (0, 1) for v in presences):
        raise ValueError('Each independently sampled presence is exact0/1')
    if raw.get(adapter).get('level') != 128:
        raise ValueError('Existing admitted joint128 world required')
    components = [0] * 128
    for i, presence in enumerate(presences):
        components[i] = presence
    trial = raw.frame(adapter, components, detailed=detailed)
    at = trial['datum_tick'] - 2
    gates = [f['fields']['C'] for f in trial['frames'] if f['tick'] == at]
    if len(gates) != 1:
        raise ValueError('One fixed numeric gate is required; no alternate reader')
    gate = gates[0]
    record = int(gate['raw'])
    direction = [((record >> s) & 15) - (16 if ((record >> s) & 15) >= 8 else 0)
                 for s in (48, 52, 56)]
    valid = (gate['site'] == [12, 17, 18] and gate['tick'] == at
             and 0 <= record < 2**64 and bool(record & 0xffffffff)
             and ((record >> 60) & 15) == 1 and direction == [1, -1, -1])
    return {'version': VERSION, 'kind': 'prepared_native_presence_count',
            'independent_presence_samples': presences, 'native_trial': trial,
            'numeric_gate': gate, 'count': ((record >> 32) & 65535) if valid else None,
            'abstention': not valid,
            'scope': 'Prepared independent presence codec and native addition, '
                     'not cardinality semantics acquired by this life. No host '
                     'aggregate, target, output fill-in or alternate reader.'}
