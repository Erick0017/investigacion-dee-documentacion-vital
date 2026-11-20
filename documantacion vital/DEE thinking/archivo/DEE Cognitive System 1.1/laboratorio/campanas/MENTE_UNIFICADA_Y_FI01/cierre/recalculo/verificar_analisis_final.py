"""Recálculo archivado desde este ZIP; no DEE, no ticks ni servicios externos."""
from pathlib import Path
import argparse, hashlib, importlib.abc, json, os, runpy, sys, time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prohibir-raiz', type=Path, action='append', default=[])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    planfile = root / 'PLAN_RECALCULO.json'
    plan = json.loads(planfile.read_bytes())
    protected = [p.resolve() for p in args.prohibir_raiz]
    readable_roots = [root, Path(sys.prefix).resolve(), Path(sys.base_prefix).resolve()]
    denied, checks = [], []

    class NoDEE(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if fullname.split('.')[0] in ('dee_thinking', 'dee_universe'):
                denied.append({'event': 'import', 'name': fullname})
                raise PermissionError('El recálculo no importa el motor.')
            return None

    def inside(path, parent): return path == parent or path.is_relative_to(parent)

    def audit(event, values):
        if event in ('subprocess.Popen', 'os.system', 'socket.connect', 'socket.connect_ex'):
            denied.append({'event': event})
            raise PermissionError('El recálculo no ejecuta procesos, decisiones ni red.')
        if event == 'open' and values and isinstance(values[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(values[0])).resolve()
            mode = values[1] if len(values) > 1 else ''
            flags = values[2] if len(values) > 2 else 0
            write = (isinstance(mode, str) and any(c in mode for c in 'wa+x')) or (isinstance(flags, int) and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
            allowed = inside(path, root) if write else any(inside(path, p) for p in readable_roots)
            if not allowed or (not inside(path, root) and any(inside(path, p) for p in protected)):
                denied.append({'event': event, 'path': str(path)})
                raise PermissionError('El recálculo sólo lee la extracción y el intérprete/stdlib, y sólo escribe sus salidas dentro de la extracción.')
        if event in ('os.scandir', 'os.listdir') and values and isinstance(values[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(values[0])).resolve()
            if not any(inside(path, p) for p in readable_roots):
                denied.append({'event': event, 'path': str(path)})
                raise PermissionError('El recálculo no explora carpetas externas ni históricas.')

    sys.meta_path.insert(0, NoDEE()); sys.addaudithook(audit)
    started = time.perf_counter()
    previous_argv, previous_cwd = sys.argv, Path.cwd()
    try:
        os.chdir(root)
        for item in plan['runs']:
            working=(root/item.get('cwd','.')).resolve(strict=True)
            if not inside(working,root):raise ValueError('Working directory outside extraction.')
            os.chdir(working)
            script = (root / item['script']).resolve(strict=True)
            if not inside(script, root): raise ValueError('Script fuera de la extracción.')
            sys.argv = [str(script), *item['args']]
            try: runpy.run_path(str(script), run_name='__main__')
            except SystemExit as error:
                if error.code not in (None, 0): raise RuntimeError('Recálculo terminó con código ' + str(error.code)) from error
            for out in item['outputs']:
                actual = (root / out['actual']).resolve(strict=True)
                reference = (root / out['reference']).resolve(strict=True)
                if not inside(actual, root) or not inside(reference, root): raise ValueError('Salida fuera de la extracción.')
                ah, rh = sha(actual), sha(reference)
                checks.append({'actual': out['actual'], 'reference': out['reference'], 'sha256': ah,
                               'reference_sha256': rh, 'byte_identical': ah == rh})
        os.chdir(root)
        if not checks or not all(c['byte_identical'] for c in checks) or denied:
            raise ValueError('No coinciden todos los recálculos con sus referencias archivadas.')
    finally:
        sys.argv = previous_argv; os.chdir(previous_cwd)
    proof = {'schema': 'MENTE_UNIFICADA_Y_FI01.archived_recalculation.v1', 'all_byte_identical': True,
             'checks': checks, 'denied_attempts': denied, 'host_seconds': time.perf_counter()-started,
             'new_native_ticks': 0, 'native_reproduction': False, 'external_service_execution': False,
             'filesystem_scope': 'Python audit hooks: extraction and interpreter/stdlib reads only; extraction writes only. Not an operating-system sandbox.',
             'scope': 'Cálculos sobre los primarios exportados; no reproduce DEE ni demuestra por sí solo capacidad del participante.'}
    folder = root / 'RECALCULADO_DESDE_ZIP'; folder.mkdir(parents=True, exist_ok=True)
    (folder / 'VERIFICACION_RECALCULO_DESDE_ZIP.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps(proof, ensure_ascii=False))


if __name__ == '__main__': main()


