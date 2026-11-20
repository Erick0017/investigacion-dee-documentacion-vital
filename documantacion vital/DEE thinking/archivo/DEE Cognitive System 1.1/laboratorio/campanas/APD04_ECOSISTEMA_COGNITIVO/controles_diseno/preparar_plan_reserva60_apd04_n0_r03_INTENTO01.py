"""N0 R03 DRAFT assembler: optional explicit prepared actuator codec.

R01/R02 bytes remain immutable. R02's 64-event calendar is preserved exactly.
Only --actuator-codec R02 prepends one literal t=0 command. This script never
closes a plan, selects a candidate/sensor, starts a driver, or imports Native.
"""
import argparse
import contextlib
import copy
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
R02_SHA = 'cd3a1e4bc18909bad994f0494fd51cccd9f6d0e45a134d2612c5bb02acce752b'
CODECS = ('R01', 'R02')
CONFIG_EVENT = {
    'at_seconds': 0,
    'kind': 'command',
    'request_id': 'apd04_reserve_r03_prepare_actuator_codec_R02',
    'argv': ['configurar-actuador-ecosistema', 'R02'],
}


def dependencies():
    import importlib.util
    import hashlib
    path = HERE / 'preparar_plan_reserva60_apd04_n0_r02.py'
    if hashlib.sha256(path.read_bytes()).hexdigest() != R02_SHA:
        raise ValueError('Preserved R02 changed; never silently reconstruct it')
    spec = importlib.util.spec_from_file_location('preserved_R02_N0_only', path)
    r02 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(r02)
    return r02, r02.base()


def build(r02, r01, life, world, sensor, codec='R01'):
    if codec not in CODECS:
        raise ValueError('Prepared codec must be R01 or R02, never inferred from an answer')
    plan = r02.make(r01, life, world, sensor)
    original = copy.deepcopy(plan['events'])
    if codec == 'R02':
        plan['events'].insert(0, copy.deepcopy(CONFIG_EVENT))
        if plan['events'][1:] != original:
            raise AssertionError('Only the one initial command may be added')
    elif plan['events'] != original:
        raise AssertionError('R01 codec must preserve the entire R02 calendar')
    if plan['duration_seconds'] < 3600:
        raise AssertionError('The native reserve window may not be shortened')
    plan['assembly_revision'] = 'APD04.reserve60.N0.R03.optional_prepared_actuator_codec'
    plan['prepared_actuator_codec'] = {
        'selected_literal': codec,
        'option_default': 'R01: no configuration event; do not infer or assert current actor state',
        'R02_initial_command': copy.deepcopy(CONFIG_EVENT) if codec == 'R02' else None,
        'attribution': 'P0 externally prepared conversion of a formed selector emission, not acquired selection or R2 regulation',
        'proposal_R02': 'formed selector -1 or 0 maps INSPECT; formed +1 maps USE; unformed/NULL remains unformed, not HOLD or INSPECT',
        'validation_scope': 'Literal command reservation only. No actor method invoked, no material admission or resulting codec proved by this assembler.',
        'operator_must_choose_before_closing_reserve': True,
        'no_runtime_result_conditioned_codec_switch': True,
    }
    plan['initial_timing_scope'] = {
        'R02_config_before_environment_open_at_same_offset0': codec == 'R02',
        'all_original64_offsets_and_relative_order_unchanged': True,
        'configuration_execution_can_delay_original_t0_and_later_work': codec == 'R02',
        'report_actual_lateness_without_shifting_calendar_or_rescuing_responses': True,
        'duration_seconds': plan['duration_seconds'],
        'window_not_3600_seconds_after_configuration_completion': codec == 'R02',
    }
    plan['status'] = 'DRAFT_NOT_AUTHORIZED_FOR_NATIVE'
    return plan


def parse_command_without_execution(ui, argv):
    """Current parser validation only; pending prospective CLI is not a pass."""
    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr):
            parsed = ui.command_parser().parse_args(argv)
            rows = ui.literal_rows(parsed)
        return {'parser_accepted': True, 'literal_rows': rows,
                'not_an_execution_or_admission_test': True}
    except (SystemExit, ValueError, AttributeError) as exc:
        return {'parser_accepted': False, 'status': 'PENDING_CURRENT_UI_CONTRACT',
                'exception_type': type(exc).__name__, 'error': str(exc),
                'parser_stderr': stderr.getvalue(),
                'not_an_execution_or_admission_test': True}


