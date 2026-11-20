"""Authenticated loopback bridge to one actual official Native owner.

No Studio, MCP, Codex, policy, calculator or kernel import at module import.
POST admits a durable ID once. GET polls; ambiguous material is never retried.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import argparse
import hashlib
import hmac
import importlib.util
import json
import os
import queue
import threading
import time
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sdk_common import (RUNTIME, SCHEMA, IDENTIFIER, atomic, budget, canonical,
                        closed_native, digest, instance_home, native_payload, operational_window, read, safe, sha, validate_pair)
from resource_wait import (BOOT_FREE_BYTES, PHASE_FREE_BYTES, wait_for_resource,
                           ResourceUnavailableBeforeNative, ResourceWaitExpired)
from restoration_contract import FIELDS, expected_view, compare as compare_restoration

MAX_REQUEST = 5 * 1024 * 1024

class Conflict(RuntimeError): pass

class Service:
    def __init__(self, instance_id, *, runtime=RUNTIME, factory=None, token=None, mode=None, memory=None):
        self.runtime = Path(runtime).resolve(strict=True)
        self.home, self.cfg = instance_home(instance_id, self.runtime)
        if mode not in ('new', 'continue'): raise ValueError('Explicit new or continue mode required')
        self.mode=mode; self.restoration_verified=mode=='new'
        paired = (self.home / 'SDK_PAIR.json').is_file()
        if mode == 'new' and (paired or self.cfg['localSequence'] != 0): raise Conflict('NEW cannot reuse an advanced instance')
        if mode == 'continue' and (not paired or self.cfg['localSequence'] == 0): raise Conflict('CONTINUE requires an actual sealed pair')
        if mode == 'continue': validate_pair(self.home, self.cfg)
        self.instance_id = instance_id
        self.window = operational_window(self.cfg, self.runtime)
        self.token = token or read(safe(self.runtime, 'configuracion/CONEXION_PRIVADA.json', exists=True))['token']
        if not isinstance(self.token, str) or len(self.token) < 32: raise ValueError('Private token required')
        self.store = self.home / 'http_operations'; self.store.mkdir(exist_ok=True)
        self.lock_path = self.home / 'SDK_SERVICE.lock'
        self.lease_fd = os.open(self.lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(self.lease_fd, canonical({'pid': os.getpid(), 'instanceId': instance_id, 'started': time.time()}).encode())
        os.fsync(self.lease_fd)
        self.lock = threading.RLock(); self.work = queue.Queue(); self.status = 'STARTING'
        self.owner = None; self.adapter = None; self.factory = factory
        if memory is None:
            from native_factory import free_memory
            memory = free_memory
        self.memory = memory; self.resource_wait = None
        self.phase = self.cfg.get('nextPhase', 'decision')
        self.native_tick = self.cfg.get('nativeTick', 991187)
        self.local_sequence = self.cfg.get('localSequence', 0)
        self.session_id = self.cfg['sessionId']; self.last_output = None
        self.acks = read(self.home / 'ACTION_ACKS.json') if (self.home / 'ACTION_ACKS.json').exists() else {}
        self.backend_proof = None; self.last_error = None
        self.stop_requested = False
        prior = []
        for file in self.store.glob('*.json'):
            row = read(file)
            if row['status'] in ('PENDING', 'PENDING_RESOURCE', 'RUNNING', 'UNCERTAIN'): prior.append(row['operationId'])
        if prior:
            self.status = 'PRESERVED_UNCERTAIN'; self.last_error = {'code': 'RECONCILIATION_REQUIRED', 'operations': prior}
            self.thread = None
        else:
            self.thread = threading.Thread(target=self.worker, name='SDK-single-Native-writer', daemon=False)
            self.thread.start()

    def check_common(self, body):
        if not isinstance(body, dict) or body.get('instanceId') != self.instance_id or body.get('sessionId') != self.session_id:
            raise Conflict('Instance/session mismatch')
        op = body.get('operationId')
        if not isinstance(op, str) or IDENTIFIER.fullmatch(op) is None: raise ValueError('Finite operation ID required')
        return op

    def operation(self, op):
        if IDENTIFIER.fullmatch(op) is None: raise ValueError('Invalid operation ID')
        path = self.store / (op + '.json')
        if not path.is_file():path=self.home/'restoration_proofs'/(op+'.json')
        if not path.is_file(): raise KeyError('Unknown operation ID')
        row = read(path)
        return {k: row[k] for k in ('operationId', 'status', 'kind', 'value', 'error',
                                  'nativeAdmissionStarted', 'resourceWait') if k in row}

    def submit(self, kind, body):
        op = self.check_common(body)
        expected = {'instanceId', 'operationId', 'sessionId'} | ({'payload'} if kind != 'close' else set())
        if set(body) != expected: raise ValueError('Exact SDK operation DTO required')
        request_sha = digest({'kind': kind, 'body': body}); path = self.store / (op + '.json')
        with self.lock:
            if path.exists():
                prior = read(path)
                if prior['requestSha256'] != request_sha: raise Conflict('Operation ID payload changed')
                # Return the existing durable status, never queue it again.
                return self.operation(op)
            if self.status != 'READY': raise Conflict('Native service is not ready; preserve current state')
            if kind=='decision' and not self.restoration_verified:
                raise Conflict('Persist complete K4 restoration proof before the first continued decision')
            if kind != 'close' and kind != self.phase: raise Conflict('Native phase mismatch')
            if kind == 'decision' and time.time() >= self.window['lastNewUtcEpoch']: raise Conflict('Last new episode cutoff reached')
            if kind != 'close' and self.last_output is not None:
                if self.last_output['operationId'] not in self.acks: raise Conflict('Actual action ACK required before next phase')
            if any(read(p)['status'] in ('PENDING', 'PENDING_RESOURCE', 'RUNNING', 'UNCERTAIN') for p in self.store.glob('*.json')):
                raise Conflict('Only one admitted Native operation per instance')
            if kind == 'close' and self.phase != 'decision': raise Conflict('Close only at completed episode boundary')
            native = None
            if kind != 'close':
                native, local, oid = native_payload(kind, body['payload'], self.cfg['sequenceOffset'])
                expected_local = self.local_sequence + (1 if kind in ('decision', 'query_sensor') else 0)
                if kind == 'feedback': expected_local = self.local_sequence
                if local != expected_local: raise Conflict('Local sequence does not continue actual cursor')
                if kind == 'feedback':
                    if self.last_output is None or body['payload']['actionId'] != self.last_output['operationId']:
                        raise Conflict('Feedback must acknowledge actual last Native output')
                context = {'session_id': self.session_id, 'sequence': native.get('seq', native.get('observation', {}).get('seq')),
                           'observation_id': oid, 'operation_id': op, 'mode': 'LIVE_NATIVE'}
            row = {'schema': SCHEMA, 'operationId': op, 'kind': kind, 'requestSha256': request_sha,
                   'status': 'PENDING', 'body': body, 'admittedUtcEpoch': time.time(),
                   'nativeAdmissionStarted': False}
            if native is not None: row.update(nativePayload=native, nativeContext=context, localSequence=local)
            atomic(path, row, new=True); self.work.put(op)
            return self.operation(op)

    def ack(self, body):
        op = self.check_common(body)
        if set(body) != {'instanceId', 'operationId', 'sessionId', 'actionId', 'observationId', 'localSequence', 'ack'}:
            raise ValueError('Exact actual action ACK DTO')
        with self.lock:
            action = body['actionId']
            native = read(self.store / (action + '.json'))
            if native['status'] != 'COMPLETED' or native['kind'] not in ('decision', 'query_sensor'):
                raise Conflict('ACK only an actual completed Native action')
            if native['localSequence'] != body['localSequence'] or native['nativeContext']['observation_id'] != body['observationId']:
                raise Conflict('ACK observation/sequence mismatch')
            # ACK is preserved literally; it is never synthesized by the service.
            if not isinstance(body['ack'], dict): raise ValueError('Actual connector ACK object')
            ack = body['ack']
            if (ack.get('protocol') != 'DEE.RBX.Connector.R01' or ack.get('sessionId') != self.session_id
                    or ack.get('actionId') != action or ack.get('operationId') != action
                    or ack.get('observationId') != body['observationId'] or ack.get('seq') != body['localSequence']
                    or ack.get('executionStatus') != 'EXECUTED' or ack.get('technicalControl') is not False
                    or not isinstance(ack.get('result'), dict)):
                raise Conflict('Exact actual Native connector execution ACK required')
            prior = self.acks.get(action)
            if prior is not None and prior != body: raise Conflict('ACK bytes changed')
            self.acks[action] = body; atomic(self.home / 'ACTION_ACKS.json', self.acks)
            return {'status': 'ACKNOWLEDGED', 'actionId': action}

    def handshake(self):
        pair = read(self.home / 'SDK_PAIR.json') if (self.home / 'SDK_PAIR.json').exists() else None
        return {'instanceId': self.instance_id, 'sessionId': self.session_id, 'lifeId': self.cfg['lifeId'],
                'nativeTick': self.native_tick, 'sequenceOffset': self.cfg['sequenceOffset'],
                'localSequence': self.local_sequence, 'initialPublicState': self.cfg['initialPublicState'],
                'sourceWorldSha256': self.cfg['sourceWorldSha256'], 'protocolVersion': 'DEE.RBX.Connector.R01',
                'runtimeVersion': '0.1.1', 'backendKind': 'NATIVE_REAL', 'technicalControl': False,
                'snapshot': None if pair is None else pair['snapshot'],
                'backendProof': None if pair is None else pair['backendProof'],
                'checkpointSha256': None if pair is None else pair['snapshotSha256'],
                'pairSha256': None if pair is None else sha(self.home/'SDK_PAIR.json'),
                'completedCycles': self.cfg.get('completedCycles', 0),
                'acknowledgedActionIds': sorted(self.acks),
                'lastNewUtcEpoch': self.window['lastNewUtcEpoch'],
                'hardFinishUtcEpoch': self.window['hardFinishUtcEpoch'],
                'status': self.status, 'resourceWait': self.resource_wait,
                'hostRevision': 'R06', 'nativeCodeUnchanged': True,
                'restorationProofRequired': self.mode=='continue',
                'restorationProofRecorded': self.restoration_verified}

    def status_value(self):
        return {'instanceId': self.instance_id, 'sessionId': self.session_id, 'status': self.status,
                'nextPhase': self.phase, 'nativeTick': self.native_tick, 'localSequence': self.local_sequence,
                'backendWriterClosed': self.owner is None, 'lastError': self.last_error,
                'resourceWait': self.resource_wait, 'hostRevision': 'R06',
                'restorationProofRecorded':self.restoration_verified}

    def restoration_proof(self, body):
        """Authenticated technical evidence only; never calls Native or observes."""
        op=self.check_common(body)
        if set(body)!={'instanceId','operationId','sessionId','checkpointSha256','pairSha256','proof'}:
            raise ValueError('Exact restoration-proof DTO required')
        with self.lock:
            pairpath=self.home/'SDK_PAIR.json';pair=read(pairpath);pair_sha=sha(pairpath)
            request_sha=digest(body);folder=self.home/'restoration_proofs';folder.mkdir(exist_ok=True)
            path=folder/(op+'.json')
            if (self.store/(op+'.json')).exists():raise Conflict('Restoration ID collides with a Native operation')
            if path.exists():
                prior=read(path)
                if prior['requestSha256']!=request_sha or prior['pairSha256']!=pair_sha:
                    raise Conflict('Restoration proof ID or paired bytes changed')
                if prior['status']!='RECORDED':raise Conflict('Prior restoration mismatch remains preserved')
                self.restoration_verified=True;return prior['value']
            if (self.mode!='continue' or self.status!='READY' or self.phase!='decision' or not self.work.empty()
                    or any(read(p)['status'] in ('PENDING','PENDING_RESOURCE','RUNNING','UNCERTAIN') for p in self.store.glob('*.json'))):
                raise Conflict('Restoration proof only at the untouched continued boundary')
            if body['pairSha256']!=pair_sha or body['checkpointSha256']!=pair['snapshotSha256']:
                raise Conflict('Actual current pair and snapshot hashes required')
            if digest(pair['snapshot'])!=pair['snapshotSha256']:raise Conflict('Paired World bytes changed')
            proof=body['proof'];actual=proof.get('actual') if isinstance(proof,dict) else None
            if (not isinstance(actual,dict) or set(actual)!=set(FIELDS)
                    or proof.get('schema')!='DEE.RBX.RestorationProof.R06' or proof.get('poseTolerance')!=1e-5):
                raise ValueError('Complete literal eight-field restoration evidence required')
            expected=expected_view(pair['snapshot']);comparison=compare_restoration(expected,actual)
            state=actual['state']
            cursor_ok=(state.get('sessionId'),state.get('lifeId'),state.get('nativeTick'),state.get('sequence'),
                       state.get('completedOpportunities'),state.get('phase'))==(
                self.session_id,self.cfg['lifeId'],self.native_tick,self.local_sequence,
                self.cfg['completedCycles'],'BOUNDARY')
            ledger=[]
            wanted=list(self.acks)
            feedback=state.get('lastFeedbackOperationId')
            if not isinstance(feedback,str):raise ValueError('Actual saved feedback operation ID required')
            wanted.append(feedback)
            for identifier in sorted(set(wanted)):
                value=self.operation(identifier)
                ledger.append(value)
                if value['status']!='COMPLETED':cursor_ok=False
            ok=(comparison['passed'] and cursor_ok and proof.get('ok') is True and
                proof.get('differenceCount')==0 and proof.get('differences')==[] and
                compare_restoration(expected,proof.get('expected'))['passed'])
            row={'schema':SCHEMA,'operationId':op,'kind':'restoration_proof','requestSha256':request_sha,
                 'pairSha256':pair_sha,'checkpointSha256':body['checkpointSha256'],'body':body,
                 'serverComparison':comparison,'serverCursorMatched':cursor_ok,'serverLedgerCheck':ledger,
                 'nativeAdmissionStarted':False,'recordedUtcEpoch':time.time(),
                 'status':'RECORDED' if ok else 'REJECTED'}
            checksum=digest(row)
            row['value']={'operationId':op,'status':row['status'],'restorationProofSha256':checksum,
                          'checkpointSha256':body['checkpointSha256']}
            atomic(path,row,new=True)
            if not ok:raise Conflict('Complete original restoration comparison failed; evidence preserved')
            self.restoration_verified=True;return row['value']

    def stop_failed(self, body):
        """Administrative exit of a known failed boot; never stops a live owner."""
        op = self.check_common(body)
        if set(body) != {'instanceId','operationId','sessionId'}: raise ValueError('Exact failed-boot close DTO')
        with self.lock:
            if (self.status != 'FAILED_PRESERVED' or self.owner is not None
                    or self.thread is not None and self.thread.is_alive() or not self.work.empty()):
                raise Conflict('Only failed service with dead worker/no owner/no queued work')
            states = [read(p) for p in self.store.glob('*.json')]
            if any(r['status'] in ('PENDING','PENDING_RESOURCE','RUNNING','UNCERTAIN') for r in states):
                raise Conflict('Pending or uncertain operation must remain preserved')
            ledger = read(self.runtime / 'estado_demo/LEDGER_SDK_R06.json')
            if ledger['intents']: raise Conflict('Native intents prevent administrative exit')
            proof = closed_native(self.home, self.cfg)
            if proof['nativeTick'] != self.native_tick or proof['writerClosed'] is not True or proof['pending'] != 0:
                raise Conflict('Exact current closed Native proof required')
            result = {'schema': SCHEMA, 'operationId': op, 'kind': 'FAILED_BOOT_ADMIN_CLOSE',
                'instanceId': self.instance_id, 'sessionId': self.session_id, 'serverPid': os.getpid(),
                'statusPreserved': self.status, 'errorPreserved': self.last_error, 'native': proof,
                'newNativeTicks': 0, 'materialOperationsRetried': 0, 'closedUtcEpoch': time.time()}
            atomic(self.home / ('SERVER_BOOT_FAILURE_' + op + '.json'), result, new=True)
            self.stop_requested = True
            return result

    def wait_resource(self, required, *, row=None, path=None, fixed_deadline=None):
        deadline = self.window['hardFinishUtcEpoch']
        if row is None or row['kind'] == 'decision':
            deadline = min(deadline, self.window['lastNewUtcEpoch'])
        if fixed_deadline is not None: deadline = min(deadline, fixed_deadline)
        if row is not None:
            row.setdefault('resourceDeadlineUtcEpoch', min(time.time()+900, deadline))
            deadline = min(deadline, row['resourceDeadlineUtcEpoch'])
        def sample(value):
            with self.lock:
                self.resource_wait = value
                if value['free'] < required:
                    self.status = 'PENDING_RESOURCE'
                    if row is not None:
                        row.update(status='PENDING_RESOURCE', nativeAdmissionStarted=False,
                                   resourceWait=value)
                        atomic(path, row)
        value = wait_for_resource(required, deadline_utc=deadline, memory=self.memory, on_sample=sample)
        with self.lock:
            self.resource_wait = None; self.status = 'READY' if self.owner is not None else 'STARTING'
        return value

    def worker(self):
        manager = None
        try:
            if self.factory is None:
                from native_factory import create_session
                self.factory = create_session
            boot_deadline = time.time()+900
            while True:
                self.wait_resource(BOOT_FREE_BYTES, fixed_deadline=boot_deadline)
                try:
                    manager, self.adapter = self.factory(self.home, self.cfg, self.window)
                    break
                except ResourceUnavailableBeforeNative:
                    continue  # Factory has not entered or created a Native owner.
            self.owner = manager.__enter__(); self.status = 'READY'
            while True:
                remaining = self.window['hardFinishUtcEpoch'] - time.time()
                if remaining <= 0: raise RuntimeError('Finite SDK host deadline reached')
                try: op = self.work.get(timeout=min(1, remaining))
                except queue.Empty: continue
                path = self.store / (op + '.json'); row = read(path)
                try:
                    if row['kind'] == 'close':
                        row.update(status='RUNNING', startedUtcEpoch=time.time(), nativeAdmissionStarted=False)
                        atomic(path, row)
                        manager.__exit__(None, None, None); manager = None; self.owner = None
                        proof = closed_native(self.home, self.cfg)
                        proof.update(sessionId=self.session_id, backendWriterClosed=True, bridgeQuiescent=True,
                                     localSequence=self.local_sequence, closedUtcEpoch=time.time())
                        proof['proofSha256'] = digest(proof); self.backend_proof = proof
                        atomic(self.home / 'BACKEND_CLOSED.json', proof)
                        value = {'backendProof': proof}; self.status = 'CLOSED'
                    else:
                        while True:
                            self.wait_resource(PHASE_FREE_BYTES, row=row, path=path)
                            row.update(status='RUNNING', startedUtcEpoch=time.time(), nativeAdmissionStarted=True)
                            atomic(path, row)
                            try:
                                value = self.adapter.execute(row['kind'], row['nativePayload'], row['nativeContext'])
                                break
                            except ResourceUnavailableBeforeNative:
                                # This typed exception is raised exclusively before actual.execute.
                                # No Native queue admission or ledger intent has occurred.
                                row.update(status='PENDING_RESOURCE', nativeAdmissionStarted=False)
                                atomic(path, row)
                                continue
                        self.native_tick = value['nativeTick']; self.local_sequence = row['localSequence']
                        if row['kind'] in ('decision', 'query_sensor'):
                            self.last_output = {'operationId': op, 'value': value}
                            # Q1 may return no releasable route. Native feedback still completes the existing episode.
                            self.phase = 'query_sensor' if row['kind'] == 'decision' and value.get('action') != 'SAFE_WAIT' else 'feedback'
                        else:
                            self.phase = 'decision'; self.last_output = None
                            self.cfg['completedCycles'] = self.cfg.get('completedCycles', 0) + 1
                        self.cfg.update(nativeTick=self.native_tick, localSequence=self.local_sequence, nextPhase=self.phase)
                        atomic(self.home / 'INSTANCE.json', self.cfg)
                    row.update(status='COMPLETED', value=value, completedUtcEpoch=time.time()); atomic(path, row)
                    if row['kind'] == 'close': break
                except ResourceWaitExpired as error:
                    row.update(status='FAILED_KNOWN', nativeAdmissionStarted=False,
                               error={'code': 'RESOURCE_WAIT_EXPIRED', 'message': str(error),
                                      'preNativeAdmissionGuaranteed': True}, failedUtcEpoch=time.time())
                    atomic(path, row); self.status='FAILED_PRESERVED'; self.last_error=row['error']; break
                except BaseException as error:
                    # A durable Native request may exist. Classify conservatively and never requeue.
                    row.update(status='UNCERTAIN', error={'code': 'PRESERVED_NO_REPLAY', 'message': str(error)}, failedUtcEpoch=time.time())
                    atomic(path, row); self.status = 'PRESERVED_UNCERTAIN'; self.last_error = row['error']; break
        except BaseException as error:
            self.status = 'FAILED_PRESERVED'; self.last_error = {'code': 'OWNER_START_OR_CLOSE_FAILED', 'message': str(error)}
        finally:
            if manager is not None:
                try: manager.__exit__(None, None, None)
                except BaseException as error:
                    self.status = 'PRESERVED_UNCERTAIN'; self.last_error = {'code': 'CLOSE_UNCERTAIN', 'message': str(error)}
            self.owner = None

    def seal(self, body):
        op = self.check_common(body)
        if set(body) != {'instanceId', 'operationId', 'sessionId', 'snapshot'}: raise ValueError('Exact checkpoint DTO')
        with self.lock:
            if self.status != 'CLOSED' or self.backend_proof is None: raise Conflict('Close official Native before Agent.capture')
            snapshot = body['snapshot']
            state = snapshot.get('state', {})
            if state.get('sessionId') != self.session_id or state.get('lifeId') != self.cfg['lifeId'] or state.get('nativeTick') != self.native_tick:
                raise Conflict('Agent/Native closed pair identity or tick mismatch')
            if state.get('sequence') != self.local_sequence: raise Conflict('Agent cursor differs from actual Native sequence')
            if state.get('completedOpportunities') != self.cfg.get('completedCycles', 0):
                raise Conflict('Agent completed opportunities differ from actual Native feedback')
            after = closed_native(self.home, self.cfg)
            for key in ('snapshotSha256', 'databaseSha256', 'cardSha256', 'nativeTick'):
                if after[key] != self.backend_proof[key]: raise Conflict('Native changed after close')
            pair = {'schema': SCHEMA, 'checkpointId': op, 'snapshotSha256': digest(snapshot),
                    'snapshot': snapshot, 'backendProof': self.backend_proof, 'native': after,
                    'sessionId': self.session_id, 'instanceId': self.instance_id, 'localSequence': self.local_sequence,
                    'scope': 'Full Native remains private locally; Agent/World coupled here. No independent rollback claim.'}
            if (self.home / 'SDK_PAIR.json').exists():
                old = read(self.home / 'SDK_PAIR.json')
                archive = self.home / ('SDK_PAIR_' + old['checkpointId'] + '.json')
                if not archive.exists(): atomic(archive, old, new=True)
            atomic(self.home / 'SDK_PAIR.json', pair)
            self.stop_requested = True
            return {'checkpointId': op, 'checkpointSha256': pair['snapshotSha256'], 'nativeTick': self.native_tick, 'status': 'SEALED'}

    def release(self):
        if self.thread is not None and self.thread.is_alive(): raise Conflict('Owner still active; no lease release')
        os.close(self.lease_fd); self.lock_path.unlink()

def handler(service):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'DEE-Local-SDK/0.1.0'
        def log_message(self, *_): pass  # Never put bearer credentials or private bodies in access logs.
        def send(self, status, value):
            data = canonical(value).encode('utf8'); self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(data)))
            self.end_headers(); self.wfile.write(data)
        def authorized(self):
            value = self.headers.get('Authorization', '')
            return hmac.compare_digest(value, 'Bearer ' + service.token)
        def dispatch(self):
            if not self.authorized(): self.send(401, {'ok': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Private loopback token required'}}); return
            parsed = urlsplit(self.path); path = parsed.path
            if self.command == 'GET':
                if path == '/v1/instances/' + service.instance_id + '/handshake': result = service.handshake()
                elif path == '/v1/instances/' + service.instance_id + '/status': result = service.status_value()
                elif path.startswith('/v1/operations/'):
                    if parse_qs(parsed.query).get('instanceId') != [service.instance_id]: raise Conflict('Instance required')
                    result = service.operation(path.removeprefix('/v1/operations/'))
                else: raise KeyError('Unknown SDK route')
                self.send(200, {'ok': True, 'result': result}); return
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= MAX_REQUEST: raise ValueError('Bounded JSON body required')
            body = json.loads(self.rfile.read(length))
            if path.startswith('/v1/native/'):
                result = service.submit(path.removeprefix('/v1/native/'), body); code = 202
            elif path == '/v1/session/close': result = service.submit('close', body); code = 202
            elif path == '/v1/action-ack': result = service.ack(body); code = 200
            elif path == '/v1/checkpoint': result = service.seal(body); code = 200
            elif path == '/v1/restoration-proof': result = service.restoration_proof(body); code = 200
            elif path == '/v1/admin/stop-failed': result = service.stop_failed(body); code = 200
            else: raise KeyError('Unknown SDK route')
            self.send(code, {'ok': True, 'result': result})
        def execute(self):
            try: self.dispatch()
            except Conflict as error: self.send(409, {'ok': False, 'error': {'code': 'PRESERVE_CONFLICT', 'message': str(error)}})
            except KeyError as error: self.send(404, {'ok': False, 'error': {'code': 'NOT_FOUND', 'message': str(error)}})
            except (ValueError, TypeError) as error: self.send(400, {'ok': False, 'error': {'code': 'SCHEMA', 'message': str(error)}})
            except BaseException as error: self.send(500, {'ok': False, 'error': {'code': 'PRESERVE_INTERNAL', 'message': str(error)}})
        do_GET = execute
        do_POST = execute
    return Handler

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--instance', required=True); parser.add_argument('--port', type=int, default=8896)
    parser.add_argument('--mode', choices=('new', 'continue'), required=True)
    parser.add_argument('--start-real-native', action='store_true')
    args = parser.parse_args()
    if not args.start_real_native: parser.error('Explicit --start-real-native required; requirements/status use sdk_cli.py')
    if not 1024 <= args.port <= 65535: parser.error('Unprivileged loopback port')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), BaseHTTPRequestHandler)
    server.timeout = 1
    service = None
    try:
        service = Service(args.instance, mode=args.mode)
        server.RequestHandlerClass = handler(service)
        while time.time() < service.window['hardFinishUtcEpoch'] and not service.stop_requested:
            server.handle_request()
    finally:
        server.server_close()
        if service is not None:
            if service.thread is not None: service.thread.join(timeout=650)
            service.release()

if __name__ == '__main__': main()
