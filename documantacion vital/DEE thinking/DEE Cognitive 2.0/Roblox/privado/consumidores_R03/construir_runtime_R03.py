"""Root-only FS build of the private SDK. Never imports DEE or creates a world.

Copies Cognitive glue and one official binary runtime, not kernel source. The
whole one-life paired export is copied separately and remains immutable.
"""
from pathlib import Path
import argparse
import ast
import datetime as dt
import hashlib
import json
import os
import secrets
import shutil
import sys

# R03: adaptación de localización; el constructor y sus protocolos se conservan.
_R03_PRODUCT = Path(__file__).resolve().parents[3]
_R03_LOCATOR_OVERRIDE = None

def _r03_config(product=None):
    product = Path(product or _R03_PRODUCT).resolve(strict=True)
    locator = _R03_LOCATOR_OVERRIDE or product / 'Roblox/LOCALIZADORES.json'
    return product, json.loads(Path(locator).read_text('utf-8-sig'))

def _r03_plain(path):
    for point in (path, *path.parents):
        if point.is_symlink() or getattr(point.lstat(), 'st_file_attributes', 0) & 1024:
            raise ValueError('R03_PHYSICAL_PATH_REQUIRED')
    return path

def _r03_laboratory(product=None):
    product, config = _r03_config(product)
    relative = Path(config['laboratory_active_relative'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('R03_RELATIVE_LAB_REQUIRED')
    path = product / 'Roblox' / relative
    _r03_plain(path)
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(product / 'Roblox/laboratorio') or not resolved.is_dir():
        raise ValueError('R03_CANONICAL_LAB_REQUIRED_NO_FALLBACK')
    return resolved

def _r03_runtime():
    _, config = _r03_config()
    if config.get('fallbackToProvisionBundle') is not False:
        raise ValueError('R03_NO_RUNTIME_FALLBACK')
    root = Path(config['operationalRuntime']).resolve(strict=True)
    _r03_plain(root)
    return root

def _r03_check(product):
    lab = _r03_laboratory(product)
    relative_files = [
        'revision_R07_CIERRE_8_PUNTOS/native/lease_PILOT_R07_bundle/rbx07_native_v3.py',
        'revision_R07_CIERRE_8_PUNTOS/native/bundle/rbx07_identity_v3.py',
        'revision_R07_CIERRE_8_PUNTOS/native/bundle/rbx07_funciones_v3.py',
        'revision_R07_CIERRE_8_PUNTOS/native/adapter_v3.py',
        'revision_R07_CIERRE_8_PUNTOS/native/owner_support_v3_R07.py',
        'revision_R07_CIERRE_8_PUNTOS/native/PILOT/sistema/app/servicio_eventos_v3.py',
        'revision_R07_CIERRE_8_PUNTOS/native/PILOT/VIDA_PADRE_PAR28.json',
        'revision_R06_INTEGRAL_V2/evidencia/NATIVE_CONTINUACION_C16_R01/WORLD_CHECKPOINT.json']
    rows = []
    for relative in relative_files:
        path = lab / relative
        _r03_plain(path)
        data = path.read_bytes()
        rows.append({'relative':relative,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    for relative in ['revision_R06_INTEGRAL_V2/evidencia/PAR28/native_root/sistema',
                     'revision_R07_CIERRE_8_PUNTOS/persistencia/PREFIJO_PAR28_COMPLETO']:
        path=lab/relative; _r03_plain(path)
        if not path.is_dir():raise ValueError('R03_REQUIRED_SOURCE_TREE_MISSING')
    return {'schema':'DEE.Roblox.SourceRouting.R03','laboratory':str(lab),
            'runtime':str(_r03_runtime()),'source_files':rows,
            'NativeImported':False,'worldOpened':False,'SQLiteOpened':False,'buildExecuted':False}

if __name__ == '__main__' and '--verificar-fuentes' in sys.argv:
    parser = argparse.ArgumentParser(description='R03: comprobación de rutas, sin Native ni build.')
    parser.add_argument('--source-product', required=True)
    parser.add_argument('--localizadores', type=Path)
    parser.add_argument('--verificar-fuentes', action='store_true', required=True)
    arguments = parser.parse_args()
    _R03_LOCATOR_OVERRIDE = arguments.localizadores
    print(json.dumps(_r03_check(arguments.source_product), ensure_ascii=False, indent=2))
    raise SystemExit(0)

sys.path.insert(0, str(_r03_runtime() / 'backend'))


from sdk_common import RUNTIME, SCHEMA, atomic, canonical, read, safe, sha

def replace_once(text, before, after):
    if text.count(before) != 1: raise ValueError('Source anchor count changed: ' + before[:100])
    return text.replace(before, after)

def checked_copy(source, target):
    source = Path(source); target = Path(target)
    st = source.lstat()
    if source.is_symlink() or getattr(st, 'st_file_attributes', 0) & 1024: raise ValueError('No linked source')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.is_file() and sha(target) == sha(source): return
        raise FileExistsError('Preserve differing destination ' + str(target))
    temp = target.with_name(target.name + '.COPYING')
    with source.open('rb') as inp, temp.open('xb') as out:
        shutil.copyfileobj(inp, out, 1024 * 1024); out.flush(); os.fsync(out.fileno())
    if sha(source) != sha(temp): raise RuntimeError('Copy/source SHA mismatch')
    os.replace(temp, target)

def tree(source, target, *, exclude=(), include_bytecode=False, exclude_suffixes=()):
    source = Path(source); target = Path(target)
    for current, dirs, files in os.walk(source, followlinks=False):
        rel = Path(current).relative_to(source)
        if Path(current).is_symlink() or getattr(Path(current).lstat(), 'st_file_attributes', 0) & 1024: raise ValueError('Linked directory')
        dirs[:] = [d for d in dirs if d not in exclude and d != '__pycache__']
        (target / rel).mkdir(parents=True, exist_ok=True)
        for name in files:
            if (not include_bytecode and name.endswith(('.pyc', '.pyo'))) or name in exclude or name.endswith(exclude_suffixes): continue
            checked_copy(Path(current) / name, target / rel / name)

def write_source(target, text):
    ast.parse(text)
    target = Path(target); target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if target.read_bytes() == text.encode('utf8'): return
        raise FileExistsError('Generated SDK source differs; preserve prior version')
    with target.open('x', encoding='utf8', newline='\n') as out: out.write(text)

def build(product, *, copy_payload=False):
    product = Path(product).resolve(strict=True)
    r07 = _r03_laboratory(product) / 'revision_R07_CIERRE_8_PUNTOS'
    r06 = _r03_laboratory(product) / 'revision_R06_INTEGRAL_V2'
    deps = RUNTIME / 'dependencias'; deps.mkdir(exist_ok=True)
    window = read(RUNTIME / 'configuracion/VENTANA_CONGELADA.json')
    hard = window['hardFinishUtcEpoch']; last = window['lastNewUtcEpoch']
    # Keep the three original apparatus basenames because the unchanged
    # Cognitive dispatcher imports them. New KEY/FOLDER prevent epoch reuse.
    actor = (r07 / 'native/lease_PILOT_R07_bundle/rbx07_native_v3.py').read_text('utf-8-sig')
    replacements = {
        "VERSION = 'DEE.RBX01.async_native.INTEGRAL.V3.R01'": "VERSION = 'DEE.Roblox.SDK.native.0.1.0'",
        "KEY = 'DEE.Cognitive.RBX01.async_native.INTEGRAL.V3.R01'": "KEY = 'DEE.Cognitive.Roblox.SDK.native.0.1.0'",
        "CODE_SCOPE_KEY = 'DEE.Cognitive.RBX01.CODE_SCOPE_INTEGRAL_V3'": "CODE_SCOPE_KEY = 'DEE.Cognitive.Roblox.SDK.CODE_SCOPE.0.1.0'",
        "FOLDER = 'RBX07_NATIVE_INTEGRAL_V3'": "FOLDER = 'DEE_SDK_NATIVE_0_1_0'",
        "re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_(MAIN|CTRL[0-9]?|LOAD[123]|PILOT)', c.get('life_id', ''))": "re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_SDK_DEMO_[0-9A-F]{16}', c.get('life_id', ''))",
        "role_limits = {'main': 24, 'control': 6, 'load': 3, 'pilot': 3}": "role_limits = {'pilot': 3}",
    }
    for before, after in replacements.items(): actor = replace_once(actor, before, after)
    actor = replace_once(actor, "CODE_SCOPE_KEY = 'DEE.Cognitive.Roblox.SDK.CODE_SCOPE.0.1.0'", "CODE_SCOPE_KEY = 'DEE.Cognitive.Roblox.SDK.CODE_SCOPE.0.1.0'\nLEASE_KEY = 'DEE.Cognitive.Roblox.SDK.LEASE.0.1.0'")
    actor = replace_once(actor, "c['native_cutoff_utc_epoch'] == 1794913620", "c['native_cutoff_utc_epoch'] == c['operational_lease']['hardFinishUtcEpoch']")
    actor = replace_once(actor, "c.get('last_new_cycle_utc_epoch') == 1794909600", "c.get('last_new_cycle_utc_epoch') == c['operational_lease']['lastNewUtcEpoch']")
    actor = replace_once(actor, "    return c\n\n\ndef identity", "    lease = c['operational_lease']\n    need(lease.get('schema') == 'DEE.Roblox.SDK.operational_lease.0.1.0' and lease['lifeId'] == c['life_id'] and lease['startUtcEpoch'] < lease['lastNewUtcEpoch'] < lease['hardFinishUtcEpoch'] and lease['hardFinishUtcEpoch'] - lease['startUtcEpoch'] <= 21600 and 0 < lease['cumulativeCycleCap'] <= 3, 'Finite SDK operational session')\n    return c\n\n\ndef identity")
    actor = replace_once(actor, "'scope_sha256': hashlib.sha256(SCOPE.read_bytes()).hexdigest(),", "'scope_sha256': digest({k:v for k,v in c.items() if k not in ('native_cutoff_utc_epoch','last_new_cycle_utc_epoch','operational_lease')}),")
    actor = replace_once(actor, "    validate_literal(row)\n    identity(a)", "    validate_literal(row)\n    identity(a)\n    need(dict(a.world.runtime.snapshot_metadata_entries).get(LEASE_KEY) == canonical(scope()['operational_lease']), 'Explicit closed operational lease witness required')")
    actor = replace_once(actor, "m['cycles'] < scope()['max_cycles']", "m['cycles'] < min(scope()['max_cycles'], scope()['operational_lease']['cumulativeCycleCap'])")
    bundle = deps / 'sdk_bundle'; bundle.mkdir(exist_ok=True)
    write_source(bundle / 'rbx07_native_v3.py', actor)
    for name in ('rbx07_identity_v3.py', 'rbx07_funciones_v3.py'):
        text = (r07 / 'native/bundle' / name).read_text('utf-8-sig')
        if name == 'rbx07_identity_v3.py': text = text.replace('DEE.RBX01.readonly_identity_bootstrap.INTEGRAL.V3.R01', 'DEE.Roblox.SDK.identity.0.1.0')
        write_source(bundle / name, text)
    adapter = (r07 / 'native/adapter_v3.py').read_text('utf-8-sig')
    adapter = adapter.replace('DEE.RBX01.async_native.INTEGRAL.V3.R01', 'DEE.Roblox.SDK.native.0.1.0').replace('RBX07_NATIVE_INTEGRAL_V3/events.jsonl', 'DEE_SDK_NATIVE_0_1_0/events.jsonl')
    write_source(RUNTIME / 'backend/native_adapter.py', adapter)
    # Preserve the actual original owner, and generate only its SDK path/lease
    # wrapper. Material paths, agenda, reader and motor are unchanged.
    owner = (r07 / 'native/owner_support_v3_R07.py').read_text('utf-8-sig')
    owner = owner.replace('AGGREGATE = 160000', 'AGGREGATE = 40000')
    owner = owner.replace("REVISION_ROOT / 'native/ledger_v3_R07.py'", "REVISION_ROOT / 'backend/ledger_sdk.py'")
    owner = replace_once(owner, '    if destination != REVISION_ROOT / "native/PILOT":raise ValueError("PILOT_ONLY_PROSPECTIVE_OWNER")',
        "    if destination.parent != REVISION_ROOT / 'estado_demo/instancias' or not __import__('re').fullmatch(r'SDK_DEMO_[0-9A-F]{16}', destination.name): raise ValueError('SDK_PRIVATE_INSTANCE_ONLY')")
    owner = replace_once(owner, "    if not (destination/'LEASE_APPLIED_PILOT_R07.json').is_file():raise RuntimeError('EXPLICIT_CLOSED_LEASE_MIGRATION_REQUIRED')", "    if not (destination/'SDK_READY.json').is_file(): raise RuntimeError('SDK_IMPORT0_AND_SCOPE_REQUIRED')")
    owner = replace_once(owner, 'cutoff_epoch != 1794913620', "cutoff_epoch != json.loads((destination / 'INSTANCE.json').read_text('utf8'))['operationalLease']['hardFinishUtcEpoch']")
    owner = replace_once(owner, 'time.time() >= 1794909600', "time.time() >= scope['last_new_cycle_utc_epoch']")
    anchor = "    context = json.loads((destination / 'CONTEXTO_EJECUCION.json').read_text('utf8'))\n    imported ="
    if owner.count(anchor) != 2: raise ValueError('Both preserved owner context readers required')
    owner = owner.replace(anchor, "    context = json.loads((destination / 'CONTEXTO_EJECUCION.json').read_text('utf8'))\n    context['system'] = str(destination / 'sistema')\n    context['prefix'] = str(REVISION_ROOT / context['prefix'])\n    imported =")
    write_source(RUNTIME / 'backend/sdk_owner.py', owner)
    if not (RUNTIME / 'backend/ledger_sdk.py').is_file(): raise ValueError('New explicit SDK ledger code required; never reuse old R07 accounting')
    manifest = {'schema': SCHEMA, 'sourcePairSha256': 'c4638b02ea660f2e32d13c015637e817a28d471e96c3bee0284918f1d55cf2c2',
                'nativeSources': {p.name: sha(p) for p in sorted(bundle.glob('*.py'))},
                'preservedMechanism': 'Only new epoch identity, finite lease and private paths; inherited sensor, reader, decoder and physical calendar unchanged.',
                'window': window, 'newNativeTicks': 0, 'payloadCopyRequested': copy_payload}
    if (deps / 'SDK_SOURCES.json').exists():
        if read(deps / 'SDK_SOURCES.json') != manifest: raise ValueError('Existing source manifest differs')
    else: atomic(deps / 'SDK_SOURCES.json', manifest, new=True)
    if copy_payload:
        template = deps / 'sistema_base'
        tree(r06 / 'evidencia/PAR28/native_root/sistema', template, exclude=('estado', 'servicio_eventos_v3.py', 'cola_local.py', 'mundo_genesis_apd05.py'))
        # Same functioning dispatcher with versioned SDK apparatus; no R07 state.
        for p in bundle.glob('*.py'):
            target = template / 'capacidades' / p.name
            if target.exists():
                if sha(target) == sha(p): continue
                raise RuntimeError('Unexpected preexisting SDK capability')
            checked_copy(p, target)
        service = (r07 / 'native/PILOT/sistema/app/servicio_eventos_v3.py').read_text('utf-8-sig')
        service = replace_once(service, "scope.get('system') != str(system)", "scope.get('system') != '.'")
        write_source(template / 'app/servicio_eventos_v3.py', service)
        for name in ('cola_local.py', 'mundo_genesis_apd05.py'):
            checked_copy(r07 / 'native/PILOT/sistema/app' / name, template / 'app' / name)
        tree(r07 / 'persistencia/PREFIJO_PAR28_COMPLETO', RUNTIME / 'estado_demo/prefijos/PAR28_COMPLETO')
        for name in ('importar_diagnostico.py', 'observador_pasivo.py'):
            checked_copy(product / 'reproducibilidad' / name, deps / 'herramientas_import0' / name)
        checked_copy(product / 'reproducibilidad/propietario_diagnostico.py', deps / 'producto/reproducibilidad/propietario_diagnostico.py')
        tree(product / 'motor/python313', deps / 'producto/motor/python313', include_bytecode=True,
             exclude_suffixes=('.cpp','.cc','.cxx','.h','.hpp','.c'))
        # Only one official binary motor tree is shared by all SDK instances.
        # Its remaining bootstrap import paths are enumerated by native_tools;
        # copying a kernel source tree is deliberately not a fallback.
        for src, dst in ((r06 / 'evidencia/NATIVE_CONTINUACION_C16_R01/WORLD_CHECKPOINT.json', 'WORLD_PADRE_PAR28.json'),
                         (r07 / 'native/PILOT/VIDA_PADRE_PAR28.json', 'VIDA_PADRE_PAR28.json')):
            checked_copy(src, RUNTIME / 'estado_demo/prefijos' / dst)
        members = []; empty_directories = []
        for current, dirs, files in os.walk(template):
            dirs.sort()
            if not dirs and not files: empty_directories.append(Path(current).relative_to(template).as_posix())
            for name in sorted(files):
                p = Path(current) / name
                members.append({'file': p.relative_to(template).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)})
        anchors = {key: {'file': 'estado_demo/prefijos/' + name, 'sha256': sha(RUNTIME / 'estado_demo/prefijos' / name)}
                   for key,name in (('sourceWorld', 'WORLD_PADRE_PAR28.json'), ('sourceRecord', 'VIDA_PADRE_PAR28.json'))}
        tools = [{'file': 'dependencias/herramientas_import0/' + n, 'sha256': sha(deps / 'herramientas_import0' / n)}
                 for n in ('importar_diagnostico.py', 'observador_pasivo.py')]
        template_manifest = {'schema': SCHEMA, 'members': members,
               'empty_directories': empty_directories, 'tool_sources': tools, 'import_paths': ['dependencias/producto/reproducibilidad'], 'anchors': anchors}
        if (deps / 'PLANTILLA_SISTEMA.json').exists():
            if read(deps / 'PLANTILLA_SISTEMA.json') != template_manifest: raise ValueError('Existing private template differs')
        else: atomic(deps / 'PLANTILLA_SISTEMA.json', template_manifest, new=True)
        ready = {'schema': SCHEMA, 'templateSha256': sha(deps / 'PLANTILLA_SISTEMA.json'),
                 'prefixManifestSha256': sha(RUNTIME / 'estado_demo/prefijos/PAR28_COMPLETO/EXPORTACION_SERVICIO.json'),
                 'pythonSha256': sha(deps / 'producto/motor/python313/python.exe'), 'newNativeTicks': 0}
        atomic(deps / 'PRIVATE_PAYLOAD_READY.json', ready)
    return manifest

def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--source-product', required=True)
    p.add_argument('--copy-private-payload', action='store_true'); p.add_argument('--root-fs-build', action='store_true')
    a = p.parse_args()
    if not a.root_fs_build: p.error('Explicit --root-fs-build; no Native operation')
    print(canonical(build(a.source_product, copy_payload=a.copy_private_payload)))

if __name__ == '__main__': main()
