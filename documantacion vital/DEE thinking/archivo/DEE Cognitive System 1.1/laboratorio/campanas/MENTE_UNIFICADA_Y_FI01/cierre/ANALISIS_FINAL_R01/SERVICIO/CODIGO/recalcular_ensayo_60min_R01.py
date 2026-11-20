"""Portable audit of the fixed sixty-minute service trial, not native replay.

Recomputes readers from archived uint64, deduplicated native admissions, actual
worker files/law, transport denominators and process-continuity witnesses.
"""
import argparse,base64,gzip,hashlib,json,struct,zlib
from collections import Counter
from pathlib import Path


def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def canonical(q):return json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
def walk(q,path='$'):
    if isinstance(q,dict):
        yield path,q
        for key,value in q.items():yield from walk(value,path+'.'+str(key))
    elif isinstance(q,list):
        for index,value in enumerate(q):yield from walk(value,path+'['+str(index)+']')
def fields(n):
    if type(n)is not int and not(isinstance(n,str)and n.isdecimal()):raise ValueError('RAW must be an exact integer/decimal string, never float/bool')
    n=int(n)
    if not 0<=n<2**64:raise ValueError('Exact uint64 RAW required')
    def signed(k):v=(n>>k)&15;return v-16 if v>=8 else v
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'direction':[signed(k)for k in(48,52,56)],'semantic':(n>>60)&15}
def calculate(root):
    result=load(root/'RESULTADO.json');protocol=load(root/'PROTOCOLO.json');rows=load(root/'REGISTROS_TRANSPORTE.json.gz');complete=load(root/'CAMPOS_Y_RECIBOS_COMPLETOS.json.gz');artifact_index=load(root/'ARTEFACTOS_REALES.json');events=[json.loads(line)for line in(root/'ADMISIONES_Y_EVENTOS.jsonl').read_text(encoding='utf8').splitlines()if line]
    checks={};issues=[];sources=[];raw=0;uint64_count=0;native={};native_readers=[];memory=[];worker_rows=[];prepared={};request_outcomes=[];fence_calls=0;native_observation_paths=Counter()
    def check(label,value):
        checks[label]=bool(value)
        if not value:issues.append(label)
    for name in('RESULTADO.json','PROTOCOLO.json','REGISTROS_TRANSPORTE.json.gz','CAMPOS_Y_RECIBOS_COMPLETOS.json.gz','ARTEFACTOS_REALES.json','ADMISIONES_Y_EVENTOS.jsonl','FUENTES_Y_CORTE_ANTES_DEL_PRIMER_TICK.json'):
        b=(root/name).read_bytes();sources.append({'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    check('frozen_480_opportunities',len(protocol['events'])==protocol['nominal_events']==480)
    check('protocol_identity',hashlib.sha256((root/'PROTOCOLO.json').read_bytes()).hexdigest()==result['protocol_sha256'])
    for item in result['sources']:
        data=(root/'codigo'/item['file']).read_bytes();check('archived_executed_source_'+item['file'],len(data)==item['bytes']and hashlib.sha256(data).hexdigest()==item['sha256'])
    for label,f in complete['snapshots'].items():
        size=f['N']**3;values=[0]*size;clocks=[int(f['clock_default'])]*size
        for index,v in f['raw_nonzero']:values[index]=int(v)
        for index,v in f['clock_exceptions']:clocks[index]=int(v)
        for field,array in(('RAW',values),('clocks',clocks)):
            if any(type(v)is not int or not 0<=v<2**64 for v in array):raise ValueError('Exact complete-field uint64 required')
            digest=hashlib.sha256(b''.join(struct.pack('<Q',v)for v in array)).hexdigest();uint64_count+=len(array);check(label+'_'+field,digest==f[field+'_sha256'])
        rec=result['before'if label=='before'else'final'];check(label+'_exact_snapshot_source',f['snapshot_sha256']==rec['snapshot_sha256']and f['tick']==rec['physical']['tick'])
    artifact_files={}
    for item in artifact_index['files']:
        data=(root/item['file']).read_bytes();check('actual_artifact_'+item['file'],len(data)==item['bytes']and hashlib.sha256(data).hexdigest()==item['sha256']);artifact_files[(item['output_name'],item['sha256'])]=data
    def audit_reader(reader,identifier,path):
        if 'observations'in reader and 'choice'in reader:
            observations=reader['observations'];candidate=[];expected={(15+2*x,17,15+2*z):(x,1,z)for x in(-1,0,1)for z in(0,-1)}
            actual={tuple(o['site'])for o in observations};allowed=expected if len(observations)==6 else{k:v for k,v in expected.items()if k[2]==15}
            check(identifier+'_'+path+'_fixed_geometry',actual==set(allowed))
            for o in observations:
                f=fields(o['raw']);direction=list(allowed.get(tuple(o['site']),()))
                if f['state']>0 and f['semantic']==1 and f['direction']==direction:candidate.append(direction[0])
            answer=candidate[0]if len(candidate)==1 else None;check(identifier+'_'+path+'_native_reader',reader['choice']==answer)
            native_readers.append({'id':identifier,'path':path,'tick':reader.get('tick'),'choice':answer,'fixed_classes':len(observations)})
        if 'panel'in reader and 'formed_native_command'in reader:
            expected={(37,33,32),(37,33,34),(33,37,32),(33,37,34),(37,37,32),(37,37,34),(29,37,32),(29,37,34),(37,29,32),(37,29,34),(29,29,32),(29,29,34)}
            check(identifier+'_'+path+'_twelve_frozen_memory_gates',len(reader['panel'])==12 and{tuple(o['site'])for o in reader['panel']}==expected)
            candidate=[]
            for o in reader['panel']:
                f=fields(o['raw'])
                if f['state']>0 and f['semantic']==1 and f['direction'][:2]==[0,0]and f['direction'][2]in(-1,1):candidate.append(f['direction'][2])
            answer=candidate[0]if len(candidate)==1 else None;check(identifier+'_'+path+'_memory_reader',reader['formed_native_command']==answer)
    ordered=[r for r in rows if r['id'].startswith('fi60_')]
    for transport in ordered:
        identifier=transport['id'];payload=json.loads(transport['payload']);check(identifier+'_literal_payload',hashlib.sha256(canonical(payload)).hexdigest()==transport['payload_sha']);request_outcomes.append({'id':identifier,'transport_status':transport['status'],'operation':payload['operacion'],'mode':payload.get('situaciones',[{}])[0].get('modo')})
        if not transport['result']:continue
        answer=json.loads(transport['result']);top=answer.get('result',{});fence=top.get('INSTRUMENTO_FENCE')
        if fence:
            check(identifier+'_no_fence_denials',not fence['denied']);fence_calls+=len(fence['exact_environment_processes'])
        for path,node in walk(top):
            if all(k in node for k in('raw','state','s_reg','semantic','direction')):
                f=fields(node['raw']);raw+=1;native_observation_paths[node.get('tick')]+=1;check(identifier+'_'+path+'_RAW',all(node[k]==v for k,v in f.items()))
            if 'receipt'in node and isinstance(node['receipt'],dict)and all(k in node['receipt']for k in('id','status','requested_tick')):
                rr=node['receipt'];old=native.get(rr['id']);check(identifier+'_'+path+'_receipt_consistency',old is None or old==rr);native[rr['id']]=rr
            if 'reader'in node and isinstance(node['reader'],dict):
                audit_reader(node['reader'],identifier,path)
                if 'context_signal'in node and 'formed_native_command'in node['reader']:
                    memory.append({'id':identifier,'context':node['context_signal'],'tick':node.get('read_tick'),'choice':node['reader']['formed_native_command']})
            if node.get('schema')=='EO02.local_worker.receipt.v2':
                receipt=node;public=receipt['raw_observations'];content=bytes(public)*max(1,32+sum(public[::2]));output=zlib.compress(content,9)if receipt['worker']==1 else hashlib.sha256(content).digest();actual=artifact_files.get((receipt['output_name'],receipt['output_sha256']))
                check(identifier+'_'+path+'_actual_worker_bytes',actual==output and len(output)==receipt['output_bytes']and hashlib.sha256(content).hexdigest()==receipt['input_sha256']and len(content)==receipt['input_bytes'])
                if receipt['operation']in('prepare','execute_service'):
                    expected=1 if sum(public[::2])+receipt['modelled_capacity_credit_not_actor_input']>=sum(public[1::2])else-1
                    check(identifier+'_'+path+'_environmental_law',receipt['accepted']==(receipt['worker']==expected))
                    if receipt['operation']=='prepare'and receipt['accepted']:prepared[receipt['output_name']]=receipt
                elif receipt['operation']=='verify_commit':
                    old=prepared.get(receipt['prepared_artifact_check']['name']);check(identifier+'_'+path+'_known_actual_prepared_artifact',old is not None)
                    if old:check(identifier+'_'+path+'_verify_law',receipt['accepted']==(receipt['worker']!=old['worker']and receipt['prepared_artifact_check']['valid']))
                worker_rows.append({'id':identifier,'operation':receipt['operation'],'worker':receipt['worker'],'accepted':receipt['accepted'],'transaction_completed':receipt['transaction_completed'],'public_values':public,'bytes':len(output),'native_tick':receipt['native_tick']})
    archived={r['id']:r for r in complete['new_receipts']};status_mapping={}
    for identifier,rr in native.items():
        saved=archived.get(identifier);check('native_saved_receipt_'+str(identifier),saved is not None)
        if saved:
            check('native_receipt_times_'+str(identifier),saved['requested_tick']==rr['requested_tick']and saved['effective_tick']==rr['effective_tick']and saved['channels']==rr['channels'])
            status_mapping.setdefault(saved['status'],set()).add(rr['status'])
    check('numeric_receipt_status_mapping_consistent',all(len(v)==1 for v in status_mapping.values()))
    native_counts=Counter(next(iter(status_mapping[r['status']]))if r['status']in status_mapping else'unmapped_numeric_'+str(r['status'])for r in archived.values())
    check('sixty_real_minutes_recorded',result.get('host_seconds_from_owner_ready_to_horizon',0)>=3600)
    check('one_life_one_genealogy',result['before']['life_id']==result['final']['life_id']==protocol['life_id']and result['before']['world_id']==result['final']['world_id']and result['before']['parent']==result['final']['parent'])
    check('all_executed_source_bytes_unchanged',all(x['unchanged']for x in result['final_source_integrity']))
    reloads=[e for e in events if e['kind']=='same_life_full_state_process_reload'];check('one_planned_process_reload',len(reloads)==1)
    if reloads:
        reload=reloads[0];check('pending_full_protocol_and_fields_preserved',reload['physical_equal']and reload['pending_protocol_equal']);check('genuine_pending_chain_at_reload',reload['before']['operational_dependencies']['external_pending_present']and reload['before']['operational_dependencies']['cascade_pending_present'])
    pause=[e for e in events if e['kind']=='pause_exact_boundary_comparison'];check('three_exact_pauses',len(pause)==3 and all(e['equal']for e in pause))
    last_memory={}
    for q in memory:last_memory[q['context']]=q
    admission_events=[e for e in events if e['kind']in('admission','transport_validation_rejection')]
    admissions=Counter(e['reply']['admission']if e['kind']=='admission'else'rejected_transport_validation'for e in admission_events)
    nominal={e['id']for e in protocol['events']};observed={e['id']for e in admission_events}
    check('every_nominal_opportunity_was_attempted',nominal<=observed)
    material=[r for r in request_outcomes if r['operation']=='sesion']
    return {'schema':'DEE.unified.sixty_minute_archived_recalculation.v1','sources':sources,'issues':issues,'checks':checks,
        'serialized_RAW_observations_checked':raw,'complete_uint64_checked':uint64_count,'native_receipts':{'requested':len(archived),**dict(native_counts),'covered_by_named_completed_result_receipts':len(native),'missing_named_receipt_ids':sorted(set(archived)-set(native))},
        'transport_admission_denominators':{'requested_material_attempts':len(admission_events),'nominal_attempts':len(nominal&observed),**dict(admissions)},
        'material_request_outcomes':dict(Counter(r['transport_status']for r in material)),
        'transport_outcomes_including_controls':dict(Counter(r['transport_status']for r in request_outcomes)),'all_request_outcomes':request_outcomes,'native_readers':native_readers,'memory_uses':memory,'last_memory_uses':last_memory,'workers':worker_rows,'fence_external_calls':fence_calls,
        'worker_counts':{'actual_executions':len(worker_rows),'accepted':sum(x['accepted']for x in worker_rows),'rejected':sum(not x['accepted']for x in worker_rows),'transaction_commits':sum(x['transaction_completed']for x in worker_rows)},
        'wall_seconds_recorded':result.get('host_seconds_from_owner_ready_to_horizon'),'initial':result['before'],'final':result['final'],
        'scope':'Recalculation only: no DEE import, Runtime, worker rerun or policy training. Repeated uses belong to one life. Operational requests/idle ticks/worker usefulness are separate. beta+ is explicit re-teaching, not autonomous learning or retention of old beta-. A missing/ambiguous native output is not filled from its expected answer.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();result=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'issues':result['issues'],'RAW':result['serialized_RAW_observations_checked'],'complete_uint64':result['complete_uint64_checked'],'workers':result['worker_counts']}));return bool(result['issues'])
if __name__=='__main__':raise SystemExit(main())
