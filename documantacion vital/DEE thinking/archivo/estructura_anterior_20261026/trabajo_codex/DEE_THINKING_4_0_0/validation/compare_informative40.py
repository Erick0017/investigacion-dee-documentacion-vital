"""Directed CPC3/3.5 -> native4 regression, with separate interpreter processes.

Original modules are read-only test references, never a dependency of DEE4.
Full RAW/clocks are hashed at every recorded boundary. Numeric/functional
readouts are not used as inputs by either process.
"""
from array import array
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding='utf-8')


def record(o):
    r = o.record
    return {'tick': o.tick, 'coordinate': [o.coordinate.x, o.coordinate.y, o.coordinate.z],
            'raw': o.raw, 'clock': o.clock, 'state': r.state, 'semantic': r.semantic,
            'load': r.s_reg, 'direction': [r.dx, r.dy, r.dz]}


def canonical_channel(name):
    if name.startswith('observed_consequence.') and name.rsplit('.', 1)[-1] in ('1', '-1'):
        return name.rsplit('.', 1)[0]
    return name


def receipts(runtime):
    return [{'id': r.id, 'kind': str(r.kind), 'status': str(r.status),
             'requested_tick': r.requested_tick, 'effective_tick': r.effective_tick,
             'channels': [canonical_channel(x) for x in r.channels], 'reason': r.reason}
            for r in runtime.receipts]


def digest(world, organization):
    runtime = world.runtime
    raw = runtime.raw_copy()
    clock = runtime.clock_copy()
    ports = world.view(organization).spec.ports
    row = {'tick': runtime.current_tick,
           'raw_sha256': hashlib.sha256(array('Q', raw).tobytes()).hexdigest(),
           'clock_sha256': hashlib.sha256(array('Q', clock).tobytes()).hexdigest(),
           'ports': {name: record(runtime.observe(q)) for name, q in ports.items()},
           'receipts': receipts(runtime)}
    if organization == 'adapter':
        body = world.view('body').observe()
        row['relation'] = {'delta': body.delta, 'centers_available': body.centers_available,
                           'supports_intact': body.supports_intact}
    return row


def configurations(evidence):
    configs = []
    base = evidence / 'experimentos/seleccion_revisable'
    frozen = json.loads((base / 'EXPERIMENT_CONFIG.json').read_text(encoding='utf-8'))
    for entry in frozen['cases']:
        config = {k: v for k, v in entry.items() if k not in ('id', 'kind')}
        configs.append({'id': 'policy/' + entry['id'], 'family': 'policy', 'configuration': config,
                        'points': [0, 1, 2, 3, 6, 10, 11, 14, 15],
                        'source': str((base / 'casos' / entry['id'] / 'MEASUREMENTS.json').relative_to(evidence))})
    base = evidence / 'experimentos/comparacion_seleccion'
    for family in ['native_discovery', 'native_confirmation', 'post_information']:
        for path in sorted((base / family).glob('*/MEASUREMENTS.json')):
            if path.parent.name in ('late_information_remove', 'identical_copy_sham'):
                continue
            x = json.loads(path.read_text(encoding='utf-8'))
            m = x.get('metadata', {})
            if 'history' not in m or 'origin' not in m or 'arrival_tick' not in m:
                continue
            config = {'origin': m['origin'], 'history': m['history'], 'context': m['context'],
                      'report': m['report'], 'consequence': m['consequence'],
                      'query': m['query_enabled'], 'consequence_enabled': m['consequence_enabled'],
                      'selected_cut': m.get('selected_cut'), 'distance': m['distance'],
                      'post_query': m.get('post_query', False)}
            end = m['arrival_tick'] + (21 if config['post_query'] else 16)
            points = sorted({x for x in [32, 33, 34, 37, 43, 47, 51, 56, 61, 64, end] if x <= end})
            configs.append({'id': 'information/' + family + '/' + path.parent.name,
                            'family': 'information', 'configuration': config, 'points': points,
                            'source': str(path.relative_to(evidence))})
    return configs


