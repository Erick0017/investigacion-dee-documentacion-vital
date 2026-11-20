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
    ids={x['receipt']['id']for x in receipts};assert ids=={2652,2653},ids
    control=d['cases']['CPC9_COMPOSITION']['data']['conditions'][0]
    assert control['condition']=='cut_arrival_0'and control['new_raw']=='0'and control['clock_preserved']
    out={'schema':'DEE.R12.existing_interventions.v1','new_DEE_ticks':0,
        'CPC9':{'source':{'path':str(data_path),'sha256':sha(data_path),
                        'pointer':'/cases/CPC9_COMPOSITION/data/conditions/0'},
                'intervention':control,'scope':'External diagnostic edit already recorded; not an autonomous DEE action.'},
        'IC01':{'source':source,'source_pre':social['progress']['source'],
                'cuts':social['progress']['cuts'],'applied_receipts':receipts,
                'scope':'Recorded prestate and admitted SEM4 entries. No unobserved post-interception cell is reconstructed.'}}
    dest=ROOT/'evidencia_reutilizada/INTERVENCIONES_R12.json'
    if dest.exists():assert json.loads(dest.read_text(encoding='utf8'))==out
    else:dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'file':str(dest),'sha256':sha(dest),'applied_cut_ids':sorted(ids),'new_DEE_ticks':0}))
if __name__=='__main__':main()
