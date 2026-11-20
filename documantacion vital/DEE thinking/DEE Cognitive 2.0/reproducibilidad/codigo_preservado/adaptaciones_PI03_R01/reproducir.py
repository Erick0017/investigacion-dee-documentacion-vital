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
def recipes():
    return {p.stem: read(p) for p in sorted((HERE / 'recetas').glob('*.json'))}
def recipe(name):
    values = recipes()
    if name not in values: raise ValueError('Receta desconocida: ' + name)
    return values[name]

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

def verification(name):
    c = config(); r = recipe(name); result = {'recipe': name, 'checked_utc': now(), 'checks': [], 'new_native_ticks': 0, 'DEE_imports': 0}
    def check(kind, function):
        try: result['checks'].append({'kind': kind, 'available_and_identity_checked': True, 'result': function()})
        except Exception as e: result['checks'].append({'kind': kind, 'available_and_identity_checked': False, 'error': str(e)})
    check('code_capsule', lambda: capsule_check(c['code_capsule']))
    check('full_prefix', lambda: verify_pair(c['pairs'][r['prefix']]))
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
    result['requirements_available'] = all(v['available_and_identity_checked'] for v in result['checks'])
    result['historical_verification'] = r.get('verification', {})
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
    if not re.fullmatch(r'PI03_REPRO_[A-Za-z0-9_]{1,48}', args.vida):
        raise ValueError('Vida diagnóstica obligatoria PI03_REPRO_<ID>; nunca MAIN/ACTIVO')
    r = recipe(args.receta); c = config()
    if args.variante not in r['variants']: raise ValueError('Variante no fijada en la receta')
    dest = fresh_destination(args.destino)
    # Same identity may not silently become another technical repetition.
    registry = HERE / 'EJECUCIONES'
    if (registry / (args.vida + '.json')).exists(): raise ValueError('ID ya utilizado, incluso si el destino se movió')
    result = verification(args.receta)
    if not result['requirements_available']: emit(result); return 2
    lock = HERE / 'EJECUCION_MATERIAL.lock'
    with lock.open('x', encoding='utf-8') as f:
        json.dump({'pid': os.getpid(), 'life': args.vida, 'destination': str(dest), 'created_utc': now(), 'no_automatic_stale_lock_removal': True}, f)
    complete = False
    try:
        dest.mkdir(parents=False, exist_ok=True); registry.mkdir(exist_ok=True)
        capsule = resource(c['code_capsule']); m = read(capsule / c['code_capsule'].get('manifest', 'SISTEMA_CODIGO.json'))
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
                   'source_code_manifest_sha256': sha(capsule / c['code_capsule'].get('manifest', 'SISTEMA_CODIGO.json')),
                   'never_select_or_promote': True, 'evaluation_expected_values_never_passed_to_world': True}
        save(dest / 'CONTEXTO_EJECUCION.json', context)
        save(registry / (args.vida + '.json'), {k: context[k] for k in ('life', 'recipe', 'variant', 'destination', 'created_utc')})
        for script in ('importar_diagnostico.py', 'ejecutar_diagnostico.py'):
            command = [str(py), '-I', '-B', '-X', 'utf8', str(HERE / script), '--contexto', str(dest / 'CONTEXTO_EJECUCION.json')]
            with (dest / (script + '.stdout.txt')).open('x', encoding='utf-8') as out, (dest / (script + '.stderr.txt')).open('x', encoding='utf-8') as err:
                process = subprocess.run(command, cwd=dest, stdout=out, stderr=err, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            if process.returncode: raise RuntimeError(script + ' falló; no se reintenta. Conservar destino y bloqueo para conciliación.')
        complete = True
        emit({'destination': str(dest), 'life': args.vida, 'completed_native_reproduction': True,
              'summary': str(dest / 'RESULTADO_REPRODUCCION.json'), 'principal_modified': False})
        return 0
    finally:
        if complete: lock.unlink()
        # A failed/uncertain owner can remain alive. Never erase its guard or retry.

def recalculate(args):
    c = config(); a = c['analysis']; root = resource(a)
    manifest = inside(root, a.get('manifest', 'ANALISIS_MANIFIESTO.json'))
    m = read(manifest); rows = m.get('files', m.get('members'))
    if not isinstance(rows, list): raise ValueError('Manifiesto de análisis no reconocido')
    checked_files(root, rows)
    script = inside(root, a.get('recalculation_script', 'RECALCULO/RECALCULO_TODO.py'))
    dest = fresh_destination(args.destino)
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(script), '--root', str(root), '--out-dir', str(dest)]
    if args.grupos: command += ['--groups', *args.grupos]
    return subprocess.run(command, cwd=root, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)).returncode

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='modo', required=True)
    sub.add_parser('listar')
    verify = sub.add_parser('verificar'); verify.add_argument('receta', nargs='?')
    calc = sub.add_parser('recalcular'); calc.add_argument('--destino', required=True)
    calc.add_argument('--grupos', nargs='+', choices=('A', 'B', 'C', 'D', 'OH', 'PRIMER_AVISO', 'E'))
    run = sub.add_parser('reproducir'); run.add_argument('receta'); run.add_argument('--variante', required=True)
    run.add_argument('--vida', required=True); run.add_argument('--destino', required=True)
    args = parser.parse_args()
    if args.modo == 'listar':
        emit({'mode': 'read_only_catalogue', 'DEE_imports': 0, 'new_native_ticks': 0,
              'recipes': [{key: value.get(key) for key in ('id', 'title', 'prefix', 'modalities', 'assistance', 'limitations', 'verification')} for value in recipes().values()]}); return 0
    if args.modo == 'verificar':
        names = [args.receta] if args.receta else list(recipes())
        values = [verification(name) for name in names]; emit(values)
        return 0 if all(v['requirements_available'] for v in values) else 2
    if args.modo == 'recalcular': return recalculate(args)
    return run_material(args)

if __name__ == '__main__':
    try: raise SystemExit(main())
    except Exception as error:
        emit({'error': type(error).__name__, 'detail': str(error), 'automatic_retry': False,
              'scope': 'Se preservan el destino y cualquier futuro interrumpido. No se selecciona ni promueve ningún control.'})
        raise SystemExit(2)
