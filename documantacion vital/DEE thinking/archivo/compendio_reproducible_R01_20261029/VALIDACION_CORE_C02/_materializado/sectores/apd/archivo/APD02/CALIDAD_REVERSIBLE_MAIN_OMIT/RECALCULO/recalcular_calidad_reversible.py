"""Portable retrospective comparison of equal-price MAIN and OMIT histories.

All reference arithmetic below belongs to the auditor AFTER actual effects.
No engine, provider call, external route policy or native update is executed.
"""
import argparse,collections,hashlib,importlib.util,json
from pathlib import Path

def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
HERE=Path(__file__).parent
scanmod=load('qr_archived_scanner',HERE/'auditar_archivo_ventana_apd02.py')
u=scanmod.u;r4=scanmod.r4
effect=load('qr_private_effect_auditor',HERE/'auditar_efecto_apd02_r02.py')
TREATMENT=('a1','a2','b1','b2','b3','a3','a4')
BLOCKS=(('a1','a2'),('b1','b2','b3'),('a3','a4'))

def check_ref_observations(observations,origin):
    wanted=[[(origin[j]+off[j])%67 for j in range(3)]for off in((-1,-1,0),(1,-1,0))]
    indexed={tuple(o['site']):o for o in observations}
    if len(observations)!=2 or set(indexed)!={tuple(p)for p in wanted}:raise ValueError('Both fixed acquired-reference fields required')
    values=[u.decoded(indexed[tuple(site)])['s_reg']for site in wanted]
    return {'A':values[0],'B':values[1],'difference':values[0]-values[1],'observations':observations}

