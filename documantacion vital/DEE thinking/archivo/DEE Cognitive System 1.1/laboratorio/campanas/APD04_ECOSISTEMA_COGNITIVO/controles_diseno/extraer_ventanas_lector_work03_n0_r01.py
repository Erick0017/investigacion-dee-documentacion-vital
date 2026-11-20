"""N0 exact existing local observations, not trajectories or new Native probes."""
from collections import Counter
import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
PREFIX = 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/PREFIJO_R04_COMPLETADO_WORK03_N0_R01/PREFIJO_COMPLETADO_ORIGINAL.jsonl.gz'
EXPECTED = '82fecf4203964d79d8e6bac2df9308cae2afc1d91c7c6ac497c58ea25a2a75b0'


def run(out):
    if out.exists(): raise FileExistsError('Do not replace existing N0 evidence')
    hp = Path(__file__).with_name('extraer_densificacion_r04_contextos_n0_r02.py')
    spec = importlib.util.spec_from_file_location('local_exact_observation_helpers', hp)
    h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
    encoded = (ROOT / PREFIX).read_bytes()
    if h.sha(encoded) != EXPECTED: raise ValueError('Closed prefix differs')
    line = gzip.decompress(encoded).splitlines(keepends=True)[617]; row = json.loads(line); seen = {}
    for locator, node in h.walk(row):
        if {'raw', 'tick', 'site'} <= set(node):
            raw = int(node['raw']); clock = str(node.get('clock'))
            key = (int(node['tick']), tuple(node['site']), str(raw), clock)
            group = seen.setdefault(key, {'observation_original_values': node, 'all_original_locators': []})
            group['all_original_locators'].append(locator)
    records = sorted(seen.values(), key=lambda r: (r['observation_original_values']['tick'], r['observation_original_values']['site']))
    per_tick = {}
    for item in records:
        o = item['observation_original_values']; state = int(o['raw']) & 0xffffffff
        counts = per_tick.setdefault(str(o['tick']), Counter()); counts[str(state)] += 1
    conflicts = {}
    for key in seen: conflicts.setdefault((key[0], key[1]), set()).add((key[2], key[3]))
    conflicting = [{'tick': k[0], 'site': list(k[1]), 'variants': sorted(values)} for k, values in conflicts.items() if len(values) > 1]
    observed2or3 = [r for r in records if int(r['observation_original_values']['raw']) & 0xffffffff in (2, 3)]
    result = {'schema': 'APD04.work03.existing_local_windows.N0.R01', 'Native_ticks': 0,
              'source_closed_prefix': PREFIX, 'source_sha256': EXPECTED, 'zero_based_line': 617, 'line_sha256': h.sha(line),
              'request_id': row['event']['request_id'], 'unique_tick_site_RAW_clock_observations': len(records),
              'records': records, 'state_counts_by_sampled_tick': {k: dict(v) for k, v in per_tick.items()},
              'conflicting_tick_site_observations': conflicting,
              'state2_or3_observations': len(observed2or3),
              'first_sampled_tick_state2or3': min((r['observation_original_values']['tick'] for r in observed2or3), default=None),
              'limits': ['Sampled sites/windows only, no complete intervening global world or known first birth.',
                         'Potential trace locations are geometric candidate observations, not proven continuous lineage.',
                         'A last sample lacking state2/3 in other sites does not establish global absence.',
                         'Different request stages can repeat the same observation; deduplication preserves every original locator.',
                         'No inference of attention, memory, death or functional usefulness from the state class alone.']}
    out.mkdir(); (out / 'CODIGO').mkdir()
    for p in (Path(__file__), hp): shutil.copy2(p, out / 'CODIGO' / p.name)
    h.save(out / 'OBSERVACIONES_EXISTENTES_WORK03.json', result)
    buf = io.StringIO(newline=''); writer = csv.writer(buf, lineterminator='\n')
    writer.writerow(['tick', 'x', 'y', 'z', 'RAW_text_exact', 'clock_text_exact', 'state', 's_reg', 'dx', 'dy', 'dz', 'semantic', 'first_original_locator'])
    for item in records:
        o = item['observation_original_values']; raw = int(o['raw'])
        direction = [((raw >> k) & 15) - (16 if ((raw >> k) & 15) >= 8 else 0) for k in (48, 52, 56)]
        writer.writerow([o['tick'], *o['site'], str(raw), str(o.get('clock')), raw & 0xffffffff,
                         (raw >> 32) & 65535, *direction, (raw >> 60) & 15, item['all_original_locators'][0]])
    with (out / 'OBSERVACIONES_ENTERAS_EXACTAS.csv').open('x', encoding='utf8', newline='') as stream: stream.write(buf.getvalue())
    check = list(csv.DictReader(io.StringIO(buf.getvalue())))
    if len(check) != len(records) or any(int(r['RAW_text_exact']) != int(o['observation_original_values']['raw']) for r, o in zip(check, records)):
        raise ValueError('CSV exact integer roundtrip differs')
    h.save(out / 'MANIFIESTO.json', {'members': [{'file': p.relative_to(out).as_posix(), 'sha256': h.file_sha(p), 'bytes': p.stat().st_size}
                                             for p in sorted(out.rglob('*')) if p.is_file()], 'self_hash_excluded': True})
    print(json.dumps({'out': str(out), 'observations': len(records), 'state2or3': len(observed2or3),
                      'first_sampled_state2or3_tick': result['first_sampled_tick_state2or3'], 'conflicts': len(conflicting), 'Native_ticks': 0}))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(); run(args.out)
