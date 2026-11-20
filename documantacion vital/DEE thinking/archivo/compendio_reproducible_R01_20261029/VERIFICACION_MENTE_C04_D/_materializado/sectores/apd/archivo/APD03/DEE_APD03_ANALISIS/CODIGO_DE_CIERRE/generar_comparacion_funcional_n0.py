"""Compare closed MAIN/4 conventional trajectories, archived bytes only."""
import argparse,collections,gzip,hashlib,json
from pathlib import Path

PROGRAM_SHA='96b6b1a82bd4a3f3bc0cb6f9650752ed8bf3506b9e0bf37de2ea6dc2c51ca599'
TAG_TO_TASK={name+'_offered':name for name in('experience_full','reserve_full_1','reserve_hidden_1',
    'reserve_hidden_2','habitat_after_quality','reserve_full_later','final_hidden_no_feedback')}
TAG_TO_TASK.update(pending_goal_first_op='after_window_same_goal_across_UI_processes',
    continuation_same_queued_ID='after_window_same_goal_across_UI_processes')


def read(path):
    path=Path(path);data=path.read_bytes();return json.loads(gzip.decompress(data)if path.suffix=='.gz'else data)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source(path):
    path=Path(path);return {'file':str(path),'bytes':path.stat().st_size,'sha256':sha(path)}


