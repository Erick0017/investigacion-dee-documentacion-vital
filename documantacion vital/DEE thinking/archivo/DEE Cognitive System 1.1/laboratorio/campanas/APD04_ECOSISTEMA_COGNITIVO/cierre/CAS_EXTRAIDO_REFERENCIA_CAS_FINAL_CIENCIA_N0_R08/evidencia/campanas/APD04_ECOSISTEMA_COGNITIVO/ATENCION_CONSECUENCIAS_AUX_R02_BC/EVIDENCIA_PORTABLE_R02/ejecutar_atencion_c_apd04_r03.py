"""C exactly once: same physics, extended generic same-ID wait and owner monitor."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import shutil
import threading
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_SENSOR02_C_R03'
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
SOFT_STOP = datetime(2026, 10, 26, 21, 55, tzinfo=timezone.utc)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    if OUT.exists() or (ROOT / 'sistema/estado/vidas/APD04_ATENCION_SENSOR02_AUX').exists():
        raise FileExistsError('C already exists; no repeated import or Native task')
    if datetime.now(timezone.utc) >= SOFT_STOP:
        raise TimeoutError('The fixed branch deadline has passed before any import')
    old = load('unchanged_physical_plan_for_C_r03', HERE / 'ejecutar_atencion_consecuencias_apd04_r01.py')
    original_load = old.load
    old.OUT = OUT
    old.FROZEN = LAB / 'revisiones/R07_ATENCION_C_ESPERA_EJECUTADO'
    old.BRANCHES = [old.BRANCHES[2]]
    monitors = []

    def watched_load(name, path):
        module = original_load(name, path)
        if name != 'attention_existing_single_entry_UI':
            return module
        normal_read, normal_backend, normal_supervisor = module.read, module.OriginalBackend, module.Supervisor

        def extended_read(source):
            value = normal_read(source)
            if Path(source).name == 'ENTRADA_SENCILLA_APD03.json':
                value = dict(value, material_wait_seconds=900)
            return value
        module.read = extended_read

        class WatchedBackend(normal_backend):
            def start(self, life, directory):
                value = super().start(life, directory)
                process, job = self.process, self.job
                write(OUT / 'REVISION_SUPERVISION_ANTES_MATERIAL.json', {
                    'material_wait_seconds': 900, 'same_id_reads_only_after_timeout': True,
                    'soft_stop_utc': SOFT_STOP.isoformat(), 'front_hard_close_utc': '2026-10-26T22:00:00+00:00',
                    'new_life_C_only': True, 'physical_protocol_changed': False,
                    'argv': self.owner_argv(life), 'pid': process.pid, 'job_name': value['job_name']})

                def monitor():
                    samples = []
                    while True:
                        code = process.poll()
                        samples.append({'wall_utc': datetime.now(timezone.utc).isoformat(),
                            'exit_code': code, 'resources': self.pc.job_resources(job)})
                        if code is not None:
                            write(OUT / 'OWNER_HANDLE_EXIT.json', {'samples': samples,
                                'process_pid': process.pid, 'exit_code': code,
                                'monitor_did_not_terminate_any_process': True})
                            return
                        time.sleep(.5)
                thread = threading.Thread(target=monitor, daemon=True)
                thread.start()
                monitors.append(thread)
                return value

        class WaitingSupervisor(normal_supervisor):
            def material(self, situations, feedback='real', actuator='closed', request_id=None):
                value = super().material(situations, feedback=feedback, actuator=actuator, request_id=request_id)
                while module.row_of(value).get('status') not in module.TERMINAL:
                    if datetime.now(timezone.utc) >= SOFT_STOP:
                        write(OUT / 'LIMITE_SUPERVISION_SIN_REINTENTO.json', {
                            'id': request_id, 'last_result': value,
                            'wall_utc': datetime.now(timezone.utc).isoformat(),
                            'scope': 'Client/owner budget limit, never a cognitive verdict.'})
                        return value
                    if self.backend.process.poll() is not None:
                        return value
                    time.sleep(5)
                    value = self.result(request_id)
                return value

            def close(self):
                try:
                    return super().close()
                except BaseException:
                    process, job = self.backend.process, self.backend.job
                    if process is not None and process.poll() is None and datetime.now(timezone.utc) >= SOFT_STOP:
                        write(OUT / 'FIN_POR_PRESUPUESTO_PROPIO.json', {
                            'pid': process.pid, 'wall_utc': datetime.now(timezone.utc).isoformat(),
                            'resources_before_termination': self.backend.pc.job_resources(job),
                            'pending_not_cleared': self.state.get('pending_material'),
                            'reason': 'Declared front deadline; owned Job only, no repair or rewind.'})
                        self.backend.pc.terminate_job(job, 124)
                        write(OUT / 'OWNED_EXIT_AFTER_BUDGET.json', self.backend.finish_owned(10))
                    raise
        module.OriginalBackend = WatchedBackend
        module.Supervisor = WaitingSupervisor
        return module

    old.load = watched_load
    try:
        old.main()
    except BaseException as error:
        write(OUT / 'DRIVER_FAILURE_PRESERVED.json', {'error': repr(error),
            'traceback': traceback.format_exc(), 'no_physical_retry': True})
        raise
    finally:
        for monitor in monitors:
            monitor.join(timeout=2)
        if OUT.is_dir():
            shutil.copy2(Path(__file__), OUT / Path(__file__).name)


if __name__ == '__main__':
    main()
