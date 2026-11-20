"""Exact sparse RAW contrasts from the already checksum-verified cuts; no Native."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'


def main():
    data = json.loads((EVIDENCE / 'CONTRASTE_CORTES_T658K_N0.json').read_text(encoding='utf8'))
    cuts = {row['label']: row for row in data['cuts']}
    a, b = [cuts[name] for name in ('APD04_ATENCION_REAL_AUX', 'APD04_ATENCION_OMIT_AUX')]
    if a['N'] != b['N'] or a['tick'] != b['tick']:
        raise ValueError('An equal-tick RAW comparison was requested')
    aa = {row['index']: row for row in a['all_nonzero_RAW_sites']}
    bb = {row['index']: row for row in b['all_nonzero_RAW_sites']}
    changes = [{'index': i, 'site': (aa.get(i) or bb[i])['site'],
        'A_raw': aa.get(i, {}).get('raw', '0'), 'B_raw': bb.get(i, {}).get('raw', '0'),
        'A_fields': aa.get(i), 'B_fields': bb.get(i)}
        for i in sorted(aa.keys() | bb.keys())
        if aa.get(i, {}).get('raw', '0') != bb.get(i, {}).get('raw', '0')]
    inactive = [{(row['index'], row['raw']) for row in cut['all_nonzero_RAW_sites'] if row['state'] == 0}
                for cut in data['cuts']]
    result = {'schema': 'APD04.equal_committed_tick_RAW_A_B.N0.v1',
        'tick': a['tick'], 'same_clock_fields': a['clocks_sha256'] == b['clocks_sha256'],
        'RAW_differing_sites': len(changes), 'changes': changes,
        'all_187_inactive_nonzero_RAW_identical_across_four_cuts': all(rows == inactive[0] for rows in inactive),
        'Native_ticks': 0,
        'scope': 'History-dependent physical differences remain at the last committed common tick. '
                 'This does not establish their accessibility, classify them all as memory, '
                 'or explain the uncommitted slow future.'}
    with (EVIDENCE / 'DIFERENCIAS_CORTES_AB_T658068_N0.json').open('x', encoding='utf8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'changes'}, indent=2))


if __name__ == '__main__':
    main()
