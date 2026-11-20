"""Local prepared interface to Cognitive. No model, solver, or actor Runtime.

HTTP serves only 127.0.0.1. One command worker calls the existing Supervisor;
refreshes read cached SQLite owner metadata and immutable external frames.
"""
from __future__ import annotations
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import contextlib
import ctypes
import gzip
import hashlib
import http.client
import importlib.util
import json
import os
import queue
import re
import shlex
import socket
import sys
import threading
import time
import traceback
from types import SimpleNamespace
import uuid
import webbrowser
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VERSION = 'DEE.Cognitive.2.0.local.R02'
PROTECTED = {'E1_SOCIAL_11', 'MA_MAIN_R9', 'APD04_SEMILLA_COLABORADOR_R01', 'APD05_MAIN'}
FORMS = ('alfa', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'suma', 'diferencia', 'agrega',
         'resta', 'total', 'quita', 'compara', 'recuerda', 'luma', 'nara', 'clasifica', 'equilibra')


def now():
    return datetime.now(timezone.utc).isoformat()


@contextlib.contextmanager
def shared_read_handle(path):
    """Windows reader permits the owner's atomic replace, never a write."""
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateFileW(str(Path(path).resolve()), 0x80000000, 1 | 2 | 4, None, 3, 128, None)
    if handle == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    try: yield kernel, handle
    finally: kernel.CloseHandle(handle)


def read_bytes_shared(path):
    if os.name != 'nt': return Path(path).read_bytes()
    from ctypes import wintypes
    with shared_read_handle(path) as (kernel, handle):
        kernel.GetFileSizeEx.argtypes = [wintypes.HANDLE, ctypes.POINTER(ctypes.c_longlong)]
        kernel.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
                                   ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
        size = ctypes.c_longlong()
        if not kernel.GetFileSizeEx(handle, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        if not 0 <= size.value <= 67108864: raise ValueError('Bounded passive JSON read exceeded 64 MiB.')
        data = ctypes.create_string_buffer(size.value)
        received = wintypes.DWORD()
        if not kernel.ReadFile(handle, data, size.value, ctypes.byref(received), None):
            raise ctypes.WinError(ctypes.get_last_error())
        if received.value != size.value: raise IOError('Incomplete immutable metadata read.')
        return data.raw[:received.value]


def read(path):
    return json.loads(read_bytes_shared(path).decode('utf-8-sig'))


def atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.pending.' + uuid.uuid4().hex)
    with temp.open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temp, path)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def bootstrap():
    """Verify the already prepared runtime. Never install/extract on opening."""
    import struct
    python = ROOT / 'motor/python313/python.exe'
    packages = ROOT / 'motor/python313/site-packages'
    marker = packages / 'INSTALACION_DEE.json'
    wheel_sha = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
    if sys.version_info[:2] != (3, 13) or struct.calcsize('P') != 8 or Path(sys.executable).resolve() != python.resolve():
        raise RuntimeError('Use el CPython 3.13 x64 incluido mediante ABRIR_DEE_COGNITIVE.bat.')
    if not marker.is_file() or read(marker).get('wheel_sha256') != wheel_sha:
        raise RuntimeError('Runtime local no preparado. Falta INSTALACION_DEE.json válido; use el instalador offline explícito antes de abrir Génesis. No se instala nada al abrir.')
    sys.path[:0] = [str(ROOT / 'sistema'), str(ROOT / 'sistema/app')]
    from app.native_tools import identity
    identity(ROOT / 'sistema')
    import dee_thinking
    if not Path(dee_thinking.__file__).resolve().is_relative_to(packages.resolve()):
        raise RuntimeError('Import ajeno al paquete local; no se utiliza silenciosamente otro motor.')
    for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[variable] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    return module('genesis_existing_entry', ROOT / 'sistema/app/usar_dee.py')


def decode_row(value):
    row = value.get('request') or value
    if isinstance(row, dict):
        row = dict(row)
        for field in ('result', 'error'):
            if isinstance(row.get(field), str):
                try: row[field] = json.loads(row[field])
                except ValueError: pass
    return row


def exact_json(value):
    """Do not let JSON.parse round uint64 fields in nested native receipts."""
    if type(value) is int and abs(value) > 9007199254740991:
        return str(value)
    if isinstance(value, dict): return {str(k): exact_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)): return [exact_json(v) for v in value]
    return value


