"""Deterministic thread schedule reproduces the HTTP status mirror race.

Loads GUI class definitions only. A mocked owner, work queue and result replace
every physical operation. No socket, DEE import, owner or Runtime is created.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import threading

HERE = Path(__file__).resolve().parent
APP = HERE.parents[1] / 'documantacion vital/DEE thinking/DEE Cognitive 2.0/aplicacion/GENESIS/genesis.py'

OLD_WORK = """                result = self.perform(action, value)
                self.jobs[ident].update(status='completed', result=result, finished_utc=now())
                self.event('interface_operation_result', interface_action=action, result=result)
            except Exception as error:
                self.jobs[ident].update(status='error', error={'type': type(error).__name__, 'detail': str(error)}, finished_utc=now())
                self.event('interface_operation_error', interface_action=action, error=self.jobs[ident]['error'])
"""
NEW_WORK = """                result = self.perform(action, value)
                # Publish completion and its event under the same RLock used by
                # status(); no Native processing or request is repeated here.
                with self.mutex:
                    self.jobs[ident].update(status='completed', result=result, finished_utc=now())
                    self.event('interface_operation_result', interface_action=action, result=result)
            except Exception as error:
                with self.mutex:
                    self.jobs[ident].update(status='error', error={'type': type(error).__name__, 'detail': str(error)}, finished_utc=now())
                    self.event('interface_operation_error', interface_action=action, error=self.jobs[ident]['error'])
"""
OLD_JOBS = "'jobs': list(self.jobs.values())[-20:],"
NEW_JOBS = "'jobs': [dict(row) for row in list(self.jobs.values())[-20:]],"


def load(text, name):
    spec = importlib.util.spec_from_loader(name, loader=None)
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(APP)
    exec(compile(text, str(APP), 'exec'), module.__dict__)
    return module


def one_schedule(text, name):
    module = load(text, name)
    pending_read = threading.Event()
    job_updated = threading.Event()
    finished = threading.Event()
    class State(dict):
        first = True
        def get(self, key, default=None):
            value = super().get(key, default)
            if key == 'pending_material' and self.first:
                self.first = False
                pending_read.set()
                # Finite scheduling hook: while status holds the GUI mutex,
                # give the old unlocked worker a deterministic chance to finish.
                job_updated.wait(.15)
            return value
    class Job(dict):
        def update(self, *args, **kwargs):
            super().update(*args, **kwargs)
            job_updated.set()
    class StopMockWorker(BaseException): pass
    class Work:
        sent = False
        def get(self):
            if self.sent:
                raise StopMockWorker()
            self.sent = True
            return 'job_one', 'ejecutar', {'id': 'same_transport'}
        def task_done(self): pass
    class Backend:
        def record(self, life): return None
        def manager(self, args): return {'observation': None}
    instance = module.Genesis.__new__(module.Genesis)
    instance.life = 'SYNTHETIC_NO_NATIVE'
    instance.backend = Backend()
    instance.session = type('Session', (), {'owned': True, 'state': State(
        pending_material={'id': 'same_transport', 'payload_sha256': 'same_payload'},
        uncertain_preserved=False)})()
    instance.mutex = threading.RLock()
    instance.events = []
    instance.jobs = {'job_one': Job(id='job_one', status='queued')}
    instance.work = Work()
    instance.recording = False
    instance.viewer_only = False
    instance.presentation = {}
    instance.config = {}
    def perform(action, value):
        assert pending_read.wait(2)
        instance.session.state['pending_material'] = None
        return {'request': {'id': 'same_transport', 'status': 'completed'}}
    instance.perform = perform
    def event(name, **data):
        with instance.mutex:
            instance.events.append({'event': name, **data})
    instance.event = event
    def worker():
        try:
            instance._work()
        except StopMockWorker:
            pass
        finally:
            finished.set()
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    snapshot = instance.status()
    at_return = snapshot['jobs'][0]['status']
    assert finished.wait(2)
    thread.join(timeout=1)
    after_json_render = json.loads(json.dumps(snapshot))
    fresh = instance.status()
    return {'variant': name, 'pending_in_old_snapshot': snapshot['pending'],
            'job_at_status_return': at_return,
            'job_after_worker_finished_before_HTTP_JSON': after_json_render['jobs'][0]['status'],
            'old_snapshot_mixed_pending_with_completed': bool(after_json_render['pending'])
                and after_json_render['jobs'][0]['status'] == 'completed',
            'fresh_snapshot_pending': fresh['pending'], 'fresh_job_status': fresh['jobs'][0]['status'],
            'mock_physical_calls': 1, 'native_ticks': 0, 'HTTP_requests': 0}


def main():
    original = APP.read_bytes()
    text = original.decode('utf8')
    assert text.count(OLD_WORK) == 1 and text.count(OLD_JOBS) == 1
    locked = text.replace(OLD_WORK, NEW_WORK, 1)
    complete = locked.replace(OLD_JOBS, NEW_JOBS, 1)
    cases = [one_schedule(text, 'R01_unlocked_live_job_reference'),
             one_schedule(locked, 'lock_only_live_job_reference'),
             one_schedule(complete, 'lock_and_top_level_job_snapshot')]
    assert cases[0]['old_snapshot_mixed_pending_with_completed']
    assert cases[1]['old_snapshot_mixed_pending_with_completed']
    assert not cases[2]['old_snapshot_mixed_pending_with_completed']
    assert cases[2]['job_after_worker_finished_before_HTTP_JSON'] == 'processing'
    assert cases[2]['fresh_snapshot_pending'] is None
    assert cases[2]['fresh_job_status'] == 'completed'
    assert APP.read_bytes() == original
    report = {'schema': 'DEE20.directed_status_worker_thread_race.N0.v1',
              'app_sha256_observed': hashlib.sha256(original).hexdigest(),
              'real_app_changed': False, 'no_http_no_native': True, 'cases': cases,
              'scope': 'GUI transport publication and stable status snapshot only; not a Native answer or memory change.'}
    (HERE / 'PRUEBA_RACE_STATUS_WORKER_N0.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    (HERE / 'PARCHE_RACE_STATUS_WORKER_N0.json').write_text(json.dumps({
        'file': 'aplicacion/GENESIS/genesis.py', 'original_sha256': report['app_sha256_observed'],
        'changes': [{'old': OLD_WORK, 'new': NEW_WORK}, {'old': OLD_JOBS, 'new': NEW_JOBS}]},
        ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
