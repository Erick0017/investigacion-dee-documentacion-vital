"""Private lifecycle launcher. Requirements/status do not start a DEE owner."""
from pathlib import Path
import argparse
import ast
import json
import os
import secrets
import sys
import time
import importlib.util
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME, SCHEMA, atomic, budget, canonical, closed_native, instance_home, read, safe, sha

def requirements(instance=None):
    window = budget(now=0); deps = RUNTIME / 'dependencias'
    items = {'python313': deps / 'producto/motor/python313/python.exe',
             'pairedPrefix': RUNTIME / 'estado_demo/prefijos/PAR28_COMPLETO/EXPORTACION_SERVICIO.json',
             'systemTemplate': deps / 'PLANTILLA_SISTEMA.json', 'nativeSources': deps / 'SDK_SOURCES.json',
             'nativeAdapter': RUNTIME / 'backend/r06/native_adapter.py', 'owner': RUNTIME / 'backend/r06/sdk_owner.py',
             'privateConnection': RUNTIME / 'configuracion/CONEXION_PRIVADA.json',
             'payloadComplete': deps / 'PRIVATE_PAYLOAD_READY.json'}
    checks = {k: {'present': p.is_file(), 'path': str(p.relative_to(RUNTIME))} for k,p in items.items()}
    value = {'schema': SCHEMA, 'noNativeOpened': True, 'ready': all(x['present'] for x in checks.values()),
             'checks': checks, 'window': window, 'windowExpired': time.time() >= window['hardFinishUtcEpoch']}
    value['effectivePaths'] = {'privateRoot': str(RUNTIME), 'pythonExecutable': sys.executable,
        'store': str(deps / 'sistema_base/app/lives.py'), 'template': str(deps / 'sistema_base'),
        'actor': str(deps / 'sistema_base/capacidades/rbx07_native_v3.py'),
        'prefix': str(RUNTIME / 'estado_demo/prefijos/PAR28_COMPLETO'),
        'ledger': str(RUNTIME / 'estado_demo/LEDGER_SDK_R06.json'),
        'configuration': str(RUNTIME / 'configuracion')}
    spec = importlib.util.find_spec('dee_thinking')
    if spec is not None and spec.origin:
        package = Path(spec.origin).resolve()
        value['effectivePaths']['nativePackage'] = str(package)
        value['nativePackageInsidePrivateRuntime'] = package.is_relative_to(RUNTIME)
        value['effectivePaths']['nativeBinaryCandidates'] = [str(p) for p in package.parent.glob('_native*.pyd')]
    else:
        value['nativePackageInsidePrivateRuntime'] = False
    value['ready'] = value['ready'] and value['nativePackageInsidePrivateRuntime']
    if instance is not None:
        home, cfg = instance_home(instance); value['closedNative'] = closed_native(home, cfg)
        value['instanceId'] = instance
    return value

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    r = sub.add_parser('requisitos'); r.add_argument('--instance')
    s = sub.add_parser('estado'); s.add_argument('--instance', required=True)
    sub.add_parser('crear-token-privado')
    sub.add_parser('crear-ledger-nuevo')
    a = p.parse_args()
    if a.command == 'requisitos': result = requirements(a.instance)
    elif a.command == 'estado':
        home, cfg = instance_home(a.instance)
        result = {'schema': SCHEMA, 'noNativeOpened': True, 'instance': cfg,
                  'serviceLockPresent': (home / 'SDK_SERVICE.lock').exists(),
                  'pairedCheckpointPresent': (home / 'SDK_PAIR.json').exists()}
        if not result['serviceLockPresent']: result['closedNative'] = closed_native(home, cfg)
    elif a.command == 'crear-token-privado':
        path = RUNTIME / 'configuracion/CONEXION_PRIVADA.json'
        atomic(path, {'schema': SCHEMA, 'bind': '127.0.0.1', 'port': 8896, 'token': secrets.token_urlsafe(36)}, new=True)
        result = {'created': str(path.relative_to(RUNTIME)), 'tokenPrinted': False, 'noNativeOpened': True}
    else:
        from ledger_sdk import initialize
        initialize(RUNTIME / 'estado_demo/LEDGER_SDK_R06.json', budget())
        result = {'created': 'estado_demo/LEDGER_SDK_R06.json', 'noNativeOpened': True,
                  'physicalPrefixNotReset': True, 'newBudgetOnly': True}
    print(canonical(result))

if __name__ == '__main__': main()
