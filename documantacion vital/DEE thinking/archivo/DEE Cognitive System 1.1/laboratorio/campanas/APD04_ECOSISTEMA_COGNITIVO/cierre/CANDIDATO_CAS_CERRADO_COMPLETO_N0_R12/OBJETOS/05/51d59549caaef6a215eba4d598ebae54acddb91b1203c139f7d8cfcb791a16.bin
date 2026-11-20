"""RAW exacto del panel material heredado ya ejecutado en MAIN; cero ticks.

Exporta la línea original completa, no una transcripción de su resultado.
El recálculo portátil opera únicamente sobre esa línea gzip e índice.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def decode(raw):
    value = int(raw)
    if not 0 <= value < 2**64:
        raise ValueError('Exact uint64 required')
    return value & 0xffffffff, (value >> 60) & 15, [((value >> k) & 15) - (16 if ((value >> k) & 15) >= 8 else 0) for k in (48, 52, 56)]


def recalculate(folder):
    index = json.loads((folder / 'INDICE_LINEA_ORIGINAL.json').read_bytes())
    encoded = (folder / index['exported_line']).read_bytes()
    original_line = gzip.decompress(encoded)
    if sha(encoded) != index['export_sha256'] or sha(original_line) != index['original_line_sha256']:
        raise ValueError('Essential primary line differs')
    event = json.loads(original_line)
    value = event['result']['request']['result']
    if isinstance(value, str):
        value = json.loads(value)
    panel = value['result']['rows'][0]
    rows = []
    for family, key in (('forms', 'form'), ('memories', 'context')):
        for number, item in enumerate(panel[family]):
            reader = item['result']['reader']
            candidates = []
            for observation in reader['panel']:
                state, semantic, direction = decode(observation['raw'])
                if state and semantic == 1 and direction in ([0, 0, -1], [0, 0, 1]):
                    candidates.append({'sign': direction[2], 'site': observation['site'],
                                       'raw': observation['raw'], 'clock': observation.get('clock')})
            sign = candidates[0]['sign'] if len(candidates) == 1 else None
            if sign != reader['formed_native_command']:
                raise ValueError('Exact RAW disagrees with formed_native_command')
            rows.append({'family': family, 'name': item[key], 'candidate_count': len(candidates),
                         'RAW_sign': sign, 'reported_formed_native_command': reader['formed_native_command'],
                         'candidate_observations': candidates, 'reader_uses_target_or_token': reader['reader_uses_target_or_token'],
                         'locator': '$.result.request.result.result.rows[0].' + family + '[' + str(number) + '].result.reader'})
    return {'schema': 'APD04.inherited_material_panel.exact_RAW.N0.R01', 'life': 'APD04_MAIN',
            'primary_line_sha256': sha(original_line), 'request_id': event['requested_id'],
            'rows': rows, 'forms': sum(r['family'] == 'forms' for r in rows),
            'memory_queries': sum(r['family'] == 'memories' for r in rows),
            'unique_formed_forms': sum(r['family'] == 'forms' and r['candidate_count'] == 1 for r in rows),
            'unique_formed_memory_queries': sum(r['family'] == 'memories' and r['candidate_count'] == 1 for r in rows),
            'new_native_ticks': 0, 'new_semantic_primitives_claimed': 0,
            'scope': 'A material panel previously run consecutively in one life, not 22 independent learners, not 18 meanings or NSM65 acquisition. luma/nara are already within the16 inherited forms.'}


def export(root, out):
    path = root / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/MAIN_ADQUISICION_R01/TRAYECTORIA/EVENTOS.jsonl'
    data = path.read_bytes()
    if sha(data) != '09489d4569c1a330dc621fcb95f81fe412b48601b8c0d9ace90c6301ca752e01':
        raise ValueError('Previously closed acquisition log changed')
    matched = [(i, line) for i, line in enumerate(data.splitlines(keepends=True))
               if json.loads(line).get('kind') == 'scheduled_material_result'
               and json.loads(line).get('requested_id') == 'apd04main_old_panel_r01']
    if len(matched) != 1:
        raise ValueError('Expected exactly one already-executed panel result')
    number, original_line = matched[0]
    out.mkdir(parents=True, exist_ok=False)
    encoded = gzip.compress(original_line, compresslevel=9, mtime=0)
    (out / 'PANEL_EVENTO_ORIGINAL.jsonl.gz').write_bytes(encoded)
    dump(out / 'INDICE_LINEA_ORIGINAL.json', {'original': path.relative_to(root).as_posix(),
         'original_log_sha256': sha(data), 'original_log_bytes': len(data), 'zero_based_line': number,
         'original_line_sha256': sha(original_line), 'original_line_bytes': len(original_line),
         'exported_line': 'PANEL_EVENTO_ORIGINAL.jsonl.gz', 'export_sha256': sha(encoded), 'exported_bytes': len(encoded),
         'extraction': 'Exact splitlines(keepends=True) selected by material request ID and completed-result kind; no JSON reserialization.',
         'original_log_remains_local': True})
    result = recalculate(out)
    dump(out / 'RECALCULO_PANEL_HEREDADO.json', result)
    if path.read_bytes() != data:
        raise ValueError('Original log changed during read')
    print(json.dumps({'out': str(out), 'forms': result['unique_formed_forms'], 'memory_queries': result['unique_formed_memory_queries'], 'new_native_ticks': 0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    p = sub.add_parser('export')
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p = sub.add_parser('recalc')
    p.add_argument('--evidence', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.operation == 'export':
        export(args.root.resolve(), args.out.resolve())
    else:
        dump(args.out, recalculate(args.evidence.resolve()))
