"""Archived R03 three-gate routing failure; no Runtime or physics replay."""
import argparse,array,collections,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
from recalcular_cadena_main_apd02 import read,sha,walk,decoded,pure_z,selector,delta_read,FORM_CODEC,CONTEXTS,HISTORY,I,pos,content

def choice3(reader,origin):
    expected={tuple((origin[j]+off[j])%67 for j in range(3)):sign for sign in(-1,0,1)for off in[(2*sign,2,0)]};observations=reader['observations']
    if len(observations)!=3 or {tuple(o['site'])for o in observations}!=set(expected):raise ValueError('Frozen complete three-gate set differs')
    cs=[]
    for o in observations:
        d=decoded(o);sg=expected[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==[sg,1,0]:cs.append(sg)
    return cs[0]if len(cs)==1 else None,cs
def arrays(frame):
    n=frame['N'];raw=array.array('Q',[0])*(n**3);clock=array.array('Q',[int(frame['clock_default'])])*(n**3)
    for i,value in frame['raw_nonzero']:raw[i]=int(value)
    for i,value in frame['clock_exceptions']:clock[i]=int(value)
    def digest(values):
        if sys.byteorder!='little':values=array.array('Q',values);values.byteswap()
        return hashlib.sha256(values.tobytes()).hexdigest()
    if digest(raw)!=frame['RAW_sha256']or digest(clock)!=frame['clocks_sha256']:raise ValueError('Sparse full-field reconstruction SHA mismatch')
    return raw,clock
def calculate(root,evaluator):
    x=read(root/'REGISTROS_VENTANA.json.gz');proto=read(root/'PROTOCOLO.json');snap=read(root/'PROYECCION_SNAPSHOTS.json.gz');hist=read(root/'HISTORIA_MAIN_CADENA_R01.json.gz');index=read(root/'ARTEFACTOS.json')
    spec=importlib.util.spec_from_file_location('private_quality_after_terminal_effect',evaluator);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
    issues=[];checks=0;observations=0;readers=[];receipt_records={};transitions=collections.Counter();observed_outcomes=collections.defaultdict(set);raw_seen={}
    def check(label,ok):
        nonlocal checks
        checks+=1
        if not ok:issues.append(label)
    def merge(r,label):
        rid=str(r['id']);new={k:r.get(k)for k in('id','kind','requested_tick','channels','status','effective_tick','reason')};observed_outcomes[rid].add(r['status'])
        if rid not in receipt_records:receipt_records[rid]=new;return
        old=receipt_records[rid]
        check(label+':receipt_identity',all(old[k]==new[k]for k in('id','kind','requested_tick','channels')))
        terminal=lambda v:v not in('pending','scheduled')
        if terminal(old['status'])and terminal(new['status']):check(label+':terminal_outcome_consistent',old==new)
        elif terminal(new['status']):receipt_records[rid]=new;transitions[old['status']+'->'+new['status']]+=1
    transports={k:v for k,v in x['records'].items()if not k.endswith('_parsed')}
    for identifier,transport in transports.items():
        parsed=json.loads(transport['result']);check(identifier+':completed',transport['status']=='completed');check(identifier+':id',parsed['id']==identifier);check(identifier+':payload_sha',hashlib.sha256(transport['payload'].encode()).hexdigest()==transport['payload_sha'])
        if identifier+'_parsed'in x['records']:check(identifier+':mirror',x['records'][identifier+'_parsed']==parsed)
        for path,node in walk(parsed):
            if not isinstance(node,dict):continue
            label=identifier+path
            if 'raw'in node and'site'in node and'tick'in node:
                observations+=1;d=decoded(node)
                for k,v in d.items():
                    if k in node:check(label+':'+k,node[k]==v)
                key=(tuple(node['site']),int(node['tick']));stamp=(str(node['raw']),str(node.get('clock')))
                if key in raw_seen:check(label+':same_site_tick',raw_seen[key]==stamp)
                else:raw_seen[key]=stamp
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                merge(node['receipt'],label)
                if'id'in node:check(label+':id_matches_receipt',node['id']==node['receipt']['id'])
                if'tick'in node:check(label+':requested_tick',node['tick']==node['receipt']['requested_tick'])
            if 'formed_native_command'in node and'panel'in node:
                codec={f:(I,v)for f,v in CONTEXTS.items()}if len(node['panel'])==12 else FORM_CODEC
                answer,cs=pure_z(node,codec);check(label+':common_pureZ',answer==node['formed_native_command']and cs==node['candidates']);readers.append({'id':identifier,'path':path,'kind':'common_pureZ','gates':len(node['panel']),'choice':answer})
            if 'choice'in node and'observations'in node:
                answer,cs=choice3(node,(45,15,45))if len(node['observations'])==3 else selector(node,(15,15,15));recorded=[c.get('choice')if isinstance(c,dict)else c for c in node['candidates']];check(label+':fixed_selector',answer==node['choice']and cs==recorded);readers.append({'id':identifier,'path':path,'kind':'three_gate'if len(node['observations'])==3 else'six_gate','gates':len(node['observations']),'choice':answer})
    logs=[json.loads(line)for line in(root/'ADMISIONES.jsonl').read_text(encoding='utf8').splitlines()if line];check('unique_transport_ids',len(logs)==len({r['id']for r in logs}));check('all_requested_transport_present',{r['id']for r in logs}==set(transports))
    for log in logs:check(log['id']+':queued_payload',log['admission']['admission']=='queued'and json.loads(transports[log['id']]['payload'])==log['payload'])
    ordered=[transports[r['id']]for r in logs]
    for previous,nextrow in zip(ordered,ordered[1:]):check(previous['id']+':FIFO',previous['finished_utc']<=nextrow['started_utc'])
    apd=[];memory={};language=[];deltas=[];preparation=None;env=None
    for event in proto['events']:
        identifier=proto['prefix']+event['id'];parsed=json.loads(transports[identifier]['result']);rows=parsed['result']['rows'];situations=event['payload']['situaciones'];check(identifier+':payload',event['payload']==json.loads(transports[identifier]['payload']));check(identifier+':row_count',len(rows)==len(situations))
        for slot,(s,row)in enumerate(zip(situations,rows)):
            label=identifier+':'+str(slot);mode=s['modo']
            if mode=='apd02-ruta-admitir':preparation=row['preparation']
            elif mode=='apd02-ambiente':env=row['after'];check(label+':environment',env==s['configuracion'])
            elif mode=='memoria':
                trial=row['result']['rows'][0];answer,_=pure_z(trial['reader'],{f:(I,v)for f,v in CONTEXTS.items()});memory.setdefault(event['id'],[]).append({'context':s['contexto'],'answer':answer,'expected_declared_history':HISTORY[s['contexto']],'match':answer==HISTORY[s['contexto']]})
            elif mode=='apd02-lenguaje':
                answer,_=pure_z(row['word']['reader'],FORM_CODEC);interaction=row['interaction'];check(label+':function',answer==row['native_function_choice']and interaction['kind']==('native_current_selection'if answer==1 else'query'))
                result=selector(interaction['reader'],(15,15,15))[0]if answer==1 else pure_z(interaction['reader'],{f:(I,v)for f,v in CONTEXTS.items()})[0];language.append({'form':s['texto'],'datum':s['valor'],'explicit_context_P0':s['contexto'],'native_function_choice':answer,'native_interaction_choice':result,'interaction_kind':interaction['kind']})
            elif mode=='apd02-acumular':
                value=None
                for frame in row['frames']:
                    value,cs=delta_read(frame);check(label+':delta_RAW',value==frame['reader']['value']and cs==frame['reader']['candidates'])
                check(label+':delta_result',value==row['numeric_result']);deltas.append({'increment':row['increment'],'result':value,'uses_before':row['legacy_uses_before'],'uses_after':row['legacy_uses_after'],'delay_periods':row['delay_periods'],'read_tick':row['read_tick']})
            elif mode=='apd02':
                word,_=pure_z(row['word']['reader'],FORM_CODEC);route,_=choice3(row['route']['reader'],(45,15,45));op='add'if word==1 else'sub'if word==-1 else None;proc='native'if route==-1 else'external'if route in(0,1)else None;receipt=row['committed_effect'];public={'task_id':receipt['task_id'],'text':s['texto'],'operands':s['operandos']};check(label+':physical_choices',op==row['selected_operation']==receipt['selected_operation']and proc==row['selected_procedure']==receipt['selected_procedure']);check(label+':public_request',row['literal_form']==s['texto']and row['raw_operands']==s['operandos']);check(label+':environment',env==row['environment'])
                check(label+':not_executed_without_route',proc is None and receipt['provider_calls']=={'native':0,'external':0}and row['native_numeric']is None and row['external_tool']is None and receipt['artifact']is None and receipt['state']=='no_output');check(label+':no_actual_artifact',not index['by_slot'][label]['copied_actual_file'])
                policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':env['presupuesto'],'max_delay_ticks':env['demora_maxima'],'resource_limits_required_for_success':True};quality=q.evaluate_literal_committed(public,receipt,sandbox_root=root,policy=policy);check(label+':quality',content(quality)==content(row['quality']));check(label+':category_only',q.actor_feedback(quality,binary=True)==row['feedback_to_participant'])
                consequence=row['native_consequence'];check(label+':common_consequence_not_correct_route',consequence['category']==row['feedback_to_participant']['category']and consequence['no_action_or_correct_route_argument']is True);check(label+':complete_trace_window',len(consequence['frames'])==19 and consequence['frames'][-1]['tick']==consequence['boundary']+15)
                opdeps=parsed['committed_snapshot']['operational_dependencies'];check(label+':external_pending_not_inferred_from_transport',not opdeps['external_uncertain_present']and not opdeps['cascade_pending_present']and not opdeps['external_pending_present'])
                apd.append({'id':identifier,'literal':s['texto'],'operands':s['operandos'],'word_sign':word,'operator':op,'route':route,'quality':quality['feedback']['category'],'semantic_correct_for_original_request':quality['axes']['operation_corresponds_to_original_request'],'numeric_correct_original_request':quality['axes']['numeric_correct_for_original_request'],'provider_calls':receipt['provider_calls'],'native_arithmetic_executed':False,'artifact_completed':quality['completed_task'],'native_route_reader_tick':row['route']['reader']['tick']})
    check('all_recorded_native_requests_resolved',all(r['status']not in('scheduled','pending')for r in receipt_records.values()))
    fields={name:arrays(frame)for name,frame in snap['snapshots'].items()};source=snap['snapshots']['INITIAL'];final=snap['snapshots']['FINAL'];check('initial_full_snapshot_provenance',source['snapshot_sha256']==x['initial']['snapshot_sha256']);check('final_full_snapshot_provenance',final['snapshot_sha256']==x['final']['snapshot_sha256']);check('no_native_pending_in_final_snapshot',final['native_pending']==[]);check('native_trace_closed_in_final_snapshot',final['selected_metadata']['route']['pending_window']is None)
    collision=[47,19,45];cell=(collision[0]*67+collision[1])*67+collision[2];raw=int(fields['INITIAL'][0][cell]);d=decoded({'raw':raw});check('blocker_is_inactive_sem4_not_empty',d['state']==0 and d['semantic']==4 and raw!=0)
    hp=hist['records']['apd02m1_admitir_parsed']['result']['rows'][0]['language_preparation'];witnesses=[r for r in hp['rows']if r['site']==collision];check('prior_prepared_terminator_provenance',len(witnesses)==1 and int(witnesses[0]['post']['raw'])==raw and witnesses[0]['form']=='recuerda')
    covered={tuple(r['site'])for r in preparation['pre']+preparation['loop_pre']};check('all_checked_geometry_and_loop_were_RAW0',all(int(o['raw'])==0 for o in preparation['pre']+preparation['loop_pre']));check('blocked_injection_site_was_omitted_from_preflight',tuple(collision)not in covered)
    final_ports=final['selected_channels'];port='APD02.trace.R03.support.minus';check('declared_query_support_hits_same_site',final_ports[port]['site']==collision)
    bad=[r for r in receipt_records.values()if port in(r['channels']or[])];check('all_twelve_support_minus_rejected_occupied',len(bad)==12 and all(r['status']=='rejected_occupied'and r['effective_tick']is None for r in bad));first=min(bad,key=lambda r:r['requested_tick'])
    check('FIFO_owner_stopped',not x['owner_final']['running']and x['pending']==[]and not x.get('forced_own_job_close',False)and x['job_before_cleanup']['job_active_processes']==0)
    return{'schema':'DEE.APD02.route_ABAB_archived_R03.R02','issues':issues,'checks':checks,'serialized_RAW_observations':observations,'unique_observed_site_ticks':len(raw_seen),'whole_field_uint64_checked':2*67**3*2,'source_primary_sha256':sha(root/'REGISTROS_VENTANA.json.gz'),'evaluator_sha256':sha(evaluator),'transport':{'requested':len(logs),'admitted':sum(l['admission']['admission']=='queued'for l in logs),'completed':sum(t['status']=='completed'for t in transports.values()),'material':sum(not t['is_control']for t in transports.values()),'controls':sum(bool(t['is_control'])for t in transports.values())},'native_inputs':{'unique_requested':len(receipt_records),'final_status_counts':dict(collections.Counter(r['status']for r in receipt_records.values())),'recorded_resolution_transitions':dict(transitions),'all_receipts':sorted(receipt_records.values(),key=lambda r:r['id']),'pending_final_snapshot':final['native_pending']},'readers':readers,'APD':{'requested':len(apd),'operator_emissions':sum(r['word_sign']in(-1,1)for r in apd),'route_emissions':sum(r['route']is not None for r in apd),'native_or_external_executed':0,'correct_numeric':0,'wrong_numeric':0,'numeric_not_executed_or_indeterminate':len(apd),'NO_RESPONSE':sum(r['quality']=='NO_RESPONSE'for r in apd),'cases':apd},'memory':memory,'new_functions':language,'accumulator_after':deltas,'blocker':{'initial_observation':{'site':collision,'tick':source['tick'],'raw':str(raw),'clock':str(fields['INITIAL'][1][cell]),**d},'prior_lexical_preparation_row':witnesses[0],'prior_preparation_primary_sha256':sha(root/'HISTORIA_MAIN_CADENA_R01.json.gz'),'coordinate_identity':'H(47,17,47)+2*(0,1,0)+(0,0,-2) = routeO(45,15,45)+(2,4,0)','in_preflight_geometry_or_loop':tuple(collision)in covered,'declared_support_channel':final_ports[port],'first_rejected_receipt':first,'rejected_supports':bad,'scope':'Exact prepared-site overlap and rejected RAW-empty admission are demonstrated. No intervention isolating this single site was executed in this audit, so it is a demonstrated blocked prerequisite, not proof that fixing it alone suffices or that all twelve failed outputs have only one cause.'},'continuity':{'initial':x['initial'],'final':x['final'],'enabled_seconds':x['enabled_seconds'],'not_60_minutes':True,'owner_pid':x['owner_initial']['pid'],'idle_ticks_delta':x['owner_final']['idle_ticks']-x['owner_initial']['idle_ticks'],'clean_own_job':x['job_before_cleanup']['job_active_processes']==0},'scope':'Read-only archived recalc, no native import or new ticks. Three gates are R03, six gates are the unchanged current-comparator. Scheduled receipt copies are merged only into matching terminal identities, never counted as final pending or new admissions. Full sparse RAW+clock vectors are reconstructed against their SHA; complete snapshot metadata/receipts remain local. Twelve no-route outcomes are not twelve wrong arithmetic answers or an empirical limit on an otherwise admitted learning policy. P0 overlap and adverse future remain preserved.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--evaluador',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia,a.evaluador)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':r['issues'],'RAW':r['serialized_RAW_observations'],'whole_fields':r['whole_field_uint64_checked'],'native_inputs':r['native_inputs']['final_status_counts'],'APD':{k:v for k,v in r['APD'].items()if k!='cases'},'native_ticks':0}));raise SystemExit(bool(r['issues']))
