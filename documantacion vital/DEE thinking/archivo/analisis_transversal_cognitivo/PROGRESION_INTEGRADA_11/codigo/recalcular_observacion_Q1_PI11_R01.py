"""Passive Q1 anomaly metrology from closed witnesses and DEETSNP1/v2 files.

Only Python stdlib. No engine, owner, replay, consultation or operational write.
Default prints JSON. --output creates a NEW evidence file, never overwrites.
Clock deltas, RAW differences and sparse recorded moments are not lineage IDs.
The internal snapshot FNV is not recalculated; gzip CRC and encoded SHA are.
"""
from array import array
from collections import Counter
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import struct
import sys

P = Path(__file__).resolve().parents[1]
DEFAULT_WITNESS = P / 'fuentes/PRIMARIOS_CERRADOS_R01/MAIN01/episodio_0013.json'
DEFAULT_CHECKPOINTS = P / 'estados/MAIN01/sistema/estado/checkpoints'
Q1 = (24, 12, 12)
A = (23, 11, 12)
B = (25, 11, 12)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def need(ok, why):
    if not ok:
        raise ValueError(why)


def regular(p):
    p = Path(p).absolute()
    for node in (p, *p.parents):
        need(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024),
             'No symlink/reparse source paths')
    need(p.is_file(), 'Existing closed source required')
    return p


def fields(value):
    ds = [(value >> s) & 15 for s in (48, 52, 56)]
    return {'raw': str(value), 'state': value & 0xffffffff,
            's_reg': (value >> 32) & 65535,
            'direction': [v - 16 if v & 8 else v for v in ds],
            'semantic': (value >> 60) & 15}


def snapshot(path):
    path = regular(path)
    encoded = path.read_bytes()
    need(len(encoded) <= 32 * 1024 * 1024, 'Bounded source file required')
    data = gzip.decompress(encoded) if encoded[:2] == b'\x1f\x8b' else encoded
    need(len(data) <= 128 * 1024 * 1024, 'Bounded decoded snapshot required')
    need(data[:8] == b'DEETSNP1' and struct.unpack_from('<I', data, 8)[0] == 2,
         'Known frozen snapshotv2 only')
    n = struct.unpack_from('<I', data, 12)[0]
    tick = struct.unpack_from('<Q', data, 16)[0]
    need(n == 67, 'This declared observation is N67 only')
    # Serializer header: magic8/version4/N4/T8/fixed17/text_length4/text/total8.
    length = struct.unpack_from('<I', data, 41)[0]
    need(length <= 1024, 'Bounded phase field')
    phase = data[45:45 + length].decode('utf8')
    offset = 45 + length
    total = struct.unpack_from('<Q', data, offset)[0]
    need(total == n ** 3, 'Physical array length mismatch')
    offset += 8
    need(offset + total * 16 <= len(data) - 8, 'Physical arrays truncated')
    raw_bytes = data[offset:offset + total * 8]
    clock_bytes = data[offset + total * 8:offset + total * 16]
    raw = array('Q'); raw.frombytes(raw_bytes)
    clocks = array('Q'); clocks.frombytes(clock_bytes)
    if sys.byteorder != 'little':
        raw.byteswap(); clocks.byteswap()
    meta = {'path': str(path.resolve()), 'bytes': len(encoded), 'sha256': sha(encoded),
            'decoded_bytes': len(data), 'N': n, 'T': tick, 'phase': phase,
            'RAW_sha256': sha(raw_bytes), 'clocks_sha256': sha(clock_bytes),
            'gzip_CRC_checked': encoded[:2] == b'\x1f\x8b', 'internal_FNV_recalculated': False}
    return meta, raw, clocks


def index(site, n):
    return (site[0] * n + site[1]) * n + site[2]


