"""Portable standard-library recalculation of APD01 archived controls. Zero ticks."""
import argparse,gzip,hashlib,json,sys
from array import array
from pathlib import Path

def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def digest(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf8')
def fields(v):
    if type(v)is not int and not(isinstance(v,str)and v.isdecimal()):raise ValueError('Exact integer RAW required')
    n=int(v)
    if not 0<=n<2**64:raise ValueError('Not uint64')
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,
            'direction':[((n>>s)&15)-(16 if((n>>s)&15)>=8 else 0)for s in(48,52,56)]}
def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def pbytes(v):
    q=array('Q',v)
    if sys.byteorder!='little':q.byteswap()
    return q.tobytes()
def memory_read(r):
    gates={(33+4*x,33+4*y,33+z):[0,0,z]for x,y in((1,0),(0,1),(1,1),(-1,1),(1,-1),(-1,-1))for z in(-1,1)}
    if len(r['panel'])!=12 or{tuple(o['site'])for o in r['panel']}!=set(gates):raise ValueError('Changed12-gate memory reader')
    candidates=[]
    for o in r['panel']:
        f=fields(o['raw'])
        if f['state']and f['semantic']==1 and f['direction']==gates[tuple(o['site'])]:candidates.append(f['direction'][2])
    return candidates[0]if len(candidates)==1 else None
def six_read(r):
    origin=r.get('origin',[15,15,15]);gates={tuple((origin[j]+[2*x,2,2*z][j])%67 for j in range(3)):[x,1,z]for x in(-1,0,1)for z in(0,-1)}
    if len(r['observations'])!=6 or{tuple(o['site'])for o in r['observations']}!=set(gates):raise ValueError('Changed6-gate reader')
    candidates=[]
    for o in r['observations']:
        f=fields(o['raw']);d=gates[tuple(o['site'])]
        if f['state']and f['semantic']==1 and f['direction']==d:candidates.append(d[0])
    return candidates[0]if len(candidates)==1 else None

class Audit:
    def __init__(self,root):self.root=root;self.issues=[];self.sources=[];self.raw=set();self.reader_checks=0
    def source(self,p):
        self.sources.append({'file':p.relative_to(self.root).as_posix(),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size})
        return read(p)
    def inspect(self,v,label):
        requests={};readers=0
        for o in walk(v):
            if all(k in o for k in('raw','state','s_reg','semantic','direction','clock','site')):
                sig=digest(canonical(o))
                if sig not in self.raw:
                    self.raw.add(sig)
                    if any(o[k]!=x for k,x in fields(o['raw']).items()):self.issues.append(label+':RAW:'+sig)
                    if not 0<=int(o['clock'])<2**64:self.issues.append(label+':clock')
            if 'formed_native_command'in o and 'panel'in o:
                if memory_read(o)!=o['formed_native_command']:self.issues.append(label+':memory_reader')
                readers+=1
            if 'choice'in o and 'observations'in o:
                if six_read(o)!=o['choice']:self.issues.append(label+':six_reader')
                readers+=1
            if 'id'in o and isinstance(o.get('receipt'),dict):
                rr=o['receipt'];i=int(o['id'])
                if int(rr['id'])!=i:self.issues.append(label+':receipt_id')
                if i in requests and requests[i]!=rr:self.issues.append(label+':inconsistent_receipt_views:'+str(i))
                requests[i]=rr
        self.reader_checks+=readers;statuses={}
        for r in requests.values():statuses[r['status']]=statuses.get(r['status'],0)+1
        return {'requested_unique_events':len(requests),'receipt_statuses_at_capture':statuses,'fixed_readers_checked':readers}

