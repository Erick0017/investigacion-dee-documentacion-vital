"""Bounded native social calibration on exact, individually identified forks.

No engine/kernel alteration, no anatomical/memory cleanup, no new host selector.
The optional common action opportunity intentionally omits the old native return.
"""
from pathlib import Path
import argparse, datetime, gzip, hashlib, json, os, shutil, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SYS = ROOT / 'sistema'
EV = ROOT / 'evidencia/campanas/ENTE_DEE_OPERATIVO_01/social'
sys.path.insert(0, str(SYS))
from app.lives import Store
from capacidades import cierre_funcional_cf01 as cf


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_record(rec):
    return {k: v for k, v in rec.items() if k != 'operations'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('case')
    p.add_argument('--value', type=int, required=True)
    p.add_argument('--cut', choices=('none', 'minus_bus', 'plus_bus'), default='none')
    p.add_argument('--repeat-blocks', type=int, default=1)
    p.add_argument('--action', action='store_true')
    args = p.parse_args()
    budget = json.loads((HERE.parent / 'PRESUPUESTO.json').read_text(encoding='utf8'))
    if time.monotonic() >= budget['monotonic_deadline'] - 600:
        raise RuntimeError('EO01 fixed budget closing; no new auxiliary run')
    if not args.case.startswith('EO01_SOC_AUX_'):
        raise ValueError('Diagnostic identity namespace required')
    if not 1 <= args.repeat_blocks <= 3:
        raise ValueError('Bounded repeat blocks1..3')
    EV.mkdir(parents=True, exist_ok=True)
    output = EV / (args.case + '.json.gz')
    if output.exists():
        raise FileExistsError('Preserved case is not overwritten')
    sources = [Path(__file__), HERE / 'PLAN_SOCIAL_R1.json',
               SYS / 'app/lives.py', SYS / 'app/native_tools.py',
               SYS / 'capacidades/cierre_funcional_cf01.py',
               SYS / 'capacidades/arquitectura_distribuida_mi02_r8.py',
               SYS / 'capacidades/integracion_distribuida_mi02_r6.py']
    index = [{'path': str(q.relative_to(ROOT)), 'sha256': sha(q), 'bytes': q.stat().st_size} for q in sources]
    digest = hashlib.sha256(json.dumps(index, sort_keys=True).encode()).hexdigest()
    archive = EV / 'codigo_ejecutado' / digest
    for q in sources:
        dst = archive / q.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copyfile(q, dst)
    (archive / 'INDICE.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf8')
    store = Store()
    original = store.record('CF01_MAIN')
    if original['physical']['tick'] != 67723 or original['snapshot_sha256'] != '205a34e3b0925fe6d9631d4934aaf29c427171f123d4176adf68bf44d76e07bb':
        raise RuntimeError('Preselected complete parent has changed; no fallback')
    born = store.fork('CF01_MAIN', args.case, kind='DIAGNOSTIC_COPY')
    result = {'schema': 'EO01.social.aux.primary.v1', 'case': args.case,
              'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'code_digest': digest, 'source_index': index, 'arguments': vars(args),
              'fork_record': safe_record(born), 'blocks': []}
    def experiment(a):
        rows = []
        for k in range(args.repeat_blocks):
            r = cf.pulse(a, participant='B_incoming', value=args.value, delay=1, horizon=80, cut=args.cut)
            row = {'index': k, 'private_input': r}
            if args.action:
                action = cf.episode(a, availability=1, mode='omit_return', public=[10,20], trace=False)
                row['common_action'] = action
                row['fixed_reader'] = cf.decode_window(action)
            rows.append(row)
        return rows
    try:
        mutated = store.mutate(args.case, 'EO01_SOCIAL_AUX', experiment, vars(args))
        result['blocks'] = mutated['result']
        result['final_record'] = safe_record(store.record(args.case))
        result['source_unchanged'] = all(sha(ROOT / q['path']) == q['sha256'] for q in index)
    except Exception as error:
        result['error'] = {'type': type(error).__name__, 'detail': str(error)}
        result['final_record'] = safe_record(store.record(args.case))
        raise
    finally:
        result['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with gzip.open(output, 'xt', encoding='utf8') as f:
            json.dump(result, f, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    print(json.dumps({'case': args.case, 'path': str(output), 'sha256': sha(output),
                      'tick': result['final_record']['physical']['tick'],
                      'contexts': [[v['s_reg'] for v in b['private_input']['after']['context_A']] for b in result['blocks']],
                      'commands': [b.get('fixed_reader',{}).get('command') for b in result['blocks']]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