def validate(r02, r01, plan):
    root = r02.ROOT
    driver = root / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py'
    proof = r01.validate_n0(plan, driver)
    protocol = r02.load('protocol_R03_N0_only', root / 'sistema/app/protocolo_apd04.py')
    ui = r02.load('UI_R03_parser_N0_only', root / 'sistema/app/usar_dee.py')
    rows = [r for e in plan['events'] if e['kind'] == 'material' for r in e['situations']]
    for row in rows:
        protocol.validate_literal(row)
    for row in plan['after_window_pending']['situations']:
        protocol.validate_literal(row)
    commands = [{'request_id': e['request_id'], 'argv': e['argv'],
                 **parse_command_without_execution(ui, e['argv'])}
                for e in plan['events'] if e['kind'] == 'command']
    if any(name.startswith('dee_thinking') for name in sys.modules):
        raise RuntimeError('N0 assembler must not import the Native engine')
    return {**proof, 'material_rows_validated': len(rows), 'pending_rows_validated': 1,
            'commands_current_parser': commands, 'Native_imports': 0,
            'all_current_commands_parsed': all(c['parser_accepted'] for c in commands),
            'DRAFT_not_executable_even_if_schema_valid': True}


def freeze(r02, out):
    root = r02.ROOT
    paths = [Path(__file__), HERE / 'preparar_plan_reserva60_apd04_n0_r02.py',
             HERE / 'preparar_plan_reserva60_apd04_n0_r01.py', HERE / 'PLAN_RESERVA60_DRAFT_R01.json',
             root / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py',
             root / 'sistema/app/protocolo_apd04.py', root / 'sistema/app/usar_dee.py']
    return r02.freeze_sources(out.parent / (out.stem + '_FUENTES_R03'), paths)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--self-check-n0', action='store_true')
    ap.add_argument('--life')
    ap.add_argument('--world-id')
    ap.add_argument('--sensor', choices=('independent_balanced', 'independent_two_pairs'))
    ap.add_argument('--actuator-codec', choices=CODECS, default='R01',
                    help='Optional explicit P0 codec. Omission retains R01 calendar with no configuration command.')
    args = ap.parse_args()
    r02, r01 = dependencies()
    if args.out.exists():
        raise FileExistsError('Preserve previous DRAFT or proof bytes')
    if args.self_check_n0:
        if args.life or args.world_id or args.sensor:
            raise ValueError('N0 self-check must not select a candidate or sensor')
        cases = []
        for sensor in r02.SENSORS:
            for codec in CODECS:
                plan = build(r02, r01, 'N0_NOT_A_CREATED_LIFE', 'N0_NOT_A_CREATED_WORLD', sensor, codec)
                cases.append({'sensor_option_not_selected': sensor, 'codec_option_not_selected': codec,
                              'checks': validate(r02, r01, plan),
                              'duration_seconds': plan['duration_seconds'],
                              'original64_events_exactly_preserved': True})
        sources = freeze(r02, args.out)
        r02.dump(args.out, {'schema': 'APD04.reserve60.R03.N0_proof', 'cases': cases, 'sources': sources,
                           'status': 'N0_STATIC_PROOF_NOT_A_NATIVE_PLAN', 'Native_ticks': 0,
                           'R01_R02_and_original_DRAFT_unchanged': True,
                           'no_life_sensor_or_codec_selected_for_reserve': True,
                           'no_S_edits_no_word_no_zip_no_contract_changes': True})
        print(json.dumps({'proof': str(args.out), 'cases': len(cases), 'Native_ticks': 0,
                          'not_closed': True}, ensure_ascii=False))
        return
    if not args.life or not args.sensor:
        raise ValueError('Any later DRAFT assembly requires an explicitly supplied life and sensor; no automatic choice')
    plan = build(r02, r01, args.life, args.world_id or args.life, args.sensor, args.actuator_codec)
    checks = validate(r02, r01, plan)
    sources = freeze(r02, args.out)
    r02.dump(args.out, plan)
    r02.dump(args.out.parent / (args.out.stem + '_PREPARACION_R03.json'),
             {'checks': checks, 'sources': sources, 'status': plan['status'],
              'Root_GO_required_in_a_later_explicit_closing_step': True, 'Native_ticks': 0})
    print(json.dumps({'plan': str(args.out), 'status': plan['status'], 'codec': args.actuator_codec,
                      **checks}, ensure_ascii=False))


if __name__ == '__main__':
    main()
