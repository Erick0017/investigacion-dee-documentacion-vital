"""Copia incremental de cortes cerrados. Nunca ejecuta experimentos ni toca el origen."""
from pathlib import Path, PurePosixPath
import argparse, base64, fnmatch, gzip, hashlib, importlib.util, io, json, os, re, shutil, sqlite3, sys, tempfile, time, zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
WHEEL_NAME = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHEEL_SHA = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
OWNER = ROOT / 'actualizaciones/ARCHIVOS_GESTIONADOS.json'
EXCLUDED_PARTS = {'__pycache__', '.git', '.venv', 'node_modules'}
BLOCKED_NAMES = {'.env', '.npmrc', '.pypirc', '.netrc', 'credentials.json', 'credentials', 'id_rsa', 'id_ed25519'}
PROTECTED_PREFIXES = ('trabajo_personal/', 'entregas/', 'actualizaciones/respaldos/', 'actualizaciones/conflictos/', 'actualizaciones/temporales/', 'motor/python313/site-packages/')


def now(): return datetime.now(timezone.utc).isoformat()


def sha_bytes(value): return hashlib.sha256(value).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def read(path): return json.loads(Path(path).read_text(encoding='utf8'))


def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def safe_name(name):
    p = PurePosixPath(name)
    if not name or not p.parts or p.is_absolute() or '..' in p.parts or ':' in name or '\\' in name:
        raise ValueError('Ruta no relativa/segura: ' + name)
    reserved = {'CON','PRN','AUX','NUL',*(f'COM{x}' for x in range(1,10)),*(f'LPT{x}' for x in range(1,10))}
    if any(part.endswith((' ','.')) or part.split('.')[0].upper() in reserved or any(ord(c)<32 for c in part) for part in p.parts):
        raise ValueError('Nombre no portable/seguro en Windows: ' + name)
    if any(part in EXCLUDED_PARTS for part in p.parts) or p.name.lower() in BLOCKED_NAMES:
        raise ValueError('Archivo excluido/privado: ' + name)
    return p


def atomic_bytes(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + '.pending.' + str(time.time_ns()))
    with pending.open('xb') as stream:
        stream.write(value); stream.flush(); os.fsync(stream.fileno())
    os.replace(pending, path)


def research_member(relative, package):
    """Filtro de bytes archivados, nunca un filtro de estímulos del ente."""
    path = PurePosixPath(relative); name = path.as_posix()
    if any(part in EXCLUDED_PARTS for part in path.parts): return False
    # La investigación exporta fuentes y primarios, no otras entregas, copias
    # del motor ni estados profundos. Los snapshots seleccionados completos se
    # copian exclusivamente por lives(), con identidad y hash comprobados.
    if path.suffix.lower() in ('.zip','.whl','.deetsnap','.pyd','.dll','.exe','.pyc') or name.endswith('.deetsnap.gz'): return False
    if package.get('root_files_only') and len(path.parts) != 1: return False
    if package.get('include_patterns') and not any(fnmatch.fnmatchcase(name, pattern) for pattern in package['include_patterns']): return False
    if any(fnmatch.fnmatchcase(name, pattern) for pattern in package.get('exclude_patterns', [])): return False
    if any(name == prefix.rstrip('/') or name.startswith(prefix.rstrip('/') + '/') for prefix in package.get('exclude_prefixes', [])): return False
    return name not in package.get('exclude_files', [])


def source_bytes(path):
    path = Path(path); before = path.stat(); value = path.read_bytes(); after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError('Archivo cambió durante la copia; no se distribuye una operación en curso: ' + str(path))
    return value


def conflict(name, target, incoming, message):
    """Conserva la variante recibida y un recibo; nunca sustituye la local."""
    safe_name(name)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '_' + str(time.time_ns())
    folder = ROOT / 'actualizaciones/conflictos' / stamp
    received = folder / 'version_recibida' / name
    received.parent.mkdir(parents=True, exist_ok=True)
    received.write_bytes(incoming)
    receipt = {'utc': now(), 'file': name, 'reason': message,
               'local_preserved': str(target.relative_to(ROOT)),
               'local_sha256': sha(target) if target.is_file() else None,
               'incoming_sha256': sha_bytes(incoming),
               'incoming_saved': received.relative_to(ROOT).as_posix(),
               'personal_state_unchanged': True}
    (folder / 'CONFLICTO.json').write_bytes(encoded(receipt))
    return RuntimeError(message + ': ' + name + '; véase ' + str(folder.relative_to(ROOT)))


