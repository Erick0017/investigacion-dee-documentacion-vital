"""Final read-only verification of the exact protected objects recorded at startup."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    lab = Path(__file__).resolve().parent.parent
    budget_path = lab / 'PRESUPUESTO.json'
    budget = json.loads(budget_path.read_text(encoding='utf-8'))
    root = lab.parents[2].resolve(strict=True)
    output = args.output.resolve()
    if not output.is_relative_to(root / 'evidencia'):
        raise ValueError('Output must be under the existing system evidencia directory')
    if output.exists():
        raise FileExistsError(output)
    checks = []
    for name, reference in budget['parent_and_protected'].items():
        source = Path(reference['path']).resolve(strict=True)
        if not source.is_relative_to(root):
            raise ValueError(f'Unexpected protected path: {name}')
        actual = {'bytes': source.stat().st_size, 'sha256': sha256(source)}
        checks.append({'id': name, 'path': str(source), 'expected': reference,
                       'actual': actual, 'unchanged': all(
                           actual[key] == reference[key] for key in ('bytes', 'sha256'))})
    elapsed = (time.monotonic() - budget['initial_monotonic_sample']
               + budget['elapsed_before_monotonic_sample_seconds'])
    report = {
        'schema': 'APD01.protected_objects.actual_readback.v1',
        'verified_utc': datetime.now(timezone.utc).isoformat(),
        'native_ticks': 0,
        'scope': 'Exact protected bytes only; not a capability or scientific regression test',
        'startup_budget_sha256': sha256(budget_path),
        'original_start_utc': budget['start_utc'],
        'original_deadline_utc': budget['deadline_utc'],
        'elapsed_monotonic_seconds_from_original_start': elapsed,
        'within_original_budget_at_verification': elapsed <= budget['max_seconds'],
        'checks': checks,
        'all_unchanged': all(row['unchanged'] for row in checks),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(output), 'all_unchanged': report['all_unchanged'],
                      'elapsed_seconds': elapsed, 'native_ticks': 0}))
    if not report['all_unchanged']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
