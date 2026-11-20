"""Portable primary-record recalculation; stdlib only, no DEE or new ticks."""
from pathlib import Path
import argparse,base64,csv,gzip,hashlib,json,zlib

def read(p):
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fields(raw):
    n=int(raw)
    if not 0<=n<2**64:raise ValueError('Non uint64 RAW')
    def signed(v):return v-16 if v>=8 else v
    return dict(state=n&0xffffffff,s_reg=(n>>32)&65535,semantic=(n>>60)&15,
        direction=[signed((n>>x)&15)for x in(48,52,56)])
def verify_views(v,errors,case):
    n=0
    if isinstance(v,dict):
        if all(k in v for k in('raw','clock','state','s_reg','semantic','direction')):
            n+=1
            if any(v[k]!=x for k,x in fields(v['raw']).items()):errors.append([case,'RAW_view'])
            if type(v['clock'])not in(int,str)or not 0<=int(v['clock'])<2**64:errors.append([case,'clock'])
        for k,x in v.items():
            if k not in('stdout','stderr'):n+=verify_views(x,errors,case)
    elif isinstance(v,list):
        for x in v:n+=verify_views(x,errors,case)
    return n
def decode(r):
    critical=r['row']['critical_tick'];samples=[]
    for tick in(critical-16,critical-15):
        f=next(x for x in r['frames']if x['tick']==tick);roles=[]
        for role in(-1,0,1):
            q=fields(f['contacts'][str(role)]['raw'])
            if q['state']>0 and q['semantic']==1 and q['direction']in([role,-1,-1],[role,-1,0]):roles.append(role)
        samples.append({'tick':tick,'roles':roles,'command':(1 if roles[0]>=0 else-1)if len(roles)==1 else None})
    chosen=None if len(samples[-1]['roles'])>1 else next((x for x in reversed(samples)if x['command']is not None),None)
    return (None,None,None)if chosen is None else(chosen['command'],chosen['roles'][0],chosen['tick'])
def counts(requests):
    statuses={}
    for q in requests:
        s=q['receipt']['status'];statuses[s]=statuses.get(s,0)+1
    return dict(requested=len(requests),applied=statuses.get('applied',0),
        rejected=sum(n for s,n in statuses.items()if s.startswith('rejected')),
        pending=sum(n for s,n in statuses.items()if s in('pending','queued','accepted')),statuses=statuses)
def worker_check(event,command,raw,errors,label):
    receipt=event.get('worker_receipt')
    if command is None:
        if receipt:errors.append([label,'worker_without_action'])
        return None
    if not receipt:errors.append([label,'missing_worker']);return None
    before=event['before'];pending=before.get('pending_transaction')
    verifying=before['domain'].startswith('transaccion')and pending is not None
    pair=receipt['raw_observations']
    if verifying:
        payload=base64.b64decode(pending['payload_base64'])
        artifact=base64.b64decode(pending['prepared_output_base64'])
        valid=(hashlib.sha256(artifact).hexdigest()==pending['prepared_output_sha256'])
        valid=valid and(zlib.decompress(artifact)==payload if pending['prepared_by']==1 else artifact==hashlib.sha256(payload).digest())
        check=receipt.get('prepared_artifact_check')or{}
        actual_read=bool(check.get('actual_file_read')and check.get('sha256')==hashlib.sha256(artifact).hexdigest()and check.get('bytes')==len(artifact))
        if check.get('valid')!=bool(valid and actual_read):errors.append([label,'actual_prepared_artifact_read'])
        valid=valid and actual_read
        accepted=command!=pending['prepared_by']and valid
        operation='verify_commit'
    else:
        payload=bytes(pair)*max(1,32+sum(pair[::2]))
        accepted=command==(1 if sum(pair[::2])+before['reference']>=sum(pair[1::2])else-1)
        operation='prepare'if before['domain'].startswith('transaccion')else'execute_service'
    output=zlib.compress(payload,9)if command==1 else hashlib.sha256(payload).digest()
    expected=dict(worker=command,operation=operation,accepted=accepted,
        transaction_completed=bool(verifying and accepted),input_bytes=len(payload),
        input_sha256=hashlib.sha256(payload).hexdigest(),output_bytes=len(output),
        output_sha256=hashlib.sha256(output).hexdigest())
    for k,v in expected.items():
        if receipt.get(k)!=v:errors.append([label,'worker.'+k])
    return expected