def transformed(relative, value):
    """Sólo rutas de la copia. Ninguna regla nativa ni política de decisión cambia."""
    if not relative.endswith(('.py', '.json')): return value
    text = value.decode('utf8')
    if relative == 'sistema/app/lives.py':
        old = "self.root=Path(root or SYSTEM_ROOT).resolve();self.state=self.root/'estado';identity(self.root)"
        new = "self.root=Path(root or SYSTEM_ROOT).resolve();self.state=(self.root/'../trabajo_personal/estado').resolve();identity(self.root)"
        if old not in text: raise ValueError('Cambió Store: revisar el adaptador portátil, sin reemplazo aproximado.')
        text = text.replace(old, new).replace("target.relative_to(self.root).as_posix()", "Path(os.path.relpath(target,self.root)).as_posix()")
    elif relative == 'sistema/app/native_tools.py':
        text = text.replace("Path(system_root)/'runtime/", "Path(system_root)/'../motor/")
    elif relative == 'sistema/app/legacy.py':
        text = text.replace("system_root/'runtime/optional_numeric'", "system_root/'../motor/optional_numeric'")
    elif relative == 'sistema/app/access_guard.py':
        text = text.replace("runtime=[Path(sys.prefix)", "runtime=[root.parent/'motor',root.parent/'trabajo_personal/estado',Path(sys.prefix)")
        text = text.replace("allowed=inside(p,root/'estado')", "allowed=inside(p,root.parent/'trabajo_personal/estado')or inside(p,root/'estado')")
    elif relative == 'sistema/capacidades/habitat_externo_01.py':
        text = text.replace("executable = Path(config['external_python'])", "executable = (SYSTEM / config['external_python']).resolve()")
        text = text.replace("SYSTEM / 'runtime/habitat_externo_deps'", "SYSTEM.parent / 'motor/habitat_externo_deps'")
    elif relative == 'sistema/gestionar.py':
        text = text.replace("external_python=str(Path(config['external_python']))", "external_python=str((system/Path(config['external_python'])).resolve())")
        text = text.replace("system/'runtime/habitat_externo_deps'", "system.parent/'motor/habitat_externo_deps'")
        text = text.replace("directory=s.root/'estado/servicios_locales'/args.vida", "directory=s.state/'servicios_locales'/args.vida")
    elif relative == 'sistema/capacidades/core/reproduccion/worker_core.py':
        text = text.replace("Path(__file__).resolve().parents[3]/'runtime", "Path(__file__).resolve().parents[4]/'motor")
    elif relative == 'sistema/app/compactar_historia_operativa.py':
        text = text.replace("target.relative_to(store.root).as_posix()", "Path(os.path.relpath(target,store.root)).as_posix()")
    elif relative == 'sistema/capacidades/core/DEPENDENCIAS.json':
        text = text.replace('../../runtime/', '../../../motor/')
    return text.encode('utf8')


