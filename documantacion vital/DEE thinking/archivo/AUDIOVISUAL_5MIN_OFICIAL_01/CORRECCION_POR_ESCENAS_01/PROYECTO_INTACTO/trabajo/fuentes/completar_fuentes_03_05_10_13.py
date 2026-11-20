"""Directed stdlib extraction of two preserved snapshot-v2 field buffers.

No engine, runtime, owner, query, tick API, external module, or simulation import.
Only the known binary prefix is decoded; its full native checksum is verified.
The remainder is retained by its complete-file hashes, not semantically parsed.
"""
from pathlib import Path
from array import array
from collections import Counter
import base64
import gzip
import hashlib
import json
import struct
import sys

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[2]
THINK = ARCHIVE.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    b = Path(path).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)


def pointer(value, path):
    if path in ('', '/'):
        return value
    for token in path.strip('/').split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def fields(raw):
    def direction(shift):
        v = (raw >> shift) & 15
        return v - 16 if v & 8 else v
    return {'raw': str(raw), 'rawstr': str(raw), 'state': raw & 0xffffffff,
            's_reg': (raw >> 32) & 65535,
            'direction': [direction(i) for i in (48, 52, 56)],
            'semantic': (raw >> 60) & 15}


def parse_fields(path, expected, expected_encoded_sha):
    encoded = path.read_bytes()
    assert sha(encoded) == expected_encoded_sha, ('encoded checksum', str(path))
    native = gzip.decompress(encoded)
    # Snapshot-v2 FNV64 is checked over ALL native bytes except the trailer.
    h = 1469598103934665603
    for v in memoryview(native)[:-8]:
        h = ((h ^ v) * 1099511628211) & ((1 << 64) - 1)
    assert h == struct.unpack_from('<Q', native, len(native) - 8)[0], 'native checksum'
    offset = 0

    def take(n):
        nonlocal offset
        assert 0 <= n <= len(native) - 8 - offset, 'prefix bounds'
        b = native[offset:offset+n]
        offset += n
        return b

    def number(fmt):
        return struct.unpack(fmt, take(struct.calcsize(fmt)))[0]

    assert take(8) == b'DEETSNP1'
    assert number('<I') == 2
    n = number('<I')
    tick = number('<Q')
    paused = number('<B')
    next_event_id = number('<Q')
    next_sequence = number('<Q')
    text_size = number('<I')
    assert text_size < 16 * 1024 * 1024
    phase = take(text_size).decode('utf8')
    total = number('<Q')
    assert total == n**3 and total <= 128**3 * 4
    raw_offset = offset
    raw_bytes = take(total * 8)
    clock_offset = offset
    clock_bytes = take(total * 8)
    raw = array('Q'); raw.frombytes(raw_bytes)
    clocks = array('Q'); clocks.frombytes(clock_bytes)
    if sys.byteorder != 'little':
        raw.byteswap(); clocks.byteswap()
    summary = {'N': n, 'tick': tick, 'RAW_sha256': sha(raw_bytes),
               'clocks_sha256': sha(clock_bytes), 'sites': total,
               'occupied': sum(bool(v & 0xffffffff) for v in raw),
               'max_s_reg': max((v >> 32) & 65535 for v in raw),
               'raw_nonzero': sum(v != 0 for v in raw),
               'state_zero_raw_nonzero': sum(v != 0 and not(v & 0xffffffff) for v in raw)}
    for key in ('N', 'tick', 'RAW_sha256', 'clocks_sha256'):
        assert summary[key] == expected[key], (key, summary[key], expected[key])
    for key in ('occupied', 'max_s_reg'):
        if key in expected:
            assert summary[key] == expected[key]

    def point(site):
        i = (site[0] * n + site[1]) * n + site[2]
        return {'site': list(site), 'tick': tick, 'clock': str(clocks[i]),
                'clockstr': str(clocks[i]), **fields(raw[i])}

    points = [point([i//(n*n), (i//n) % n, i % n])
              for i, v in enumerate(raw) if v]
    buffers = {}
    for name, data, start in [('RAW', raw_bytes, raw_offset), ('clocks', clock_bytes, clock_offset)]:
        buffers[name] = {'codec': 'uint64-little-endian+gzip+base64', 'bytes': len(data),
                         'sha256': sha(data), 'native_offset': start,
                         'data': base64.b64encode(gzip.compress(data, mtime=0)).decode('ascii')}
    result = {'source': {'path': str(path), 'encoded_sha256': sha(encoded),
                        'encoded_bytes': len(encoded), 'native_sha256': sha(native),
                        'native_bytes': len(native), 'native_FNV64_checked': True,
                        'gzip_CRC_checked': True, 'format': 'DEETSNP1 / version2'},
              'summary': summary, 'prefix': {'paused': paused, 'next_event_id': next_event_id,
                                            'next_sequence': next_sequence, 'phase': phase},
              'classification': 'Registro', 'points': points,
              'occupied_points': [p for p in points if p['state'] != 0],
              'complete_buffers': buffers,
              'coverage': 'Every nonzero RAW in the complete N^3 field; all RAW and clocks also preserved exactly.',
              'limits': ['No trajectory is reconstructed between this cut and another cut.',
                         'Nonzero RAW/state0 is retained and is not relabelled occupied matter.',
                         'Channel/metadata/owner remainder is not semantically parsed by this prefix decoder.']}
    return result, point


def main():
    target = HERE / 'ESCENAS_03_05_10_13.json'
    original = target.read_bytes()
    assert sha(original) == 'e36d42520dc041b38c613324e90fff5b76ef52be8ebee37185ed545e3225c725'
    revisions = HERE / 'revisiones'
    revisions.mkdir(exist_ok=True)
    with (revisions / 'ESCENAS_03_05_10_13_R01.json').open('xb') as f:
        f.write(original)
    d = json.loads(original)
    publication_path = ARCHIVE/'analisis_transversal_cognitivo/ECI02/datos/PRUEBA_PUBLICACION_P1_ECI02_R01.json'
    publication = read_json(publication_path)
    s3 = d['scenes']['S03']
    minus_derived_path = Path(d['input_files_read_and_hashed'][5]['path'])
    minus_derived = read_json(minus_derived_path)['sources'][1]
    native_transaction = json.loads(publication['cycles'][1]['terminal_request']['result'])
    assert native_transaction['result'] == minus_derived['cycles'][1]['recorded_result']
    assert native_transaction['result'] == s3['native_result_exact_for_reader_context']
    s3['stages'][0]['source_pointer'] = '/cycles/0/after/physical'
    s3['stages'][1]['source_pointer'] = '/cycles/1/before/physical'
    s3['stages'][3]['source_pointer'] = '/cycles/1/after/physical'
    for i, phase in [(0, ('0','after')), (1, ('1','before')), (3, ('1','after'))]:
        c, part = phase
        rec = publication['cycles'][int(c)][part]
        assert rec['physical'] == s3['stages'][i]['physical_state_descriptor']
        s3['stages'][i]['life_record_locator'] = {'path': str(publication_path),
            'sha256': s3['source']['sha256'], 'pointer': f'/cycles/{c}/{part}'}
        s3['stages'][i]['life_record_identity'] = {k:rec[k] for k in
            ('life_id','world_id','profile','branch','parent','snapshot','snapshot_sha256','storage')}
    s3['stages'][2]['source_pointer'] = '/cycles/1/terminal_request/result'
    s3['stages'][2]['source_decoding'] = {'codec': 'JSON-serialized string', 'decoded_pointer': '/result'}
    for item in s3['stages'][2]['points_with_exact_local_pointers']:
        original_point = pointer(native_transaction['result'], item['pointer'])
        for k, v in original_point.items():
            assert item['point'][k] == v
        item['source'] = {'path': str(publication_path), 'sha256': s3['source']['sha256'],
                          'pointer': '/cycles/1/terminal_request/result', 'decode': 'JSON',
                          'decoded_pointer': '/result' + item['pointer']}
    s3['identity_evidence']['before_first_use_exact_pair_verification_scope'] = (
        'Initial imported pair at720324; not an independent full owner/queue equality check after720458 reopen.')
    saved_record = publication['cycles'][0]['after']
    snapshot_path = THINK/'DEE Cognitive 2.0/sistema'/saved_record['snapshot']
    saved, saved_point = parse_fields(snapshot_path, saved_record['physical'], saved_record['snapshot_sha256'])
    assert saved['source']['native_sha256'] == saved_record['storage']['decoded_sha256']
    assert saved['source']['native_bytes'] == saved_record['storage']['decoded_bytes']
    saved['life'] = saved_record['life_id']
    saved['role'] = 'Saved720458 and loaded unchanged before the second owner operation'
    saved['source_record'] = {'path': str(publication_path), 'sha256': s3['source']['sha256'],
                              'pointers': ['/cycles/0/after/storage','/cycles/1/before/storage']}
    reader_sites = [p['point']['site'] for p in s3['stages'][2]['points_with_exact_local_pointers']]
    saved['later_MA_reader_sites_observed_at_saved_cut'] = [saved_point(p) for p in reader_sites]

    s13 = d['scenes']['S13']
    principal = s13['selected_principal']
    full13, _ = parse_fields(Path(principal['source_path']), principal['summary'], principal['source_sha256'])
    assert len(full13['points']) == len(s13['selected_principal_points']) == 275
    for a, b in zip(full13['points'], s13['selected_principal_points']):
        for k, v in a.items():
            assert b[k] == v, (k, a, b)
    full13['life'] = s13['life']
    full13['role'] = 'Selected documented published principal727225; no later evaluation cut'
    cloud = {'schema': 'DEE.official5min.preserved-fields.v1', 'new_native_ticks': 0,
             'snapshots': {'S03_MINUS_saved720458': saved, 'S13_principal727225': full13}}
    cloud_path = HERE/'ESTADOS_GUARDADOS_S03_S13.json.gz'
    cloud_bytes = gzip.compress((json.dumps(cloud, ensure_ascii=False, separators=(',',':'))+'\n').encode(), mtime=0)
    with cloud_path.open('xb') as f:
        f.write(cloud_bytes)
    cloud_locator = {'path':str(cloud_path),'sha256':sha(cloud_bytes),'bytes':len(cloud_bytes)}
    s3['saved_snapshot_fields'] = {**cloud_locator,'pointer':'/snapshots/S03_MINUS_saved720458'}
    s3['coverage']['saved_state_points_kind'] = 'Complete saved snapshot720458 parsed read-only with stdlib; all nonzero RAW incl.state0 and all occupied points preserved.'
    s3['coverage']['saved_snapshot_summary'] = saved['summary']
    s3['coverage']['saved_and_loaded_same_encoded_snapshot_reference'] = (
        publication['cycles'][0]['after']['snapshot'] == publication['cycles'][1]['before']['snapshot'] and
        publication['cycles'][0]['after']['snapshot_sha256'] == publication['cycles'][1]['before']['snapshot_sha256'])
    s13['selected_checkpoint_fields'] = {**cloud_locator,'pointer':'/snapshots/S13_principal727225'}
    points13 = s13['selected_principal_points']
    s13['selected_principal_spatial_scope'] = {
        'N':67,'tick':727225,'every_nonzero_RAW_verified_against_full_snapshot':True,
        'points':len(points13),'occupied':sum(p['state'] != 0 for p in points13),
        'nonzero_RAW_state0':sum(p['state'] == 0 for p in points13),
        'bounds_inclusive':[[min(p['site'][j] for p in points13) for j in range(3)],
                            [max(p['site'][j] for p in points13) for j in range(3)]],
        'scope':'Spatially separated regions of this whole checkpoint; suitable for a global view. No functional region labels inferred from coordinates.'}

    s12 = d['scenes']['S12']
    records = s12['transfer_record_locators']['records']
    s12['primary_life'] = records['04_FUENTE_T.json.gz']['life']
    s12['life_by_source_record'] = {name:{'life':r['life'],'N':r['N'],'source':r['source']}
                                   for name,r in records.items()}
    agg_path = ARCHIVE/'produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos/R05/datos/agregacion_FI01_R05.json'
    agg_bytes = agg_path.read_bytes()
    assert sha(agg_bytes) == '3ce763ebfe8e20bac1397d5c86d3b95cfc7021bf7ebb48d60c54276fd210aead'
    aggregate = json.loads(agg_bytes)['aggregate128']
    s12['another_experiment']['life_by_arm'] = {
        arm:{'life':v['life'], 'initial':v['initial'], 'leaf_tick':v['leaf_tick'],
             'native_datum_tick':v['native_datum_tick'],'fixed_reader_tick':v['fixed_reader_tick'],
             'reader':v['reader'],'source':{'path':str(agg_path),'sha256':sha(agg_bytes),
                                          'pointer':'/aggregate128/pair/'+arm}}
        for arm,v in aggregate['pair'].items()}
    s12['another_experiment']['case_id'] = 'FI01_B05 historical aggregate intervention (128 contributions)'
    d['schema'] = 'DEE.official5min.directed-source-cases.v2'
    d['revision'] = {'previous_sha256':sha(original),'preserved_previous_path':str(revisions/'ESCENAS_03_05_10_13_R01.json'),
                     'changes':['Correct primary JSON-string locators for03; no observed result changed.',
                                'Add complete saved720458 and selected727225 field extractions.',
                                'Make exact12 arm identities explicit; no cross-life assignment.'],
                     'new_native_ticks':0}
    d['input_files_read_and_hashed'].extend([
        {'path':str(snapshot_path),'sha256':saved['source']['encoded_sha256'],'bytes':saved['source']['encoded_bytes'],'read_as':'stdlib gzip+snapshot-v2 field prefix'},
        {'path':principal['source_path'],'sha256':full13['source']['encoded_sha256'],'bytes':full13['source']['encoded_bytes'],'read_as':'stdlib gzip+snapshot-v2 field prefix'},
        {'path':str(agg_path),'sha256':sha(agg_bytes),'bytes':len(agg_bytes),'read_as':'stdlib JSON'}])
    replacement = (json.dumps(d, ensure_ascii=False, indent=2)+'\n').encode('utf8')
    temporary = target.with_suffix('.json.tmp')
    with temporary.open('xb') as f:
        f.write(replacement)
    assert set(json.loads(replacement)['scenes']) == {'S03','S05','S10','S11','S12','S13'}
    temporary.replace(target)
    print(json.dumps({'file':str(target),'bytes':len(replacement),'sha256':sha(replacement),
                      'preserved_R01_sha256':sha(original),'field_extraction':cloud_locator,
                      'S03_saved':saved['summary'],'S13_spatial':s13['selected_principal_spatial_scope'],
                      'new_native_ticks':0},ensure_ascii=False))


if __name__ == '__main__':
    main()