def recalc(root):
    a=Audit(root);cost=[];o2=[];reversal=[]
    folder=root/'RETORNO_COMUN_391_R1';summary=a.source(folder/'RESULTADOS.json')
    for declared in summary['outcomes']:
        key=declared['id'];v=a.source(folder/key/'02_RESULTADO_COMPLETO.json.gz')['result'];counts=a.inspect(v,'391:'+key)
        f=v['feedback'];timing=f['timing'];k=timing['boundary_multiplier']
        if timing['boundary']!=391*k or timing['query_tick']!=391*k-4 or timing['datum_tick']!=391*k-1:a.issues.append(key+':timing')
        if k%2!=(0 if key.startswith('even_')else 1):a.issues.append(key+':parity')
        before=[fields(o['raw'])['s_reg']for o in f['references_before']];after=[fields(o['raw'])['s_reg']for o in f['references_after']]
        old=[memory_read(q['result']['reader'])for q in v['old_six']]
        actual=six_read(v['common_use']['reader'])
        if before!=declared['reference_pre']or after!=declared['reference_post']or actual!=declared['common21_choice']or old!=declared['old_six']:a.issues.append(key+':summary')
        cost.append({'id':key,'before':before,'after':after,'difference_after':after[0]-after[1],
                     'feedback_choice':six_read(f['reader']),'cost_input':f['cost_observation'],'mode':f['mode'],
                     'common21_first_use':actual,'old_six':old,**counts})
    for front,labels,out in(('RUTA_O2_R3',('real','omit','sham'),o2),('REVERSION_O2_R3',('SAME_LAW','REVERSE'),reversal)):
        directory=root/front;frozen=a.source(directory/'ANTES_DEL_PRIMER_TICK.json')
        for s in frozen['sources']:
            p=directory/s['file'];a.source(p)if p.suffix=='.json'else a.sources.append({'file':p.relative_to(root).as_posix(),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size})
            if digest(p.read_bytes())!=s['sha256']:a.issues.append(front+':source_bytes:'+s['file'])
        for label in labels:
            v=a.source(directory/label/'03_RESULTADO_COMPLETO.json.gz')['result'];counts=a.inspect(v,front+':'+label);tasks=[]
            for row in v['rows']:
                choice=six_read(row['route']['reader']);native=row['native_calculation'];ext=row['external_calculator'];numeric=None
                if native is not None:
                    t=native['native_trial'];at=t['datum_tick']-2;fr=[x for x in t['frames']if x['tick']==at]
                    if len(fr)!=1:raise ValueError('Missing fixed native aggregate observation')
                    gate=fr[0]['fields']['C'];ff=fields(gate['raw']);valid=gate['site']==[12,17,18]and gate['tick']==at and ff['state']>0 and ff['semantic']==1 and ff['direction']==[1,-1,-1]
                    numeric=(ff['s_reg']-(32 if native['operation']=='diferencia'else 0))if valid else None
                    if choice!=-1 or ext is not None or numeric!=native['numeric_reader']['numeric_result']:a.issues.append(front+':route_numeric')
                    # OFFLINE evaluator only; neither the native actor nor its decoder reads this sum.
                    expected=(row['operands'][0]+row['operands'][1])if native['operation']=='suma'else(row['operands'][0]-row['operands'][1])
                    if numeric!=expected:a.issues.append(front+':native_math_incorrect')
                elif ext is not None:
                    numeric=ext['value']
                    if choice not in(0,1)or numeric!=row['operands'][0]+row['operands'][1]:a.issues.append(front+':external_math')
                if choice!=row['native_route']or numeric!=row['numeric_result']:a.issues.append(front+':actor_report')
                artifact=row['artifact'];artifact_ok=False
                if artifact is not None:
                    p=directory/label/artifact['file'];b=p.read_bytes();a.sources.append({'file':p.relative_to(root).as_posix(),'sha256':digest(b),'bytes':len(b)})
                    artifact_ok=(digest(b)==artifact['sha256']and len(b)==artifact['bytes']and b==str(numeric).encode('ascii'))
                    if not artifact_ok:a.issues.append(front+':artifact')
                if front=='RUTA_O2_R3':price=(1 if choice==-1 else 5)if artifact is not None else 5
                else:price=row['declared_prices'][0 if choice==-1 else 1]
                actualcost=price+(4 if front=='REVERSION_O2_R3'and artifact is None else 0)
                returned=row['environmental_return'];ref=[fields(o['raw'])['s_reg']for o in row['references_after']]
                k=returned['boundary_multiplier']
                if k%2 or returned['query_tick']!=391*k-4 or returned['datum_tick']!=391*k-1 or returned['cost']!=actualcost or row['modelled_price']!=price:a.issues.append(front+':cost_calendar')
                cost_ports=[r for r in returned['requests']if r.get('port','').startswith('APD.route.cost')]
                expect_port=actualcost>2 and returned['mode']!='omit'
                if len(cost_ports)!=(1 if expect_port else 0):a.issues.append(front+':fixed_excess_codec')
                for r in cost_ports:
                    endpoint='APD.route.cost'if returned['mode']=='real'else'APD.route.cost_sham'
                    if r['port']!=endpoint or r['payload']!=actualcost:a.issues.append(front+':common_cost_endpoint')
                tasks.append({'opportunity':row['opportunity'],'native_route':choice,'numeric':numeric,'route':'native'if native is not None else'external'if ext is not None else'absent',
                              'artifact_verified':artifact_ok,'modelled_cost':actualcost,'reference_after':ref,'difference_after':ref[0]-ref[1]})
            old=[memory_read(q['result']['reader'])for q in v['old_six']];cmp=[six_read(q['reader'])for q in v['old_comparison13_32']]
            out.append({'arm':label,'tasks':tasks,'old_six':old,'old_comparison13_32':cmp,'final':v['final'],**counts})
    projection_path=root/'RUTA_O2_R3/COMPARACION_PASIVA/PRE_TERCERA_ACCION_RAW_CLOCK_COMPLETO.json.gz'
    projection=a.source(projection_path);states=[]
    for c in projection['cases']:
        n=c['N'];raw=array('Q',[0])*(n**3);clocks=array('Q',[int(c['clock_default'])])*(n**3);seen=set()
        for i,v,clock in c['rows']:
            if i in seen or not 0<=i<len(raw):raise ValueError('Invalid sparse RAW index')
            seen.add(i);raw[i]=int(v)
        for i,clock in c['clock_exceptions']:clocks[i]=int(clock)
        for i,v,clock in c['rows']:
            if clocks[i]!=int(clock):a.issues.append('projection:clock_row')
        if digest(pbytes(raw))!=c['RAW_sha256']or digest(pbytes(clocks))!=c['clocks_sha256']:a.issues.append('projection:whole_field_hash')
        states.append((c,raw,clocks))
    comparisons=[]
    for ia,ib in((0,1),(0,2),(1,2)):
        ca,ra,cla=states[ia];cb,rb,clb=states[ib];n=ca['N'];indices=[i for i,(x,y)in enumerate(zip(ra,rb))if x!=y]
        differences=[{'site':[i//(n*n),(i//n)%n,i%n],'a':fields(ra[i]),'b':fields(rb[i]),'clock_a':str(cla[i]),'clock_b':str(clb[i])}for i in indices]
        comparisons.append({'arms':[ca['arm'],cb['arm']],'ticks':[ca['tick'],cb['tick']],
                            'RAW_differences':len(indices),'clock_differences':sum(x!=y for x,y in zip(cla,clb)),
                            'differences':differences,'channels_equal':ca['channels']==cb['channels'],
                            'pending_equal':ca['pending']==cb['pending'],'pending_counts':[len(ca['pending']),len(cb['pending'])],
                            'receipts_equal':ca['receipts']==cb['receipts'],'execution_equal':ca['execution']==cb['execution'],
                            'different_metadata_keys':[k for k in sorted(set(ca['metadata_value_sha256'])|set(cb['metadata_value_sha256']))if ca['metadata_value_sha256'].get(k)!=cb['metadata_value_sha256'].get(k)]})
    final=a.source(root/'RUTA_O2_R3/COMPARACION_PASIVA/DELTA_RECIBOS_FINALES_COMPLETOS.json.gz');late=[];finalcounts={}
    for c in final['cases']:
        captured={};statuses={}
        if c['pending']:a.issues.append('delta:final_pending')
        for r in c['final_receipts_of_requested_events']:
            v=r['final_receipt'];statuses[str(v['status'])]=statuses.get(str(v['status']),0)+1
            if r['id']!=v['id']:a.issues.append('delta:final_receipt_id')
            if r['captured_status']=='scheduled':late.append({'history':c['id'],**r})
        for k,v in statuses.items():finalcounts[k]=finalcounts.get(k,0)+v
    if finalcounts!={'2':325}or len(late)!=2:a.issues.append('delta:final_denominators')
    return {'schema':'APD01.common_cost_O2_and_complete_fields.archived_recalculation.v1','native_ticks':0,
            'common391':cost,'O2_actual_tasks':o2,'O2_reversal_from_actual_negative_state':reversal,
            'complete_prethird_field_comparisons':comparisons,'delta_final_receipt_statuses':finalcounts,
            'delta_later_applied_not_rewritten_early_records':late,
            'RAW_observations_checked':len(a.raw),'fixed_readers_checked':a.reader_checks,
            'sources':a.sources,'issues':a.issues,
            'scope':'Archived arithmetic, exact records, receipts and functional transduction checked. No native replay. Modelled prices are external task costs, not CPU/energy. Common return has a fixed prepared asymmetric bias; reversal is a legitimate negative. Full fields are not complete file identity; differing records/agendas/metadata are retained, no unique lineage inferred.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    if a.salida.exists():raise FileExistsError('Preserve earlier calculation')
    result=recalc(a.evidencia)
    a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'issues':result['issues'],'common391_cases':len(result['common391']),
                      'O2_tasks':sum(len(x['tasks'])for x in result['O2_actual_tasks']),
                      'reversal_tasks':sum(len(x['tasks'])for x in result['O2_reversal_from_actual_negative_state']),
                      'RAW_checked':result['RAW_observations_checked'],'readers':result['fixed_readers_checked'],
                      'comparisons':[{k:v for k,v in x.items()if k in('arms','RAW_differences','clock_differences','channels_equal','pending_equal')}for x in result['complete_prethird_field_comparisons']]}))
    raise SystemExit(bool(result['issues']))
