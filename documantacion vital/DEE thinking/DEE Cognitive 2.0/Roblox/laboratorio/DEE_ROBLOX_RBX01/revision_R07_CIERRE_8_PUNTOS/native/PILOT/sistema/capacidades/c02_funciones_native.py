"""C02 bounded access to inherited Native lexical/numeric functions.

Import is stdlib-only and creates no world. Every material function requires
the already-owned exact C02 adapter. No Runtime factory, RAW/clock setter,
bank edit, answer table, external calculator or numerical result repair exists.
The caller provides the opportunity/order and persists the returned primaries.
Only the lexical emission selects ADD/DIFF in ``solve``. This fixed coupling
is designed anatomy; it is not learned grammar or an autonomous planner.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

VERSION = 'DEE.RBX01.C02.inherited_native_functions.R01'
SYSTEM_KEY = 'DEE.Cognitive.System.1.1.life.v1'
FORMS = ('luma', 'nara')
SIGN_OPERATION = {1: 'suma', -1: 'diferencia'}
MUTABLE_KEYS = (
    'DEE.Cognitive.System.1.1.APD03.generic_lexicon.R02',
    'DEE.Cognitive.System.1.1.APD04.shared_lexicon.R02',
    'DEE.Cognitive.System.1.1.FI01.raw_perception.B05.v1',
)
DEPENDENCIES = (
    'lexico_generico_apd03_r02.py', 'lexico_compartido_apd04.py',
    'mente_acumulativa_r02.py', 'mente_unificada_01.py',
    'percepcion_cruda_fi01.py', 'aritmetica_apd_01.py',
    'aritmetica_directa_eci02.py', 'pi09_aritmetica_temporal_P0_R01.py',
    'selector_acrecion_nativo.py',
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def _libraries():
    # These imports occur only inside an explicit material call on the owner.
    from capacidades import lexico_generico_apd03_r02 as teacher
    from capacidades import lexico_compartido_apd04 as reader
    from capacidades import pi09_aritmetica_temporal_P0_R01 as arithmetic
    from capacidades import mente_unificada_01 as unified
    return teacher, reader, arithmetic, unified


def identity(adapter, expected_life_id):
    need(type(expected_life_id) is str and
         re.fullmatch(r'ECI02_[A-Z0-9_]+_RBX01_C02_[A-Z0-9_]{1,40}', expected_life_id),
         'Exact experimental C02 identity required; no protected/principal ID')
    need(int(adapter.world.runtime.dimension) == 67, 'Inherited N67 only')
    entries = dict(adapter.world.runtime.snapshot_metadata_entries)
    need(SYSTEM_KEY in entries, 'Whole inherited system identity missing')
    actual = json.loads(entries[SYSTEM_KEY])
    need(actual.get('life_id') == expected_life_id and actual.get('profile') == 'fisica_directa',
         'Wrong owner/profile; no identity substitution or new life')
    # The ROOT actor must also enforce its pinned scope and selected-main guard.
    # This local guard rejects accidental installation under an operational ACTIVO.
    selected = Path(__file__).resolve().parents[1] / 'estado' / 'ACTIVO.json'
    need(not selected.exists(), 'Experimental helper refuses a selected product directory')
    return actual


def _preflight(adapter, expected_life_id):
    actual = identity(adapter, expected_life_id)
    teacher, reader, arithmetic, unified = _libraries()
    # No prepare/admit calls: all physical interfaces and histories must exist.
    teacher.get(adapter)
    reader.get(adapter)
    contract = unified.get(adapter)
    guard = contract.get('phase_protection')
    need(guard and guard.get('version') == 'MUFI01.sensor_calendar.R3P0'
         and guard.get('enabled') is True,
         'Existing R3P0 clock guard required; never install or repair silently')
    return actual, teacher, reader, arithmetic


def _form(form):
    need(type(form) is str and form in FORMS, 'Literal admitted luma/nara cue only')


def _integers(left, right):
    need(type(left) is int and type(right) is int and 0 <= left <= 32 and 0 <= right <= 32,
         'Independent exact raw operands 0..32; no expected result')


def next_lexical_tick(tick):
    need(type(tick) is int and tick >= 0, 'Exact nonnegative physical tick required')
    return (tick // 67 + 1) * 67


def _query_tick(start):
    # Literal pre-existing R3P0 arithmetic calendar. Receives only a clock.
    requested = start + 56
    boundary = ((requested - 2) // 391 + 1) * 391
    return boundary + 2 if boundary <= requested + 8 else requested


def forecast_numeric(start):
    need(type(start) is int and start >= 0, 'Exact numeric start tick')
    body_start = start
    while _query_tick(body_start) % 67 == 19:
        need(body_start - start < 11, 'Prepared phase guard exceeded bound; no search by answer')
        body_start += 1
    return {'start_tick': start, 'guard_paid_ticks': body_start-start,
            'body_start_tick': body_start, 'query_tick': _query_tick(body_start),
            'numeric_read_tick': _query_tick(body_start)+1,
            'end_tick': _query_tick(body_start)+142,
            'scope': 'Clock-only existing guard; no operand, target or observed answer'}


def forecast_solve(start):
    query_tick = next_lexical_tick(start)
    return {'start_tick': start, 'word_input_tick': query_tick,
            'word_read_tick': query_tick+4, 'word_end_tick': query_tick+7,
            'numeric_if_word_valid': forecast_numeric(query_tick+7),
            'end_tick_upper': forecast_numeric(query_tick+7)['end_tick'],
            'order_prepared_by_host': True}


def _deadline(end_tick, deadline_tick):
    need(deadline_tick is None or (type(deadline_tick) is int and end_tick < deadline_tick),
         'C02_TOOL_DEADLINE: insufficient prepared gap; no input admitted or return retimed')


def lesson(adapter, form, sign, *, expected_life_id, revision=False,
           teacher_mode='paired', deadline_tick=None):
    _form(form)
    need(type(sign) is int and sign in (-1, 1), 'Observed signed experience only')
    need(type(revision) is bool and teacher_mode in ('paired', 'omitted', 'desync'),
         'Explicit lesson/control mode only')
    actual, teacher, _, _ = _preflight(adapter, expected_life_id)
    start = int(adapter.tick)
    predicted = next_lexical_tick(start) + (11 if teacher_mode == 'desync' else 0) + 3
    _deadline(predicted, deadline_tick)
    value = teacher.teach(adapter, form, sign, mode=teacher_mode, revision=revision)
    need(int(adapter.tick) == predicted, 'Teacher calendar differs; preserve reached state, no retry')
    return {'version': VERSION, 'kind': 'C02_observed_lexical_experience',
            'life_id': actual['life_id'], 'before_tick': start, 'after_tick': int(adapter.tick),
            'form': form, 'observed_sign': sign, 'revision': revision,
            'teacher_mode': teacher_mode, 'native_lesson': value,
            'assistance': 'Cue/sign came from an observed environmental event; physical teacher and timing prepared',
            'answer_stored_by_this_helper': False}


def recall(adapter, form, *, expected_life_id, deadline_tick=None):
    _form(form)
    actual, _, reader, _ = _preflight(adapter, expected_life_id)
    start = int(adapter.tick)
    predicted = next_lexical_tick(start) + 7
    _deadline(predicted, deadline_tick)
    value = reader.query(adapter, form, detailed=False)
    need(int(adapter.tick) == predicted, 'Reader calendar differs; preserve state, no alternate reader')
    command = value['reader']['formed_native_command']
    need(command is None or type(command) is int and command in (-1, 1),
         'Out-of-contract lexical output; no response completion')
    return {'version': VERSION, 'kind': 'C02_native_recall', 'life_id': actual['life_id'],
            'before_tick': start, 'after_tick': int(adapter.tick), 'form': form,
            'native_word': value, 'native_sign': command,
            'status': 'FORMED' if command is not None else 'NULL',
            'decoder': 'Fixed inherited common36; no teacher sign/target in query or reader'}


def numeric(adapter, operation, left, right, *, expected_life_id, deadline_tick=None):
    need(operation in ('suma', 'diferencia'), 'Only inherited prepared ADD/DIFF')
    _integers(left, right)
    actual, _, _, arithmetic = _preflight(adapter, expected_life_id)
    start = int(adapter.tick)
    predicted = forecast_numeric(start)
    _deadline(predicted['end_tick'], deadline_tick)
    literal = {'modo': 'eci01-aritmetica-directa', 'operacion': operation,
               'izquierda': left, 'derecha': right}
    # This stateless entry uses the existing FI128 body and fixed numeric gate.
    # It performs no external calculation and never calls the APD route/provider.
    value = arithmetic.execute_public(adapter, literal, actuator='closed')
    need(int(adapter.tick) == predicted['end_tick'] and
         value['native_operation']['native_trial']['query_tick'] == predicted['query_tick'],
         'Numeric calendar differs; preserve actual output, no retiming/retry')
    number = value['numeric_result']
    need(number is None or type(number) is int, 'Invalid numeric type; no host repair')
    return {'version': VERSION, 'kind': 'C02_native_numeric', 'life_id': actual['life_id'],
            'before_tick': start, 'after_tick': int(adapter.tick), 'operation': operation,
            'operands': [left, right], 'clock_forecast': predicted,
            'native_numeric': value, 'numeric_result': number,
            'status': 'FORMED' if number is not None else 'NULL',
            'host_computed_arithmetic_result': False,
            'scope': 'Prepared independent operand coding/FI128/decoder; operation choice must be attributed by caller'}


def solve(adapter, form, left, right, *, expected_life_id, deadline_tick=None):
    """One prepared memory -> actual operator -> actual numeric result chain."""
    _form(form)
    _integers(left, right)
    identity(adapter, expected_life_id)
    start = int(adapter.tick)
    forecast = forecast_solve(start)
    _deadline(forecast['end_tick_upper'], deadline_tick)
    remembered = recall(adapter, form, expected_life_id=expected_life_id, deadline_tick=deadline_tick)
    sign = remembered['native_sign']
    if sign is None:
        return {'version': VERSION, 'kind': 'C02_assisted_native_composition',
                'before_tick': start, 'after_tick': int(adapter.tick), 'recall': remembered,
                'operation': None, 'numeric': None, 'numeric_result': None,
                'status': 'NO_LEXICAL_EMISSION', 'no_numeric_fallback': True,
                'host_ordered_pipeline': True}
    operation = SIGN_OPERATION[sign]
    calculated = numeric(adapter, operation, left, right,
                         expected_life_id=expected_life_id, deadline_tick=deadline_tick)
    return {'version': VERSION, 'kind': 'C02_assisted_native_composition',
            'before_tick': start, 'after_tick': int(adapter.tick), 'recall': remembered,
            'operation': operation, 'operation_selected_from_native_sign': sign,
            'fixed_sign_opcode_codec': {'+1': 'ADD', '-1': 'DIFF'},
            'numeric': calculated, 'numeric_result': calculated['numeric_result'],
            'status': calculated['status'], 'host_ordered_pipeline': True,
            'external_calculator_called': False,
            'scope': 'Inherited association selects operation; fixed prepared order and transduction; no planner claim'}


def compose(adapter, forms, data, *, expected_life_id, deadline_tick=None):
    """Explicit two-stage order; actual first integer becomes second operand.

    This can exceed the old Q2 return gap. The ROOT actor must supply a
    prospective deadline large enough or split the stages across opportunities.
    """
    need(isinstance(forms, list) and len(forms) == 2 and isinstance(data, list) and len(data) == 3,
         'Exactly two prepared stages and three raw values')
    for form in forms:
        _form(form)
    for value in data:
        need(type(value) is int and 0 <= value <= 32, 'Exact raw values 0..32')
    start = int(adapter.tick)
    predicted_first = forecast_solve(start)['end_tick_upper']
    _deadline(forecast_solve(predicted_first)['end_tick_upper'], deadline_tick)
    first = solve(adapter, forms[0], data[0], data[1], expected_life_id=expected_life_id,
                  deadline_tick=deadline_tick)
    actual = first['numeric_result']
    if actual is None or not 0 <= actual <= 32:
        return {'version': VERSION, 'kind': 'C02_explicit_two_stage_composition',
                'first': first, 'second': None, 'numeric_result': None,
                'status': 'FIRST_NULL_OR_OUT_OF_NEXT_OPERAND_DOMAIN',
                'host_ordered_pipeline': True, 'no_expected_intermediate_substitution': True}
    second = solve(adapter, forms[1], actual, data[2], expected_life_id=expected_life_id,
                   deadline_tick=deadline_tick)
    return {'version': VERSION, 'kind': 'C02_explicit_two_stage_composition',
            'first': first, 'second': second, 'transported_actual_intermediate': actual,
            'numeric_result': second['numeric_result'], 'status': second['status'],
            'host_ordered_pipeline': True, 'no_expected_intermediate_substitution': True}


def declared_scope():
    return {'version': VERSION, 'forms': list(FORMS), 'reader': 'APD04 inherited common36 at q+4',
            'lesson': 'APD03 legal cue/teacher encounters; no prepare/admit',
            'operations': ['suma', 'diferencia'], 'operand_domain': [0, 32],
            'sum_result_domain': [0, 64], 'difference_result_domain': [-32, 32],
            'mutable_base_metadata_keys': list(MUTABLE_KEYS),
            'required_base_files': list(DEPENDENCIES),
            'autonomous_plan': False, 'new_arithmetic_algorithm_learned': False,
            'Runtime_created_on_import': False, 'Native_ticks_on_import': 0}
