"""Register transport UI metadata for an ALREADY imported complete paired life.

No Runtime construction, native load, physics tick, SQLite write, recipe,
snapshot edit, teaching, new import, or change to VIDA/ACTIVO is performed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--vida', required=True)
    p.add_argument('--snapshot-sha256', required=True)
    p.add_argument('--parent-sha256', required=True)
    p.add_argument('--paired-manifest', type=Path, required=True)
    p.add_argument('--paired-sha256', required=True)
    p.add_argument('--salida', type=Path, required=True)
    p.add_argument('--root-go', choices=('APD04_REGISTER_EXISTING_PAIRED_IMPORT_N0',), required=True)
    args = p.parse_args()
    root = args.root.resolve(strict=True)
    system = root/'sistema'
    ui = load('apd04_existing_ui_registration_only', system/'app/usar_dee.py')
    life = ui.identifier(args.vida)
    source_manifest = args.paired_manifest.resolve(strict=True)
    if not source_manifest.is_relative_to(system/'estado/fuentes_emparejadas'):
        raise ValueError('The declared original complete pair must remain in its selected state directory.')
    if source_manifest.name != 'EXPORTACION_SERVICIO.json' or sha(source_manifest) != args.paired_sha256:
        raise ValueError('Original paired manifest identity differs.')
    pair = read(source_manifest)
    card_path = system/'estado/vidas'/life/'VIDA.json'
    card = read(card_path)
    if card['life_id'] != life or card['world_id'] != life or card['branch'] != 'EXPLICIT_IMPORTED_CONTINUITY':
        raise ValueError('This helper only registers an explicit existing paired import, never recreates a life.')
    if card['snapshot_sha256'] != args.snapshot_sha256 or card['parent']['encoded_sha256'] != args.parent_sha256:
        raise ValueError('Current imported snapshot or its parent differs from the explicit expected identities.')
    if pair['snapshot_sha256'] != args.parent_sha256:
        raise ValueError('Declared parent is not this full source pair.')
    snapshot = (system/card['snapshot']).resolve(strict=True)
    if not snapshot.is_relative_to(system/'estado/checkpoints') or sha(snapshot) != args.snapshot_sha256:
        raise ValueError('Current native complete snapshot differs.')
    if (system/'estado/locks'/(life+'.lock')).exists():
        raise RuntimeError('An owner lock is present. Do not register metadata while a writer may be active.')
    transport = system/'estado/servicios_persistentes'/life
    mapping_path = transport/'IMPORTACION.json'
    mapping = read(mapping_path)
    if (transport/'IMPORTACION_EN_CURSO.json').exists():
        raise ValueError('An incomplete import is preserved, not registered as usable.')
    if mapping['new_life_id'] != life or mapping['source_life_id'] != pair['life_id'] or mapping['imported_snapshot_sha256'] != args.snapshot_sha256:
        raise ValueError('Imported transport provenance differs from the declared native life.')
    if mapping['verification']['manifest_sha256'] != args.paired_sha256:
        raise ValueError('Existing imported journal is not bound to the selected original pair.')
    journal = transport/'cola.sqlite3'
    if (journal.with_name(journal.name+'-wal')).exists() and journal.with_name(journal.name+'-wal').stat().st_size:
        raise ValueError('The standalone imported journal has an uncheckpointed WAL; do not modify or omit it.')
    unchanged_paths = [card_path, snapshot, journal, mapping_path, system/'estado/ACTIVO.json', source_manifest]
    before = {str(path): sha(path) for path in unchanged_paths}
    with sqlite3.connect(journal.as_uri()+'?mode=ro&immutable=1', uri=True) as con:
        if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Existing journal integrity failed.')
        owner = json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        pending = con.execute("SELECT id,status FROM requests WHERE status IN ('queued','processing','uncertain') ORDER BY seq").fetchall()
    if owner.get('running') is not False or owner.get('life_id') != life or owner.get('tick') != card['physical']['tick']:
        raise ValueError('Existing owner metadata does not identify this stopped imported cut.')
    if pending:
        raise ValueError('This initial one-time registration requires no pending/uncertain requests; preserve them otherwise.')
    for key in ('N', 'tick', 'RAW_sha256', 'clocks_sha256'):
        if card['physical'][key] != pair['physical'][key] or card['physical'][key] != mapping['physical'][key]:
            raise ValueError('Imported native physical identity differs: '+key)
    config = read(ui.selected_config_path(root))
    backend = ui.OriginalBackend(root, config)
    session = ui.Supervisor(root, life, backend, config)
    if session.state_path.exists() or args.salida.exists():
        raise FileExistsError('Existing UI protocol/receipt is preserved. Registration is not a replay or overwrite.')
    state = dict(session.state)
    state.update(world_id=life, source_life=pair['life_id'], source_snapshot_sha256=args.parent_sha256,
                 imported_at=card['created_utc'], registration_kind='REGISTER_EXISTING_COMPLETE_PAIRED_IMPORT_N0',
                 registration_utc=datetime.now(timezone.utc).isoformat(),
                 existing_imported_snapshot_sha256=args.snapshot_sha256,
                 paired_export_manifest_sha256=args.paired_sha256,
                 source_pair_path_relative=source_manifest.relative_to(root).as_posix(),
                 no_new_import_no_T0_no_native_load_no_new_ticks=True,
                 attribution='Administrative UI transport registration only; the previous complete paired import remains the sole physical parent.')
    if any(sha(path) != digest for path, digest in before.items()):
        raise ValueError('A protected causal source changed during this zero-tick registration check.')
    ui.write_atomic(session.state_path, state)
    after = {str(path): sha(path) for path in unchanged_paths}
    if before != after:
        raise ValueError('Causal source changed; registration evidence preserved, no Native started.')
    result = {'schema': 'APD04.existing_paired_import.UI_registration.N0.v1', 'life_id': life,
              'protocol': str(session.state_path), 'protocol_sha256': sha(session.state_path),
              'record': card, 'import_mapping': mapping, 'owner_read_only': owner,
              'protected_before': before, 'protected_after': after, 'causal_files_unchanged': before == after,
              'new_ticks': 0, 'new_imports': 0, 'only_operational_write': str(session.state_path),
              'no_engine_imported': not any(name.startswith('dee_thinking') for name in sys.modules)}
    with args.salida.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