def emit(path,value):
    with Path(path).open('x',encoding='utf8')as stream:
        json.dump(value,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in('main-stage','three','standard','supervision','program','out'):parser.add_argument('--'+key,required=True,type=Path)
    args=parser.parse_args();stage=args.main_stage.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    program=read(args.program)
    if sha(args.program)!=PROGRAM_SHA:raise ValueError('Exact common program required')
    tasks={e['task_id']:e for e in program['events']if e['kind']=='task'}
    report=read(stage/'RESULTADOS/RECALCULO_MAIN_FINAL.json');supervision=read(args.supervision)
    io=read(stage/'RECURSOS_OS_NATIVE/RESULTADO.json');evidence=stage/'EVIDENCIA_MAIN'
    events=[];locations=[]
    for path in sorted((evidence/'EVENTOS').glob('*.json.gz')):
        events.append(read(path));locations.append(source(path))
    ids={r['id']for r in events if r.get('kind')=='material'}
    continuation=read(evidence/'CONTINUACION_OTRO_PROCESO.json.gz')
    pending_id=continuation['same_queued_ID_result']['request']['id']
    for line_number,line in enumerate(gzip.decompress((evidence/'SESIONES_UI_NUEVAS.jsonl.gz').read_bytes()).splitlines()):
        row=json.loads(line)
        if row.get('event')not in('literal_material_result','same_id_read_only_result'):continue
        transport=row.get('result')or{};request=transport.get('request')or transport
        if request.get('status')!='completed'or request.get('is_control')or not request.get('result')or request['id']in ids:continue
        result=request['result'];decoded=json.loads(result)if isinstance(result,str)else result
        events.append({'kind':'material','id':request['id'],'tag':'continuation_same_queued_ID'if request['id']==pending_id else'ordinary_UI_final_panel',
            'decoded_result':decoded,'ui_source_line':line_number})
        ids.add(request['id'])
    checks=[];main_tasks={tid:[]for tid in tasks};main_raw=[];quality_rows=[];actual_order=[]
    def check(value,description):
        checks.append({'check':description,'verified':bool(value)})
        if not value:raise ValueError(description)
    expected_ops={(r['transport_id'],r['opportunity']):r for r in report['opportunities']}
    for event in events:
        if event.get('kind')!='material':continue
        decoded=event.get('decoded_result')or{};rows=(decoded.get('result')or{}).get('rows',[])
        tag=event['tag']
        for row in rows:
            if row.get('kind')=='APD02_quality_request'and tag in tasks:
                task=tasks[tag];effect=row['committed_effect'];artifact=row['quality']['private_audit']['observed_artifact']
                if tag not in actual_order:actual_order.append(tag)
                check(task['public_resources']['allowed_actions']==['ACT']and task['max_opportunities']==1,tag+': ACT-only1')
                check(row['literal_form']==task['text']and row['raw_operands']==[task['left'],task['second']],tag+': same raw facts')
                check(effect['delay_ticks']<=8 and effect['price']<=2,tag+': common fixed resource limits')
                parent=[r for r in report['APD02_quality_uses']if r['tag']==tag and r['scope_group']=='three_two_provider_cases']
                check(len(parent)==1 and parent[0]['actual_bytes_independently_verified'],tag+': original artifact byte verified')
                check(artifact==parent[0]['actual_file'],tag+': committed actual file agrees with closed byte audit')
                compact={'task_id':tag,'domain':'two_provider_quality','action':'ACT','operation':effect['selected_operation'],
                    'procedure':effect['selected_procedure'],'completed':parent[0]['success'],'actual_file':artifact,
                    'new_fact':False,'return_delivered':True,'transport_id':event['id']}
                main_tasks[tag].append(compact);quality_rows.append(compact)
            for opportunity in row.get('opportunities',[]):
                if not {'native_selection','environment_effect','word'}<=set(opportunity):continue
                tid=TAG_TO_TASK[tag];task=tasks[tid];public=opportunity['public_observation'];effect=opportunity['environment_effect']
                if tid not in actual_order:actual_order.append(tid)
                check(public['text']==task['text']and public['left']==task['left']and public['context']==task['context'],tid+': public form,left,context')
                check(public['second']is None or public['second']==task['second'],tid+': visible second is true fact')
                check(effect['public_after']['second']==task['second'],tid+': postaction public fact')
                for key,value in public['public_resources'].items():
                    check(value==task['public_resources'][key],tid+': fixed interface resource '+key)
                check(task['public_resources']['allowed_actions']==['ACT','QUERY']and task['max_opportunities']==4,tid+': common ACT/QUERY4')
                check(opportunity['raw_missing_fact_codec']['raw_value']==int(public['second']is None),tid+': physical sensor missingness')
                check(opportunity['return_mode']==task['feedback'],tid+': same feedback omission mode')
                closed=expected_ops[(event['id'],opportunity['opportunity'])]
                check(closed['action']==effect['selected_action']and closed['file_completed']==effect['final_goal_file_completed'],tid+': primary vs closed audit')
                compact={'task_id':tid,'domain':'native_only_goal','action':effect['selected_action'],
                    'completed':effect['final_goal_file_completed'],'new_fact':effect['new_public_fact_revealed'],
                    'return_delivered':opportunity['return_mode']=='real','transport_id':event['id'],
                    'opportunity':opportunity['opportunity'],'raw_observation_auditor':public,
                    'physical_sensor_value':opportunity['raw_missing_fact_codec']['raw_value'],
                    'actual_file':closed['actual_file'],'physical_query_tick':closed['query_tick']}
                main_tasks[tid].append(compact);main_raw.append(compact)
    check(len(main_raw)==14 and len(quality_rows)==3,'14goal+3quality comparable opportunities')
    check(actual_order==list(tasks),'MAIN actual task chronology equals the prospective common event order')
    check(report['counts']['ACT']==8 and report['counts']['QUERY']==6,'Closed MAIN high-level goal denominators')
    ordered=[]
    for task in(e for e in program['events']if e['kind']=='task'):
        tid=task['task_id'];rr=main_tasks[tid]
        check(bool(rr)and len(rr)<=task['max_opportunities'],tid+': finite opportunity budget observed')
        check(all(r['action']in task['public_resources']['allowed_actions']for r in rr),tid+': allowed actions respected')
        if rr[0]['domain']=='native_only_goal':
            check((rr[0]['raw_observation_auditor']['second']is not None)==task['second_initially_public'],tid+': matching initial missingness')
            values=[r['actual_file']['operands']for r in rr if r['actual_file']]
            check(values==[[task['left'],task['second']]],tid+': actual goal artifact operands')
        ordered.append({'task_id':tid,'domain':rr[0]['domain'],'form':task['text'],'operands':[task['left'],task['second']],
            'initial_second_public':task['second_initially_public'],'max_opportunities':task['max_opportunities'],
            'opportunity_invocations':task['opportunity_invocations'],'feedback':task['feedback'],
            'main_actions':[r['action']for r in rr],'main_completed':any(r['completed']for r in rr),
            'main_actual_opportunities':len(rr),'main_transports':[r['transport_id']for r in rr]})
    refs=[]
    for name,folder in[(name,args.three/name)for name in('fijo','tabla_contextual','wsls')]+[('wsls_estandar',args.standard/'wsls_estandar')]:
        summary=read(folder/'resumen.json');rows=[json.loads(line)for line in(folder/'eventos_primarios.jsonl').read_bytes().splitlines()]
        check(summary['program_sha256']==PROGRAM_SHA,name+': same prospective program')
        opportunities=[r for r in rows if r['kind']=='opportunity']
        check(list(dict.fromkeys(r['task_id']for r in opportunities))==list(tasks),name+': same task event order')
        for row in opportunities:
            task=tasks[row['task_id']];obs=row['public_observation']
            check(obs['left']is None and obs['second']in(None,0)and obs['context']==0,name+': values/context blinded before decision')
            check(row['return_delivered']==(task['feedback']=='real'),name+': same return omission')
        for item in ordered:
            rr=[r for r in opportunities if r['task_id']==item['task_id']]
            item.setdefault('references',{})[name]={'actions':[r['committed_action']for r in rr],
                'completed':any(r['final_goal_file_completed']for r in rr),'opportunities':len(rr)}
        refs.append({'policy':name,'summary_source':source(folder/'resumen.json'),'primary_source':source(folder/'eventos_primarios.jsonl'),
            'goal_completed_total':[summary['native_only_completed'],summary['native_only_total']],
            'quality_completed_total':[summary['quality_completed'],summary['quality_total']],
            'all_completed_total':[summary['tasks_completed'],summary['task_count']],
            'opportunities':summary['opportunities_requested'],'QUERY':summary['queries'],
            'ACT':summary['opportunities_requested']-summary['queries']-summary['no_output'],
            'instrumented_worker_interval':summary['process_total'],'owned_worker_job':summary['owned_job_resources'],
            'energy':'NO MEDIDA'})
    total=supervision['final_job'];cpu=total['cpu_user_seconds']+total['cpu_kernel_seconds']
    check(cpu==1881.90625 and total['peak_job_committed_bytes']==356691968,'Actual outer supervisor TOTAL resource values')
    check(all(job['job_active_processes']==0 for job in io['jobs'].values()),'Both measured Native jobs closed')
    native_io=[{'job_name':name,**row}for name,row in io['jobs'].items()]
    result={'schema':'DEE.APD03.closed_MAIN_four_references.N0','checks':checks,'discrepancies':0,
        'program_source':source(args.program),'main_recalculation_source':source(stage/'RESULTADOS/RECALCULO_MAIN_FINAL.json'),
        'main_primary_sources':locations,'main_UI_source':source(evidence/'SESIONES_UI_NUEVAS.jsonl.gz'),
        'main':{'goal_completed_total':[8,8],'quality_completed_total':[sum(r['completed']for r in quality_rows),3],
            'all_completed_total':[sum(r['main_completed']for r in ordered),len(ordered)],'comparable_opportunities':17,
            'QUERY':6,'ACT':11,'goal_opportunities':14,'quality_opportunities':3,
            'raw_opportunity_comparisons':main_raw,'quality_comparisons':quality_rows,
            'resources_outer_TOTAL':{'source':source(args.supervision),'job':total,'CPU_seconds':cpu,
                'supervised_wall_seconds':supervision['wall_seconds'],'enabled_environment_seconds':report['window']['enabled_seconds'],
                'scope':'Whole supervised programme: driver, clients, Native owner jobs and process continuations;352 spawned processes, not352 entities. Nested resource accounts are not added.'},
            'resources_native_only_IO_class8':{'source':source(stage/'RECURSOS_OS_NATIVE/RESULTADO.json'),'jobs':native_io,
                'scope':'OS logical transfer counts cumulative since each disjoint Native job creation; late observer attachment does not erase earlier totals. Not physical disk or energy.'},
            'driver_CPU_ns_separate':report['window']['driver_cpu_ns'],
            'driver_scope':'Already contained in outer supervision when descendant; never add it to outer TOTAL.',
            'per_decision_host_latency_comparable':None,
            'per_decision_host_latency_reason':'Archive groups several physical operations/material requests and idle/service work; no matching isolated host decision interval shared with comparator samples.',
            'energy':'NO MEDIDA'},'references':refs,'by_task_in_common_order':ordered,
        'coverage_excluded':program['outside_comparator_coverage'],
        'information_fence':'Native selection uses learned form cue and raw missingness; context field is not transduced. Conventional projection explicitly blinds context/magnitudes, then executor receives actual operands after committed action.',
        'preparation':'Six prior mathematical associations explicitly supplied to conventional policies, not new APD03 acquisition or equal training cost. Native learned luma/nara, MA use/panels and assisted composition are excluded from these11tasks.',
        'timing_scope':'Native retains a one-hour evolving world and application/service load. References execute logical event order without one-hour basal physics. No division of whole-hour CPU/wall by task count or by classic decision time is an efficiency result.',
        'IO_scope':'Main class8 job I/O versus reference GetProcessIoCounters worker I/O are genuine but differently scoped logical OS counters. Earlier class9 reserved IoInfo zeros are NO MEDIDO, never no I/O.',
        'statistical_scope':'One continuous MAIN plus one trajectory per conventional policy. Tasks/queries/forks are dependent uses, not independent learners.',
        'new_native_ticks':0,'new_provider_calls':0,'energy':'NO MEDIDA'}
    emit(out/'COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json',result)
    print(json.dumps({'out':str(out),'checks':len(checks),'discrepancies':0,'sha256':sha(out/'COMPARACION_FUNCIONAL_Y_COSTE_MAIN_REFERENCIAS.json')}))


if __name__=='__main__':main()