def analyze_arm(folder,origin,quality):
    scan=scanmod.scan(folder,origin);x=scan['x'];proto=scan['proto'];artifacts=u.read(folder/'ARTEFACTOS.json');issues=list(scan['issues']);checks=scan['checks'];effects=[];panels={};other=[]
    def check(name,ok):
        nonlocal checks
        checks+=1
        if not ok:issues.append(name)
    check('window_has_no_transport_error',not x.get('error'))
    for event in proto['events']:
        identifier=proto['prefix']+event['id'];transport=scan['transports'].get(identifier)
        check(identifier+':present_completed',transport is not None and transport['status']=='completed')
        if not transport or identifier not in scan['parsed']:continue
        rows=scan['parsed'][identifier].get('result',{}).get('rows',[]);situations=event['payload']['situaciones'];check(identifier+':literal_unchanged',json.loads(transport['payload'])==event['payload']);check(identifier+':row_count',len(rows)==len(situations))
        for slot,(s,row)in enumerate(zip(situations,rows)):
            label=identifier+':'+str(slot);mode=s['modo']
            if mode=='apd02':
                receipt=row['committed_effect'];public={'task_id':receipt['task_id'],'text':s['texto'],'operands':s['operandos']};item=artifacts['by_slot'][label];directory=folder/item['directory']
                audited=effect.audit_effect(row,public,directory,quality=quality,raw_util=u,route_util=r4,origin=origin)
                issues.extend(label+':'+v for v in audited['issues']);checks+=len(audited['checks'])
                check(label+':return_mode_exact',row['feedback_mode']==event['payload'].get('retorno','real'))
                returned=row['native_consequence'];refs=None
                if returned:
                    refs={'before':check_ref_observations(returned['before'],origin),'after':check_ref_observations(returned['after'],origin)}
                    check(label+':return_is_category_not_correct_route',returned['category']==row['feedback_to_participant']['category']and returned['no_action_or_correct_route_argument']is True)
                    check(label+':literal_feedback_mode',returned['mode']==event['payload'].get('retorno','real'))
                effects.append({'event':event['id'],'slot':slot,'literal':s['texto'],'raw_operands':s['operandos'],'trial_group':'treatment'if event['id']in TREATMENT else'common_probe'if event['id']=='common_probe'else'old_form_retention','before_tick':row['before']['tick'],'after_tick':row['after']['tick'],'route_query_tick':row['route']['query_tick']if row['route']else None,'actor_feedback_category':row['feedback_to_participant']['category'],'native_elapsed_ticks':int(row['after']['tick'])-int(row['before']['tick']),'host_elapsed_seconds_recorded':row.get('host_elapsed_seconds'),'environment':row['environment'],'feedback_mode':row['feedback_mode'],'native_references':refs,'artifact':item,**{k:v for k,v in audited.items()if k not in('checks','issues')}})
            elif mode=='memoria':
                sign,candidates=u.pure_z(row['result']['rows'][0]['reader'],{f:(u.I,v)for f,v in u.CONTEXTS.items()})
                panels.setdefault(event['id'],[]).append({'context':s['contexto'],'choice':sign,'candidate_count':len(candidates),'beta_deliberately_revised_not_inherited_minus':s['contexto']=='beta'})
            elif mode=='apd02-lenguaje':
                word,_=u.pure_z(row['word']['reader'],u.FORM_CODEC);interaction=row.get('interaction');other.append({'event':event['id'],'kind':mode,'literal':s['texto'],'native_function_choice':word,'prepared_context':s['contexto'],'recorded_interaction_kind':interaction.get('kind')if interaction else None})
            elif mode=='apd02-acumular':
                values=[]
                for frame in row['frames']:
                    value,cs=u.delta_read(frame);check(label+':delta_RAW',value==frame['reader']['value']and cs==frame['reader']['candidates']);values.append(value)
                check(label+':delta_result_not_host_replacement',values[-1]==row['numeric_result'])
                other.append({'event':event['id'],'kind':mode,'increment':row['increment'],'read_values':values,'numeric_result':row['numeric_result'],'legacy_uses_before':row['legacy_uses_before'],'legacy_uses_after':row['legacy_uses_after'],'read_tick':row['read_tick'],'not_a_new_teacher':s['valor']==0})
    check('exact14_APD_effects',len(effects)==14)
    byevent={e['event']:e for e in effects if e['trial_group']=='treatment'};check('exact7_treatment_events',set(byevent)==set(TREATMENT))
    for event,e in byevent.items():
        env=e['environment'];check(event+':equal_legal_prices_delay_availability',env['precios']==[1,1]and env['demora']==[0,0]and env['disponibilidad']==[True,True]and env['presupuesto']==2)
        expected=['none','wrong_value']if event.startswith('b')else['wrong_value','none'];check(event+':law_frozen_not_retargeted',env['fallos']==expected)
    retention=[];before={r['context']:r['choice']for r in panels.get('old6_before',[])}
    for row in panels.get('old6_after',[]):retention.append({**row,'observed_before':before.get(row['context']),'same_as_own_before':row['context']in before and before[row['context']]==row['choice'],'declared_beta_teacher_sign':1 if row['context']=='beta'else None,'matches_declared_beta_teacher':row['choice']==1 if row['context']=='beta'else None})
    opportunities=[]
    for block in BLOCKS:
        for left,right in zip(block,block[1:]):
            a=byevent.get(left);b=byevent.get(right)
            if a and b:opportunities.append({'after_event':left,'next_common_block_opportunity':right,'preceding_detailed_quality_category':a['category'],'preceding_actor_feedback_category':a['actor_feedback_category'],'preceding_selected_procedure':a['selected_procedure'],'next_selected_procedure':b['selected_procedure'],'changed_route':a['selected_procedure']!=b['selected_procedure'],'next_task_success':b['task_success_under_limits'],'informative_failure_selected':a['actor_feedback_category']=='FAILURE'and a['selected_procedure']in('native','external')})
    clean=not x.get('forced_own_job_close',False)and not x.get('owner_final',{}).get('running',True)and x.get('pending')==[]and x.get('job_before_cleanup',{}).get('job_active_processes')==0
    check('one_window_stopped_cleanly',clean)
    return {'issues':issues,'checks':checks,'primary_sha256':u.sha(folder/'REGISTROS_VENTANA.json.gz'),'protocol_sha256':u.sha(folder/'PROTOCOLO.json'),'transport':scan['transport_summary'],'native_inputs':scan['native_inputs'],'RAW_serialized_observations':scan['RAW_serialized_observations'],'fixed_readers_recomputed':len(scan['fixed_readers']),'native_numeric_readers_recomputed':len(scan['native_numeric_readers']),'effects':effects,'panels':panels,'retention_against_own_before':retention,'other_function_uses':other,'same_block_consequence_opportunities':opportunities,'initial':x['initial'],'final':x['final'],'owner_stopped_cleanly':clean,'host_seconds':x.get('host_seconds'),'aggregate':{'requested_APD_effects':len(effects),'treatment_effects':sum(e['trial_group']=='treatment'for e in effects),'common_probe_effects':sum(e['trial_group']=='common_probe'for e in effects),'old_form_effects':sum(e['trial_group']=='old_form_retention'for e in effects),'route_outputs':sum(e['route_choice']is not None for e in effects),'actual_provider_calls':sum(sum(e['provider_calls'].values())for e in effects),'actual_valid_files':sum(e['real_artifact_valid']is True for e in effects),'numeric_correct_original_request':sum(e['numeric_artifact_correct_for_original_request']is True for e in effects),'quality_success':sum(e['task_success_under_limits']is True for e in effects),'category_counts':dict(collections.Counter(e['category']for e in effects))}}

