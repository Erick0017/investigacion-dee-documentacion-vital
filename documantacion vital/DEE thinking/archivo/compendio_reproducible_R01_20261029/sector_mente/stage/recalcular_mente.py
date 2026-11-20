"""Read selected original primary bytes; no engine import or new native ticks."""
from pathlib import Path
import argparse,gzip,hashlib,json
HERE=Path(__file__).resolve().parent
def read(p):
    p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def core(d):
    if isinstance(d.get('data'),dict):return d['data'].get('result',d['data'])
    v=d.get('result',d)
    while isinstance(v,dict)and isinstance(v.get('result'),dict):v=v['result']
    return v
def inspect(d):
    r=core(d);rows=r.get('rows',[])if isinstance(r,dict)else[]
    receipt={};observations=[]
    def walk(x):
        if isinstance(x,dict):
            if 'raw'in x and'clock'in x and'direction'in x:observations.append({k:x[k]for k in('raw','clock','direction','state','semantic','s_reg','site')if k in x});return
            if isinstance(x.get('receipt'),dict)and'id'in x:receipt[str(x['id'])]=x['receipt'].get('status')
            for k,v in x.items():
                if k not in('before','after','sources','initial','final','pre_snapshot','history_snapshot','post_joint_snapshot'):walk(v)
        elif isinstance(x,list):
            for a in x:walk(a)
    walk(r)
    return {'top_level_rows':len(rows),'decoded_signs':[x.get('decoded_sign',x.get('native_class'))for x in rows if'decoded_sign'in x or'native_class'in x],
       'materially_useful':sum(x.get('useful_material_action')is True for x in rows),'unique_native_request_ids':len(receipt),'receipt_status_counts':{str(k):list(receipt.values()).count(k)for k in sorted(set(receipt.values()),key=str)},
       'exact_native_observations':len(observations),'witness_sha256':hashlib.sha256(json.dumps(observations,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--id',required=True);a.add_argument('--out',type=Path,required=True);n=a.parse_args()
    c=read(HERE/'sector_config.json');m=next(x for x in c['mechanisms']if x['id']==n.id);out=n.out.resolve()
    assert not out.exists()or(out.is_dir()and all(p.is_file()and p.name in('EJECUCION_STDOUT.log','EJECUCION_STDERR.log')for p in out.iterdir())),'Existing results are protected'
    out.mkdir(parents=True,exist_ok=True)
    rows=[{'reference':rel,**inspect(read(HERE/rel))}for rel in m['references']]
    result={'id':m['id'],'native_ticks':0,'method':'Exact archived primary extraction and arithmetic; not native reproduction','cases':rows,'scope':'Receipt IDs deduplicated only within each primary, not summed as independent subjects. Empty/incorrect responses remain in primaries.'}
    (out/'RECALCULO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'id':n.id,'primaries':len(rows),'native_ticks':0}))
if __name__=='__main__':main()
