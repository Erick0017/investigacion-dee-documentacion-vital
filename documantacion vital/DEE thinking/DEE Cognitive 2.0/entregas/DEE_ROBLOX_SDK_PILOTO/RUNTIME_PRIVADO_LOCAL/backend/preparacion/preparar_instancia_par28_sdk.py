"""Private, stdlib-only SDK preparation. No Native import, owner or SQLite use.

plan() reads manifests/anchors only; it neither verifies nor copies the 5327
state members. prepare() copies the declared code template and two anchors to
ONE unused SDK identity. The complete immutable prefix remains shared. The
separate Root-only importer performs official import_pair later, never T0.

PLANTILLA_SISTEMA.json: schema, members[{file,bytes,sha256}] relative to
dependencias/sistema_base, empty_directories, tool_sources[{file,sha256}] and
import_paths relative to the runtime, anchors.sourceWorld/sourceRecord
{file,sha256}. No operational lookup falls back to the historical laboratory.
"""
from pathlib import Path, PurePosixPath
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
import time
import uuid

SCHEMA = 'DEE.Roblox.SDK.private.0.1.0'
RUNTIME = Path(__file__).resolve().parents[2]
ID = re.compile(r'SDK_DEMO_[0-9A-F]{16}')
SESSION = re.compile(r'SDK_SESSION_[0-9a-f]{32}')
LIFE_PREFIX = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'
SOURCE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V2_MAIN'
SNAPSHOT = 'b3163197548980355c45c6ffd57d2785b3a5e75cf71d8de3afb6b6ffdd4722d1'
EXPORT_SHA = 'fb3fdada9423eb890c8b0a466be74f60568c2464c8cfc004bf32c3b8950f3e7e'
PAIR_SHA = 'c4638b02ea660f2e32d13c015637e817a28d471e96c3bee0284918f1d55cf2c2'
WORLD_SHA = '48544f655382bdf97b4930200158e35371d878c29d17c1ce918077aa27cf6930'
PREFIX = 'estado_demo/prefijos/PAR28_COMPLETO'
TEMPLATE = 'dependencias/sistema_base'
TEMPLATE_INDEX = 'dependencias/PLANTILLA_SISTEMA.json'
WINDOW = 'configuracion/VENTANA_CONGELADA.json'
REQUIRED_CODE = {'app/lives.py', 'app/native_tools.py', 'app/importacion_emparejada.py',
                 'capacidades/rbx07_native_v3.py', 'capacidades/rbx07_identity_v3.py',
                 'capacidades/rbx07_funciones_v3.py', 'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json',
                 'capacidades/PI10_PLUGINS_R01.json'}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def raw(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf8')


def new_json(path, value):
    with Path(path).open('xb') as out:
        out.write(raw(value)); out.flush(); os.fsync(out.fileno())


def relative(name):
    need(isinstance(name, str) and name and '\\' not in name and ':' not in name,
         'EXPLICIT_RELATIVE_PATH')
    need(all(part not in ('', '.', '..') for part in name.split('/')), 'NO_DOT_OR_EMPTY_SEGMENTS')
    p = PurePosixPath(name)
    need(not p.is_absolute(), 'NO_ABSOLUTE_MEMBER')
    return p


def unlinked(s):
    need(not stat.S_ISLNK(s.st_mode) and not getattr(s, 'st_file_attributes', 0) & 1024,
         'NO_SYMLINK_OR_REPARSE')


def fingerprint(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns,
            getattr(s, 'st_file_attributes', 0))


class Guard:
    """Per-operation ancestor cache, never a global cache or directory census."""
    def __init__(self, root):
        self.root = Path(os.path.abspath(root)); self.directories = {}
        for p in reversed((self.root, *self.root.parents)):
            s = p.lstat(); unlinked(s)
            need(stat.S_ISDIR(s.st_mode), 'DIRECTORY_ROOT_REQUIRED')
            self.directories[p] = (s.st_dev, s.st_ino)

    def path(self, name, exists=True):
        p = self.root / relative(name)
        cursor = self.root
        for part in p.relative_to(self.root).parts[:-1]:
            cursor = cursor / part
            if cursor not in self.directories and os.path.lexists(cursor):
                s = cursor.lstat(); unlinked(s)
                need(stat.S_ISDIR(s.st_mode), 'DIRECTORY_PARENT_REQUIRED')
                self.directories[cursor] = (s.st_dev, s.st_ino)
        if os.path.lexists(p):
            unlinked(p.lstat())
        elif exists:
            raise FileNotFoundError(p)
        return p

    def recheck(self):
        for p, identity in self.directories.items():
            s = p.lstat(); unlinked(s)
            need(stat.S_ISDIR(s.st_mode) and (s.st_dev, s.st_ino) == identity,
                 'DIRECTORY_IDENTITY_CHANGED')


def hash_file(path):
    """Regular-file read, identity and complete same-API stats before/after."""
    path = Path(path); before = path.lstat(); unlinked(before)
    need(stat.S_ISREG(before.st_mode), 'REGULAR_FILE_REQUIRED')
    h = hashlib.sha256(); count = 0
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        opened = os.fstat(stream.fileno())
        # Windows lstat/fstat ctime meanings can differ; preserve same-API checks.
        a, b = fingerprint(before), fingerprint(opened)
        need(a[:5] + a[6:] == b[:5] + b[6:], 'OPENED_FILE_IDENTITY_CHANGED')
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block); count += len(block)
        need(count == before.st_size and fingerprint(os.fstat(stream.fileno())) == fingerprint(opened),
             'FILE_CHANGED_DURING_READ')
    after = path.lstat(); unlinked(after)
    need(fingerprint(after) == fingerprint(before), 'FILE_CHANGED_AFTER_READ')
    return h.hexdigest()


