"""N0: expose eight already archived actual goal artifacts as readable JSON.

Copies original bytes from the closed pair, never from targets or json.dumps.
The compact exported witnesses are extractions of existing archived primaries;
this is desnormalization, not a new discovery or new Native execution.
"""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import shutil


PAIR_SHA = '9610905c1c3879fd4de3062894c2978c8cb5187e068185cfe889b7b2ee80a085'
SNAPSHOT_SHA = 'c7cf2e78837ed5f99c950016314bfe5f8fbfa868f72a67af36a94a78261a24ba'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def walk(value, path='$'):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, path + '[' + json.dumps(key) + ']')
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, path + '[' + str(i) + ']')


def sources(stage):
    primary = stage / 'EVIDENCIA_MAIN'
    for path in sorted((primary / 'EVENTOS').glob('*.json.gz')):
        event = read(path)
        if event.get('kind') == 'material':
            yield path, path.relative_to(stage).as_posix(), event.get('decoded_result'), event.get('id')
    path = primary / 'SESIONES_UI_NUEVAS.jsonl.gz'
    for line, text in enumerate(gzip.decompress(path.read_bytes()).decode('utf8').splitlines()):
        if not text.strip():
            continue
        event = json.loads(text)
        if event.get('event') not in ('literal_material_result', 'same_id_read_only_result'):
            continue
        result = event.get('result') or {}
        request = result.get('request') or result
        if request.get('status') != 'completed' or request.get('is_control') or not request.get('result'):
            continue
        value = request['result']
        value = json.loads(value) if isinstance(value, str) else value
        locator = path.relative_to(stage).as_posix() + '#line' + str(line) + '/request.result(JSON)'
        yield path, locator, value, request.get('id')


def extract(args):
    if args.out.exists():
        raise FileExistsError('Use a new extraction directory; never overwrite a closed result.')
    manifest_path = args.paired / 'EXPORTACION_SERVICIO.json'
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if sha(manifest_bytes) != PAIR_SHA or manifest['life_id'] != 'APD03_MAIN' or manifest['snapshot_sha256'] != SNAPSHOT_SHA:
        raise ValueError('Not the confirmed closed Main T604825 pair.')
    members = [m for m in manifest['members'] if m['file'].startswith('artefactos_trabajador/apd03_step_') and m['file'].endswith('.json')]
    if len(members) != 8:
        raise ValueError('Expected exactly eight actual Main goal JSON members.')
    found = {}
    for path, locator, payload, transport_id in sources(args.main_stage):
        if not isinstance(payload, dict):
            continue
        blobs = {(r['relative_path'], r['sha256']): r for _, r in walk(payload)
                 if {'relative_path', 'content_base64', 'sha256', 'bytes'} <= r.keys()}
        for pointer, row in walk(payload):
            for i, opportunity in enumerate(row.get('opportunities', [])):
                effect = opportunity.get('environment_effect') or {}
                committed = effect.get('committed_effect') or {}
                artifact = committed.get('artifact')
                if not artifact:
                    continue
                task_id = committed['task_id']
                if not task_id.startswith('apd03_goal_'):
                    continue
                matches = [m for m in members if Path(m['file']).name == task_id + '.json']
                if len(matches) != 1:
                    raise ValueError('Actual pair member is missing or ambiguous: ' + task_id)
                member = matches[0]
                data = (args.paired / member['file']).read_bytes()
                blob = blobs.get((artifact['relative_path'], artifact['sha256']))
                if blob is None:
                    raise ValueError('Exact original artifact base64 omitted in primary: ' + task_id)
                primary_bytes = base64.b64decode(blob['content_base64'], validate=True)
                if data != primary_bytes or sha(data) != member['sha256'] or sha(data) != artifact['sha256'] or len(data) != member['bytes'] or len(data) != blob['bytes']:
                    raise ValueError('Actual pair, primary base64, committed receipt or member differ: ' + task_id)
                records = opportunity['native_numeric']
                if len(records) != 1:
                    raise ValueError('Expected one actual native numerical operation per committed goal.')
                number = records[0]
                trial = number['native_trial']
                frames = [frame for frame in trial['frames'] if frame['tick'] == trial['datum_tick'] - 2]
                if len(frames) != 1:
                    raise ValueError('Native RAW witness frame is missing or ambiguous.')
                witness = {'operation': number['operation'], 'datum_tick': trial['datum_tick'],
                           'frame': frames[0], 'reported_numeric_result': number['numeric_reader']['numeric_result']}
                record = {'task_id': task_id, 'file': 'FILES/' + task_id + '.json', 'bytes': len(data), 'sha256': sha(data),
                          'pair_member': member, 'source_primary_file': str(path.resolve()),
                          'source_primary_locator_in_Main_stage': locator, 'source_primary_sha256': sha(path.read_bytes()),
                          'source_json_pointer': pointer + '["opportunities"][' + str(i) + ']',
                          'transport_id': transport_id, 'artifact_blob': blob, 'committed_artifact_receipt': artifact,
                          'native_numeric_witness': witness, 'native_numeric_witness_extraction_sha256': sha(json.dumps(witness, sort_keys=True, separators=(',', ':')).encode('utf8'))}
                if task_id in found and found[task_id]['sha256'] != record['sha256']:
                    raise ValueError('Same task has divergent actual original bytes.')
                found[task_id] = record
    if len(found) != 8:
        raise ValueError('Not all eight actual files are backed by archived exact primary base64 and Native RAW.')
    args.out.mkdir(parents=True)
    for record in sorted(found.values(), key=lambda r: r['task_id']):
        source = args.paired / record['pair_member']['file']
        dest = args.out / record['file']
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    index = {'schema': 'APD03.actual_goal_files_desnormalization.N0.R01', 'new_native_ticks': 0,
             'scope': 'Readable copies of original bytes already embedded in closed Main primaries; no new evidence discovery, target reconstruction or operational backup.',
             'source_pair_manifest': str(manifest_path.resolve()), 'source_pair_manifest_sha256': PAIR_SHA,
             'source_snapshot_sha256': SNAPSHOT_SHA, 'life': 'APD03_MAIN', 'tick': 604825,
             'witness_extraction_not_original_JSON_serialization': True,
             'files': sorted(found.values(), key=lambda r: r['task_id'])}
    write_new(args.out / 'INDICE_Y_EXTRACCIONES_PRIMARIAS.json', index)
    shutil.copyfile(Path(__file__), args.out / Path(__file__).name)
    write_new(args.out / 'RECALCULO_ARCHIVOS_GOAL.json', recalculate(args.out))
    print(json.dumps({'actual_files': len(found), 'original_bytes': sum(r['bytes'] for r in found.values()), 'new_native_ticks': 0}))


