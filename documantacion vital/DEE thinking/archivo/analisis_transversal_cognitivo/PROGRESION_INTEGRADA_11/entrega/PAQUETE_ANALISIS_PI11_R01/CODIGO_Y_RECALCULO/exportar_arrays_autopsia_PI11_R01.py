"""Lossless, portable PI11 auditor arrays; Python standard library only.

Export reads five frozen full snapshots referenced by the literal R01 autopsy,
then compares reconstructed arrays byte for byte before creating a NEW JSON.
The export is not an operational snapshot: no agenda, interfaces, receipts,
metadata, resource files or restoration is supplied.

From an extracted archive, with no source snapshots or original P paths:
  python codigo/exportar_arrays_autopsia_PI11_R01.py --verify-export fuentes/ARRAYS_AUTOPSIA_COMPACTOS_PI11_R01.json
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import struct
import zlib

SCHEMA = 'DEE.PI11.passive.lossless_auditor_arrays.R01'
TICKS = (972419, 975259, 977111, 978675, 979389)
AUTOPSY_SHA = '448678cfe20352d7f932494c683b73bb4239b9b371db91977261bee50488551a'
AUTOPSY_CODE_SHA = '3632d7977e38691a87659e911293acd4a2718565741d03447290cff51665694b'
UINT64_MAX = (1 << 64) - 1

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text('utf-8-sig'))

def exact_snapshot_arrays(path, expected_sha):
    encoded = Path(path).read_bytes()
    need(sha(encoded) == expected_sha, 'Frozen source snapshot SHA256 mismatch')
    need(len(encoded) <= 32 * 1024 * 1024, 'Bounded frozen encoded snapshot required')
    is_gzip = encoded[:2] == b'\x1f\x8b'
    need(is_gzip, 'Declared gzip snapshot required')
    data = gzip.decompress(encoded)  # Includes gzip CRC/length verification.
    need(len(data) <= 128 * 1024 * 1024, 'Bounded decoded snapshot required')
    need(data[:8] == b'DEETSNP1', 'Known DEETSNP1 magic required')
    version, n = struct.unpack_from('<II', data, 8)
    tick = struct.unpack_from('<Q', data, 16)[0]
    need(version == 2 and n == 67, 'Known full N67 snapshot v2 required')
    text_bytes = struct.unpack_from('<I', data, 41)[0]
    need(text_bytes <= 1024, 'Bounded phase text required')
    phase = data[45:45 + text_bytes].decode('utf8')
    sites_offset = 45 + text_bytes
    sites = struct.unpack_from('<Q', data, sites_offset)[0]
    need(sites == n ** 3, 'Complete source array dimensions required')
    raw_offset = sites_offset + 8
    clocks_offset = raw_offset + sites * 8
    need(clocks_offset + sites * 8 <= len(data) - 8, 'Source arrays truncated')
    raw = data[raw_offset:clocks_offset]
    clocks = data[clocks_offset:clocks_offset + sites * 8]
    return {
        'N': n, 'T': tick, 'sites': sites, 'snapshot_version': version,
        'snapshot_phase': phase, 'decoded_snapshot_bytes': len(data),
        'source_RAW_byte_offset': raw_offset,
        'source_clocks_byte_offset': clocks_offset,
        'source_gzip_CRC_checked': True,
        'source_internal_FNV_recalculated': False,
    }, raw, clocks

def reconstruct(row):
    """Uses only the exported row. Never accesses source snapshots or P paths."""
    need(row['N'] == 67 and row['sites'] == row['N'] ** 3 == 300763, 'Complete N67 array header required')
    need(row['T'] in TICKS, 'Declared finite audit cut only')
    need(row['endianness'] == 'little' and row['word_bits'] == 64, 'Exact <Q words required')
    need(row['flattening'] == 'index=(x*N+y)*N+z', 'Exact linear coordinate order required')
    need(row['RAW_encoding'] == 'sorted_index_decimal_uint64_pairs; absent_indices_are_exact_zero', 'Exact sparse RAW encoding required')
    sparse = row['RAW_nonzero']
    need(isinstance(sparse, list) and len(sparse) <= row['sites'], 'Finite sparse RAW array required')
    raw = bytearray(row['sites'] * 8)
    previous = -1
    active = 0
    for pair in sparse:
        need(isinstance(pair, list) and len(pair) == 2, 'Exact index/value pair required')
        index, decimal = pair
        need(type(index) is int and previous < index < row['sites'], 'Sorted unique in-range indices required')
        need(isinstance(decimal, str) and decimal.isascii() and decimal.isdecimal(), 'Exact decimal uint64 string required')
        value = int(decimal)
        need(0 < value <= UINT64_MAX and str(value) == decimal, 'Canonical nonzero uint64 required')
        struct.pack_into('<Q', raw, index * 8, value)
        active += bool(value & 0xffffffff)
        previous = index
    clock = row['clocks_uniform']
    need(set(clock) == {'encoding', 'value', 'count'}, 'Exact uniform clock encoding required')
    need(clock['encoding'] == 'repeat_uint64' and clock['count'] == row['sites'], 'Complete uniform clocks required')
    need(type(clock['value']) is int and clock['value'] == row['T'], 'Uniform source clocks must equal the cut tick')
    clocks = struct.pack('<Q', clock['value']) * clock['count']
    counts = {'RAW_nonzero_support': len(sparse), 'active_STATE_nonzero': active,
              'STATE0_RAW_nonzero': len(sparse) - active}
    need(counts == row['counts'], 'Reconstructed counts mismatch')
    need(sha(raw) == row['RAW_sha256'], 'Reconstructed complete RAW SHA256 mismatch')
    need(sha(clocks) == row['clocks_sha256'], 'Reconstructed complete clocks SHA256 mismatch')
    return bytes(raw), clocks, counts

def verify_export(path):
    """Portable mode: the JSON itself is the only data file read."""
    encoded = Path(path).read_bytes()
    export = json.loads(encoded.decode('utf-8-sig'))
    need(export['schema'] == SCHEMA, 'Exact auditor export schema required')
    need(export['operational_snapshot'] is False and export['new_Native_ticks'] == 0, 'Passive auditor scope required')
    need(export['autopsy']['sha256'] == AUTOPSY_SHA, 'Literal original R01 autopsy binding required')
    need([row['T'] for row in export['cuts']] == list(TICKS), 'Exactly the five declared cuts required')
    rows = []
    for row in export['cuts']:
        raw, clocks, counts = reconstruct(row)
        rows.append({'T': row['T'], 'sites': row['sites'], **counts,
                     'RAW_bytes': len(raw), 'clocks_bytes': len(clocks),
                     'RAW_sha256': sha(raw), 'clocks_sha256': sha(clocks),
                     'complete_reconstruction_hashes_verified': True})
    return {'schema': SCHEMA + '.verification', 'export_file': str(path),
            'export_sha256': sha(encoded), 'only_export_JSON_read': True,
            'source_snapshot_paths_required': False, 'Native_executed': False,
            'new_Native_ticks': 0, 'DEE_imports': 0, 'cuts': rows}

def export_arrays(autopsy_path, output_path):
    autopsy_path, output_path = Path(autopsy_path), Path(output_path)
    need(not output_path.exists(), 'Never overwrite existing auditor evidence')
    autopsy_bytes = autopsy_path.read_bytes()
    need(sha(autopsy_bytes) == AUTOPSY_SHA, 'Original R01 autopsy must remain literal')
    autopsy = json.loads(autopsy_bytes.decode('utf-8-sig'))
    original_code = Path(autopsy['recalculation_script']['path'])
    need(sha(original_code.read_bytes()) == AUTOPSY_CODE_SHA, 'Original R01 recalculation code must remain literal')
    by_tick = {x['tick']: x for x in autopsy['complete_snapshot_cuts']}
    cuts = []
    for tick in TICKS:
        prior = by_tick[tick]
        snapshot_path = Path(prior['source']['path'])
        header, original_raw, original_clocks = exact_snapshot_arrays(snapshot_path, prior['source']['sha256'])
        need(header['T'] == tick, 'Source cut tick mismatch')
        need(original_clocks == struct.pack('<Q', tick) * header['sites'], 'Source clocks are not exactly uniform; export refused')
        sparse = [[index, str(word[0])] for index, word in enumerate(struct.iter_unpack('<Q', original_raw)) if word[0]]
        active = sum(bool(int(pair[1]) & 0xffffffff) for pair in sparse)
        row = {**header, 'endianness': 'little', 'word_bits': 64,
               'flattening': 'index=(x*N+y)*N+z',
               'source_snapshot': {'basename': snapshot_path.name, 'sha256': prior['source']['sha256'],
                                   'encoded_bytes': prior['source']['bytes']},
               'RAW_encoding': 'sorted_index_decimal_uint64_pairs; absent_indices_are_exact_zero',
               'RAW_nonzero': sparse,
               'clocks_uniform': {'encoding': 'repeat_uint64', 'value': tick, 'count': header['sites']},
               'RAW_sha256': sha(original_raw), 'clocks_sha256': sha(original_clocks),
               'counts': {'RAW_nonzero_support': len(sparse), 'active_STATE_nonzero': active,
                          'STATE0_RAW_nonzero': len(sparse) - active},
               'complete_reconstruction_bytes_equal_source': True}
        need(row['RAW_sha256'] == prior['RAW_sha256'] and row['clocks_sha256'] == prior['clocks_sha256'], 'Autopsy source arrays mismatch')
        reconstructed_raw, reconstructed_clocks, counts = reconstruct(row)
        need(reconstructed_raw == original_raw and reconstructed_clocks == original_clocks, 'Byte-for-byte lossless reconstruction failed')
        for key, count in counts.items():
            need(count == prior[key], 'Autopsy occupation count mismatch')
        need(sha(snapshot_path.read_bytes()) == prior['source']['sha256'], 'Source snapshot changed during export')
        cuts.append(row)
    value = {'schema': SCHEMA, 'operational_snapshot': False, 'new_Native_ticks': 0,
             'DEE_imports': 0, 'owner_calls': 0, 'SQLite_opened': False,
             'scope': 'Lossless complete physical RAW/clocks arrays for auditor occupation metrology only. No operational world, agenda, interfaces, receipts, metadata, environmental resources or cognitive-state completeness is supplied.',
             'autopsy': {'basename': autopsy_path.name, 'sha256': AUTOPSY_SHA,
                         'original_recalculation_code_sha256': AUTOPSY_CODE_SHA},
             'export_code': {'basename': Path(__file__).name, 'sha256': sha(Path(__file__).read_bytes())},
             'hashes': {'algorithm': 'SHA256', 'input': 'Complete N^3 uint64 words in little-endian linear index order; no headers included'},
             'STATE_definition': 'STATE=RAW & 0xffffffff; active iff STATE != 0. RAW!=0 includes STATE0 fields and is not a cognitive capacity metric.',
             'verification_before_write': 'Reconstructed all complete RAW/clocks bytes from sparse/uniform rows and compared byte for byte with source snapshot arrays. All array hashes and counts also matched the frozen R01 autopsy.',
             'cuts': cuts}
    need(sha(autopsy_path.read_bytes()) == AUTOPSY_SHA and sha(original_code.read_bytes()) == AUTOPSY_CODE_SHA, 'Original autopsy evidence changed')
    # Compact JSON is intentionally exact and readily compressed by the ZIP.
    encoded = (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode('utf8')
    with output_path.open('xb') as handle:
        handle.write(encoded)
    verification = verify_export(output_path)
    verification['export_bytes'] = len(encoded)
    verification['deflate_bytes_at_level9'] = len(zlib.compress(encoded, 9))
    return verification

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-export', type=Path, help='Portable relative JSON; no snapshots or original P paths needed')
    parser.add_argument('--autopsy', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.verify_export is not None:
        need(args.autopsy is None and args.output is None, 'Portable verify mode reads only the specified JSON')
        result = verify_export(args.verify_export)
    else:
        root = Path(__file__).resolve().parents[1]
        result = export_arrays(args.autopsy or root / 'fuentes/AUTOPSIA_CIERRE_PI11_R01.json',
                               args.output or root / 'fuentes/ARRAYS_AUTOPSIA_COMPACTOS_PI11_R01.json')
    print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))

if __name__ == '__main__':
    main()