def calculate(root):
    bindings=u.read(root/'BINDING/VINCULACION_N0.json');post=u.read(root/'BINDING/VINCULACION_POSTIMPORT_N0.json');origin=r4.origin_from_source(root/'FUENTES/ruta_adaptativa_apd02_04.py');quality=load('qr_exact_post_effect_quality',root/'FUENTES/evaluador_calidad_apd02.py')
    real=analyze_arm(root/'MAIN',origin,quality);omit=analyze_arm(root/'OMIT',origin,quality);issues=['MAIN:'+v for v in real['issues']]+['OMIT:'+v for v in omit['issues']];checks=[]
    def check(name,ok):
        checks.append({'name':name,'ok':ok})
        if not ok:issues.append(name)
    mp=u.read(root/'MAIN/PROTOCOLO.json');op=u.read(root/'OMIT/PROTOCOLO.json')
    check('same_exact_encoded_parent_original',real['initial']['snapshot_sha256']==bindings['paired_parent']['snapshot_sha256']==post['parent_encoded_sha256'])
    for key in('N','tick','RAW_sha256','clocks_sha256'):check('same_initial_physical_'+key,real['initial']['physical'][key]==omit['initial']['physical'][key]==post['paired_parent_physical'][key])
    check('control_import_documentary_snapshot_only',omit['initial']['snapshot_sha256']==post['only_documentary_protocol_change']['after']and op['snapshot_sha256']==omit['initial']['snapshot_sha256'])
    check('fixed_event_calendar_and_actual_payloads',len(mp['events'])==len(op['events'])==17)
    for me,oe in zip(mp['events'],op['events']):
        expected=json.loads(json.dumps(me));expected['payload']['retorno']='omit';check(me['id']+':only_omitted_feedback',expected==oe)
    check('all_control_feedback_omitted',all(e['feedback_mode']=='omit'for e in omit['effects']))
    pairs=[]
    for a,b in zip(real['effects'],omit['effects']):
        check(a['event']+':matched_literal_opportunity',a['event']==b['event']and a['slot']==b['slot']and a['literal']==b['literal']and a['raw_operands']==b['raw_operands']and a['environment']==b['environment'])
        pairs.append({'event':a['event'],'slot':a['slot'],'group':a['trial_group'],'MAIN':{'choice':a['route_choice'],'procedure':a['selected_procedure'],'category':a['category'],'actor_feedback_category':a['actor_feedback_category'],'quality_success':a['task_success_under_limits'],'ticks':[a['before_tick'],a['after_tick']],'route_query_tick':a['route_query_tick']},'OMIT':{'choice':b['route_choice'],'procedure':b['selected_procedure'],'category':b['category'],'actor_feedback_category':b['actor_feedback_category'],'quality_success':b['task_success_under_limits'],'ticks':[b['before_tick'],b['after_tick']],'route_query_tick':b['route_query_tick']},'different_choice':a['route_choice']!=b['route_choice'],'physical_age_before_difference':int(a['before_tick'])-int(b['before_tick']),'route_query_same_exact_age':a['route_query_tick']==b['route_query_tick']})
    return {'schema':'APD02.equal_price_quality_reversal.ROOT_vs_exact_paired_OMIT.archived.v1','issues':issues,'comparison_checks':checks,'origin_from_frozen_source':list(origin),'route_source_sha256':u.sha(root/'FUENTES/ruta_adaptativa_apd02_04.py'),'quality_source_sha256':u.sha(root/'FUENTES/evaluador_calidad_apd02.py'),'MAIN':real,'OMIT':omit,'matched_opportunities':pairs,'native_ticks':0,'new_provider_calls':0,'scope':'Retrospective auditor reconstructs fixed RAW readers and rereads the actual files. Feedback differs after a common complete paired physical parent. Encoded imported identity/metadata and subsequent interactive futures/ages may differ and are reported, not erased. No beta-minus inheritance assumption; beta explicit-plus teaching is distinct from the other five. Functional negatives do not become integrity errors. A local quality-conditioned route change is not a general policy, missing-data perception, semantic understanding, autonomous task initiative or R2.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'issues':r['issues'],'MAIN':r['MAIN']['aggregate'],'OMIT':r['OMIT']['aggregate'],'native_ticks':0},ensure_ascii=False));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