def copy_checked(source, target, expected, source_guard, target_guard):
    source = source_guard.path(source); target = target_guard.path(target, exists=False)
    need(not os.path.lexists(target), 'FRESH_DESTINATION_FILE_ONLY')
    before = source.lstat(); unlinked(before)
    need(stat.S_ISREG(before.st_mode) and before.st_size == expected['bytes'], 'SOURCE_SIZE_MISMATCH')
    target.parent.mkdir(parents=True, exist_ok=True)
    # Validate newly created parents before opening the exclusive destination.
    target_guard.path(target.relative_to(target_guard.root).as_posix(), exists=False)
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    h = hashlib.sha256(); count = 0
    with os.fdopen(os.open(source, flags), 'rb') as inp, target.open('xb') as out:
        opened = os.fstat(inp.fileno()); a, b = fingerprint(before), fingerprint(opened)
        need(a[:5] + a[6:] == b[:5] + b[6:], 'SOURCE_IDENTITY_CHANGED_AT_OPEN')
        for block in iter(lambda: inp.read(1048576), b''):
            count += len(block); need(count <= expected['bytes'], 'SOURCE_GREW_DURING_COPY')
            h.update(block); out.write(block)
        out.flush(); os.fsync(out.fileno())
        need(fingerprint(os.fstat(inp.fileno())) == fingerprint(opened), 'SOURCE_CHANGED_DURING_COPY')
    need(count == expected['bytes'] and h.hexdigest() == expected['sha256'] and
         fingerprint(source.lstat()) == fingerprint(before), 'SOURCE_COPY_HASH_MISMATCH')
    need(hash_file(target) == expected['sha256'], 'TARGET_COPY_HASH_MISMATCH')


def member_rows(rows, *, template=False):
    need(isinstance(rows, list), 'MEMBER_LIST_REQUIRED')
    result = {}
    for row in rows:
        name = row['file']; p = relative(name)
        need(name not in result and type(row['bytes']) is int and row['bytes'] >= 0 and
             re.fullmatch(r'[0-9a-f]{64}', row['sha256']) is not None, 'UNIQUE_EXACT_MEMBER_REQUIRED')
        if template:
            need(p.parts[0] not in ('estado', '.git', '.codex') and p.name != 'ACTIVO.json',
                 'TEMPLATE_MUST_NOT_CONTAIN_OPERATIONAL_STATE')
        result[name] = row
    return result


