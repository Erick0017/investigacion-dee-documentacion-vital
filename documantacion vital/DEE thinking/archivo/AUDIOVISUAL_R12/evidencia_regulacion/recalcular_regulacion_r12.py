"""Pure archival checks using only this evidence folder; never runs DEE."""
from pathlib import Path
import array, gzip, hashlib, json, sys

ROOT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
data = json.loads((ROOT/'CPC5_REGULACION_DATOS_EXACTOS.json').read_text(encoding='utf8'))
checked = 0
for item in data['files']:
    assert sha(ROOT/item['export_relative']) == item['source']['sha256']
    checked += 1
rows = []
for name, arm in data['cases'].items():
    source = json.loads((ROOT/'primarios'/name/'RESULT.json').read_text(encoding='utf8'))
    total = 0
    for bank, pair in source['captures'].items():
        rr, ff = pair['resource'], pair['function']
        rv = rr['state']>0 and rr['semantic']!=5 and rr['s_reg']==3 and rr['direction']==([1,0,1] if bank=='N' else [1,0,0])
        fv = ff['state']>0 and ff['semantic']!=5 and ff['s_reg']==7 and ff['direction']==[0,1,0]
        total += int(rv)+2*int(fv)
        assert rv == arm['qualified_readers'][bank]['qualified_resource']
        assert fv == arm['qualified_readers'][bank]['qualified_function']
    assert total == arm['functional_observer']['external_utility']
    for window in arm['contact_contexts']:
        tick = window['tick']; arrays = []
        for kind in ('raw','clock'):
            a = array.array('Q'); a.frombytes(gzip.decompress((ROOT/'primarios'/name/f'T{tick}.{kind}.u64.gz').read_bytes()))
            if sys.byteorder!='little': a.byteswap()
            arrays.append(a)
        for p in window['points']:
            i = p['site'][0]*67*67+p['site'][1]*67+p['site'][2]
            assert str(arrays[0][i]) == p['raw'] and str(arrays[1][i]) == p['clock']
    rows.append({'case':name,'external_functional_observer':total,'admitted_inputs':sum(c['final_receipt']['status']=='applied' for c in source['calls']),'requested_inputs':len(source['calls'])})
print(json.dumps({'evidence_files_hash_checked':checked,'cases':rows,'new_DEE_ticks':0,'original_folders_required':False},ensure_ascii=False))
