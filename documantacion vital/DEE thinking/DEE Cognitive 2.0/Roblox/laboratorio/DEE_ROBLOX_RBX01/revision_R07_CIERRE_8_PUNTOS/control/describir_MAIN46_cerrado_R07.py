"""Describe the closed SAME current MAIN root; never imports Native or opens SQLite.

One content-hash sweep, then a path-set/stat sweep without a second full hash.
This is SAME_ROOT_CURRENT_COMPLETE_DESCRIPTOR_NOT_FROZEN_ROLLBACK. Metadata
stability cannot prove an immutable physical freeze or detect a writer that
restores every observed stat. No restoration or continuation is implemented.
Only explicit --write-root-only creates the fresh, exact evidence directory.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import stat

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'native/MAIN'
DESTINATION = ROOT / 'evidencia/PUNTO46_R07'
CUT = ROOT / 'evidencia/MAIN_REAPERTURA_35_46_R07'
WORLD_SHA = '1fa9d6e9207e0743b4459c1382142c1d5bc2dad5868183fde1363ff20f0ed6c8'
CLOSURE_SHA = 'becd84d077c4fb01023593dbea9220fa0e5f2ebfcde8942aab63dd6b66f21a45'
LEDGER_SHA = '98b848d3792bac28140ade66bb86221612474e4a36d5ad8f89888f7f4a845194'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN'
MODE = 'SAME_ROOT_CURRENT_COMPLETE_DESCRIPTOR_NOT_FROZEN_ROLLBACK'
MAX_COPY_BYTES = 250000000
MAX_FILES = 30000
MAX_SOURCE_BYTES = 1500000000


def need(value, message):
    if not value:
        raise ValueError(message)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def signature(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
            s.st_mtime_ns, s.st_ctime_ns, getattr(s, 'st_file_attributes', 0))


def cross_api_identity(s):
    # Windows lstat/fstat expose different ctime meanings on some Python builds.
    # Keep complete ctime checks within each API, rather than across the APIs.
    value = signature(s)
    return value[:6] + value[7:]


def unlinked(s):
    need(not stat.S_ISLNK(s.st_mode) and not getattr(s, 'st_file_attributes', 0) & 1024,
         'SYMLINK_OR_REPARSE_POINT_REJECTED')


def safe(path, exists=True):
    p = Path(os.path.abspath(path))
    for q in reversed((p, *p.parents)):
        if os.path.lexists(q):
            unlinked(q.lstat())
    if exists:
        need(p.exists(), 'REQUIRED_PATH_MISSING:' + str(p))
    return p


def new_json(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def read_json(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def hash_stable(path, expected_stat=None, copy_to=None, copy_limit=None):
    """Read one file once. Optional critical copy shares this same byte stream."""
    p = safe(path)
    before = p.lstat()
    unlinked(before)
    need(stat.S_ISREG(before.st_mode), 'REGULAR_FILE_REQUIRED')
    if expected_stat is not None:
        need(signature(before) == expected_stat, 'FILE_CHANGED_BEFORE_OPEN')
    if copy_to is not None:
        copy_limit = before.st_size if copy_limit is None else copy_limit
        need(0 <= before.st_size <= copy_limit, 'COPY_FILE_EXCEEDS_APPROVED_SIZE')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(p, flags)
    out = None
    try:
        with os.fdopen(fd, 'rb') as source:
            opened = os.fstat(source.fileno())
            need(cross_api_identity(opened) == cross_api_identity(before), 'OPENED_FILE_IDENTITY_CHANGED')
            if copy_to is not None:
                out = Path(copy_to).open('xb')
            h = hashlib.sha256()
            count = 0
            while True:
                block = source.read(1048576)
                if not block:
                    break
                h.update(block)
                count += len(block)
                if out is not None:
                    need(count <= copy_limit, 'COPY_GREW_BEYOND_APPROVED_SIZE')
                    out.write(block)
            need(count == before.st_size and signature(os.fstat(source.fileno())) == signature(opened),
                 'FILE_CHANGED_DURING_READ')
            if out is not None:
                out.flush()
                os.fsync(out.fileno())
    finally:
        if out is not None:
            out.close()
    after = p.lstat()
    unlinked(after)
    need(signature(after) == signature(before), 'FILE_CHANGED_AFTER_READ')
    return {'bytes': count, 'sha256': h.hexdigest(), 'stat': signature(before)}


def inventory(root, hash_contents, copy_targets=None, copy_limits=None):
    """No exclusions: include hidden files, interfaces, outbox, artifacts and DB bytes."""
    root = safe(root)
    need(stat.S_ISDIR(root.lstat().st_mode), 'ROOT_DIRECTORY_REQUIRED')
    directories = {}
    files = {}
    stack = [root]
    total = 0
    while stack:
        directory = stack.pop()
        ds = directory.lstat()
        unlinked(ds)
        need(stat.S_ISDIR(ds.st_mode), 'DIRECTORY_TYPE_CHANGED')
        relative = directory.relative_to(root).as_posix()
        directories[relative] = signature(ds)
        with os.scandir(directory) as entries:
            for entry in entries:
                p = Path(entry.path)
                # Windows DirEntry.stat may omit inode/device/link fields. Use
                # lstat consistently in both sweeps and the open-file check.
                s = p.lstat()
                unlinked(s)
                name = p.relative_to(root).as_posix()
                if stat.S_ISDIR(s.st_mode):
                    stack.append(p)
                else:
                    need(stat.S_ISREG(s.st_mode), 'SPECIAL_FILE_REJECTED:' + name)
                    need(name not in files, 'DUPLICATE_RELATIVE_PATH')
                    total += s.st_size
                    need(len(files) < MAX_FILES and total <= MAX_SOURCE_BYTES, 'FINITE_INVENTORY_LIMIT')
                    row = hash_stable(p, signature(s), (copy_targets or {}).get(name),
                                      (copy_limits or {}).get(name)) if hash_contents else {
                        'bytes': s.st_size, 'stat': signature(s)}
                    files[name] = row
        need(signature(directory.lstat()) == signature(ds), 'DIRECTORY_CHANGED_DURING_ENUMERATION')
    return {'files': files, 'directories': directories, 'bytes': total}


def require_closed(native, closure):
    need(closure['life'] == LIFE, 'EXACT_MAIN_LIFE')
    need(closure['physical_fingerprint_recorded_by_official_owner']['tick'] == 1019339,
         'EXACT_MAIN46_T1019339')
    owner = closure['owner_closed']
    need(owner['kind'] == 'OWNER_CLOSED' and owner['pid'] == 3352 and owner['exit_code'] == 0,
         'OFFICIAL_OWNER3352_CLOSED_EXIT0')
    need(closure['transport']['no_pending_or_uncertain'] is True, 'RECORDED_QUEUE_DRAINED')
    need(closure['transport']['owner']['running'] is False, 'RECORDED_OWNER_NOT_RUNNING')
    absent = [native / 'sistema/estado/ACTIVO.json',
              native / 'sistema/estado/locks' / (LIFE + '.lock'),
              native / 'sistema/estado/vidas' / LIFE / 'FUTURO_INTERRUMPIDO.json',
              native / 'LEASE_MIGRATION_IN_PROGRESS.json']
    for p in absent:
        safe(p, exists=False)
        need(not os.path.lexists(p), 'ACTUAL_NATIVE_OWNER_OR_MIGRATION_LOCK_PRESENT:' + str(p))
    db = safe(closure['transport']['database']['path'])
    need(db.is_relative_to(native), 'QUEUE_INSIDE_EXACT_MAIN_ROOT')
    for suffix in ('-wal', '-journal'):
        p = safe(Path(str(db) + suffix), exists=False)
        need(not p.exists() or p.stat().st_size == 0, 'LIVE_SQLITE_SIDECAR_REJECTED')
    return [str(p) for p in absent]


def run(a):
    created = False
    destination = Path(os.path.abspath(a.destination))
    try:
        need(a.write_root_only is True, 'EXPLICIT_WRITE_ROOT_ONLY_REQUIRED')
        need(Path(os.path.abspath(a.native_root)) == MAIN and destination == DESTINATION,
             'EXACT_MAIN_AND_PUNTO46_ROOTS_ONLY')
        native = safe(MAIN)
        safe(DESTINATION.parent)
        safe(destination, exists=False)
        need(not os.path.lexists(destination), 'FRESH_OUTPUT_ONLY_NO_RETRY')
        world = safe(CUT / 'WORLD_CHECKPOINT.json')
        close_path = safe(CUT / 'CONCILIACION_CIERRE_R07.json')
        ledger = safe(CUT / 'LEDGER_AL_CIERRE.json')
        anchors = [('WORLD_CHECKPOINT.json', world, WORLD_SHA),
                   ('CONCILIACION_CIERRE_R07.json', close_path, CLOSURE_SHA),
                   ('LEDGER_AL_CIERRE.json', ledger, LEDGER_SHA)]
        checked = {}
        for name, p, expected in anchors:
            row = hash_stable(p)
            need(row['sha256'] == expected, 'EXACT_CLOSED_ANCHOR_SHA:' + name)
            checked[name] = row
        closure = read_json(close_path)
        need(closure['world']['sha256'] == WORLD_SHA and closure['literal_closed_ledger']['sha256'] == LEDGER_SHA,
             'ANCHORS_BIND_SAME_CLOSED_CUT')
        need(closure['global_consumed'] == 51612 and closure['global_intents'] == {}, 'LITERAL_CLOSED_LEDGER_CUT')
        ledger_value = read_json(ledger)
        need(ledger_value['consumed'] == 51612 and ledger_value['intents'] == {}, 'LITERAL_LEDGER_VALUES')
        absent = require_closed(native, closure)
        critical = [closure['native_card'], closure['snapshot'], closure['transport']['database']]
        critical_by_name = {}
        for row in critical:
            p = safe(row['path'])
            need(p.is_relative_to(native), 'CRITICAL_FILE_OUTSIDE_MAIN')
            name = p.relative_to(native).as_posix()
            need(name not in critical_by_name, 'DUPLICATE_CRITICAL_PATH')
            critical_by_name[name] = row
        copy_bytes = sum(r['bytes'] for r in critical) + sum(r['bytes'] for r in checked.values())
        need(copy_bytes <= MAX_COPY_BYTES, 'ALL_CRITICAL_COPIES_MUST_FIT_250_MB')
        destination.mkdir()
        created = True
        new_json(destination / 'IN_PROGRESS.json', {'pid': os.getpid(), 'utc': utc(), 'mode': MODE})
        objects = destination / 'critical'
        objects.mkdir()
        targets = {name: objects / ('CRITICAL_' + str(i) + '.blob')
                   for i, name in enumerate(critical_by_name)}
        before = inventory(native, True, targets, {name: row['bytes'] for name, row in critical_by_name.items()})
        for name, expected in critical_by_name.items():
            actual = before['files'].get(name)
            need(actual is not None and actual['sha256'] == expected['sha256'] and actual['bytes'] == expected['bytes'],
                 'CURRENT_CRITICAL_DIFFERS_CLOSED_CUT:' + name)
            copy_row = hash_stable(targets[name])
            need(copy_row['sha256'] == actual['sha256'] and copy_row['bytes'] == actual['bytes'], 'CRITICAL_COPY_SHA')
        for key in ('scope', 'owner_journal'):
            expected = closure[key]
            p = safe(expected['path'])
            need(p.is_relative_to(native), 'CLOSED_WITNESS_OUTSIDE_MAIN')
            actual = before['files'].get(p.relative_to(native).as_posix())
            need(actual is not None and actual['sha256'] == expected['sha256'] and actual['bytes'] == expected['bytes'],
                 'CURRENT_CLOSED_WITNESS_CHANGED:' + key)
        for name, p, expected in anchors:
            row = hash_stable(p, checked[name]['stat'], destination / name)
            need(row['sha256'] == expected, 'ANCHOR_CHANGED_DURING_DESCRIPTOR')
        after = inventory(native, False)
        need(before['directories'] == after['directories'] and before['bytes'] == after['bytes'] and
             set(before['files']) == set(after['files']), 'SECOND_ENUMERATION_PATH_OR_DIRECTORY_CHANGE')
        for name, row in before['files'].items():
            need(row['stat'] == after['files'][name]['stat'], 'SECOND_ENUMERATION_FILE_STAT_CHANGE:' + name)
        need(require_closed(native, closure) == absent, 'OWNER_BOUNDARY_CHANGED')
        members = [{**row, 'file': name, 'current_locator': str(native / name),
                    'critical_copy': str(targets[name]) if name in targets else None}
                   for name, row in before['files'].items()]
        record = {'schema': 'DEE.R07.MAIN46.current_complete_descriptor.R07', 'status': MODE,
                  'utc': utc(), 'source_root': str(native), 'life': LIFE, 'native_tick': 1019339,
                  'physical_fingerprint_recorded_by_official_owner': closure['physical_fingerprint_recorded_by_official_owner'],
                  'world': {'path': str(world), 'sha256': WORLD_SHA},
                  'closure': {'path': str(close_path), 'sha256': CLOSURE_SHA},
                  'literal_closed_ledger': {'path': str(ledger), 'sha256': LEDGER_SHA, 'consumed': 51612},
                  'members': members, 'directories': before['directories'], 'source_bytes': before['bytes'],
                  'critical_copy_bytes': copy_bytes, 'critical_copy_cap_bytes': MAX_COPY_BYTES,
                  'actual_native_owner_locks_absent': absent, 'all_current_files_hashed_once': True,
                  'second_path_set_and_stat_sweep_equal': True, 'second_full_hash_performed': False,
                  'immutable_full_backup': False, 'physical_freeze_equivalence': False,
                  'current_root_required_for_uncopied_members': True, 'rollback_or_restore_authorized': False,
                  'global_runtime_roots_and_live_ledger_touched': False, 'SQLite_connections': 0,
                  'Native_imports': 0, 'Native_calls': 0, 'MCP_calls': 0, 'new_ticks': 0,
                  'limitations': ['Same current root only; continuation can invalidate current locators.',
                                  'Stat checks cannot detect every possible concurrent rewrite.',
                                  'ADC and RAW/clocks are linked to the pinned World/official closure; no physics loader ran.',
                                  'Never restore this old literal ledger over later global accounting.']}
        manifest = destination / 'DESCRIPTOR_MAIN46_R07.json'
        new_json(manifest, record)
        result = {'status': MODE, 'manifest': str(manifest), 'members': len(members),
                  'source_bytes': before['bytes'], 'copied_critical_bytes': copy_bytes, 'Native_calls': 0}
        new_json(destination / 'RESULTADO.json', result)
        (destination / 'IN_PROGRESS.json').unlink()
        return result
    except BaseException as error:
        if created:
            try:
                safe(destination)
                new_json(destination / 'INCOMPLETE_PRESERVED.json',
                         {'utc': utc(), 'error': type(error).__name__ + ': ' + str(error),
                          'source_unchanged_by_this_tool': True, 'automatic_retry': False,
                          'partial_output_preserved': True, 'not_a_frozen_rollback': True})
            except BaseException:
                pass
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-root-only', action='store_true')
    parser.add_argument('--native-root', type=Path, default=MAIN)
    parser.add_argument('--destination', type=Path, default=DESTINATION)
    print(json.dumps(run(parser.parse_args()), ensure_ascii=False, indent=2))