def coord(i, n):
    return [i // (n * n), (i // n) % n, i % n]


def distance(site, center, n):
    return max(min((site[j] - center[j]) % n, (center[j] - site[j]) % n) for j in range(3))


def compare(witness_path, checkpoint_root):
    witness_path = regular(witness_path)
    witness_bytes = witness_path.read_bytes()
    j = json.loads(witness_bytes)
    need(j['ordinal'] == 13 and j['before_tick'] == 967727 and j['after_tick'] == 969291,
         'This observation is the declared closed MAIN01 ordinal13 only')
    need(j['actual_failed'] is False and j['returned_failed'] is False, 'Actual recorded nonfailure required')
    snapshots = {}
    for tick in (j['before_tick'], j['after_tick']):
        paths = sorted(Path(checkpoint_root).glob(f"{j['life_id']}.T{tick}.*.deetsnap.gz"))
        need(paths, 'Required complete checkpoint not found')
        variants = [snapshot(p) for p in paths]
        need(all(v[0]['T'] == tick for v in variants), 'Snapshot filename/header mismatch')
        physical = {(m['N'], m['T'], m['phase'], m['RAW_sha256'], m['clocks_sha256']) for m, _, _ in variants}
        need(len(physical) == 1, 'Same-tick variants disagree physically; do not choose a convenient source')
        snapshots[tick] = variants
    pre, raw0, clock0 = snapshots[j['before_tick']][0]
    post, raw1, clock1 = snapshots[j['after_tick']][0]
    n = pre['N']
    raw_changes = []
    for i, (a, b) in enumerate(zip(raw0, raw1)):
        if a != b:
            site = coord(i, n)
            raw_changes.append({'site': site, 'before': fields(a), 'after': fields(b),
                                'before_clock': clock0[i], 'after_clock': clock1[i],
                                'toroidal_Chebyshev_distance_from_Q1': distance(site, Q1, n)})
    banks = []
    for name, site, expected0, expected1 in (('A', A, j['Q1_references_before']['A'], j['references_after']['q1']['A']),
                                             ('B', B, j['Q1_references_before']['B'], j['references_after']['q1']['B'])):
        i = index(site, n)
        need(str(raw0[i]) == expected0['raw'] and str(raw1[i]) == expected1['raw']
             and str(clock0[i]) == expected0['clock'] and str(clock1[i]) == expected1['clock'],
             'Snapshot bank fields differ from immutable witness')
        banks.append({'bank': name, 'site': list(site), 'before': fields(raw0[i]), 'after': fields(raw1[i]),
                      's_reg_delta': fields(raw1[i])['s_reg'] - fields(raw0[i])['s_reg'],
                      'before_clock': clock0[i], 'after_clock': clock1[i]})
    frames = []
    for frame in j['trace_observations']:
        view = frame['frame']
        refs = frame.get('references')
        frames.append({'phase': frame['phase'], 'tick': int(frame.get('tick', view['tick'])),
                       'stencil_sites': len(view['observations']),
                       'nonzero_RAW': [o for o in view['observations'] if int(o['raw']) != 0],
                       'Q1_banks': refs,
                       'lineage_identifiers': False})
    zero = [f['tick'] for f in frames if f['Q1_banks'] is not None and f['Q1_banks']['A_minus_B'] == 0]
    one = [f['tick'] for f in frames if f['Q1_banks'] is not None and f['Q1_banks']['A_minus_B'] == 1]
    need(zero and one, 'Need temporal reference observations on both sides of the change')
    window = {'latest_recorded_equal_banks_tick': max(zero), 'first_recorded_unequal_banks_tick': min(one),
              'interval': f"({max(zero)}, {min(one)}]", 'unobserved_intermediate_tick': 969290,
              'exact_change_tick_identified': False}
    outcome = [r for r in j['requests'] if r.get('channel') == 'PI10.Q1.TC.R01.outcome.nonfailure']
    need(len(outcome) == 1 and outcome[0]['receipt']['status'] == 'applied', 'Single applied Q1 nonfailure birth required')
    for variants in snapshots.values():
        for m, _, _ in variants:
            need(sha(Path(m['path']).read_bytes()) == m['sha256'], 'Frozen snapshot changed during inspection')
    need(sha(witness_path.read_bytes()) == sha(witness_bytes), 'Frozen witness changed during inspection')
    return {
        'schema': 'DEE.PI11.open_passive_Q1_observation.R01', 'exploratory_not_new_capacity': True,
        'new_native_ticks': 0, 'DEE_imports': 0, 'owner_calls': 0,
        'source_witness': {'path': str(witness_path.resolve()), 'bytes': len(witness_bytes), 'sha256': sha(witness_bytes),
                           'json_locators': ['/trace_observations', '/Q1_references_before', '/references_after/q1',
                                             '/requests', '/actual_failed', '/returned_failed']},
        'recalculation_script': {'path': str(Path(__file__).resolve()), 'sha256': sha(Path(__file__).read_bytes())},
        'snapshot_variants': {str(t): [v[0] for v in variants] for t, variants in snapshots.items()},
        'all_same_tick_variants_have_same_RAW_clocks': True,
        'encoded_snapshots_are_not_claimed_identical': True,
        'source_hashes_stable_during_inspection': True,
        'geometry': {'N': n, 'Q1_origin': list(Q1), 'bank_A': list(A), 'bank_B': list(B),
                     'array_index': '(x*N+y)*N+z',
                     'coordinate_source': 'sistema/capacidades/observador_causal_retrospectivo_01.py:44–45',
                     'bank_source': 'sistema/capacidades/pi10_dos_trazas_legales_R01.py:bank_observations'},
        'facts': {'actual_failed': j['actual_failed'], 'returned_failed': j['returned_failed'],
                  'first_motor': j['first_stage']['motor'], 'second_motor': j['second_stage']['motor'],
                  'Q1_nonfailure_request': outcome[0], 'bank_delta_before': j['Q1_references_before']['A_minus_B'],
                  'bank_delta_after': j['references_after']['q1']['A_minus_B'],
                  'bank_payloads': banks, 'bank_change_window': window},
        'recorded_frames': frames,
        'global_comparison': {'sites': n ** 3, 'RAW_changed_sites': len(raw_changes),
                              'clocks_changed_sites': sum(a != b for a, b in zip(clock0, clock1)),
                              'clock_delta_histogram': {str(k): v for k, v in sorted(Counter(b-a for a,b in zip(clock0,clock1)).items())},
                              'nonzero_RAW_before': sum(bool(v) for v in raw0), 'nonzero_RAW_after': sum(bool(v) for v in raw1),
                              'state_zero_nonzero_RAW_before': sum(v != 0 and v & 0xffffffff == 0 for v in raw0),
                              'state_zero_nonzero_RAW_after': sum(v != 0 and v & 0xffffffff == 0 for v in raw1)},
        'local_radius4_RAW_changes': [c for c in raw_changes if c['toroidal_Chebyshev_distance_from_Q1'] <= 4],
        'all_global_RAW_changes': raw_changes,
        'interpretation': [
            'La asimetría Q1 aparece después del último registro igual enT969289 y antes o enT969291; no se identifica el tick exacto ni un encuentro único.',
            'A aumenta110→114 yB110→113. El incremento común de ambos y la asimetría adicional no deben confundirse; no se interpretan como más conceptos o energía.',
            'El stencil registra un estado móvil de dirección[-1,0,0] y después una dirección mixta[-1,-1,0] enelhub. Igual RAW en sitios distintos no demuestra identidad de portador ni ascendencia única.',
            'Nonfailure=false no equivale a ausencia de entrada: el canal material outcome.nonfailure recibió payload0 y el recibo está applied. Carga cero no garantiza neutralidad.',
            'El control sin retorno punitivo conserva nacimientos nonfailure y el paisaje heredado. No debe describirse como un mundo vacío o sin experiencia material.',
            'Los snapshots extremos no registran los encuentros intermedios. La asociación temporal entre retorno, movimiento y cambio de banco no selecciona por sí sola una causa entre retorno actual, recurrencia, contexto acumulado o interacción de factores.'
        ],
        'not_demonstrated': ['Nuevo aprendizaje útil atribuido exclusivamente a un fallo', 'Nueva capacidad autónoma',
                             'Linaje individual de portadores', 'No-feedback físicamente vacío',
                             'Causa microscópica única del incremento', 'Pérdida global de información'],
        'existing_next_discriminator': 'Comparar los brazos None y heredado ya programados por Root, conservando fase, entradas y contexto; esta herramienta no ejecuta esa comparación ni exige un experimento nuevo.',
        'coverage': 'Seis checkpoints extremos y seis frames de un testigo cerrado; no serialización completa de cada tick, no rastreador de todos los encuentros.',
        'checks': ['Gzip CRC de cada fuente', 'SHA256 antes/después', 'Arrays iguales entre variantes al mismo tick',
                   'Campos de bancos coinciden con el testigo', 'Coordenadas por indexado documentado',
                   'No se importó DEE ni se avanzó mundo']}


def main(args):
    result = compare(args.witness, args.checkpoints)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        need(args.output.parent.resolve() == (P/'fuentes').resolve(), 'Evidence output limited to this campaign fuentes')
        with args.output.open('x', encoding='utf8', newline='\n') as f:
            f.write(text)
        print(json.dumps({'path': str(args.output.resolve()), 'bytes': len(text.encode('utf8')),
                          'sha256': sha(text.encode('utf8')), 'new_native_ticks': 0,
                          'RAW_changes': result['global_comparison']['RAW_changed_sites'],
                          'bank_change_window': result['facts']['bank_change_window']}, ensure_ascii=False))
    else:
        print(text, end='')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--witness', type=Path, default=DEFAULT_WITNESS)
    ap.add_argument('--checkpoints', type=Path, default=DEFAULT_CHECKPOINTS)
    ap.add_argument('--output', type=Path)
    main(ap.parse_args())
