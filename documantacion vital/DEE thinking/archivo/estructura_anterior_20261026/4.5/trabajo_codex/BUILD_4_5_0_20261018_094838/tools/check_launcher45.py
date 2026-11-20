"""Exercise the real Spanish PowerShell launcher and a finite restored session.

No prepared snapshot or expected response is supplied to the launcher. The
auditor checks its transcript only after the native trajectory has completed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    root = a.root.resolve(); output = a.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True, exist_ok=False)
    report = {'schema': 'DEE45.real-launcher-check.v1', 'status': 'FAILED'}
    started = time.monotonic()
    try:
        snapshot = output / 'vida_continuada.deetsnap.gz'
        transcript = output / 'TRANSCRIPCION.json'
        events = output / 'sesion.eventos'
        lines = ['nuevo repertorio 2', 'bloque L01:-1,L02:+1 0', 'consulta L01,L02 67',
                 'guardar "' + snapshot.as_posix() + '"', 'reiniciar confirmar',
                 'cargar "' + snapshot.as_posix() + '"', 'consulta L01,L02 134', 'salir']
        events.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        powershell = Path(os.environ.get('SystemRoot', 'C:/Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
        argv = [str(powershell), '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(root / 'iniciar_4_5.ps1'),
                '-PythonExecutable', sys.executable, '-Events', str(events), '-Transcript', str(transcript)]
        try:
            process = subprocess.run(argv, cwd=output, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired as exc:
            (output / 'LAUNCHER.stdout.log').write_bytes(exc.stdout or b'')
            (output / 'LAUNCHER.stderr.log').write_bytes(exc.stderr or b'')
            put(output / 'COMMAND.json', {'argv': argv, 'status': 'TIMEOUT', 'timeout_seconds': 300})
            raise
        (output / 'LAUNCHER.stdout.log').write_bytes(process.stdout)
        (output / 'LAUNCHER.stderr.log').write_bytes(process.stderr)
        put(output / 'COMMAND.json', {'argv': argv, 'exit_code': process.returncode, 'waited': True,
                                      'elapsed_seconds': time.monotonic() - started, 'timeout_seconds': 300})
        if process.returncode:
            raise RuntimeError('Real PowerShell launcher failed; retain stdout/stderr')
        primary = json.loads(transcript.read_text(encoding='utf-8'))
        rows = primary['eventos']
        if len(rows) != 7 or any('error' in row for row in rows):
            raise AssertionError(('Unexpected or rejected command', rows))
        panels = [row['resultado']['lectura'] for row in rows if row['orden'].startswith('consulta ')]
        values = [[r['value'] for r in panel['responses']] for panel in panels]
        if values != [[-1, 1], [-1, 1]] or not all(r['covered'] and r['receipt']['status'] == 'applied' for panel in panels for r in panel['responses']):
            raise AssertionError(('Native postlaunch/restore query differs', values))
        if not snapshot.is_file() or rows[5]['resultado']['operacion'] != 'RESTAURACION_NO_PREPARACION':
            raise AssertionError('No explicit restoration')
        marker = root / '.mente45_env/DEE_THINKING_45_ENV.json'
        identity = json.loads((root / 'RELEASE_IDENTITY.json').read_text(encoding='utf-8'))
        if json.loads(marker.read_text(encoding='utf-8'))['wheel_sha256'] != identity['wheel_sha256']:
            raise AssertionError('Launcher environment marker differs from exact wheel')
        report.update({'status': 'VERIFIED', 'real_powershell_launcher': True, 'offline_owned_environment': True,
                       'native_queries': values, 'restored_without_repreparation': True, 'comparison_after_trajectory_only': True,
                       'events_sha256': sha(events), 'transcript_sha256': sha(transcript), 'snapshot_sha256': sha(snapshot),
                       'wheel_sha256': identity['wheel_sha256'], 'native_sha256': identity['native_sha256'],
                       'elapsed_seconds': time.monotonic() - started})
    except BaseException as exc:
        report['error'] = repr(exc)
        put(output / 'LAUNCHER_REPORT.json', report)
        raise
    put(output / 'LAUNCHER_REPORT.json', report)
    print(json.dumps({'status': report['status'], 'elapsed_seconds': report['elapsed_seconds']}))


if __name__ == '__main__':
    main()
