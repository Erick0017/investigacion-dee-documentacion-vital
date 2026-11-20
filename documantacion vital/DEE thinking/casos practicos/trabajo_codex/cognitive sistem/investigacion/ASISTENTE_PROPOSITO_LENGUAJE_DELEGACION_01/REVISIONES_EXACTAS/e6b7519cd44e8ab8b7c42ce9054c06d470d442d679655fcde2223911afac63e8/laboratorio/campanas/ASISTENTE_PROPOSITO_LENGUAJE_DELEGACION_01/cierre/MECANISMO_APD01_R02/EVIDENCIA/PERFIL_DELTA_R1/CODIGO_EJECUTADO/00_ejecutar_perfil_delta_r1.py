"""Bounded APD01 clone controls; caller-authorized native experiments, not T0.

Six actual histories from the same complete protected closed-epoch prefix.
No expected totals or correct answers are passed to the native candidate.
"""
import argparse
import gc
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8') + b'\n'
    if path.exists():
        raise FileExistsError('Preserve primary ' + str(path))
    path.write_bytes(gzip.compress(payload, mtime=0) if path.suffix == '.gz' else payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--parent', default='APD01_BASE_LEXICA')
    parser.add_argument('--max-seconds', type=float, default=300)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('New run directory only')
    args.out.mkdir(parents=True)
    sys.path.insert(0, str(args.system.resolve()))
    from app.lives import Store
    from app.native_tools import physical
    from app.process_control import protect_current
    from capacidades import mente_acumulativa_r02 as ma
    protect_current(output=args.out / 'RECURSOS_PROCESO.json')
    module_path = Path(__file__).with_name('traslacion_acumulativa_core06_candidata.py')
    spec = importlib.util.spec_from_file_location('APD01_AFFINE_R1_EXECUTED', module_path)
    candidate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate)
    protocol_path = Path(__file__).with_name('PROTOCOLO_TRASLACION_ACUMULATIVA_R1.json')
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    sources = [Path(__file__), module_path, protocol_path,
               args.system / 'app/lives.py', args.system / 'capacidades/mente_acumulativa_r02.py']
    frozen = args.out / 'CODIGO_EJECUTADO'
    frozen.mkdir()
    rows = []
    for i, source in enumerate(sources):
        destination = frozen / (str(i).zfill(2) + '_' + source.name)
        shutil.copyfile(source, destination)
        rows.append({'source': str(source.resolve()), 'archived': destination.relative_to(args.out).as_posix(),
                     'bytes': source.stat().st_size, 'sha256': sha(source)})
    store = Store(args.system)
    parent = store.record(args.parent)
    emit(args.out / 'ANTES_DEL_PRIMER_TICK.json', {
        'protocol': protocol, 'parent': parent, 'sources': rows,
        'native_execution_not_yet_started': True,
        'no_actor_expected_answer_inputs': True,
        'max_process_seconds': args.max_seconds,
        'single_native_owner_at_a_time': True})
    started = time.monotonic()
    outcomes = []
    for history in protocol['frozen_histories']:
        if time.monotonic() - started >= args.max_seconds:
            outcomes.append({'id': history['id'], 'not_executed': 'Fixed process budget reached'})
            continue
        life = 'APD01_AFFINE_R1_' + history['id']
        prefix = args.out / history['id']
        prefix.mkdir()
        fork = store.fork(args.parent, life, kind='APD01_BOUNDED_AFFINE_CONTROL_FROM_IDENTICAL_PARENT')
        emit(prefix / '00_FORK.json.gz', fork)
        def run(a):
            value = {'parent_physical': physical(a.world), 'preparation': candidate.prepare(a)}
            a.save(prefix / '01_ADMITIDO_COMPLETO.deetsnap.gz')
            lesson = candidate.teach(a, *history['teaching_pair'], teacher=history['teacher'], intervention=history['intervention'])
            value['lesson'] = lesson
            a.save(prefix / '02_POST_LECCION_COMPLETO.deetsnap.gz')
            emit(prefix / '02_LECCION.json.gz', lesson)
            value['uses'] = []
            for i, increment in enumerate(protocol['common_query_increments']):
                result = candidate.accumulate(a, increment)
                value['uses'].append(result)
                emit(prefix / ('03_USO_' + str(i) + '.json.gz'), result)
            value['after_five_uses'] = physical(a.world)
            a.save(prefix / '04_CINCO_USOS_COMPLETO.deetsnap.gz')
            value['old_six'] = []
            for context in ('alfa', 'beta', 'gamma', 'delta', 'epsilon', 'zeta'):
                result = ma.query(a, context, detail=False)
                value['old_six'].append({'context': context, 'result': result})
            value['after_panel'] = physical(a.world, occupation=True)
            return value
        try:
            result = store.mutate(life, 'APD01_AFFINE_R1_FIXED_FIVE_USE_RESERVE', run,
                                  {'history': history['id'], 'protocol_sha256': sha(protocol_path)})
            emit(prefix / '05_RESULTADO_COMPLETO.json.gz', result)
            native = result['result']
            summary = {'id': history['id'], 'life': life,
                       'numeric_outputs': [row['numeric_result'] for row in native['uses']],
                       'abstentions': [row['abstention'] for row in native['uses']],
                       'old_six': [row['result']['reader']['formed_native_command'] for row in native['old_six']],
                       'final': store.record(life)}
            outcomes.append(summary)
        except Exception as error:
            reached = store.record(life)
            outcome = {'id': history['id'], 'life': life, 'error': {'type': type(error).__name__, 'detail': str(error)},
                       'reached': reached, 'future_not_rolled_back': True}
            emit(prefix / '05_ERROR_ESTADO_CONSERVADO.json.gz', outcome)
            outcomes.append(outcome)
        gc.collect()
        print(json.dumps({'finished_history': history['id'], 'elapsed': time.monotonic()-started,
                          'summary': {k:v for k,v in outcomes[-1].items() if k not in ('final','reached')}}, ensure_ascii=False), flush=True)
    emit(args.out / 'RESULTADOS.json', {'schema': 'APD01.affine_candidate.actual_histories.v1',
                                      'parent': parent, 'elapsed_seconds': time.monotonic()-started,
                                      'histories': outcomes, 'native_dynamics': 'Official DEE4.5/v27 only',
                                      'scope': 'Correlated exact forks, not independent learners. Bounded five-use native cumulative offset; all adverse futures retained.'})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
