"""PI09 diagnostic: declared whole-world wait, then the unchanged native_pair.

Importing this module uses stdlib only. No Runtime construction, input, state
editing, result calculation, fallback, promotion or automatic retry exists.
"""
from pathlib import Path

VERSION = 'DEE.PI09.explicit_wait_native_arithmetic.R01'
MODES = frozenset({'eci01-pi09-aritmetica'})
WAITS = (0, 36, 64)
SYSTEM_KEY = 'DEE.Cognitive.System.1.1.life.v1'


def validate_literal(row):
    if not isinstance(row, dict) or set(row) != {'modo', 'operacion', 'izquierda', 'derecha', 'espera'}:
        raise ValueError('Exact modo/operacion/izquierda/derecha/espera; no target, result, phase or history fields')
    if row['modo'] not in MODES or row['operacion'] not in ('suma', 'diferencia'):
        raise ValueError('Declared diagnostic arithmetic operation only')
    if any(type(row[k]) is not int or not 0 <= row[k] <= 32 for k in ('izquierda', 'derecha')):
        raise ValueError('Independent integer operands0..32 only')
    if type(row['espera']) is not int or row['espera'] not in WAITS:
        raise ValueError('Only the prospectively declared0/36/64 wait conditions')
    return row


def calendar_query_timing(requested, protected=True):
    """Literal R3P0 integer rule, used to forecast only; no Native observation."""
    if type(requested) is not int or requested < 2:
        raise ValueError('Exact positive requested query tick required')
    effective = requested
    if protected:
        boundary = ((requested-2)//391+1)*391
        if boundary <= requested+8: effective = boundary+2
    wait = effective-requested
    if not 0 <= wait <= 10: raise AssertionError('R3P0 displacement exceeded10')
    return {'requested_query_tick': requested, 'effective_query_tick': effective,
            'wait_ticks': wait, 'protected': bool(protected)}


def forecast(start, wait, protected=True):
    if type(start) is not int or type(wait) is not int or wait not in WAITS:
        raise ValueError('Exact tick and declared wait required')
    # Existing FI128: raw_relative=-19, leaf=start+2, datum=root+38,
    # query=datum-3. This forecasts the unchanged body, never an answer.
    value = calendar_query_timing(start+wait+56, protected)
    query = value['effective_query_tick']
    return {**value, 'before_wait_tick': start, 'condition_wait_ticks': wait,
            'native_pair_start_tick': start+wait, 'numeric_gate_tick': query+1,
            'query_moduli': {'67': query % 67, '391': query % 391, '782': query % 782},
            'predicted_native_pair_end_tick': query+142,
            'predicted_total_advance': query+142-start,
            'scope': 'Pure integer calendar, no sensor, operands, target, decoder or outcome.'}


def validate(a, row):
    validate_literal(row)
    system = Path(__file__).resolve().parents[1]
    if (system/'estado/ACTIVO.json').exists():
        raise ValueError('Diagnostic plugin rejects any selected/product system')
    from dee_thinking.persistence import decode_metadata
    from capacidades import percepcion_cruda_fi01 as raw
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    identity = decode_metadata(entries[SYSTEM_KEY]) if SYSTEM_KEY in entries else {}
    if not isinstance(identity.get('life_id'), str) or 'PI09' not in identity['life_id']:
        raise ValueError('Explicit PI09 diagnostic transport identity required; no principal use')
    if int(a.world.runtime.dimension) != 67 or raw.get(a).get('level') != 128:
        raise ValueError('Existing N67/FI128 complete lived preparation required')
    return row


def _perform(a, row, *, native_pair, physical, protected):
    """Dependency-injected for pure orchestration tests; not an alternate engine."""
    before = physical(a.world)
    start = int(a.tick)
    predicted = forecast(start, row['espera'], protected)
    if row['espera']:
        a.run_until(start+row['espera'])
    if int(a.tick) != start+row['espera']:
        raise ValueError('Actual legal wait disagrees; preserve current future, never retry')
    after_wait = physical(a.world)
    operation = native_pair(a, row['operacion'], row['izquierda'], row['derecha'], detailed=True)
    trial = operation['native_trial']
    if int(trial['query_tick']) != predicted['effective_query_tick']:
        raise ValueError('Actual existing arithmetic calendar differs from sealed forecast; preserve result/future')
    after = physical(a.world)
    numeric = operation['numeric_reader']
    return {'kind': 'PI09_operator_wait_then_existing_native_numeric', 'version': VERSION,
            'literal_operator_request': dict(row), 'before': before, 'after_wait': after_wait, 'after': after,
            'condition_wait_ticks': row['espera'], 'legal_wait_advanced': after_wait['tick']-before['tick'],
            'forecast': predicted, 'actual_query_moduli': {str(m): int(trial['query_tick']) % m for m in (67,391,782)},
            'native_operation': operation, 'numeric_reader': numeric, 'numeric_result': numeric['numeric_result'],
            'fixed_numeric_reader_unchanged': True, 'native_pair_detailed_existing_instrument': True,
            'no_extra_material_query_or_input_for_wait': True,
            'operator_selected_wait_and_operation': True, 'host_computed_binary_result': False,
            'same_lived_adapter': True, 'state_installed': False,
            'scope': 'P0 timing condition plus unchanged independent codec, FI128 body and fixed C reader. '
                     'Detailed=True adds existing nominal-tree read instrumentation, not inputs. '
                     'A numeric error or NULL is retained; no later reader, expected-value substitution, repair or retry.'}


def dispatch(a, row, *, actuator='closed', directory=None):
    validate(a, row)
    if actuator != 'closed': raise ValueError('This diagnostic has no actuator-ablation variant')
    from capacidades import aritmetica_apd_01 as arithmetic
    from capacidades import mente_unificada_01 as mu
    from app.native_tools import physical
    guard = mu.get(a).get('phase_protection')
    if guard and (guard.get('version') != 'MUFI01.sensor_calendar.R3P0' or guard.get('enabled') is not True):
        raise ValueError('Unknown inherited phase protection')
    return _perform(a, row, native_pair=arithmetic.native_pair, physical=physical, protected=bool(guard))


def code_files():
    home = Path(__file__).resolve().parent
    return tuple(home/name for name in (
        Path(__file__).name, 'aritmetica_apd_01.py', 'aritmetica_directa_eci02.py',
        'percepcion_cruda_fi01.py', 'mente_unificada_01.py', 'selector_acrecion_nativo.py'))


def operational_dependencies(a=None, directory=None):
    return {'version': VERSION, 'present': False, 'stateless': True,
            'pending': None, 'uncertain': False,
            'scope': 'No installed device or plugin cognitive state; inherited full-world dependencies remain in their original handlers.'}


def uncertain(a=None): return False
