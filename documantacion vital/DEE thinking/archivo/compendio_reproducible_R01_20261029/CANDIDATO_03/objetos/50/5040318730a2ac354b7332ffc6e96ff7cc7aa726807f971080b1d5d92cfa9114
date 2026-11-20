"""Export exact RAW/clocks before/after C expansion, not restorable snapshots."""
from pathlib import Path
from array import array
from collections import Counter
import argparse
import hashlib
import importlib.util
import json
import sqlite3
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/C_EXPANSION_CAMPOS_EXACTOS_N0'


def metrics(raw, clocks, n, tick):
    state = Counter(int(value & 0xffffffff) for value in raw)
    return {'N': n, 'tick': tick, 'sites': len(raw), 'occupied': len(raw) - state[0],
        'RAW_nonzero': sum(value != 0 for value in raw),
        'state_zero_RAW_nonzero': sum(bool(value) and not value & 0xffffffff for value in raw),
        'states_exact': {str(k): v for k, v in sorted(state.items())}, 'max_s_reg': max((value >> 32) & 65535 for value in raw),
        'clocks_min_max': [str(min(clocks)), str(max(clocks))],
        'clocks_not_equal_to_tick': sum(clock != tick for clock in clocks)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.index:
        index = json.loads(args.index.read_text(encoding='utf8'))
        calculated = []
        for row in index['fields']:
            data = (args.index.parent / row['file']).read_bytes()
            if hashlib.sha256(data).hexdigest() != row['sha256']:
                raise ValueError('Encoded field bytes differ')
            decoded = zlib.decompress(data)
            count = row['N'] ** 3
            if len(decoded) != count * 16:
                raise ValueError('Wrong exact integer-array dimensions')
            if hashlib.sha256(decoded[:count * 8]).hexdigest() != row['decoded_RAW_sha256'] or hashlib.sha256(decoded[count * 8:]).hexdigest() != row['decoded_clocks_sha256']:
                raise ValueError('Exact decoded RAW or clocks source hash differs')
            raw, clocks = array('Q'), array('Q')
            raw.frombytes(decoded[:count * 8]); clocks.frombytes(decoded[count * 8:])
            if sys.byteorder != 'little':raw.byteswap(); clocks.byteswap()
            actual = metrics(raw, clocks, row['N'], row['tick'])
            if actual != row['metrics']:
                raise ValueError('Primary field metrics differ')
            calculated.append(actual)
        output = {'fields': calculated, 'Native_ticks': 0,
                  'full_operational_snapshot': False, 'restorable_as_life': False}
        target = args.out or args.index.parent / 'RECALCULO_CAMPOS.json'
        with target.open('x', encoding='utf8') as stream:json.dump(output, stream, indent=2)
        print(json.dumps(output, indent=2));return
    if OUT.exists():
        raise FileExistsError('The exact-field extraction exists; do not overwrite')
    observer_path = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    spec = importlib.util.spec_from_file_location('exact_offline_snapshot_parser', observer_path)
    observer = importlib.util.module_from_spec(spec); spec.loader.exec_module(observer)
    database = ROOT / 'sistema/estado/servicios_persistentes/APD04_ATENCION_SENSOR02_AUX/cola.sqlite3'
    with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as connection:
        records = [json.loads(connection.execute('select result from requests where id=?', (identifier,)).fetchone()[0])
            for identifier in ('apd04_attention_C_2_goal0_first4', 'apd04_attention_C_3_goal0_next2')]
    OUT.mkdir()
    fields = []
    for record in records:
        state = record['committed_snapshot']
        source = ROOT / 'sistema' / state['snapshot']
        snapshot = observer.Snapshot(source)
        if snapshot.encoded_sha256 != state['snapshot_sha256']:
            raise ValueError('Committed source snapshot differs')
        raw_bytes, clock_bytes = observer.pbytes(snapshot.raw), observer.pbytes(snapshot.clocks)
        encoded = zlib.compress(raw_bytes + clock_bytes, level=9)
        name = 'C_T' + str(snapshot.tick) + '_RAW_CLOCKS_U64_LE.zlib'
        with (OUT / name).open('xb') as stream:stream.write(encoded)
        fields.append({'file': name, 'sha256': hashlib.sha256(encoded).hexdigest(), 'bytes': len(encoded),
            'source_full_snapshot': source.relative_to(ROOT).as_posix(),
            'source_full_snapshot_sha256': snapshot.encoded_sha256,
            'source_checksum_valid': snapshot.checksum_valid, 'N': snapshot.N, 'tick': snapshot.tick,
            'decoded_RAW_sha256': hashlib.sha256(raw_bytes).hexdigest(),
            'decoded_clocks_sha256': hashlib.sha256(clock_bytes).hexdigest(),
            'metrics': metrics(snapshot.raw, snapshot.clocks, snapshot.N, snapshot.tick)})
    index = {'schema': 'APD04.exact_partial_fields.before_after_C.v1', 'fields': fields,
        'encoding': 'zlib of concatenated N**3 uint64 little-endian RAW then N**3 uint64 clocks',
        'scope': 'Exact observational fields only, not a full operational snapshot. Queues, interfaces, '
                 'metadata, protocol progress and receipts remain in local complete originals. Cannot continue a life.',
        'Native_ticks': 0}
    with (OUT / 'INDICE_CAMPOS.json').open('x', encoding='utf8') as stream:json.dump(index, stream, indent=2)
    print(json.dumps(fields, indent=2))


if __name__ == '__main__':
    main()