def literal_command(text, entry):
    """Syntactic frontend, not Spanish semantic interpretation or arithmetic."""
    text = text.strip()
    # A fixed optional bracket spelling: no arithmetic result is calculated.
    short = re.fullmatch(r'([a-z]+)\s*\[\s*(\d+)\s*,\s*(\d+)\s*\]', text)
    if short:
        text = 'usar ' + short[1] + ' ' + short[2] + ' ' + short[3]
    tokens = shlex.split(text)
    if not tokens:
        raise ValueError('Sintaxis vacía; no se envió una experiencia.')
    if tokens[0] == 'palabra': tokens[0] = 'palabra-ecosistema'
    if tokens[0] == 'acceso':
        if (len(tokens) == 3 and tokens[1] == 'memoria'
                and tokens[2] in ('alfa', 'beta', 'gamma', 'delta', 'epsilon', 'zeta')):
            return [{'modo': 'memoria', 'operacion_memoria': 'usar', 'contexto': tokens[2]}], 'omit', 'closed'
        if (len(tokens) == 5 and tokens[1] == 'numero'
                and tokens[2] in ('suma', 'diferencia')
                and all(re.fullmatch(r'(?:0|[1-9]|[12][0-9]|3[0-2])', value) for value in tokens[3:])):
            row = {'modo': 'eci01-aritmetica-directa', 'operacion': tokens[2],
                   'izquierda': int(tokens[3]), 'derecha': int(tokens[4])}
            from capacidades.aritmetica_directa_eci02 import validate_literal
            validate_literal(row)
            return [row], 'omit', 'closed'
        if (len(tokens) == 4 and tokens[1] == 'balance'
                and all(re.fullmatch(r'(?:0|[1-9]|1[0-9]|20)', value) for value in tokens[2:])):
            row = {'modo': 'eci01-balance', 'izquierda': int(tokens[2]), 'derecha': int(tokens[3])}
        elif len(tokens) == 3 and tokens[1] == 'vivir' and tokens[2] in ('1', '2', '3', '4'):
            row = {'modo': 'eci01-vigencia-vivir', 'oportunidades': int(tokens[2]), 'lexico': True}
        else:
            raise ValueError('Sintaxis: acceso balance L R (enteros0..20) | acceso vivir1..4; no se envió una experiencia.')
        from capacidades.acceso_integrado_eci01 import validate_literal
        validate_literal(row)
        return [row], 'real', 'closed'
    if tokens[0] == 'vigencia':
        if tokens == ['vigencia', 'estado']:
            row = {'modo': 'apd05-vigencia-estado'}
        elif len(tokens) == 3 and tokens[1] == 'vivir' and tokens[2] in ('1', '2', '3', '4'):
            row = {'modo': 'apd05-vigencia-vivir', 'oportunidades': int(tokens[2]), 'lexico': True}
        else:
            raise ValueError('Sintaxis: vigencia estado | vigencia vivir 1..4; no se envió una experiencia.')
        from app.protocolo_apd05 import validate_literal
        validate_literal(row)
        return [row], 'real', 'closed'
    # Arbitrary local paths, JSON files and external modules are never accepted.
    admitted = {'usar', 'palabra-ecosistema', 'ensenar', 'ensenar-nueva', 'ensenar-ecosistema',
                'lenguaje', 'lenguaje-nuevo', 'acumular', 'componer', 'ecosistema-vivir',
                'ecosistema-cambio', 'ecosistema-iniciar', 'objetivo', 'paso', 'meta', 'meta-paso'}
    if tokens[0] not in admitted:
        raise ValueError('Comando fuera de la gramática local; no se envió una experiencia.')
    if tokens[0] in {'usar', 'palabra-ecosistema', 'ensenar', 'ensenar-nueva', 'ensenar-ecosistema', 'lenguaje', 'lenguaje-nuevo', 'objetivo', 'meta'}:
        if len(tokens) < 2 or tokens[1] not in FORMS:
            raise LookupError('Forma no registrada; no se envió una experiencia.')
    try:
        options = entry.command_parser().parse_args(tokens)
    except (SystemExit, argparse.ArgumentError) as error:
        raise ValueError('Sintaxis o rango inválido; no se envió una experiencia.') from error
    return entry.literal_rows(options), options.retorno, options.actuador


