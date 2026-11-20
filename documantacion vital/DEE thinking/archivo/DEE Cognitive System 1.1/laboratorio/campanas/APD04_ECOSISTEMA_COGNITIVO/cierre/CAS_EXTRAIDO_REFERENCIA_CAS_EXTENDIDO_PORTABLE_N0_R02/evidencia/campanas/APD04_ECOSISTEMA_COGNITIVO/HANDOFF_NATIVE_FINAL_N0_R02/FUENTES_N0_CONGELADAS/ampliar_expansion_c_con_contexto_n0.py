"""Complete the exact partial-field C extraction with final cut/operational context."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import zlib

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT = EVIDENCE / 'C_DENSIFICACION_CONTEXTOS_R02_N0'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module);return module


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():yield from walk(child)
    elif isinstance(value, list):
        for child in value:yield from walk(child)


def main():
    if OUT.exists():raise FileExistsError('This exact context extraction exists')
    observer = load('read_saved_snapshot_only', ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py')
    extractor = load('field_metrics_only', Path(__file__).with_name('extraer_campos_expansion_c_n0.py'))
    original = EVIDENCE / 'C_EXPANSION_CAMPOS_EXACTOS_N0'
    index = json.loads((original / 'INDICE_CAMPOS.json').read_text(encoding='utf8'))
    vida = json.loads((ROOT / 'sistema/estado/vidas/APD04_ATENCION_SENSOR02_AUX/VIDA.json').read_text(encoding='utf8'))
    if vida['physical']['tick'] != 648688:
        raise ValueError('The exact final cut differs; no replacement chosen')
    OUT.mkdir()
    for field in index['fields']:shutil.copy2(original / field['file'], OUT / field['file'])
    index['fields'].append({'source_full_snapshot': 'sistema/' + vida['snapshot'],
        'source_full_snapshot_sha256': vida['snapshot_sha256']})
    requested = set()
    primary_members = []
    for op in vida['operations']:
        if op['kind'] != 'PERSISTENT_SESION':continue
        path = ROOT / 'sistema/estado/servicios_persistentes/APD04_ATENCION_SENSOR02_AUX' / op['result_file']
        encoded = path.read_bytes()
        if hashlib.sha256(encoded).hexdigest() != op['result_sha256']:raise ValueError('Primary differs')
        value = json.loads(encoded)
        primary_members.append({'source': path.relative_to(ROOT).as_posix(), 'sha256': op['result_sha256']})
        for row in walk(value):
            if 'id' in row and 'port' in row and isinstance(row.get('receipt'), dict):requested.add(int(row['id']))
    contexts = []
    for field in index['fields']:
        path = ROOT / field['source_full_snapshot']
        snapshot = observer.Snapshot(path)
        if snapshot.encoded_sha256 != field['source_full_snapshot_sha256']:raise ValueError('Exact source differs')
        raw_bytes, clocks_bytes = observer.pbytes(snapshot.raw), observer.pbytes(snapshot.clocks)
        if 'file' not in field:
            field.update(file='C_T648688_RAW_CLOCKS_U64_LE.zlib', N=snapshot.N, tick=snapshot.tick,
                decoded_RAW_sha256=hashlib.sha256(raw_bytes).hexdigest(),
                decoded_clocks_sha256=hashlib.sha256(clocks_bytes).hexdigest(),
                metrics=extractor.metrics(snapshot.raw, snapshot.clocks, snapshot.N, snapshot.tick),
                source_checksum_valid=snapshot.checksum_valid)
            encoded = zlib.compress(raw_bytes + clocks_bytes, 9)
            with (OUT / field['file']).open('xb') as stream:stream.write(encoded)
            field.update(bytes=len(encoded), sha256=hashlib.sha256(encoded).hexdigest())
        channels = snapshot.channels
        metadata = {}
        omitted_keys = []
        for key, value in snapshot.metadata.items():
            if key.startswith('DEE.Cognitive.System.1.1') and any(term in key.lower() for term in ('apd02', 'apd03', 'apd04', 'life.v1')):
                metadata[key] = {'exact_value_string': value,
                    'exact_snapshot_packet_hex': snapshot.metadata_packets[key].hex(),
                    'packet_sha256': hashlib.sha256(snapshot.metadata_packets[key]).hexdigest()}
            else:omitted_keys.append(key)
        context = {'tick': snapshot.tick, 'source_snapshot_sha256': snapshot.encoded_sha256,
            'all_channel_specs_exact': channels, 'all_pending_native_inputs': snapshot.pending,
            'native_receipts_for_committed_C_episode_ids': [r for r in snapshot.receipts if r['id'] in requested],
            'requested_episode_ids_count': len(requested),
            'selected_operational_metadata_exact': metadata,
            'omitted_other_metadata_keys': omitted_keys,
            'total_native_receipt_count_in_original': len(snapshot.receipts),
            'scope': 'Selected original operational packets, all interfaces and pending Native inputs. '
                     'Not all historical receipts or owner metadata; not restorable alone.'}
        name = 'CONTEXTO_T' + str(snapshot.tick) + '.json'
        with (OUT / name).open('x', encoding='utf8') as stream:json.dump(context, stream, ensure_ascii=False, indent=2)
        encoded = (OUT / name).read_bytes()
        contexts.append({'file': name, 'sha256': hashlib.sha256(encoded).hexdigest(), 'bytes': len(encoded)})
    index.update(schema='APD04.C_expansion_exact_fields_operational_context.R02', contexts=contexts)
    index['primary_members'] = primary_members
    index['scope'] += ' Includes selected exact operational packets, all interface specs and pending Native events for three committed cuts; full local snapshots remain indispensable for continuity.'
    with (OUT / 'INDICE_CAMPOS.json').open('x', encoding='utf8') as stream:json.dump(index, stream, ensure_ascii=False, indent=2)
    for name in ('extraer_campos_expansion_c_n0.py', 'ampliar_expansion_c_con_contexto_n0.py'):
        shutil.copy2(Path(__file__).with_name(name), OUT / name)
    print(json.dumps({'folder': str(OUT), 'bytes': sum(p.stat().st_size for p in OUT.iterdir() if p.is_file()),
        'cuts': [f['tick'] for f in index['fields']], 'contexts': contexts, 'Native_ticks': 0}, indent=2))


if __name__ == '__main__':main()
