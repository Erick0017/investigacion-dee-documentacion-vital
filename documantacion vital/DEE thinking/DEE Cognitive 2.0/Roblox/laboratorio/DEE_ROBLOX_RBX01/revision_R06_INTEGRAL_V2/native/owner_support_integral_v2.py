# Opt-in C02 event-driven host; R03 sources remain preserved.
# Explicit continuous=True; single resume; every material checkpoints.
"""R02 Root-only finite official-owner setup and shared aggregate tick ledger.

This module is stdlib on import. Calling configured_owner starts no process;
entering the returned owner is an explicit material action for Root alone.
The official512MiB Job, IPC queue, manager and checkpoint code are retained.
"""
from pathlib import Path, PurePosixPath
import ast, hashlib, json, os, sqlite3, sys, time, types

LIMIT = 512 * 1024 * 1024
AGGREGATE = 100000
REVISION_ROOT = Path(__file__).resolve().parents[1]
OWNER_SOURCE_SHA256 = "e7053088b6492d9d10abe1c861da560de1fb1f4a9d00468661df53782523e52b"
MAX_WORLDS = 6


def preserve_source_empty_directories(destination):
    """After Root's coherent import0, restore exact declared empty scaffold.

    This changes directories only. Snapshot/card/SQLite bytes must stay equal.
    It cannot repair missing populated data or continue an owner/uncertain queue.
    """
    destination = Path(destination).resolve(strict=True)
    context = json.loads((destination / 'CONTEXTO_EJECUCION.json').read_text('utf8'))
    imported = json.loads((destination / 'IMPORTACION_DIAGNOSTICA.json').read_text('utf8'))
    if not (imported['new_native_ticks'] == 0 and imported['comparison']['physical_equal'] and
            imported['comparison']['causal_prefix_equal']):
        raise ValueError('Closed exact import0 required')
    system = destination / 'sistema'; life = context['life']; pair = Path(context['prefix'])
    cardfile = system / 'estado/vidas' / life / 'VIDA.json'
    card = json.loads(cardfile.read_text('utf8'))
    service = system / 'estado/servicios_persistentes' / life
    worker = system / 'estado/servicios_locales' / life
    database = service / 'cola.sqlite3'
    if any(Path(str(database) + x).exists() and Path(str(database) + x).stat().st_size for x in ('-wal', '-journal')):
        raise RuntimeError('Open/uncertain transport must remain preserved')
    if (system / 'estado/locks' / (life + '.lock')).exists():
        raise RuntimeError('Owner lock present')
    con = sqlite3.connect(database.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        owner = json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        if owner.get('running') is not False or con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]:
            raise RuntimeError('Only closed complete transport')
    finally:
        con.close()
    def sha(path):
        value = hashlib.sha256()
        with path.open('rb') as source:
            for block in iter(lambda: source.read(1048576), b''): value.update(block)
        return value.hexdigest()
    manifest = pair / 'EXPORTACION_SERVICIO.json'
    if sha(manifest) != context['prefix_manifest_sha256']:
        raise ValueError('Full pair changed')
    critical = [cardfile, system / card['snapshot'], database]
    before = {str(p): sha(p) for p in critical}; created = []
    declared = json.loads(manifest.read_text('utf8')).get('empty_directories_preserved', [])
    for name in sorted(declared, key=lambda x: (len(PurePosixPath(x).parts), x)):
        relative = PurePosixPath(name)
        if (relative.is_absolute() or '\\' in name or ':' in name or
                not relative.parts or any(x in ('.', '..') for x in relative.parts)):
            raise ValueError('Safe declared empty directory')
        if relative.parts[0] == 'artefactos_trabajador':
            target = worker.joinpath(*relative.parts[1:])
        elif relative.parts[0] == 'resultados':
            target = service.joinpath(*relative.parts)
        else:
            raise ValueError('Only declared worker/result directory')
        for part in (target, *target.parents):
            if part.is_symlink() or part.exists() and getattr(part.lstat(), 'st_file_attributes', 0) & 1024:
                raise ValueError('No linked operational paths')
        if target.exists():
            if not target.is_dir(): raise ValueError('Directory occupied by file')
            continue
        source = pair.joinpath(*relative.parts)
        if not source.is_dir() or any(p.is_file() for p in source.rglob('*')) or not target.parent.is_dir():
            raise ValueError('Missing populated/ancestor data is never repaired')
        target.mkdir(); created.append(name)
    if before != {str(p): sha(p) for p in critical}:
        raise RuntimeError('Directory preservation altered physical/transport bytes')
    value = {'schema': 'DEE.RBX01.source_empty_directories.R01', 'created': created,
             'declared': len(declared), 'critical_unchanged': True, 'new_native_ticks': 0}
    output = destination / 'RBX01_DIRECTORIOS_FUENTE.json'
    if output.exists():
        raise FileExistsError('Directory witness already exists, preserve')
    write_atomic(output, value)
    return value


