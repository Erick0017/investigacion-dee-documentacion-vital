"""Portable audit of the actual APD service archive; never native replay.

All arithmetic below is an external audit of already emitted native operators.
The archive, diaries and computed verdicts never feed the participant.
"""
import argparse,gzip,hashlib,importlib.util,json,struct,zlib
from collections import Counter
from pathlib import Path
_spec=importlib.util.spec_from_file_location('archived_APD_auditor',Path(__file__).with_name('auditar_apd_resultados_r04.py'))
apd=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(apd)

def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(q):return json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
def walk(q,path='$'):
    if isinstance(q,dict):
        yield path,q
        for key,value in q.items():yield from walk(value,path+'.'+str(key))
    elif isinstance(q,list):
        for i,value in enumerate(q):yield from walk(value,path+'['+str(i)+']')
def fields(raw):
    u=apd.unpack(raw);return {'state':int(raw)&0xffffffff,'s_reg':u['payload'],'direction':u['direction'],'semantic':u['semantic']}
def memory(reader):
    expected={(37,33,32),(37,33,34),(33,37,32),(33,37,34),(37,37,32),(37,37,34),(29,37,32),(29,37,34),(37,29,32),(37,29,34),(29,29,32),(29,29,34)}
    panel=reader['panel']
    if len(panel)!=12 or{tuple(o['site'])for o in panel}!=expected:raise ValueError('The fixed twelve old-memory gates differ')
    candidates=[]
    for o in panel:
        n=apd.unpack(o['raw'])
        expected_sign=o['site'][2]-33
        if n['active']and n['semantic']==1 and n['direction']==[0,0,expected_sign]:candidates.append(expected_sign)
    return candidates[0]if len(candidates)==1 else None

