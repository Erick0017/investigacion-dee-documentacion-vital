"""Development launcher fixture, explicitly not a complete release ZIP proof."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from package45 import WHEEL, wheel_identity, sha, put


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--wheel', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--fixture', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if sha(a.wheel) != a.expected_sha256:
        raise ValueError('Wrong final development wheel')
    fixture = a.fixture.resolve()
    if fixture.exists():
        raise FileExistsError(fixture)
    (fixture / 'wheel').mkdir(parents=True)
    target = fixture / 'wheel' / WHEEL
    shutil.copyfile(a.wheel, target)
    shutil.copyfile(ROOT / 'iniciar_4_5.ps1', fixture / 'iniciar_4_5.ps1')
    identity = wheel_identity(target.read_bytes())
    put(fixture / 'RELEASE_IDENTITY.json', identity)
    put(fixture / 'MANIFEST.json', {'schema': 'DEE45.manifest.v1', 'archive_root': 'DEE_thinking_4_5_0',
        'scope': 'Development launcher-only fixture; NOT a release archive manifest or proof.',
        'files': [{'path': 'wheel/' + WHEEL, 'bytes': target.stat().st_size, 'sha256': sha(target)}]})
    result = subprocess.run([sys.executable, '-I', '-B', str(ROOT / 'tools/check_launcher45.py'),
                             '--root', str(fixture), '--output', str(a.output.resolve())], timeout=360)
    if result.returncode:
        raise SystemExit(result.returncode)
    put(a.output / 'DEVELOPMENT_SCOPE.json', {'scope': 'Launcher-only development fixture; exact release ZIP extraction/install proof remains pending.',
        'fixture': str(fixture), 'wheel_sha256': identity['wheel_sha256'], 'launcher_sha256': sha(fixture / 'iniciar_4_5.ps1')})


if __name__ == '__main__':
    main()
