"""Reproducibilidad Cognitive: lectura por defecto; actuación sólo en destino diagnóstico.

listar/verificar/recalcular no importan DEE. reproducir usa un par completo
preservado y una cápsula compartida; nunca selecciona ni promueve una vida.
"""
from pathlib import Path, PurePosixPath
import argparse, datetime, hashlib, json, os, re, shutil, sqlite3, subprocess, sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PRODUCT = HERE.parent
WHEEL = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHEEL_SHA = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA = '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()
def emit(value): print(json.dumps(value, ensure_ascii=False, indent=2), flush=True)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p, value):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')
        f.flush(); os.fsync(f.fileno())
def unlinked(path, boundary):
    """Reject symlink/junction components; do not follow links to another tree."""
    path = Path(path).absolute(); boundary = Path(boundary).absolute()
    for item in (path, *path.parents):
        if item.exists() and (item.is_symlink() or getattr(item.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('Enlace/reparse point no admitido: ' + str(item))
        if item == boundary: break
    return path.resolve(strict=True)
def inside(root, name):
    rel = PurePosixPath(name)
    if not isinstance(name, str) or '\\' in name or ':' in name or rel.is_absolute() or not rel.parts or any(x in ('..', '.') for x in rel.parts):
        raise ValueError('Ruta relativa insegura: ' + str(name))
    raw = root.joinpath(*rel.parts)
    p = unlinked(raw, root)
    if not p.is_relative_to(root.resolve()): raise ValueError('Ruta fuera del almacén')
    return p
def resource(entry): return inside(PRODUCT, entry['product_relative'])
def config(): return read(HERE / 'RECURSOS.json')
def selected_code_capsule(c, r):
    if r.get('required_capsule') == 'historical_apd03':
        return {'product_relative': c['historical_apd03']['code_capsule'],
                'manifest': 'APD03_SOURCES_MANIFEST.json',
                'manifest_sha256': c['historical_apd03']['code_manifest_sha256']}
    if r.get('code_capsule_key'):
        return c['code_capsules'][r['code_capsule_key']]
    return c['code_capsule']
def recipes():
    return {p.stem: read(p) for p in sorted((HERE / 'recetas').glob('*.json'))}
def recipe(name):
    values = recipes()
    if name not in values: raise ValueError('Receta desconocida: ' + name)
    return values[name]
def recorded_verifications(name):
    folder = HERE / 'verificaciones' / name
    return [read(p) for p in sorted(folder.glob('*.json'))] if folder.exists() else []

def dependency_advisories(name):
    """Only explicit static dependency-block records; no actor input or policy."""
    blocked = []
    for record in recorded_verifications(name):
        if record.get('schema') != 'DEE.reproduction.static_dependency_advisory.v1':
            continue
        replacement = record.get('use_replacement_recipe')
        if (record.get('recipe') != name or
                record.get('status') != 'DOCUMENTED_DEPENDENCY_BLOCK_SUPERSEDED' or
                record.get('actual_native_execution_completed') is not False or
                record.get('new_native_ticks') != 0 or
                not isinstance(replacement, str) or
                not re.fullmatch(r'[A-Za-z0-9_]{1,120}', replacement) or
                replacement == name):
            raise ValueError('Invalid explicit static-dependency advisory; fail closed')
        blocked.append(record)
    return blocked


def checked_files(root, rows, exact=False, omit=()):
    seen = set(); total = 0
    for row in rows:
        name = row['file']
        if name in seen: raise ValueError('Miembro repetido: ' + name)
        p = inside(root, name)
        if not p.is_file() or p.stat().st_size != row['bytes'] or sha(p) != row['sha256']:
            raise ValueError('Identidad/tamaño alterado: ' + name)
        seen.add(name); total += row['bytes']
    if exact:
        actual = set()
        for base, directories, files in os.walk(root, followlinks=False):
            for d in directories: unlinked(Path(base) / d, root)
            for f in files:
                p = unlinked(Path(base) / f, root)
                rel = p.relative_to(root).as_posix()
                if rel not in omit: actual.add(rel)
        if actual != seen: raise ValueError('Conjunto incompleto o miembros no indexados')
    return {'files_verified': len(seen), 'bytes_verified': total}

def verify_pair(entry):
    root = resource(entry); index = root / 'EXPORTACION_SERVICIO.json'
    expected = entry.get('manifest_sha256')
    if not expected: raise ValueError('Falta hash fijado del manifiesto; material no asegurado')
    if sha(index) != expected: raise ValueError('Manifiesto de prefijo distinto del fijado')
    m = read(index)
    if m.get('schema') != 'DEE.persistent_service.paired_export.v1' or m.get('queue_journal_required') is not True:
        raise ValueError('Se requiere exportación completa snapshot + transporte')
    if m['life_id'] != entry['life_id'] or m['physical']['tick'] != entry['tick']:
        raise ValueError('Identidad/corte del prefijo no coincide')
    check = checked_files(root, m['members'], exact=True, omit=('EXPORTACION_SERVICIO.json',))
    names = {row['file'] for row in m['members']}
    if not {'VIDA.deetsnap.gz', 'cola.sqlite3'} <= names or sha(root / 'VIDA.deetsnap.gz') != m['snapshot_sha256']:
        raise ValueError('Falta snapshot completo o diario emparejado')
    con = sqlite3.connect((root / 'cola.sqlite3').as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        if con.execute('PRAGMA integrity_check').fetchone()[0] != 'ok': raise ValueError('SQLite no íntegro')
        statuses = {}
        for identifier, payload, recorded, status in con.execute('SELECT id,payload,payload_sha,status FROM requests'):
            encoded = json.dumps(json.loads(payload), ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
            if hashlib.sha256(encoded).hexdigest() != recorded: raise ValueError('Payload de transporte alterado: ' + str(identifier))
            if status not in ('queued', 'processing', 'completed', 'uncertain', 'failed_preserved', 'rejected_invalid'):
                raise ValueError('Estado de transporte desconocido')
            statuses[status] = statuses.get(status, 0) + 1
    finally: con.close()
    return {**check, 'path': str(root), 'manifest_sha256': expected, 'life': m['life_id'], 'physical': m['physical'],
            'transport_status_counts': statuses, 'new_ticks': 0,
            'scope': 'Bytes y diario congelados; un export propio puede conservar su recibo processing. No se purga ni se reenvía.'}

def capsule_check(c):
    root = resource(c); manifest = root / c.get('manifest', 'SISTEMA_CODIGO.json')
    if c.get('manifest_sha256') and sha(manifest) != c['manifest_sha256']: raise ValueError('Cápsula de código cambió')
    m = read(manifest)
    required = {'gestionar.py', 'app/lives.py', 'app/importacion_emparejada.py', 'app/cola_local.py', 'app/process_control.py'}
    if not required <= {r['file'] for r in m['files']}: raise ValueError('Cápsula de código incompleta')
    return {**checked_files(root, m['files']), 'path': str(root), 'manifest_sha256': sha(manifest)}

def recipe_analysis_check(r):
    """Static evidence/script verification only; no Native/actor import."""
    a = r.get('analysis')
    if not isinstance(a, dict) or a.get('interface') != 'DEE.recalculation.root_outdir.v1':
        raise ValueError('La receta no tiene recálculo stdlib incorporado con esta interfaz')
    root = resource(a)
    manifest = inside(root, a.get('manifest', 'MANIFIESTO_ESTABLE.json'))
    if sha(manifest) != a['manifest_sha256']:
        raise ValueError('El manifiesto del recálculo de receta cambió')
    rows = read(manifest).get('files')
    if not isinstance(rows, list):
        raise ValueError('Se requiere lista files del material de recálculo')
    checked = checked_files(root, rows, exact=True, omit=(manifest.relative_to(root).as_posix(),))
    script = inside(root, a['recalculation_script'])
    if script.suffix != '.py':
        raise ValueError('Recálculo Python preservado; no shell/comando arbitrario')
    return {'path': str(root), 'script': str(script), 'manifest_sha256': sha(manifest), **checked}


def verification(name):
    c = config(); r = recipe(name); result = {'recipe': name, 'checked_utc': now(), 'checks': [], 'new_native_ticks': 0, 'DEE_imports': 0}
    def check(kind, function):
        try: result['checks'].append({'kind': kind, 'available_and_identity_checked': True, 'result': function()})
        except Exception as e: result['checks'].append({'kind': kind, 'available_and_identity_checked': False, 'error': str(e)})
    selected_capsule = selected_code_capsule(c, r)
    check('code_capsule', lambda: capsule_check(selected_capsule))
    check('full_prefix', lambda: verify_pair(c['pairs'][r['prefix']]))
    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI10.diagnostic_family.identity_binding.R02':
        def pi10_static_tools():
            names = {'pi10_vinculo_reproduccion_R02.py': r['diagnostic_identity_binding']['helper_sha256'],
                     'pi10_guardia_reproduccion_R02.py': r['material_supervisor']['sha256']}
            for filename, digest in names.items():
                if sha(HERE / filename) != digest:
                    raise ValueError('PI10 reproduction source changed: ' + filename)
            return {'files_sha256': names, 'DEE_imports': 0, 'new_native_ticks': 0}
        check('PI10_static_binding_and_finite_guard', pi10_static_tools)
    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R01':
        def pi11_static_tools():
            names = {'pi11_vinculo_reproduccion_R01.py': r['diagnostic_identity_binding']['helper_sha256'],
                     'pi11_guardia_reproduccion_R01.py': r['material_supervisor']['sha256']}
            for filename, digest in names.items():
                if sha(HERE / filename) != digest:
                    raise ValueError('PI11 reproduction source changed: ' + filename)
            return {'files_sha256': names, 'DEE_imports': 0, 'new_native_ticks': 0}
        check('PI11_static_binding_and_finite_guard', pi11_static_tools)
    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R02':
        def pi11_static_tools():
            names = {'pi11_vinculo_reproduccion_R02.py': r['diagnostic_identity_binding']['helper_sha256'],
                     'pi11_guardia_reproduccion_R02.py': r['material_supervisor']['sha256']}
            for filename, digest in names.items():
                if sha(HERE / filename) != digest:
                    raise ValueError('PI11 reproduction source changed: ' + filename)
            return {'files_sha256': names, 'DEE_imports': 0, 'new_native_ticks': 0}
        check('PI11_R02_static_binding_and_finite_guard', pi11_static_tools)
    if r.get('analysis'):
        check('recipe_documentary_recalculation', lambda: recipe_analysis_check(r))
    def engine():
        py = inside(PRODUCT, 'motor/python313/python.exe')
        wheel = inside(PRODUCT, 'sistema/runtime/' + WHEEL)
        if sha(wheel) != WHEEL_SHA: raise ValueError('WHL oficial distinto')
        candidates = list((PRODUCT / 'motor/python313').rglob('*_native*.pyd'))
        candidates += list((PRODUCT / 'motor/python313').rglob('_native*.pyd'))
        pyds = {str(p.resolve()): p for p in candidates}
        matching = [p for p in pyds.values() if sha(p) == PYD_SHA]
        if not matching: raise ValueError('PYD oficial no localizado o hash distinto')
        return {'python': str(py), 'python_sha256': sha(py), 'wheel_sha256': WHEEL_SHA, 'PYD': str(matching[0]), 'PYD_sha256': PYD_SHA,
                'scope': 'Identidad estática. Este modo no importa el motor ni acredita ejecución.'}
    check('shared_official_engine', engine)
    if r.get('reproduction_enabled') is False:
        result['checks'].append({'kind': 'executable_adaptation', 'available_and_identity_checked': False,
                                  'error': 'Material preservado; receta no habilitada para ejecución.', 'blockers': r.get('blockers', [])})
    advisory_blocks = dependency_advisories(name)
    result['material_execution_blocked_by_advisory'] = bool(advisory_blocks)
    if advisory_blocks:
        result['checks'].append({'kind': 'explicit_static_dependency_advisory',
                                'available_and_identity_checked': False,
                                'error': 'Historical recipe preserved but material execution blocked by a known dependency advisory.',
                                'advisories': advisory_blocks})
    result['requirements_available'] = all(v['available_and_identity_checked'] for v in result['checks'])
    result['historical_verification'] = r.get('verification', {})
    result['actual_registered_verifications'] = recorded_verifications(name)
    return result

def fresh_destination(value):
    raw = Path(value).absolute(); parent = raw.parent.resolve(strict=True)
    unlinked(parent, parent.anchor)
    dest = parent / raw.name
    if dest == PRODUCT or (dest.is_relative_to(PRODUCT) and not dest.is_relative_to(HERE / 'diagnosticos')):
        raise ValueError('Destino sólo fuera del producto o en reproducibilidad/diagnosticos')
    if PRODUCT.is_relative_to(dest): raise ValueError('El destino contiene el producto original')
    if dest.exists():
        unlinked(dest, parent)
        if not dest.is_dir() or any(dest.iterdir()): raise ValueError('Destino ya usado/no vacío; se conserva sin cambios')
    return dest

def run_material(args):
    if not re.fullmatch(r'ECI02_PI03_REPRO_[A-Za-z0-9_]{1,48}', args.vida):
        raise ValueError('Vida diagnóstica obligatoria ECI02_PI03_REPRO_<ID>; nunca MAIN/ACTIVO')
    r = recipe(args.receta); c = config()
    if dependency_advisories(args.receta):
        emit(verification(args.receta)); return 2  # Before destination creation/import/owner.
    if r.get('requires_explicit_material') and not getattr(args, 'material', False):
        raise ValueError('Esta receta exige --material para ejecutar DEE en la copia explícita')
    if args.variante not in r['variants']: raise ValueError('Variante no fijada en la receta')
    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI10.diagnostic_family.identity_binding.R02' and not globals().get('_PI10_FAMILY_GUARD_ACTIVE', False):
        import importlib.util
        helper = HERE / 'pi10_guardia_reproduccion_R02.py'
        if sha(helper) != r['material_supervisor']['sha256']:
            raise ValueError('PI10 finite material guard changed; no destination/import/owner')
        spec = importlib.util.spec_from_file_location('PI10_stable_RP_finite_material_guard', helper)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module.run_supervised(sys.modules[__name__], args)
    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R01' and not globals().get('_PI11_FAMILY_GUARD_ACTIVE', False):
        import importlib.util
        helper = HERE / 'pi11_guardia_reproduccion_R01.py'
        if sha(helper) != r['material_supervisor']['sha256']:
            raise ValueError('PI11 finite material guard changed; no destination/import/owner')
        spec = importlib.util.spec_from_file_location('PI11_stable_RP_finite_material_guard', helper)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module.run_supervised(sys.modules[__name__], args)
    if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R02' and not globals().get('_PI11_FAMILY_GUARD_ACTIVE', False):
        import importlib.util
        helper = HERE / 'pi11_guardia_reproduccion_R02.py'
        if sha(helper) != r['material_supervisor']['sha256']:
            raise ValueError('PI11 finite material guard changed; no destination/import/owner')
        spec = importlib.util.spec_from_file_location('PI11_stable_RP_finite_material_guard', helper)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module.run_supervised(sys.modules[__name__], args)
    dest = fresh_destination(args.destino)
    # Same identity may not silently become another technical repetition.
    registry = HERE / 'EJECUCIONES'
    if (registry / (args.vida + '.json')).exists(): raise ValueError('ID ya utilizado, incluso si el destino se movió')
    for folder in ('vidas', 'servicios_locales', 'servicios_persistentes'):
        if (PRODUCT / 'sistema/estado' / folder / args.vida).exists():
            raise ValueError('Identidad ya presente en el almacén operativo; no se reutiliza')
    result = verification(args.receta)
    if not result['requirements_available']: emit(result); return 2
    lock = HERE / 'EJECUCION_MATERIAL.lock'
    with lock.open('x', encoding='utf-8') as f:
        json.dump({'pid': os.getpid(), 'life': args.vida, 'destination': str(dest), 'created_utc': now(), 'no_automatic_stale_lock_removal': True}, f)
    complete = False
    try:
        dest.mkdir(parents=False, exist_ok=True); registry.mkdir(exist_ok=True)
        selected_capsule = selected_code_capsule(c, r)
        capsule = resource(selected_capsule); m = read(capsule / selected_capsule.get('manifest', 'SISTEMA_CODIGO.json'))
        system = dest / 'sistema'; system.mkdir()
        for item in m['files']:
            relative = item['file']
            if relative.startswith(('estado/', 'runtime/')) or relative.endswith('.sqlite3'):
                raise ValueError('La cápsula no puede insertar estados/colas en otro individuo')
            source = inside(capsule, relative); target = system / Path(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.open('rb') as src, target.open('xb') as dst: shutil.copyfileobj(src, dst)
            if sha(target) != item['sha256']: raise ValueError('Copia de código no íntegra')
        (system / 'estado/checkpoints').mkdir(parents=True)
        (system / 'runtime').mkdir()
        # Share exact official wheel once. A hardlink is not an installed second engine.
        os.link(PRODUCT / 'sistema/runtime' / WHEEL, system / 'runtime' / WHEEL)
        pair = resource(c['pairs'][r['prefix']]); py = PRODUCT / 'motor/python313/python.exe'
        context = {'schema': 'DEE.reproduction.explicit_diagnostic.v1', 'life': args.vida, 'recipe': args.receta,
                   'variant': args.variante, 'prefix': str(pair), 'prefix_manifest_sha256': sha(pair / 'EXPORTACION_SERVICIO.json'),
                   'system': str(system), 'python': str(py), 'product': str(PRODUCT), 'destination': str(dest), 'created_utc': now(),
                   'recipe_sha256': sha(HERE / 'recetas' / (args.receta + '.json')), 'fixed_recipe': r,
                   'source_code_manifest_sha256': sha(capsule / selected_capsule.get('manifest', 'SISTEMA_CODIGO.json')),
                   'source_code_capsule_key': r.get('code_capsule_key', 'PI02_DEFAULT'),
                   'tool_sources': [{'file': name, 'sha256': sha(HERE / name)} for name in
                       ('reproducir.py', 'importar_diagnostico.py', 'ejecutar_diagnostico.py',
                        'propietario_diagnostico.py', 'observador_pasivo.py')],
                   'never_select_or_promote': True, 'evaluation_expected_values_never_passed_to_world': True}
        save(dest / 'CONTEXTO_EJECUCION.json', context)
        if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI10.diagnostic_family.identity_binding.R02':
            import importlib.util
            helper = HERE / 'pi10_vinculo_reproduccion_R02.py'
            if sha(helper) != r['diagnostic_identity_binding']['helper_sha256']:
                raise ValueError('PI10 family binding source changed; no Native import')
            spec = importlib.util.spec_from_file_location('PI10_stable_RP_family_binding', helper)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            module.bind_context(dest / 'CONTEXTO_EJECUCION.json')
        if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R01':
            import importlib.util
            helper = HERE / 'pi11_vinculo_reproduccion_R01.py'
            if sha(helper) != r['diagnostic_identity_binding']['helper_sha256']:
                raise ValueError('PI11 family binding source changed; no Native import')
            spec = importlib.util.spec_from_file_location('PI11_stable_RP_family_binding', helper)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            module.bind_context(dest / 'CONTEXTO_EJECUCION.json')
        if r.get('diagnostic_identity_binding', {}).get('schema') == 'DEE.PI11.diagnostic_family.identity_binding.R02':
            import importlib.util
            helper = HERE / 'pi11_vinculo_reproduccion_R02.py'
            if sha(helper) != r['diagnostic_identity_binding']['helper_sha256']:
                raise ValueError('PI11 family binding source changed; no Native import')
            spec = importlib.util.spec_from_file_location('PI11_stable_RP_family_binding', helper)
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            module.bind_context(dest / 'CONTEXTO_EJECUCION.json')
        save(registry / (args.vida + '.json'), {k: context[k] for k in ('life', 'recipe', 'variant', 'destination', 'created_utc')})
        for script in ('importar_diagnostico.py', 'ejecutar_diagnostico.py'):
            command = [str(py), '-I', '-B', '-X', 'utf8', str(HERE / script), '--contexto', str(dest / 'CONTEXTO_EJECUCION.json')]
            with (dest / (script + '.stdout.txt')).open('x', encoding='utf-8') as out, (dest / (script + '.stderr.txt')).open('x', encoding='utf-8') as err:
                process = subprocess.run(command, cwd=dest, stdout=out, stderr=err, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            if process.returncode: raise RuntimeError(script + ' falló; no se reintenta. Conservar destino y bloqueo para conciliación.')
        final = read(dest / 'RESULTADO_REPRODUCCION.json')
        if final.get('owner_closed_coherently') is not True:
            raise RuntimeError('No coherent owner closure in final proof; preserve execution guard')
        complete = True
        emit({'destination': str(dest), 'life': args.vida, 'material_execution_closed': final.get('owner_closed_coherently') is True,
              'completed_native_reproduction': final.get('status') == 'COMPLETED', 'local_criteria_met': final.get('criteria_met'),
              'summary': str(dest / 'RESULTADO_REPRODUCCION.json'), 'principal_modified': False})
        return 0
    finally:
        if complete: lock.unlink()
        # A failed/uncertain owner can remain alive. Never erase its guard or retry.

def recalculate(args):
    if getattr(args, 'receta', None):
        if args.grupos:
            raise ValueError('Los grupos históricos PI02 no se aplican a otra receta')
        r = recipe(args.receta)
        verified = recipe_analysis_check(r)
        root = Path(verified['path'])
        dest = fresh_destination(args.destino)
        if dest.exists():
            raise ValueError('El recálculo de receta exige un directorio NUEVO')
        command = [sys.executable, '-I', '-B', '-X', 'utf8', verified['script'], '--root', str(root), '--out-dir', str(dest)]
        process = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8',
                                 errors='strict', creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if process.stdout:
            sys.stdout.write(process.stdout); sys.stdout.flush()
        if process.stderr:
            sys.stderr.write(process.stderr); sys.stderr.flush()
        return process.returncode
    c = config(); a = c['analysis']; root = resource(a)
    manifest = inside(root, a.get('manifest', 'ANALISIS_MANIFIESTO.json'))
    if a.get('manifest_sha256') and sha(manifest) != a['manifest_sha256']:
        raise ValueError('Manifiesto del análisis preservado cambió')
    m = read(manifest); rows = m.get('files', m.get('members'))
    if not isinstance(rows, list): raise ValueError('Manifiesto de análisis no reconocido')
    checked_files(root, rows)
    script = inside(root, a.get('recalculation_script', 'RECALCULO/RECALCULO_TODO.py'))
    dest = fresh_destination(args.destino)
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(script), '--root', str(root), '--out-dir', str(dest)]
    if args.grupos: command += ['--groups', *args.grupos]
    return subprocess.run(command, cwd=root, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)).returncode


def external_f1_info():
    entry = config().get('instrument_deltas', {}).get('PI04_F1')
    if not entry: return []
    return [{'id': 'PI04_F1_OBSERVADOR_COLA_AUDITOR', 'kind': 'instrumento_externo',
             'modality': 'A_recalculo_registros', 'entrypoint': 'recalcular-f1 --destino <DIRECTORIO_NUEVO>',
             'product_relative': entry['product_relative'], 'manifest_sha256': entry['manifest_sha256'],
             'new_native_ticks': 0, 'DEE_imports': 0, 'acquisition_attributed_to_MAIN': False,
             'scope': entry['scope'], 'operation_coverage': entry.get('operation_coverage', {})}]

def recalculate_f1(args):
    dest = fresh_destination(args.destino)
    if dest.exists(): raise ValueError('F1 exige un destino NUEVO, incluso si el directorio existente está vacío')
    c = config(); entry = c.get('instrument_deltas', {}).get('PI04_F1')
    if not entry: raise ValueError('Herramienta externa F1 no incorporada')
    root = resource(entry); manifest = inside(root, 'MANIFIESTO_SHA256.json')
    if sha(manifest) != entry['manifest_sha256']: raise ValueError('Manifiesto F1 distinto del fijado')
    expected_names = {'DATOS_F1.json', 'RECALCULAR_F1.py', 'LEER_PRIMERO.txt', 'RESULTADO_CONTRASTADO.json'}
    members = read(manifest)['members']
    if set(members) != expected_names: raise ValueError('Miembros F1 no reconocidos')
    for name, witness in members.items():
        path = inside(root, name)
        if path.stat().st_size != witness['bytes'] or sha(path) != witness['sha256']:
            raise ValueError('Identidad de F1 alterada: ' + name)
    dest.mkdir(parents=False, exist_ok=False)
    save(dest / 'CONTEXTO_HERRAMIENTA_F1.json', {
        'kind': 'instrumento_externo', 'modality': 'A_recalculo_registros', 'created_utc': now(),
        'source': str(root), 'manifest_sha256': entry['manifest_sha256'],
        'RP_code_sha256': sha(HERE / 'reproducir.py'), 'no_MAIN_capacity_or_acquisition': True,
        'scope': 'Exact frozen physical features only; no Native owner, world import or new ticks.'})
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(inside(root, 'RECALCULAR_F1.py'))]
    process = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8',
                             timeout=120, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if process.returncode:
        save(dest / 'FALLO_PRESERVADO.json', {'returncode': process.returncode, 'stdout': process.stdout,
             'stderr': process.stderr, 'automatic_retry': False, 'new_native_ticks': 0})
        raise RuntimeError('F1 falló; destino preservado sin reintento')
    result = json.loads(process.stdout)
    if result != read(root / 'RESULTADO_CONTRASTADO.json'):
        raise ValueError('F1 difiere del resultado contrastado; preservar destino')
    if result.get('new_Native_ticks') != 0 or result.get('DEE_imports') != 0:
        raise ValueError('Modalidad F1 no es recálculo puro')
    save(dest / 'RESULTADO_F1.json', result)
    proof = {'kind': 'instrumento_externo', 'mode': 'recalcular-f1', 'result': str(dest / 'RESULTADO_F1.json'),
             'result_sha256': sha(dest / 'RESULTADO_F1.json'), 'checks': result['checks'],
             'result_equal_preserved_reference': True, 'stderr_bytes': len(process.stderr.encode('utf-8')),
             'new_native_ticks': 0, 'DEE_imports': 0, 'MAIN_modified': False,
             'not_Native_reproduction': True, 'not_a_MAIN_capacity': True}
    save(dest / 'VERIFICACION_HERRAMIENTA_F1.json', proof)
    emit(proof)
    return 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='modo', required=True)
    sub.add_parser('listar')
    f1 = sub.add_parser('recalcular-f1'); f1.add_argument('--destino', required=True)
    verify = sub.add_parser('verificar'); verify.add_argument('receta', nargs='?')
    calc = sub.add_parser('recalcular'); calc.add_argument('--destino', required=True)
    calc.add_argument('--receta', help='Recálculo documental de una receta incorporada, sin Native')
    calc.add_argument('--grupos', nargs='+', choices=('A', 'B', 'C', 'D', 'OH', 'PRIMER_AVISO', 'E'))
    run = sub.add_parser('reproducir'); run.add_argument('receta'); run.add_argument('--variante', required=True)
    run.add_argument('--vida', required=True); run.add_argument('--destino', required=True)
    run.add_argument('--material', action='store_true', help='Autoriza la ejecución material de una receta que lo exige; listar/verificar/recalcular no actúan')
    args = parser.parse_args()
    if args.modo == 'listar':
        emit({'mode': 'read_only_catalogue', 'DEE_imports': 0, 'new_native_ticks': 0,
              'external_tools': external_f1_info(),
              'recipes': [{**{key: value.get(key) for key in ('id', 'title', 'prefix', 'modalities', 'assistance', 'limitations', 'verification', 'usage')},
                           'actual_registered_verifications': recorded_verifications(value['id']), 'material_execution_blocked_by_advisory': bool(dependency_advisories(value['id']))} for value in recipes().values()]}); return 0
    if args.modo == 'verificar':
        names = [args.receta] if args.receta else list(recipes())
        values = [verification(name) for name in names]; emit(values)
        return 0 if all(v['requirements_available'] for v in values) else 2
    if args.modo == 'recalcular': return recalculate(args)
    if args.modo == 'recalcular-f1': return recalculate_f1(args)
    return run_material(args)

if __name__ == '__main__':
    try: raise SystemExit(main())
    except Exception as error:
        emit({'error': type(error).__name__, 'detail': str(error), 'automatic_retry': False,
              'scope': 'Se preservan el destino y cualquier futuro interrumpido. No se selecciona ni promueve ningún control.'})
        raise SystemExit(2)
