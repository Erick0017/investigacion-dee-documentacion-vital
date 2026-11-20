"""Portable stdlib-only capacity audit. Never imports DEE or advances ticks.

Primary counterexamples are recomputed, not treated as integrity failures.
The actual output is read from RAW motor samples; target sums are audit-only.
"""
from pathlib import Path
import argparse,gzip,hashlib,json

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def signed(n):return n-16 if n>=8 else n
def decoded(raw):
    n=int(raw)
    return{'state':n&0xffffffff,'s_reg':(n>>32)&65535,
      'semantic':(n>>60)&15,'direction':[signed((n>>p)&15)for p in(48,52,56)]}
def walk(q):
    yield q
    if isinstance(q,dict):
        for v in q.values():yield from walk(v)
    elif isinstance(q,list):
        for v in q:yield from walk(v)
def episodes(q,path='$',values=None,owner=None):
    if isinstance(q,dict):
        if isinstance(q.get('values'),list):values=q['values']
        if all(k in q for k in('before','after','row','reader','frames')):
            yield path,q,values,owner
        for k,v in q.items():yield from episodes(v,path+'.'+k,values,q)
    elif isinstance(q,list):
        for i,v in enumerate(q):yield from episodes(v,path+'['+str(i)+']',values,owner)
def command(ep):
    critical=ep['row']['critical_tick'];samples=[]
    for t in(critical-16,critical-15):
        f=next(f for f in ep['frames']if f['tick']==t);roles=[]
        for r in(-1,0,1):
            q=decoded(f['contacts'][str(r)]['raw'])
            if q['state']>0 and q['semantic']==1 and q['direction']in([r,-1,-1],[r,-1,0]):roles.append(r)
        samples.append({'tick':t,'roles':roles,'command':(1 if roles[0]>=0 else-1)if len(roles)==1 else None,'conflict':len(roles)>1})
    if samples[-1]['conflict']:return None,samples
    valid=next((s for s in reversed(samples)if s['command']is not None),None)
    return None if valid is None else valid['command'],samples
def sensor_targets(ep):
    critical=ep['row']['critical_tick'];f=next((f for f in ep['frames']if f['tick']==critical-17),None)
    if f is None:return None
    if 'fanin_targets'in f:return f['fanin_targets']
    for k in('fanin','r10'):
        if isinstance(f.get(k),dict)and'targets'in f[k]:return f[k]['targets']
    return None
def difference(before,after,key):
    return{'before':[v['s_reg']for v in before[key]],'after':[v['s_reg']for v in after[key]]}
