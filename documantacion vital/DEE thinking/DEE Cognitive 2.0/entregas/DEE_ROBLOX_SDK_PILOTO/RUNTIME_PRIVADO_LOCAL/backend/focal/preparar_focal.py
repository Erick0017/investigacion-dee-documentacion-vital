"""FS-only FOCAL6 overlay onto a fresh full-prefix SDK diagnostic instance.

The base preparation remains archived. No Native engine import, state import,
owner or scene is executed by crear(). Import0 is a separate explicit command.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[1])]
from sdk_common import RUNTIME, atomic, canonical, read, sha

HERE = Path(__file__).resolve().parent

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m

def crear(instance_id, session_id, condition, *, execute=False):
    if condition not in ('OSCILANTE', 'CONTROL'): raise ValueError('Closed prospective focal condition')
    source = read(HERE / 'PERFIL_FOCAL_CONGELADO.json')
    for name, expected in source['nativeSources'].items():
        if sha(HERE / name) != expected: raise RuntimeError('Frozen FOCAL Native source changed')
    fs = module(RUNTIME / 'backend/preparacion/preparar_instancia_par28_sdk.py', '_focal_base_fs')
    planned = fs.plan(RUNTIME, instance_id, session_id)
    if not execute:
        return {'profile': 'FOCAL', 'condition': condition, 'maxCycles': 6, 'maxLocalSequence': 12,
                'basePlan': planned, 'newNativeTicks': 0, 'executed': False}
    prepared = fs.prepare(planned, RUNTIME, execute_root_only=True)
    home = RUNTIME / prepared['home']; cfgpath = home / 'INSTANCE.json'; ctxpath = home / 'CONTEXTO_EJECUCION.json'
    marker = home / 'FOCAL_OVERLAY_IN_PROGRESS.json'; atomic(marker, {'condition': condition, 'newNativeTicks': 0}, new=True)
    try:
        cfg = read(cfgpath); ctx = read(ctxpath); archive = home / 'FOCAL_BASE_PREPARATION'; archive.mkdir()
        for name in ('INSTANCE.json', 'CONTEXTO_EJECUCION.json', 'PREPARACION_PAR28_SDK.json'):
            (archive / name).write_bytes((home / name).read_bytes())
        for name, expected in source['nativeSources'].items():
            target = home / 'sistema/capacidades' / name
            (archive / name).write_bytes(target.read_bytes())
            data = (HERE / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected: raise RuntimeError('FOCAL source read changed')
            target.write_bytes(data)
        scopepath = home / 'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json'; scope = read(scopepath)
        scope.update(role='focal', max_cycles=6, max_total_ticks=24576,
                     sources_sha256=source['nativeSources'], code_scope_manifest_sha256=sha(HERE / 'PERFIL_FOCAL_CONGELADO.json'))
        scope['operational_lease']['additionalCycles'] = 6; scope['operational_lease']['cumulativeCycleCap'] = 6
        atomic(scopepath, scope)
        cfg.update(profile='FOCAL', focalCondition=condition, maxCycles=6, maxLocalSequence=12)
        ctx['profile'] = 'FOCAL'; ctx['focalOverlay'] = {'condition': condition,
             'sourceManifest': 'backend/focal/PERFIL_FOCAL_CONGELADO.json',
             'sourceManifestSha256': sha(HERE / 'PERFIL_FOCAL_CONGELADO.json'), 'nativeSources': source['nativeSources'],
             'baseContextSha256': sha(archive / 'CONTEXTO_EJECUCION.json')}
        atomic(cfgpath, cfg); atomic(ctxpath, ctx)
        proof = {'profile': 'FOCAL', 'condition': condition, 'instanceId': cfg['instanceId'], 'lifeId': cfg['lifeId'],
                 'sessionId': cfg['sessionId'], 'home': str(home.relative_to(RUNTIME)), 'contextSha256': sha(ctxpath),
                 'maxCycles': 6, 'maxLocalSequence': 12, 'NativeImported': False, 'newNativeTicks': 0}
        atomic(home / 'PREPARACION_FOCAL.json', proof, new=True); marker.unlink(); return proof
    except BaseException as error:
        atomic(home / 'FOCAL_OVERLAY_INCOMPLETE.json', {'error': repr(error), 'preserved': True, 'noAutomaticRetry': True}, new=True)
        raise

def check_overlay(home):
    cfg = read(home / 'INSTANCE.json'); c = read(home / 'CONTEXTO_EJECUCION.json')
    if cfg.get('profile') != 'FOCAL' or cfg['focalCondition'] not in ('OSCILANTE', 'CONTROL'):
        raise ValueError('FOCAL profile/condition required')
    if any((home / n).exists() for n in ('FOCAL_OVERLAY_IN_PROGRESS.json','FOCAL_OVERLAY_INCOMPLETE.json')):
        raise RuntimeError('Partial FOCAL overlay preserved')
    pin = c['focalOverlay']
    if sha(HERE / 'PERFIL_FOCAL_CONGELADO.json') != pin['sourceManifestSha256']: raise RuntimeError('FOCAL source manifest changed')
    for name, expected in pin['nativeSources'].items():
        if sha(home / 'sistema/capacidades' / name) != expected: raise RuntimeError('FOCAL actor source changed')
    return cfg

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    create = sub.add_parser('crear'); create.add_argument('--instance', required=True); create.add_argument('--session')
    create.add_argument('--condition', choices=('OSCILANTE','CONTROL'), required=True); create.add_argument('--execute-fs-only', action='store_true')
    imp = sub.add_parser('importar'); imp.add_argument('--instance', required=True); imp.add_argument('--context-sha256', required=True)
    imp.add_argument('--deadline-utc-epoch', type=float, required=True); imp.add_argument('--execute-root-only', action='store_true')
    a = p.parse_args()
    if a.command == 'crear': value = crear(a.instance, a.session, a.condition, execute=a.execute_fs_only)
    else:
        home = RUNTIME / 'estado_demo/instancias' / a.instance; check_overlay(home)
        base = module(RUNTIME / 'backend/preparacion/importar_instancia_sdk.py', '_focal_official_import0')
        value = base.import0(home, RUNTIME, execute_root_only=a.execute_root_only, context_sha256=a.context_sha256,
                            deadline_utc_epoch=a.deadline_utc_epoch, validation_campaign=True)
    print(canonical(value))
