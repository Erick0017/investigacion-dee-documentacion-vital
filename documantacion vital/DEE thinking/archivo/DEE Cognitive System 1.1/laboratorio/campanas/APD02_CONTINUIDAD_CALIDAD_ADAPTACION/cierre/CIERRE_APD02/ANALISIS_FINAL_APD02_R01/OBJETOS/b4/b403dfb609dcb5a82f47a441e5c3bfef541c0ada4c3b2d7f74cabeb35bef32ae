"""Prospective closed-reserve functional audit; references remain external/private."""
import argparse,collections,importlib.util,json
from pathlib import Path
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=load('archive_window_scan',Path(__file__).with_name('auditar_archivo_ventana_apd02.py'))
u=base.u;r4=base.r4
effect=load('archive_effect_audit_R02',Path(__file__).with_name('auditar_efecto_apd02_r02.py'))
goal=load('archive_goal_audit_R03',Path(__file__).with_name('auditar_evento_objetivo_apd02_r03.py'))
def calculate(root,evaluator,route_source):
    origin=r4.origin_from_source(route_source);s=base.scan(root,origin);x=s['x'];proto=s['proto'];index=u.read(root/'ARTEFACTOS.json');quality=load('private_committed_quality',evaluator)
    issues=list(s['issues']);checks=s['checks'];apd=[];memories=[];language=[];teachers=[];acc=[];raw128=[];goals=[];compositions=[];incomplete=[];environment=None
    memory_expected=dict(u.HISTORY);function_expected={'compara':1,'recuerda':-1}
    def check(name,ok):
        nonlocal checks
        checks+=1
        if not ok:issues.append(name)
    def one_effect(row,public,label,event,kind):
        receipt=row['committed_effect'];item=index['by_node'][label];folder=root/item['directory']if receipt['artifact']else root
        if receipt['state']=='uncertain':
            check(label+':uncertain_no_feedback_or_quality',row.get('quality')is None and row.get('feedback_to_participant')is None)
            result={'node':label,'event':event['id'],'opportunity_kind':kind,'state':'uncertain','no_success_imputed':True};apd.append(result);return result
        verified=effect.audit_effect(row,public,folder,quality=quality,raw_util=u,route_util=r4,origin=origin)
        for name,ok in verified['checks'].items():check(label+':'+name,ok)
        check(label+':exact_current_environment',row['environment']==environment);check(label+':frozen_return_mode',row['feedback_mode']==event['payload'].get('retorno','real'))
        result={k:v for k,v in verified.items()if k not in('checks','issues')};result.update({'node':label,'event':event['id'],'opportunity_kind':kind,'artifact_binding':item,'environment':row['environment'],'feedback_mode':row['feedback_mode']});apd.append(result);return result
    for event in proto['events']:
        identifier=proto['prefix']+event['id'];parsed=s['parsed'].get(identifier);transport=s['transports'].get(identifier)
        if parsed is None or transport['status']!='completed':
            incomplete.append({'event':event['id'],'planned_at_seconds':event['at_seconds'],'transport':None if transport is None else transport['status'],'requested_payload':event['payload'],'no_execution_or_correctness_imputed':True});continue
        rows=parsed.get('result',{}).get('rows',[]);situations=event['payload']['situaciones'];check(identifier+':frozen_payload',json.loads(transport['payload'])==event['payload']);check(identifier+':row_count',len(rows)==len(situations))
        for slot,(request,row)in enumerate(zip(situations,rows)):
            label=identifier+':'+str(slot);mode=request['modo']
            if mode=='apd02-ambiente':
                environment=row['after'];check(label+':frozen_environment',environment==request['configuracion'])
            elif mode=='apd02':
                one_effect(row,{'task_id':row['committed_effect']['task_id'],'text':request['texto'],'operands':request['operandos']},label,event,'direct')
            elif mode=='apd02-docencia':
                check(label+':explicit_lexical_lesson',row['form']==request['texto']and row['teacher_sign']==request['senal']and row['lesson_is_external']is True)
                req=row['requests'];all_applied=all(r['receipt']['status']=='applied'for r in req)
                function_expected[request['texto']]=request['senal']if all_applied else None
                teachers.append({'event':event['id'],'domain':'new_function_word','literal':request['texto'],'requested_sign':request['senal'],'requested':len(req),'applied':sum(r['receipt']['status']=='applied'for r in req),'all_applied':all_applied,'native_hub_observation':row['hub'],'acquisition_not_assumed_from_admission':True,'explicit_teacher_is_not_autonomous_revision':True})
            elif mode=='memoria':
                trial=row['result']['rows'][0]
                if request.get('operacion_memoria')in('revisar','ensenar'):
                    check(label+':explicit_memory_revision',trial['context_signal']==request['contexto']and trial['teaching_signal']==request['senal'])
                    req=trial['requests'];all_applied=all(r['receipt']['status']=='applied'for r in req);prior=memory_expected[request['contexto']];memory_expected[request['contexto']]=request['senal']if all_applied else None
                    teachers.append({'event':event['id'],'domain':'memory_context','context':request['contexto'],'historical_expected_before':prior,'requested_sign':request['senal'],'requested':len(req),'applied':sum(r['receipt']['status']=='applied'for r in req),'all_applied':all_applied,'native_hub_observation':trial['hub'],'new_reference_not_old_retention':True,'acquisition_not_assumed_from_admission':True})
                else:
                    answer,_=u.pure_z(trial['reader'],{f:(u.I,v)for f,v in u.CONTEXTS.items()});context=request['contexto'];expected=memory_expected[context]
                    memories.append({'event':event['id'],'context':context,'choice':answer,'expected_from_explicit_history':expected,'match':None if expected is None else answer==expected,'historical_retention_without_new_teacher':context!='beta' or event['at_seconds']<1560,'beta_revision_not_old_retention':context=='beta'and event['at_seconds']>1560,'mode':event['payload'].get('retorno','real')})
            elif mode=='apd02-lenguaje':
                answer,_=u.pure_z(row['word']['reader'],u.FORM_CODEC);interaction=row['interaction'];check(label+':fixed_function_codec',row['native_function_choice']==answer and((answer==1 and interaction['kind']=='native_current_selection')or(answer==-1 and interaction['kind']=='query')or(answer is None and interaction is None)))
                actual=None
                if interaction is not None:actual=u.selector(interaction['reader'],(15,15,15))[0]if answer==1 else u.pure_z(interaction['reader'],{f:(u.I,v)for f,v in u.CONTEXTS.items()})[0]
                language.append({'event':event['id'],'literal':request['texto'],'raw_datum':request['valor'],'operator_addressed_context':request['contexto'],'native_function_choice':answer,'expected_from_explicit_teaching_history':function_expected[request['texto']],'actual_interaction_choice':actual,'expected_historical_content_if_accessed':memory_expected[request['contexto']]if answer==-1 else None,'matches_history_if_accessed':actual==memory_expected[request['contexto']]if answer==-1 and memory_expected[request['contexto']]is not None else None,'scope':'Acquired cue chooses prepared current comparison or historical access. Context addressing remains external P0; explicit revision/restoration is not autonomous repair.'})
            elif mode=='apd02-acumular':
                frame_values=[]
                for frame in row['frames']:
                    value,cs=u.delta_read(frame);check(label+':delta_fixed_RAW',value==frame['reader']['value']and cs==frame['reader']['candidates']);frame_values.append({'tick':frame['tick'],'value':value})
                check(label+':delta_actual_final',row['numeric_result']==frame_values[-1]['value']);check(label+':delta_literal_delay_increment',row['increment']==request['valor']and row['delay_periods']==request.get('demora_periodos',0));check(label+':delta_use_counter_not_memory',row['legacy_uses_after']==row['legacy_uses_before']+1)
                comparison=None
                if acc:
                    check(label+':same_accumulator_use_sequence',row['legacy_uses_before']==acc[-1]['legacy_uses_after'])
                    comparison={'previous_observed_value':acc[-1]['numeric_result'],'current_increment':request['valor'],'expected_value_from_previous_if_present':acc[-1]['numeric_result']+request['valor']if acc[-1]['numeric_result']is not None else None,'matches_previous_plus_increment':row['numeric_result']==acc[-1]['numeric_result']+request['valor']if acc[-1]['numeric_result']is not None else None,'a_functional_outcome_not_integrity_requirement':True}
                acc.append({'event':event['id'],'increment':row['increment'],'delay_periods':row['delay_periods'],'maintenance':row['maintenance'],'prepared_bank':row['prepared_bank'],'legacy_uses_before':row['legacy_uses_before'],'legacy_uses_after':row['legacy_uses_after'],'numeric_result':row['numeric_result'],'comparison_to_previous_within_reserve':comparison,'RAW_frames':frame_values,'scope':'Physical recirculating value read from RAW. Prepared renewal resources/timing are P0; counters are not reconstructed memory or autonomous maintenance.'})
            elif mode=='crudos':
                components=request['componentes'];check(label+':128_independent_literals',len(components)==128 and row['raw_components']==components and row['level']==128)
                mapping={'MU.raw.L128.'+side+'.root.'+str(a)+'.'+str(b)+'.raw.'+str(c):2*(16*a+4*b+c)+parity for parity,side in enumerate(('left','right'))for a in range(4)for b in range(4)for c in range(4)}
                leaves=[r for r in row['requests']if r['port']in mapping];check(label+':fixed128_leaf_codec',len(leaves)==128 and{r['port']for r in leaves}==set(mapping)and all(r['payload']==components[mapping[r['port']]]and r['tick']==row['input_tick']for r in leaves))
                frames=[f for f in row['frames']if f['tick']==row['datum_tick']-2];check(label+':single_C_frame',len(frames)==1);c=frames[0]['fields']['C'];d=u.decoded(c);aggregate=d['s_reg']if c['site']==[12,17,18]and d['active']and d['semantic']==1 and d['direction']==[1,-1,-1]else None
                raw128.append({'event':event['id'],'literal_components':components,'native_C_RAW':c,'native_aggregate':aggregate,'external_auditor_sum_only':sum(components),'native_aggregate_matches_external_posthoc_sum':aggregate==sum(components),'native_choice':u.selector(row['reader'],(15,15,15))[0],'native_input_requests':len(row['requests']),'applied':sum(r['receipt']['status']=='applied'for r in row['requests']),'scope':'The host sum is calculated only here after the action for audit; the actor transported128 independent raw operands. A wrong/absent aggregate is a functional negative, not silently repaired or an archived-data contradiction.'})
            elif mode=='apd02-componer':
                value=request['datos'][0];stages=[];actual=row['rows'];check(label+':bounded_supplied_sequence',len(actual)<=len(request['formas']))
                for j,step in enumerate(actual):
                    check(label+':actual_intermediate_in_domain',type(value)is int and 0<=value<=32)
                    result=one_effect(step,{'task_id':step['committed_effect']['task_id'],'text':request['formas'][j],'operands':[value,request['datos'][j+1]]},label+':stage:'+str(j),event,'assisted_composition_stage');stages.append(result['node'])
                    instruction={'actual_operation':step['selected_operation'],'actual_procedure':step['selected_procedure'],'data_source':'actual_previous_output_and_next_literal_operand'};check(label+':actual_instruction_'+str(j),row['actual_instructions'][j]==instruction)
                    if not step['quality']['task_success']:
                        check(label+':failed_stage_no_substitute',j==len(actual)-1);value=None;break
                    value=step['committed_effect'].get('used_value')
                    if type(value)is not int or not 0<=value<=32:check(label+':invalid_intermediate_stops',j==len(actual)-1);value=None;break
                completed=len(actual)==len(request['formas'])and value is not None and all(r['quality']['task_success']for r in actual);check(label+':output_is_actual_last_value',row['result']==(value if completed else None))
                compositions.append({'event':event['id'],'operator_supplied_forms':request['formas'],'literal_data':request['datos'],'requested_stages':len(request['formas']),'archived_executed_stages':len(actual),'actual_stage_nodes':stages,'complete_valid_files':completed,'actual_result':row['result'],'not_a_learned_planner':True})
            elif mode=='apd02-meta':
                state=row['operational_environment_state'];expected_second=request['operandos'][1];public0=None;audited=[];done=False
                for j,op in enumerate(row['result']['opportunities']):
                    node=label+':goal:'+str(j);binding=index['by_node'][node];receipt=op['environment_effect']['committed_effect'];folder=(root/binding['directory']if receipt.get('artifact')else root)if receipt is not None else None
                    result=goal.audit_goal_opportunity(op,artifact_directory=folder,quality_module=quality,expected_second=expected_second)
                    for issue in result['issues']:check(node+':'+issue,False)
                    e=op['environment_effect'];public=e['public_before'];check(node+':literal_goal',public['text']==request['texto']and public['left']==request['operandos'][0]);check(node+':environment_hidden_or_actual',public['second']in(None,expected_second))
                    if j==0:check(node+':initial_visibility_literal',public['second']==(expected_second if request['segundo_visible']else None));public0=public
                    else:check(node+':same_environment_after_previous_action',public==audited[-1]['public_after'])
                    check(node+':no_more_actions_after_completion',not done);done=op['environment_effect']['progress_after']['verified_file_goal_completed']
                    returned=op['common_return']
                    if returned:
                        expected_ports={-1,0,1}if returned['category']=='FAILURE'and returned['mode']=='real'else set()
                        check(node+':fixed_common_return_all_or_none',{int(r['port'].rsplit('.',1)[1])for r in returned['requests']}==expected_ports and all(r['payload']==0 for r in returned['requests']))
                    if receipt and receipt.get('state')!='uncertain':check(node+':real_goal_provider_not_fixture',receipt['fixture_does_not_advance_DEE']is False)
                    result['node']=node;result['artifact_binding']=binding;audited.append(result)
                if audited:
                    check(label+':progress_matches_last_actual_action',row['result']['progress']==row['result']['opportunities'][-1]['environment_effect']['progress_after'])
                    check(label+':operational_public_not_history_or_recommended_action',state['public']==audited[-1]['public_after']and set(state)=={'schema','public','private_environment','progress','artifacts'})
                check(label+':bounded_goal_opportunities',len(audited)<=4)
                goals.append({'event':event['id'],'literal_request':request,'initial_public':public0,'actual_opportunities':audited,'final_operational_progress':state['progress'],'complete_verified_file':state['progress']['verified_file_goal_completed'],'private_environment_fact_only':state['private_environment'],'scope':'Goal/private operand/progress are declared external world state. Only an actual QUERY exposes the operand; ACT receives native arithmetic. The four-opportunity loop and completion stop are prepared assistance, not a learned planner.'})
            else:check(label+':recognized_frozen_mode',False)
    def counts(rows):
        complete=[r for r in rows if 'category'in r]
        return{'archived_effect_rows':len(rows),'archived_terminal_quality_rows':len(complete),'operator_emissions':sum(r['word_sign']in(-1,1)for r in complete),'route_emissions':sum(r['route_choice']is not None for r in complete),'provider_calls':sum(sum(r['provider_calls'].values())for r in complete),'semantic_correct':sum(r['semantic_correct']for r in complete),'provider_number_correct_for_original_request':sum(r['numeric_provider_correct_for_original_request']for r in complete),'artifact_number_correct_for_original_request':sum(r['numeric_artifact_correct_for_original_request']is True for r in complete),'valid_real_files':sum(r['real_artifact_valid']for r in complete),'completed_tasks':sum(r['valid_completed_task']for r in complete),'success_under_resource_limits':sum(r['task_success_under_limits']for r in complete),'categories':dict(collections.Counter(r['category']for r in complete))}
    direct=[r for r in apd if r['opportunity_kind']=='direct'];last_math=[r for r in direct if r['event']=='old_math6_no_feedback'];memory_groups={}
    for row in memories:memory_groups.setdefault(row['event'],[]).append(row)
    return{'schema':'DEE.APD02.continuous_reserve_archived_functions.R01','issues':issues,'checks':checks,'primary_sha256':u.sha(root/'REGISTROS_VENTANA.json.gz'),'RAW_serialized_observations':s['RAW_serialized_observations'],'unique_observed_site_ticks':s['unique_observed_site_ticks'],'fixed_readers':s['fixed_readers'],'native_numeric_readers':s['native_numeric_readers'],'transport':s['transport_summary'],'planned_material_events':len(proto['events']),'incomplete_or_unexecuted_planned_events':incomplete,'native_inputs':s['native_inputs'],'APD':{'all_primitives':counts(apd),'direct':counts(direct),'final_math6':counts(last_math),'cases':apd},'memory_panels':memory_groups,'explicit_new_teaching':teachers,'new_function_uses':language,'accumulator':acc,'raw128':raw128,'assisted_composition':compositions,'goals':goals,'continuity':{'initial':x['initial'],'final':x['final'],'owner_final':x.get('owner_final'),'pending_transport':x.get('pending'),'sources_unchanged':x.get('sources_unchanged')},'scope':'Pure archived audit, not Native reproduction or new learning. All fixed readers derive from RAW and every declared file comes from the exact event/stage and existing operational directory. Explicit compara revision/restoration and beta new content are external teaching; only the other5 contexts can count as old-retention after beta changes. Math correctness, learned-cue use, file effect, cost/delay and availability are independent axes. Duration/owner continuity is a separate calculator. No source, world, queue, choice or response is modified.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--evaluador',type=Path,required=True);p.add_argument('--fuente-ruta',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia,a.evaluador,a.fuente_ruta)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':r['issues'],'checks':r['checks'],'RAW':r['RAW_serialized_observations'],'APD':r['APD']['all_primitives'],'new_native_ticks':0}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
