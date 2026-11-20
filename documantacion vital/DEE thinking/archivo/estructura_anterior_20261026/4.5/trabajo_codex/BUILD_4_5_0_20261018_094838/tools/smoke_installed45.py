"""Finite public-API replay of an installed 4.5 wheel, never a fixture answer.

Run outside the source tree. The continuation child receives only its snapshot
and output directory. Baseline/child comparisons happen after both trajectories.
"""
from __future__ import annotations
import argparse
import array
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def physical(session):
    rt = session.world.runtime if hasattr(session, 'world') else session.runtime
    def words(values):
        a = array.array('Q', values)
        if sys.byteorder != 'little':
            a.byteswap()
        return hashlib.sha256(a.tobytes()).hexdigest()
    return {'tick': int(rt.current_tick), 'dimension': int(rt.dimension),
            'raw_uint64_le_sha256': words(rt.raw_copy()), 'clocks_uint64_le_sha256': words(rt.clock_copy())}


def identity(expected_native=None):
    import dee_thinking as d
    if sys.version_info[:2] != (3, 13) or sys.maxsize <= 2**32:
        raise AssertionError('CPython 3.13 x64 required')
    if d.__version__ != '4.5.0' or d.kernel_identity()['kernel_version'] != 27:
        raise AssertionError('Not DEE thinking 4.5.0 / v27')
    site = Path(sys.prefix).resolve() / 'Lib/site-packages'
    module = Path(d.__file__).resolve(); native = Path(d._native.__file__).resolve()
    if not module.is_relative_to(site) or not native.is_relative_to(site):
        raise AssertionError('Both Python and native implementation must come from isolated site-packages')
    digest = sha(native)
    if expected_native is not None and digest != expected_native:
        raise AssertionError('Unexpected native binary')
    if any(name.startswith(('dee_universe', 'CPC3', 'CPC4', 'CPC5', 'CPC6', 'CPC7', 'SEM01')) for name in sys.modules):
        raise AssertionError('Historical laboratory imported')
    return {'version': d.__version__, 'kernel': d.kernel_identity(), 'python': sys.executable,
            'module': str(module), 'native': str(native), 'native_sha256': digest, 'loaded_from_site_packages': True}


def operative(session):
    # Public exports only; not a training-map reader or replacement physics.
    return {'identifier': session.identifier, 'forms': list(session.forms), 'geometry': session.geometry,
            'queries': session.queries, 'journal': session.journal,
            'receipts': session.receipts(), 'channels': list(session.world.runtime.channel_names)}


def stable_operative(exported):
    # A prepared descriptor has a construction-state cache; inert load/attach
    # deliberately has no such cache and MUST NOT reinstall the initial body.
    # Preserve that flag in both primaries; compare every other declared field.
    result = json.loads(json.dumps(exported))
    result['geometry'].pop('initial_state_available')
    return result


def initial(output):
    import dee_thinking as d
    from dee_thinking.consolidated import RepertoireSession
    output.mkdir(parents=True, exist_ok=False)
    report = {'schema': 'DEE45.installed-smoke.initial.v1', 'identity': identity(), 'provenance': 'INSTRUMENTO; responses below are measured native products'}
    world = d.create_organization('mobile_pair')
    for j, teacher in enumerate((7, 11)):
        world.submit(f'l{j}.cue', 5, 0); world.submit(f'l{j}.teacher', teacher, 0)
    world.run_until(6)
    for j in range(2):
        world.probe(f'q{j}.query', 13, 6)
    world.run_until(11)
    decoder = d.OutputDecoder()
    mobile = [world.decode(f'q{j}', 'response', decoder).integer for j in range(2)]
    if mobile != [25, 29]:
        raise AssertionError(('Legacy mobile physical regression', mobile))
    report['legacy_mobile'] = {'decoded': mobile, 'physics': physical(world)}
    del world
    cascade = d.create_learnable_cascade(2)
    receipts = d.experience_composition(cascade, [(3, 9), (3, 11)])
    if not all(row['status'] == 'applied' for row in receipts):
        raise AssertionError(('Legacy cascade admission', receipts))
    result = d.query_composition(cascade, 13)
    if result['decoded'] != {'stage0': 25, 'stage1': 39}:
        raise AssertionError(('Legacy cascade physical regression', result))
    report['legacy_cascade'] = {'readout': result, 'receipts': receipts, 'physics': physical(cascade)}
    del cascade
    s = RepertoireSession.create(count=2, identifier='clean-main')
    before = physical(s)
    for _ in range(3):
        s.observe()
    if physical(s) != before:
        raise AssertionError('Passive observation changed RAW/clocks/tick')
    s.acquire_block({'L01': -1, 'L02': 1}, 0)
    query = s.schedule_query(['L01', 'L02'], 67)
    s.run_until(68)
    pending = {'physics': physical(s), 'operative': operative(s)}
    proof = s.save_snapshot(output / 'pending.deetsnap.gz')
    # Same MAIN continues; snapshot is never restored into this baseline.
    s.run_until(70)
    first = s.queries[0]['captured']
    retained = s.query(['L01', 'L02'], 134)
    values1 = [row['value'] for row in first['responses']]
    values2 = [row['value'] for row in retained['responses']]
    if values1 != [-1, 1] or values2 != [-1, 1]:
        raise AssertionError(('New acquired correspondence/regression', values1, values2))
    if not all(r['covered'] and r['receipt']['status'] == 'applied' for panel in (first, retained) for r in panel['responses']):
        raise AssertionError('Acquisition/query admission or coverage failed')
    report['new_main'] = {'query_id': query['id'], 'passive_unchanged': True, 'pending': pending, 'snapshot': proof,
                          'first': first, 'retained': retained, 'physics': physical(s), 'operative': operative(s)}
    del s
    controls = []
    for mode in ('unpaired', 'no_event'):
        c = RepertoireSession.create(count=2)
        c.acquire('L01', -1, 0, mode=mode)
        observed = c.query('L01', 67)
        row = observed['responses'][0]
        if row['covered'] or row['value'] is not None:
            raise AssertionError(('Control turned unavailable into learned value', mode, row))
        controls.append({'mode': mode, 'response': observed, 'physics': physical(c), 'receipts': c.receipts()})
        del c
    report['controls'] = controls
    report['status'] = 'VERIFIED'
    put(output / 'INITIAL.json', report)
    return report