def window(runtime, now=None):
    p = Guard(runtime).path(WINDOW); c = read(p)
    keys = {'schema', 'startUtcEpoch', 'lastNewUtcEpoch', 'hardFinishUtcEpoch', 'maxNativeTicks',
            'maxSdkCycles', 'ownerMemoryBytes', 'threads', 'maxRawSupport', 'minimumHostFreeBytes', 'sealed'}
    need(set(c) == keys and c['schema'] == SCHEMA and c['sealed'] is True, 'FROZEN_SDK_WINDOW_REQUIRED')
    need(c['startUtcEpoch'] < c['lastNewUtcEpoch'] < c['hardFinishUtcEpoch'] and
         c['hardFinishUtcEpoch'] - c['startUtcEpoch'] <= 21600 and c['maxNativeTicks'] == 40000 and
         c['maxSdkCycles'] == 3 and c['ownerMemoryBytes'] == 536870912 and c['threads'] == 1 and
         c['maxRawSupport'] == 10000 and c['minimumHostFreeBytes'] == 3758096384, 'SDK_BOUNDS_CHANGED')
    return c, hash_file(p)


def project_public_state(source_world):
    """NEW only: seven fields from pinned B-absent PAR28, never invented lineage.

    Resume/K4 must use the actual saved Agent.snapshot, never this projection.
    The complete original World remains a separate private pinned anchor.
    """
    s = source_world['S']
    need(type(s['permissionStock']) is int and type(s['numberAVersion']) is int,
         'EXACT_PUBLIC_INTEGER_FIELDS')
    for name in ('inventoryKey', 'inventoryResource', 'numberAPresent', 'codeBPresent'):
        need(type(s[name]) is bool, 'EXACT_PUBLIC_BOOLEAN:' + name)
    need(s['codeBPresent'] is False, 'NO_PRESENT_B_WITHOUT_DECLARED_LINEAGE')
    result = {name: s[name] for name in ('permissionStock', 'inventoryKey', 'inventoryResource',
              'numberAPresent', 'codeBPresent', 'numberAVersion')}
    result['codeBCurrent'] = False
    return result


