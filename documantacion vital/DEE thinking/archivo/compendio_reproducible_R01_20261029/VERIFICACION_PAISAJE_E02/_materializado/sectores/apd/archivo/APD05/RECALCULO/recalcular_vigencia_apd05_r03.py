"""N0 R03: reconcile nonchronological receipt aliases; preserve strict R02 RAW readers.

No actor, Native import or execution. A terminal receipt may coexist with its
scheduled witness in another nested object. Two unequal terminal witnesses are
still an error, as are changed identity fields. Source JSON is never modified.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, importlib.util, json


def load_reader(path):
    spec = importlib.util.spec_from_file_location('strict_r02', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    common36 = module.lexical36
    def lexical_declared_geometry(reader):
        if len(reader['panel']) != 24:
            return common36(reader)
        # Existing APD01 R04 common24 uses only I(8) and J(4), not APD04 K.
        geometries = [((33,33,33), v) for v in ((1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(-1,0,0),(0,-1,0))]
        geometries += [((47,47,47), v) for v in ((-1,0,0),(0,-1,0),(1,0,0),(0,1,0))]
        gates = {tuple((o[i]+4*v[i]+(sign if i==2 else 0))%67 for i in range(3)): sign
                 for o,v in geometries for sign in (-1,1)}
        if len(gates)!=24 or {tuple(o['site']) for o in reader['panel']} != set(gates):
            raise ValueError('Frozen common24 geometry differs')
        candidates=[]
        for observation in reader['panel']:
            f=module.fields(observation); sign=gates[tuple(observation['site'])]
            if f['state']>0 and f['semantic']==1 and f['direction']==[0,0,sign]:
                candidates.append(sign)
        return (candidates[0] if len(candidates)==1 else None),len(candidates)
    module.lexical36 = lexical_declared_geometry
    return module


def normalize(records, reader):
    groups = defaultdict(list)
    for i, event in enumerate(records):
        for locator, node in reader.walk(event, '$[' + str(i) + ']'):
            if isinstance(node, dict) and isinstance(node.get('receipt'), dict) and 'id' in node['receipt']:
                groups[str(node['receipt']['id'])].append({'locator': locator + '.receipt', 'receipt': node['receipt']})
    pending = {'scheduled', 'pending', 'admitted'}
    terminal = {'applied', 'rejected_late', 'rejected_invalid', 'rejected_occupied', 'rejected_conflict', 'rejected_queue_full'}
    resolved = {}
    alias_details = []
    for identity, witnesses in groups.items():
        invariants = [{k: w['receipt'].get(k) for k in ('id', 'kind', 'channels', 'requested_tick')} for w in witnesses]
        if any(x != invariants[0] for x in invariants):
            raise ValueError('Changed Native identity invariants: ' + identity)
        if any(w['receipt'].get('status') not in pending | terminal for w in witnesses):
            raise ValueError('Unknown Native status: ' + identity)
        finals = [w['receipt'] for w in witnesses if w['receipt']['status'] in terminal]
        if finals and any(x != finals[0] for x in finals):
            raise ValueError('Contradictory terminal Native receipt: ' + identity)
        if not finals and any(w['receipt'] != witnesses[0]['receipt'] for w in witnesses):
            raise ValueError('Ambiguous unresolved Native receipt: ' + identity)
        resolved[identity] = finals[0] if finals else witnesses[0]['receipt']
        if finals and any(w['receipt']['status'] in pending for w in witnesses):
            alias_details.append({'id': identity, 'resolved': resolved[identity], 'original_witnesses': witnesses})

    def clone(value, key=None):
        if key in ('result', 'result_json') and isinstance(value, str) and value.lstrip().startswith(('{', '[')):
            value = json.loads(value)
        if isinstance(value, dict):
            if key == 'receipt' and 'id' in value:
                return dict(resolved[str(value['id'])])
            return {k: clone(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [clone(v) for v in value]
        return value
    return clone(records), resolved, alias_details


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('events')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    base = Path(__file__).with_name('recalcular_vigencia_apd05_r02.py')
    reader = load_reader(base)
    raw = Path(args.events).read_bytes()
    records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    normalized, native, aliases = normalize(records, reader)
    summary = reader.summarize(normalized)
    per_event = []
    for i, event in enumerate(normalized):
        ids = {str(node['receipt']['id']) for _, node in reader.walk(event)
               if isinstance(node, dict) and isinstance(node.get('receipt'), dict) and 'id' in node['receipt']}
        per_event.append({'index': i, 'label': event.get('label'), 'id': event.get('id'),
            'Native_ids': len(ids), 'Native_statuses': dict(Counter(native[k]['status'] for k in ids))})
    result = {'schema': 'APD05.exact_RAW_archived_version_recalculation.R03',
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'strict_R02_reader_sha256': hashlib.sha256(base.read_bytes()).hexdigest(),
        'new_Native_ticks': 0, 'receipt_alias_policy': 'Immutable identity fields equal; unique terminal wins over nonchronological scheduled aliases; unequal terminals fail.',
        'scheduled_terminal_alias_groups': aliases, 'event_receipt_denominators': per_event, **summary}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('source_sha256', 'native_ids_unique', 'native_receipt_statuses', 'access_formed', 'access_correct_in_reference20_domain', 'access_useful_environmental_effects')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
