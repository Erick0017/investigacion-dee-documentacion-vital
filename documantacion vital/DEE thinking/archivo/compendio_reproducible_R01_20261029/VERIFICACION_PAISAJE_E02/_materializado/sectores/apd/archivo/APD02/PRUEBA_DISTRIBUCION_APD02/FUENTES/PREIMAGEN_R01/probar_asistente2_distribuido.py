"""Bounded APD02 proof in an exact extracted Full, through the existing launcher.

No policy, fallback, target-driven routing, T0 recreation or original mutation.
All audits occur after native results; the request sequence is fixed beforehand.
"""
import hashlib,importlib.util,json,time
from datetime import datetime
from pathlib import Path
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def run(root,life,alias,sequence,call):
    settings=sequence['service_protocol']
    if settings['schema']!='APD02.full.operational.R01'or alias!='ASISTENTE_CALIDAD'or sequence.get('status')!='CLOSED_FOR_EXACT_ARCHIVE_PROOF':raise ValueError('Explicit CLOSED fixed APD02 paired protocol required; a candidate is not executable')
    material_sha=hashlib.sha256(json.dumps(settings,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
    if material_sha!=sequence.get('material_settings_sha256'):raise ValueError('Prospectively fixed payload/temporal settings changed')
    prefix=settings['prefix'];python=root/'motor/python313/python.exe';launcher=root/'actualizaciones/arrancar.py';pc=load('archive_owned_job',root/'sistema/app/process_control.py')
    raw=load('archive_raw_auditor',root/'actualizaciones/recalcular_cadena_main_apd02.py');route=load('archive_route_auditor',root/'actualizaciones/recalcular_ruta04_main_apd02.py');quality=load('archive_quality_only',root/'sistema/capacidades/evaluador_calidad_apd02.py');effect=load('archive_effect_only',root/'actualizaciones/auditar_efecto_apd02_r02.py');goal=load('archive_goal_only',root/'actualizaciones/auditar_evento_objetivo_apd02_r03.py')
    origin=route.origin_from_source(root/'sistema/capacidades/ruta_adaptativa_apd02_04.py');folder=root/'trabajo_personal/resultados'/('ENTREGA_'+life);folder.mkdir(parents=True,exist_ok=False)
    result={'schema':'DEE.APD02.exact_extracted_paired_service_proof.R01','protocol':settings,'functional_issues':[],'results':{},'audit_after_actions_only':True,'no_target_route_or_operation_actor_arguments':True,'copied_archive_only':True};owner=None;job=None;owner_index=0
    def cmd(label,args):return json.loads(call(label,['gestor',*args]))
    def row_of(value):return value.get('request')or value
    def native(value):return json.loads(row_of(value)['result'])['result']
    def fence(value):
        v=native(value).get('INSTRUMENTO_FENCE')
        if not isinstance(v,dict)or v.get('denied')or v.get('no_lab_evidence_or_history_reads_allowed')is not False or v.get('legacy_combined_flag_deprecated_no_universal_history_guarantee')is not True or v.get('no_undeclared_external_lab_or_evidence_reads_allowed')is not True or v.get('operational_history_reads_universally_blocked')is not False:raise ValueError('Absent/denied/misleading instrument descriptor, not an OS sandbox')
        return v
    def control(label,operation):
        identifier=prefix+label;value=cmd(label,['mente-unificada-'+operation,'--vida',life,'--id',identifier,'--esperar',str(settings['control_wait_seconds'])]);row=row_of(value)
        if row.get('status')!='completed':raise RuntimeError('Same technical ID not completed; preserve state, never retry: '+identifier)
        return json.loads(row['result'])
    def request(label,rows,mode='omit',wait=True):
        identifier=prefix+label;value=cmd(label,['mente-unificada-pedir','--vida',life,'--id',identifier,'--situaciones',json.dumps(rows,ensure_ascii=False,separators=(',',':')),'--retorno',mode,'--esperar',str(settings['material_wait_seconds']if wait else 0)])
        if wait:
            if row_of(value).get('status')!='completed':raise RuntimeError('New material request not completed; no automatic resubmit')
            fence(value)
        result['results'][label]=value;return value
    def client(label,arguments,mode='omit'):
        identifier=prefix+label;args=['asistente2',life,*arguments,'--id',identifier,'--retorno',mode,'--esperar',str(settings['material_wait_seconds'])];value=json.loads(call(label,args))
        if row_of(value).get('status')!='completed':raise RuntimeError('Literal client request did not complete; no fallback')
        fence(value);result['results'][label]=value;result.setdefault('actual_new_launcher_calls',[]).append({'label':label,'argv':args,'launcher_sha256':sha(launcher)});return value
    def memory_panel(value):
        rows=native(value)['rows'];expected=[r['contexto']for r in settings['old_panel']];entries=[r['result']['rows'][0]for r in rows];contexts=[r['context_signal']for r in entries]
        if len(entries)!=len(expected)or len(set(contexts))!=len(contexts)or set(contexts)!=set(expected):raise ValueError('Duplicate/incomplete memory panel')
        return{r['context_signal']:raw.pure_z(r['reader'],{f:(raw.I,v)for f,v in raw.CONTEXTS.items()})[0]for r in entries}
    def delta(value):
        r=native(value)['rows'][0];frames=[]
        for f in r['frames']:
            answer,cs=raw.delta_read(f)
            if answer!=f['reader']['value']or cs!=f['reader']['candidates']:raise ValueError('Accumulator reader differs from exact fixed RAW')
            frames.append({'tick':f['tick'],'value':answer})
        if frames[-1]['value']!=r['numeric_result']:raise ValueError('Accumulator final number not from RAW')
        if type(r['numeric_result'])is not int:result['functional_issues'].append('accumulator_no_unique_native_value')
        return{'numeric_result':r['numeric_result'],'increment':r['increment'],'delay_periods':r['delay_periods'],'legacy_uses_before':r['legacy_uses_before'],'legacy_uses_after':r['legacy_uses_after'],'frames':frames}
    def audit_apd(value,request_row,label):
        r=native(value)['rows'][0]
        def one(part,form,operands):
            receipt=part['committed_effect'];directory=Path(part['effect_directory']).resolve()
            if not directory.is_relative_to(root/'trabajo_personal/estado/servicios_locales'/life):raise ValueError('Effect not in this exact extracted personal life')
            report=effect.audit_effect(part,{'task_id':receipt['task_id'],'text':form,'operands':operands},directory,quality=quality,raw_util=raw,route_util=route,origin=origin)
            if report['issues']:raise ValueError('Archived physical/file/evaluator mismatch: '+str(report['issues']))
            if not report['task_success_under_limits']:result['functional_issues'].append(label+':'+report['category'])
            return report
        if request_row['modo']=='apd02':audit=one(r,request_row['texto'],request_row['operandos'])
        else:
            current=request_row['datos'][0];parts=[]
            for i,part in enumerate(r['rows']):
                parts.append(one(part,request_row['formas'][i],[current,request_row['datos'][i+1]]))
                if not part['quality']['task_success']:break
                current=part['committed_effect'].get('used_value')
            audit={'assisted_order_not_learned_planner':True,'parts':parts,'actual_result':r['result']}
            if r['result']is None:result['functional_issues'].append(label+':composition_not_complete')
        result.setdefault('APD_archived_audits',{})[label]=audit
    def audit_goal(value,label):
        body=native(value);r=body['rows'][0];episode=body['final']['operational']['episodes'];directory=root/'trabajo_personal/estado/servicios_locales'/life/('apd02_goal_resume_'+str(episode))/'world';items=[]
        for opportunity in r['result']['opportunities']:
            checked=goal.audit_goal_opportunity(opportunity,artifact_directory=directory,quality_module=quality,expected_second=settings['goal_initialization']['operandos'][1])
            if checked['issues']:raise ValueError('Goal RAW/actual file interpretation differs: '+str(checked['issues']))
            returned=opportunity['common_return']
            if returned:
                expected={-1,0,1}if returned['category']=='FAILURE'and returned['mode']=='real'else set()
                if{int(q['port'].rsplit('.',1)[1])for q in returned['requests']}!=expected:raise ValueError('Goal return did not use fixed common ports')
            items.append(checked)
        result.setdefault('goal_archived_audits',{})[label]={'episode_derived_from_exact_session_counter':episode,'actual_directory':str(directory),'opportunities':items}
    def start():
        nonlocal owner,job,owner_index
        if job is not None or(owner and owner.poll()is None):raise ValueError('No second owner before previous owned job closes')
        owner_index+=1;launch=time.time();args=[str(python),'-I','-B','-X','utf8',str(launcher),'asistente2',life,'iniciar','--pausado','--intervalo','.1','--max-segundos',str(settings['owner_max_seconds'])]
        owner,job,name=pc.spawn_owned(args,cwd=root,stdout=(folder/('OWNER_'+str(owner_index)+'.txt')).open('x',encoding='utf8'),stderr=(folder/('OWNER_'+str(owner_index)+'_ERR.txt')).open('x',encoding='utf8'),memory_limit=settings['resource_limit_bytes'])
        result.setdefault('owned_starts',[]).append({'index':owner_index,'launcher_pid':owner.pid,'job_name':name,'argv':args});limit=time.monotonic()+60
        while time.monotonic()<limit:
            if owner.poll()is not None:raise RuntimeError('New extracted owner exited before ready')
            state=cmd('owner'+str(owner_index)+'_readiness',['mente-unificada-estado','--vida',life]);cached=state.get('observation')or state.get('owner')or state
            if cached.get('running')and datetime.fromisoformat(cached['wall_utc']).timestamp()>=launch:return cached
            time.sleep(.1)
        raise TimeoutError('Own extracted owner readiness')
    def stop(label):
        nonlocal owner,job
        receipt=control(label,'detener');owner.wait(timeout=60);resources=pc.job_resources(job);end=time.monotonic()+5;samples=[resources]
        while resources.get('job_active_processes',0)and time.monotonic()<end:time.sleep(.02);resources=pc.job_resources(job);samples.append(resources)
        result.setdefault('owned_close',[]).append({'index':owner_index,'resources':resources,'bounded_exit_grace_samples':samples})
        if resources.get('job_active_processes')!=0:raise RuntimeError('Own job still has process after grace; clean closure not proved')
        pc.close_job(job);job=None
        if owner.returncode:raise RuntimeError('Own owner failed')
        owner=None;return receipt
    call('new_default_entry_explicit_paired_copy',['investigacion',life]);card=root/'trabajo_personal/estado/vidas'/life/'VIDA.json';initial=read(card);selected=next(r for r in read(root/'entes/CATALOGO.json')['cuts']if r['alias']==alias);physical_keys=('N','tick','RAW_sha256','clocks_sha256')
    if selected['source_life']!=sequence['source_cut']['life_id']or selected['snapshot_sha256']!=sequence['source_cut']['snapshot_sha256']or initial['parent']['encoded_sha256']!=selected['snapshot_sha256']or initial['branch']!='EXPLICIT_IMPORTED_CONTINUITY'or any(initial['physical'][k]!=selected['physical'][k]for k in physical_keys):raise ValueError('Research entry did not import the exact complete CLOSED selected state before any input')
    result['exact_import']={'life_id':life,'world_id':initial['world_id'],'source_life':selected['source_life'],'source_snapshot_sha256':selected['snapshot_sha256'],'initial_physical':initial['physical'],'no_T0':True,'new_default_entry_actually_used':True}
    try:
        result['owner1']=start();result['resume1']=control('resume1','reanudar')
        before=request('old6_before',settings['old_panel']);result['baseline_memory_RAW']=memory_panel(before)
        if any(v not in(-1,1)for v in result['baseline_memory_RAW'].values()):result['functional_issues'].append('initial_old_memory_panel_not_fully_accessible')
        for i,r in enumerate(settings['new_apd']):
            value=client('new_apd_'+str(i),['usar','--texto',r['texto'],'--operandos',*[str(v)for v in r['operandos']]]);audit_apd(value,r,'new_apd_'+str(i))
        for i,r in enumerate(settings['new_functions']):
            value=client('new_function_'+str(i),['lenguaje','--texto',r['texto'],'--valor',str(r['valor']),'--contexto',r['contexto']]);part=native(value)['rows'][0];word=raw.pure_z(part['word']['reader'],raw.FORM_CODEC)[0];interaction=part['interaction'];answer=None
            if word!=part['native_function_choice']:raise ValueError('Function word not from fixed RAW')
            if interaction is not None:answer=raw.selector(interaction['reader'],(15,15,15))[0]if word==1 else raw.pure_z(interaction['reader'],{f:(raw.I,v)for f,v in raw.CONTEXTS.items()})[0]
            expected=1 if r['texto']=='compara'else-1
            result.setdefault('function_archived_audits',[]).append({'literal':r['texto'],'native_function_choice':word,'actual_interaction_choice':answer,'declared_preceding_lesson_expected':expected,'not_actor_input':True})
            if word!=expected or answer is None:result['functional_issues'].append('function_'+r['texto']+'_not_currently_usable_as_declared')
        result['delta_before']=delta(client('delta_before',['acumular','--valor',str(settings['accumulator_before']['valor']),'--demora-periodos',str(settings['accumulator_before']['demora_periodos'])]))
        result['raw128']=request('raw128',[settings['new_raw']]);rawrow=native(result['raw128'])['rows'][0];answer=raw.selector(rawrow['reader'],(15,15,15))[0];result['raw128_reader_audit']={'choice':answer,'matches_recorded':answer==rawrow['reader']['choice'],'all_components':rawrow['raw_components'],'literal_components_unchanged':rawrow['raw_components']==settings['new_raw']['componentes']}
        result['raw128_reader_audit']['native_requests']=len(rawrow['requests']);result['raw128_reader_audit']['native_applied']=sum(r['receipt']['status']=='applied'for r in rawrow['requests'])
        if result['raw128_reader_audit']['native_applied']!=len(rawrow['requests']):result['functional_issues'].append('raw128_some_native_inputs_rejected')
        if answer is None:result['functional_issues'].append('raw128_no_unique_output')
        if not result['raw128_reader_audit']['matches_recorded']or not result['raw128_reader_audit']['literal_components_unchanged']:raise ValueError('RAW128 instrument mismatch')
        aggregate_frames=[f for f in rawrow['frames']if f['tick']==rawrow['datum_tick']-2]
        if len(aggregate_frames)!=1:raise ValueError('Fixed raw128 aggregate C frame absent')
        observation=aggregate_frames[0]['fields']['C'];decoded=raw.decoded(observation);aggregate=decoded['s_reg']if observation['site']==[12,17,18]and decoded['active']and decoded['semantic']==1 and decoded['direction']==[1,-1,-1]else None
        result['raw128_reader_audit'].update(native_aggregate_from_RAW=aggregate,auditor_posthoc_sum=sum(settings['new_raw']['componentes']))
        if aggregate!=sum(settings['new_raw']['componentes']):result['functional_issues'].append('raw128_aggregate_not_the_fixed_literal_frame')
        r=settings['composition'];value=client('new_composition',['componer','--formas',*r['formas'],'--datos',*[str(v)for v in r['datos']]]);audit_apd(value,r,'new_composition')
        teacher=settings['declared_teaching'];taught=request('explicit_beta_minus_lesson',[teacher]);teacher_requests=native(taught)['rows'][0]['result']['rows'][0]['requests'];teacher_applied=sum(r['receipt']['status']=='applied'for r in teacher_requests);result['teacher_actual_admission']={'requested':len(teacher_requests),'applied':teacher_applied};after=request('old5_plus_new_beta_after_lesson',settings['old_panel']);result['after_teaching_memory_RAW']=memory_panel(after)
        new_beta=result['baseline_memory_RAW'].get('beta')==settings['required_actual_baseline_for_new_revision']and result['after_teaching_memory_RAW'].get('beta')==teacher['senal']and teacher_applied==len(teacher_requests);result['declared_teaching_is_verified_new_revision']=new_beta
        if not new_beta:result['functional_issues'].append('fixed_beta_minus_not_verified_as_new_revision_no_retarget')
        goal_request=settings['goal_initialization'];client('goal_init',['meta-iniciar','--texto',goal_request['texto'],'--operandos',*[str(v)for v in goal_request['operandos']],'--segundo-oculto'],mode='real')
        first=client('goal_first_one',['meta-paso','--oportunidades','1'],mode='real');audit_goal(first,'before_reload');firstrow=native(first)['rows'][0];state=firstrow['operational_environment_state'];result['goal_before_reload']=state
        if state['progress']['opportunities_used']!=1 or state['progress']['verified_file_goal_completed']or state['progress']['uncertain_effect']is not None:raise ValueError('The declared genuine incomplete goal boundary was not reached; no substitute')
        control('pause_pending','pausar');queued=request('queued_delta_zero',[settings['queued_accumulator_after']],wait=False);qr=row_of(queued)
        if qr.get('status')!='queued'or json.loads(qr['payload'])['situaciones']!=[settings['queued_accumulator_after']]:raise ValueError('No actual queued literal request; comparing absent pending would be invalid')
        result['actual_pending_transport_before']={'id':qr['id'],'status':qr['status'],'payload':qr['payload'],'payload_sha':qr['payload_sha']}
        result['saved_pending']=control('save_pending','guardar');result['paired_pending_export']=control('export_pending','exportar');result['owner1_stop']=stop('stop1');witness=result['saved_pending']['committed_snapshot'];cut=read(card)
        result['owner2']=start();result['loaded_pending']=control('save_loaded_pending','guardar');loaded=result['loaded_pending']['committed_snapshot']
        if any(witness['physical'][k]!=loaded['physical'][k]for k in physical_keys)or witness['operational_dependencies']!=loaded['operational_dependencies']:raise ValueError('Complete saved native/external pending state changed before next process input')
        pending=cmd('same_queued_ID_before_resume',['mente-unificada-resultado','--vida',life,'--id',prefix+'queued_delta_zero']);qr2=row_of(pending)
        if any(qr2.get(k)!=qr.get(k)for k in('id','status','payload','payload_sha')):raise ValueError('Exact queued request/progress not preserved across processes')
        result['actual_pending_transport_after']=qr2;control('resume2','reanudar');limit=time.monotonic()+settings['material_wait_seconds'];poll=0
        while time.monotonic()<limit:
            poll+=1;value=cmd('same_delta_ID_poll_'+str(poll),['mente-unificada-resultado','--vida',life,'--id',prefix+'queued_delta_zero'])
            if row_of(value).get('status')in('completed','failed_preserved','uncertain','rejected_invalid'):break
            time.sleep(.1)
        if row_of(value).get('status')!='completed':raise RuntimeError('Queued continuation incomplete; same ID not resubmitted')
        fence(value);result['results']['queued_delta_zero_after_reload']=value;result['delta_after_reload']=delta(value)
        if type(result['delta_before']['numeric_result'])is not int or result['delta_after_reload']['numeric_result']!=result['delta_before']['numeric_result']:result['functional_issues'].append('delta_value_not_retained_across_owner_reload')
        continuation=client('goal_continue',['meta-paso','--oportunidades','3'],mode='real');audit_goal(continuation,'after_reload');result['goal_after_reload']=native(continuation)['rows'][0]['operational_environment_state']
        if not result['goal_after_reload']['progress']['verified_file_goal_completed']:result['functional_issues'].append('four_opportunity_goal_did_not_complete_no_repair')
        result['old_after_reload']=request('old5_plus_new_beta_after_reload',settings['old_panel']);result['after_reload_memory_RAW']=memory_panel(result['old_after_reload'])
        for context,previous in result['baseline_memory_RAW'].items():
            expected=teacher['senal']if context=='beta'else previous
            if result['after_teaching_memory_RAW'].get(context)!=expected or result['after_reload_memory_RAW'].get(context)!=expected:result['functional_issues'].append('memory_not_retained_or_revised_'+context)
        control('final_pause','pausar');result['final_export']=control('final_export','exportar');result['owner2_stop']=stop('stop2');final=read(card);snapshot=(root/'sistema'/final['snapshot']).resolve(strict=True)
        if final['life_id']!=initial['life_id']or final['world_id']!=initial['world_id']or final['physical']['tick']<=cut['physical']['tick']or not snapshot.is_relative_to(root/'trabajo_personal')or sha(snapshot)!=final['snapshot_sha256']:raise ValueError('Continuation replaced identity/state or used original source paths')
        result['continued_state']={'life_id':life,'world_id':final['world_id'],'tick':final['physical']['tick'],'snapshot':str(snapshot),'snapshot_sha256':final['snapshot_sha256'],'physical':final['physical'],'parent':final.get('parent')}
        result['pending_reload_verified']={'physical_fields_equal_before_input':True,'exact_serialized_operational_dependencies_equal':True,'same_queued_ID_payload_status':True,'no_requeue_or_T0':True,'pending_goal_is_external_world_facts_not_memory_or_plan':True}
        return result
    finally:
        if owner and owner.poll()is None:
            try:result['emergency_stop']=stop('emergency_stop')
            except Exception as error:result['stop_failure_preserved']=str(error)
        if job is not None:
            resources=pc.job_resources(job)
            if resources.get('job_active_processes',0):
                result['forced_owned_job_cleanup']={'last_resource':resources,'no_effect_retry':True};pc.terminate_job(job,125)
                if owner:owner.wait(timeout=60)
            result['finally_job_resources']=pc.job_resources(job);pc.close_job(job)
        with(folder/'PRUEBA_SERVICIO_APD02.json').open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
