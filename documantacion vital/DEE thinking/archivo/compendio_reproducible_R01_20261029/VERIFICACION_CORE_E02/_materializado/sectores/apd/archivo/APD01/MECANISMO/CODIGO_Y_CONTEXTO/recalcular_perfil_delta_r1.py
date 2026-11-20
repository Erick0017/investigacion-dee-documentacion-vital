"""Portable archived RAW/receipt checks, not native replay or host teaching."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def load(path):
    b = path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix == '.gz' else b)


def walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def fields(value):
    if type(value) is not int and not (isinstance(value, str) and value.isdecimal()):
        raise ValueError('Exact integer RAW required')
    n = int(value)
    if not 0 <= n < 2**64:
        raise ValueError('uint64 out of domain')
    return {'state': n & 0xffffffff, 's_reg': (n >> 32) & 65535,
            'semantic': (n >> 60) & 15,
            'direction': [((n >> shift) & 15) - (16 if ((n >> shift) & 15) >= 8 else 0)
                          for shift in (48, 52, 56)]}


def calculate(root):
    frozen = load(root / 'ANTES_DEL_PRIMER_TICK.json')
    protocol = frozen['protocol']
    rows, issues, sources, seen_raw = [], [], [], set()
    parents = []
    for history in protocol['frozen_histories']:
        identity = history['id']
        file = root / identity / '05_RESULTADO_COMPLETO.json.gz'
        document = load(file)
        sources.append({'file': file.relative_to(root).as_posix(),
                        'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
        data = document['result']
        parents.append(data['parent_physical'])
        raw_count = 0
        for node in walk(data):
            if all(k in node for k in ('raw', 'state', 's_reg', 'semantic', 'direction', 'clock', 'site')):
                encoded = json.dumps(node, sort_keys=True, separators=(',', ':')).encode('utf-8')
                digest = hashlib.sha256(encoded).hexdigest()
                if digest in seen_raw:
                    continue
                seen_raw.add(digest)
                decoded = fields(node['raw'])
                raw_count += 1
                if any(node[k] != value for k, value in decoded.items()):
                    issues.append(identity + ':RAW:' + digest)
                if not 0 <= int(node['clock']) < 2**64:
                    issues.append(identity + ':clock:' + digest)
        expected_delta = history['teaching_pair'][1] - history['teaching_pair'][0]  # Offline evaluator.
        expected_gate = history['teacher'] == 'paired' and history['intervention'] != 'cut'
        running = expected_delta
        checks = []
        requested = []
        requested.extend(data['lesson']['requests'])
        for step, use in enumerate(data['uses']):
            requested.extend(use['requests'])
            running += protocol['common_query_increments'][step]  # Offline scoring only.
            qsite = [20 + step, 23 + 8 * step, 30]
            reader_site = [qsite[0] + 1, qsite[1] + 2, 30]
            gate = use['frames'][-1]['reader_site']
            decoded = fields(gate['raw'])
            valid = bool(decoded['state']) and decoded['semantic'] == 1 and decoded['direction'] == [0, 1, 0]
            actual_number = decoded['s_reg'] - 4096 if valid else None
            good = (gate['site'] == reader_site and gate['tick'] == use['arrival'] + 2
                    and actual_number == use['numeric_result'] and use['abstention'] == (not valid)
                    and use['numeric_result'] == (running if expected_gate else None))
            if not good:
                issues.append(identity + ':numeric_step:' + str(step))
            checks.append({'step': step, 'actual': actual_number,
                           'offline_expected': running if expected_gate else None,
                           'native_gate_valid': valid, 'exact': good})
        old_six = []
        for old in data['old_six']:
            requested.extend(old['result']['requests'])
            reader = old['result']['reader']
            candidates = []
            allowed = {(33+4*x, 33+4*y, 33+sign): [0, 0, sign]
                       for x, y in ((1,0),(0,1),(1,1),(-1,1),(1,-1),(-1,-1)) for sign in (-1,1)}
            if len(reader['panel']) != 12 or {tuple(o['site']) for o in reader['panel']} != set(allowed):
                issues.append(identity + ':old_fixed_geometry:' + old['context'])
            for o in reader['panel']:
                f = fields(o['raw'])
                if f['state'] and f['semantic'] == 1 and f['direction'] == allowed[tuple(o['site'])]:
                    candidates.append(f['direction'][2])
            native = candidates[0] if len(candidates) == 1 else None
            if native != reader['formed_native_command']:
                issues.append(identity + ':old_reader:' + old['context'])
            old_six.append(native)
        unique = {x['id']: x for x in requested}
        if len(unique) != len(requested):
            issues.append(identity + ':duplicate_request_id')
        statuses = {}
        for request in requested:
            receipt = request['receipt']
            statuses[receipt['status']] = statuses.get(receipt['status'], 0) + 1
            if int(receipt['id']) != request['id']:
                issues.append(identity + ':receipt_id')
        rows.append({'id': identity, 'life': document['INSTRUMENTO']['life_id'],
                     'numeric_steps': checks, 'old_six': old_six,
                     'old_six_match_inherited_history': old_six == [-1,-1,1,-1,-1,1],
                     'requested': len(requested), 'receipt_statuses': statuses,
                     'unique_new_RAW_observations': raw_count,
                     'after_five_uses': data['after_five_uses'], 'after_panel': data['after_panel']})
    if any(parent != parents[0] for parent in parents[1:]):
        issues.append('Not_equal_physical_prefixes')
    witness_path = root / 'TESTIGOS_FISICOS_POST_USOS.json'
    witnesses = load(witness_path)
    for case in witnesses['cases']:
        for observation in case['sites'].values():
            f = fields(observation['raw'])
            if any(observation[k] != value for k, value in f.items()):
                issues.append(case['id'] + ':fixed_snapshot_witness')
    cut = next(c for c in witnesses['cases'] if c['id'] == 'CUT')['sites']['cut_interaction']
    sources.append({'file': witness_path.name, 'sha256': hashlib.sha256(witness_path.read_bytes()).hexdigest()})
    return {'schema': 'APD01.affine_native_accumulation.archived_recalculation.v1',
            'native_ticks': 0, 'histories': rows, 'sources': sources, 'issues': issues,
            'all_equal_initial_physical_prefixes': not any(parent != parents[0] for parent in parents[1:]),
            'requested': sum(r['requested'] for r in rows),
            'applied': sum(r['receipt_statuses'].get('applied', 0) for r in rows),
            'old_six_queries': sum(len(r['old_six']) for r in rows),
            'old_six_match_queries': sum(sum(x == y for x,y in zip(r['old_six'],[-1,-1,1,-1,-1,1])) for r in rows),
            'RAW_observations_checked': len(seen_raw),
            'cut_fixed_location_observation': cut,
            'scope': 'Six correlated forks from one identical physical prefix. Learned offset content, '
                     'designed turns and cumulative addition. Not acquisition of a general binary operator, '
                     'autonomous initiative, or a test after arbitrary delays/returns. Fixed snapshot '
                     'witnesses are external observations, not an access available to the participant.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidencia', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    if args.salida.exists():
        raise FileExistsError('Use a new archived calculation output')
    result = calculate(args.evidencia)
    args.salida.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('issues','requested','applied','old_six_queries','old_six_match_queries','RAW_observations_checked','native_ticks')}))
    raise SystemExit(bool(result['issues']))