def continuation(snapshot, output, expected_native):
    from dee_thinking.consolidated import load_consolidated_session
    output.mkdir(parents=True, exist_ok=False)
    ident = identity(expected_native)
    s = load_consolidated_session(snapshot)
    pending = {'physics': physical(s), 'operative': operative(s)}
    if s.tick != 68:
        raise AssertionError('Not the pending operational state')
    s.run_until(70)
    first = s.queries[0]['captured']
    retained = s.query(['L01', 'L02'], 134)
    # This child does not read INITIAL.json, teaching maps, targets or references.
    report = {'schema': 'DEE45.installed-smoke.continuation.v1', 'identity': ident, 'pending': pending,
              'first': first, 'retained': retained, 'physics': physical(s), 'operative': operative(s), 'status': 'COMPLETED',
              'information_inputs': ['native pending snapshot', 'fixed query request L01/L02 at tick 134']}
    put(output / 'CONTINUATION.json', report)
    return report


def run_all(output):
    started = time.monotonic()
    parent = initial(output)
    child_output = output / 'child'
    command = [sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--mode', 'continue', '--snapshot', str(output / 'pending.deetsnap.gz'),
               '--output', str(child_output), '--expected-native', parent['identity']['native_sha256']]
    child = subprocess.run(command, cwd=output, capture_output=True, timeout=180)
    (output / 'CHILD.stdout.log').write_bytes(child.stdout); (output / 'CHILD.stderr.log').write_bytes(child.stderr)
    put(output / 'CHILD_COMMAND.json', {'argv': command, 'exit_code': child.returncode, 'timeout_seconds': 180, 'waited': True})
    if child.returncode:
        raise RuntimeError('Separate-process continuation failed; see CHILD.stderr.log')
    observed = json.loads((child_output / 'CONTINUATION.json').read_text(encoding='utf-8'))
    baseline = parent['new_main']
    comparisons = {key: baseline[key] == observed[key] for key in ('first', 'retained', 'physics')}
    comparisons.update({'pending_physics': baseline['pending']['physics'] == observed['pending']['physics'],
                        'pending_operative_stable': stable_operative(baseline['pending']['operative']) == stable_operative(observed['pending']['operative']),
                        'operative_stable': stable_operative(baseline['operative']) == stable_operative(observed['operative']),
                        'inert_load_has_no_initial_material_cache': baseline['operative']['geometry']['initial_state_available'] is True and observed['operative']['geometry']['initial_state_available'] is False})
    if not all(comparisons.values()):
        raise AssertionError(('Posttrajectory baseline/child mismatch', comparisons))
    report = {'schema': 'DEE45.installed-smoke.v1', 'status': 'VERIFIED', 'identity': parent['identity'],
              'legacy_mobile': parent['legacy_mobile']['decoded'], 'legacy_cascade': parent['legacy_cascade']['readout']['decoded'],
              'new_acquired_values': [r['value'] for r in parent['new_main']['first']['responses']],
              'retained_values': [r['value'] for r in parent['new_main']['retained']['responses']],
              'control_unavailable_preserved': True, 'comparison_after_trajectories_only': True,
              'separate_process_continuation': True, 'physical_and_operational_comparisons': comparisons,
              'descriptor_provenance_difference': {'field': 'geometry.initial_state_available', 'prepared': True, 'loaded': False,
                 'scope': 'Construction-state availability, not RAW/clocks, geometry, ports or protocol; exact primary descriptors retained in INITIAL/CONTINUATION.'},
              'elapsed_seconds': time.monotonic() - started}
    put(output / 'SMOKE_REPORT.json', report)
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode', choices=('all', 'initial', 'continue'), default='all')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--snapshot', type=Path)
    p.add_argument('--expected-native')
    args = p.parse_args()
    out = args.output.resolve()
    try:
        if args.mode == 'continue':
            if args.snapshot is None or args.expected_native is None:
                p.error('continue requires --snapshot and --expected-native')
            result = continuation(args.snapshot.resolve(), out, args.expected_native)
        elif args.mode == 'initial':
            result = initial(out)
        else:
            result = run_all(out)
        print(json.dumps({'status': result['status'], 'output': str(out)}, ensure_ascii=False))
    except BaseException as exc:
        out.mkdir(parents=True, exist_ok=True)
        put(out / 'SMOKE_ERROR.json', {'status': 'FAILED', 'error': repr(exc), 'mode': args.mode})
        raise
