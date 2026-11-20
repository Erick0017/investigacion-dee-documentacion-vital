# C02 preparation: versioned adaptation of R04, never a Native execution.
"""Prepare only an RBX code destination and official import0 context.

Stdlib only. Does NOT import Native, create a world, launch an owner, run the
diagnostic importer, alter ACTIVO, or mutate source capsule/pair. Root reviews
and invokes the separately documented official import under a512MiB Job.
"""
from pathlib import Path, PurePosixPath
import argparse, ast, hashlib, json, os, re, shutil, stat

PAIR_MANIFEST = 'f80c72145dc5b20e1c0c066d0bab9755183eea6e7c7ef89c8ce33b8339788d19'
SOURCE_SNAPSHOT = 'fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'
CAPSULE_MANIFEST = '692d0d78772c88aad9ec59a0d564d81f71b838fbc277687a55e27edc40be6bab'
WHEEL = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHEEL_SHA = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
FUNCTION_FILES = ('lexico_generico_apd03_r02.py', 'lexico_compartido_apd04.py',
    'mente_acumulativa_r02.py', 'mente_unificada_01.py', 'percepcion_cruda_fi01.py',
    'aritmetica_apd_01.py', 'aritmetica_directa_eci02.py',
    'pi09_aritmetica_temporal_P0_R01.py', 'selector_acrecion_nativo.py')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n'); out.flush(); os.fsync(out.fileno())


# Host-only opt-in optimization. Cache existing SOURCE directory ancestors,
# never files or negative lookups. Destination paths/leaves are checked fresh.
# All member hashes, sizes, source pins and semantic preparation remain intact.
_SOURCE_ROOTS = ()
_SOURCE_DIR_CACHE = {}
_RESOLVED_ROOT_CACHE = {}
_PATH_STATS = {'lstat_calls': 0, 'cached_directory_hits': 0, 'final_rechecked': 0}

def _directory_signature(info):
    return (info.st_dev, info.st_ino, info.st_mode,
            getattr(info, 'st_file_attributes', 0))

def source_cache_begin(*roots):
    global _SOURCE_ROOTS
    need(not _SOURCE_ROOTS, 'One explicit preparation per process; no cache reuse across worlds')
    _SOURCE_ROOTS = tuple(Path(root).absolute() for root in roots)

def _safe_lstat(path):
    _PATH_STATS['lstat_calls'] += 1
    try:
        value = path.lstat()
    except FileNotFoundError:
        return None
    need(not stat.S_ISLNK(value.st_mode) and not (getattr(value, 'st_file_attributes', 0) & 1024),
         'No linked/reparse paths: ' + str(path))
    return value

def regular(path):
    path = Path(path)
    is_source = any(path.is_relative_to(root) for root in _SOURCE_ROOTS)
    for part in (path, *path.parents):
        # Positive SOURCE ancestors are shared across pair/capsule/WHL trees.
        # A destination may share one of those already checked ancestors.
        if part != path and part in _SOURCE_DIR_CACHE:
            _PATH_STATS['cached_directory_hits'] += 1
            continue
        value = _safe_lstat(part)
        if value is not None and is_source and part != path and stat.S_ISDIR(value.st_mode):
            _SOURCE_DIR_CACHE[part] = _directory_signature(value)

def source_final_recheck():
    # Full fresh ancestor sweep BEFORE the first destination mkdir/write.
    # This is a quiescent-tree check, not a claim of atomic adversarial TOCTOU protection.
    for path, expected in _SOURCE_DIR_CACHE.items():
        value = _safe_lstat(path)
        need(value is not None and stat.S_ISDIR(value.st_mode)
             and _directory_signature(value) == expected,
             'Source ancestor changed during full verification: ' + str(path))
    _PATH_STATS['final_rechecked'] = len(_SOURCE_DIR_CACHE)

def resolved_root(root):
    if any(root.is_relative_to(path) for path in _SOURCE_ROOTS):
        if root not in _RESOLVED_ROOT_CACHE:
            _RESOLVED_ROOT_CACHE[root] = root.resolve()
        return _RESOLVED_ROOT_CACHE[root]
    return root.resolve()


def member(root, name):
    p = PurePosixPath(name)
    need(p.parts and not p.is_absolute() and '\\' not in name and ':' not in name and all(x not in ('.', '..') for x in p.parts), 'Safe manifest relative path')
    target = root.joinpath(*p.parts)
    regular(target)
    need(target.resolve().is_relative_to(resolved_root(root)), 'Manifest member escapes')
    return target


