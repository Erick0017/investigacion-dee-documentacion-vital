"""Bind the two exact delivered ZIPs to their existing proofs, without DEE ticks."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def contains_exact(value, expected):
    if isinstance(value, dict):
        return any(contains_exact(item, expected) for item in value.values())
    if isinstance(value, list):
        return any(contains_exact(item, expected) for item in value)
    return isinstance(value, str) and value.lower() == expected.lower()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'analysis', 'analysis-proof', 'full', 'full-proof',
                 'protected', 'word', 'editorial', 'cut', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    output = args.output.resolve()
    if not output.is_relative_to(root / 'evidencia') or output.exists():
        raise ValueError('A new external proof under the current evidencia is required')
    bundles = []
    for kind, archive, proof in [('analysis', args.analysis, args.analysis_proof),
                                 ('full_collaboration', args.full, args.full_proof)]:
        archive = archive.resolve(strict=True)
        proof = proof.resolve(strict=True)
        digest = sha(archive)
        if not contains_exact(read(proof), digest):
            raise ValueError('Existing exact-archive proof does not bind current ZIP: ' + kind)
        if kind == 'analysis' and archive.stat().st_size > 16000000:
            raise ValueError('Analysis archive exceeds the absolute transfer limit')
        bundles.append({'kind': kind, 'path': str(archive), 'bytes': archive.stat().st_size,
                        'sha256': digest, 'existing_exact_archive_proof': str(proof),
                        'proof_sha256': sha(proof), 'proof_contains_exact_current_ZIP_SHA256': True})
    editorial = read(args.editorial)
    if sha(args.word) != editorial['sha256'] or args.word.stat().st_size != editorial['bytes']:
        raise ValueError('Current Word differs from the checked editorial bytes')
    protected = read(args.protected)
    if not protected['all_unchanged']:
        raise ValueError('A protected original differs from startup')
    cut = read(args.cut)
    main_cut = cut['main']
    source_main = []
    for key in ('record', 'snapshot'):
        member = (root / 'sistema' / main_cut[key]).resolve(strict=True)
        if not member.is_relative_to(root / 'sistema') or sha(member) != main_cut[key + '_sha256']:
            raise ValueError('Source ASISTENTE_MAIN moved after the stopped R04 cut')
        source_main.append({'field': key, 'path': str(member), 'sha256': sha(member), 'unchanged': True})
    lab = Path(__file__).resolve().parent.parent
    budget = read(lab / 'PRESUPUESTO.json')
    elapsed = (time.monotonic() - budget['initial_monotonic_sample']
               + budget['elapsed_before_monotonic_sample_seconds'])
    if elapsed > budget['max_seconds']:
        raise ValueError('Original operational time budget exhausted')
    report = {'schema': 'APD01.external_final_delivery_binding.v1',
              'verified_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Exact delivered bytes, their existing archive proofs, stopped source state and protected originals. Not a global cognitive verdict.',
              'native_ticks': 0, 'Runtime_imported': False, 'bundles': bundles,
              'manual': {'path': str(args.word.resolve()), 'sha256': sha(args.word),
                         'bytes': args.word.stat().st_size, 'editorial_proof': str(args.editorial.resolve()),
                         'editorial_proof_sha256': sha(args.editorial),
                         'visual_validation': editorial['visual_validation']},
              'protected_originals_proof': {'path': str(args.protected.resolve()),
                                            'sha256': sha(args.protected), 'all_unchanged': True},
              'source_MAIN': {'life': main_cut['life_id'], 'tick': main_cut['tick'],
                              'members': source_main, 'cut_proof_sha256': sha(args.cut)},
              'original_budget': {'start_utc': budget['start_utc'], 'deadline_utc': budget['deadline_utc'],
                                  'max_seconds': budget['max_seconds'], 'elapsed_monotonic_seconds': elapsed,
                                  'within_original_budget': True},
              'no_upload_or_external_send_performed': True,
              'verifier_sha256': sha(Path(__file__))}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf8') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print(json.dumps({'output': str(output), 'sha256': sha(output),
                      'bundles': bundles, 'elapsed_seconds': elapsed}))


if __name__ == '__main__':
    main()