class LocalTransport:
    """Mixin: existing metadata/client and QueueDB, no Runtime or refresh child."""
    def manager(self, args, timeout=None):
        operation = str(args[0]).removeprefix('mente-unificada-')
        if operation == 'importar':
            return super().manager(args, timeout)
        p = argparse.ArgumentParser(add_help=False)
        p.add_argument('--vida', required=True); p.add_argument('--id')
        p.add_argument('--esperar', type=float, default=30)
        p.add_argument('--situaciones'); p.add_argument('--ticks', type=int)
        p.add_argument('--actuador', default='closed'); p.add_argument('--retorno', default='real')
        a = p.parse_args(list(map(str, args[1:])))
        from app.cliente_mente_unificada import request
        backend = self
        class MetadataStore:
            state = backend.state_root
            def record(self, life): return backend.record(life)
        return request(MetadataStore(), a.vida, 'sesion' if operation == 'pedir' else ('avanzar' if operation == 'continuar' else operation),
                       identifier=a.id, situations=json.loads(a.situaciones) if a.situaciones else None,
                       ticks=a.ticks, actuator=a.actuador, feedback=a.retorno, wait=a.esperar)

    def record(self, life):
        if getattr(self, 'external_view_only', False):
            from app.cola_local import QueueDB
            database = self.state_root / 'servicios_persistentes' / self.external_world_id / 'cola.sqlite3'
            if not database.is_file():
                raise FileNotFoundError('El propietario externo aún no publicó su servicio; no se importa otra vida.')
            value = QueueDB(database).get_meta('genesis_record_index')
            if not value or value.get('life_id') != life:
                raise FileNotFoundError('No hay índice coherente del propietario externo para esta vida.')
            return value
        cache = getattr(self, '_genesis_record', None)
        process = getattr(self, 'process', None)
        active = process is not None and process.poll() is None
        if cache and cache.get('life_id') != life:
            raise ValueError('El índice en caché pertenece a otra vida; no se redirige su propietario.')
        if cache and active:
            from app.cola_local import QueueDB
            database = self.state_root / 'servicios_persistentes' / cache['world_id'] / 'cola.sqlite3'
            if database.is_file():
                published = QueueDB(database).get_meta('genesis_record_index')
                # A complete import preserves prior metadata. The parent's
                # published index must never redirect this copy's owner.
                if (published and published.get('life_id') == life
                        and published.get('world_id') == cache['world_id']):
                    self._genesis_record = published
                    return published
            return cache
        # Only before starting an owner or after its actual OS exit. Normal
        # refreshes use the owner's published immutable index, not this file.
        self._genesis_record = read(self.state_root / 'vidas' / life / 'VIDA.json')
        return self._genesis_record

    @property
    def state_root(self):
        return self.root / ('trabajo_personal/estado' if (self.root / 'actualizaciones/arrancar.py').is_file() else 'sistema/estado')

    def owner_argv(self, life):
        return [str(self.python), '-I', '-B', '-X', 'utf8', str(HERE / 'propietario_genesis.py'),
                '--vida', life, '--pausado', '--intervalo', str(self.config['idle_interval_seconds']),
                '--max-segundos', str(self.config['owner_max_seconds'])]


