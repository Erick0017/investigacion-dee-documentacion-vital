"""Recompute the closed quality/composition window, with no DEE/provider execution.

Original literal requests, acquired operator, native route, actual number,
real file and resource law are separate axes. References never reach DEE.
"""
import argparse,collections,hashlib,importlib.util,json
from pathlib import Path

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
u=load('archived_raw_util',Path(__file__).with_name('recalcular_cadena_main_apd02.py'))
r4=load('fixed_route04_util',Path(__file__).with_name('recalcular_ruta04_main_apd02.py'))
effect=load('post_action_audit',Path(__file__).with_name('auditar_efecto_apd02.py'))

def calculate(root,evaluator,route_source):
    x=u.read(root/'REGISTROS_VENTANA.json.gz');proto=u.read(root/'PROTOCOLO.json');index=u.read(root/'ARTEFACTOS.json');origin=r4.origin_from_source(route_source);quality=load('private_post_effect_quality',evaluator)
    issues=[];checks=0;raw_count=0;seen={};receipts={};statuses=collections.defaultdict(set);readers=[];native_numbers=[]
    def check(name,value):
        nonlocal checks
        checks+=1
        if not value:issues.append(name)
    terminal=lambda s:s not in('scheduled','pending')
    transports={k:v for k,v in x['records'].items()if not k.endswith('_parsed')}
    for identifier,t in transports.items():
        parsed=json.loads(t['result']);check(identifier+':completed',t['status']=='completed');check(identifier+':sameID',parsed['id']==identifier);check(identifier+':payloadSHA',hashlib.sha256(t['payload'].encode()).hexdigest()==t['payload_sha'])
        if identifier+'_parsed'in x['records']:check(identifier+':parsed_mirror',parsed==x['records'][identifier+'_parsed'])
        guard=parsed.get('result',{}).get('INSTRUMENTO_FENCE')
        if guard:check(identifier+':truthful_audit_hook',not guard['denied']and guard.get('operational_history_reads_universally_blocked')is False)
        for path,node in u.walk(parsed):
            if not isinstance(node,dict):continue
            label=identifier+path
            if'raw'in node and'site'in node and'tick'in node:
                raw_count+=1;d=u.decoded(node)
                for key,value in d.items():
                    if key in node:check(label+':'+key,node[key]==value)
                key=(tuple(node['site']),node['tick']);stamp=(str(node['raw']),str(node.get('clock')))
                if key in seen:check(label+':same_site_tick',seen[key]==stamp)
                else:seen[key]=stamp
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                rc=node['receipt'];rid=str(rc['id']);entry={k:rc.get(k)for k in('id','kind','channels','requested_tick','status','effective_tick','reason')};statuses[rid].add(rc['status'])
                if rid in receipts:
                    old=receipts[rid];check(label+':same_receipt_identity',all(old[k]==entry[k]for k in('id','kind','channels','requested_tick')))
                    if terminal(old['status'])and terminal(entry['status']):check(label+':same_terminal_receipt',old==entry)
                    elif terminal(entry['status']):receipts[rid]=entry
                else:receipts[rid]=entry
            if'formed_native_command'in node and'panel'in node:
                codec={f:(u.I,v)for f,v in u.CONTEXTS.items()}if len(node['panel'])==12 else u.FORM_CODEC
                answer,cs=u.pure_z(node,codec);check(label+':fixed_word_or_memory_reader',answer==node['formed_native_command']and cs==node['candidates']);readers.append({'id':identifier,'path':path,'gate_count':len(node['panel']),'choice':answer})
            if'choice'in node and'observations'in node:
                answer,cs=r4.choice3(node,origin)if len(node['observations'])==3 else u.selector(node,(15,15,15))
                check(label+':fixed_route_or_current_reader',answer==node['choice']and cs==[v.get('choice')if isinstance(v,dict)else v for v in node['candidates']]);readers.append({'id':identifier,'path':path,'gate_count':len(node['observations']),'choice':answer})
            if node.get('kind')=='APD01_candidate_numeric_operation':
                number=u.numeric(node);check(label+':native_number_from_RAW',number==node['numeric_reader']['numeric_result']);native_numbers.append({'id':identifier,'path':path,'value':number,'operation':node['operation']})
    logs=[json.loads(v)for v in(root/'ADMISIONES.jsonl').read_text(encoding='utf8').splitlines()if v]
    check('unique_transport_ids',len(logs)==len({v['id']for v in logs}));check('all_transport_records',{v['id']for v in logs}==set(transports))
    for item in logs:check(item['id']+':original_admission_and_payload',item['admission']['admission']=='queued'and item['payload']==json.loads(transports[item['id']]['payload']))
    for a,b in zip(logs,logs[1:]):check(a['id']+':FIFO_completed_before_next_start',transports[a['id']]['finished_utc']<=transports[b['id']]['started_utc'])
    apd=[];composition=[];memory=[];teachers=[];raw128=[];environment=None;expected_history={f:1 if f in('suma','agrega','total')else-1 for f in('suma','diferencia','agrega','resta','total','quita')}
    def audit_one(row,s,label,event,kind):
        item=index['by_node'][label];receipt=row['committed_effect'];public={'task_id':receipt['task_id'],'text':s['texto'],'operands':s['operandos']}
        folder=root/item['directory']if receipt['artifact']else root
        result=effect.audit_effect(row,public,folder,quality=quality,raw_util=u,route_util=r4,origin=origin)
        for name,ok in result['checks'].items():check(label+':'+name,ok)
        check(label+':environment_is_frozen_current',row['environment']==environment);check(label+':feedback_mode',row['feedback_mode']==event['payload'].get('retorno','real'))
        result={k:v for k,v in result.items()if k not in('checks','issues')};result.update({'node':label,'event':event['id'],'opportunity_kind':kind,'artifact_binding':item,'expected_sign_from_explicit_teaching_history':expected_history[s['texto']],'actual_sign_matches_teaching_history':result['word_sign']==expected_history[s['texto']],'teaching_history_is_not_itself_acquisition_proof':True})
        apd.append(result);return result
    for event in proto['events']:
        identifier=proto['prefix']+event['id'];parsed=json.loads(transports[identifier]['result']);rows=parsed['result']['rows'];situations=event['payload']['situaciones'];check(identifier+':frozen_payload',json.loads(transports[identifier]['payload'])==event['payload']);check(identifier+':row_count',len(rows)==len(situations))
        for slot,(s,row)in enumerate(zip(situations,rows)):
            label=identifier+':'+str(slot);mode=s['modo']
            if mode=='apd02-ambiente':environment=row['after'];check(label+':fixed_environment',environment==s['configuracion'])
            elif mode=='apd-docencia':
                check(label+':explicit_teacher_not_implicit_repair',row['form']==s['texto']and row['teacher_sign']==s['senal']and s['revision']is True)
                req=row['requests'];admitted=all(r['receipt']['status']=='applied'for r in req)
                if admitted:expected_history[s['texto']]=s['senal']
                teachers.append({'event':event['id'],'literal':s['texto'],'requested_sign':s['senal'],'requested':len(req),'applied':sum(r['receipt']['status']=='applied'for r in req),'all_applied':admitted,'acquisition_not_assumed_from_admission':True,'hub_RAW':row['hub'],'scope':'External explicit opposite teaching/restoration, not autonomous recovery or retention without reteaching.'})
            elif mode=='apd02':audit_one(row,s,label,event,'direct')
            elif mode=='apd02-componer':
                value=s['datos'][0];actual=row['rows'];stages=[];check(label+':not_more_stages_than_supplied',len(actual)<=len(s['formas']))
                for j,step in enumerate(actual):
                    check(label+':intermediate_is_actual_previous_output',type(value)is int and 0<=value<=32)
                    stage=audit_one(step,{'texto':s['formas'][j],'operandos':[value,s['datos'][j+1]]},label+':stage:'+str(j),event,'assisted_composition_stage');stages.append(stage['node'])
                    expected_instruction={'actual_operation':stage['selected_operation'],'actual_procedure':stage['selected_procedure'],'data_source':'actual_previous_output_and_next_literal_operand'}
                    check(label+':instruction_'+str(j),row['actual_instructions'][j]==expected_instruction)
                    if not step['quality']['task_success']:
                        check(label+':failed_stage_stops_without_substitute',j==len(actual)-1);value=None;break
                    value=step['committed_effect'].get('used_value')
                    if type(value)is not int or not 0<=value<=32:
                        check(label+':out_of_domain_stops',j==len(actual)-1);value=None;break
                complete=len(actual)==len(s['formas'])and all(step['quality']['task_success']for step in actual)and value is not None
                check(label+':actual_result_no_host_solver',row['result']==(value if complete else None));check(label+':instruction_count',len(row['actual_instructions'])==len(actual))
                composition.append({'event':event['id'],'operator_supplied_forms':s['formas'],'literal_data':s['datos'],'requested_stages':len(s['formas']),'executed_stages':len(actual),'stage_nodes':stages,'complete_verified_effects':complete,'actual_result':row['result'],'scope':'Order supplied externally; intermediate operands are unchanged actual preceding effects. No learned planner/grammar/tool invention.'})
            elif mode=='memoria':
                trial=row['result']['rows'][0];sg,_=u.pure_z(trial['reader'],{f:(u.I,v)for f,v in u.CONTEXTS.items()});memory.append({'event':event['id'],'context':s['contexto'],'choice':sg,'expected_declared_history':u.HISTORY[s['contexto']],'match':sg==u.HISTORY[s['contexto']]})
            elif mode=='crudos':
                components=s['componentes'];check(label+':literal128_no_host_aggregation',len(components)==128 and row['raw_components']==components and row['level']==128)
                frame=[f for f in row['frames']if f['tick']==row['datum_tick']-2]
                check(label+':single_prequery_aggregate_frame',len(frame)==1)
                c=frame[0]['fields']['C'];decoded=u.decoded(c);aggregate=decoded['s_reg']if decoded['active']and decoded['semantic']==1 and decoded['direction']==[1,-1,-1]else None
                check(label+':prepared_C_site',c['site']==[12,17,18]);check(label+':physical_aggregate_matches_auditor_sum',aggregate==sum(components))
                expected_ports={'MU.raw.L128.'+side+'.root.'+str(a)+'.'+str(b)+'.raw.'+str(c)for side in('left','right')for a in range(4)for b in range(4)for c in range(4)}
                raw_inputs=[r for r in row['requests']if r['port']in expected_ports];check(label+':128_inputs_all_same_material_tick',len(raw_inputs)==128 and{r['port']for r in raw_inputs}==expected_ports and all(r['tick']==row['input_tick']and r['receipt']['status']=='applied'for r in raw_inputs))
                component_by_port={'MU.raw.L128.'+side+'.root.'+str(a)+'.'+str(b)+'.raw.'+str(c):2*(16*a+4*b+c)+parity for parity,side in enumerate(('left','right'))for a in range(4)for b in range(4)for c in range(4)}
                check(label+':128_literal_values_not_preaggregated',all(r['payload']==components[component_by_port[r['port']]]for r in raw_inputs))
                choice=u.selector(row['reader'],(15,15,15))[0];raw128.append({'event':event['id'],'visible_components':components,'native_C_RAW':c,'native_aggregate':aggregate,'external_auditor_sum_only':sum(components),'native_choice':choice,'native_input_requests':len(row['requests']),'all_applied':all(r['receipt']['status']=='applied'for r in row['requests']),'scope':'Raw128 aggregation is a prepared native transducer and comparator, not an APD file, acquired arithmetic policy or resource counter.'})
            else:check(label+':known_mode',False)
    direct=[r for r in apd if r['opportunity_kind']=='direct'];final=[r for r in direct if r['event']=='old_apd6_no_feedback']
    def counts(rows):return{'opportunities':len(rows),'operator_emissions':sum(r['word_sign']in(-1,1)for r in rows),'route_emissions':sum(r['route_choice']is not None for r in rows),'provider_calls':sum(sum(r['provider_calls'].values())for r in rows),'semantic_correct':sum(r['semantic_correct']for r in rows),'provider_number_correct_original_request':sum(r['numeric_provider_correct_for_original_request']for r in rows),'artifact_number_correct_original_request':sum(r['numeric_artifact_correct_for_original_request']is True for r in rows),'valid_real_files':sum(r['real_artifact_valid']for r in rows),'completed_tasks':sum(r['valid_completed_task']for r in rows),'success_under_resource_limits':sum(r['task_success_under_limits']for r in rows),'categories':dict(collections.Counter(r['category']for r in rows))}
    check('exact_declared_parent',x['initial']['snapshot_sha256']==proto['snapshot_sha256']);check('native_receipts_terminal_not_pending',all(terminal(r['status'])for r in receipts.values()));check('stopped_no_forced_cleanup',not x['owner_final']['running']and x['pending']==[]and x['job_before_cleanup']['job_active_processes']==0 and not x.get('forced_own_job_close',False));check('one_runtime_load',x['owner_final']['runtime_loads_in_this_process']==1 and x['owner_initial']['pid']==x['owner_final']['pid']);check('frozen_sources_unchanged',x['sources_unchanged']is True)
    return{'schema':'DEE.APD02.quality_composition_archived.R01','issues':issues,'checks':checks,'RAW_serialized_observations':raw_count,'unique_observed_site_ticks':len(seen),'fixed_readers':readers,'native_numeric_readers':native_numbers,'primary_sha256':u.sha(root/'REGISTROS_VENTANA.json.gz'),'frozen_route_source_sha256':u.sha(route_source),'quality_source_sha256':u.sha(evaluator),'transport':{'requested':len(logs),'admitted':sum(l['admission']['admission']=='queued'for l in logs),'completed':sum(t['status']=='completed'for t in transports.values()),'material':sum(not t['is_control']for t in transports.values()),'controls':sum(bool(t['is_control'])for t in transports.values())},'native_inputs':{'unique_requested':len(receipts),'terminal_status_counts':dict(collections.Counter(r['status']for r in receipts.values())),'serialized_status_sets':dict(collections.Counter(','.join(sorted(v))for v in statuses.values())),'receipts':sorted(receipts.values(),key=lambda r:r['id'])},'APD_primitives':{'all':counts(apd),'direct_only':counts(direct),'final_old6':counts(final),'cases':apd},'explicit_teaching':teachers,'assisted_composition':composition,'old_memory6':memory,'raw128':raw128,'continuity':{'initial':x['initial'],'final':x['final'],'enabled_seconds':x['enabled_seconds'],'not_a60minute_test':True,'idle_delta':x['owner_final']['idle_ticks']-x['owner_initial']['idle_ticks'],'material_calls_delta':x['owner_final']['material_calls']-x['owner_initial']['material_calls'],'owner_stopped':not x['owner_final']['running'],'pending_transport':x['pending']},'scope':'Archived recalculation only, no Runtime/provider callback/new tick/repair. Each actual effect is reread from its exact event and nested-stage directory. Explicit opposite teaching/restoration, category return, native arithmetic, external tool, file effect and resource adequacy retain distinct attribution. This single continuing life is not an independent control, autonomous planner or general policy claim.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--evaluador',type=Path,required=True);p.add_argument('--fuente-ruta',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();out=calculate(a.evidencia,a.evaluador,a.fuente_ruta)
    with a.salida.open('x',encoding='utf8')as f:json.dump(out,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':out['issues'],'checks':out['checks'],'RAW':out['RAW_serialized_observations'],'APD':out['APD_primitives']['all'],'native_ticks':0}));raise SystemExit(bool(out['issues']))
