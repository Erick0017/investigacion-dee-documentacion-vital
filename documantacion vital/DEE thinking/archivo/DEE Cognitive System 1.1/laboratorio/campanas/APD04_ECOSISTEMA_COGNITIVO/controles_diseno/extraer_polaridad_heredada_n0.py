"""Extract only existing APD03 decisive RAW observations, never imports Native."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def walk(obj, path='$'):
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, path + '.' + str(k))
    elif isinstance(obj, list):
        for k, v in enumerate(obj):
            yield from walk(v, path + '[' + str(k) + ']')


def decode(obs):
    n = int(obs['raw'])
    if not 0 <= n < 2 ** 64:
        raise ValueError('non uint64 RAW')
    return {'raw': str(n), 'state': n & 0xffffffff,
            'semantic': (n >> 60) & 15, 's_reg': (n >> 32) & 65535,
            'direction': [((n >> k) & 15) - (16 if ((n >> k) & 15) >= 8 else 0)
                          for k in (48, 52, 56)]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('events')
    p.add_argument('output')
    args = p.parse_args()
    rows = []
    for file in sorted(Path(args.events).glob('*.json.gz')):
        event = json.loads(gzip.decompress(file.read_bytes()))
        decoded_event = event
        try:
            wrapped = event['result']['request']['result']
            decoded_event = json.loads(wrapped)['result']
        except (KeyError, TypeError, json.JSONDecodeError):
            pass
        for path, node in walk(decoded_event):
            if not isinstance(node, dict) or node.get('kind') not in ('native_current_selection', 'native_joint_raw_perception'):
                continue
            candidates = []
            reader = node.get('reader', {})
            for obs in reader.get('observations', []):
                data = decode(obs)
                for x in (-1, 0, 1):
                    for z in (0, -1):
                        if (obs['site'] == [15 + 2*x, 17, 15 + 2*z] and
                                data['state'] and data['semantic'] == 1 and data['direction'] == [x, 1, z]):
                            candidates.append({'choice': x, 'observation': obs, 'decoded': data})
            row = {'source': str(file.resolve()), 'source_sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                   'event_tag': event.get('tag'), 'event_transport': event.get('id', event.get('transport_id')),
                   'object_path': path, 'kind': node['kind'], 'read_tick': node['read_tick'],
                   'datum': node.get('raw_sensor_value'),
                   'raw_components': node.get('raw_components'), 'level': node.get('level'),
                   'reported_choice': reader.get('choice'),
                   'RAW_recalculated_choice': candidates[0]['choice'] if len(candidates) == 1 else None,
                   'candidates': candidates, 'references_pre': node.get('references_pre'),
                   'requests': node.get('requests'),
                   'aggregate_C': [f['fields']['C'] for f in node.get('frames', [])
                                   if f['tick'] == node.get('datum_tick', -1) - 2 and 'C' in f.get('fields', {})]}
            rows.append(row)
    output = {'schema': 'DEE.APD04.inherited_polarity.N0.R01', 'new_native_ticks': 0,
              'scope': 'Existing snapshots/events only, not a promise for untested values or changed history.',
              'rows': rows}
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    for row in rows:
        print(json.dumps({k: row[k] for k in ('source', 'event_tag', 'object_path', 'kind', 'read_tick', 'datum',
                                            'level', 'reported_choice', 'RAW_recalculated_choice', 'aggregate_C')}, ensure_ascii=False))
    print('rows', len(rows))


if __name__ == '__main__':
    main()
