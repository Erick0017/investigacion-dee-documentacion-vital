"""Root-only exact four-empty-directory transport correction. Default read-only.

No DEE import, Native owner/input/tick, reset, queue repair or source mutation.
All60 old30 files must match the preserved full pair and immutable PREPARADO.
Only missing empty directories named by the original export may be created.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ctypes, hashlib, json, os, sqlite3

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
SYSTEM = P / 'estados/B_REAL_R01/sistema'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01'
A = 'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
CONCILIATION = P / 'control/CONCILIACION_ARRANQUE_B_REAL_PI08_R01.json'
MISSING = ['inflight_minus', 'inflight_plus', 'inflight_silence', 'reservoir']

def require(ok, message):
    if not ok: raise ValueError(message)
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
    for node in (p, *p.parents):
        require(not node.exists() or not(node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No linked/reparse path')
    return p
def tree(root):
    regular(root); files, directories = [], []
    for path in sorted(root.rglob('*')):
        regular(path)
        if path.is_dir(): directories.append(path.relative_to(root).as_posix())
        elif path.is_file(): files.append({'file': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)})
        else: raise ValueError('Only ordinary source/target members')
    return {'files': files, 'directories': directories}
def absent(pid):
    require(os.name == 'nt', 'Fresh exact Windows process proof required')
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]; k.OpenProcess.restype = ctypes.c_void_p
    h = k.OpenProcess(0x1000, False, pid)
    if not h:
        error = ctypes.get_last_error(); require(error == 87, 'Cannot prove exact former owner absent')
        return {'pid': pid, 'present': False, 'winerror': error}
    try:
        code = ctypes.c_uint32(); require(k.GetExitCodeProcess(ctypes.c_void_p(h), ctypes.byref(code)), 'Cannot read process exit status')
        require(code.value != 259, 'Actual former PID still live/reused; do not alter/stop it')
        return {'pid': pid, 'exited': True, 'exit_code': code.value}
    finally: k.CloseHandle(ctypes.c_void_p(h))

def main(args):
    output = P / 'control/RESTAURACION_VACIOS_B_REAL_PI08_R01.json'
    require(not output.exists(), 'Existing correction proof protected; do not repeat')
    seal = read(P / 'codigo/SELLO_PI08_B_R01.json'); pair = regular(Path(seal['source_prefix']['path']))
    manifest = read(pair / 'EXPORTACION_SERVICIO.json')
    require(sha(pair / 'EXPORTACION_SERVICIO.json') == seal['source_prefix']['manifest_sha256'], 'Stable paired-source identity differs')
    source = regular(pair / 'artefactos_trabajador/PI04_C2C_COORDINACION_R01/dispositivo')
    worker = regular(SYSTEM / 'estado/servicios_locales' / LIFE)
    target = worker / 'PI04_C2C_COORDINACION_R01/dispositivo'
    original = read(source.parent.parent / 'PI08_C2C_INTEGRACION_R01/PREPARADO.json')['source_device_tree']
    source_tree, before_tree = tree(source), tree(target)
    require(source_tree == original and len(source_tree['files']) == 60, 'Preserved original30 tree/PREPARADO differs')
    require(before_tree['files'] == source_tree['files'], 'File bytes differ: directory-only correction forbidden')
    missing = sorted(set(source_tree['directories']) - set(before_tree['directories']))
    require(missing == MISSING and not(set(before_tree['directories']) - set(source_tree['directories'])), 'Only the exact diagnosed four missing directories may be repaired')
    for name in missing:
        declared = 'artefactos_trabajador/PI04_C2C_COORDINACION_R01/dispositivo/' + name
        require(declared in manifest['empty_directories_preserved'] and not any((source / name).iterdir()), 'Directory is not declared/empty in the paired source')
        require(not regular(target / name).exists(), 'Existing directory must never be overwritten')
    conciliation = read(CONCILIATION)
    require(conciliation['life_id'] == LIFE and conciliation['Native_inputs_or_ticks'] == 0 and conciliation['no_B_KEY_or_requests'] is True,
            'Exact reconciled pre-material startup required')
    processes = [absent(int(row['pid'])) for row in conciliation['actual_process_checks']]
    cardfile = SYSTEM / 'estado/vidas' / LIFE / 'VIDA.json'; card = read(cardfile)
    require(card['physical']['tick'] == 861426 and card['snapshot_sha256'] == conciliation['closed_world']['snapshot']['sha256'], 'Failed startup current cut changed')
    service = SYSTEM / 'estado/servicios_persistentes' / LIFE; db = service / 'cola.sqlite3'
    for path in (SYSTEM / 'estado/locks',): require(not path.exists() or not any(path.iterdir()), 'Affected lock remains')
    require(not (P / 'PI08_ROOT_NATIVE_WRITER.lock').exists() and not(cardfile.parent / 'FUTURO_INTERRUMPIDO.json').exists(), 'Unresolved material marker remains')
    require(not any(Path(str(db) + tail).exists() and Path(str(db) + tail).stat().st_size for tail in ('-wal', '-journal')), 'Nonempty SQLite journal')
    con = sqlite3.connect(db.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        require(con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok', 'SQLite integrity failure')
        owner = json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        require(owner.get('running') is False and owner.get('tick') == 861426, 'Imported closed-owner status differs')
        require(not con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0], 'Unresolved transport request')
        require(not con.execute("SELECT COUNT(*) FROM requests WHERE id LIKE 'PI08_B_REAL_R01%'").fetchone()[0], 'B material request already exists')
    finally: con.close()
    acardfile = C / 'sistema/estado/vidas' / A / 'VIDA.json'; acard = read(acardfile)
    protected = [cardfile, SYSTEM / card['snapshot'], db, C / 'sistema/estado/ACTIVO.json', acardfile, C / 'sistema' / acard['snapshot']]
    before = {str(path): sha(regular(path)) for path in protected}
    result = {'schema': 'DEE.PI08.B.four_empty_directory_transport_correction.R01',
              'recorded_utc': datetime.now(timezone.utc).isoformat(), 'applied': args.aplicar,
              'life_id': LIFE, 'tick': 861426, 'missing_directories': missing,
              'source_manifest_sha256': sha(pair / 'EXPORTACION_SERVICIO.json'),
              'conciliation': {'path': str(CONCILIATION), 'sha256': sha(CONCILIATION)},
              'fresh_former_process_checks': processes, 'old30_files_verified': 60,
              'Native_executed': False, 'new_Native_inputs': 0, 'new_ticks': 0,
              'source_or_scientific_code_modified': False, 'critical_hashes_before': before}
    if args.aplicar:
        # Every guard and byte comparison precedes the only four mutations.
        for name in missing: (target / name).mkdir(exist_ok=False)
        after_tree = tree(target)
        require(after_tree == source_tree, 'Post-correction literal old30 tree differs; preserve and stop')
        require(before == {str(path): sha(path) for path in protected}, 'Critical Native/SQLite/A bytes changed concurrently')
        result.update(created=[str(target / name) for name in missing], literal_tree_equals_PREPARADO=True,
                      Native_card_snapshot_SQLite_and_A_all_unchanged=True)
        with output.open('x', encoding='utf8') as stream: json.dump(result, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'mode': 'APPLIED_ROOT_ONLY' if args.aplicar else 'READ_ONLY_READY', 'proof': str(output) if args.aplicar else None,
                      'sha256': sha(output) if args.aplicar else None, 'missing': missing, 'files_verified': 60, 'Native_executed': False}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--aplicar', action='store_true')
    main(parser.parse_args())
