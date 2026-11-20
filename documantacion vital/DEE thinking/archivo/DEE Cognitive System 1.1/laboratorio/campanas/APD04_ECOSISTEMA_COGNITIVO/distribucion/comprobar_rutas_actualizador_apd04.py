"""Zero-native-tick checks of collaboration updater path relocation only."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--actualizador', type=Path, required=True)
    parser.add_argument('--origen', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    source = args.origen.resolve(strict=True)
    updater = args.actualizador.resolve(strict=True)
    if args.salida.exists():
        raise FileExistsError('Preserve the previous logistics receipt.')
    spec = importlib.util.spec_from_file_location('closed_collaboration_updater_apd04', updater)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    found = module.canonical_source()
    thinking, docs = module.scientific_roots(source)
    assert found == source
    assert thinking == source.parent / '4.5'
    assert docs == source.parent.parent
    paths = (
        'sistema/app/lives.py', 'sistema/app/native_tools.py',
        'sistema/app/legacy.py', 'sistema/app/access_guard.py',
        'sistema/capacidades/habitat_externo_01.py', 'sistema/gestionar.py',
        'sistema/capacidades/core/reproduccion/worker_core.py',
        'sistema/app/compactar_historia_operativa.py',
        'sistema/capacidades/core/DEPENDENCIAS.json',
    )
    rows = []
    for name in paths:
        path = source / name
        before = path.read_bytes()
        transformed = module.transformed(name, before)
        if name.endswith('.py'):
            ast.parse(transformed.decode('utf8'), filename=name)
        else:
            json.loads(transformed)
        assert path.read_bytes() == before
        rows.append({'file': name, 'source_sha256': hashlib.sha256(before).hexdigest(),
                     'distribution_sha256': hashlib.sha256(transformed).hexdigest(),
                     'source_unchanged': True, 'transformed_bytes_only_in_memory': True})
    receipt = {
        'schema': 'APD04.collaboration.path_relocation.no_native.v1',
        'source': str(source), 'updater': str(updater), 'updater_sha256': sha(updater),
        'resolved_source': str(found), 'thinking': str(thinking), 'science': str(docs),
        'source_protected_life': module.read(source/'sistema/estado/ACTIVO.json')['life_id'],
        'transforms': rows, 'new_native_ticks': 0, 'new_lives': 0,
        'zip_generated': False, 'original_scientific_files_unchanged': True,
        'scope': 'Only structural path discovery and syntax/JSON of existing portable adapters; not scientific validation or a closed release.',
    }
    with args.salida.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    main()
