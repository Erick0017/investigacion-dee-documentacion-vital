"""Seal an explicitly identified current complete APD04 cut using the existing N0 sealer.

No owner is started, no tick is advanced, no queue is cleared/checkpointed and no
historical snapshot is substituted for a newer published life. Pending queued
transport may be retained only when explicitly requested; processing/uncertain
futures are rejected by the established sealer.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--life', required=True)
    parser.add_argument('--tick', type=int, required=True)
    parser.add_argument('--snapshot-sha256', required=True)
    parser.add_argument('--target-name', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--scope', required=True)
    parser.add_argument('--allow-queued', action='store_true')
    parser.add_argument('--root-go', choices=('APD04_EXACT_CURRENT_POSTSTOP_PAIR_N0',), required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    system = root/'sistema'
    for name in (args.life, args.target_name):
        if not name or any(ch not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-' for ch in name):
            raise ValueError('An explicit simple local identity is required')
    record_path = system/'estado/vidas'/args.life/'VIDA.json'
    record = read(record_path)
    if (record['life_id'] != args.life or record['physical']['tick'] != args.tick
            or record['snapshot_sha256'] != args.snapshot_sha256):
        raise ValueError('Actual current published life differs; no old favorable cut is substituted')
    target = system/'estado/fuentes_emparejadas'/args.target_name
    out = args.out.resolve()
    if target.exists() or out.exists():
        raise FileExistsError('A sealed pair/attempt already exists; no replacement')
    protected_paths = [system/'estado/ACTIVO.json', record_path, system/record['snapshot']]
    protected_before = {str(path): sha(path) for path in protected_paths}
    ui = load('apd04_existing_UI_for_exact_poststop_pair', system/'app/usar_dee.py')
    sealer = load('apd04_existing_APD03_poststop_sealer',
        root/'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py')
    pair = sealer.stopped_pair(root, ui, args.life, target,
        allow_queued=args.allow_queued, scope=args.scope)
    protected_after = {str(path): sha(path) for path in protected_paths}
    if protected_before != protected_after:
        raise ValueError('A protected current source changed during N0 sealing')
    out.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, out/Path(__file__).name)
    result = {'schema': 'APD04.explicit_current_postSTOP_pair.N0.v1',
        'pair': pair, 'source_sha256': sha(__file__),
        'protected_before': protected_before, 'protected_after': protected_after,
        'new_owner_started': False, 'new_native_ticks': 0}
    with (out/'CORTE_COMPLETO_POSTSTOP.json').open('x', encoding='utf8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'life': args.life, 'tick': args.tick,
        'snapshot_sha256': args.snapshot_sha256, 'manifest_sha256': pair['manifest_sha256'],
        'directory': pair['directory'], 'new_native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
