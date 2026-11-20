"""Finite backend/persistence replay of the longitudinal declared U0 profile.

No response oracle or policy is passed to MAIN. This extends the earlier T40
technical proof to native consolidation and the later opaque-name interfaces.
It is a technical replay, not another independent learning sample.
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
from common import identity, put, sha, digest, operational, record
from supervisor import OwnedJob
from integrated import Session
import order_memory, action_feedback, language, consolidation, curriculum
from action_feedback_access import deduplicate_requests

WINDOWS = (0, 5, 23, 33, 34, 43, 53, 68, 70, 88, 89, 90, 91, 94, 97, 105)
SOURCES = ('common.py', 'integrated.py', 'order_memory.py', 'action_feedback.py',
           'action_feedback_access.py', 'language.py', 'consolidation.py',
           'curriculum.py', 'order_language.py', 'test_longitudinal_technical.py')


def native_equal(a, b):
    return {'N': a.runtime.dimension == b.runtime.dimension,
            'tick': a.runtime.current_tick == b.runtime.current_tick,
            'RAW_complete': a.runtime.raw_copy() == b.runtime.raw_copy(),
            'clocks_complete': a.runtime.clock_copy() == b.runtime.clock_copy()}


def op_equal(a, b):
    va, vb = operational(a), operational(b); caches = []
    for v in (va, vb):
        caches.append({k: x for k, x in v['metadata'].items() if k.startswith('dee_thinking.organizational.')})
        v['metadata'] = {k: x for k, x in v['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    return {'operative_except_framework_cache': va == vb}, caches[0] == caches[1]


def schedule(s, requests, aliases):
    grouped = deduplicate_requests(s.world, requests)
    aliases.append(grouped); s.stimulate(grouped['requests'])


def observed(s):
    out = {'physical': digest(s.world), 'body': order_memory.observations(s.world, s.geometry['body']),
           'consolidation': consolidation.capture(s.world, s.geometry['consolidation'])}
    if s.geometry.get('language'):
        out['language'] = language.capture(s.world, s.geometry['language'])
        out['decoded_actual_products'] = language.decode(out['language'])
    return out


def passive(s):
    before = digest(s.world); before_op = operational(s.world)
    a = observed(s); b = observed(s)
    result = {'tick': before['tick'], 'physical_unchanged': before == digest(s.world),
              'operative_unchanged': before_op == operational(s.world), 'same_readout': a == b}
    assert all(value for key, value in result.items() if key != 'tick'); return result


def resume(snapshot, output):
    output.mkdir(parents=True, exist_ok=False)
    source_hashes = {name: sha(HERE / name) for name in SOURCES}
    s = Session.load(snapshot); before = digest(s.world); pending = s.receipts()
    s.advance_to(105); end = s.save(output / 'CONTINUED_T105.deetsnap')
    put(output / 'CONTINUATION.json', {'classification': 'TECHNICAL_OTHER_PROCESS_CONTINUATION',
        'parent_sha256': sha(snapshot), 'initial': before, 'pending_before': pending,
        'final': end, 'source_sha256': source_hashes,
        'scope': 'Loaded only complete persisted state. No recipe preparation or evaluator/teaching file was opened.'})


def other_process(snapshot, output):
    output.mkdir(); target = output / 'continued'
    argv = [sys.executable, '-I', '-B', '-X', 'utf8', str(Path(__file__).resolve()),
            '--resume', str(snapshot), '--output', str(target)]
    started = time.monotonic(); job = None
    with (output / 'stdout.log').open('wb') as out, (output / 'stderr.log').open('wb') as err:
        child = subprocess.Popen(argv, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            job = OwnedJob(child)
            try: child.wait(timeout=120)
            except subprocess.TimeoutExpired: job.terminate(); child.wait(timeout=15); raise
        except BaseException:
            if child.poll() is None:
                if job: job.terminate()
                else: child.kill()
                child.wait(timeout=15)
            raise
        finally:
            if job: job.close()
    command = {'argv': argv, 'exit_code': child.returncode, 'seconds': time.monotonic() - started}
    put(output / 'COMMAND.json', command); assert child.returncode == 0
    return target, command


def main_test(output, bilateral):
    output.mkdir(parents=True, exist_ok=False); started = time.monotonic(); versions = output / 'executed_sources'; versions.mkdir()
    hashes = {}
    for name in SOURCES:
        content = (HERE / name).read_bytes(); (versions / name).write_bytes(content); hashes[name] = sha(HERE / name)
    report = {'schema': 'CPC6.longitudinal-technical.v1', 'engine': identity(),
        'classification': 'TECHNICAL_REPLAY_LONGITUDINAL_DECLARED_PROFILE', 'source_sha256': hashes,
        'profile': {'N': 67, 'history': 'AB', 'current_actual': -1, 'source_values': {'P': 1, 'Q': -1},
                    'consolidation': 'bilateral' if bilateral else 'open', 'name': 'FORMA_01',
                    'old_renewal_tick': 69, 'new_read_tick': 94, 'horizon': 105},
        'windows': WINDOWS, 'backends': [], 'verified': False,
        'scope': 'Exact equal input protocol; no new sample, expected response, target class or corrected policy supplied. Earlier 13 invalid-input checks are not repeated.'}
    baseline = None; lazy_mid = None; lazy_final = None
    for backend in ('LAZY', 'DENSE_SEQUENTIAL', 'DENSE_PARALLEL'):
        folder = output / backend; folder.mkdir(); s = curriculum.new_individual(backend=backend, bilateral=bilateral); aliases = []
        s.stimulate(order_memory.experience('AB'))
        s.stimulate([{'port': 'order.read', 'payload': 7, 'tick': 2, 'kind': 'probe', 'origin': 'TECHNICAL_COMMON_READER'}])
        s.stimulate(action_feedback.source_protocol(s.geometry['adapter'], {'P': 1, 'Q': -1}))
        schedule(s, action_feedback.query_protocol(s.geometry['adapter']), aliases)
        s.stimulate(curriculum.query(s, 'original', 69, 11))
        s.stimulate(consolidation.query(94, bilateral=bilateral))
        states = []; passive_rows = []; captured = []; mid = None
        for tick in WINDOWS:
            s.advance_to(tick)
            if tick == 5: s.stimulate(action_feedback.actual_protocol(s.geometry['adapter'], -1))
            if tick == 34:
                schedule(s, language.teaching(s.geometry['language']), aliases)
                schedule(s, language.query(s.geometry['language']), aliases)
                mid = folder / 'PENDING_NAME_AND_NATIVE_INPUTS_T34.deetsnap'; s.save(mid)
                pending = [r for r in s.receipts() if r['receipt']['status'].lower() == 'scheduled']; assert pending
                loaded = Session.load(mid); checks = native_equal(s.world, loaded.world); op, cache = op_equal(s.world, loaded.world)
                checks.update(op); checks['geometry_JSON'] = json.loads(json.dumps(s.geometry)) == json.loads(json.dumps(loaded.geometry))
                checks['requests'] = s.requests == loaded.requests; assert all(checks.values())
                midpoint = {'checks': checks, 'framework_cache_equal_separately': cache, 'pending': pending,
                            'python_geometry_container_equal_separately': s.geometry == loaded.geometry, 'sha256': sha(mid)}
                del loaded
            states.append(digest(s.world)); captured.append(observed(s))
            if tick in (68, 90, 97): passive_rows.append(passive(s))
        same = states == baseline if baseline is not None else True; assert same
        if baseline is None: baseline = states
        final = s.save(folder / 'FINAL_T105.deetsnap')
        if backend == 'LAZY':
            lazy_mid = mid; lazy_final = folder / 'FINAL_T105.deetsnap'
            continued = Session.load(mid); continued.advance_to(105)
            continued.save(folder / 'RESTORED_FINAL_T105.deetsnap')
            checks = native_equal(s.world, continued.world); op, cache = op_equal(s.world, continued.world); checks.update(op)
            assert all(checks.values()); report['same_process_continuation'] = {'checks': checks, 'framework_cache_equal_separately': cache}
        report['backends'].append({'backend': backend, 'physical_windows': states, 'same_complete_RAW_clocks_tick_as_LAZY': same,
            'observations': captured, 'passivity': passive_rows, 'midpoint': midpoint, 'final': final, 'alias_transport': aliases})
        put(output / 'INCREMENTAL.json', report); del s
    resumed_path, command = other_process(lazy_mid, output / 'OTHER_PROCESS')
    resumed = Session.load(resumed_path / 'CONTINUED_T105.deetsnap'); expected = Session.load(lazy_final)
    checks = native_equal(resumed.world, expected.world); op, cache = op_equal(resumed.world, expected.world); checks.update(op)
    assert all(checks.values()); report['other_process'] = {'command': command, 'checks': checks, 'framework_cache_equal_separately': cache}
    report['source_files_unchanged_during_test'] = {name: sha(HERE / name) == value for name, value in hashes.items()}
    report['verified'] = True; report['elapsed_seconds'] = time.monotonic() - started
    put(output / 'TECHNICAL.json', report); print(json.dumps({'verified': True, 'backends': 3, 'horizon': 105, 'bilateral': bilateral}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--bilateral', action='store_true'); p.add_argument('--resume', type=Path); a = p.parse_args()
    if a.resume: resume(a.resume, a.output)
    else: main_test(a.output, a.bilateral)
