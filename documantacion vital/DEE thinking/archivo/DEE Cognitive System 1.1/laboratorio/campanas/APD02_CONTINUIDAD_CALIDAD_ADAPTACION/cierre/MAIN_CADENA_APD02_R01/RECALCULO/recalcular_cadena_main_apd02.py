"""Independent archived RAW/receipt/real-effect audit; never import DEE."""
import argparse,collections,gzip,hashlib,importlib.util,json
from pathlib import Path

N=67
I=(33,33,33);J=(47,47,47);H=(47,17,47)
CONTEXTS={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0),'epsilon':(1,-1,0),'zeta':(-1,-1,0)}
HISTORY={'alfa':-1,'beta':-1,'gamma':1,'delta':-1,'epsilon':-1,'zeta':1}
FORM_CODEC={**{f:(I,v)for f,v in CONTEXTS.items()},'suma':(I,(-1,0,0)),'diferencia':(I,(0,-1,0)),'agrega':(J,(-1,0,0)),'resta':(J,(0,-1,0)),'total':(J,(1,0,0)),'quita':(J,(0,1,0)),'compara':(H,(1,0,0)),'recuerda':(H,(0,1,0))}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def walk(x,path='$'):
    yield path,x
    if isinstance(x,dict):
        for k,v in x.items():yield from walk(v,path+'.'+k)
    elif isinstance(x,list):
        for k,v in enumerate(x):yield from walk(v,path+'['+str(k)+']')
def decoded(o):
    n=int(o['raw'])
    if not 0<=n<2**64:raise ValueError('RAW not uint64')
    return{'state':n&0xffffffff,'semantic':(n>>60)&15,'s_reg':(n>>32)&65535,'direction':[((n>>k)&15)-(16 if((n>>k)&15)>=8 else 0)for k in(48,52,56)],'active':bool(n&0xffffffff)}
