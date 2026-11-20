"""A fixed operator's HTTP itinerary, not an actor policy or a DEE solver.

No action is run on import. --validar only checks the immutable JSON plan.
Every POST is logged before transmission and sent ONCE. A timeout preserves the
ID and aborts; this program never retries material or picks another future.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SCHEMA = 'DEE20.fixed_operator_http_itinerary.v1'
ACTIONS = {'abrir', 'vivir', 'pausar', 'guardar', 'detener', 'ejecutar', 'ensenar',
           'resultado', 'exportar', 'grabar', 'reposo', 'conciliar-propietario'}
KINDS = {'action', 'presentation', 'observe', 'hold', 'session', 'shutdown'}
SAFE_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,90}\Z')


def utc():
    return datetime.now(timezone.utc).isoformat()


def exact_bytes(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':'), sort_keys=True).encode('utf8')


def validate(plan):
    if plan.get('schema') != SCHEMA:
        raise ValueError('Unexpected itinerary schema')
    if not SAFE_ID.fullmatch(plan.get('life_id', '')):
        raise ValueError('An explicit, safe life_id is required')
    steps = plan.get('steps')
    if not isinstance(steps, list) or not 1 <= len(steps) <= 100:
        raise ValueError('The fixed itinerary requires 1..100 steps')
    ids, material_ids = set(), set()
    for step in steps:
        if not isinstance(step, dict) or not SAFE_ID.fullmatch(step.get('id', '')):
            raise ValueError('Every step requires a safe ID')
        if step['id'] in ids:
            raise ValueError('Duplicate step ID: ' + step['id'])
        ids.add(step['id'])
        kind = step.get('kind')
        if kind not in KINDS:
            raise ValueError('Unsupported step kind: ' + str(kind))
        if not isinstance(step.get('group', ''), str):
            raise ValueError('group must be a presentation label')
        deadline = float(step.get('deadline_seconds', 180))
        if not 1 <= deadline <= 300:
            raise ValueError('Bound each job/session deadline to 1..300 seconds')
        hold = float(step.get('hold_seconds', 0))
        if not 0 <= hold <= 30:
            raise ValueError('Fixed readability hold must be 0..30 seconds')
        if kind == 'action':
            payload = step.get('payload')
            if not isinstance(payload, dict) or set(payload) - {'action', 'value'}:
                raise ValueError('action payload is the literal app payload only')
            action = payload.get('action')
            if action not in ACTIONS:
                raise ValueError('Unsupported literal app action')
            value = payload.get('value')
            if action in {'ejecutar', 'ensenar'}:
                if not isinstance(value, dict) or not SAFE_ID.fullmatch(value.get('id', '')):
                    raise ValueError('Material operation needs its explicit transport ID before recording')
                if value['id'] in material_ids:
                    raise ValueError('A transport ID cannot be transmitted twice by this itinerary')
                material_ids.add(value['id'])
        elif kind == 'observe':
            if step.get('path', '/api/status') not in {'/api/status', '/api/frame'}:
                raise ValueError('observe uses only the passive status/frame interfaces')
        elif kind == 'presentation':
            path = step.get('path', '/api/presentation')
            if path not in {'/api/presentation', '/api/view'} or not isinstance(step.get('payload'), dict):
                raise ValueError('presentation needs its exact fixed local endpoint and JSON payload')
        elif kind == 'shutdown' and step.get('payload', {}) != {}:
            raise ValueError('shutdown must not carry hidden task information')
    return {'schema': SCHEMA, 'life_id': plan['life_id'], 'steps': len(steps),
            'explicit_material_ids': sorted(material_ids),
            'operator_schedule_not_actor_initiative': True}


def decode(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            pass
    return value


def concise_status(status):
    record = status.get('record') or {}
    owner = status.get('owner') or {}
    owner = owner.get('observation') or owner
    return {'life_id': status.get('life_id'), 'record_life_id': record.get('life_id'),
            'world_id': record.get('world_id'),
            'tick': (owner.get('physical') or record.get('physical') or {}).get('tick'),
            'record_tick': (record.get('physical') or {}).get('tick'),
            'snapshot_sha256': record.get('snapshot_sha256'),
            'owned': status.get('owned_by_this_app'), 'running': owner.get('running'),
            'paused': owner.get('paused'), 'pending': status.get('pending'),
            'uncertain': status.get('uncertain') or owner.get('uncertain_external_result')}


def concise_result(job):
    value = job.get('result') or {}
    transport = value.get('native_transport') or value
    request = transport.get('request') if isinstance(transport, dict) else None
    result = {'job_id': job.get('id'), 'job_status': job.get('status'),
              'interface_action': job.get('action'), 'error': job.get('error')}
    if isinstance(request, dict):
        native = decode(request.get('result'))
        result.update(transport_id=request.get('id'), transport_status=request.get('status'),
                      payload_sha256=request.get('payload_sha'))
        if isinstance(native, dict):
            result.update(before_tick=native.get('before_tick'), after_tick=native.get('after_tick'),
                          operation=native.get('operation'))
            inner = native.get('result') or {}
            if isinstance(inner, dict):
                result['rows'] = []
                for row in inner.get('rows', []):
                    reader = row.get('reader') or {}
                    result['rows'].append({k: row[k] for k in ('form', 'texto', 'mode', 'modo',
                        'formed_native_command', 'selected', 'value', 'output', 'answer') if k in row})
                    if reader:
                        result['rows'][-1]['reader'] = {k: reader.get(k) for k in
                            ('formed_native_command', 'ambiguous', 'reader_sites') if k in reader}
    elif isinstance(transport, dict):
        result.update(transport_id=transport.get('id'), transport_status=transport.get('status'),
                      admission=transport.get('admission'))
    return result


class Itinerary:
    def __init__(self, base, plan, plan_path, out, max_seconds, capture_utc):
        parsed = urllib.parse.urlsplit(base)
        if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost'} or parsed.path not in {'', '/'}:
            raise ValueError('Only the already-running local app is permitted')
        self.base = base.rstrip('/')
        self.plan, self.plan_path, self.out = plan, plan_path, out
        self.token = None
        self.begun = time.monotonic()
        self.deadline = self.begun + max_seconds
        self.capture_utc = capture_utc
        self.out.mkdir(parents=True, exist_ok=False)
        (self.out / 'resultados').mkdir()
        self.stream = (self.out / 'EVENTOS.jsonl').open('x', encoding='utf8', newline='\n')
        self.posts = 0
        self.terminals = 0

    def event(self, event, **data):
        item = {'utc': utc(), 'monotonic_seconds': time.monotonic(),
                'elapsed_seconds': time.monotonic() - self.begun,
                'capture_started_utc': self.capture_utc, 'event': event, **data}
        self.stream.write(json.dumps(item, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n')
        self.stream.flush()
        return item

    def remaining(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Fixed total operator deadline reached; no retry, reset or replacement life')
        return remaining

    def request(self, path, payload=None):
        self.remaining()
        headers = {}
        body = None
        method = 'GET'
        if payload is not None:
            body = exact_bytes(payload)
            method = 'POST'
            headers = {'Content-Type': 'application/json', 'X-Genesis-Token': self.token or ''}
            self.event('POST_intent_once', path=path, payload=payload,
                       payload_sha256=hashlib.sha256(body).hexdigest(),
                       no_retry_after_uncertain_transport=True)
            self.posts += 1
        request = urllib.request.Request(self.base + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=min(12, self.remaining())) as response:
                value = json.load(response)
        except Exception as error:
            self.event('HTTP_failure_preserved', method=method, path=path,
                       error={'type': type(error).__name__, 'detail': str(error)},
                       material_or_control_POST_not_retried=method == 'POST')
            raise
        return value

    def status(self):
        value = self.request('/api/status')
        if value.get('life_id') != self.plan['life_id']:
            raise ValueError('The local app selected another life; no automatic selection or import')
        record = value.get('record')
        if record and record.get('life_id') != self.plan['life_id']:
            raise ValueError('The published record belongs to another life; abort instead of rerouting')
        return value

    def artifact(self, step, value):
        path = self.out / 'resultados' / (step['id'] + '.json.gz')
        data = exact_bytes(value)
        with path.open('xb') as raw:
            with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=6) as zipped:
                zipped.write(data)
        return {'file': str(path.relative_to(self.out)), 'bytes': path.stat().st_size,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'uncompressed_sha256': hashlib.sha256(data).hexdigest()}

    def connect(self, step):
        # Repeated GETs are bounded transport readiness only. No POST is retried.
        limit = min(self.deadline, time.monotonic() + float(step.get('deadline_seconds', 30)))
        while True:
            try:
                value = self.request('/api/session')
                self.token = value['token']
                status = self.status()
                self.event('session_connected', step=step['id'], version=value.get('version'),
                           token_not_recorded=True, status=concise_status(status))
                return
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                if time.monotonic() >= limit:
                    raise
                time.sleep(min(.5, max(0, limit - time.monotonic())))

    def action(self, step):
        status = self.status()
        if concise_status(status)['uncertain']:
            raise RuntimeError('Preserved uncertain effect; operator does not add another action')
        accepted = self.request('/api/action', step['payload'])
        ident = accepted.get('id')
        if not isinstance(ident, str):
            raise ValueError('POST did not return one job identity; do not resubmit')
        self.event('job_submitted_once', step=step['id'], group=step.get('group'),
                   job_id=ident, accepted=accepted)
        limit = min(self.deadline, time.monotonic() + float(step.get('deadline_seconds', 180)))
        polls = 0
        while time.monotonic() < limit:
            status = self.status()
            polls += 1
            job = next((row for row in status.get('jobs', []) if row.get('id') == ident), None)
            if job and job.get('status') in {'completed', 'error'}:
                self.terminals += 1
                brief = concise_result(job)
                self.event('job_terminal', step=step['id'], group=step.get('group'), polls=polls,
                           result=brief, status=concise_status(status),
                           primary=self.artifact(step, {'job': job, 'status': concise_status(status)}))
                if job['status'] != 'completed':
                    raise RuntimeError('Fixed step failed; primary preserved, no POST repetition: ' + step['id'])
                if brief.get('transport_status') in {'uncertain', 'waiting_or_processing', 'processing', 'queued'}:
                    raise RuntimeError('Transport effect not safely terminal; retain its ID, no automatic retry')
                # /api/status assembles cached owner metadata before taking the
                # job-list lock. A terminal job may share one response with the
                # preceding pending mirror. Confirm ONLY that exact terminal ID
                # by bounded passive GETs; do not clear it, POST or requeue it.
                if status.get('pending') and not concise_status(status)['uncertain']:
                    pending = status['pending']
                    if (brief.get('transport_status') == 'completed'
                            and pending.get('id') == brief.get('transport_id')
                            and pending.get('payload_sha256') == brief.get('payload_sha256')):
                        consistency_limit = min(self.deadline, time.monotonic() + 5)
                        self.event('terminal_pending_mirror_readonly_confirmation_begin', step=step['id'],
                                   transport_id=brief['transport_id'], status=concise_status(status),
                                   no_POST_no_queue_mutation=True)
                        while status.get('pending') and time.monotonic() < consistency_limit:
                            fresh = self.status()
                            self.event('terminal_pending_mirror_readonly_observation', step=step['id'],
                                       transport_id=brief['transport_id'], status=concise_status(fresh))
                            if concise_status(fresh)['uncertain']:
                                raise RuntimeError('Uncertain effect during passive consistency confirmation')
                            fresh_pending = fresh.get('pending')
                            if fresh_pending and (fresh_pending.get('id') != brief['transport_id']
                                    or fresh_pending.get('payload_sha256') != brief['payload_sha256']):
                                raise RuntimeError('Another pending ID or payload appeared; no automatic action')
                            status = fresh
                            if status.get('pending'):
                                time.sleep(min(.1, max(0, consistency_limit - time.monotonic())))
                if status.get('pending') or concise_status(status)['uncertain']:
                    raise RuntimeError('Pending or uncertain state preserved; no new task is submitted')
                allowed = step.get('allow_transport_status', ['completed'])
                if brief.get('transport_status') and brief['transport_status'] not in allowed:
                    raise RuntimeError('Transport status outside the predeclared step scope')
                return
            if concise_status(status)['uncertain']:
                raise RuntimeError('Owner reported an uncertain effect while waiting; preserve submitted ID')
            # Poll results are intentionally NOT serialized repeatedly. Only the
            # one terminal result, its identity, and its compact status are saved.
            time.sleep(min(.5, max(0, limit - time.monotonic())))
        self.event('job_deadline_preserved', step=step['id'], job_id=ident, polls=polls,
                   status=concise_status(status), no_retry=True)
        raise TimeoutError('One submitted job exceeded the fixed deadline; keep same ID: ' + ident)

    def hold(self, seconds):
        until = min(self.deadline, time.monotonic() + seconds)
        while time.monotonic() < until:
            time.sleep(min(.5, until - time.monotonic()))
        self.remaining()

    def run(self):
        report = {'schema': SCHEMA, 'life_id': self.plan['life_id'], 'success': False,
                  'operator_schedule_not_actor_learning': True,
                  'plan_path': str(self.plan_path),
                  'plan_sha256': hashlib.sha256(self.plan_path.read_bytes()).hexdigest(),
                  'no_automatic_native_restart_or_material_retry': True,
                  'capture_started_utc': self.capture_utc, 'started_utc': utc()}
        try:
            self.event('fixed_itinerary_started', **report)
            for index, step in enumerate(self.plan['steps']):
                self.remaining()
                self.event('step_started', index=index, step=step['id'], kind=step['kind'],
                           group=step.get('group'), label=step.get('label'))
                kind = step['kind']
                if kind == 'session':
                    self.connect(step)
                elif kind == 'action':
                    self.action(step)
                elif kind == 'presentation':
                    response = self.request(step.get('path', '/api/presentation'), step['payload'])
                    self.event('presentation_result', step=step['id'], response=response,
                               scope='Operator text/camera presentation; not a DEE response or decision')
                elif kind == 'observe':
                    value = self.status() if step.get('path', '/api/status') == '/api/status' else self.request('/api/frame')
                    self.event('passive_observation', step=step['id'],
                               primary=self.artifact(step, value),
                               status=concise_status(value) if 'life_id' in value else
                                   {key: value.get(key) for key in ('available', 'tick', 'N', 'captured_utc', 'RAW_sha256', 'clocks_sha256')})
                elif kind == 'shutdown':
                    response = self.request('/api/shutdown', {})
                    self.event('interface_shutdown_result', step=step['id'], response=response)
                    self.token = None
                self.hold(float(step.get('hold_seconds', 0)))
                self.event('step_completed', step=step['id'])
            report['success'] = True
        except BaseException as error:
            report['error'] = {'type': type(error).__name__, 'detail': str(error)}
            self.event('itinerary_aborted_preserve_future', error=report['error'],
                       no_owner_kill_no_rewind_no_reteach=True)
        finally:
            report.update(finished_utc=utc(), wall_seconds=time.monotonic() - self.begun,
                          posts_once=self.posts, terminal_jobs=self.terminals)
            self.event('fixed_itinerary_finished', result=report)
            self.stream.close()
            (self.out / 'RESULTADO.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
        return report['success']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--base-url', default='http://127.0.0.1:8765')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--max-seconds', type=float, default=1800)
    parser.add_argument('--capture-started-utc', help='Recorder timestamp, copied verbatim as timing metadata only')
    parser.add_argument('--validar', action='store_true', help='N0 plan validation; no HTTP, actor, owner or Runtime')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding='utf-8-sig'))
    checked = validate(plan)
    if args.validar:
        print(json.dumps(checked, ensure_ascii=False, indent=2))
        return 0
    if not args.out:
        parser.error('--out is required for execution')
    if not 1 <= args.max_seconds <= 3600:
        parser.error('--max-seconds must be a fixed 1..3600 seconds')
    if plan['steps'][0]['kind'] != 'session':
        parser.error('Execution must begin with a read-only session/identity handshake')
    return 0 if Itinerary(args.base_url, plan, args.plan, args.out,
                          args.max_seconds, args.capture_started_utc).run() else 1


if __name__ == '__main__':
    raise SystemExit(main())
