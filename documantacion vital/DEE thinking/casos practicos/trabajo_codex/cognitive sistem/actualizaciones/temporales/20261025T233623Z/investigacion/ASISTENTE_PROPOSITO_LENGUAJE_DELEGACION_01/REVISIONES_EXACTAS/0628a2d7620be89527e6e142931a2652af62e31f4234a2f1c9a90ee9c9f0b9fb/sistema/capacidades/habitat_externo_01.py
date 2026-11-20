"""Opt-in external instrumentation for an existing lived N67 E1.

This bridge transduces sin(theta) and native directions. It contains no policy,
target, historical response table, laboratory import or automatic DEE reset.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import time

from dee_thinking.persistence import encode_metadata, decode_metadata
from app.native_tools import physical, observe, exact_receipt

KEY = 'DEE.Cognitive.System.1.1.habitat01.external_bridge.v1'
SYSTEM = Path(__file__).resolve().parents[1]


def _saved(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return json.loads(decode_metadata(entries[KEY])['bridge_state_json']) if KEY in entries else None


def state(a):
    bridge = _saved(a)
    return {'INSTRUMENTO': {'tick': int(a.tick), 'passive': True, 'has_complete_external_bridge': bridge is not None,
            'index': None if bridge is None else bridge['index'],
            'mode': None if bridge is None else bridge['mode'],
            'last_visible_observation': None if bridge is None else bridge['last_observation'],
            'environment_elapsed': None if bridge is None else bridge['environment']['elapsed'],
            'environment': 'Gymnasium Pendulum-v1', 'ticks_per_step': 67},
            'INTERPRETACION': 'Bridge instrument state, not learned Pendulum control. No DEE ticks or queries introduced.'}


def _action(read):
    if read['state'] != 1 or read['semantic'] != 1:
        return {'status': 'NO_QUALIFIED_OUTPUT', 'command': 0}
    vector = tuple(read['direction'])
    if vector == (1, 0, 0): return {'status': 'NATIVE_POSITIVE_X', 'command': 2}
    if vector == (-1, 0, 0): return {'status': 'NATIVE_NEGATIVE_X', 'command': -2}
    if vector == (0, 0, 0): return {'status': 'NATIVE_ACTIVE_NEUTRAL', 'command': 0}
    return {'status': 'CONFLICT_OUTSIDE_FIXED_CODEC', 'command': 0}


class _Worker:
    def __init__(self):
        config = json.loads((SYSTEM / 'contratos/HABITAT_EXTERNO_01.json').read_text(encoding='utf-8'))
        executable = Path(config['external_python'])
        worker = SYSTEM / 'app/habitat_externo/pendulum_worker.py'
        if not executable.is_file() or hashlib.sha256(executable.read_bytes()).hexdigest() != config['external_python_sha256']:
            raise RuntimeError('Declared external interpreter missing or identity changed; no fallback or installation attempted')
        if hashlib.sha256(worker.read_bytes()).hexdigest() != config['worker_sha256']:
            raise RuntimeError('Operational worker identity differs from admitted contract')
        self.p = subprocess.Popen([str(executable), '-I', '-B', '-u', str(worker), '--deps',
            str(SYSTEM / 'runtime/habitat_externo_deps')], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding='utf-8')
        identity = self.call('info')['identity']
        if identity['gymnasium'] != config['gymnasium'] or identity['source_sha256'] != config['pendulum_source_sha256']:
            self.close()
            raise RuntimeError('Published environment identity differs from admitted contract')
        self.identity = identity

    def call(self, op, **values):
        self.p.stdin.write(json.dumps({'op': op, **values}, allow_nan=False) + '\n')
        self.p.stdin.flush()
        line = self.p.stdout.readline()
        if not line: raise RuntimeError('External worker exited: ' + self.p.stderr.read())
        result = json.loads(line)
        if not result['ok']: raise RuntimeError(str(result))
        return result

    def close(self):
        if self.p.poll() is None:
            self.call('close')
            self.p.wait(timeout=5)


def run(a, *, steps=1, seed=71001, reset_environment=False, mode='closed', gravity=10.0):
    """Use Store.mutate; caller explicitly opts into the external process bridge."""
    if type(steps) is not int or not 1 <= steps <= 200 or mode not in ('closed', 'nulled', 'delay1'):
        raise ValueError('Finite 1..200 steps and declared bridge mode required')
    if int(a.world.runtime.dimension) != 67 or not hasattr(a, 'quantity'):
        raise ValueError('Existing full N67 quantity profile required; no substitute life is created')
    if type(reset_environment) is not bool or type(seed) is not int:
        raise ValueError('Explicit reset boolean and integer auditor seed required')
    saved = _saved(a)
    worker = _Worker()
    try:
        if saved is not None and not reset_environment:
            initial = worker.call('restore', snapshot=saved['environment'])
            obs, previous, index = initial['observation'], saved['previous_observation'], saved['index']
        else:
            initial = worker.call('reset', seed=seed, g=float(gravity))
            obs = initial['observation']; previous = list(obs); index = 0
        initial_snapshot = worker.call('snapshot')['snapshot']
        if initial_snapshot['elapsed'] + steps > 200:
            raise ValueError('Requested steps exceed remaining external episode; explicit environmental reset needed, never a DEE reset')
        start = physical(a.world, occupation=True)
        initial_previous = list(previous)
        rows = []
        for _ in range(steps):
            k = max(0, (a.tick - 65) // 67 + 1)
            at = 70 + 67 * k
            visible = previous if mode == 'delay1' else obs
            unbounded = round(73 + 40 * visible[1])
            q = max(1, min(145, unbounded))
            a.quantity.present_object(q, round_index=k)
            requested = [dict(x) for x in a.quantity.state['requests'][-2:]]
            requested.append(a.input('quantity.reader', 7, at - 1, 'probe', 'FIXED_EXTERNAL_SENSOR_READER'))
            a.run_until(at)
            native = observe(a.world, a.quantity.geometry['center'])
            action = _action(native)
            torque = 0 if mode == 'nulled' else action['command']
            began = time.perf_counter()
            response = worker.call('step', torque=torque)
            elapsed_host = time.perf_counter() - began
            rows.append({'index': index, 'tick': int(a.tick), 'observation_before': list(obs),
                'codec': {'value': q, 'unclipped': unbounded, 'saturated': q != unbounded,
                    'delay': 1 if mode == 'delay1' else 0, 'discarded': ['cos(theta)', 'angular_velocity'],
                    'no_reward_or_hidden_state_to_E1': True}, 'native_read': native, 'actuator': action,
                'executed_torque': torque, 'environment_response': response,
                'requests': [exact_receipt(a.world.runtime.receipt(x['id'])) for x in requested],
                'host_worker_seconds': elapsed_host})
            previous = list(obs); obs = response['observation']; index += 1
            bridge = {'environment': worker.call('snapshot')['snapshot'], 'previous_observation': previous,
                'last_observation': obs, 'index': index, 'mode': mode, 'ticks_per_step': 67,
                'delay_buffer': previous, 'explicit_environment_reset_without_DEE_reset': reset_environment}
            a.world.runtime.set_snapshot_metadata(KEY, encode_metadata({'bridge_state_json': json.dumps(bridge, ensure_ascii=False, allow_nan=False)}))
        return {'identity': worker.identity, 'initial_native': start,
            'initial_environment': {'seed': seed, 'g': gravity, 'reset_or_restore': initial,
                'snapshot': initial_snapshot, 'previous_observation': initial_previous},
            'rows': rows, 'final_environment': bridge, 'final_native': physical(a.world, occupation=True),
            'attribution': 'Opt-in external bridge, fixed sin quantization and direction-to-torque mapping. Inherited comparison reference; no learned Pendulum policy claimed.'}
    finally:
        worker.close()