def main():
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--codigo',type=Path);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    paths=sorted([*a.primarios.glob('*.json.gz'),*a.primarios.glob('*.json')]);rows=[];files=[];issues=[];observation_count=0;cases={};r10cases={}
    code_hashes={}if a.codigo is None else{sha(f):str(f.relative_to(a.codigo))for f in a.codigo.rglob('*.py')}
    for path in paths:
        if path.name.startswith('RECALCULO_'):continue
        try:q=json.loads(gzip.decompress(path.read_bytes())if path.suffix=='.gz'else path.read_bytes())
        except Exception as e:issues.append({'file':path.name,'error':'unreadable:'+repr(e)});continue
        files.append({'file':path.name,'sha256':sha(path),'bytes':path.stat().st_size})
        for obj in walk(q):
            if isinstance(obj,dict)and all(k in obj for k in('raw','clock','state','s_reg','semantic','direction')):
                observation_count+=1;d=decoded(obj['raw'])
                if any(d[k]!=obj[k]for k in d):issues.append({'file':path.name,'error':'RAW fields differ','record':obj})
                if not isinstance(obj['clock'],(int,str))or not 0<=int(obj['clock'])<2**64:issues.append({'file':path.name,'error':'clock_not_exact_uint64'})
        sources=q.get('sources',{})if isinstance(q,dict)else{}
        if a.codigo is not None:
            for original,digest in sources.items():
                if digest not in code_hashes:issues.append({'file':path.name,'error':'executed_source_not_preserved','original':original,'sha256':digest})
        for pointer,ep,values,owner in episodes(q):
            got,samples=command(ep)
            if got!=ep.get('formed_native_command'):issues.append({'file':path.name,'path':pointer,'error':'cached_native_command_differs','got':got,'cached':ep.get('formed_native_command')})
            targets=sensor_targets(ep);want_sums=None;actual_sums=None;sum_exact=None;target=None
            if values is not None and len(values)in(2,4,8):
                want_sums=[sum(values[::2]),sum(values[1::2])]
                if targets is not None:actual_sums=[decoded(x['raw'])['s_reg']for x in targets];sum_exact=actual_sums==want_sums
                # R9 capacity pilots calibrated12, real4 reserve14, new R10world4.
                calibration=4 if 'R10_'in path.name else 14 if 'RESERVA_R07'in path.name else 12
                target=1 if want_sums[0]+calibration>=want_sums[1]else-1
            requests=list(ep['requests']);owner=owner or{}
            requests+=owner.get('extra_receipts',owner.get('input_receipts',[]))+owner.get('secondary_requests',[])
            byid={r['id']:r for r in requests};statuses={}
            for r in byid.values():
                s=r['receipt']['status'];statuses[s]=statuses.get(s,0)+1
            rows.append({'file':path.name,'episode':pointer,'values':values,'critical_tick':ep['row']['critical_tick'],'end_tick':ep['row']['end_tick'],
               'command':got,'samples':samples,'valid':got is not None,'auditor_target':target,'audit_matches':None if target is None else got==target,
               'target_sums':want_sums,'physical_sensor_sums':actual_sums,'sum_exact':sum_exact,
               'job_completed_as_actually_executed':ep['job_completed'],'actuator':ep['row']['actuator'],'feedback':ep['row']['feedback'],
               'resource_only_not_a_data_answer':owner.get('resource_only_not_a_data_answer',False),
               'own':difference(ep['before'],ep['after'],'own'),'context':difference(ep['before'],ep['after'],'context_A'),
               'private_B':difference(ep['before'],ep['after'],'private_B'),'requested':len(byid),'statuses':statuses})
        if path.name.startswith('PILOTO_R03_')and len([r for r in rows if r['file']==path.name])==1:cases[path.name.removeprefix('PILOTO_R03_').removesuffix('.json.gz')]=rows[-1]
        if path.name.startswith('R10_V2_basis_')and len([r for r in rows if r['file']==path.name])==1:r10cases[path.name.removeprefix('R10_V2_basis_').removesuffix('.json.gz')]=rows[-1]
    contrasts=[]
    for index,left,right in[(0,'M0','ML0'),(1,'M0','MR0'),(2,'M0','ML1'),(3,'P0','PR1'),(4,'M0','ML2'),(5,'P0','PR2'),(6,'M0','ML3'),(7,'P0','PR3')]:
        if left not in cases or right not in cases:continue
        l=cases[left];r=cases[right];changed=[i for i,(x,y)in enumerate(zip(l['values'],r['values']))if x!=y]
        okay=changed==[index]and l['command']is not None and r['command']is not None and l['command']!=r['command']and l['sum_exact']and r['sum_exact']
        contrasts.append({'component_zero_based':index,'left':l['file'],'right':r['file'],'only_changed':changed,'commands':[l['command'],r['command']],'relevant_in_this_controlled_family':okay})
    r10contrasts=[]
    for index,left,right in[(0,'M0','ML0'),(2,'M0','ML1'),(4,'M0','ML2'),(6,'M0','ML3'),(1,'P0','PR0'),(3,'P0','PR1'),(5,'P0','PR2'),(7,'P0','PR3')]:
        if left not in r10cases or right not in r10cases:continue
        l=r10cases[left];r=r10cases[right];changed=[i for i,(x,y)in enumerate(zip(l['values'],r['values']))if x!=y]
        okay=changed==[index]and l['command']is not None and r['command']is not None and l['command']!=r['command']and l['sum_exact']and r['sum_exact']
        r10contrasts.append({'component_zero_based':index,'left':l['file'],'right':r['file'],'only_changed':changed,'commands':[l['command'],r['command']],'relevant_in_this_controlled_family':okay})
    observation_equivalence=None
    lookup={r['file']:r for r in rows}
    if 'PILOTO_R03_M0.json.gz'in lookup and 'PANEL_R04_OBSERVACION_SIN_AMPLIAR.json.gz'in lookup:
        aq=json.loads(gzip.decompress((a.primarios/'PILOTO_R03_M0.json.gz').read_bytes()))['result']
        bq=json.loads(gzip.decompress((a.primarios/'PANEL_R04_OBSERVACION_SIN_AMPLIAR.json.gz').read_bytes()))['result']
        a0=aq['physical'];b0=bq['physical']
        observation_equivalence={k:a0[k]==b0[k]for k in('N','tick','RAW_sha256','clocks_sha256')}
        ar=aq['result'];br=bq['result']['rows'][0]
        observation_equivalence['native_requested_receipts_equal']=ar['native']['requests']==br['native']['requests']
        observation_equivalence['extra_requested_receipts_equal']=ar['extra_receipts']==br['extra_receipts']
    out={'schema':'EO02.capacity.recalculation.v1','new_native_ticks':0,'files':files,'observation_checks':observation_count,'episodes':rows,
      'relevant_component_contrasts':contrasts,'R10_relevant_component_contrasts':r10contrasts,'passive_observation_physical_equivalence':observation_equivalence,
      'totals':{'primaries':len(files),'episodes':len(rows),'formed_valid':sum(r['valid']for r in rows),'physical_sum_correct':sum(r['sum_exact']is True for r in rows),
         'physical_sum_incorrect':sum(r['sum_exact']is False for r in rows),'components_relevant_R03_first_use':sum(r['relevant_in_this_controlled_family']for r in contrasts),
         'components_relevant_R10':sum(r['relevant_in_this_controlled_family']for r in r10contrasts)},
      'issues':issues,'limits':['First-use arity and repeated use differ; failed sums are scientific negatives, not parser errors.','16/32 serial observations do not imply joint16/32 cognitive integration.','Samples share fork prefixes, not independent organisms.','Archive sums and targets are audit-only and never replace RAW motor decoding.']}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({'output':str(a.salida),'sha256':sha(a.salida),'totals':out['totals'],'issues':len(issues)},ensure_ascii=False));return bool(issues)
if __name__=='__main__':raise SystemExit(main())