def write_atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.WRITING')
    if temporary.exists():
        raise RuntimeError('Prior ledger write uncertain; preserve, no retry')
    with temporary.open('x', encoding='utf8') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n'); out.flush(); os.fsync(out.fileno())
    os.replace(temporary, path)


class TickLedger:
    """One aggregate100k ledger with separate durable intents/reservations per life.

    The short exclusive technical file lock protects JSON update only; Native
    processing remains concurrent across DIFFERENT complete worlds. An unknown
    intent is never purged, guessed or replayed. This is host accounting only.
    """
    SCHEMA='DEE.RBX01.INTEGRAL.V2.prospective_native_budget.R01'
    def __init__(self,path,life,max_cycles):
        self.path=Path(path).resolve();self.life=life;self.max_cycles=max_cycles
        if max_cycles!=24:raise ValueError('Exactly24 prospective new opportunities per world')
        if not self.path.is_relative_to(REVISION_ROOT):raise ValueError('Ledger stays in this revision')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.lock():
            if not self.path.exists():
                write_atomic(self.path,{'schema':self.SCHEMA,'limit':AGGREGATE,'max_worlds':MAX_WORLDS,
                  'consumed':0,'worlds':{},'intents':{},'historical_source_ticks_not_new_budget':{'DEV4':6256},
                  'max_ticks_per_cycle':4096,'no_reset_of_physical_or_environmental_clocks':True})
            self.read()
    def lock(self):
        from contextlib import contextmanager
        @contextmanager
        def held():
            path=self.path.with_name(self.path.name+'.LOCK');fd=None;deadline=time.monotonic()+10
            while fd is None:
                try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
                except FileExistsError:
                    if time.monotonic()>=deadline:raise RuntimeError('Ledger technical lock persists; preserve, no stale-lock deletion')
                    time.sleep(.02)
            token=os.urandom(16).hex()
            try:
                with os.fdopen(fd,'w',encoding='utf8')as out:json.dump({'pid':os.getpid(),'token':token,'life':self.life},out);out.flush();os.fsync(out.fileno())
                yield
            finally:
                # Never unlink a replaced lock from another process.
                if path.exists()and json.loads(path.read_text('utf8')).get('token')==token:path.unlink()
        return held()
    def read(self):
        v=json.loads(self.path.read_text('utf8'))
        if v.get('schema')!=self.SCHEMA or v.get('limit')!=AGGREGATE or v.get('max_worlds')!=MAX_WORLDS or not isinstance(v.get('intents'),dict):
            raise ValueError('Integral aggregate budget identity')
        if v['consumed']!=sum(w['consumed']for w in v['worlds'].values()):raise ValueError('Aggregate dose disagrees with worlds')
        return v
    def begin(self,life,identifier,mode):
        with self.lock():
            v=self.read()
            if life!=self.life or life in v['intents']:raise RuntimeError('Wrong life or its unresolved Native intent')
            if life not in v['worlds']:
                if len(v['worlds'])>=MAX_WORLDS:raise RuntimeError('Six-world prospective budget exhausted')
                v['worlds'][life]={'consumed':0,'reserved':0,'cycles':0,'max_cycles':self.max_cycles}
            w=v['worlds'][life]
            if w['max_cycles']!=self.max_cycles:raise ValueError('World opportunity supply changed')
            if mode=='eci01-rbx01-decision':
                if w['reserved']or w['cycles']>=self.max_cycles:raise RuntimeError('Opportunity exhausted/pending')
                if v['consumed']+sum(x['reserved']for x in v['worlds'].values())+4096>AGGREGATE:raise RuntimeError('Aggregate100k Native budget exhausted')
                w['reserved']=4096
            elif mode not in('eci01-rbx01-query-sensor','eci01-rbx01-function','eci01-rbx01-feedback','eci01-rbx01-estado'):
                raise ValueError('Closed integral Native modes')
            elif mode!='eci01-rbx01-estado'and not w['reserved']:raise RuntimeError('No reserved opportunity')
            v['intents'][life]={'life':life,'id':identifier,'mode':mode,'utc_epoch':time.time()};write_atomic(self.path,v)
    def finish(self,life,identifier,before,after,mode):
        with self.lock():
            v=self.read();i=v['intents'].get(life);w=v['worlds'][life]
            if not i or(i['life'],i['id'],i['mode'])!=(life,identifier,mode):raise RuntimeError('Actual Native budget correlation mismatch')
            n=after-before
            if not(0<=n<=w['reserved'])and not(mode=='eci01-rbx01-estado'and n==0):raise RuntimeError('Unexpected Native advance; intent preserved')
            v['consumed']+=n;w['consumed']+=n;w['reserved']-=n
            if mode=='eci01-rbx01-feedback':w['reserved']=0;w['cycles']+=1
            if w['consumed']>98304 or v['consumed']>AGGREGATE:raise RuntimeError('Budget exceeded; preserve intent')
            w['last_completed']={**i,'before_tick':before,'after_tick':after,'actual_ticks':n}
            v['last_completed']=w['last_completed'];del v['intents'][life];write_atomic(self.path,v)