def recalc(ev):
    errors=[];cases=[];allrows=[];archives={};views=0
    for p in sorted(ev.glob('*.json.gz')):
        d=read(p);manager=d.get('result',{});result=manager.get('result',{})
        if not isinstance(result,dict)or not result.get('rows'):continue
        case=d['case'];life=manager.get('INSTRUMENTO',{}).get('life_id')
        fence=manager.get('INSTRUMENTO_FENCE',{})
        if fence.get('denied'):errors.append([case,'denied_file_boundary'])
        rows=[]
        for i,r in enumerate(result['rows']):
            label=case+':'+str(i);command,posture,tick=decode(r)
            if command!=r['formed_native_command']or tick!=r['reader']['source_tick']:errors.append([label,'reader'])
            executed=command if r['row']['actuator']=='closed'else None
            if executed!=r['executed_external_command']:errors.append([label,'actuator'])
            q=r['situation'];raw=r['raw_components'];event=r['external_event']
            before=event['before'];credit=before['reference']
            worker=worker_check(event,executed,raw,errors,label)if before['domain']!='puertas'else None
            ok=bool(executed is not None and executed==(1 if sum(raw[::2])+credit>=sum(raw[1::2])else-1))if worker is None else worker['accepted']
            contact=executed is not None and not ok
            if ok!=r['job_completed']or contact!=r['observed_result']['contact']:errors.append([label,'environment'])
            returned=posture if contact else None
            if r['row']['feedback']=='omit':returned=None
            elif r['row']['feedback']=='decoupled'and returned is not None:returned=-returned if returned else 1
            if returned!=r['row']['returned_posture']:errors.append([label,'consequence'])
            tactile=[x for x in r['requests']if x['port'].startswith('EO01.post.tactile.')]
            if len(tactile)!=int(returned is not None):errors.append([label,'tactile_count'])
            if tactile and(tactile[0]['payload']!=0 or tactile[0]['tick']<=r['observed_result']['tick']):errors.append([label,'pre_action_solution'])
            extra=r['sensory_extra']['request_receipts']
            den=counts(r['requests']+extra)
            views+=verify_views(r,errors,label)
            own0=[fields(x['raw'])['s_reg']for x in r['before']['own']]
            own1=[fields(x['raw'])['s_reg']for x in r['after']['own']]
            frame=next(f for f in r['frames']if f['tick']==r['row']['critical_tick']-17)
            targets=[fields(x['raw'])['s_reg']for x in frame['sensory_fanin_targets']]
            if targets!=[sum(raw[::2]),sum(raw[1::2])]:errors.append([label,'four_raw_sensor_sum'])
            row=dict(case=case,ordinal=i,life=life,context=q['contexto'],regime=q.get('regimen','original'),
                tool=q.get('herramienta','puertas'),raw=raw,external_credit=credit,
                private_B_current_observation=q.get('privada_B'),
                start_tick=r['before']['tick'],end_tick=r['after']['tick'],
                command=command,executed=executed,useful=bool(ok),incorrect=bool(contact),
                abstention=command is None,feedback=r['row']['feedback'],posture=posture,
                own_before=own0,own_after=own1,counts=den,worker=worker,
                context_before=[fields(x['raw'])['s_reg']for x in r['before']['context_A']],
                context_after=[fields(x['raw'])['s_reg']for x in r['after']['context_A']],
                B_private_before=[fields(x['raw'])['s_reg']for x in r['before']['private_B']],
                B_private_after=[fields(x['raw'])['s_reg']for x in r['after']['private_B']],
                boundary_sample_source_tick=tick,first_use_before_current_feedback=True)
            rows.append(row);allrows.append(row)
        caseout=dict(case=case,file=p.name,sha256=sha(p),bytes=p.stat().st_size,
            returncode=d['returncode'],life=life,attempts=len(rows),
            useful=sum(x['useful']for x in rows),incorrect=sum(x['incorrect']for x in rows),
            abstentions=sum(x['abstention']for x in rows),
            counts={k:sum(x['counts'][k]for x in rows)for k in('requested','applied','rejected','pending')},
            rows=rows,code_revision=d.get('code_revision_sha256'))
        caseout['real_transactions']=sum(bool(x['worker']and x['worker']['transaction_completed'])for x in rows)
        caseout['declared_worker_processes']=len(fence.get('exact_environment_processes',[]))
        if sum(x['worker']is not None for x in rows)!=caseout['declared_worker_processes']:errors.append([case,'exact_worker_process_count'])
        cases.append(caseout)
        version=d.get('code_revision_sha256')
        if version and version not in archives:
            folder=ev/'codigo_ejecutado'/version;index=read(folder/'INDICE.json')
            matches=hashlib.sha256(json.dumps(index,sort_keys=True).encode()).hexdigest()==version
            bad=[n for n,s in index.items()if not(folder/n).is_file()or sha(folder/n)!=s]
            archives[version]=dict(index_matches=matches,members=len(index),mismatches=bad)
            if bad or not matches:errors.append([version,'executed_code_bytes'])
    lives={}
    for life in sorted({r['life']for r in allrows}):
        rs=sorted((r for r in allrows if r['life']==life),key=lambda r:r['start_tick'])
        gaps=[[a['end_tick'],b['start_tick']]for a,b in zip(rs,rs[1:])if a['end_tick']!=b['start_tick']]
        lives[life]=dict(attempts=len(rs),useful=sum(r['useful']for r in rs),
            incorrect=sum(r['incorrect']for r in rs),abstentions=sum(r['abstention']for r in rs),
            start_tick=rs[0]['start_tick'],end_tick=rs[-1]['end_tick'],gaps=gaps,
            first_own=rs[0]['own_before'],last_own=rs[-1]['own_after'])
    return dict(schema='MA.primary_recalculation.v1',cases=cases,lives=lives,
        first_use_panels={c['case']:dict(numerator=c['useful'],denominator=c['attempts'],
          note='Each current action precedes its own feedback. A previous different query in this panel may already have changed the shared state.')
          for c in cases if c['case']in('05_RETENCION_3','07_RETENCION_4','09_OTRAS_TRAS_REVISION','14_REGRESO_ANTERIOR','16_RESERVA_FINAL_MAIN')},
        verified_RAW_clock_views=views,executed_archives=archives,discrepancies=errors,
        scope='Archived measurements and byte arithmetic only; not a native reproduction or a claim of four retained contextual policies.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidencia',required=True,type=Path);p.add_argument('--salida',required=True,type=Path);a=p.parse_args()
    result=recalc(a.evidencia);a.salida.mkdir(parents=True,exist_ok=True)
    (a.salida/'RESULTADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({'lives':result['lives'],'discrepancies':result['discrepancies'],'RAW_clock_checks':result['verified_RAW_clock_views']}))
    return int(bool(result['discrepancies']))
if __name__=='__main__':raise SystemExit(main())
