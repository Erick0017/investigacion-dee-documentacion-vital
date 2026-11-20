"""Finite technical replay of D01 inputs; no new scientific success criteria.

The checker compares actual complete state after native evolution. It never
sends an expected direction, target, answer map or corrected policy to U0.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from common import ROOT, identity, put, sha, digest, operational, record
from supervisor import OwnedJob
import integrated
import order_memory
import action_feedback
import language

WINDOWS = (0, 3, 5, 8, 14, 15, 19, 20, 23, 33, 40)
SOURCES = ('common.py', 'integrated.py', 'order_memory.py', 'action_feedback.py', 'language.py', 'test_integrated_technical.py')


def normalized(world):
    value = operational(world)
    cache = {k: v for k, v in value['metadata'].items() if k.startswith('dee_thinking.organizational.')}
    value['metadata'] = {k: v for k, v in value['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    return value, cache


def full_equal(a, b):
    return {'N': a.runtime.dimension == b.runtime.dimension,
            'tick': a.runtime.current_tick == b.runtime.current_tick,
            'RAW_complete': a.runtime.raw_copy() == b.runtime.raw_copy(),
            'clocks_complete': a.runtime.clock_copy() == b.runtime.clock_copy()}


def passive(session):
    before = digest(session.world); op = operational(session.world)
    observations = [session.observe() for _ in range(3)]
    checks = {'physical_unchanged': digest(session.world) == before,
              'operative_unchanged': operational(session.world) == op,
              'same_observation_without_advance': observations[0] == observations[1] == observations[2]}
    assert all(checks.values()); return {'tick': before['tick'], 'checks': checks}


def child_continue(snapshot, final_tick, output):
    output.mkdir(parents=True, exist_ok=False)
    s = integrated.Session.load(snapshot); initial = digest(s.world); pending = s.receipts()
    s.advance_to(final_tick); final = s.save(output / 'CONTINUED.deetsnap')
    put(output / 'CONTINUATION.json', {'classification': 'TECHNICAL_OTHER_PROCESS_CONTINUATION',
        'parent_sha256': sha(snapshot), 'initial': initial, 'pending_receipts_before': pending,
        'final': final, 'source_sha256': sha(__file__),
        'scope': 'Only persisted physical/operative state was loaded. No preparation, teaching log, expected result or evaluator file was opened.'})


def child_command(argv, output, timeout=60):
    started = time.monotonic(); job = None
    with (output / 'child.stdout.log').open('wb') as stdout, (output / 'child.stderr.log').open('wb') as stderr:
        process = subprocess.Popen(argv, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            job = OwnedJob(process)
            try: process.wait(timeout=timeout)
            except subprocess.TimeoutExpired: job.terminate(); process.wait(timeout=15); raise
        except BaseException:
            if process.poll() is None:
                if job: job.terminate()
                else: process.kill()
                process.wait(timeout=15)
            raise
        finally:
            if job: job.close()
    result = {'argv': argv, 'exit_code': process.returncode, 'elapsed_seconds': time.monotonic() - started}
    put(output / 'CHILD_COMMAND.json', result); assert process.returncode == 0
    return result


def invalid_input_tests(session):
    checks = []
    cases = ({'payload': 1.5}, {'payload': True}, {'payload': -1}, {'payload': 65536},
             {'tick': 8.5}, {'tick': True}, {'tick': -1}, {'tick': 2**64}, {'kind': 'automatic_answer'})
    for replacement in cases:
        before = digest(session.world); op = operational(session.world); requests = deepcopy(session.requests)
        request = {'port': 'order.read', 'payload': 3, 'tick': 9, 'kind': 'probe'}; request.update(replacement)
        error = None
        try: session.stimulate([request])
        except (TypeError, ValueError, RuntimeError) as exc: error = repr(exc)
        state_unchanged = digest(session.world) == before and operational(session.world) == op and session.requests == requests
        checks.append({'request': request, 'rejected': error is not None, 'error': error, 'state_unchanged': state_unchanged})
        assert error is not None and state_unchanged
    for tick in (8.5, True, -1, 2**64):
        before = digest(session.world); error = None
        try: session.advance_to(tick)
        except (TypeError, ValueError, RuntimeError) as exc: error = repr(exc)
        assert error is not None and digest(session.world) == before
        checks.append({'advance_tick': tick, 'rejected': True, 'error': error, 'state_unchanged': True})
    return checks


def diagnostic_uint64(session, output):
    import dee_thinking as d
    before = digest(session.world); op = operational(session.world)
    edit = d.ResearchStateEdit(); edit.coordinate = d.Coordinate(1, 1, 1)
    edit.raw = d.pack_record(65535, 65535, 1, -1, 1, 1); edit.clock = 2**63 + 123
    edit.label = 'FORMAT_ONLY_DIAGNOSTIC_UINT64_NO_EVOLUTION'
    world = session.world.diagnostic_fork([edit], True)
    pre = record(world, (1, 1, 1)); snapshot = output / 'UINT64_FORMAT_ONLY.deetsnap'; world.save_snapshot(str(snapshot))
    restored = d.OrganizationalWorld.load_snapshot(str(snapshot)); post = record(restored, (1, 1, 1))
    checks = full_equal(world, restored); checks.update({'exact_record': pre == post,
        'clock_exact_above_float_precision': int(post['clock']) == 2**63 + 123,
        'RAW_exact_above_float_precision': int(post['raw']) == edit.raw > 2**53,
        'MAIN_unchanged': digest(session.world) == before and operational(session.world) == op})
    assert all(checks.values())
    return {'classification': 'FORMAT_ONLY_DIAGNOSTIC_FORK', 'checks': checks, 'record': post,
            'snapshot': snapshot.name, 'sha256': sha(snapshot), 'native_ticks_evolved': 0,
            'scope': 'Explicit RAW/clock intervention only in a diagnostic fork, not MAIN or an inversion of time. This tests serialization/types, not physical function of this field combination.'}


def decoder_boundaries():
    import dee_thinking as d
    zero = {'tick': 0, 'site': [0, 0, 0], 'raw': str(d.pack_record(1, 0, 1, 0, 1, 1)),
            'clock': str(2**63 + 7), 'state': 1, 's_reg': 0, 'semantic': 1, 'direction': [1, 0, 1], 'active': True}
    absent = dict(zero, raw='0', state=0, active=False)
    wrong = dict(zero, direction=[0, 0, 0])
    values = [language.decode({'queries': {'SYNTHETIC': value}}) for value in (zero, absent, wrong)]
    assert len(values[0]) == 1 and values[1:] == [[], []]
    return {'classification': 'SYNTHETIC_DECODER_UNIT_FIXTURE_NOT_NATIVE_MEASUREMENT',
            'zero_load_active_readout_retained': values[0], 'missing_response': values[1],
            'outside_decoder_direction': values[2], 'verified': True}


def main_test(output):
    output.mkdir(parents=True, exist_ok=False); started = time.monotonic(); engine = identity()
    sources = {}; versions = output / 'executed_sources'; versions.mkdir()
    for name in SOURCES:
        path = HERE / name; content = path.read_bytes(); (versions / name).write_bytes(content); sources[name] = sha(path)
    report = {'schema': 'CPC6.integrated-technical.v1', 'classification': 'TECHNICAL_REPLAY_OF_D01_INPUT_PROTOCOL',
        'engine': engine, 'source_sha256': sources, 'windows': WINDOWS,
        'input_scenario': {'history': 'AB', 'actual': -1, 'source_values': {'P': 1, 'Q': -1},
                          'actual_scheduled_only_after_forecast_tick': 5, 'checkpoint_tick': 8, 'final_tick': 40},
        'backends': [], 'verified': False,
        'scope': 'Same native input protocol, three computational backends and technical continuations. No new independent learning cases and no expected native output used.'}
    baseline = None; mid_snapshot = None
    for backend in ('DENSE_SEQUENTIAL', 'LAZY', 'DENSE_PARALLEL'):
        folder = output / backend; folder.mkdir(); s = integrated.create(backend=backend)
        s.stimulate(order_memory.experience('AB'))
        s.stimulate([{'port': 'order.read', 'payload': 7, 'tick': 2, 'kind': 'probe', 'origin': 'TECHNICAL_COMMON_READER'}])
        g = s.geometry['adapter']; s.stimulate(action_feedback.source_protocol(g, {'P': 1, 'Q': -1}))
        s.stimulate(action_feedback.query_protocol(g))
        states = []; passivity = []; original_at_mid = None
        for tick in WINDOWS:
            s.advance_to(tick); passivity.append(passive(s))
            if tick == 5: s.stimulate(action_feedback.actual_protocol(g, -1))
            states.append(digest(s.world))
            if tick == 8:
                before_save = digest(s.world); checkpoint = folder / 'PENDING_T8.deetsnap'; s.save(checkpoint)
                assert digest(s.world) == before_save
                scheduled = [r for r in s.receipts() if r['receipt']['status'].lower() == 'scheduled']; assert scheduled
                restored = integrated.Session.load(checkpoint); loaded = full_equal(s.world, restored.world)
                a, ca = normalized(s.world); b, cb = normalized(restored.world)
                loaded.update({'operative_except_framework_cache': a == b,
                               'session_geometry_JSON_contract': json.loads(json.dumps(s.geometry)) == json.loads(json.dumps(restored.geometry)),
                               'session_requests': s.requests == restored.requests,
                               'session_identity': s.identity == restored.identity})
                assert all(loaded.values()); original_at_mid = {'loaded_checks': loaded,
                    'geometry_Python_container_equality_separately': s.geometry == restored.geometry,
                    'geometry_scope': 'Published research geometry is JSON data. Tuple/list conversion is reported separately; coordinates, integers, ports and all stored geometry values must match exactly. RAW/clocks are never normalized.',
                    'framework_cache_equal_separately': ca == cb,
                    'pending_receipts': scheduled, 'snapshot_sha256': sha(checkpoint)}
                if backend == 'DENSE_SEQUENTIAL':
                    mid_snapshot = checkpoint; initial = digest(s.world); op = operational(s.world)
                    fork = s.fork('TECHNICAL_FORK'); geometry = deepcopy(s.geometry); requests = deepcopy(s.requests)
                    fork.geometry['body']['center'][0] = (fork.geometry['body']['center'][0] + 1) % 67
                    fork.requests[0]['origin'] = 'FORK_ONLY_METADATA'; fork.advance_to(9)
                    fork_checks = {'MAIN_physical': digest(s.world) == initial, 'MAIN_operative': operational(s.world) == op,
                                   'geometry_deep': s.geometry == geometry, 'requests_deep': s.requests == requests}
                    assert all(fork_checks.values()); report['deep_fork'] = fork_checks
                    report['invalid_requests_and_advance'] = invalid_input_tests(s)
                    report['uint64'] = diagnostic_uint64(s, folder)
        restored.advance_to(40); same = full_equal(s.world, restored.world)
        a, ca = normalized(s.world); b, cb = normalized(restored.world)
        same['operative_except_framework_cache'] = a == b; assert all(same.values())
        final = s.save(folder / 'FINAL_T40.deetsnap'); restored.save(folder / 'RESTORED_FINAL_T40.deetsnap')
        comparison = states == baseline if baseline is not None else True
        assert comparison
        if baseline is None: baseline = states
        item = {'backend': backend, 'complete_state_SHA_windows': states, 'same_physical_windows_as_DENSE': comparison,
                'passivity': passivity, 'midpoint': original_at_mid, 'continued_equal': same,
                'continued_framework_cache_equal_separately': ca == cb, 'final': final}
        report['backends'].append(item); put(output / 'INCREMENTAL.json', report)
        del restored, s
    other = output / 'OTHER_PROCESS'; other.mkdir()
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(Path(__file__).resolve()), '--resume', str(mid_snapshot),
               '--final-tick', '40', '--output', str(other / 'continued')]
    report['other_process_command'] = child_command(command, other)
    resumed = integrated.Session.load(other / 'continued/CONTINUED.deetsnap')
    expected = integrated.Session.load(output / 'DENSE_SEQUENTIAL/FINAL_T40.deetsnap')
    checks = full_equal(resumed.world, expected.world); a, ca = normalized(resumed.world); b, cb = normalized(expected.world)
    checks['operative_except_framework_cache'] = a == b; assert all(checks.values())
    report['other_process_checks'] = checks; report['other_process_framework_cache_equal_separately'] = ca == cb
    report['decoder_boundaries'] = decoder_boundaries()
    report['source_files_unchanged_during_test'] = {name: sha(HERE / name) == value for name, value in sources.items()}
    report['elapsed_seconds'] = time.monotonic() - started; report['verified'] = True
    put(output / 'TECHNICAL.json', report); print(json.dumps({'verified': True, 'backends': 3, 'other_process': True}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--resume', type=Path); p.add_argument('--final-tick', type=int, default=40); a = p.parse_args()
    if a.resume: child_continue(a.resume, a.final_tick, a.output)
    else: main_test(a.output)
