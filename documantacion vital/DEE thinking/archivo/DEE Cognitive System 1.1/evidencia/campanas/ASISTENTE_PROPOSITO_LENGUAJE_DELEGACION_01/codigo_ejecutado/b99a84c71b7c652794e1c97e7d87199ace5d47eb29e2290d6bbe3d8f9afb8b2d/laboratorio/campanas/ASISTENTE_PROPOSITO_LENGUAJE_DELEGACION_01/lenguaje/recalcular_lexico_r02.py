"""Standalone RAW recalculation, common20gates, admission and history controls."""
import argparse,gzip,hashlib,json
from pathlib import Path
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def decode(raw):
    v=int(raw)
    def sg(k):
        x=(v>>k)&15;return x-16 if x&8 else x
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,'direction':[sg(k)for k in(48,52,56)]}
def run(folder):
    protocol=read(folder/'PROTOCOLO_CONGELADO.json');errors=[];cases=[];nobs=0;gates=None
    for case in protocol['cases']:
        path=folder/(case+'_01_PRIMARY.json.gz');p=read(path);r=p['result']
        z={'case':case,'primary':path.name,'primary_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
           'life_id':p['INSTRUMENTO']['life_id'],'tick':p['physical']['tick'],'snapshot_sha256':p['INSTRUMENTO']['snapshot_sha256'],'groups':{}}
        for group in('first_queries','old_panel','post_old_queries'):
            rows=[]
            for i,q in enumerate(r[group]):
                sites=[o['site']for o in q['reader']['panel']]
                if gates is None:gates=sites
                if sites!=gates or len(sites)!=20 or len({tuple(p)for p in sites})!=20:errors.append([case,group,i,'COMMON20GATES_CHANGED'])
                found=[]
                for o in q['reader']['panel']:
                    d=decode(o['raw']);nobs+=1
                    if any(d[k]!=o[k]for k in d):errors.append([case,group,i,'RAW_FIELD_MISMATCH',o['site']])
                    if d['state']>0 and d['semantic']==1 and d['direction']in([0,0,-1],[0,0,1]):found.append({'site':o['site'],'sign':d['direction'][2],'s_reg':d['s_reg']})
                out=found[0]['sign']if len(found)==1 else None
                if found!=q['reader']['candidates']or out!=q['reader']['formed_native_command']:errors.append([case,group,i,'READER_MISMATCH'])
                for frame in q['frames']:
                    for o in frame['sites']:
                        d=decode(o['raw']);nobs+=1
                        if any(d[k]!=o[k]for k in d):errors.append([case,group,i,'TRACE_RAW_FIELD_MISMATCH',o['site']])
                req=q['requests'];applied=sum(x['receipt']['status']=='applied'for x in req)
                rows.append({'form':q['form'],'native_output':out,'ambiguous':len(found)>1,
                             'input_tick':q['input_tick'],'read_tick':q['read_tick'],
                             'requested':len(req),'applied':applied,'rejected_or_other':len(req)-applied})
                if any(x['value']not in(5,7)for x in req):errors.append([case,group,i,'NON_GENERIC_QUERY_CONTENT'])
            z['groups'][group]=rows
        fresh=[*z['groups']['first_queries'],*z['groups']['post_old_queries']]
        if case in('paired','reversed'):
            target={'agrega':1,'resta':-1}
            if case=='reversed':target={k:-v for k,v in target.items()}
            z['acquired_sign_matches']={'numerator':sum(q['native_output']==target[q['form']]for q in fresh),'denominator':len(fresh)}
        else:z['new_output']={'valid':sum(q['native_output']in(-1,1)for q in fresh),'none':sum(q['native_output']is None for q in fresh),'denominator':len(fresh)}
        z['old8_matches']={'numerator':sum(q['native_output']==v for q,v in zip(z['groups']['old_panel'],protocol['old_last_observed_signs'])),'denominator':len(z['groups']['old_panel'])}
        z['admission']={}
        for group in('teaching','first_queries','old_panel','post_old_queries'):
            req=[x for q in r[group]for x in q['requests']];applied=sum(x['receipt']['status']=='applied'for x in req)
            z['admission'][group]={'requested':len(req),'applied':applied,'rejected_or_other':len(req)-applied}
        cases.append(z)
    return {'schema':'APD01.lexical_recalculation.R02','cases':cases,'common_gate_sites':gates,
            'RAW_observations_decoded':nobs,'discrepancies':errors,'native_ticks_executed':0,
            'scope':'Archived RAW and receipt recalculation, not new physical replication. Four histories share an inherited prefix; new forms are not new operations or syntax.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();r=run(a.primarios);b=(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with a.salida.open('xb')as f:f.write(b)
    print(json.dumps({'cases':[{k:z[k]for k in('case','life_id','old8_matches')}for z in r['cases']],
                      'RAW_observations_decoded':r['RAW_observations_decoded'],'discrepancies':r['discrepancies'],'sha256':hashlib.sha256(b).hexdigest()}))
    raise SystemExit(bool(r['discrepancies']))