def write_new(path, value):
    with Path(path).open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')


def recalculate(evidence):
    index = read(evidence / 'INDICE_Y_EXTRACCIONES_PRIMARIAS.json')
    issues = []
    checks = 0
    rows = []
    def check(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            issues.append(message)
    check(len(index['files']) == 8, 'Not eight exported actual goals')
    for row in index['files']:
        path = (evidence / row['file']).resolve()
        check(path.is_relative_to(evidence.resolve()), 'Exported path escaped evidence')
        data = path.read_bytes()
        blob = base64.b64decode(row['artifact_blob']['content_base64'], validate=True)
        check(data == blob, row['task_id'] + ': exact bytes differ from archived primary base64')
        check(len(data) == row['bytes'] == row['pair_member']['bytes'] == row['artifact_blob']['bytes'], row['task_id'] + ': bytes differ')
        hashes = [row['sha256'], row['pair_member']['sha256'], row['artifact_blob']['sha256'], row['committed_artifact_receipt']['sha256']]
        check(all(value == sha(data) for value in hashes), row['task_id'] + ': original hashes differ')
        native = row['native_numeric_witness']
        check(sha(json.dumps(native, sort_keys=True, separators=(',', ':')).encode('utf8')) == row['native_numeric_witness_extraction_sha256'], row['task_id'] + ': extracted witness hash differs')
        frame = native['frame']
        field = frame['fields']['C']
        raw = int(field['raw'])
        direction = [((raw >> bit) & 15) - (16 if ((raw >> bit) & 15) >= 8 else 0) for bit in (48, 52, 56)]
        tick = native['datum_tick'] - 2
        check(frame['tick'] == field['tick'] == tick and field['site'] == [12, 17, 18], row['task_id'] + ': Native C geometry/tick differs')
        check(raw & 0xffffffff != 0 and (raw >> 60) & 15 == 1 and direction == [1, -1, -1], row['task_id'] + ': Native C class differs')
        s_reg = (raw >> 32) & 65535
        value = s_reg if native['operation'] == 'suma' else s_reg - 32
        actual = json.loads(data)
        check(value == native['reported_numeric_result'] == actual['value'], row['task_id'] + ': Native RAW numerical result differs from original file')
        check(actual['task_id'] == row['task_id'] and actual['procedure'] == 'native', row['task_id'] + ': original artifact identity differs')
        check(actual['operation'] == ('add' if native['operation'] == 'suma' else 'sub'), row['task_id'] + ': operation differs from Native record')
        left, second = actual['operands']
        check(actual['value'] == (left + second if actual['operation'] == 'add' else left - second), row['task_id'] + ': original committed arithmetic incorrect')
        rows.append({'task_id': row['task_id'], 'value': value, 'bytes': len(data), 'sha256': sha(data),
                     'source_primary_sha256': row['source_primary_sha256'], 'native_raw_C': raw, 'native_tick': tick})
    return {'schema': 'APD03.actual_goal_files_recalculation.N0.R01', 'new_native_ticks': 0,
            'checks': checks, 'issues': issues, 'files': rows, 'source_pair_manifest_sha256': index['source_pair_manifest_sha256'],
            'original_primary_files_not_duplicated': True, 'witness_scope': 'Exact decoded fragments with source hashes/localizers, not independent full trajectory or continuation state.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('extraer')
    build.add_argument('--paired', type=Path, required=True)
    build.add_argument('--main-stage', type=Path, required=True)
    build.add_argument('--out', type=Path, required=True)
    verify = commands.add_parser('recalcular')
    verify.add_argument('--evidence', type=Path, required=True)
    verify.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'extraer':
        extract(args)
    else:
        result = recalculate(args.evidence)
        write_new(args.out, result)
        print(json.dumps({'checks': result['checks'], 'issues': result['issues'], 'new_native_ticks': 0}))


if __name__ == '__main__':
    main()