def plan(runtime=RUNTIME, instance_id=None, session_id=None):
    runtime = Path(os.path.abspath(runtime)); guard = Guard(runtime)
    instance_id = instance_id or 'SDK_DEMO_' + uuid.uuid4().hex[:16].upper()
    session_id = session_id or 'SDK_SESSION_' + uuid.uuid4().hex
    need(isinstance(instance_id, str) and ID.fullmatch(instance_id) is not None, 'SDK_NEW_ID_ONLY')
    need(isinstance(session_id, str) and SESSION.fullmatch(session_id) is not None, 'SDK_NEW_SESSION_ONLY')
    home_rel = 'estado_demo/instancias/' + instance_id
    need(not os.path.lexists(guard.path(home_rel, exists=False)), 'NEW_INSTANCE_NO_REUSE_OR_RETRY')
    index = guard.path(TEMPLATE_INDEX); template = read(index)
    need(template['schema'] == SCHEMA, 'SDK_TEMPLATE_SCHEMA')
    rows = member_rows(template['members'], template=True)
    need(REQUIRED_CODE <= rows.keys(), 'COMPLETE_OFFICIAL_CODE_TEMPLATE_REQUIRED')
    for name in template['empty_directories']: relative(name)
    for name in template['import_paths']: guard.path(name)
    tools = template['tool_sources']
    need(isinstance(tools, list) and {Path(r['file']).name for r in tools} >=
         {'importar_diagnostico.py', 'observador_pasivo.py'}, 'PINNED_OFFICIAL_TOOLS_REQUIRED')
    for row in tools:
        need(hash_file(guard.path(row['file'])) == row['sha256'], 'OFFICIAL_TOOL_CHANGED')
    prefix_index = guard.path(PREFIX + '/EXPORTACION_SERVICIO.json')
    need(hash_file(prefix_index) == EXPORT_SHA, 'ORIGINAL_PAR28_EXPORT_MANIFEST_REQUIRED')
    prefix = read(prefix_index); member_rows(prefix['members'])
    need(prefix['schema'] == 'DEE.persistent_service.paired_export.v1' and prefix['life_id'] == SOURCE and
         prefix['backend'] == 'mente_unificada' and prefix['profile'] == 'fisica_directa' and
         prefix['queue_journal_required'] is True and prefix['new_Native_ticks'] == 0 and
         prefix['snapshot_sha256'] == SNAPSHOT and prefix['physical']['N'] == 67 and
         prefix['physical']['tick'] == 991187 and prefix['source_PAR28_manifest_sha256'] == PAIR_SHA,
         'COMPLETE_ORIGINAL_PAR28_NOT_USED_PILOT')
    for name in prefix['empty_directories_preserved']: relative(name)
    anchors = template['anchors']; world_row = anchors['sourceWorld']; card_row = anchors['sourceRecord']
    need(world_row['sha256'] == WORLD_SHA and hash_file(guard.path(world_row['file'])) == WORLD_SHA,
         'LITERAL_ORIGINAL_PAR28_WORLD')
    need(hash_file(guard.path(card_row['file'])) == card_row['sha256'], 'LITERAL_PARENT_CARD')
    source_world = read(guard.path(world_row['file'])); card = read(guard.path(card_row['file']))
    need(source_world['native_tick'] == 991187 and source_world['S']['completedCycles'] == 28 and
         source_world['S']['seq'] == 56 and source_world['S']['permissionStock'] == 164 and
         card['life_id'] == SOURCE and card['snapshot_sha256'] == SNAPSHOT and
         card['physical']['N'] == 67 and card['physical']['tick'] == 991187, 'PAR28_ANCHOR_COUNTERS')
    limits, budget_sha = window(runtime)
    cfg = {'instanceId': instance_id, 'lifeId': LIFE_PREFIX + instance_id, 'sequenceOffset': 56,
           'initialPublicState': project_public_state(source_world), 'sourceWorldSha256': WORLD_SHA,
           'sessionId': session_id, 'runtimeVersion': '0.1.0', 'nextPhase': 'decision',
           'localSequence': 0, 'nativeTick': 991187, 'completedCycles': 0}
    result = {'schema': SCHEMA, 'status': 'FS_PLAN_ONLY_NO_NATIVE_OR_STATE_COPY', 'instance': cfg,
              'home': home_rel, 'templateManifestSha256': hash_file(index), 'budgetSha256': budget_sha,
              'limits': limits, 'sourcePrefix': PREFIX, 'sourcePrefixManifestSha256': EXPORT_SHA,
              'sourceSnapshotSha256': SNAPSHOT, 'anchors': anchors, 'tool_sources': tools,
              'import_paths': template['import_paths'], 'templateMembers': len(rows),
              'templateBytes': sum(r['bytes'] for r in rows.values()),
              'prefixMembers': len(prefix['members']), 'prefixBytes': sum(r['bytes'] for r in prefix['members']),
              'payloadVerificationDeferredToOfficialImportPair': True, 'Native_imported': False}
    guard.recheck()
    return result


def _configure(runtime, home, cfg):
    """Parent-owned, FS-only scope/host builder. No actor/owner is opened here."""
    source = Guard(runtime).path('backend/configure_instance.py')
    sys.path.insert(0, str(Path(runtime) / 'backend'))
    spec = importlib.util.spec_from_file_location('_sdk_prepare_instance_scopes', source)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.create_scopes(home, cfg)


