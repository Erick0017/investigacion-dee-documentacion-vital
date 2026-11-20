"""Compare already saved complete cuts globally, never infer uncommitted ticks."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CONTRASTE_CORTES_T658K_N0.json'


def main():
    path = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    spec = importlib.util.spec_from_file_location('frozen_passive_snapshot_parser', path)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    selected = []
    prefix = ROOT / 'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
    manifest = json.loads((prefix / 'EXPORTACION_SERVICIO.json').read_text(encoding='utf8'))
    # Locate only the exact member identified by the already verified manifest hash.
    expected = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
    candidates = [p for p in prefix.rglob('*.deetsnap.gz') if hashlib.sha256(p.read_bytes()).hexdigest() == expected]
    if len(candidates) != 1:
        raise ValueError('The declared sealed snapshot is not unique')
    selected.append(('sealed_common_prefix', candidates[0], expected))
    for life in ('APD04_ATENCION_REAL_AUX', 'APD04_MAIN', 'APD04_ATENCION_OMIT_AUX'):
        record_path = ROOT / 'sistema/estado/vidas' / life / 'VIDA.json'
        if record_path.is_file():
            record = json.loads(record_path.read_text(encoding='utf8'))
            if record['physical']['tick'] >= 650000:
                selected.append((life, ROOT / 'sistema' / record['snapshot'], record['snapshot_sha256']))
    results = []
    for label, snapshot_path, digest in selected:
        snapshot = observer.Snapshot(snapshot_path)
        if snapshot.encoded_sha256 != digest:
            raise ValueError('Selected complete cut changed')
        raw_nonzero = []
        semantics, directions, boxes = Counter(), Counter(), Counter()
        active = 0
        for index, raw in enumerate(snapshot.raw):
            if not raw:
                continue
            site = observer.coord(index, snapshot.N)
            value = observer.fields(raw)
            raw_nonzero.append({'index': index, 'site': site, 'clock': str(snapshot.clocks[index]), **value})
            semantics[(bool(value['state']), value['semantic'])] += 1
            directions[tuple(value['direction'])] += 1
            boxes[tuple(x // 16 for x in site)] += 1
            active += bool(value['state'])
        exceptional_clocks = [{'index': i, 'site': observer.coord(i, snapshot.N), 'clock': str(clock),
                               'raw': str(snapshot.raw[i])}
                              for i, clock in enumerate(snapshot.clocks) if clock != snapshot.tick]
        windows = {}
        for key, packet in snapshot.metadata.items():
            if 'pending_window' in packet and 'R04' in packet:
                try:
                    value = json.loads(packet)
                    windows[key] = {k: value[k] for k in ('version', 'pending_window', 'uses', 'consequences') if k in value}
                except (ValueError, TypeError):
                    continue
        results.append({'label': label, 'snapshot': snapshot_path.relative_to(ROOT).as_posix(),
            'snapshot_sha256': digest, 'checksum_valid': snapshot.checksum_valid,
            'tick': snapshot.tick, 'N': snapshot.N,
            'RAW_sha256': observer.sha(observer.pbytes(snapshot.raw)),
            'clocks_sha256': observer.sha(observer.pbytes(snapshot.clocks)),
            'occupied': active, 'raw_nonzero': len(raw_nonzero),
            'state_zero_RAW_nonzero': len(raw_nonzero) - active,
            'max_s_reg': max((v >> 32) & 65535 for v in snapshot.raw),
            'clock_range_exact': [str(min(snapshot.clocks)), str(max(snapshot.clocks))],
            'clock_exceptions_count': len(exceptional_clocks),
            'clock_exceptions': exceptional_clocks,
            'semantic_counts': [{'state_active': k[0], 'semantic': k[1], 'count': n} for k, n in sorted(semantics.items())],
            'directions': [{'direction': list(k), 'count': n} for k, n in sorted(directions.items())],
            'spatial_16_site_boxes': [{'box': list(k), 'count': n} for k, n in sorted(boxes.items())],
            'all_nonzero_RAW_sites': raw_nonzero,
            'selected_local_context': [snapshot.observation(site) for site in (
                [24, 12, 53], [26, 12, 53], [24, 13, 54], [24, 13, 52],
                [26, 13, 54], [26, 13, 52], [23, 15, 53], [25, 15, 53], [27, 15, 53])],
            'pending_native_inputs': snapshot.pending, 'route_windows': windows,
            'interfaces_count': len(snapshot.channels),
            'scope': 'Exact committed cut only. Marker does not identify the actual current/uncommitted native tick.'})
    output = {'schema': 'APD04.committed_cuts_global_comparison.N0.v1', 'cuts': results,
        'new_native_ticks': 0, 'Runtime_created': False,
        'limitations': ['No post-timeout full snapshot is available; no native-crash or exact-stall-tick claim follows.',
            'Different lives, histories and ticks cannot establish one common physical failure mechanism.',
            'Low occupied count does not exclude a local bottleneck, blocked reader or expensive host operation.']}
    with OUT.open('x', encoding='utf8') as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps([{k: row[k] for k in ('label', 'tick', 'occupied', 'raw_nonzero',
        'state_zero_RAW_nonzero', 'max_s_reg', 'clock_range_exact', 'clock_exceptions_count')}
        for row in results], indent=2))


if __name__ == '__main__':
    main()
