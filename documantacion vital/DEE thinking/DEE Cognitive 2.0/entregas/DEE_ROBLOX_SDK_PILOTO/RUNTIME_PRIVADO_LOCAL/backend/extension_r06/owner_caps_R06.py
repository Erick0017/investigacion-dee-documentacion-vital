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
AGGREGATE = 40000
REVISION_ROOT = Path(__file__).resolve().parents[2]
OWNER_SOURCE_SHA256 = "e7053088b6492d9d10abe1c861da560de1fb1f4a9d00468661df53782523e52b"
MAX_WORLDS = 6


def preserve_source_empty_directories(destination):
    """After Root's coherent import0, restore exact declared empty scaffold.

    This changes directories only. Snapshot/card/SQLite bytes must stay equal.
    It cannot repair missing populated data or continue an owner/uncertain queue.
    """
    destination = Path(destination).resolve(strict=True)
    context = json.loads((destination / 'CONTEXTO_EJECUCION.json').read_text('utf8'))
    context['system'] = str(destination / 'sistema')
    context['prefix'] = str(REVISION_ROOT / context['prefix'])
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


import importlib.util as _ledger_import
_ledger_spec = _ledger_import.spec_from_file_location('_r07_ledger', REVISION_ROOT / 'backend/extension_r06/ledger_caps_R06.py')
_ledger_module = _ledger_import.module_from_spec(_ledger_spec)
_ledger_spec.loader.exec_module(_ledger_module)
TickLedger = _ledger_module.TickLedger


def configured_owner(product, destination, ledger_file, *, tag='RBX01_INTEGRAL_V3', cutoff_epoch, continuous=False):
    """Return an unopened context-manager wrapping the existing official Owner.

Root must have completed official import0 first. Importer and owner may never
overlap. The C02 process lifetime has a finite28800sec ceiling and the Native actor
independently checks the earlier global cutoff at every16tick block.
"""
    product = Path(product).resolve(strict=True)
    destination = Path(destination).resolve(strict=True)
    if destination.parent != REVISION_ROOT / 'estado_demo/instancias' or not __import__('re').fullmatch(r'SDK_DEMO_[0-9A-F]{16}', destination.name): raise ValueError('SDK_PRIVATE_INSTANCE_ONLY')
    ledger_file = Path(ledger_file).resolve()
    if (destination/'LEASE_MIGRATION_IN_PROGRESS.json').exists():raise RuntimeError('LEASE_TRANSACTION_INCOMPLETE_NO_OWNER')
    if not (destination/'SDK_READY.json').is_file(): raise RuntimeError('SDK_IMPORT0_AND_SCOPE_REQUIRED')
    if not destination.is_relative_to(REVISION_ROOT) or not ledger_file.is_relative_to(REVISION_ROOT):
        raise ValueError('C02 namespace only; never open or reset an R03 destination/ledger')
    if cutoff_epoch != json.loads((destination / 'sistema/capacidades/SDK_CAPABILITIES_SCOPE_R06.json').read_text('utf8'))['native_cutoff_utc_epoch']:
        raise ValueError('Exact current finite SDK operational cutoff required')
    host_scope_path = destination / 'sistema/app/HOST_SDK_CAPABILITIES_R06.json'
    host_scope_data = host_scope_path.read_bytes()
    host_scope = json.loads(host_scope_data)
    if (host_scope.get('schema') != 'DEE.RBX01.INTEGRAL.V3.host_scope.v1'
            or host_scope.get('event_driven') is not True
            or host_scope.get('single_initial_resume') is not True
            or host_scope.get('native_cutoff_utc_epoch') != cutoff_epoch
            or host_scope.get('sealed') is not True):
        raise ValueError('Root-sealed exact C02 event-driven host required')
    host_scope_sha256 = hashlib.sha256(host_scope_data).hexdigest()
    if continuous is not True:
        raise ValueError('C02 requires explicit continuous=True; default never starts it')
    context = json.loads((destination / 'CONTEXTO_EJECUCION.json').read_text('utf8'))
    context['system'] = str(destination / 'sistema')
    context['prefix'] = str(REVISION_ROOT / context['prefix'])
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
    replacement = "self.cmd=[str(PY),'-I','-B','-X','utf8',str(self.system/'app/servicio_capabilities_R06.py'),'--system-root',str(self.system),'--vida',self.life,'--scope-sha256'," + repr(host_scope_sha256) + ",'--intervalo','60','--guardar-cada','3600','--max-segundos','7200']"
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
    scope = json.loads((destination / 'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json').read_text('utf8'))
    ledger = TickLedger(ledger_file,context['life'],scope['max_cycles'],role=scope['role'])

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
            if mode == 'eci01-rbx01-decision' and time.time() >= scope['last_new_cycle_utc_epoch']:
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
