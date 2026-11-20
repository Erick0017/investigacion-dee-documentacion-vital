"""Zero-tick exact fixed-location witnesses from already complete snapshots."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system', type=Path, required=True)
    parser.add_argument('--evidencia', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    if args.salida.exists():
        raise FileExistsError('Preserve previous witness extraction')
    source = args.system / 'capacidades/observador_causal_retrospectivo_01.py'
    spec = importlib.util.spec_from_file_location('APD01_PASSIVE_SNAPSHOT_PARSER', source)
    observer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(observer)
    result = {'schema': 'APD01.affine_fixed_physical_witnesses.v1', 'native_ticks': 0,
              'parser_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'cases': []}
    for identity in ('T', 'U', 'D', 'H', 'CUT', 'SHAM'):
        path = args.evidencia / identity / '04_CINCO_USOS_COMPLETO.deetsnap.gz'
        s = observer.Snapshot(path)
        # Frozen physical hypothesis locations, not a search for a target load.
        sites = {'training_junction': [20, 15, 30], 'cut_interaction': [20, 19, 30],
                 'sham_interaction': [20, 19, 34], 'nominal_fifth_read_memory': [25, 57, 30]}
        result['cases'].append({'id': identity, 'snapshot': str(path.resolve()),
                                'snapshot_sha256': s.encoded_sha256, 'N': s.N, 'tick': s.tick,
                                'RAW_sha256': s.summary()['RAW_sha256'],
                                'clocks_sha256': s.summary()['clocks_sha256'],
                                'pending': s.pending,
                                'sites': {k: s.observation(v) for k, v in sites.items()}})
        del s
    result['scope'] = ('Fixed-location passive extraction from complete five-use cuts. '
                       'Raw observations do not prove a unique material lineage or '
                       'native access to information located by this auditor.')
    args.salida.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'cases': len(result['cases']), 'native_ticks': 0,
                      'cut_witness': next(x for x in result['cases'] if x['id'] == 'CUT')['sites']['cut_interaction']}))