def prepare(planned, runtime=RUNTIME, *, execute_root_only=False):
    need(execute_root_only is True, 'ROOT_ONLY_FS_PREPARATION')
    runtime = Path(os.path.abspath(runtime)); guard = Guard(runtime)
    cfg = planned['instance']; current = plan(runtime, cfg['instanceId'], cfg['sessionId'])
    need(current == planned, 'PLAN_OR_SOURCE_CHANGED')
    # FS preparation is reusable and makes no Native admission. Material import
    # and each operating lease receive their own explicit finite Root deadline.
    guard.path('backend/configure_instance.py')
    home = guard.path(current['home'], exists=False); home.mkdir(parents=True)
    try:
        new_json(home / 'PREPARACION_EN_CURSO.json', {'schema': SCHEMA, 'lifeId': cfg['lifeId'], 'Native_imported': False})
        system = home / 'sistema'; system.mkdir(); template = read(guard.path(TEMPLATE_INDEX))
        source_guard = Guard(guard.path(TEMPLATE)); target_guard = Guard(system)
        for name, row in member_rows(template['members'], template=True).items():
            copy_checked(name, name, row, source_guard, target_guard)
        for name in [*template['empty_directories'], 'estado/checkpoints', 'estado/locks']:
            target_guard.path(name, exists=False).mkdir(parents=True, exist_ok=True)
        transport = target_guard.path('capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json')
        value = read(transport); value['life_id'] = cfg['lifeId']; value['role'] = 'rbx01'
        transport.write_bytes(raw(value))
        registry = target_guard.path('capacidades/PI10_PLUGINS_R01.json')
        value = read(registry); value['files_sha256'][transport.name] = hash_file(transport)
        registry.write_bytes(raw(value))
        for key, name in [('sourceWorld', 'WORLD_PADRE_PAR28.json'), ('sourceRecord', 'VIDA_PADRE_PAR28.json')]:
            row = current['anchors'][key]; source = guard.path(row['file'])
            copy_checked(row['file'], name, {'bytes': source.stat().st_size, 'sha256': row['sha256']}, guard, Guard(home))
        _configure(runtime, home, cfg)
        need(not (system / 'estado/ACTIVO.json').exists(), 'PREPARATION_MUST_NOT_SELECT_LIFE')
        need(not (system / 'estado/vidas').exists() or not any((system / 'estado/vidas').iterdir()),
             'PREPARATION_MUST_NOT_IMPORT_OR_CREATE_LIFE')
        context = {'schema': SCHEMA, 'life': cfg['lifeId'], 'instance_id': cfg['instanceId'],
                   'product': 'dependencias/producto', 'system': (home / 'sistema').relative_to(runtime).as_posix(),
                   'prefix': PREFIX, 'prefix_manifest_sha256': EXPORT_SHA,
                   'source_life_id': SOURCE, 'source_tick': 991187, 'source_snapshot_sha256': SNAPSHOT,
                   'source_world': (home / 'WORLD_PADRE_PAR28.json').relative_to(runtime).as_posix(),
                   'source_world_sha256': WORLD_SHA,
                   'source_record': (home / 'VIDA_PADRE_PAR28.json').relative_to(runtime).as_posix(),
                   'source_record_sha256': current['anchors']['sourceRecord']['sha256'],
                   'source_code_directory': TEMPLATE, 'template_manifest': TEMPLATE_INDEX,
                   'template_manifest_sha256': current['templateManifestSha256'], 'budget_sha256': current['budgetSha256'],
                   'tool_sources': current['tool_sources'], 'import_paths': current['import_paths'],
                   'new_native_ticks': 0, 'preparation_did_not_import_native': True}
        new_json(home / 'INSTANCE.json', cfg); new_json(home / 'CONTEXTO_EJECUCION.json', context)
        source_guard.recheck(); target_guard.recheck(); guard.recheck()
        new_json(home / 'PREPARACION_PAR28_SDK.json', {'schema': SCHEMA, 'status': 'PREPARED_NOT_IMPORTED',
                 'instanceId': cfg['instanceId'], 'sourceTick': 991187, 'sequenceOffset': 56,
                 'sharedPrefixCopiedByPreparation': False, 'Native_imported': False, 'new_native_ticks': 0,
                 'context_sha256': hash_file(home / 'CONTEXTO_EJECUCION.json')})
        (home / 'PREPARACION_EN_CURSO.json').unlink()
        return {'status': 'PREPARED_NOT_IMPORTED', 'home': current['home'], 'instanceId': cfg['instanceId']}
    except BaseException as error:
        try:
            new_json(home / 'PREPARACION_INCOMPLETA.json', {'schema': SCHEMA, 'error': repr(error),
                     'partial_preserved': True, 'automatic_retry': False, 'Native_imported': False})
        except BaseException:
            pass
        raise


