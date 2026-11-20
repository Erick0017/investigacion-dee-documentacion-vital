"""0tick exact RAW/common24gate audit for the third lexical curriculum."""
import argparse,gzip,hashlib,json
from pathlib import Path
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def decode(raw):
    v=int(raw)
    def sg(k):
        x=(v>>k)&15;return x-16 if x&8 else x
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,'direction':[sg(k)for k in(48,52,56)]}
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def run(folder):
    protocol=read(folder/'PROTOCOLO_CONGELADO.json');errors=[];cases=[];nobs=0;gates=None
    oldsigns=dict(zip(protocol['old_first'],[-1,-1,1,-1,-1,1,1,-1,1,-1]))
    for case in protocol['cases']:
        path=folder/(case+'_01_PRIMARY.json.gz');p=read(path);r=p['result'];unique={}
        for node in walk(r):
            if 'raw'in node and all(k in node for k in('state','s_reg','semantic','direction')):
                d=decode(node['raw']);nobs+=1
                if any(d[k]!=node[k]for k in d):errors.append([case,'RAW_FIELD_MISMATCH',node.get('site')])
            if isinstance(node.get('receipt'),dict):
                receipt=node['receipt'];rid=node.get('id',receipt.get('id'))
                if rid is not None:
                    key=str(rid)
                    if key in unique and unique[key]!=receipt:errors.append([case,'RECEIPT_CHANGED',key])
                    unique[key]=receipt
        z={'case':case,'life_id':p['INSTRUMENTO']['life_id'],'tick':p['physical']['tick'],
           'snapshot_sha256':p['INSTRUMENTO']['snapshot_sha256'],'primary_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'groups':{}}
        for group in('old_first','first_new','later_panel'):
            rows=[]
            if [q['form']for q in r[group]]!=protocol[group]:errors.append([case,group,'QUERY_ORDER_CHANGED'])
            for i,q in enumerate(r[group]):
                sites=[o['site']for o in q['reader']['panel']]
                if gates is None:gates=sites
                if sites!=gates or len(sites)!=24 or len({tuple(s)for s in sites})!=24:errors.append([case,group,i,'COMMON24GATES_CHANGED'])
                found=[]
                for o in q['reader']['panel']:
                    d=decode(o['raw'])
                    if d['state']>0 and d['semantic']==1 and d['direction']in([0,0,-1],[0,0,1]):
                        found.append({'site':o['site'],'sign':d['direction'][2],'s_reg':d['s_reg']})
                out=found[0]['sign']if len(found)==1 else None
                if found!=q['reader']['candidates']or out!=q['reader']['formed_native_command']:errors.append([case,group,i,'READER_MISMATCH'])
                if any(v['value']not in(5,7)for v in q['requests']):errors.append([case,group,i,'NON_GENERIC_QUERY_CONTENT'])
                req=q['requests'];applied=sum(v['receipt']['status']=='applied'for v in req)
                rows.append({'form':q['form'],'native_output':out,'ambiguous':len(found)>1,'input_tick':q['input_tick'],
                    'read_tick':q['read_tick'],'requested':len(req),'applied':applied,'rejected_or_other':len(req)-applied})
            z['groups'][group]=rows
        if z['groups']['old_first']and z['groups']['first_new']and max(q['read_tick']for q in z['groups']['old_first'])>=min(q['input_tick']for q in z['groups']['first_new']):
            errors.append([case,'OLD_PANEL_DID_NOT_PRECEDE_FIRST_NEW_QUERY'])
        fresh=z['groups']['first_new']+[q for q in z['groups']['later_panel']if q['form']in('total','quita')]
        if case in('paired','reversed'):
            targets=protocol[case]
            z['new_association_matches']={'numerator':sum(q['native_output']==targets[q['form']]for q in fresh),'denominator':len(fresh)}
        else:z['new_outputs']={'valid':sum(q['native_output']in(-1,1)for q in fresh),'none':sum(q['native_output']is None for q in fresh),'denominator':len(fresh)}
        for group in('old_first','later_panel'):
            rows=[q for q in z['groups'][group]if q['form']in oldsigns]
            z[group+'_old10']={'numerator':sum(q['native_output']==oldsigns[q['form']]for q in rows),'denominator':len(rows)}
        counts={}
        for receipt in unique.values():counts[receipt['status']]=counts.get(receipt['status'],0)+1
        z['requests_unique']={'requested':len(unique),'status_counts':counts}
        z['group_admission']={}
        for group in('teaching','old_first','first_new','later_panel'):
            req=[v for q in r[group]for v in q['requests']];applied=sum(v['receipt']['status']=='applied'for v in req)
            z['group_admission'][group]={'requested':len(req),'applied':applied,'rejected_or_other':len(req)-applied}
        cases.append(z)
    return {'schema':'APD01.lexical_recalculation.R04','cases':cases,'common_gate_sites':gates,
        'RAW_observations_decoded':nobs,'discrepancies':errors,'native_ticks_executed':0,
        'scope':'Three forks of one prefix; two new arbitrary signal associations to already available sign/operation classes. No new arithmetic algorithms, NSM meanings, autonomous growth, grammar or independent biographies.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();r=run(a.primarios);b=(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with a.salida.open('xb')as f:f.write(b)
    print(json.dumps({'cases':[{k:z[k]for k in('case','life_id','old_first_old10','later_panel_old10','requests_unique')}for z in r['cases']],
        'RAW_observations_decoded':r['RAW_observations_decoded'],'discrepancies':r['discrepancies'],'sha256':hashlib.sha256(b).hexdigest()}))
    raise SystemExit(bool(r['discrepancies']))