def replace_once(text, before, after):
    need(text.count(before) == 1, 'Frozen patch anchor changed: ' + before[:75])
    return text.replace(before, after)


def owner_extension(text):
    text = text.replace('pi11_identidad_diagnostica_R02 as pi11_identity', 'rbx02_identity_C02 as pi11_identity')
    anchor = '        pi11_identity.validate_external(self.a,row,payload=payload)\n'
    need(text.count(anchor) == 2, 'Exactly validate/execute RBX insertion anchors')
    validation = (anchor +
        "        if row is not None and str(row.get('modo','')).startswith('eci01-rbx01-'):\n"
        "            from capacidades import rbx02_native_C02 as rbx\n"
        "            rbx.validate(self.a,row)\n"
        "            return\n")
    execution = (anchor +
        "        if row is not None and str(row.get('modo','')).startswith('eci01-rbx01-'):\n"
        "            from capacidades import rbx02_native_C02 as rbx\n"
        "            rbx.validate(self.a,row)\n"
        "            self.before_mutation('RBX01_EXPLICIT_ASYNC_NATIVE_PHASE')\n"
        "            value=rbx.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n"
        "            return {'version':rbx.VERSION,'rows':[value]}\n")
    index = text.index(anchor)
    text = text[:index] + text[index:].replace(anchor, validation, 1)
    # Skip the inserted first anchor and replace the second original anchor.
    index = text.index('    def execute(self,payload):')
    text = text[:index] + text[index:].replace(anchor, execution, 1)
    text = replace_once(text, '    def external_uncertainty(self):\n',
        "    def external_uncertainty(self):\n        from capacidades import rbx02_native_C02 as rbx\n        if rbx.uncertain(self.a):return True\n")
    text = replace_once(text,
        "        result['PI09']=pi09.operational_dependencies(self.a,self.work_directory)\n        return result\n",
        "        result['PI09']=pi09.operational_dependencies(self.a,self.work_directory)\n        from capacidades import rbx02_native_C02 as rbx\n        result['RBX01']=rbx.operational_dependencies(self.a,self.work_directory)\n        return result\n")
    text = replace_once(text, '        return result\n\n    def validate(self,payload):',
        "        from capacidades import rbx02_native_C02 as rbx\n        rbx.operational_dependencies(self.a,self.work_directory)\n        for path in (*rbx.code_files(),*pi11_identity.code_files()):\n            self.code_sha256['RBX01/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n        return result\n\n    def validate(self,payload):")
    ast.parse(text)
    return text