class Build:
    def __init__(self, source, bootstrap=False):
        self.source = source.resolve(); self.bootstrap = bootstrap
        self.previous = read(OWNER) if OWNER.exists() else {'members': {}}
        self.members = {}; self.changed = []; self.origins = []; self.omissions = []
        self.staged = {}
        self.configured_names = set()

    def add(self, name, value, origin=None, source_digest=None):
        safe_name(name)
        if name.startswith(PROTECTED_PREFIXES): raise ValueError('Zona personal/local no gestionada: ' + name)
        target = ROOT / name; digest = sha_bytes(value); old = self.previous['members'].get(name)
        if target.exists():
            existing = sha(target)
            if existing != digest:
                in_this_build = self.members.get(name, {}).get('sha256') == existing
                if old and existing != old['sha256'] and not in_this_build and name not in self.configured_names:
                    raise conflict(name, target, value, 'Conflicto: modificación local protegida, no sobrescrita')
                if not old and not self.bootstrap:
                    raise conflict(name, target, value, 'Archivo local sin propiedad de actualización')
                self.changed.append(name)
            else:
                self.members[name] = {'sha256': digest, 'bytes': len(value)}
                if origin: self.origins.append({'package': name, 'source': origin, 'source_sha256': source_digest or digest, 'packaged_sha256': digest})
                return
        else: self.changed.append(name)
        # Construir primero fuera del árbol operativo: un error posterior de
        # fuente, cierre o conflicto no deja una distribución a medio actualizar.
        temporary = ROOT / 'actualizaciones/temporales' / self.release / name
        temporary.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_bytes(value); self.staged[name] = temporary
        self.members[name] = {'sha256': digest, 'bytes': len(value)}
        if origin: self.origins.append({'package': name, 'source': origin, 'source_sha256': source_digest or digest, 'packaged_sha256': digest})

    def copy(self, source, name, origin=None):
        value = source_bytes(source); original_digest = sha_bytes(value)
        self.add(name, transformed(name, value), origin or str(source.relative_to(self.source)), original_digest)

    def tree(self, source, target):
        for path in sorted(source.rglob('*')):
            if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.relative_to(source).parts): continue
            if path.suffix.lower() in ('.pyc', '.pyo') or path.name.lower() in BLOCKED_NAMES: continue
            if target == 'sistema/contratos' and path.name == 'HABITAT_EXTERNO_01.json': continue
            self.copy(path, (PurePosixPath(target) / path.relative_to(source).as_posix()).as_posix())

    def json(self, name, value, origin=None): self.add(name, encoded(value), origin)

    def prepare_release(self, args):
        selection_file = ROOT / 'actualizaciones/SELECCION.json'
        selection = read(selection_file)
        # Reconocer sólo cierres nuevos que tengan continuidad explícita, manual
        # y lista de vidas. No inferir un cierre de un snapshot recién creado.
        if not args.cerrar and not args.verificacion:
            known_seal = self.source / selection['verification']
            threshold = known_seal.stat().st_mtime if known_seal.exists() else 0
            seals = sorted((self.source/'entregas').glob('VERIFICACION_FINAL_EXTERNA*.json'), key=lambda p:p.stat().st_mtime, reverse=True)
            continuities = sorted(self.source.glob('CONTINUIDAD_*.json'), key=lambda p:p.stat().st_mtime, reverse=True)
            for candidate in seals:
                if candidate.stat().st_mtime <= threshold: break
                for continuity in continuities:
                    data = read(continuity)
                    campaign = data.get('campaign')
                    manual = data.get('manual')
                    lives = data.get('lives')
                    if not isinstance(campaign,str) or not isinstance(manual,str) or not isinstance(lives,list): continue
                    identifier = re.sub('[^A-Z0-9]','',campaign.upper())
                    seal_identifier = re.sub('[^A-Z0-9]','',candidate.stem.upper())
                    if identifier not in seal_identifier: continue
                    if continuity.stat().st_mtime > candidate.stat().st_mtime + 2: continue
                    if not (self.source/manual).is_file(): continue
                    selected = []
                    for life in lives:
                        name = life if isinstance(life,str) else life.get('life',life.get('life_id')) if isinstance(life,dict) else None
                        if name and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',name) and (self.source/'sistema/estado/vidas'/name/'VIDA.json').is_file(): selected.append(name)
                    if not selected: continue
                    args.cerrar=campaign;args.verificacion=candidate.relative_to(self.source).as_posix();args.manual=manual;args.vida=list(dict.fromkeys([*(args.vida or []),*selected]));break
                if args.cerrar: break
        seal = self.source / (args.verificacion or selection['verification'])
        if not seal.resolve().is_relative_to(self.source): raise ValueError('El comprobante debe pertenecer al sistema origen.')
        if not seal.is_file(): raise ValueError('Falta la verificación de cierre. No se distribuye una campaña abierta.')
        self.release = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        self.seal_mtime = seal.stat().st_mtime
        self.seal_sha = sha(seal); previous_seal = self.previous.get('source_seal_sha256')
        if args.cerrar:
            if not args.verificacion: raise ValueError('--cerrar requiere --verificacion con un comprobante de cierre real.')
            selection['campaign'] = args.cerrar; selection['verification'] = args.verificacion
            if args.manual: selection['manual'] = args.manual
            for life in args.vida or []:
                if life not in selection['lives']: selection['lives'].append(life)
            # SELECCION es la configuración explícita del mantenedor, no una
            # modificación personal del código del colaborador. Registrar un
            # cierre autoriza sólo su normalización; la variante previa recibe
            # el mismo respaldo transaccional y viaja en el delta si cambió.
            self.configured_names.add('actualizaciones/SELECCION.json')
        elif previous_seal and previous_seal != self.seal_sha:
            raise ValueError('Comprobante cambió: registre el nuevo corte con --cerrar, --verificacion y --manual. No se adivinan vidas ni promociones.')
        # Todo fichero operativo debe ser anterior al cierre declarado. Una campaña
        # activa puede seguir escribiendo sin que la copia interfiera con ella.
        code = self.source / 'sistema'
        late = [p.relative_to(code).as_posix() for folder in ('app','capacidades','contratos','organizaciones')
                for p in (code / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.stat().st_mtime > seal.stat().st_mtime + 2]
        late += [p.name for p in code.iterdir() if p.is_file() and p.suffix in ('.py','.ps1','.json') and p.stat().st_mtime > seal.stat().st_mtime + 2]
        if late: raise RuntimeError('Hay código/contratos posteriores al cierre. Se conserva la entrega anterior; no se interrumpe la campaña: ' + ', '.join(late[:8]))
        self.selection = selection
        self.json('actualizaciones/SELECCION.json', selection)
        self.copy(seal, 'investigacion/VERIFICACION_CORTE_ORIGINAL.json')

    def system(self):
        for folder in ('app','capacidades','contratos','organizaciones','documentacion','pruebas_minimas'):
            self.tree(self.source / 'sistema' / folder, 'sistema/' + folder)
        for path in (self.source / 'sistema').iterdir():
            if path.is_file() and path.suffix in ('.py','.ps1','.md','.json'):
                self.copy(path, 'sistema/' + path.name)
        self.copy(self.source / 'sistema/runtime' / WHEEL_NAME, 'motor/' + WHEEL_NAME)
        if self.members['motor/' + WHEEL_NAME]['sha256'] != WHEEL_SHA:
            raise ValueError('El WHL del origen no es el oficial congelado; no se publica.')
        self.tree(self.source / 'sistema/runtime/optional_numeric', 'motor/optional_numeric')
        self.tree(self.source / 'sistema/runtime/habitat_externo_deps', 'motor/habitat_externo_deps')
        cfg = read(self.source / 'sistema/contratos/HABITAT_EXTERNO_01.json')
        cfg['distribution_original_interpreter_sha256'] = cfg['external_python_sha256']
        cfg['external_python'] = '../motor/python312/python.exe'
        cfg['external_python_sha256'] = sha(ROOT / 'motor/python312/python.exe')
        self.json('sistema/contratos/HABITAT_EXTERNO_01.json', cfg)
        self.json('sistema/CONFIGURACION_DISTRIBUCION.json', {
            'software': 'Cognitive 1.1; same operational manager', 'state': '../trabajo_personal/estado',
            'motor': '../motor', 'operational_original_untouched': True,
            'adaptations': 'Relative I/O, personal state location and interpreter/codec dependency paths only. No kernel, RAW, clocks, taught contents or decision rules modified.'})

    def service_bundle(self, record, row, snap, descriptor):
        """Closed-cut transport only; no actor, new ticks or state inference."""
        state=(self.source/'sistema/estado').resolve();life=record['life_id']
        if(state/'locks'/(record['world_id']+'.lock')).exists():raise ValueError('Persistent owner still active: '+life)
        relative=descriptor.get('sidecar_directory','servicios_persistentes/'+record['world_id']);safe_name(relative)
        folder=(state/relative).resolve(strict=True)
        if not folder.is_relative_to(state):raise ValueError('Transport outside declared operational state')
        db=folder/'cola.sqlite3';wal=folder/'cola.sqlite3-wal'
        if not db.is_file()or wal.exists()and wal.stat().st_size:raise ValueError('Missing durable journal or uncheckpointed WAL; stop the owner without deleting its state.')
        if db.stat().st_mtime>self.seal_mtime+2:raise ValueError('Transport journal is later than the selected closed cut')
        observer_path=self.source/'sistema/capacidades/observador_causal_retrospectivo_01.py'
        spec=importlib.util.spec_from_file_location('_closed_cut_snapshot_observer',observer_path);observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
        snapshot=observer.Snapshot(snap);key='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'
        if key not in snapshot.metadata:raise ValueError('Record claims a service but the complete snapshot has no protocol')
        protocol=json.loads(snapshot.metadata[key]);backend=protocol.get('backend','ma02')
        if backend not in('ma02','mente_unificada'):raise ValueError('Undeclared persistent backend')
        con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
        try:
            if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Operational journal integrity failed')
            value=con.execute('SELECT value FROM meta WHERE key=?',('owner',)).fetchone();owner=json.loads(value[0])if value else{}
            if owner.get('running')is not False:raise ValueError('Source owner is not recorded as gracefully stopped')
            pending=con.execute("SELECT id,payload,payload_sha,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
            if protocol.get('closed_epoch')and pending:raise ValueError('Closed epoch contains unresolved transport')
            if not protocol.get('closed_epoch')and protocol.get('native_tick_at_checkpoint',snapshot.tick)!=snapshot.tick:raise ValueError('Snapshot and transport protocol are out of sync')
        finally:con.close()
        base='entes/protocolos/'+life;members=[]
        def include(source,relative):
            if source.stat().st_mtime>self.seal_mtime+2:raise ValueError('Operational file later than seal: '+relative)
            value=source_bytes(source);self.add(base+'/'+relative,value,str(source.relative_to(self.source)),sha_bytes(value))
            members.append({'file':relative,'bytes':len(value),'sha256':sha_bytes(value)})
        include(db,'cola.sqlite3')
        for source in sorted((folder/'resultados').rglob('*')):
            if source.is_file():include(source,'resultados/'+source.relative_to(folder/'resultados').as_posix())
        work_relative=descriptor.get('worker_directory','servicios_locales/'+life);safe_name(work_relative);work=(state/work_relative).resolve()
        if not work.is_relative_to(state):raise ValueError('Worker state outside declared system')
        if work.is_dir():
            for source in sorted(work.rglob('*')):
                if source.is_file():include(source,'artefactos_trabajador/'+source.relative_to(work).as_posix())
        members.append({'file':'VIDA.deetsnap.gz','bytes':snap.stat().st_size,'sha256':row['snapshot_sha256']})
        paired={'schema':'DEE.persistent_service.paired_export.v1','life_id':life,'profile':row['profile'],'backend':backend,
            'native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':row['snapshot_sha256'],'physical':row['physical'],
            'members':members,'queue_journal_required':True,'source_record':{'life_id':life,'world_id':record['world_id'],'parent':record.get('parent')},
            'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,
            'scope':'Complete selected native checkpoint with stopped, same-cut transport journal/outbox and worker artifacts. Native snapshot stored once in the collaboration package and materialized only for explicit paired import.'}
        bundle={'schema':'DEE.collaboration.deduplicated_service_bundle.v1','snapshot_package_member':row['snapshot'],
            'paired_export_manifest':paired,'assets_prefix':base,'native_snapshot_stored_once':True}
        self.json(base+'/PAQUETE_SERVICIO.json',bundle)
        row['persistent_service']={'bundle':base+'/PAQUETE_SERVICIO.json','backend':backend,'epoch':protocol.get('epoch',1),
            'closed_epoch':bool(protocol.get('closed_epoch')),'pending_transport_rows':len(pending),
            'full_state_import_requires_bundle':True,'snapshot_alone_not_a_full_service':True}
        return row

    def life(self, life, alias=None, cut=None, scope=None, limits=None, persistent_service=None):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}',life): raise ValueError('Identidad de vida no válida')
        source_record = self.source / 'sistema/estado/vidas' / life / 'VIDA.json'
        value = source_bytes(source_record); record = json.loads(value)
        if (source_record.parent / 'FUTURO_INTERRUMPIDO.json').exists() and cut is None:
            raise ValueError('Vida con futuro interrumpido, necesita corte explícito: ' + life)
        snap = self.source / 'sistema' / (cut['snapshot'] if cut else record['snapshot'])
        if not snap.resolve().is_relative_to((self.source/'sistema/estado/checkpoints').resolve()): raise ValueError('Snapshot fuera del estado operativo declarado')
        if snap.stat().st_mtime > self.seal_mtime + 2:
            raise ValueError('Estado posterior al cierre, no se incorpora trabajo en curso: ' + life)
        expected = cut['sha256'] if cut else record['snapshot_sha256']
        if sha(snap) != expected: raise ValueError('Snapshot de origen no coincide: ' + life)
        tick = cut['tick'] if cut else record['physical']['tick']
        # Los bytes del snapshot incluyen todos los campos, interfaces, colas y
        # progreso del propietario. VIDA es un índice, no la memoria del ente.
        name = f'entes/estados/{life}.T{tick}.{expected[:16]}.deetsnap.gz'
        self.copy(snap, name)
        row = {'alias': alias or life, 'source_life': life, 'world_id': record['world_id'], 'profile': record['profile'],
               'tick': tick, 'snapshot': name, 'snapshot_sha256': expected,
               'physical': None if cut else record['physical'],
               'source_record': f'sistema/estado/vidas/{life}/VIDA.json', 'source_record_sha256': sha_bytes(value),
               'source_snapshot': snap.relative_to(self.source).as_posix(), 'parent': record.get('parent'),
               'scope': scope or 'Corte completo de vida admitida; consulte el contrato y el informe de su campaña, no se eleva por estar distribuida.',
               'limits': limits or 'Funciones finitas y asistencia explícita; no garantiza todos los contratos históricos ni acceso ilimitado.',
               'historical_cut_not_latest': cut is not None, 'no_memories_merged': True,
               'restore': 'INICIAR.bat abrir ' + (alias or life) + ' COLAB_IDENTIDAD_NUEVA'}
        descriptor=persistent_service or(record.get('persistent_service')if cut is None else None)
        if descriptor:row=self.service_bundle(record,row,snap,descriptor)
        if cut is None and record.get('archived_operation_ledgers'):
            archives=[]
            for item in record['archived_operation_ledgers']:
                safe_name(item['file']);source=(self.source/'sistema'/item['file']).resolve(strict=True)
                if not source.is_relative_to((self.source/'sistema/estado').resolve()):raise ValueError('Ledger archive outside source state')
                if sha(source)!=item['encoded_sha256']:raise ValueError('Lossless original ledger archive identity differs')
                target='entes/historiales/'+life+'/'+source.name;self.copy(source,target)
                archives.append({**item,'package_file':target,'actor_dependency':False})
            row['archived_operation_ledgers']=archives
        self.json(f'entes/fichas/{alias or life}.json', row)
        return row

    def lives(self):
        descriptions = self.selection.get('descriptions', {})
        rows = []
        for life in self.selection['lives']:
            desc = descriptions.get(life, {})
            rows.append(self.life(life, **desc))
        for cut in self.selection.get('historical_cuts', []):
            rows.append(self.life(cut['life'], alias=cut['alias'], cut=cut, scope=cut['scope'], limits=cut['limits']))
        self.json('entes/CATALOGO.json', {'schema': 'DEE.collaboration.lives.v1', 'cuts': rows,
            'physical_snapshot_bytes_preserved': True, 'full_historical_auditor_diaries_omitted': True,
            'open_always_creates_explicit_imported_copy_not_T0': True, 'default_source_protected': 'E1_SOCIAL_11'})

    def documentation(self):
        master = self.source / self.selection['manual']
        if not master.resolve().is_relative_to(self.source): raise ValueError('El Manual Maestro debe pertenecer al sistema origen.')
        self.copy(master, master.name)
        self.json('documentos/MANUAL_VIGENTE.json', {'file': master.name, 'sha256': sha(master),
            'root_copy': master.name,
            'single_current_DOCX_authority': 'Root only; this JSON is a pointer, not another Word edition or mirror.',
            'source_campaign': self.selection['campaign'],
            'editorial_status': 'Sin validación visual según el nombre del documento recibido; no se reeditó para distribuir.' if 'SIN_VALIDACION_VISUAL' in master.name else 'Documento del corte cerrado seleccionado. Su validación editorial es la de su fuente; distribuirlo no añade validación visual.'})
        thinking = self.source.parents[2] / '4.5'
        official = thinking / 'DEE_THINKING_4_5_0_COMPILACION_Y_VALIDACION_RESULTADOS.zip'
        found = []
        if official.exists():
            with zipfile.ZipFile(official) as z:
                for member in z.namelist():
                    base = PurePosixPath(member).name
                    if base.endswith('.docx') and ('Libro_Blanco' in base or 'Maestro_Arquitectura' in base):
                        name = 'documentos/thinking_4_5/' + base
                        if name not in found:
                            self.add(name, z.read(member), 'DEE thinking/4.5/' + official.name + '::' + member); found.append(name)
                prefix = 'DEE_thinking_4_5_0/source/'
                for member in z.namelist():
                    if not member.startswith(prefix) or member.endswith('/'): continue
                    relative = member[len(prefix):]; p = PurePosixPath(relative)
                    if p.parts[0] in ('fixtures','tests','benchmarks'): continue
                    if p.suffix not in ('.cpp','.hpp','.h','.py','.cmake','.in','.toml','.json','.md','.txt','.ps1'): continue
                    self.add('fuentes/producto_4_5/' + relative,z.read(member),'DEE thinking/4.5/' + official.name + '::' + member)
        if len(found) < 2: self.omissions.append('Manuales DOCX oficiales 4.5 no recuperados por nombre; consulte documentación operativa incluida.')
        docs = self.source.parents[3]
        extra = [docs / 'FISICA DEE Y PROCESAMIENTO NATIVO/DEE_V4_0_1.docx',
                 docs / 'FISICA DEE Y PROCESAMIENTO NATIVO/Procesamiento_Nativo_DEE_Libro_Manual_v1.docx',
                 docs / 'mente basal/ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V2_1.docx']
        for path in extra:
            if path.is_file(): self.copy(path, 'documentos/ciencia/' + path.name, 'documantacion vital/' + path.relative_to(docs).as_posix())
            else: self.omissions.append('Documento no encontrado: ' + path.name)
        for name in ('INFORME_TECNICO.md','LEEME.md'):
            if (thinking / name).exists(): self.copy(thinking / name, 'documentos/thinking_4_5/' + name, 'DEE thinking/4.5/' + name)
        # Sólo fuentes ya disponibles; extraerlas no compila ni ejecuta el kernel.
        core = self.source / 'sistema/capacidades/core'
        index = read(core / 'documentacion/INDICE_MIEMBROS.json')
        selected = {name: row for name, row in index['paths'].items() if name.startswith('cpc8/genealogia/product45/')}
        selected = {name: row for name,row in selected.items() if PurePosixPath(name).suffix in ('.cpp','.hpp','.h','.json','.md','.txt')}
        wanted = {}
        for name, row in selected.items(): wanted.setdefault(row['sha256'], []).append(name)
        with gzip.open(core / 'mecanismos/RECUPERACION_POR_HASH.jsonl.gz', 'rt', encoding='ascii') as f:
            for line in f:
                obj = json.loads(line)
                if obj['sha256'] not in wanted: continue
                value = base64.b64decode(obj['base64'], validate=True)
                if sha_bytes(value) != obj['sha256']: raise ValueError('Fuente recuperada corrupta')
                for original in wanted.pop(obj['sha256']):
                    self.add('fuentes/thinking_4_5/' + PurePosixPath(original).name, value, 'Core::' + original)
        if wanted: raise ValueError('Faltan fuentes seleccionadas en el Core')

    def research(self):
        names = {'CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json','CONTINUIDAD_MENTE_DEE_INTEGRAL_MI01.json','CONTINUIDAD_CICLO02.json'}
        for path in self.source.glob('CONTINUIDAD_*.json'):
            if read(path).get('campaign') == self.selection['campaign']: names.add(path.name)
        for name in sorted(names):
            if (self.source / name).exists(): self.copy(self.source / name, 'investigacion/continuidad_original/' + name)
        # Reportes cerrados compactos, no archivos de motor ni telemetría profunda.
        folders = [self.source / 'laboratorio/campanas/MI02_ARQUITECTURA_DISTRIBUIDA/PAQUETE_ANALISIS_CANDIDATO_02']
        for folder in folders:
            for name in ('INFORME_CIENTIFICO_MI02.md','INCORPORACIONES_MI02.md','CAPACIDADES_POR_VIDA.csv','ARQUITECTURA_Y_FLUJOS_MI02.md'):
                if (folder / name).exists(): self.copy(folder / name, 'investigacion/MI02/' + name)
        current = self.source / 'evidencia/campanas' / self.selection['campaign']
        for name in ('INFORME_RESULTADOS.md','INFORME_CIENTIFICO.md','CAPACIDADES_POR_VIDA.csv','INCORPORACIONES.md','CAMBIOS_INCORPORADOS.md','DECISIONES_E_INCORPORACIONES.md'):
            if (current/name).is_file() and (current/name).stat().st_mtime <= self.seal_mtime + 2:
                self.copy(current/name,'investigacion/corte_actual/' + name)
        for path in (self.source / 'evidencia/informes').glob('*'):
            if path.is_file() and path.stat().st_size < 2_000_000 and path.suffix in ('.md','.json','.csv'):
                self.copy(path, 'investigacion/informes/' + path.name)
        for package in self.selection.get('research_packages', []):
            source_relative = package['source']; target_relative = package['target']
            safe_name(source_relative); safe_name(target_relative)
            folder = (self.source / source_relative).resolve(strict=True)
            if not folder.is_relative_to(self.source) or not folder.is_dir() or not target_relative.startswith('investigacion/'):
                raise ValueError('Paquete científico seleccionado fuera del origen o destino declarado.')
            for path in sorted(folder.rglob('*')):
                if not path.is_file(): continue
                relative = path.relative_to(folder)
                if not research_member(relative.as_posix(), package): continue
                if path.suffix.lower() in ('.zip','.whl','.deetsnap','.pyd','.dll','.exe','.pyc') or path.name.endswith('.deetsnap.gz'):
                    raise ValueError('El paquete científico no debe duplicar motor, ZIP o estados profundos: ' + str(relative))
                if path.stat().st_mtime > self.seal_mtime + 2:
                    raise ValueError('Evidencia posterior al corte seleccionado: ' + str(relative))
                self.copy(path, (PurePosixPath(target_relative) / relative.as_posix()).as_posix())
        self.json('investigacion/INDICE_ORIGEN_Y_OMISIONES.json', {'source_system_relative': '../DEE Cognitive System 1.1',
            'included': self.origins, 'excluded': ['ZIP históricos completos', 'telemetría profunda y snapshots no seleccionados',
                'entornos .venv del autor, cachés materializados redundantes, credenciales y resultados personales',
                'diarios de auditoría completos de cada vida: no necesarios para restaurar su snapshot operativo íntegro'],
            'missing_optional': self.omissions, 'not_full_scientific_historical_archive': True,
            'further_evidence_locator': 'Sistema original/evidencia/campanas/<CAMPAÑA> y sistema original/entregas; sólo localizadores, nunca importaciones operativas.'})

    def finish(self):
        # Archivos de distribución escritos por Codex también pertenecen al manifiesto.
        for folder in ('actualizaciones','ejemplos'):
            for path in (ROOT / folder).glob('*'):
                if path.is_file() and path.name not in ('ARCHIVOS_GESTIONADOS.json','CAMBIOS.jsonl','VERIFICACION_LOCAL.json','VERIFICACION_PORTABILIDAD.json') and path.suffix not in ('.zip','.nuevo'):
                    name = path.relative_to(ROOT).as_posix()
                    if name in self.staged: continue
                    self.members[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
        for name in ('LEER_PRIMERO.md','INICIAR.bat','ACTUALIZAR.bat','CREAR_ZIP.bat','AGENTS.md','trabajo_personal/LEER_PRIMERO.md','documentos/INDICE.md'):
            path = ROOT / name
            if path.exists(): self.members[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
        self.members.update({name: row for name,row in self.previous['members'].items()
                             if name.startswith('motor/python') or name.startswith('motor/externo_')})
        for folder in ('motor/python313','motor/python312','motor/externo_numpy'):
            for path in (ROOT / folder).rglob('*'):
                if path.is_file() and 'site-packages' not in path.parts and '__pycache__' not in path.parts:
                    name = path.relative_to(ROOT).as_posix(); self.members[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
        depfile = ROOT / 'motor/DEPENDENCIAS.json'
        if depfile.exists(): self.members['motor/DEPENDENCIAS.json'] = {'sha256': sha(depfile), 'bytes': depfile.stat().st_size}
        redist = ROOT / 'motor/VC_redist.x64.exe'
        if redist.exists(): self.members['motor/VC_redist.x64.exe'] = {'sha256': sha(redist), 'bytes': redist.stat().st_size}
        for path in (ROOT / 'motor/habitat_externo_deps').rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                self.members[path.relative_to(ROOT).as_posix()] = {'sha256': sha(path), 'bytes': path.stat().st_size}
        previous_names = set(self.previous['members']); current_names = set(self.members)
        retired = sorted(previous_names - current_names)
        report = {'schema': 'DEE.collaboration.manifest.v1', 'release': self.release, 'updated_utc': now(),
                  'source_campaign': self.selection['campaign'], 'source_seal_sha256': self.seal_sha,
                  'members': self.members, 'retired_members': retired, 'no_self_hash': True, 'personal_work_never_managed': True}
        # Incluye también cambios del propio lanzador, guías y actualizador; no
        # sólo los archivos que llegaron del sistema fuente en esta ejecución.
        self.changed = sorted(name for name,row in self.members.items() if self.previous['members'].get(name,{}).get('sha256') != row['sha256'])
        applied = []; moved = []
        backup_root = ROOT / 'actualizaciones/respaldos' / self.release
        try:
            for name, temporary in self.staged.items():
                target = ROOT / name
                if sha(temporary) != self.members[name]['sha256']: raise ValueError('Archivo preparado corrupto: ' + name)
                if target.is_file():
                    backup = backup_root / name; backup.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(target, backup)
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(temporary, target); applied.append(name)
            for name in retired:
                if name.startswith(PROTECTED_PREFIXES): continue
                safe_name(name); path = ROOT / name
                if path.is_file() and sha(path) == self.previous['members'][name]['sha256']:
                    backup = backup_root / name; backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(path), str(backup)); moved.append(name)
        except Exception:
            for name in reversed(moved): shutil.move(str(backup_root / name), str(ROOT / name))
            for name in reversed(applied):
                backup = backup_root / name
                if backup.is_file(): shutil.copy2(backup, ROOT / name)
                else: (ROOT / name).unlink(missing_ok=True)
            raise
        atomic_bytes(OWNER, encoded(report))
        with (ROOT / 'actualizaciones/CAMBIOS.jsonl').open('a', encoding='utf8') as f:
            f.write(json.dumps({'release': self.release,'campaign': self.selection['campaign'],'changed': self.changed,'retired_saved_to_backup': retired,'no_scientific_experiments_repeated': True},ensure_ascii=False) + '\n')
        return report


def seal_zip(manifest, changed=None):
    delivery = ROOT / 'entregas'; delivery.mkdir(exist_ok=True)
    names = sorted(name for name in manifest['members'] if not name.startswith('entregas/'))
    names += ['actualizaciones/ARCHIVOS_GESTIONADOS.json','actualizaciones/CAMBIOS.jsonl']
    if changed is not None:
        names = sorted({name for name in changed if not name.startswith('entregas/')} | {'actualizaciones/ARCHIVOS_GESTIONADOS.json','actualizaciones/CAMBIOS.jsonl'})
        target = delivery / ('cognitive_sistem_actualizacion_' + manifest['release'] + '.zip')
    else: target = delivery / 'cognitive_sistem_colaborador.zip'
    temporary = target.with_suffix('.candidato.zip')
    for name in names:
        safe_name(name)
        if name.startswith(PROTECTED_PREFIXES) and name != 'trabajo_personal/LEER_PRIMERO.md':
            raise ValueError('El ZIP no incluye estados personales, respaldos ni entregas: ' + name)
        expected = manifest['members'].get(name)
        if expected and (not (ROOT/name).is_file() or sha(ROOT/name) != expected['sha256']):
            raise ValueError('El archivo gestionado cambió; no se sella una mezcla de versiones: ' + name)
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for name in names:
            if name.startswith('trabajo_personal/') and name != 'trabajo_personal/LEER_PRIMERO.md': continue
            z.write(ROOT / name, 'cognitive sistem/' + name)
    with zipfile.ZipFile(temporary) as z:
        if z.testzip() is not None: raise ValueError('ZIP corrupto')
        if changed is None:
            for name,row in manifest['members'].items():
                if name.startswith('entregas/'): continue
                if sha_bytes(z.read('cognitive sistem/' + name)) != row['sha256']: raise ValueError('Miembro no coincide: ' + name)
    # Mantener el ZIP anterior recuperable, fuera del paquete nuevo.
    if target.exists():
        old = read(delivery / 'ULTIMA_ENTREGA.json') if (delivery / 'ULTIMA_ENTREGA.json').exists() else {}
        backup = delivery / ('cognitive_sistem_colaborador.anterior.' + str(old.get('release','sin_id')) + '.zip')
        if backup.exists(): backup = backup.with_name(backup.stem + '.' + str(time.time_ns()) + '.zip')
        os.replace(target, backup)
    os.replace(temporary, target)
    proof = {'zip': target.name, 'sha256': sha(target), 'bytes': target.stat().st_size,
             'members': len(names), 'release': manifest['release'], 'crc': 'verified',
             'member_hashes': 'verified' if changed is None else 'checked on apply',
             'not_a_new_scientific_validation': True}
    if changed is None: atomic_bytes(delivery / 'ULTIMA_ENTREGA.json', encoded(proof))
    return proof


def apply_update(path):
    """Aplicación receptora con integridad y conflictos; no toca trabajo_personal."""
    current = read(OWNER); path = Path(path).resolve(strict=True)
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise ValueError('ZIP corrupto')
        prefix = 'cognitive sistem/'
        release = json.loads(z.read(prefix + 'actualizaciones/ARCHIVOS_GESTIONADOS.json'))
        for name in release['members']:
            safe_name(name)
            if name.startswith(PROTECTED_PREFIXES) and name != 'trabajo_personal/LEER_PRIMERO.md':
                raise ValueError('Miembro gestionado en zona no actualizable: ' + name)
        candidates = []
        seen = set()
        for item in z.infolist():
            if item.is_dir(): continue
            if not item.filename.startswith(prefix): raise ValueError('Archivo fuera de la carpeta de distribución')
            name = item.filename[len(prefix):]; safe_name(name)
            if name in seen: raise ValueError('Miembro duplicado en el ZIP: ' + name)
            seen.add(name)
            if name.startswith('trabajo_personal/'):
                # Incluso el README se conserva; nunca se escribe en trabajo personal.
                continue
            if name in ('actualizaciones/ARCHIVOS_GESTIONADOS.json','actualizaciones/CAMBIOS.jsonl'): continue
            expected = release['members'].get(name)
            if expected is None: raise ValueError('Miembro no gestionado: ' + name)
            value = z.read(item)
            if sha_bytes(value) != expected['sha256']: raise ValueError('Hash inválido: ' + name)
            target = ROOT / name; old = current['members'].get(name)
            if target.exists() and sha(target) != expected['sha256'] and (old is None or sha(target) != old['sha256']):
                raise conflict(name, target, value, 'Conflicto personal protegido, no se aplicó')
            candidates.append((name,value))
        # Comprobar de antemano que el incremental tiene todas las bases necesarias.
        offered = {n for n,_ in candidates}
        for name,row in release['members'].items():
            if name.startswith('trabajo_personal/'): continue
            if name not in offered and (not (ROOT/name).is_file() or sha(ROOT/name) != row['sha256']):
                raise ValueError('Falta base del incremental: ' + name + '; use el ZIP completo.')
        backup = ROOT / 'actualizaciones/respaldos' / ('receptor_' + release['release'])
        applied = []; retired = []
        try:
            for name,value in candidates:
                target = ROOT / name
                if target.exists() and sha(target) == sha_bytes(value): continue
                if target.exists():
                    oldcopy = backup / name; oldcopy.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(target,oldcopy)
                target.parent.mkdir(parents=True,exist_ok=True)
                pending = target.with_name(target.name + '.nuevo'); pending.write_bytes(value); os.replace(pending,target)
                applied.append(name)
            for name in release.get('retired_members', []):
                safe_name(name)
                if name.startswith(PROTECTED_PREFIXES): continue
                old = current['members'].get(name); target = ROOT / name
                if old and target.is_file() and sha(target) == old['sha256']:
                    saved = backup / name; saved.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target), str(saved)); retired.append(name)
            atomic_bytes(OWNER, encoded(release))
        except Exception:
            for name in reversed(retired): shutil.move(str(backup / name), str(ROOT / name))
            for name in reversed(applied):
                saved = backup / name
                if saved.exists(): shutil.copy2(saved,ROOT/name)
                else: (ROOT/name).unlink(missing_ok=True)
            raise
    return {'release': release['release'], 'changed': applied, 'retired_saved_to_backup': retired, 'personal_work_untouched': True,
            'note': 'Código actualizado, sin rebobinar estados ni transferir aprendizajes. Cierre procesos Cognitive antes de actualizar.'}


def main():
    sys.stdout.reconfigure(encoding='utf8')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--origen', type=Path);p.add_argument('--cerrar');p.add_argument('--verificacion');p.add_argument('--manual');p.add_argument('--vida',action='append');p.add_argument('--aplicar',type=Path);p.add_argument('--solo-zip',action='store_true');p.add_argument('--bootstrap',action='store_true')
    a=p.parse_args()
    locks = ROOT / 'trabajo_personal/estado/locks'
    if locks.exists() and any(locks.glob('*.lock')):
        raise RuntimeError('Hay una escritura Cognitive local pendiente. Cierre sus procesos o examine su lock; el actualizador no los interrumpe ni borra locks.')
    if a.aplicar: print(json.dumps(apply_update(a.aplicar),ensure_ascii=False,indent=2)); return 0
    if a.solo_zip: print(json.dumps(seal_zip(read(OWNER)),ensure_ascii=False,indent=2)); return 0
    source = a.origen or ROOT.parent / 'DEE Cognitive System 1.1'
    if not source.is_dir():
        print('Este equipo no contiene el origen hermano. Reciba un ZIP nuevo o use ACTUALIZAR.bat --aplicar archivo.zip. No hay sincronización ni descarga automática.'); return 0
    b=Build(source,bootstrap=a.bootstrap);b.prepare_release(a);b.system();b.lives();b.documentation();b.research();manifest=b.finish()
    proof=seal_zip(manifest)
    if b.previous['members'] and b.changed: proof['incremental']=seal_zip(manifest,b.changed)
    print(json.dumps(proof,ensure_ascii=False,indent=2));return 0


if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e:
        print(type(e).__name__ + ': ' + str(e),file=sys.stderr);raise SystemExit(2)
