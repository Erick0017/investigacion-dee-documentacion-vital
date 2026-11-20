"""Continuation API for the explicitly separate R10 complete learned world.

No reconstruction, learned-field write, laboratory import or solved aggregate
is used. Task selection and the external service law remain operator/environment
assistance. The eight separate input values meet through the frozen v27 engine.
"""
from pathlib import Path
import json
from dee_thinking.persistence import encode_metadata, decode_metadata
from capacidades import sensorial_r10 as sensor
from capacidades import integracion_distribuida_mi02_r6 as native
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_evolucion_02_core as core
from capacidades.ente_evolucion_02 import GateEnvironment, LocalEnvironment
from app.native_tools import physical

KEY = 'DEE.Cognitive.System.1.1.EO02.sensorialR10.service.v1'
REVISION = 'EO02.R10.operative_adapter.2'

def check(a):
    s = native.saved(a)
    if not s or s.get('geometry', {}).get('experimental_architecture') != 'EO02_SENSORIAL_R10_T0':
        raise ValueError('A complete R10 snapshot is required. EO01/EO02 R9 is never silently substituted.')
    cf.geometry(a)
    return s['geometry']

def saved(a):
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    return decode_metadata(entries[KEY]) if KEY in entries else None

def put(a, s):
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(json.loads(json.dumps(s, allow_nan=False))))

def state(a):
    g = check(a)
    return {'revision': REVISION, 'architecture': g['architecture_revision'],
            'physical': physical(a.world, occupation=True), 'witness': cf.witness(a),
            'service': saved(a),
            'assistance': 'Prepared remote fan-in4 per side, six generic0 carriers, fixed motor reader, external law and opportunities. Learned contents belong to this distinct T0 life, not EO01.'}

def classify(a, *, observations, reference=None, domain='puertas', reset=False,
             actuator='closed', feedback='real', directory=None, trace=False):
    check(a)
    if not 1 <= len(observations) <= 32 or any(len(v) != 8 or any(type(x) is not int or not 0 <= x <= 32 for x in v) for v in observations):
        raise ValueError('One to32 frames of8 separate raw integers0..32 required; admitted range is not an exhaustive performance guarantee.')
    if reference is not None and (type(reference) is not int or not -64 <= reference <= 64):
        raise ValueError('External calibration outside bounds')
    if domain not in ('puertas', 'trabajadores') or actuator not in ('closed', 'nulled') or feedback not in ('real', 'omit', 'decoupled'):
        raise ValueError('Explicit measured domain and finite physical control mode required')
    s = saved(a) or {'revision': REVISION, 'total_attempts': 0, 'environments': {}, 'closed_environments': []}
    env = s['environments'].get(domain)
    if env is not None and reset:
        s['closed_environments'].append(env)
        env = None
    if env is None:
        env = {'domain': domain, 'reference': 4 if reference is None else reference,
               'created_at_tick': int(a.tick), 'attempts': 0, 'completed_steps': 0,
               'completed_transactions': 0, 'pending_transaction': None,
               'environment_not_cognitive_memory': True, 'reset_never_resets_native_state': True,
               'storage_epoch': domain + '_' + str(a.tick) + '_' + str(s['total_attempts'])}
    elif reference is not None and reference != env['reference']:
        raise ValueError('Declare an external fixture reset to change its credit, never reset DEE')
    s['environments'][domain] = env
    rows = []
    for values in observations:
        raw = list(values)
        s['inflight'] = {'domain': domain, 'raw': raw, 'start_tick': int(a.tick)}
        put(a, s)
        requests = sensor.submit(a, raw)
        adapter = GateEnvironment(env, raw, lambda: put(a, s))
        if domain == 'trabajadores':
            if directory is None:
                raise ValueError('An explicit local experiment directory is required')
            adapter = LocalEnvironment(env, Path(directory) / env['storage_epoch'], raw, lambda: put(a, s))
        result = core.external_episode(a, public=[0, 0], reference=env['reference'],
                                       actuator=actuator, feedback=feedback, trace=trace, environment=adapter)
        from capacidades.arquitectura_distribuida_mi02_r8 import receipts
        s['total_attempts'] += 1
        s['last_domain'] = domain
        s['last_tick'] = int(a.tick)
        s.pop('inflight', None)
        put(a, s)
        rows.append({'raw_components': raw, 'sensory_extra': requests,
                     'sensory_extra_receipts': receipts(a, requests['requests']), 'native': result,
                     'local_service': adapter.last if domain == 'trabajadores' else None,
                     'external_gate': adapter.last if domain == 'puertas' else None})
    return {'revision': REVISION, 'rows': rows, 'final': state(a),
            'scope': 'Eight material inputs combined with one learned relative criterion in this R10 world. A/B transfer is isomorphic, not8 learned policies, 16/32joint capacity, free language or general control.'}
