"""Pure control-plan export AFTER real18 closed, with fixed earlier permutation.

No world open, Native import, response selection, permutation search or replay.
The emitted file is an auditor/control configuration, never Native actor input.
"""
from pathlib import Path
import argparse, hashlib, json

P = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def require(ok, message):
    if not ok: raise ValueError(message)


def main(args):
    source = Path(args.real).resolve(strict=True)
    require(source.is_relative_to((P/'control').resolve()), 'Only a closed PI08 real-arm proof')
    real = read(source); p = read(P/'codigo/PROTOCOLO_PI08_B_R01.json')
    require(real['schema'] == 'DEE.PI08.B.actual_nonperiodic_arm.R01' and real['role'] == 'real'
            and real['status'] == 'CLOSED_18_OPPORTUNITIES' and real['closed'] is True and real['error'] is None,
            'All18 real opportunities must close before constructing the matched control')
    require(real['protocol_sha256'] == sha(P/'codigo/PROTOCOLO_PI08_B_R01.json'), 'Prospective protocol changed')
    require(len(real['rows']) == 18 and [r['B_ordinal'] for r in real['rows']] == list(range(18)), 'All real rows required')
    failed = [row['actual_failed'] for row in real['rows']]
    require(all(type(value) is bool for value in failed), 'Material failed values must be explicit booleans')
    permutation = p['controls']['yoke_permutation']
    require(sorted(permutation) == list(range(18)) and all(i != v for i, v in enumerate(permutation)), 'Precommitted derangement required')
    require(len({(v-i) % 18 for i, v in enumerate(permutation)}) > 1, 'No cyclic warning shift')
    values = [failed[i] for i in permutation]
    plan = {'schema': 'DEE.PI08.B.noncyclic_yoked_return.v1', 'permutation': permutation,
            'source_failed': failed, 'values': values, 'source_evidence_sha256': sha(source)}
    content = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n'
    require(len(content.encode('utf8')) <= 8192, 'Control plan exceeds transport field bound')
    target = P/'control/PLAN_YOKE18_B_PI08_R01.json'
    require(not target.exists(), 'Preserve the first fixed yoked plan; never choose another after outcomes')
    with target.open('x', encoding='utf8') as out: out.write(content)
    summary = {'schema': 'DEE.PI08.B.yoked_plan.prepared.v1', 'Native_executed': False,
               'source': {'path': str(source), 'sha256': sha(source)},
               'protocol_sha256': real['protocol_sha256'], 'plan': {'path': str(target), 'bytes': target.stat().st_size, 'sha256': sha(target)},
               'real_failed_count': sum(failed), 'yoked_return_failed_count': sum(values),
               'precommitted_permutation': permutation, 'no_search_or_resampling': True,
               'difference_from_source_on_same_index': sum(a != b for a,b in zip(failed, values)),
               'difference_is_NOT_actual_yoked_manipulation_result': True,
               'interpretation': 'Same boolean dose is guaranteed; actual mismatch to outcomes, effective phase and warning information require the subsequent material yoked run. An accidentally informative yoke is reported, not reselected.'}
    witness = P/'control/YOKE18_B_PLAN_EXPORTADO_PI08_R01.json'
    with witness.open('x', encoding='utf8') as out: json.dump(summary, out, ensure_ascii=False, indent=2); out.write('\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', required=True)
    main(parser.parse_args())
