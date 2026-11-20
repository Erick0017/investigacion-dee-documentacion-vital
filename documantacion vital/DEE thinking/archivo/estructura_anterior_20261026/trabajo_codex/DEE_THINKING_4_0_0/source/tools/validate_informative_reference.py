"""Compare native DEE4 evolution with primary CPC3 measurements.

The laboratory is a read-only fixture provider here. Its runner is never
imported and its saved terminal answers are never returned by the product.
"""
import argparse
import json
from pathlib import Path
import dee_thinking as d


def compare_record(actual, expected):
    r = actual.record
    return {'tick': actual.tick == expected['tick'], 'RAW': actual.raw == expected['RAW'],
            'clock': actual.clock == expected['clock'], 'state': r.state == expected['state'],
            'semantic': r.semantic == expected['semantic'], 'load': r.s_reg == expected['load'],
            'direction': [r.dx, r.dy, r.dz] == expected['direction']}


def policy_case(path):
    original = json.loads(path.read_text(encoding='utf-8'))
    config = original['configuration']
    p = d.FinitePolicyParameters()
    p.roles = getattr(d.SourceRole, config['roles'])
    p.actual_class = config['truth']
    p.origin = d.Coordinate(*config.get('origin', [30, 30, 30]))
    p.actual_enabled = config.get('actual_enabled', True)
    session = d.FinitePolicySession.create(p)
    frames = []
    for expected in original['trace']:
        tick = expected['tick']
        session.run_until(tick)
        if tick == 1 and config.get('late_action_cut'):
            e = d.ResearchStateEdit()
            e.coordinate = session.world.view('selection').spec.ports['first_action']
            e.raw = 0
            e.label = 'reference explicit late action removal'
            session = session.diagnostic_fork([e], True)
        session.process_boundary()
        ports = session.observe().physical_outputs
        checks = {name: compare_record(ports[name], value) for name, value in expected['ports'].items()}
        frames.append({'tick': tick, 'ports': len(checks),
                       'equal': all(all(x.values()) for x in checks.values()),
                       'differences': {k: v for k, v in checks.items() if not all(v.values())}})
    return {'case': path.parent.name, 'reference': str(path), 'frames': frames,
            'equal': all(x['equal'] for x in frames),
            'comparison': 'all recorded RAW, clocks and decoded fields; primary read-only telemetry, not output lookup'}


def native_information_case(path):
    original = json.loads(path.read_text(encoding='utf-8'))
    config = original['metadata']
    p = d.NativeInformationParameters()
    p.seed_path = d.reference_seed_path()
    p.origin = d.Coordinate(*config['origin'])
    p.history = getattr(d.BasalHistory, config['history'])
    p.context = config['context']
    p.actual_class = config['consequence']
    p.information_load = config['report']
    p.query_enabled = config['query_enabled']
    p.actual_enabled = config['consequence_enabled']
    p.source_cut = config.get('selected_cut') or ''
    p.post_query = config.get('post_query', False)
    p.distance = config['distance']
    session = d.NativeInformationSession.create(p)
    frames = []
    for expected in original['trace']:
        tick = expected['tick']
        session.run_until(tick)
        session.process_boundary()
        ports = session.observe().physical_outputs
        checks = {name: compare_record(ports[name], value) for name, value in expected['ports'].items()}
        body = session.world.view('body').observe()
        equal = all(all(x.values()) for x in checks.values()) and body.delta == expected['delta']
        frames.append({'tick': tick, 'ports': len(checks), 'equal': equal,
                       'delta_equal': body.delta == expected['delta'],
                       'differences': {k: v for k, v in checks.items() if not all(v.values())}})
    return {'case': path.parent.name, 'reference': str(path), 'frames': frames,
            'equal': all(x['equal'] for x in frames),
            'comparison': 'all recorded physical ports and relation; extra inert actual-report channels are not physical differences'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = []
    for path in sorted((args.evidence_root / 'experimentos/seleccion_revisable/casos').glob('*/MEASUREMENTS.json')):
        results.append(policy_case(path))
    base = args.evidence_root / 'experimentos/comparacion_seleccion'
    for family in ['native_discovery', 'native_confirmation', 'post_information']:
        for path in sorted((base / family).glob('*/MEASUREMENTS.json')):
            data = json.loads(path.read_text(encoding='utf-8'))
            if 'metadata' in data and 'origin' in data['metadata'] and 'trace' in data:
                # Later intervention arms have another history; the public
                # diagnostic-fork tests cover those separately, not as fresh.
                if family == 'post_information' and path.parent.name in ('late_information_remove', 'identical_copy_sham'):
                    continue
                results.append(native_information_case(path))
    report = {'cases': results, 'cases_reproduced': len(results),
              'all_recorded_fields_equal': bool(results) and all(x['equal'] for x in results),
              'scope': 'directed deterministic regression, not new independent scientific samples'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'cases': len(results), 'equal': report['all_recorded_fields_equal']}))
    if not report['all_recorded_fields_equal']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
