"""One nonblocking external Python-stack sample; never pause or tick DEE."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_SENSOR02_C_R03'


def main():
    if (OUT / 'HOST_PYSPY_MUESTRA.json').exists():
        raise FileExistsError('The single declared external host sample exists')
    start = json.loads((OUT / 'C/START.json').read_text(encoding='utf8'))
    executable = Path(r'D:\Descargas\ANACONDA MINICONDA\Scripts\py-spy.exe')
    argv = [str(executable), 'dump', '--pid', str(start['observation']['pid']), '--nonblocking', '--locals']
    began = datetime.now(timezone.utc).isoformat()
    captured = subprocess.run(argv, capture_output=True, timeout=20)
    for name, encoded in (('HOST_PYSPY_STDOUT.txt', captured.stdout), ('HOST_PYSPY_STDERR.txt', captured.stderr)):
        with (OUT / name).open('xb') as stream:
            stream.write(encoded)
    value = {'argv': argv, 'started_utc': began, 'finished_utc': datetime.now(timezone.utc).isoformat(),
        'exit_code': captured.returncode,
        'executable_sha256': hashlib.sha256(executable.read_bytes()).hexdigest(),
        'stdout_sha256': hashlib.sha256(captured.stdout).hexdigest(), 'stdout_bytes': len(captured.stdout),
        'stderr_sha256': hashlib.sha256(captured.stderr).hexdigest(), 'stderr_bytes': len(captured.stderr),
        'process_suspend_requested': False, 'new_DEE_ticks_by_observer': 0,
        'scope': 'Host call-stack snapshot only. Tick arguments are call targets, not the current uncommitted native tick.'}
    with (OUT / 'HOST_PYSPY_MUESTRA.json').open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(value, indent=2))


if __name__ == '__main__':
    main()