def child(args):
    import dee_thinking as d
    expected_version = '3.5.0' if args.mode == 'reference' else '4.0.0'
    if d.__version__ != expected_version or d.kernel_identity()['kernel_version'] != 27:
        raise RuntimeError('Incorrect isolated product: ' + repr((d.__version__, d.__file__)))
    configs = json.loads(args.configuration.read_text(encoding='utf-8'))
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    legacy = args.mode == 'reference'
    if legacy:
        sys.path.insert(0, str(args.evidence_root / 'src'))
        from core.revisable_selection import prepare
        from habitat.native_loop import NativeLoopSession
    rows = []
    for item in configs:
        start = time.monotonic()
        config = item['configuration']
        actual_submitted = False
        cut_applied = False
        if item['family'] == 'policy':
            if legacy:
                cfg = dict(config)
                cfg.pop('late_action_cut', None)
                world, metadata = prepare(**cfg)
                session = None
            else:
                p = d.FinitePolicyParameters()
                p.roles = getattr(d.SourceRole, config['roles'])
                p.actual_class = config['truth']
                p.actual_enabled = config.get('actual_enabled', True)
                p.origin = d.Coordinate(*config.get('origin', [30, 30, 30]))
                session = d.FinitePolicySession.create(p)
                world = session.world
            organization = 'selection'
        else:
            if legacy:
                session = NativeLoopSession.create(**config)
            else:
                p = d.NativeInformationParameters()
                p.seed_path = d.reference_seed_path()
                p.origin = d.Coordinate(*config['origin'])
                p.history = getattr(d.BasalHistory, config['history'])
                p.context = config['context']
                p.actual_class = config['consequence']
                p.information_load = config['report']
                p.query_enabled = config['query']
                p.actual_enabled = config['consequence_enabled']
                p.source_cut = config['selected_cut'] or ''
                p.distance = config['distance']
                p.post_query = config['post_query']
                session = d.NativeInformationSession.create(p)
            world = session.world
            organization = 'adapter'

        def boundary():
            nonlocal world, session, actual_submitted, cut_applied
            tick = world.runtime.current_tick
            if item['family'] == 'policy':
                if tick == 1 and config.get('late_action_cut') and not cut_applied:
                    edit = d.ResearchStateEdit()
                    edit.coordinate = world.view('selection').spec.ports['first_action']
                    edit.raw = 0
                    edit.label = 'explicit matched late action removal'
                    if legacy:
                        world = world.diagnostic_fork([edit], True)
                    else:
                        session = session.diagnostic_fork([edit], True)
                        world = session.world
                    cut_applied = True
                if legacy:
                    if tick == 2 and config.get('actual_enabled', True) and not actual_submitted:
                        for tag in ('negative', 'positive'):
                            world.submit('actual.' + tag + '.' + str(config['truth']), 1, tick)
                        actual_submitted = True
                else:
                    session.process_boundary()
            elif legacy:
                session._physical_inputs()
            else:
                session.process_boundary()

        frames = []
        folder = output / item['id']
        folder.mkdir(parents=True, exist_ok=True)
        for target in item['points']:
            while world.runtime.current_tick < target:
                boundary()
                if legacy:
                    world.advance()
                else:
                    session.advance()
            boundary()
            frames.append(digest(world, organization))
            if target in (item['points'][0], item['points'][len(item['points']) // 2], item['points'][-1]):
                path = folder / ('T' + str(target) + '.deetsnap')
                if legacy:
                    world.save_snapshot(str(path))
                else:
                    session.save_snapshot(str(path))
        # Complete operational load/continue is a separate technical check.
        technical = None
        if not legacy:
            path = folder / 'OPERATIVE_FINAL.deetsnap'
            session.save_snapshot(str(path))
            cls = d.FinitePolicySession if item['family'] == 'policy' else d.NativeInformationSession
            restored = cls.load_snapshot(str(path))
            before = digest(session.world, organization)
            loaded = digest(restored.world, organization)
            session.advance(2)
            restored.advance(2)
            technical = {'load_same': before == loaded,
                         'future_same': digest(session.world, organization) == digest(restored.world, organization),
                         'journal_same': [(x.tick, x.operation, x.interface_name, x.value, x.receipt_id) for x in session.journal] ==
                                         [(x.tick, x.operation, x.interface_name, x.value, x.receipt_id) for x in restored.journal]}
        result = {'id': item['id'], 'configuration': config, 'source': item['source'],
                  'frames': frames, 'technical': technical, 'seconds': time.monotonic() - start}
        put(folder / 'MEASUREMENTS.json', result)
        rows.append(result)
    report = {'mode': args.mode, 'version': d.__version__, 'module': d.__file__,
              'kernel': d.kernel_identity(), 'cases': rows}
    put(output / 'REPORT.json', report)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['reference', 'new'])
    p.add_argument('--evidence-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--configuration', type=Path)
    p.add_argument('--python-reference', type=Path)
    p.add_argument('--python-new', type=Path)
    a = p.parse_args()
    if a.mode:
        child(a)
        return
    if not a.python_reference or not a.python_new:
        p.error('both isolated interpreter paths are required')
    a.output.mkdir(parents=True, exist_ok=True)
    config = configurations(a.evidence_root)
    config_path = a.output / 'FROZEN_COMPARISONS.json'
    put(config_path, config)
    commands = []
    for mode, python in [('reference', a.python_reference), ('new', a.python_new)]:
        command = [str(python), '-I', '-B', str(Path(__file__).resolve()), '--mode', mode,
                   '--evidence-root', str(a.evidence_root.resolve()), '--output', str((a.output / mode).resolve()),
                   '--configuration', str(config_path.resolve())]
        started = time.monotonic()
        run = subprocess.run(command, cwd=str(a.output.resolve()), text=True, capture_output=True, timeout=240)
        (a.output / (mode + '.stdout.log')).write_text(run.stdout, encoding='utf-8')
        (a.output / (mode + '.stderr.log')).write_text(run.stderr, encoding='utf-8')
        commands.append({'mode': mode, 'argv': command, 'exit_code': run.returncode, 'seconds': time.monotonic() - started})
        put(a.output / 'COMMANDS.json', commands)
        if run.returncode:
            raise SystemExit(run.returncode)
    reference = json.loads((a.output / 'reference/REPORT.json').read_text(encoding='utf-8'))
    new = json.loads((a.output / 'new/REPORT.json').read_text(encoding='utf-8'))
    checks = []
    for old, fresh in zip(reference['cases'], new['cases']):
        frames = []
        for x, y in zip(old['frames'], fresh['frames']):
            keys = ['tick', 'raw_sha256', 'clock_sha256', 'ports', 'receipts']
            if old['id'].startswith('information/'):
                keys.append('relation')
            fields = {key: x[key] == y[key] for key in keys}
            frames.append({'tick': x['tick'], 'fields': fields, 'equal': all(fields.values())})
        checks.append({'id': old['id'], 'frames': frames, 'all_physical_and_receipt_fields_equal':
                       old['id'] == fresh['id'] and len(old['frames']) == len(fresh['frames']) and all(x['equal'] for x in frames),
                       'operational_restore_checks': fresh['technical']})
    report = {'reference_version': reference['version'], 'new_version': new['version'],
              'cases': checks, 'cases_reproduced': len(checks),
              'all_equal': len(reference['cases']) == len(new['cases']) and bool(checks) and
                           all(x['all_physical_and_receipt_fields_equal'] and all(x['operational_restore_checks'].values()) for x in checks),
              'intentional_interface_differences': ['4.0 native class metadata replaces Python session JSON',
                  'NativeInformation declares both actual sign codecs before T0; reference declares one; unused channels do not change RAW/clocks',
                  'receipt channel suffix for actual sign normalized only for comparison'],
              'scope': 'deterministic replay/adaptation regression, not additional independent science samples'}
    put(a.output / 'COMPARISON_REPORT.json', report)
    print(json.dumps({'cases': len(checks), 'all_equal': report['all_equal']}))
    if not report['all_equal']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
