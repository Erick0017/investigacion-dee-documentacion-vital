"""APD01 candidate: numeric transduction of the existing native FI01 tree.

This module constructs no Runtime and writes no physical fields. The caller
owns one complete lived adapter and its persistence/epoch protocol. Only its
explicit ``native_pair`` entry advances that owner through the existing
official FI01 operation. Importing/AST inspection advances no ticks.

The actor path never adds the operands or computes their binary difference.
Each operand independently enters one previously admitted raw channel. The
fixed reader decodes one actual native record, before the downstream selector.
The separate affine input/output representation for difference is prepared,
not discovered or learned by the life.
"""
from capacidades import percepcion_cruda_fi01 as raw

VERSION = 'APD01.native_numeric_tree.candidate.R1'
LEVEL = 128
BIAS = 32
AGGREGATE_SITE = [12, 17, 18]
AGGREGATE_DIRECTION = [1, -1, -1]


def encode_pair(operation, left, right):
    """Fixed independent scalar channels; no expected-result argument."""
    if operation not in ('suma', 'diferencia'):
        raise ValueError('Only the two explicitly prepared representations')
    if any(type(v) is not int or not 0 <= v <= 32 for v in (left, right)):
        raise ValueError('Each exact operand must lie in 0..32')
    values = [0] * LEVEL
    values[0] = left
    # Per-operand complement, as in CORE06 B-x coding, is not left-right.
    # It is nevertheless designed representation, not acquired arithmetic.
    values[1] = right if operation == 'suma' else BIAS - right
    return values


def read_numeric(trial, operation):
    """Fixed site/time decoder. It does not read the operand vector/targets."""
    if operation not in ('suma', 'diferencia'):
        raise ValueError('Unknown fixed representation')
    if trial.get('kind') != 'native_joint_raw_perception' or trial.get('level') != LEVEL:
        raise ValueError('Only the existing admitted FI01 joint128 protocol')
    at = int(trial['datum_tick']) - 2
    frames = [f for f in trial['frames'] if int(f['tick']) == at]
    if len(frames) != 1:
        raise ValueError('No unique observation at the frozen numeric gate')
    o = frames[0]['fields']['C']
    n = int(o['raw'])
    if not 0 <= n < 2**64:
        raise ValueError('Exact uint64 record required')
    active = bool(n & 0xffffffff)
    semantic = (n >> 60) & 15
    direction = [((n >> s) & 15) - (16 if ((n >> s) & 15) >= 8 else 0)
                 for s in (48, 52, 56)]
    valid = (o['site'] == AGGREGATE_SITE and int(o['tick']) == at
             and active and semantic == 1 and direction == AGGREGATE_DIRECTION)
    payload = (n >> 32) & 65535
    return {'version': VERSION, 'tick': at, 'observation': o,
            'fixed_site_direction_valid': valid,
            'representation_bias': 0 if operation == 'suma' else BIAS,
            'numeric_result': ((payload if operation == 'suma' else payload - BIAS)
                               if valid else None),
            'abstention': not valid,
            'scope': 'Prepared native aggregation plus fixed numeric transduction; '
                     'not an acquired binary operation, learned procedure choice, '
                     'teacher-free internalization or general mathematics.'}


def native_pair(adapter, operation, left, right, *, detailed=False):
    """One actual FI01 operation on the passed life; no private worlds/retries."""
    metadata = raw.get(adapter)
    if metadata.get('level') != LEVEL:
        raise ValueError('Existing joint128 preparation required; no installation')
    encoded = encode_pair(operation, left, right)
    trial = raw.frame(adapter, encoded, detailed=detailed)
    return {'kind': 'APD01_candidate_numeric_operation', 'version': VERSION,
            'operation': operation, 'operands': [left, right],
            'native_trial': trial, 'numeric_reader': read_numeric(trial, operation),
            'assistance': 'Operator or a separately demonstrated native choice '
                          'selects this operation. Independent fixed operand '
                          'codec, old tree, generic resources, R3P0 calendar and '
                          'numeric decoder remain prepared apparatus.'}

def native_count(adapter,presences,*,detailed=False):
    if not isinstance(presences,list)or len(presences)not in (2,3)or any(type(v)is not int or v not in (0,1)for v in presences):raise ValueError('Two or three independent physical presence samples0/1')
    if raw.get(adapter).get('level')!=LEVEL:raise ValueError('Existing joint128 tree required')
    values=[0]*LEVEL
    for i,v in enumerate(presences):values[i]=v
    trial=raw.frame(adapter,values,detailed=detailed)
    return {'kind':'APD01_prepared_count','presence_samples':presences,'native_trial':trial,
            'numeric_reader':read_numeric(trial,'suma'),'scope':'Prepared separate0/1samples and native aggregation, not acquired cardinality or host counting.'}
