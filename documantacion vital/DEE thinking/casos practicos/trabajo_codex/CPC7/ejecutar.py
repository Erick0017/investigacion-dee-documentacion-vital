"""Entrada pública finita. Ejecuta trayectorias, nunca respuestas guardadas."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from common import put
from supervisor import OwnedJob


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operacion', choices=['referencia', 'vida', 'control', 'demo', 'demo-repertorio', 'recalcular'])
    parser.add_argument('--out', type=Path, required=True, help='Directorio NUEVO para la ejecución; no sobrescribe evidencia')
    parser.add_argument('--config', type=Path)
    parser.add_argument('--case-id')
    parser.add_argument('--timeout', type=int, default=300)
    a = parser.parse_args()
    if not 1 <= a.timeout <= 1200:
        parser.error('timeout debe estar entre 1 y 1200 segundos')
    out = a.out.resolve()
    if out.exists():
        raise FileExistsError(out)
    if a.operacion == 'referencia':
        argv = ['src/reference_smoke.py', '--out', str(out)]
    elif a.operacion.startswith('demo'):
        argv = ['src/run_demo.py', '--profile', 'repertorio' if a.operacion == 'demo-repertorio' else 'u0', '--out', str(out)]
    elif a.operacion == 'recalcular':
        argv = ['src/recalculate_public.py', '--out', str(out)]
    else:
        if not a.config or not a.case_id:
            parser.error('vida/control requieren --config y --case-id; la preparación y el currículo quedan identificados')
        schema = json.loads(a.config.read_text(encoding='utf-8'))['schema']
        worker = 'src/run_integrated_revision.py' if schema == 'CPC7.integrated_revision.config.v1' else 'src/public_case.py'
        argv = [worker, '--config', str(a.config.resolve()), '--case-id', a.case_id, '--out', str(out)]
    argv[0] = str(ROOT / argv[0])
    command = [sys.executable, '-I', '-B', '-X', 'utf8'] + argv
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=ROOT, creationflags=subprocess.CREATE_NO_WINDOW)
    job = OwnedJob(process)
    try:
        try:
            process.wait(timeout=a.timeout)
        except subprocess.TimeoutExpired:
            job.terminate()
            process.wait(timeout=15)
            raise TimeoutError('Proceso propio terminado al vencer su presupuesto')
    finally:
        job.close()
    result = {'schema': 'CPC7.public-command.v1', 'argv': command, 'exit_code': process.returncode,
              'elapsed_seconds': time.monotonic() - started, 'timeout_seconds': a.timeout,
              'owned_process_tree_closed': True, 'operation': a.operacion,
              'scope': 'Reproducción técnica posterior, no una nueva réplica independiente por repetir la misma configuración.'}
    put(out / 'PUBLIC_COMMAND.json', result)
    if process.returncode:
        raise SystemExit(process.returncode)


if __name__ == '__main__':
    main()
