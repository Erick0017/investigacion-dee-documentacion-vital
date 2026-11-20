"""Stdlib transport supplement: preserve declared directories after full import.

Called only by a Root supervisor after its official import process exited0.
No Native import, files/content reconstruction, scientific policy or reset.
The shared published RP importer and its context fingerprints stay literal.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import ctypes, hashlib, json, os, sqlite3

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'

def require(ok, message):
    if not ok: raise ValueError(message)
def read(path): return json.loads(path.read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def regular(path):
    for node in (path, *path.parents):
        require(not node.exists() or not(node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No linked transport directory')
    return path
def relative(value):
    require(isinstance(value, str) and value and '\\' not in value and ':' not in value, 'Unsafe paired directory')
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(part not in ('.', '..') for part in path.parts), 'Escaping paired directory')
    return path
def exited_pid(pid):
    require(os.name == 'nt' and type(pid) is int and pid > 0, 'Actual importer PID required')
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]; k.OpenProcess.restype = ctypes.c_void_p
    handle = k.OpenProcess(0x1000, False, pid)
    if not handle:
        error = ctypes.get_last_error(); require(error == 87, 'Cannot prove importer exited')
        return {'pid': pid, 'absent': True, 'winerror': error}
    try:
        code = ctypes.c_uint32(); require(k.GetExitCodeProcess(ctypes.c_void_p(handle), ctypes.byref(code)), 'Cannot read importer process status')
        require(code.value != 259, 'Importer PID still active/reused: no filesystem correction')
        require(code.value == 0, 'Importer process did not exit0')
        return {'pid': pid, 'exit_code': code.value}
    finally: k.CloseHandle(ctypes.c_void_p(handle))

def materialize(system, life, context, imported, importer_pid, *, apply=False):
    """No owner may start until this returns a fully verified transport proof."""
    system = regular(Path(system).resolve(strict=True)); context = Path(context).resolve(strict=True)
    require(system.name == 'sistema' and system.parent.parent == (P / 'estados').resolve(), 'Only isolated PI08 imported systems')
    require(not (system / 'estado/ACTIVO.json').exists(), 'Never supplement a selected principal')
    require(life.startswith('ECI02_PI03_REPRO_') and 'PI08_' in life, 'Explicit PI08 diagnostic identity required')
    require(imported['life'] == life and imported['new_native_ticks'] == 0 and imported['principal_selected'] is False
            and imported['comparison']['physical_equal'] is True and imported['comparison']['causal_prefix_equal'] is True,
            'Actual coherent complete official0tick import proof required')
    process = exited_pid(importer_pid)
    info = read(context); pair = regular(Path(info['prefix']).resolve(strict=True)); manifest_file = pair / 'EXPORTACION_SERVICIO.json'
    manifest = read(manifest_file)
    require(sha(manifest_file) == info['prefix_manifest_sha256'] == imported['result']['verification']['manifest_sha256'], 'Actual source/export proof identity differs')
    require(manifest['schema'] == 'DEE.persistent_service.paired_export.v1', 'Complete paired export required')
    declared = manifest.get('empty_directories_preserved')
    require(isinstance(declared, list) and len(declared) == len(set(declared)), 'Exact exported directory list required')
    cardfile = regular(system / 'estado/vidas' / life / 'VIDA.json'); card = read(cardfile)
    require(card['snapshot_sha256'] == imported['result']['snapshot_sha256'] and card['physical'] == imported['result']['physical'], 'Imported future already changed')
    require(not (cardfile.parent / 'FUTURO_INTERRUMPIDO.json').exists(), 'Interrupted future must remain preserved')
    locks = system / 'estado/locks'; require(not locks.exists() or not any(locks.iterdir()), 'Affected owner lock remains')
    service = system / 'estado/servicios_persistentes' / life; worker = system / 'estado/servicios_locales' / life; db = service / 'cola.sqlite3'
    require(not any(Path(str(db) + suffix).exists() and Path(str(db) + suffix).stat().st_size for suffix in ('-wal', '-journal')), 'Nonempty imported SQLite journal')
    con = sqlite3.connect(db.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        require(con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok', 'Imported SQLite integrity failure')
        owner = json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        require(owner.get('running') is False and owner.get('imported_not_yet_started') is True and not owner.get('pid'), 'Only the fresh import before first owner may be supplemented')
        require(not con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0], 'Unresolved imported transport')
    finally: con.close()
    planned = []
    for name in declared:
        rel = relative(name)
        if rel.parts[0] == 'artefactos_trabajador': destination = worker.joinpath(*rel.parts[1:])
        elif rel.parts[0] == 'resultados': destination = service / Path(*rel.parts)
        else: raise ValueError('Only explicit worker/result directory mappings')
        regular(destination)
        if destination.exists():
            require(destination.is_dir(), 'Directory path occupied by a file'); continue
        source = regular(pair.joinpath(*rel.parts))
        require(source.is_dir() and not any(node.is_file() for node in source.rglob('*')), 'A missing directory with source contents is an incomplete import, never reconstructed')
        for child in source.rglob('*'):
            regular(child)
            require(child.is_dir() and child.relative_to(pair).as_posix() in declared, 'Unindexed/nonregular empty subtree')
        planned.append({'source': str(source), 'target': str(destination), 'manifest_directory': name})
    a = 'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'; acardfile = C / 'sistema/estado/vidas' / a / 'VIDA.json'; acard = read(acardfile)
    critical = [cardfile, system / card['snapshot'], db, C / 'sistema/estado/ACTIVO.json', acardfile, C / 'sistema' / acard['snapshot']]
    before = {str(path): sha(regular(path)) for path in critical}
    if apply:
        for row in sorted(planned, key=lambda row: (len(Path(row['target']).parts), row['target'])):
            target = Path(row['target'])
            # Its parents must already be copied or themselves declared/planned.
            require(target.parent.is_dir(), 'Unindexed missing ancestor')
            target.mkdir(exist_ok=False)
        require(all((worker.joinpath(*relative(name).parts[1:]) if relative(name).parts[0] == 'artefactos_trabajador' else service.joinpath(*relative(name).parts)).is_dir() for name in declared), 'A declared source directory remains absent')
        require(before == {str(path): sha(path) for path in critical}, 'Critical Native/SQLite/A bytes changed')
    return {'schema': 'DEE.PI08.import.full_pair_empty_directory_supplement.R01',
            'recorded_utc': datetime.now(timezone.utc).isoformat(), 'applied': apply, 'life_id': life,
            'source_manifest_sha256': sha(manifest_file), 'declared_directories': len(declared),
            'created_directories': planned if apply else [], 'would_create': planned if not apply else [],
            'importer_closed_process': process, 'new_Native_ticks': 0, 'new_Native_inputs': 0,
            'files_written': 0, 'critical_hashes_before': before,
            'Native_card_snapshot_SQLite_and_A_all_unchanged': before == {str(path): sha(path) for path in critical},
            'scope': 'Exact source-export empty-directory preservation after the official complete import. No data/content repair and no old checksum relaxation.'}
