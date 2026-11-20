"""Extract the already executed interventions, not just their final outcomes."""
from pathlib import Path
import gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def walk(v,path=''):
    if isinstance(v,dict):
        yield path,v
        for k,x in v.items():yield from walk(x,path+'/'+str(k))
    elif isinstance(v,list):
        for i,x in enumerate(v):yield from walk(x,path+'/'+str(i))
def main():
    data_path=ROOT/'evidencia_reutilizada/FUENTES_MECANISMOS_S06_S11_R08.json'
    d=json.loads(data_path.read_text(encoding='utf8'))
    social=d['cases']['IC01_SOCIAL']['arms']['cut'];source=social['source'];p=Path(source['path'])
    assert sha(p)==source['sha256']
    b=p.read_bytes();original=json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
    receipts=[]
    for pointer,v in walk(original):
        if v.get('id')in [2652,2653]and v.get('status')=='applied':
            receipts.append({'source_pointer':pointer,'receipt':v})
    ids={x['receipt']['id']for x in receipts}
    # The primary did not retain separate cut receipts. Do not manufacture
    # an applied status: it did retain the actual SEM4 fields at the ports.
    observed={}
    for arm in ['full','cut']:
        src=d['cases']['IC01_SOCIAL']['arms'][arm]['source'];path=Path(src['path'])
        assert sha(path)==src['sha256'];value=json.loads(path.read_text(encoding='utf8'))
        first=value['result']['passive_frames'][0]
        assert first['tick']==16563 and value['physical']['N']==67
        point=next(x['read']for x in first['ports']if x['bank']==-1)
        observed[arm]={'source':src,'source_pointer':'/result/passive_frames/0/ports/0/read',
                       'N':67,'point':point}
    assert observed['cut']['point']['semantic']==4
    assert observed['full']['point']['semantic']==1
    control=d['cases']['CPC9_COMPOSITION']['data']['conditions'][0]
    assert control['condition']=='cut_arrival_0'and control['new_raw']=='0'and control['clock_preserved']
    out={'schema':'DEE.R12.existing_interventions.v1','new_DEE_ticks':0,
        'CPC9':{'source':{'path':str(data_path),'sha256':sha(data_path),
                        'pointer':'/cases/CPC9_COMPOSITION/data/conditions/0'},
                'intervention':control,'scope':'External diagnostic edit already recorded; not an autonomous DEE action.'},
        'IC01':{'source':source,'source_pre':social['progress']['source'],
                'cuts':social['progress']['cuts'],'applied_receipts':receipts,
                'admission_receipt_status':'Not retained for these cuts in this primary JSON; no applied-count is asserted.',
                'observed_ports':observed,
                'scope':'Recorded prestate, submitted cuts and observed SEM4 postfields. No absent receipt or unobserved transit is reconstructed.'}}
    dest=ROOT/'evidencia_reutilizada/INTERVENCIONES_R12.json'
    if dest.exists():assert json.loads(dest.read_text(encoding='utf8'))==out
    else:dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'file':str(dest),'sha256':sha(dest),'retained_applied_cut_receipts':sorted(ids),'observed_SEM4':True,'new_DEE_ticks':0}))
if __name__=='__main__':main()