def configured_owner(product, destination, ledger_file, *, tag='RBX01_INTEGRAL_V2', cutoff_epoch, continuous=False):
    """Return an unopened context-manager wrapping the existing official Owner.

Root must have completed official import0 first. Importer and owner may never
overlap. The C02 process lifetime has a finite28800sec ceiling and the Native actor
independently checks the earlier global cutoff at every16tick block.
"""
    product = Path(product).resolve(strict=True)
    destination = Path(destination).resolve(strict=True)
    ledger_file = Path(ledger_file).resolve()
    if not destination.is_relative_to(REVISION_ROOT) or not ledger_file.is_relative_to(REVISION_ROOT):
        raise ValueError('C02 namespace only; never open or reset an R03 destination/ledger')
    if cutoff_epoch != 1794802380:
        raise ValueError('Fixed integral Native cutoff04:13UTCNov16 required')
    host_scope_path = destination / 'sistema/app/HOST_INTEGRAL_V2.json'
    host_scope_data = host_scope_path.read_bytes()
    host_scope = json.loads(host_scope_data)
    if (host_scope.get('schema') != 'DEE.RBX01.INTEGRAL.V2.host_scope.v1'
            or host_scope.get('event_driven') is not True
            or host_scope.get('single_initial_resume') is not True
            or host_scope.get('native_cutoff_utc_epoch') != cutoff_epoch
            or host_scope.get('sealed') is not True):
        raise ValueError('Root-sealed exact C02 event-driven host required')
    host_scope_sha256 = hashlib.sha256(host_scope_data).hexdigest()
    if continuous is not True:
        raise ValueError('C02 requires explicit continuous=True; default never starts it')
    context = json.loads((destination / 'CONTEXTO_EJECUCION.json').read_text('utf8'))
    imported = json.loads((destination / 'IMPORTACION_DIAGNOSTICA.json').read_text('utf8'))
    if not (imported['new_native_ticks'] == 0 and imported['comparison']['physical_equal'] and
            imported['comparison']['causal_prefix_equal']):
        raise ValueError('Exact full causal import0 comparison required')
    if Path(context['system']) != destination / 'sistema':
        raise ValueError('Exact existing diagnostic system')
    horizon = min(28800, int(cutoff_epoch - time.time()))
    if horizon <= 0:
        raise RuntimeError('Native cutoff reached; do not open owner')
    source = product / 'reproducibilidad/propietario_diagnostico.py'
    if hashlib.sha256(source.read_bytes()).hexdigest() != OWNER_SOURCE_SHA256:
        raise ValueError('Preserved official owner source changed')
    text = source.read_text('utf-8-sig')
    command = "self.cmd=[str(PY),'-I','-B','-X','utf8',str(self.system/'gestionar.py'),'--system-root',str(self.system),'mente-unificada-iniciar','--vida',self.life,'--backend','mente_unificada','--eci01','--pausado','--intervalo','60','--guardar-cada','3600','--max-segundos','7200']"
    replacement = "self.cmd=[str(PY),'-I','-B','-X','utf8',str(self.system/'app/servicio_eventos_integral_v2.py'),'--system-root',str(self.system),'--vida',self.life,'--scope-sha256'," + repr(host_scope_sha256) + ",'--intervalo','60','--guardar-cada','3600','--max-segundos','7200']"
    material_anchor = "self.control('reanudar');row=self.wait(identifier);self.control('pausar')"
    if text.count(command) != 1 or text.count(material_anchor) != 1:
        raise ValueError('Exact official command/material anchors changed')
    text = text.replace(command, replacement).replace(material_anchor, 'row=self.wait(identifier)')
    anchor = "'--max-segundos','7200'"
    if text.count(anchor) != 1:
        raise ValueError('Official finite owner command anchor changed')
    text = text.replace(anchor, "'--max-segundos','" + str(horizon) + "'")
    # Host startup/commit waits only. Preserve the original official source,
    # Native cadence, actor, 512MiB Job and prospective cutoff unchanged.
    for before, after in (
        ('deadline=time.monotonic()+60', 'deadline=time.monotonic()+360'),
        ('self.proc.wait(timeout=60)', 'self.proc.wait(timeout=600)'),
    ):
        if text.count(before) != 1:
            raise ValueError('Official bounded owner wait anchor changed: ' + before)
        text = text.replace(before, after)
    ast.parse(text)
    module = types.ModuleType('_RBX01_official_owner_finite_lifetime')
    module.__file__ = str(source)
    exec(compile(text, str(source) + ':RBX01_finite_lifetime_only', 'exec'), module.__dict__)
    module.configure(destination, destination / 'sistema', product / 'motor/python313/python.exe')
    if module.MEMORY_LIMIT != LIMIT:
        raise ValueError('Official512MiB owner Job limit changed')
    scope = json.loads((destination / 'sistema/capacidades/RBX06_NATIVE_SCOPE_INTEGRAL_V2.json').read_text('utf8'))
    ledger = TickLedger(ledger_file,context['life'],scope['max_cycles'])

    class FiniteOfficialOwner(module.Owner):
        def __enter__(self):
            super().__enter__()
            if self.initial.get('C02_host_event_driven') is not True:
                raise RuntimeError('Wrong service loop; preserve owner, no material')
            self._r04_idle_baseline = self.initial['idle_ticks']
            resumed = self.control('reanudar')
            resume_result = json.loads(resumed['result'])
            if (resume_result['after_tick'] != resume_result['before_tick']
                    or resume_result['owner_idle_ticks_after'] != self._r04_idle_baseline):
                raise RuntimeError('Administrative Native evolution; preserve')
            return self

        def wait(self, identifier, limit=900):
            administrative = any(identifier.startswith(self.runid + '_' + operation + '_')
                                 for operation in ('reanudar', 'pausar', 'guardar', 'detener'))
            if administrative:
                limit = 600
            else:
                deadline = getattr(self, '_rbx_phase_deadline', None)
                if deadline is None:
                    deadline = self._rbx_phase_deadline = time.monotonic() + 900
                limit = min(limit, max(0, deadline - time.monotonic()))
            return super().wait(identifier, limit=limit)

        def control(self, operation):
            if operation == 'pausar':
                self._rbx_pause_attempted = True
            return super().control(operation)

        def material(self, identifier, literal, **kwargs):
            if time.time() >= cutoff_epoch:
                raise RuntimeError('Native cutoff reached')
            mode = literal.get('modo')
            if mode == 'eci01-rbx01-decision' and time.time() >= 1794798600:
                raise RuntimeError('HOST_HORIZON_INTEGRAL_NEW_Q1_BLOCKED: before Native ledger/queue admission; zero ticks, no retry')
            ledger.begin(self.life, identifier, mode)
            self._rbx_phase_deadline = None  # Start 900s at material wait, after resume commit.
            self._rbx_pause_attempted = False
            try:
                value = super().material(identifier, literal, **kwargs)
            except BaseException:
                # Administrative pause only; never retry the material request.
                # If it is still executing, the queued pause has precedence at
                # its next owner boundary. The original ID/ledger intent stay.
                if not self._rbx_pause_attempted:
                    try:
                        self.control('pausar')
                    except BaseException as pause_error:
                        module.append({'kind': 'RBX01_PAUSE_UNCERTAIN', 'life': self.life,
                                       'id': identifier, 'error': str(pause_error),
                                       'no_material_retry': True})
                raise
            finally:
                self._rbx_phase_deadline = None
            if value['owner_idle_ticks_after'] != self._r04_idle_baseline:
                raise RuntimeError('Idle Native advance forbidden; preserve ledger intent')
            ledger.finish(self.life, identifier, value['before_tick'], value['after_tick'], mode)
            return value

    return FiniteOfficialOwner(context['life'], tag, destination / 'sistema')