def pos(origin,v,k,z=0):return tuple((origin[j]+k*v[j]+(z if j==2 else 0))%N for j in range(3))
def content(x):return{k:v for k,v in x.items()if k!='evaluation_resources'}
def pure_z(reader,codec):
    expected={pos(o,v,4,sg):sg for o,v in codec.values()for sg in(-1,1)}
    panel=reader['panel'];sites=[tuple(o['site'])for o in panel]
    if len(sites)!=len(expected)or set(sites)!=set(expected):raise ValueError('Fixed complete pureZ gate set differs')
    candidates=[]
    for o in panel:
        d=decoded(o);sg=expected[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==[0,0,sg]:candidates.append({'site':o['site'],'sign':sg,'s_reg':d['s_reg']})
    return candidates[0]['sign']if len(candidates)==1 else None,candidates
def selector(reader,origin):
    expected={tuple((origin[j]+off[j])%N for j in range(3)):(x,z)for x in(-1,0,1)for z in(0,-1)for off in[(2*x,2,2*z)]}
    sites=[tuple(o['site'])for o in reader['observations']]
    if len(sites)!=6 or set(sites)!=set(expected):raise ValueError('Fixed six selector gates differ')
    candidates=[]
    for o in reader['observations']:
        d=decoded(o);x,z=expected[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==[x,1,z]:candidates.append(x)
    return candidates[0]if len(candidates)==1 else None,candidates
def numeric(row):
    trial=row['native_trial'];at=int(trial['datum_tick'])-2;frames=[f for f in trial['frames']if int(f['tick'])==at]
    if len(frames)!=1:raise ValueError('Missing unique frozen numeric frame')
    o=frames[0]['fields']['C'];d=decoded(o);valid=(o['site']==[12,17,18]and int(o['tick'])==at and bool(d['state'])and d['semantic']==1 and d['direction']==[1,-1,-1])
    return(d['s_reg']-(0 if row['operation']=='suma'else 32))if valid else None
def delta_read(frame):
    reader=frame['reader'];sites=reader['sites']
    if len(sites)!=2 or {tuple(o['site'])for o in sites}!={(25,25,30),(26,25,30)}:raise ValueError('Recirculation common gates changed')
    candidates=[]
    for o in sites:
        d=decoded(o)
        if d['state']and d['semantic']==1 and d['direction']==[0,1,0]:candidates.append({'site':o['site'],'value':d['s_reg']-4096,'raw':str(o['raw'])})
    return candidates[0]['value']if len(candidates)==1 else None,candidates

def calculate(root,evaluator_path):
    primary=root/'REGISTROS_VENTANA.json.gz';x=read(primary);proto=read(root/'PROTOCOLO.json');artifact_index=read(root/'ARTEFACTOS.json')
    spec=importlib.util.spec_from_file_location('private_post_effect_auditor',evaluator_path);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
    issues=[];checks=collections.Counter();raw_count=0;raw_unique={};receipts={};readers=[];numerics=[]
    def check(label,ok):
        checks['checks']+=1
        if not ok:issues.append(label)
    rows={k:v for k,v in x['records'].items()if not k.endswith('_parsed')}
    for identifier,transport in rows.items():
        parsed=json.loads(transport['result']);check(identifier+':transport_id',transport['id']==identifier==parsed['id']);check(identifier+':completed',transport['status']=='completed');check(identifier+':payload_sha',hashlib.sha256(transport['payload'].encode()).hexdigest()==transport['payload_sha'])
        if identifier+'_parsed'in x['records']:check(identifier+':parsed_mirror',parsed==x['records'][identifier+'_parsed'])
        fence=parsed.get('result',{}).get('INSTRUMENTO_FENCE')
        if fence:check(identifier+':scope_guard',not fence['denied']and fence.get('operational_history_reads_universally_blocked')is False)
        # Inspect exactly one parsed result per transport ID, never both mirrors.
        for path,node in walk(parsed):
            if not isinstance(node,dict):continue
            if 'raw'in node and'site'in node and'tick'in node:
                d=decoded(node);raw_count+=1
                for key,value in d.items():
                    if key in node:check(identifier+path+':'+key,node[key]==value)
                ident=(tuple(node['site']),int(node['tick']));stamp=(str(node['raw']),str(node.get('clock')))
                if ident in raw_unique:check(identifier+path+':same_site_tick',raw_unique[ident]==stamp)
                else:raw_unique[ident]=stamp
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                r=node['receipt'];rid=str(r['id']);entry={k:r.get(k)for k in('id','kind','requested_tick','effective_tick','status','reason','channels')}
                if rid in receipts:check(identifier+path+':receipt_duplicate_identical',receipts[rid]==entry)
                else:receipts[rid]=entry
                if'id'in node:check(identifier+path+':receipt_identity',node['id']==r['id'])
                if'tick'in node:check(identifier+path+':requested_tick',node['tick']==r['requested_tick'])
                if r['status']=='applied':check(identifier+path+':effective_tick',r['effective_tick']==r['requested_tick'])
            if 'formed_native_command'in node and'panel'in node:
                codec={f:(I,v)for f,v in CONTEXTS.items()}if len(node['panel'])==12 else FORM_CODEC
                sign,candidates=pure_z(node,codec);check(identifier+path+':pureZ',sign==node['formed_native_command']);check(identifier+path+':pureZ_candidates',candidates==node['candidates']);readers.append({'id':identifier,'path':path,'kind':'pureZ','choice':sign,'gates':len(node['panel'])})
            if 'choice'in node and'observations'in node:
                origins={(int(o['site'][0])//1)for o in node['observations']}
                origin=(15,45,15)if node.get('origin')==[15,45,15]or {o['site'][1]for o in node['observations']}=={47}else(15,15,15)
                choice,candidates=selector(node,origin);check(identifier+path+':selector',choice==node['choice']);expected_candidates=[c.get('choice')if isinstance(c,dict)else c for c in node['candidates']];check(identifier+path+':selector_candidates',candidates==expected_candidates);readers.append({'id':identifier,'path':path,'kind':'six_gate','choice':choice,'gates':6})
            if node.get('kind')=='APD01_candidate_numeric_operation':
                number=numeric(node);check(identifier+path+':native_numeric_RAW',number==node['numeric_reader']['numeric_result']);numerics.append({'id':identifier,'path':path,'operation':node['operation'],'value':number})
    logs=[json.loads(line)for line in(root/'ADMISIONES.jsonl').read_text(encoding='utf8').splitlines()if line]
    check('admission_unique_ids',len(logs)==len({r['id']for r in logs}));check('admission_ids_equal_rows',{r['id']for r in logs}==set(rows))
    for row in logs:check(row['id']+':queued_once',row['admission']['admission']=='queued'and json.loads(rows[row['id']]['payload'])==row['payload'])
    order=[r['id']for r in logs];times=[rows[k]for k in order]
    check('FIFO_nonoverlap',[r['started_utc']for r in times]==sorted(r['started_utc']for r in times))
    for earlier,later in zip(times,times[1:]):check(earlier['id']+':finished_before_next_start',earlier['finished_utc']<=later['started_utc'])
    apd=[];old={};language=[];delta=[];environment=None
    for event in proto['events']:
        identifier=proto['prefix']+event['id'];payload=event['payload'];parsed=json.loads(rows[identifier]['result']);result=parsed['result'];actual=result['rows'];situations=payload['situaciones'];check(identifier+':row_count',len(actual)==len(situations));check(identifier+':frozen_payload',payload==json.loads(rows[identifier]['payload']))
        for slot,(situation,row)in enumerate(zip(situations,actual)):
            key=identifier+':'+str(slot);mode=situation['modo']
            if mode=='memoria':
                trial=row['result']['rows'][0];sign,_=pure_z(trial['reader'],{f:(I,v)for f,v in CONTEXTS.items()});old.setdefault(event['id'],[]).append({'context':situation['contexto'],'choice':sign,'expected_from_declared_history':HISTORY[situation['contexto']],'historical_match':sign==HISTORY[situation['contexto']]})
            elif mode=='apd02-admitir':environment=row['state']['operational_environment']
            elif mode=='apd02-ambiente':check(key+':environment_config',row['after']==situation['configuracion']);environment=row['after']
            elif mode=='apd02-docencia':
                check(key+':teacher_explicit',row['form']==situation['texto']and row['teacher_sign']==situation['senal']);language.append({'kind':'explicit_teacher','form':row['form'],'sign':row['teacher_sign'],'requests':len(row['requests']),'applied':sum(r['receipt']['status']=='applied'for r in row['requests'])})
            elif mode=='apd02-lenguaje':
                sign,_=pure_z(row['word']['reader'],FORM_CODEC);check(key+':function_choice',sign==row['native_function_choice']);check(key+':literal_public',row['literal_form']==situation['texto']and row['public_datum']==situation['valor']and row['operator_supplied_context']==situation['contexto']);interaction=row['interaction'];kind=interaction['kind']if interaction else None
                check(key+':function_follows_native_sign',kind==('native_current_selection'if sign==1 else'query'if sign==-1 else None));language.append({'kind':'use','form':row['literal_form'],'native_function_choice':sign,'interaction_kind':kind,'interaction_choice':interaction.get('reader',{}).get('choice',interaction.get('reader',{}).get('formed_native_command'))if interaction else None,'supplied_context_P0':situation['contexto'],'prepared_sign_function_mapping':True})
            elif mode=='apd02-acumular':
                values=[]
                for f in row['frames']:
                    value,candidates=delta_read(f);check(key+':delta_frame_value',value==f['reader']['value']);check(key+':delta_frame_candidates',candidates==f['reader']['candidates']);values.append(value)
                check(key+':delta_final_RAW',values[-1]==row['numeric_result']);check(key+':delta_input',row['increment']==situation['valor']and row['delay_periods']==situation.get('demora_periodos',0));check(key+':monotonic_cursor',row['legacy_uses_after']==row['legacy_uses_before']+1)
                if delta:check(key+':recurrence',values[-1]==delta[-1]['result']+situation['valor']);check(key+':cursor_continuity',row['legacy_uses_before']==delta[-1]['legacy_uses_after'])
                delta.append({'increment':situation['valor'],'delay_periods':row['delay_periods'],'result':values[-1],'legacy_uses_before':row['legacy_uses_before'],'legacy_uses_after':row['legacy_uses_after'],'read_tick':row['read_tick'],'gates':2,'maintenance':row['maintenance']})
            elif mode=='apd02':
                receipt=row['committed_effect'];public={'task_id':receipt['task_id'],'text':situation['texto'],'operands':situation['operandos']};check(key+':public_request',row['literal_form']==public['text']and row['raw_operands']==public['operands']);check(key+':environment',row['environment']==environment)
                word,_=pure_z(row['word']['reader'],FORM_CODEC);route,_=selector(row['route']['reader'],(15,45,15))if row['route']else(None,[]);op='add'if word==1 else'sub'if word==-1 else None;proc='native'if route==-1 else'external'if route in(0,1)else None
                check(key+':operation_from_RAW',op==row['selected_operation']==receipt['selected_operation']);check(key+':route_from_RAW',proc==row['selected_procedure']==receipt['selected_procedure']);check(key+':native_command_fields',word==row['native_operator_command']and route==row['native_route_command']);calls=receipt['provider_calls'];check(key+':selected_callback_only',calls=={'native':int(proc=='native'),'external':int(proc=='external')})
                if row['native_numeric']is not None:check(key+':raw_provider_value',numeric(row['native_numeric'])==receipt['raw_provider_response']['value']);check(key+':native_only',proc=='native'and row['external_tool']is None)
                if row['external_tool']is not None:check(key+':external_only',proc=='external'and row['native_numeric']is None);check(key+':external_raw_value',row['external_tool']['value']==receipt['raw_provider_response']['value'])
                index=0 if proc=='native'else 1;check(key+':chosen_cost_delay',receipt['price']==environment['precios'][index]and receipt['delay_ticks']==environment['demora'][index]);fault_delta=1 if environment['fallos'][index]=='wrong_value'else 0;check(key+':declared_numeric_fault_only',receipt.get('used_value')==receipt.get('raw_provider_response',{}).get('value')+fault_delta)
                effect=root/artifact_index['by_slot'][key]['directory'];policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':environment['presupuesto'],'max_delay_ticks':environment['demora_maxima'],'resource_limits_required_for_success':True};quality=q.evaluate_literal_committed(public,receipt,sandbox_root=effect,policy=policy);check(key+':actual_file_quality',content(quality)==content(row['quality']));check(key+':only_category_return',row['feedback_to_participant']==q.actor_feedback(quality,binary=True));check(key+':effect_committed_before_return',row['commit_before_verification']['tick']<=row['after']['tick']);check(key+':factual_callback_scope',receipt['fixture_does_not_advance_DEE']is False)
                returned=row.get('native_consequence');mode=payload.get('retorno','real');check(key+':declared_feedback_mode',row['feedback_mode']==mode)
                if returned:check(key+':quality_to_common_return_only',returned['cost']==(0 if quality['feedback']['category']=='SUCCESS'else 3)and returned['mode']==mode)
                apd.append({'id':identifier,'slot':slot,'text':public['text'],'operands':public['operands'],'operator_from_RAW':op,'route_from_RAW':proc,'native_numeric_before_fault':receipt.get('raw_provider_response',{}).get('value'),'actual_artifact_value':quality['private_audit']['observed_artifact']['value']if quality['private_audit']['observed_artifact']else None,'expected_private_request_value':quality['private_audit']['reference_value'],'quality_category':quality['feedback']['category'],'semantic_correct':quality['axes']['operation_corresponds_to_original_request'],'numeric_correct_original_request':quality['axes']['numeric_correct_for_original_request'],'completed_task':quality['completed_task'],'within_resources':quality['resource_acceptable'],'task_success':quality['task_success'],'feedback_mode':mode,'artifact':artifact_index['by_slot'][key]})
    status=collections.Counter(r['status']for r in receipts.values());quality_counts=collections.Counter(r['quality_category']for r in apd)
    check('initial_exact_frozen_cut',proto['snapshot_sha256']==x['initial']['snapshot_sha256']);check('single_world_identity',x['initial']['life_id']==x['final']['life_id']==x['life']and x['initial']['world_id']==x['final']['world_id']);check('owner_stopped',x['owner_final']['running']is False);check('no_pending_transport',x['pending']==[]);check('no_force',not x.get('forced_own_job_close',False));check('job_zero_after_grace',x['job_before_cleanup']['job_active_processes']==0)
    return{'schema':'DEE.APD02.integrated_main_archived_audit.R01','primary_sha256':sha(primary),'evaluator_sha256':sha(evaluator_path),'issues':issues,'checked':dict(checks),'serialized_RAW_observations':raw_count,'unique_observed_site_ticks':len(raw_unique),'fixed_readers':{'count':len(readers),'details':readers},'native_numeric_readers':numerics,'transport':{'requested':len(logs),'admitted':sum(r['admission']['admission']=='queued'for r in logs),'status_counts':dict(collections.Counter(r['status']for r in rows.values())),'material_requests':sum(not r['is_control']for r in rows.values()),'control_requests':sum(bool(r['is_control'])for r in rows.values()),'ordered_ids':order},'native_inputs':{'unique_requested':len(receipts),'status_counts':dict(status),'receipts':list(sorted(receipts.values(),key=lambda r:r['id']))},'memory_panels':old,'new_language':language,'recirculating_accumulator':{'uses':delta,'count':len(delta),'recurrence_checks_after_first':max(0,len(delta)-1),'inferred_prefix_before_first_not_independently_verified':delta[0]['result']-delta[0]['increment']if delta else None,'initial_history_witness':'Requested separately; not reconstructed from a target or metadata answer in this audit.'},'APD_quality':{'cases':apd,'category_counts':dict(quality_counts),'requested':len(apd),'responded':sum(r['operator_from_RAW']is not None and r['route_from_RAW']is not None for r in apd),'semantic_correct':sum(r['semantic_correct']for r in apd),'numeric_correct_original_request':sum(r['numeric_correct_original_request']is True for r in apd),'valid_completed':sum(r['completed_task']for r in apd),'under_resources_success':sum(r['task_success']for r in apd),'abstention':sum(r['quality_category']=='ABSTENTION'for r in apd),'no_response':sum(r['quality_category']=='NO_RESPONSE'for r in apd)},'continuity':{'initial':x['initial'],'final':x['final'],'new_ticks':x['final']['physical']['tick']-x['initial']['physical']['tick'],'owner_pid':x['owner_initial']['pid'],'idle_ticks_delta':x['owner_final']['idle_ticks']-x['owner_initial']['idle_ticks'],'material_calls_delta':x['owner_final']['material_calls']-x['owner_initial']['material_calls'],'enabled_seconds':x['enabled_seconds'],'not_a_60minute_test':True},'scope':'Archived computational audit only: complete serialized request/receipt records and all RAW observations are decoded, fixed readers reconstructed, real exported JSON artifacts reread and quality independently recomputed against the original public request. No Runtime, native ticks, alternate action, replay, answer returned to DEE, or historical full-snapshot identity inference. P0 assistance, exposed history and one genealogy are not independent replications. R03 provider gap is preserved: no observed postwrite failure in this executed chain; prospective R04 is separate.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--evaluador',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();result=calculate(a.evidencia,a.evaluador)
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':result['issues'],'RAW':result['serialized_RAW_observations'],'native_inputs':result['native_inputs']['unique_requested'],'transport':result['transport']['requested'],'APD':result['APD_quality']['category_counts'],'ticks':0}));raise SystemExit(bool(result['issues']))