def resolve_context(home, runtime=RUNTIME):
    """Resolve private relative locators in MEMORY; never rewrite the portable file."""
    runtime = Path(os.path.abspath(runtime)); guard = Guard(runtime); home = Path(os.path.abspath(home))
    need(home.parent == runtime / 'estado_demo/instancias' and ID.fullmatch(home.name) is not None,
         'ONE_EXPLICIT_PRIVATE_SDK_INSTANCE')
    guard.path(home.relative_to(runtime).as_posix())
    home_rel = home.relative_to(runtime).as_posix()
    c = read(guard.path(home_rel + '/CONTEXTO_EJECUCION.json'))
    cfg = read(guard.path(home_rel + '/INSTANCE.json'))
    need(c['schema'] == SCHEMA and c['life'] == cfg['lifeId'] == LIFE_PREFIX + home.name and
         c['instance_id'] == cfg['instanceId'] == home.name,
         'EXACT_NEW_SDK_IDENTITY')
    need(c['source_life_id'] == SOURCE and c['source_tick'] == 991187 and
         c['source_snapshot_sha256'] == SNAPSHOT and c['prefix_manifest_sha256'] == EXPORT_SHA,
         'ORIGINAL_PAR28_CONTEXT_ONLY')
    result = copy.deepcopy(c)
    for key in ('product', 'system', 'prefix', 'source_world', 'source_record', 'source_code_directory', 'template_manifest'):
        result[key] = str(guard.path(c[key]))
    need(Path(result['system']) == home / 'sistema' and Path(result['prefix']) == runtime / PREFIX,
         'NO_OPERATIONAL_PATH_REDIRECTION')
    need(Path(result['product']) == runtime / 'dependencias/producto' and
         Path(result['source_world']) == home / 'WORLD_PADRE_PAR28.json' and
         Path(result['source_record']) == home / 'VIDA_PADRE_PAR28.json' and
         Path(result['source_code_directory']) == runtime / TEMPLATE and
         Path(result['template_manifest']) == runtime / TEMPLATE_INDEX, 'FIXED_PRIVATE_RUNTIME_LOCATORS')
    result['tool_sources'] = [{**row, 'file': str(guard.path(row['file']))} for row in c['tool_sources']]
    result['import_paths'] = [str(guard.path(name)) for name in c['import_paths']]
    result['import_paths'][:0] = [result['system'], str(Path(result['system']) / 'app')]
    guard.recheck()
    return result


def preserve_source_empty_directories(home, runtime=RUNTIME):
    c = resolve_context(home, runtime); m = read(Path(c['prefix']) / 'EXPORTACION_SERVICIO.json')
    system = Path(c['system']); guard = Guard(system); created = []
    for name in m['empty_directories_preserved']:
        p = relative(name)
        if p.parts[0] == 'artefactos_trabajador':
            rel = Path('estado/servicios_locales') / c['life'] / Path(*p.parts[1:])
        else:
            rel = Path('estado/servicios_persistentes') / c['life'] / Path(*p.parts)
        target = guard.path(rel.as_posix(), exists=False); target.mkdir(parents=True, exist_ok=True)
        created.append(rel.as_posix())
    guard.recheck()
    return created


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=RUNTIME)
    parser.add_argument('--instance-id'); parser.add_argument('--session-id')
    parser.add_argument('--execute-root-only', action='store_true')
    parser.add_argument('--prepare', action='store_true', help='Copy code/anchors only; never imports Native')
    args = parser.parse_args(); value = plan(args.runtime, args.instance_id, args.session_id)
    if args.prepare: value = prepare(value, args.runtime, execute_root_only=args.execute_root_only)
    print(json.dumps(value, ensure_ascii=False, indent=2))
