"""Exercise run() with an explicitly fake transport/owner, zero Native ticks."""
import argparse
import contextlib
from datetime import datetime, timezone, timedelta
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--salida', type=Path, required=True)
    a = p.parse_args()
    root = a.root.resolve(strict=True)
    if a.salida.exists():
        raise FileExistsError('Preserve every N0 receipt.')
    path = Path(__file__).with_name('ejecutar_plan_apd04_r02.py')
    driver = load('driver_r02_test', path)
    actual_ui = load('actual_ui_parsing_functions_only', root/'sistema/app/usar_dee.py')
    card = driver.read(root/'sistema/estado/vidas/APD04_MAIN/VIDA.json')
    events = []
    fake_pc = SimpleNamespace(K=SimpleNamespace(OpenJobObjectW=lambda *args: 1, CloseHandle=lambda *args: None))
    protected = {str(root/'sistema/estado/ACTIVO.json'): driver.sha(root/'sistema/estado/ACTIVO.json'),
                 str(root/'sistema/estado/vidas/APD04_MAIN/VIDA.json'): driver.sha(root/'sistema/estado/vidas/APD04_MAIN/VIDA.json'),
                 str(root/'sistema'/card['snapshot']): driver.sha(root/'sistema'/card['snapshot'])}
    with tempfile.TemporaryDirectory(prefix='apd04_driver_N0_') as temporary:
        tmp = Path(temporary)

        class FakeBackend:
            protocol_home = tmp/'fake_protocol'
            pc = fake_pc

            def __init__(self, *args):
                pass

            def record(self, life):
                assert life == 'APD04_MAIN'
                return card

        class FakeSession:
            def __init__(self, root, life, backend, config):
                self.state = {'life_id': life, 'world_id': life, 'pending_material': None, 'uncertain_preserved': False}
                self.state_path = tmp/'FAKE_UI_PROTOCOL.json'
                self.state_path.write_text('{}', encoding='utf8')
                self.owned = False

            def open(self, new=False):
                assert new is False
                events.append('open_existing_fake')

            def start(self):
                self.owned = True
                events.append('start_paused_fake')
                return {'job_name': 'EXPLICITLY_FAKE_N0_JOB', 'started_paused': True}

            def control(self, operation):
                events.append(operation+'_fake')
                if operation == 'detener':
                    self.owned = False
                return {'request': {'status': 'completed', 'operation': operation}}

            def status(self):
                return {'ESTADO_PUBLICADO': {'tick': card['physical']['tick'], 'fake': True}}

            def material(self, situations, feedback, actuator, request_id):
                events.append(('one_submission_fake', request_id, situations, feedback, actuator))
                return {'request': {'status': 'completed', 'id': request_id, 'result': '{"fake":true}'}}

            def close(self):
                return self.control('detener')

        fake_ui = SimpleNamespace(
            selected_config_path=actual_ui.selected_config_path, OriginalBackend=FakeBackend,
            Supervisor=FakeSession, identifier=actual_ui.identifier,
            command_parser=actual_ui.command_parser, literal_rows=actual_ui.literal_rows,
            SessionLock=lambda *args: contextlib.nullcontext(), row_of=actual_ui.row_of,
            observation=actual_ui.observation, TERMINAL=actual_ui.TERMINAL)
        plan = {'schema': 'APD04.literal_supervisor_schedule.v1', 'status': 'CLOSED_FOR_EXECUTION',
                'life': 'APD04_MAIN', 'world_id': 'APD04_MAIN', 'initial_tick': card['physical']['tick'],
                'initial_snapshot_sha256': card['snapshot_sha256'], 'duration_seconds': .02,
                'deadline_utc': (datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),
                'heartbeat_seconds': 30, 'events': [
                    {'at_seconds': 0, 'kind': 'material', 'request_id': 'N0_MATERIAL_NEVER_SUBMITTED_TO_DEE',
                     'situations': [{'modo': 'EXPLICIT_FAKE_N0'}], 'feedback': 'omit'},
                    {'at_seconds': 0, 'kind': 'command', 'request_id': 'N0_COMMAND_NEVER_SUBMITTED_TO_DEE',
                     'argv': ['panel', '--retorno', 'omit']},
                    {'at_seconds': 0, 'kind': 'checkpoint', 'tag': 'FAKE_N0'},
                    {'at_seconds': .01, 'kind': 'status'}]}
        plan_path = tmp/'PLAN_FAKE_N0.json'
        plan_path.write_text(json.dumps(plan), encoding='utf8')
        with patch.object(driver, 'load', return_value=fake_ui), patch.object(driver, 'job_measure',
             return_value={'job_active_processes': 0, 'fake': True}):
            result = driver.run(root, plan_path.resolve(), tmp/'FAKE_OUTPUT')
        executed = driver.read(tmp/'FAKE_OUTPUT/RESULTADO.json')
        assert result == 0 and executed['error'] is None
        assert events[0] == 'open_existing_fake' and events[1] == 'start_paused_fake'
        assert events[2] == 'reanudar_fake' and events[-1] == 'detener_fake'
        material = [event for event in events if isinstance(event, tuple)]
        assert len(material) == 2 and len({event[1] for event in material}) == 2
        assert executed['final_record']['physical'] == card['physical']
        assert all(driver.sha(p) == h for p, h in protected.items())
        summary = {'schema': 'APD04.literal_driver.run.N0.explicit_fake.v1', 'driver_sha256': driver.sha(path),
                   'tests': ['ordered fixed schedule', 'explicit existing-life reopen', 'paused fake owner',
                             'literal material', 'literal command parser', 'fixed IDs', 'checkpoint', 'passive status',
                             'save/stop', 'protected file hashes'], 'fake_calls': events,
                   'exit_code': result, 'new_native_ticks': 0, 'new_owners': 0,
                   'real_causal_files_unchanged': True, 'no_scientific_claim': True}
        with a.salida.open('x', encoding='utf8', newline='\n') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
