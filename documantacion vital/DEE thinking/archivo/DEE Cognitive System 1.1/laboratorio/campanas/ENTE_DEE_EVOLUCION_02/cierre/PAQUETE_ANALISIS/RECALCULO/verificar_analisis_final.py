"""Recalculate all three closed EO02 evidence sets after extracting the final ZIP.

This script has no native-engine execution. Original project roots, DEE imports,
network calls and child processes are denied by an audit hook.
"""
from pathlib import Path
import argparse, hashlib, json, os, runpy, sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prohibir-raiz', action='append', default=[], type=Path)
    a = p.parse_args()
    base = Path(__file__).resolve().parent.parent
    forbidden = [q.resolve() for q in a.prohibir_raiz]
    denied = []

    def hook(event, args):
        if event in ('socket.connect', 'socket.connect_ex', 'subprocess.Popen', 'os.system'):
            denied.append(event)
            raise PermissionError('No processes or network in archived recalculation')
        if event == 'import' and args and str(args[0]).startswith('dee_thinking'):
            denied.append(str(args[0]))
            raise PermissionError('No DEE import in archived recalculation')
        if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).resolve()
            if any(path == root or path.is_relative_to(root) for root in forbidden):
                denied.append(str(path))
                raise PermissionError('Original project root is forbidden: ' + str(path))

    sys.addaudithook(hook)
    out = base / 'RECALCULADO_DESDE_ZIP'
    out.mkdir(parents=True, exist_ok=True)
    checks = []

    def execute(name, arguments, actual, reference, issues_key):
        script = base / 'RECALCULO' / name
        sys.argv = [str(script), *[str(x) for x in arguments]]
        try:
            runpy.run_path(str(script), run_name='__main__')
        except SystemExit as e:
            if e.code not in (None, 0):
                raise
        got = actual.read_bytes()
        expected = reference.read_bytes()
        q = json.loads(got)
        row = {'calculation': name, 'byte_identical': got == expected,
               'sha256': hashlib.sha256(got).hexdigest(), 'issues': q[issues_key]}
        checks.append(row)
        if not row['byte_identical'] or row['issues']:
            raise ValueError('Recalculation mismatch: ' + json.dumps(row))

    execute('recalcular_eo02.py', [
        '--primarios', base / 'EVIDENCIA_CAUSAL/RAIZ',
        '--codigos', base / 'EVIDENCIA_CAUSAL/CODIGO_EJECUTADO',
        '--artefactos', base / 'EVIDENCIA_CAUSAL/ARCHIVOS_SERVICIOS',
        '--indice-artefactos', base / 'EVIDENCIA_CAUSAL/INDICE_ARTEFACTOS_FINAL.json',
        '--salida', out / 'RAIZ'], out / 'RAIZ/RECALCULO_EO02.json',
        base / 'RECALCULO/REFERENCIA_RAIZ/RECALCULO_EO02.json', 'discrepancies')
    execute('recalcular_capacidad.py', [
        '--primarios', base / 'EVIDENCIA_CAUSAL/CAPACIDAD',
        '--codigo', base / 'CODIGO_Y_PROTOCOLOS/capacidad/revisiones',
        '--salida', out / 'RECALCULO_CAPACIDAD.json'], out / 'RECALCULO_CAPACIDAD.json',
        base / 'RECALCULO/REFERENCIA_CAPACIDAD.json', 'issues')
    execute('recalcular_contexto.py', [
        '--primarios', base / 'EVIDENCIA_CAUSAL/CONTEXTO',
        '--salida', out / 'RECALCULO_CONTEXTO.json'], out / 'RECALCULO_CONTEXTO.json',
        base / 'RECALCULO/REFERENCIA_CONTEXTO.json', 'discrepancies')
    proof = {'schema': 'EO02.analysis.extracted_recalculation.v1',
             'checks': checks, 'all_three_byte_identical': all(x['byte_identical'] for x in checks),
             'original_roots_forbidden': [str(x) for x in forbidden], 'denied_attempts': denied,
             'new_native_ticks': 0, 'new_worker_executions': 0,
             'scope': 'Archived recalculation from exact final ZIP; not native physical replay or operating-distribution test.'}
    if denied:
        raise ValueError('Unexpected prohibited access attempt')
    (out / 'VERIFICACION_RECALCULO_DESDE_ZIP.json').write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(proof, ensure_ascii=False))


if __name__ == '__main__':
    main()
