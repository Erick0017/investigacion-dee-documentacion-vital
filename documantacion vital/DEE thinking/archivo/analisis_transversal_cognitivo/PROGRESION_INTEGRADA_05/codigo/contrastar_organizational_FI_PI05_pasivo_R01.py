"""Decode exact organizational operation records in closed FI snapshots only."""
from pathlib import Path
import argparse,hashlib,json,runpy
def info(p):
    b=Path(p).read_bytes();return {'file':Path(p).name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--comparacion',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent);a=ap.parse_args()
    if a.out.exists():raise FileExistsError('No overwrite')
    j=json.loads(a.comparacion.read_text(encoding='utf-8'));p=a.root
    sm=runpy.run_path(str(p/'codigo/contrastar_prefijos_C2C_PI05_pasivo.py'),run_name='pure_snapshot_reader')
    om=runpy.run_path(str(p/'codigo/analizar_organizational_prefijos_PI05_pasivo.py'),run_name='pure_organizational_reader')
    views={};ops={}
    for k,v in j['views'].items():
        s=v['snapshot'];before=info(s['path']);x=sm['parse'](Path(s['path']),s['sha256']);after=info(s['path'])
        if before!=after:raise ValueError('Immutable snapshot changed')
        views[k],ops[k]=om['parse'](x[6])
    x=views['a'];y=views['b'];different=[{'index':i,'a':u,'b':v}for i,(u,v)in enumerate(zip(ops['a'],ops['b']))if u!=v]
    result={'schema':'DEE.PI05.organizational_FI.literal_comparison.R01','mode':'PASSIVE_SNAPSHOT_DECODING_NO_NATIVE','Native_ticks':0,'comparison_source':info(a.comparacion),'parser_sources':[info(p/'codigo/contrastar_prefijos_C2C_PI05_pasivo.py'),info(p/'codigo/analizar_organizational_prefijos_PI05_pasivo.py')],'views':views,'section_equality':{k:x['sections'][k]['sha256']==y['sections'][k]['sha256']for k in x['sections']},'external_operation_count_a':len(ops['a']),'external_operation_count_b':len(ops['b']),'external_operation_differences':different,'scope':'Organizational operation records are an explicit retained record layer, distinct from RAW/clocks and Runtime receipt history. This analysis does not supply those records to the participant or demonstrate that they are used as functional cognitive memory.'}
    with a.out.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(a.out),'bytes':a.out.stat().st_size,'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'sections':result['section_equality'],'operation_differences':different},ensure_ascii=False)[:4500])
if __name__=='__main__':main()
