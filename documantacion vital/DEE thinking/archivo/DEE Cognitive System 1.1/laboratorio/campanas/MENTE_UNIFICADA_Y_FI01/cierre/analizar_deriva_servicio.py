"""Lectura retrospectiva de referencias y fallos RAW128; cero ticks y cero targets."""
import argparse,gzip,hashlib,json
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def walk(v,path='$'):
    if isinstance(v,dict):
        yield path,v
        for k,q in v.items():yield from walk(q,path+'.'+str(k))
    elif isinstance(v,list):
        for i,q in enumerate(v):yield from walk(q,path+'['+str(i)+']')
def sr(v):
    n=int(v['raw']);assert 0<=n<2**64
    return(n>>32)&65535
def run(root):
    source=root/'REGISTROS_TRANSPORTE.json.gz';records=json.loads(gzip.decompress(source.read_bytes()));samples={};raw=[]
    for entry in records:
        if not entry['id'].startswith('fi60_'):continue
        if not entry.get('result'):continue
        result=json.loads(entry['result']);payload=json.loads(entry['payload']);mode=(payload.get('situaciones')or[{}])[0].get('modo')
        for path,node in walk(result):
            pair=None
            for key in('references','references_pre','references_after'):
                if isinstance(node.get(key),list):
                    sites={tuple(x.get('site',[])):x for x in node[key]if isinstance(x,dict)}
                    if(14,14,15)in sites and(16,14,15)in sites:pair=(sites[(14,14,15)],sites[(16,14,15)],path+'.'+key)
            fields=node.get('fields',{})
            if isinstance(fields,dict)and all(k in fields for k in('A','B')):pair=(fields['A'],fields['B'],path+'.fields')
            if pair:
                left,right,at=pair
                if tuple(left.get('site',[]))!=(14,14,15)or tuple(right.get('site',[]))!=(16,14,15):continue
                tick=left.get('tick',node.get('tick'));assert tick==right.get('tick',tick)
                key=(tick,int(left['raw']),int(right['raw']))
                value={'tick':tick,'A_raw':left['raw'],'B_raw':right['raw'],'A':sr(left),'B':sr(right),'D_A_minus_B':sr(left)-sr(right),'request':entry['id'],'mode':mode,'source_path':at}
                if key not in samples:samples[key]=value
        if mode=='crudos'and result.get('result',{}).get('rows'):
            r=result['result']['rows'][0];frames=[]
            for f in r.get('frames',[]):
                fields=f['fields'];frames.append({'tick':f['tick'],'fields':{k:{z:v[z]for z in('site','raw','clock','state','s_reg','semantic','direction')if z in v}for k,v in fields.items()}})
            raw.append({'request':entry['id'],'before_tick':r['before']['tick'],'input_tick':r['input_tick'],'datum_tick':r['datum_tick'],'query_tick':r['query_tick'],'read_tick':r['read_tick'],'components':r['raw_components'],'references_pre':r['references_pre'],'references_after':r['references_after'],'reader':r['reader'],'frames':frames,'admissions':{'requested':len(r['requests']),'status':{status:sum(str(x['receipt']['status'])==status for x in r['requests'])for status in{str(x['receipt']['status'])for x in r['requests']}}}})
    ordered=sorted(samples.values(),key=lambda v:(v['tick'],v['A'],v['B']));changes=[];old=None
    for value in ordered:
        if old is None or value['D_A_minus_B']!=old['D_A_minus_B']:
            changes.append({'previous_observation':old,'new_observation':value,'scope':'Interval bounded by archived observations; no unique causal genealogy inferred'})
        old=value
    return{'schema':'MUFI01.archived_reference_drift.v1','native_ticks':0,'source':source.name,'source_sha256':sha(source.read_bytes()),'distinct_reference_samples':len(ordered),'reference_samples':ordered,'difference_transitions':changes,'raw128_uses':raw,'scope':'Passive recomputation from exact archived RAW. Zero fixed-gate candidates is distinct from multiple candidates or technical rejection. A difference transition and a later absence do not establish a unique cause, global information destruction or a toroidal lineage.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();result=run(a.evidencia)
    a.salida.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps({'samples':result['distinct_reference_samples'],'transitions':len(result['difference_transitions']),'raw128':len(result['raw128_uses']),'native_ticks':0}))
if __name__=='__main__':main()
