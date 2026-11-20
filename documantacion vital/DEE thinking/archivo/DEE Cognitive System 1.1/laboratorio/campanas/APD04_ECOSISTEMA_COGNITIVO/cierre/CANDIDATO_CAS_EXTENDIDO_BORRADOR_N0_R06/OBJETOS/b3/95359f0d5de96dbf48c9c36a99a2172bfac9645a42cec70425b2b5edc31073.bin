"""Bound and measure the complete APD04 literal-driver tree, no DEE decisions."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def emit(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--root-go', choices=('APD04_LITERAL_PLAN_CLOSED',), required=True)
    args = parser.parse_args()
    root, plan_path, out = args.root.resolve(strict=True), args.plan.resolve(strict=True), args.out.resolve()
    driver = load('apd04_literal_driver_functions_only', Path(__file__).with_name('ejecutar_plan_apd04_r02.py'))
    plan = driver.validate_plan(driver.read(plan_path))
    deadline = datetime.fromisoformat(plan['deadline_utc'].replace('Z', '+00:00')).timestamp()
    wall_limit = min(plan.get('supervision_wall_limit_seconds', plan['duration_seconds']+1200), deadline-time.time()-30)
    if wall_limit <= plan['duration_seconds']+plan.get('closing_reserve_seconds', 180):
        raise ValueError('Not enough authorized time for the literal window and own shutdown.')
    if out.exists():
        raise FileExistsError('Do not overwrite a supervision attempt.')
    out.mkdir(parents=True)
    child_out = out/'TRAYECTORIA'
    pc = load('apd04_total_owned_process_control', root/'sistema/app/process_control.py')
    command = [sys.executable, '-I', '-B', '-X', 'utf8', str(Path(driver.__file__).resolve()),
               '--root', str(root), '--plan', str(plan_path), '--out', str(child_out),
               '--root-go', args.root_go]
    emit(out/'ANTES_DEL_PROCESO.json', {'command': command, 'plan_sha256': driver.sha(plan_path),
          'driver_sha256': driver.sha(driver.__file__), 'supervisor_sha256': driver.sha(__file__),
          'total_tree_limit_bytes': 1073741824, 'native_tree_separate_limit_bytes': 536870912,
          'wall_limit_seconds': wall_limit, 'deadline_utc': plan['deadline_utc'],
          'scope': 'Outer Job includes driver, manager clients and Native descendants. Never add nested Native figures to this total. I/O uses class8. Energy NO MEDIDA.'})
    began = time.monotonic()
    cpu_start = time.process_time_ns()
    error = None
    samples = 0
    final = None
    with (out/'STDOUT.txt').open('xb') as stdout, (out/'STDERR.txt').open('xb') as stderr:
        process, job, name = pc.spawn_owned(command, cwd=Path(sys.executable).parent,
                    stdout=stdout, stderr=stderr, memory_limit=1073741824)
        try:
            while True:
                measurement = driver.job_measure(pc, job)
                sample = {'wall_utc': datetime.now(timezone.utc).isoformat(),
                          'elapsed_seconds': time.monotonic()-began, **measurement}
                with (out/'MUESTRAS_TOTALES_CLASS8.jsonl').open('a', encoding='utf8', newline='\n') as stream:
                    stream.write(json.dumps(sample, ensure_ascii=False, separators=(',', ':'))+'\n')
                samples += 1
                if process.poll() is not None and not measurement.get('job_active_processes'):
                    break
                if time.monotonic()-began >= wall_limit:
                    error = 'Own process tree reached the predeclared wall guard; host limit, not a cognitive verdict.'
                    pc.terminate_job(job, 124)
                    process.wait(timeout=15)
                    break
                time.sleep(min(5, max(.1, wall_limit-(time.monotonic()-began))))
            final = driver.job_measure(pc, job)
        finally:
            pc.close_job(job)
    result = {'command': command, 'pid': process.pid, 'job_name': name,
              'exit_code': process.returncode, 'error': error, 'samples': samples,
              'actual_wall_seconds': time.monotonic()-began,
              'monitor_cpu_ns': time.process_time_ns()-cpu_start, 'final_total_job': final,
              'no_decisional_intervention': True, 'energy': 'NO MEDIDA'}
    emit(out/'RESULTADO_SUPERVISION.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 1 if error or process.returncode else 0


if __name__ == '__main__':
    raise SystemExit(main())