def calculate(root):
    result=load(root/'RESULTADO.json');interrupted=load(root/'CORTE_INTERRUMPIDO.json')if not result.get('final')and(root/'CORTE_INTERRUMPIDO.json').is_file()else None
    if interrupted:result={**result,'final':interrupted['main']}
    pro=load(root/'PROTOCOLO.json');rows=load(root/'REGISTROS_APD.json.gz');complete=load(root/'CAMPOS_Y_RECIBOS_COMPLETOS.json.gz');artifacts=load(root/'ARTEFACTOS_REALES.json');events=[json.loads(x)for x in(root/'ADMISIONES_Y_EVENTOS.jsonl').read_text(encoding='utf8').splitlines()if x]
    prefix=pro['request_prefix'];inherited_ids={r['id']for r in pro.get('inherited_pending_rows',[])};checks=Counter();issues=[];raw_count=0;uint64_count=0;native={};all_readers=[];memories=[];workers=[];prepared={};calendars=[];outcomes=[];apd_rows=[];counts=[];compositions=[];explicit=[];environment=[];fences=[];worker_seen=set();reader_seen=set();memory_seen=set()
    def check(label,ok):
        checks['total']+=1;checks['passed'if ok else'failed']+=1
        if not ok:issues.append(label)
    def audit_tree(node,identifier,path):
        try:
            audited=apd.audit(node,root/'artefactos')
            check(identifier+'_'+path+'_APD_decoder_and_bytes',not audited['issues'])
        except Exception as error:
            audited={'issues':[type(error).__name__+': '+str(error)],'audit_failed_not_repaired':True};check(identifier+'_'+path+'_APD_audit_supported',False)
        return audited
    source_names=('RESULTADO.json','PROTOCOLO.json','REGISTROS_APD.json.gz','PROYECCION_TRANSPORTE.json','BASELINE_P26.json.gz','CAMPOS_Y_RECIBOS_COMPLETOS.json.gz','ARTEFACTOS_REALES.json','ADMISIONES_Y_EVENTOS.jsonl','FUENTES_Y_CORTE_ANTES_DEL_PRIMER_TICK.json')
    sources=[{'file':name,'bytes':(root/name).stat().st_size,'sha256':sha(root/name)}for name in source_names]
    check('fresh_APD_transport_prefix',prefix in('apd60_','apd61_')and all(e['id'].startswith(prefix)for e in pro['events']))
    check('480_frozen_opportunities',pro['nominal_events']==len(pro['events'])==480)
    check('frozen_protocol_SHA',sha(root/'PROTOCOLO.json')==result['protocol_sha256'])
    provenance=load(root/'PROYECCION_TRANSPORTE.json')
    check('complete_prefix_projection_hash_and_count',provenance['selected_sha256']==sha(root/'REGISTROS_APD.json.gz')and provenance['selected_rows']==len(rows)and all(r['id'].startswith(prefix)or r['id']in inherited_ids for r in rows)and set(provenance['inherited_pending_ids'])==inherited_ids)
    baseline=load(root/'BASELINE_P26.json.gz');baseline_queries=[];baseline_signs={}
    check('baseline_original_case_P26',baseline.get('case')=='P26_PREPARACION_TERCER_CURRICULO_MAIN'and baseline.get('returncode')==0)
    for path,node in walk(baseline['result']):
        if node.get('kind')=='lexical_query':
            decoded=apd.lexical(node['reader']);check('baseline_'+path+'_fixed24_reader',decoded['gate_count']==24 and decoded['agrees_with_archived_command'])
            baseline_queries.append({'form':node['form'],'tick':node['read_tick'],'sign':decoded['command']});baseline_signs[node['form']]=decoded['command']
    check('baseline_old10_and_no_new_word_use',set(baseline_signs)=={'alfa','beta','gamma','delta','epsilon','zeta','suma','diferencia','agrega','resta'}and all(s in(-1,1)for s in baseline_signs.values()))
    for item in result['sources']:
        f=root/'codigo'/item['file'];check('executed_source_'+item['file'],f.stat().st_size==item['bytes']and sha(f)==item['sha256'])
    for label,s in complete['snapshots'].items():
        n=s['N']**3;arrays={'RAW':[0]*n,'clocks':[int(s['clock_default'])]*n}
        for i,v in s['raw_nonzero']:arrays['RAW'][i]=int(v)
        for i,v in s['clock_exceptions']:arrays['clocks'][i]=int(v)
        for key,values in arrays.items():
            if any(type(v)is not int or not 0<=v<2**64 for v in values):raise ValueError('Full fields must be exact uint64')
            digest=hashlib.sha256(b''.join(struct.pack('<Q',v)for v in values)).hexdigest();uint64_count+=len(values);check(label+'_'+key+'_complete_SHA',digest==s[key+'_sha256'])
        rec=result['before'if label=='before'else'final'];check(label+'_named_full_checkpoint',s['snapshot_sha256']==rec['snapshot_sha256']and s['tick']==rec['physical']['tick'])
    artifact_bytes={}
    for item in artifacts['files']:
        data=(root/item['file']).read_bytes();check('actual_artifact_'+item['file'],len(data)==item['bytes']and hashlib.sha256(data).hexdigest()==item['sha256']);artifact_bytes[(item['output_name'],item['sha256'])]=data
    selected=[r for r in rows if r['id'].startswith(prefix)or r['id']in inherited_ids]
    for transport in selected:
        identifier=transport['id'];payload=json.loads(transport['payload']);situations=payload.get('situaciones',[]);mode=situations[0].get('modo')if situations else None
        check(identifier+'_literal_payload_SHA',hashlib.sha256(canonical(payload)).hexdigest()==transport['payload_sha'])
        outcomes.append({'id':identifier,'seq':transport['seq'],'status':transport['status'],'operation':payload['operacion'],'mode':mode,'request_origin':'inherited_queued_R01'if identifier in inherited_ids else'new_R02'if prefix=='apd61_'else'new_R01'})
        if not transport.get('result'):continue
        answer=json.loads(transport['result']);top=answer.get('result',{});fence=top.get('INSTRUMENTO_FENCE')
        if fence:
            check(identifier+'_observed_guard_denials_empty',not fence['denied']);fences.append({'id':identifier,**fence})
        # Audit each top-level APD/composition once; children are still RAW checked below.
        def apd_nodes(value,path='$'):
            if isinstance(value,dict):
                if value.get('kind')in('APD01_integrated_request','APD01_prepared_count','APD01_assisted_composition'):
                    yield path,value;return
                for k,v in value.items():yield from apd_nodes(v,path+'.'+str(k))
            elif isinstance(value,list):
                for i,v in enumerate(value):yield from apd_nodes(v,path+'['+str(i)+']')
        for path,node in apd_nodes(top):
            audited=audit_tree(node,identifier,path);item={'id':identifier,'path':path,'before_tick':answer.get('before_tick'),'after_tick':answer.get('after_tick'),'audit':audited}
            if node['kind']=='APD01_integrated_request':apd_rows.append({**item,'literal_form':node['literal_form'],'environment':node['environment'],'procedure':node['procedure'],'completed':node['completed'],'numeric_result':node['numeric_result'],'native_route':node['native_route_command'],'modeled_price':node['modeled_price'],'consequence_cost':node['consequence_cost'],'return_count':len(node['outcome_returns'])})
            elif node['kind']=='APD01_prepared_count':counts.append({**item,'samples':node['presence_samples']})
            else:compositions.append({**item,'literal_forms':node.get('literal_forms'),'raw_data':node.get('raw_data'),'result':node.get('result'),'out_of_domain':node.get('out_of_domain'),'program':node.get('program')})
        for path,node in walk(top):
            if all(k in node for k in('raw','state','s_reg','semantic','direction')):
                raw_count+=1;decoded=fields(node['raw']);check(identifier+'_'+path+'_RAW_fields',all(node[k]==v for k,v in decoded.items()))
            rr=node.get('receipt')
            if isinstance(rr,dict)and all(k in rr for k in('id','status','requested_tick')):
                old=native.get(rr['id']);immutable=('requested_tick','channels');consistent=old is None or all(old[k]==rr[k]for k in immutable)
                if old and old.get('effective_tick')is not None and rr.get('effective_tick')is not None:consistent=consistent and old['effective_tick']==rr['effective_tick']
                check(identifier+'_'+path+'_receipt_identity',consistent)
                if not old or old['status']not in('applied','rejected','cancelled')or rr['status']in('applied','rejected','cancelled'):native[rr['id']]=rr
            reader=node.get('reader')
            if isinstance(reader,dict)and'observations'in reader and'choice'in reader:
                observations=reader['observations'];origin=reader.get('origin')
                if origin is None:
                    ys={o['site'][1]for o in observations};origin=[15,next(iter(ys))-2,15]if len(ys)==1 else None
                try:
                    check(identifier+'_'+path+'_allowed_selector_origin',origin in([15,15,15],[15,45,15]))
                    decoded=apd.selector(reader,origin);check(identifier+'_'+path+'_fixed_selector_RAW',decoded['agrees_with_archived_choice'])
                    rkey=(identifier,reader.get('tick'),tuple(origin))
                    if rkey not in reader_seen:all_readers.append({'id':identifier,'path':path,'tick':reader.get('tick'),'choice':decoded['choice'],'origin':origin,'candidates':decoded['candidates']});reader_seen.add(rkey)
                except Exception as error:check(identifier+'_'+path+'_selector_decode_'+type(error).__name__,False)
            if isinstance(reader,dict)and'panel'in reader and'formed_native_command'in reader:
                try:
                    choice=memory(reader)if len(reader['panel'])==12 else apd.lexical(reader)['command'];check(identifier+'_'+path+'_fixed_common_gate_reader',choice==reader['formed_native_command'])
                    if 'context_signal'in node:
                        mkey=(identifier,node['context_signal'],node.get('read_tick'))
                        if mkey not in memory_seen:memories.append({'id':identifier,'context':node['context_signal'],'tick':node.get('read_tick'),'choice':choice});memory_seen.add(mkey)
                except Exception as error:check(identifier+'_'+path+'_gate_decode_'+type(error).__name__,False)
            if all(k in node for k in('requested_query_tick','effective_query_tick','wait_ticks','critical_window_inclusive')):
                rq=node['requested_query_tick'];eq=node['effective_query_tick'];boundary=((rq-2)//391+1)*391;expected=boundary+2 if boundary<=rq+8 else rq
                check(identifier+'_'+path+'_prepared_sensor_calendar',eq==expected and node['wait_ticks']==eq-rq and node['critical_window_inclusive']==[eq-1,eq+8]and(eq-2)//391==(eq+8)//391)
                calendars.append({'id':identifier,'path':path,'requested_query_tick':rq,'effective_query_tick':eq,'wait_ticks':eq-rq})
            if node.get('schema')=='EO02.local_worker.receipt.v2':
                wkey=(node['operation'],node['output_name'],node['output_sha256'],node['host_started_ns'])
                if wkey in worker_seen:continue
                worker_seen.add(wkey)
                public=node['raw_observations'];content=bytes(public)*max(1,32+sum(public[::2]));out=zlib.compress(content,9)if node['worker']==1 else hashlib.sha256(content).digest();actual=artifact_bytes.get((node['output_name'],node['output_sha256']))
                check(identifier+'_'+path+'_real_worker_output',actual==out and len(out)==node['output_bytes']and hashlib.sha256(content).hexdigest()==node['input_sha256']and len(content)==node['input_bytes'])
                if node['operation']in('prepare','execute_service'):
                    expected=1 if sum(public[::2])+node['modelled_capacity_credit_not_actor_input']>=sum(public[1::2])else-1;check(identifier+'_'+path+'_worker_environmental_law',node['accepted']==(node['worker']==expected))
                    if node['operation']=='prepare'and node['accepted']:prepared[node['output_name']]=node
                elif node['operation']=='verify_commit':
                    old=prepared.get(node['prepared_artifact_check']['name']);check(identifier+'_'+path+'_actual_prior_preparation',old is not None)
                    if old:
                        pc=node['prepared_artifact_check'];prior_bytes=artifact_bytes.get((old['output_name'],old['output_sha256']));valid=prior_bytes is not None and len(prior_bytes)==pc['bytes']and hashlib.sha256(prior_bytes).hexdigest()==pc['sha256']and node['input_bytes']==old['input_bytes']and node['input_sha256']==old['input_sha256']
                        check(identifier+'_'+path+'_pending_artifact_and_original_payload',pc['valid']==valid and pc['actual_file_read']is True)
                        check(identifier+'_'+path+'_worker_commit_law',node['accepted']==(node['worker']!=old['worker']and valid))
                workers.append({'id':identifier,'operation':node['operation'],'worker':node['worker'],'accepted':node['accepted'],'transaction_completed':node['transaction_completed'],'public_values':public,'bytes':len(out),'native_tick':node['native_tick']})
            if node.get('kind')=='explicit_environment_change':environment.append({'id':identifier,**node})
            if ('teaching_signal'in node or node.get('kind')=='explicit_teaching')and 'requests'in node:
                explicit.append({'id':identifier,'path':path,'mode':mode,'context':node.get('context_signal',node.get('form')),'signal':node.get('teaching_signal',node.get('teacher_sign')),'before_tick':answer.get('before_tick'),'after_tick':answer.get('after_tick'),'admissions':apd.admissions(node)})
    saved={r['id']:r for r in complete['new_receipts']};mapping={}
    for key,rr in native.items():
        archived=saved.get(key);check('full_saved_receipt_'+str(key),archived is not None)
        if archived:
            check('full_saved_receipt_fields_'+str(key),all(archived[k]==rr[k]for k in('requested_tick','effective_tick','channels')));mapping.setdefault(archived['status'],set()).add(rr['status'])
    check('numeric_native_status_mapping_consistent',all(len(v)==1 for v in mapping.values()))
    native_counts=Counter(next(iter(mapping[r['status']]))if r['status']in mapping else'unmapped_numeric_'+str(r['status'])for r in saved.values())
    admission_events=[e for e in events if e['kind']in('admission','transport_validation_rejection')];admissions=Counter(e['reply']['admission']if e['kind']=='admission'else'rejected_transport_validation'for e in admission_events)
    nominal={e['id']for e in pro['events']};attempted={e['id']for e in admission_events}
    if interrupted:check('interrupted_prefix_honestly_preserved',result.get('error')and not interrupted['sixty_minutes_claimed']and interrupted['original_RESULTADO_sha256']==sha(root/'RESULTADO.json'))
    else:check('all480_nominal_opportunities_attempted',nominal<=attempted)
    check('same_life_world_parent',all(result['before'][k]==result['final'][k]for k in('life_id','world_id','parent')))
    material=[r for r in outcomes if r['operation']=='sesion'and r['id'].startswith(prefix)];inherited_outcomes=[r for r in outcomes if r['id']in inherited_ids];last={}
    for item in memories:last[item['context']]=item
    return {'schema':'DEE.APD01.service_archived_recalculation.v1','sources':sources,'checks':dict(checks),'issues':issues,'serialized_RAW_observations_checked':raw_count,'complete_uint64_checked':uint64_count,
        'native_receipts':{'requested':len(saved),**dict(native_counts),'covered_by_completed_results':len(native),'not_repeated_in_completed_results':sorted(set(saved)-set(native))},
        'transport_admission_denominators':{'all_literal_attempts':len(admission_events),'material_literal_attempts':sum(e['payload'].get('operacion')=='sesion'for e in admission_events),'nominal_attempts':len(nominal&attempted),**dict(admissions)},
        'material_request_outcomes':dict(Counter(r['status']for r in material)),'inherited_pending_execution_outcomes':inherited_outcomes,'all_request_outcomes':outcomes,'native_readers':all_readers,'memory_uses':memories,'last_memory_uses':last,'prepared_sensor_calendar_uses':calendars,
        'APD_requests':apd_rows,'native_counts':counts,'assisted_compositions':compositions,'explicit_teaching':explicit,'environment_changes':environment,'workers':workers,
        'worker_counts':{'actual_executions':len(workers),'accepted':sum(r['accepted']for r in workers),'transaction_commits':sum(r['transaction_completed']for r in workers)},
        'guard_reports':{'reports':len(fences),'exact_environment_process_calls':sum(len(r.get('exact_environment_processes',[]))for r in fences),'denials':sum(len(r['denied'])for r in fences),'legacy_boolean_not_a_history_filesystem_ACL':True,
          'scope':'Archived Python audit-hook observations, not an OS sandbox or impossibility of reading every history file. Source review/physical controls separately address hidden decision inputs. Legacy descriptors are preserved, not retroactively rewritten.'},
        'baseline_history':{'source_file':'BASELINE_P26.json.gz','source_sha256':sha(root/'BASELINE_P26.json.gz'),'case':baseline['case'],'queries':baseline_queries,'last_physically_decoded_signs':baseline_signs,'scope':'Historical preceding P26 panel, not a new query or a claim of accessibility after later idle time.'},
        'recorded_completion_criteria':{'all480_nominal_opportunities_attempted':nominal<=attempted,'interrupted_harness_prefix':bool(interrupted),'original_harness_error':result.get('error'),'sixty_minutes_not_inferred_from_integrity_checks':True},
        'initial':result['before'],'final':result['final'],'scope':'External recalculation only: no engine, Runtime, worker execution, learned policy, target feedback or repaired physical response. Same-life requests are not independent learners. Operator teaching and curriculum remain declared assistance; numeric correctness is checked conditional on the actual acquired operator.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':r['issues'],'RAW':r['serialized_RAW_observations_checked'],'uint64':r['complete_uint64_checked'],'native':r['native_receipts'],'APD':len(r['APD_requests']),'compositions':len(r['assisted_compositions'])}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
