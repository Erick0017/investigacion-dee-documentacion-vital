"""Compare already-written first-two Native primaries, no SQLite/world use."""
from pathlib import Path
import hashlib,importlib.util,json
P=Path(__file__).resolve().parents[2];out=P/'control/E3_PRIMEROS_DOS_R01_R02_FISICA_COMPARADA.json'
if out.exists():raise FileExistsError('Prior proof preserved')
spec=importlib.util.spec_from_file_location('E3_RECALC_PURE',Path(__file__).with_name('RECALCULAR_E3.py'));pure=importlib.util.module_from_spec(spec);spec.loader.exec_module(pure)
results=[]
for i in range(2):
    pair=[]
    for revision in('R01','R02'):
        file=P/f'ensayos/PI04_E3_REAL_{revision}_OP_{i}.json';raw=file.read_bytes();outer=json.loads(raw);value,row=pure.outer_value(outer)
        recalculated=pure.check_row(row,i,{'connection':1,'delay_laps':4},775355+782*i)
        pair.append({'revision':revision,'primary':str(file),'sha256':hashlib.sha256(raw).hexdigest(),'snapshot_physical':value['committed_snapshot']['physical'],'calendar':row['calendar'],'requests':row['requests'],'reader':row['reader'],'recalculated':{k:v for k,v in recalculated.items()if k!='requests'}})
    a,b=pair
    require=all(a['snapshot_physical'][k]==b['snapshot_physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256'))and a['calendar']==b['calendar']and a['requests']==b['requests']and a['reader']==b['reader']
    if not require:raise ValueError('Physical/input first prefix difference; preserve both')
    results.append({'ordinal':i,'same_N_tick_RAW_clocks':True,'same_native_requests_and_fixed_reader':True,'data':pair})
proof={'schema':'DEE.PI04.E3.R01_R02.prefix_physical_comparison.v1','new_native_ticks':0,'SQLite_opened':False,'scope':'Closed primaries only; the two technical repeats share the same prefix and do not add independent organisms or learning evidence. No statement about equality after the supply adaptation.', 'results':results}
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'same_first_two_physical':True,'new_native_ticks':0,'proof':str(out)}))