def prepare(product, dest, life, cutoff, *, feedback_arm, teacher_mode):
    here = Path(__file__).resolve().parent
    product = Path(product).resolve(strict=True)
    dest = Path(dest).resolve()
    regular(dest)
    need(dest.parent == here, 'Code destination only immediately beneath RBX native/')
    need(not dest.exists(), 'Fresh destination only; partial/existing preserved')
    code_scope_file = here.parent / 'protocolo/CODE_SCOPE_C02_R02.json'
    code_scope_doc = read(code_scope_file)
    need(code_scope_doc.get('schema') == 'DEE.RBX01.CODE_SCOPE_C02_R02' and code_scope_doc.get('sealed') is True, 'Frozen new C02 R02 source law required')
    for source_file, expected in code_scope_doc['source_files_sha256'].items():
        need(sha(member(here.parent, source_file)) == expected, 'Frozen C02 source changed: ' + source_file)
    for source_name in ('native/r02_bundle/rbx02_native_C02.py', 'native/r02_bundle/rbx02_identity_C02.py',
                        'native/r02_bundle/c02_funciones_native.py'):
        need(source_name in code_scope_doc['source_files_sha256'], 'Required new source not sealed before preparation: ' + source_name)
    need(life == 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02', 'Only explicit new MAIN_R02, never replay MAIN R01')
    need(cutoff == 1794738600, 'Fixed C02 Native cutoff10:30UTCNov15')
    role = 'main'
    need(feedback_arm in ('real', 'noaversive') and teacher_mode in ('paired', 'desync', 'omitted'),
         'Explicit prospective control arms')
    need(role != 'main' or (feedback_arm == 'real' and teacher_mode == 'paired'), 'Main receives real paired experience only')
    prior_contexts = list(here.glob('*/CONTEXTO_EJECUCION.json'))
    need(len(prior_contexts) < 6, 'C02 maximum6 prepared new-world namespaces; preserve prior attempts')
    need(all(read(p).get('life') != life for p in prior_contexts), 'A prior C02 namespace already exists; never create a duplicate life')
    pair = product / 'reproducibilidad/materiales/PI11_REAL2_PRE_T947395'
    capsule = product / 'reproducibilidad/codigo_preservado/PI11_HABITAT16_FAMILIA_R02'
    source_cache_begin(pair, capsule, product / 'sistema/runtime')
    need(sha(pair / 'EXPORTACION_SERVICIO.json') == PAIR_MANIFEST, 'Exact stable full pair')
    pairdoc = read(pair / 'EXPORTACION_SERVICIO.json')
    need(pairdoc['snapshot_sha256'] == SOURCE_SNAPSHOT and pairdoc['physical']['tick'] == 947395, 'Exact confirmed source cut')
    # Verify every full operational member before staging the code. No Native.
    for row in pairdoc['members']:
        target = member(pair, row['file'])
        need(target.stat().st_size == row['bytes'] and sha(target) == row['sha256'], 'Changed complete pair member: ' + row['file'])
    need(sha(capsule / 'SISTEMA_CODIGO.json') == CAPSULE_MANIFEST, 'Exact registered stable code capsule manifest')
    manifest = read(capsule / 'SISTEMA_CODIGO.json')
    capsule_files = {r['file']: r for r in manifest['files']}
    need(all('capacidades/' + name in capsule_files for name in FUNCTION_FILES),
         'Frozen PI11 capsule lacks a required lexical/numeric dependency; preserve and report, no silent fallback')
    wheel = product / 'sistema/runtime' / WHEEL
    need(sha(wheel) == WHEEL_SHA, 'Official frozen4.5.0 wheel identity')
    for row in manifest['files']:
        target = member(capsule, row['file'])
        need(target.stat().st_size == row['bytes'] and sha(target) == row['sha256'], 'Changed stable capsule member: ' + row['file'])
    source_final_recheck()
    need(sha(pair / 'EXPORTACION_SERVICIO.json') == PAIR_MANIFEST, 'Pair manifest changed before mkdir')
    need(sha(capsule / 'SISTEMA_CODIGO.json') == CAPSULE_MANIFEST, 'Capsule manifest changed before mkdir')
    need(sha(wheel) == WHEEL_SHA, 'WHL changed before mkdir')
    regular(dest)
    need(not dest.exists(), 'Destination appeared during read-only verification; preserve')
    dest.mkdir()
    system = dest / 'sistema'; system.mkdir()
    before = {}
    for row in manifest['files']:
        relative = row['file']; source = member(capsule, relative)
        need(not relative.startswith(('estado/', 'runtime/')) and not relative.endswith('.sqlite3'), 'Code capsule cannot inject state/queue/runtime')
        target = member(system, relative); target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        before[relative] = row['sha256']
    (system / 'estado/checkpoints').mkdir(parents=True)
    (system / 'runtime').mkdir()
    shutil.copyfile(wheel, system / 'runtime' / WHEEL)
    need(sha(system / 'runtime' / WHEEL) == WHEEL_SHA, 'Official wheel copy must remain byte-identical; no install/change')
    # Administrative scope only; no historical scientific actor/protocol edits.
    transport = system / 'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json'
    administrative = read(transport); administrative['life_id'] = life; administrative['role'] = 'rbx01'
    transport.write_text(json.dumps(administrative, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    registry = system / 'capacidades/PI10_PLUGINS_R01.json'
    pins = read(registry); pins['files_sha256'][transport.name] = sha(transport)
    registry.write_text(json.dumps(pins, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    # No PI11 role/identity fiction; new namespace and actor installed locally.
    for name in ('rbx02_native_C02.py', 'rbx02_identity_C02.py', 'c02_funciones_native.py'):
        source = here / 'r02_bundle' / name
        relative = str(source.relative_to(here.parent)).replace('\\', '/')
        need(relative in code_scope_doc['source_files_sha256'] and
             sha(source) == code_scope_doc['source_files_sha256'][relative], 'New Native function source not frozen: ' + relative)
        shutil.copyfile(source, system / 'capacidades' / name)
    owner = system / 'app/mundo_genesis_apd05.py'
    owner.write_text(owner_extension(owner.read_text('utf-8-sig')), encoding='utf8')
    queue = system / 'app/cola_local.py'
    text = replace_once(queue.read_text('utf-8-sig'), '        for row in rows:\n',
        "        for row in rows:\n            if str(row.get('modo','')).startswith('eci01-rbx01-'):\n                from capacidades.rbx02_native_C02 import validate_literal\n                validate_literal(row)\n                continue\n")
    ast.parse(text); queue.write_text(text, encoding='utf8')
    sources = {name: sha(system / 'capacidades' / name) for name in
               ('rbx02_native_C02.py', 'rbx02_identity_C02.py', 'c02_funciones_native.py')}
    write(system / 'capacidades/RBX02_NATIVE_SCOPE_C02_R02.json', {
        'schema': 'DEE.RBX01.fixed_native_scope.C02.R02', 'sealed': True, 'life_id': life,
        'code_scope': 'DEE.RBX01.CODE_SCOPE_C02_R02', 'role': role, 'feedback_arm': feedback_arm,
        'teacher_mode': teacher_mode,
        'code_scope_manifest_sha256': sha(code_scope_file),
        'source_life_id': pairdoc['life_id'], 'source_tick': 947395,
        'source_snapshot_sha256': SOURCE_SNAPSHOT, 'source_pair_manifest_sha256': PAIR_MANIFEST,
        'max_cycles': {'main': 48, 'control': 6, 'diagnostic': 4}[role], 'max_ticks_per_cycle': 4096, 'max_total_ticks': 200000,
        'max_raw_support': 10000, 'monitor_tick_block': 16, 'max_permission_stock': 200,
        'native_cutoff_utc_epoch': cutoff, 'sources_sha256': sources,
        'last_new_cycle_utc_epoch': 1794736800,
        'input_codec': {'Q1': '1+zone0..5+8*key+16*resource+32*lastFailure => scalar1..62; no task target',
                        'Q2': 'fresh paid stationSignal0/1/2 -> same datum; NoQuery=-1 omits datum pulse',
                        'function': 'visible signed LESSON via APD03; CALCULATE word-only APD04 recall -> fixed +/- operation codec -> actual Native FI128 integer'},
        'feedback': 'Actual codeRejected/collision/invalid failure bool to both generic hubs; toll alone excluded; noaversive False twice, same generic pulse count/calendar; Native efference selects bank',
        'new_anatomy': False, 'PI10_stock_consumed': False, 'promotion': False})
    changed = {name: {'before': before[name], 'after': sha(system / name)}
               for name in before if sha(system / name) != before[name]}
    need(set(changed) == {'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json', 'capacidades/PI10_PLUGINS_R01.json', 'app/mundo_genesis_apd05.py', 'app/cola_local.py'}, 'Only four declared old code/admin files may change')
    context = {'schema': 'DEE.RBX01.official_import_context.R01', 'system': str(system),
               'life': life, 'prefix': str(pair), 'prefix_manifest_sha256': PAIR_MANIFEST,
               'tool_sources': [{'file': name, 'sha256': sha(product / 'reproducibilidad' / name)}
                                for name in ('importar_diagnostico.py', 'observador_pasivo.py')]}
    write(dest / 'CONTEXTO_EJECUCION.json', context)
    record = {'schema': 'DEE.RBX01.code_preparation.C02.R02', 'life_id': life,
              'source_pair': str(pair), 'source_capsule': str(capsule), 'changed_files': changed,
              'new_files': sources, 'Native_imported': False, 'new_native_ticks': 0,
              'required_function_dependencies_from_pinned_capsule': list(FUNCTION_FILES),
              'no_current_product_source_fallback_needed': True,
              'world_created': False, 'ACTIVO_created': False,
              'next_action': 'Root only: official importar_diagnostico.py under512MiBJob; then compare physical+causal prefix'}
    record['host_path_verification'] = dict(_PATH_STATS, source_ancestor_cache_only=True,
        full_member_SHA256_and_size_checks_unchanged=True,
        no_atomic_TOCTOU_claim=True, source_ancestors_freshly_rechecked_before_first_mkdir=True)
    write(dest / 'RBX02_PREPARACION_C02_R02.json', record)
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--product', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--life', required=True)
    parser.add_argument('--native-cutoff-utc-epoch', type=float, required=True)
    parser.add_argument('--feedback-arm', choices=('real', 'noaversive'), required=True)
    parser.add_argument('--teacher-mode', choices=('paired', 'desync', 'omitted'), required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.product, args.destination, args.life, args.native_cutoff_utc_epoch,
        feedback_arm=args.feedback_arm, teacher_mode=args.teacher_mode), ensure_ascii=False, indent=2))
