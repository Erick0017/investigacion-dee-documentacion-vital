"""Explicit operator-selected prepared arithmetic on the SAME lived FI128 tree.

This function never consults R04, chooses a provider, evaluates a goal, teaches,
creates anatomy or substitutes for a failed request. It is an opt-in P0 access
to the already existing native_pair operation, not acquired arithmetic or P2.
Imports of this file do not import DEE or advance ticks.
"""
from __future__ import annotations

VERSION = 'ECI02.operator_selected_native_arithmetic.P0.R01'
MODE = 'eci01-aritmetica-directa'


def validate_literal(row):
    if not isinstance(row, dict) or set(row) != {'modo', 'operacion', 'izquierda', 'derecha'}:
        raise ValueError('Exact modo/operacion/izquierda/derecha; no target, history, route or fallback fields')
    if row['modo'] != MODE or row['operacion'] not in ('suma', 'diferencia'):
        raise ValueError('The operator explicitly selects suma or diferencia')
    if any(type(row[key]) is not int or not 0 <= row[key] <= 32 for key in ('izquierda', 'derecha')):
        raise ValueError('Each independently encoded operand is an exact integer0..32')
    return row


def validate(a, row):
    validate_literal(row)
    from capacidades import percepcion_cruda_fi01 as raw
    if int(a.world.runtime.dimension) != 67 or raw.get(a).get('level') != 128:
        raise ValueError('Existing N67/FI128 preparation required; no anatomy or reset is installed')


def execute(a, row, *, actuator='closed'):
    validate(a, row)
    if actuator != 'closed':
        raise ValueError('This explicit numeric instrument has its declared closed material protocol only')
    from capacidades import aritmetica_apd_01 as arithmetic
    from app.native_tools import physical
    before = physical(a.world)
    native = arithmetic.native_pair(a, row['operacion'], row['izquierda'], row['derecha'], detailed=False)
    return {'kind': 'ECI02_operator_selected_native_numeric', 'version': VERSION,
            'literal_operator_request': dict(row), 'before': before, 'after': physical(a.world),
            'native_operation': native, 'numeric_reader': native['numeric_reader'],
            'numeric_result': native['numeric_reader']['numeric_result'],
            'operator_selected_operation': True, 'same_lived_adapter': True,
            'R04_route_consulted': False, 'provider_called': False,
            'quality_evaluation_or_return': False, 'teacher_delivered': False,
            'fallback_to_failed_request': False,
            'scope': 'Prepared arithmetic representation, FI128 tree and fixed numeric decoder; explicit assisted function. '
                     'This is not an autonomous provider decision, learned binary operation, rescue of the earlier failed reserve, '
                     'general mathematics, promotion evidence or acquired language.'}
