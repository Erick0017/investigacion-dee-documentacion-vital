"""B/C only, same fixed physical plan; preserve A and capture owner exit data."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import shutil
import threading
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_CONSECUENCIAS_AUX_R02_BC'
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'


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
    if OUT.exists():
        raise FileExistsError('The declared B/C driver revision exists; no retries')
    OUT.mkdir(parents=True)
    old = load('unchanged_physical_attention_plan_r01', HERE / 'ejecutar_atencion_consecuencias_apd04_r01.py')
    original_load = old.load
    source = HERE / 'ejecutar_atencion_consecuencias_apd04_r01.py'
    shutil.copy2(source, OUT / source.name)
    shutil.copy2(Path(__file__), OUT / Path(__file__).name)
    write(OUT / 'REVISION_ANTES_NATIVE.json', {'revision': 'R02_BC_only_owner_monitor',
        'exact_original_plan_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'driver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'A_not_reopened_or_repeated': True, 'Native_protocol_changed': False,
        'owner_max_seconds': 7200, 'material_wait_seconds': 240,
        'intervention': 'Python owner handle/process resource monitoring only; no codec, calendar or evaluator change.'})
    completed = []
    for branch in old.BRANCHES[1:]:
        label, life, *_ = branch
        branch_out = OUT / ('RUN_' + label)
        old.OUT = branch_out
        old.FROZEN = LAB / ('revisiones/R06_ATENCION_BC_' + label + '_EJECUTADO')
        old.BRANCHES = [branch]
        monitors = []

        def watched_load(name, path):
            module = original_load(name, path)
            if name != 'attention_existing_single_entry_UI':
                return module
            normal = module.OriginalBackend

            class WatchedBackend(normal):
                def start(self, selected_life, directory):
                    value = super().start(selected_life, directory)
                    process, job = self.process, self.job
                    write(branch_out / 'OWNER_HANDLE_START.json', {'selected_life': selected_life,
                        'argv': self.owner_argv(selected_life), 'process_pid': process.pid,
                        'job_name': value['job_name'], 'started': datetime.now(timezone.utc).isoformat(),
                        'resources': self.pc.job_resources(job)})

                    def monitor():
                        samples = []
                        while True:
                            code = process.poll()
                            samples.append({'wall_utc': datetime.now(timezone.utc).isoformat(),
                                'exit_code': code, 'resources': self.pc.job_resources(job)})
                            if code is not None:
                                write(branch_out / 'OWNER_HANDLE_EXIT.json', {'samples': samples,
                                    'process_pid': process.pid, 'exit_code': code,
                                    'no_termination_by_monitor': True})
                                return
                            time.sleep(.5)
                    thread = threading.Thread(target=monitor, daemon=True)
                    thread.start()
                    monitors.append(thread)
                    return value
            module.OriginalBackend = WatchedBackend
            return module

        old.load = watched_load
        try:
            old.main()
            completed.append({'branch': label, 'complete': True})
        except BaseException as error:
            # No life is restarted, no pending material is cleared, no ID is put twice.
            write(branch_out / 'DRIVER_FAILURE_PRESERVED.json', {'error': repr(error),
                'traceback': traceback.format_exc(), 'no_physical_retry': True})
            completed.append({'branch': label, 'complete': False, 'error': repr(error)})
        finally:
            for monitor in monitors:
                monitor.join(timeout=2)
    write(OUT / 'CIERRE_BC_DRIVER.json', {'branches': completed,
        'A_remains_adverse_without_reopen': True, 'one_common_prefix_not_independent_learners': True})
    print(json.dumps(completed, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
