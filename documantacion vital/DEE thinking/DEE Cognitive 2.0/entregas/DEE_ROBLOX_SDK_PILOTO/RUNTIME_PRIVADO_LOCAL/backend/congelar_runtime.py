"""Hash only selected SDK source/configuration; no Native/state inventory."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME, SCHEMA, atomic, canonical, sha

def freeze():
    paths = sorted((RUNTIME / 'backend').rglob('*.py'))
    paths += [RUNTIME / 'runtime_local.ps1', RUNTIME / 'configuracion/VENTANA_CONGELADA.json',
              RUNTIME / 'dependencias/SDK_SOURCES.json', RUNTIME / 'dependencias/PLANTILLA_SISTEMA.json',
              RUNTIME / 'dependencias/PRIVATE_PAYLOAD_READY.json']
    rows = [{'file': p.relative_to(RUNTIME).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in paths]
    value = {'schema': SCHEMA, 'scope': 'Selected executable SDK sources and private payload anchors; no token/instances/state/logs.',
             'members': rows, 'NativeOpened': False, 'kernelModified': False}
    target = RUNTIME / 'configuracion/FUENTES_RUNTIME_CONGELADAS.json'; atomic(target, value, new=True)
    return {'manifest': str(target), 'bytes': target.stat().st_size, 'sha256': sha(target), 'members': len(rows)}

if __name__ == '__main__': print(canonical(freeze()))