class Genesis:
    def __init__(self, entry, life=None, selection=None, mock=False, new=False, diagnostic=False, viewer_only=False, world_id=None):
        self.entry, self.mock = entry, mock
        self.distributed = (ROOT / 'actualizaciones/arrancar.py').is_file()
        self.home = ROOT / ('trabajo_personal/genesis' if self.distributed else 'sistema/estado/genesis')
        if diagnostic:
            if not life: raise ValueError('Una sesión diagnóstica exige identidad explícita.')
            self.home = self.home / 'diagnosticos' / entry.identifier(life)
        self.home.mkdir(parents=True, exist_ok=True)
        self.pointer = self.home / 'SELECCION_PERSONAL.json'
        default = ROOT / 'sistema/contratos/ENTRADA_SENCILLA_APD03.json'
        local = HERE / 'SELECCION_CANDIDATA.json'
        self.config = read(selection or (local if local.is_file() else default))
        if self.config.get('status') != 'CLOSED_SELECTED_FOR_USE':
            raise ValueError('La candidata no tiene un par completo seleccionado y cerrado.')
        if life:
            self.life = entry.identifier(life)
            self.explicit_life = not new
        elif self.pointer.is_file():
            self.life = entry.identifier(read(self.pointer)['life_id'])
            self.explicit_life = False
        else:
            self.life = 'GENESIS_PERSONAL_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
            self.explicit_life = False
        if self.life in PROTECTED and not viewer_only:
            raise ValueError('Original protegido; use una copia completa personal identificada.')
        base = entry.DistributionBackend if self.distributed else entry.OriginalBackend
        backend_class = type('GenesisExistingBackend', (LocalTransport, base), {})
        self.backend = backend_class(ROOT, self.config)
        self.viewer_only = viewer_only
        if viewer_only:
            if not life or not world_id:
                raise ValueError('Solo visor exige --vida y --mundo explícitos; no se adivina pertenencia.')
            self.backend.external_view_only = True
            self.backend.external_world_id = entry.identifier(world_id)
            self.session = SimpleNamespace(owned=False, state={'pending_material': None, 'uncertain_preserved': False})
        else:
            self.session = entry.Supervisor(ROOT, self.life, self.backend, self.config)
        self.session_lock = None
        self.jobs, self.work = {}, queue.Queue(maxsize=8)
        self.latest, self.error = None, None
        self.recording, self.record_stream, self.last_recorded_frame = False, None, None
        self.record_begin = 0.0
        self.mutex = threading.RLock()
        self.events = []
        # Passive presentation only. These values never enter the Native owner,
        # an experience, the semantic decoder, or its choice of a response.
        self.presentation = {'revision': 0}
        self.thread = threading.Thread(target=self._work, daemon=True, name='GENESIS-single-command-worker')
        self.thread.start()

    def event(self, name, **value):
        item = {'wall_utc': now(), 'event': name, 'life_id': self.life, **value}
        with self.mutex:
            self.events.append(item)
            self.events = self.events[-100:]
            if self.record_stream:
                self.record_stream.write(json.dumps(item, ensure_ascii=False, separators=(',', ':')) + '\n')
                self.record_stream.flush()
                if self.record_file.stat().st_size > 32000000:
                    self.record_stream.write(json.dumps({'event': 'recording_limit_reached', 'wall_utc': now(),
                        'limit_compressed_bytes': 32000000, 'life_id': self.life,
                        'scope': 'Only recording stopped; the native owner and its receipts were not stopped or discarded.'}) + '\n')
                    self.record_stream.close(); self.record_stream = None; self.recording = False
        return item

    def submit(self, action, value=None):
        if self.viewer_only and action not in {'grabar', 'exportar'}:
            raise PermissionError('Solo visor del propietario externo: no crea propietario ni presenta entradas.')
        if action not in {'abrir', 'vivir', 'pausar', 'guardar', 'detener', 'ejecutar', 'ensenar', 'resultado', 'exportar', 'grabar', 'reposo', 'conciliar-propietario'}:
            raise ValueError('Operación de interfaz no admitida.')
        ident = 'genesis_job_' + uuid.uuid4().hex
        with self.mutex: self.jobs[ident] = {'id': ident, 'action': action, 'value': value, 'status': 'queued', 'submitted_utc': now()}
        self.event('interface_operation_submitted', interface_action=action,
                   operator_value=value, attribution='Operator-scheduled literal request; not an acquired plan or a Native outcome.')
        self.work.put_nowait((ident, action, value))
        return self.jobs[ident]

    def _work(self):
        while True:
            ident, action, value = self.work.get()
            self.jobs[ident]['status'] = 'processing'
            try:
                result = self.perform(action, value)
                # Completion and the status view share a publication lock.
                # This changes no Native request, result or physical state.
                with self.mutex:
                    self.jobs[ident].update(status='completed', result=result, finished_utc=now())
                    self.event('interface_operation_result', interface_action=action, result=result)
            except Exception as error:
                with self.mutex:
                    self.jobs[ident].update(status='error', error={'type': type(error).__name__, 'detail': str(error)}, finished_utc=now())
                    self.event('interface_operation_error', interface_action=action, error=self.jobs[ident]['error'])
            self.work.task_done()

    def perform(self, action, value):
        if action == 'grabar': return self.toggle_recording()
        if action == 'exportar': return self.export_continuity()
        if action == 'conciliar-propietario':
            process = self.backend.process
            if process is None: return {'INSTRUMENTO': 'No hay proceso propio que conciliar.'}
            if process.poll() is None:
                raise RuntimeError('El proceso propio sigue activo; use Detener, no se mata ni reinicia.')
            result = self.backend.finish_owned(1)
            self.session.owned = False
            self.session.log('already_exited_owned_process_reconciled', result=result,
                no_native_restart=True, pending_unchanged=self.session.state.get('pending_material'))
            return {'INSTRUMENTO': 'Proceso propio ya salido; se cerró su contabilidad, no se borraron colas ni se declaró STOP confirmado.', 'exited_process': result}
        if action == 'abrir':
            if self.session_lock is None:
                self.session_lock = self.entry.SessionLock(self.session.folder / 'SUPERVISOR.lock')
                self.session_lock.__enter__()
            existing = self.session.state_path.is_file()
            if not existing and self.explicit_life:
                # An explicitly assigned existing diagnostic life may not yet
                # have an entry protocol; never create another world instead.
                card = self.backend.record(self.life)
                self.session.state.update(world_id=card['world_id'], source_snapshot_sha256=(card.get('parent') or {}).get('encoded_sha256'),
                    source_life=(card.get('parent') or {}).get('life_id'), imported_at=now(),
                    genesis_explicit_existing_life=True)
                self.session.save_protocol()
                result = self.session.open(new=False)
            else:
                result = self.session.open(new=not existing)
            atomic(self.pointer, {'schema': 'GENESIS.personal_pointer.R01', 'life_id': self.life,
                'world_id': result['world_id'], 'first_selected_utc': now(),
                'not_ACTIVO': True, 'no_new_world_on_reopen': True})
            started = self.session.start() if not self.session.owned else {'already_owned': True}
            return {'INTERFAZ': 'Misma copia personal abierta; el propietario inicia pausado.', 'record': result, 'owner': started}
        if not self.session.owned:
            raise RuntimeError('Abra/continúe primero la misma copia personal; no se crea otra vida al ejecutar.')
        if action in {'vivir', 'pausar', 'guardar', 'detener'}:
            return self.session.control({'vivir': 'reanudar'}.get(action, action))
        if action == 'reposo':
            ticks = int(value.get('ticks', 67))
            if not 1 <= ticks <= 4096: raise ValueError('Reposo declarado: 1..4096 ticks, no restauración ni limpieza.')
            request_id = 'genesis_rest_' + uuid.uuid4().hex
            if self.session.state.get('pending_material'):
                raise RuntimeError('Hay una petición pendiente: concilie su mismo ID antes de otro avance.')
            payload = {'operacion': 'avanzar', 'ticks': ticks}
            self.session.state['pending_material'] = {'id': request_id,
                'payload_sha256': hashlib.sha256(self.entry.canonical(payload).encode()).hexdigest(),
                'recorded_before_submission': now()}
            self.session.save_protocol()
            self.session.log('literal_dynamic_rest_submission', id=request_id, payload=payload,
                no_recovery_promised=True, host_selected_answer=False)
            # Generic native advance, no semantic task or recovery promised.
            result = self.backend.manager(['mente-unificada-continuar', '--vida', self.life,
                '--id', request_id, '--ticks', str(ticks), '--esperar', str(self.config['material_wait_seconds'])])
            row = result.get('request') or result
            if row.get('status') in self.entry.TERMINAL:
                if row.get('id') != request_id or row.get('payload_sha') != self.session.state['pending_material']['payload_sha256']:
                    raise ValueError('Avance devolvió otra identidad/carga; pendiente preservado sin reintento.')
                self.session.state['pending_material'] = None
                self.session.state['uncertain_preserved'] = row['status'] == 'uncertain'
                self.session.save_protocol()
            self.session.log('literal_dynamic_rest_result', id=request_id, result=result)
            return {'INSTRUMENTO': 'Evolución dinámica sin nuevas tareas; fuentes heredadas permanecen.', 'native_transport': result}
        if action == 'resultado': return self.session.result()
        if action == 'ensenar':
            form = str(value.get('forma', ''))
            sign = int(value.get('senal'))
            if form not in FORMS: raise LookupError('Forma no registrada; no se envió una experiencia.')
            if sign not in (-1, 1): raise ValueError('Docencia explícita requiere señal -1 o +1.')
            command = ('ensenar-ecosistema' if form in ('clasifica', 'equilibra') else
                       'ensenar-nueva' if form in ('luma', 'nara') else 'ensenar')
            text = command + ' ' + form + ' ' + str(sign) + (' --revision' if value.get('revision') else '')
        else: text = str(value.get('texto', ''))
        rows, feedback, actuator = literal_command(text, self.entry)
        return self.session.material(rows, feedback, actuator, request_id=value.get('id'))

    def frame_home(self):
        try: return self.backend.state_root / 'servicios_persistentes' / self.backend.record(self.life)['world_id'] / 'genesis_observador'
        except (FileNotFoundError, KeyError): return None

    def status(self):
        card, owner = None, None
        try:
            card = self.backend.record(self.life)
            owner = self.backend.manager(['mente-unificada-estado', '--vida', self.life])
        except FileNotFoundError: pass
        observer = None
        if card:
            from app.cola_local import QueueDB
            database = self.backend.state_root / 'servicios_persistentes' / card['world_id'] / 'cola.sqlite3'
            if database.is_file(): observer = QueueDB(database).get_meta('genesis_observer')
        with self.mutex:
            return {'version': VERSION, 'engine': 'DEE thinking 4.5.0 / Universe v27 congelados',
                'life_id': self.life, 'record': card, 'owner': owner, 'owned_by_this_app': self.session.owned,
                'pending': self.session.state.get('pending_material'), 'uncertain': self.session.state.get('uncertain_preserved'),
                'passive_observer': observer,
                'recording': self.recording, 'events': list(self.events), 'jobs': [dict(row) for row in list(self.jobs.values())[-20:]],
                'presentation': dict(self.presentation),
                'viewer_only': self.viewer_only,
                'forms': list(FORMS), 'selected_parent': {k: self.config.get(k) for k in ('source_life', 'source_tick', 'source_snapshot_sha256')},
                'attribution': 'INTERFAZ prepared; native responses preserved. No LLM or external decision policy.',
                'repertoire_scope': 'Recorded finite forms, not a material probe or present semantic mastery guarantee.'}

    def frame(self):
        home = self.frame_home()
        if home is None:
            return {'available': False, 'detail': 'Todavía no hay captura coherente del propietario; no se crea un Runtime para dibujar.'}
        from app.cola_local import QueueDB
        database = home.parent / 'cola.sqlite3'
        value = QueueDB(database).get_meta('genesis_frame') if database.is_file() else None
        if value is None:
            return {'available': False, 'detail': 'Todavía no hay captura coherente publicada por SQLite; no se abre otro Runtime ni se lee un snapshot.'}
        value['available'] = True
        value['age_seconds'] = max(0, (datetime.now(timezone.utc) - datetime.fromisoformat(value['captured_utc'])).total_seconds())
        key = value.get('captured_utc')
        if self.record_stream and key != self.last_recorded_frame:
            self.event('passive_frame', frame=value)
            self.last_recorded_frame = key
        return value

    def configure_view(self, value):
        if self.viewer_only:
            raise PermissionError('La configuración del observador externo está congelada por su propietario.')
        allowed = {'enabled', 'interval_seconds', 'max_points', 'coordinate', 'universe'}
        if not isinstance(value, dict) or set(value) - allowed: raise ValueError('Configuración del visor fuera de contrato.')
        home = self.frame_home()
        if home is None: raise RuntimeError('Abra una copia antes de configurar su observador.')
        from app.cola_local import QueueDB
        QueueDB(home.parent / 'cola.sqlite3').meta('genesis_view_config', value)
        return {'INSTRUMENTO': 'Configuración pasiva; no entrada DEE.', 'configuration': value}

    def configure_presentation(self, value):
        """Bounded local camera/display controls; no state or task transformation."""
        allowed = {'yaw', 'pitch', 'zoom', 'field', 'coordinate', 'sections', 'label', 'focus'}
        if not isinstance(value, dict) or set(value) - allowed:
            raise ValueError('Presentation keys outside passive display contract.')
        for key, low, high in (('yaw', -10, 10), ('pitch', -1.5, 1.5), ('zoom', .35, 4)):
            if key in value and (type(value[key]) not in (float, int) or not low <= value[key] <= high):
                raise ValueError('Camera value outside its display bounds.')
        if 'field' in value and value['field'] not in {'semantic', 'state', 's_reg', 'direction', 'clock', 'changed'}:
            raise ValueError('Unknown projected field.')
        if 'coordinate' in value and (not isinstance(value['coordinate'], list) or len(value['coordinate']) != 3 or
                any(type(v) is not int or not 0 <= v < 67 for v in value['coordinate'])):
            raise ValueError('Display coordinate outside N67.')
        if 'sections' in value and (not isinstance(value['sections'], list) or
                any(v not in {'teaching', 'versions', 'continuity', 'attribution'} for v in value['sections'])):
            raise ValueError('Unknown display section.')
        if 'label' in value and (not isinstance(value['label'], str) or len(value['label']) > 180):
            raise ValueError('Bounded operator caption required.')
        if 'focus' in value and value['focus'] not in {'top', 'events', 'cell', 'world', 'command'}:
            raise ValueError('Unknown passive display focus.')
        with self.mutex:
            self.presentation.update(value)
            self.presentation['revision'] += 1
        return {'INSTRUMENTO': 'Passive presentation; no Native input, timing or response selection.',
                'presentation': dict(self.presentation)}

    def toggle_recording(self):
        if self.record_stream:
            self.event('recording_closed', replay_is_not_live=True)
            self.record_stream.close(); self.record_stream = None; self.recording = False
            return {'recording': False, 'file': str(self.record_file.relative_to(ROOT)), 'format': 'gzip JSONL exact events/frames; no MP4 encoder invoked'}
        directory = self.home / 'grabaciones'
        directory.mkdir(parents=True, exist_ok=True)
        self.record_file = directory / ('SESION_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '_' + uuid.uuid4().hex[:8] + '.jsonl.gz')
        self.record_stream = gzip.open(self.record_file, 'xt', encoding='utf8', newline='\n', compresslevel=6)
        self.recording = True
        self.event('recording_started', format='gzip JSONL synchronized event replay, not live video',
            maximum_compressed_bytes=32000000)
        return {'recording': True, 'file': str(self.record_file.relative_to(ROOT))}

    def export_continuity(self):
        status = self.status()
        frame = self.frame()
        identity = {'version': VERSION, 'life_id': self.life, 'state': status,
            'latest_frame': {k: frame.get(k) for k in ('tick', 'N', 'captured_utc', 'RAW_sha256', 'clocks_sha256', 'counts')},
            'not_a_restorable_mind_copy': True, 'complete_native_and_transport_state_remain_local': True,
            'manual': [p.name for p in ROOT.glob('*Manual_Maestro*1_*.docx')],
            'continue_command': 'ABRIR_DEE_COGNITIVE.bat', 'same_pending_id_only': True}
        output = self.home / 'continuidad'
        output.mkdir(parents=True, exist_ok=True)
        path = output / ('GENESIS_CONTINUIDAD_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '_' + uuid.uuid4().hex[:6] + '.zip')
        summary = ('DEE Cognitive 2.0 — contexto exportado, no snapshot restaurable\n\nVida: ' + self.life +
            '\nContinuar con ABRIR_DEE_COGNITIVE.bat en ESTA computadora. La aplicación conserva el puntero personal.\n'
            'Una conversación nueva no tiene acceso automático a Windows. Los diarios no alimentan respuestas del ente.\n')
        with zipfile.ZipFile(path, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr('LEER_PRIMERO.txt', summary)
            archive.writestr('CONTINUIDAD.json', json.dumps(identity, ensure_ascii=False, indent=2))
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None: raise ValueError('Exportación de continuidad ilegible.')
        return {'file': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'restorable': False}

    def close(self):
        try:
            if self.session.owned: self.session.close()
        finally:
            if self.session_lock: self.session_lock.__exit__(None, None, None); self.session_lock = None
            if self.record_stream: self.record_stream.close(); self.record_stream = None


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False


def handler(app, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass
        def valid_host(self):
            return self.headers.get('Host', '').split(':')[0] in {'127.0.0.1', 'localhost'}
        def send(self, code, value, mime='application/json; charset=utf-8'):
            data = value if isinstance(value, bytes) else json.dumps(exact_json(value), ensure_ascii=False, allow_nan=False).encode()
            self.send_response(code); self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data))); self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'")
            self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            if not self.valid_host(): return self.send(403, {'error': 'Local host only.'})
            path = self.path.split('?')[0]
            try:
                if path == '/api/status': return self.send(200, app.status())
                if path == '/api/frame': return self.send(200, app.frame())
                if path == '/api/session': return self.send(200, {'token': token, 'version': VERSION, 'application_root': str(ROOT)})
                if path in {'/', '/index.html', '/app.js', '/style.css'}:
                    name = 'index.html' if path == '/' else path[1:]
                    mime = 'text/html; charset=utf-8' if name.endswith('.html') else 'text/javascript; charset=utf-8' if name.endswith('.js') else 'text/css; charset=utf-8'
                    return self.send(200, (HERE / name).read_bytes(), mime)
                return self.send(404, {'error': 'Not found.'})
            except Exception as error: return self.send(500, {'error': {'type': type(error).__name__, 'detail': str(error)}})
        def do_POST(self):
            if not self.valid_host() or self.headers.get('X-Genesis-Token') != token:
                return self.send(403, {'error': 'Local session token required.'})
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host'):
                return self.send(403, {'error': 'Cross-origin operations denied.'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 16384: return self.send(413, {'error': 'Bounded JSON required.'})
                value = json.loads(self.rfile.read(length))
                if self.path == '/api/shutdown':
                    if app.session.owned or app.work.unfinished_tasks:
                        return self.send(409, {'error': 'Detenga y confirme primero el propietario; no se mata un futuro activo.'})
                    self.send(200, {'interface_shutdown_requested': True, 'native_owner_was_already_stopped': True})
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                    return
                if self.path == '/api/view': return self.send(200, app.configure_view(value))
                if self.path == '/api/presentation': return self.send(200, app.configure_presentation(value))
                if self.path == '/api/action': return self.send(202, app.submit(value['action'], value.get('value')))
                return self.send(404, {'error': 'Not found.'})
            except PermissionError as error:
                return self.send(403, {'error': {'type': type(error).__name__, 'detail': str(error)}})
            except (ValueError, LookupError, KeyError, queue.Full) as error:
                return self.send(400, {'error': {'type': type(error).__name__, 'detail': str(error)}})
            except Exception as error: return self.send(500, {'error': {'type': type(error).__name__, 'detail': str(error)}})
    return Handler


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    lives = p.add_mutually_exclusive_group()
    lives.add_argument('--vida'); lives.add_argument('--nueva')
    p.add_argument('--diagnostico', action='store_true', help='Puntero GUI separado; nunca reemplaza la copia personal predeterminada.')
    p.add_argument('--solo-visor', action='store_true', help='Lee WAL del propietario externo; no importa ni administra un Runtime.')
    p.add_argument('--mundo', help='Pertenencia exacta declarada para --solo-visor.')
    p.add_argument('--seleccion', type=Path)
    p.add_argument('--puerto', type=int, default=8884)
    p.add_argument('--sin-navegador', action='store_true')
    a = p.parse_args(argv)
    # A second click reopens this same local application, not another world.
    connection = http.client.HTTPConnection('127.0.0.1', a.puerto, timeout=1)
    try:
        connection.request('GET', '/api/session')
        existing = json.loads(connection.getresponse().read())
        if (str(existing.get('version', '')).startswith('DEE.Cognitive.2.0.local.')
                and existing.get('application_root') == str(ROOT)):
            connection.request('GET', '/api/status')
            current = json.loads(connection.getresponse().read())
            desired = a.vida or a.nueva
            if desired and current.get('life_id') != desired:
                raise RuntimeError('Ya hay otra vida seleccionada en este puerto; no se sustituye ni se inicia otro propietario.')
            if bool(current.get('viewer_only')) != bool(a.solo_visor):
                raise RuntimeError('El puerto pertenece a otro modo de DEE Cognitive; use otro --puerto, no se sustituye su propietario.')
            url = 'http://127.0.0.1:' + str(a.puerto)
            print('Misma aplicación local ya abierta: ' + url, flush=True)
            if not a.sin_navegador: webbrowser.open(url)
            return
    except (OSError, ValueError, http.client.HTTPException):
        pass
    finally:
        connection.close()
    entry = bootstrap()
    # Bound this web process plus the owned process tree. The Native owner's
    # existing separate Job retains its stricter 512 MiB bound.
    from app.process_control import protect_current
    protect_current(memory_limit=1073741824)
    app = Genesis(entry, a.vida or a.nueva, a.seleccion, new=bool(a.nueva), diagnostic=a.diagnostico,
                  viewer_only=a.solo_visor, world_id=a.mundo)
    token = uuid.uuid4().hex + uuid.uuid4().hex
    # A second click may open the same valid existing application; never silently
    # bind another owner or kill a stranger who happens to occupy this port.
    server = LocalServer(('127.0.0.1', a.puerto), handler(app, token))
    url = 'http://127.0.0.1:' + str(a.puerto)
    print('DEE Cognitive 2.0 ' + VERSION + '\n' + url + '\nVida personal seleccionada: ' + app.life, flush=True)
    if not a.sin_navegador: webbrowser.open(url)
    try: server.serve_forever(poll_interval=.25)
    except KeyboardInterrupt: pass
    finally:
        server.server_close()
        app.close()


if __name__ == '__main__':
    try: main()
    except Exception as error:
        print(type(error).__name__ + ': ' + str(error), file=sys.stderr)
        raise SystemExit(2)
