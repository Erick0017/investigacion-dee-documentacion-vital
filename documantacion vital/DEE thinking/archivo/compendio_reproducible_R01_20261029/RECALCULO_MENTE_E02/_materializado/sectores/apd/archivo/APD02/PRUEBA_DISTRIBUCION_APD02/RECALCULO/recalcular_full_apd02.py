"""Pure archived audit of an exact-extracted APD02 proof; never opens a Runtime."""
import argparse,collections,hashlib,importlib.util,json
from pathlib import Path
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
u=load('raw_archive',Path(__file__).with_name('recalcular_cadena_main_apd02.py'))
r4=load('route_archive',Path(__file__).with_name('recalcular_ruta04_main_apd02.py'))
effect=load('effect_archive',Path(__file__).with_name('auditar_efecto_apd02_r02.py'))
goal=load('goal_archive',Path(__file__).with_name('auditar_evento_objetivo_apd02_r03.py'))
def calculate(root,evaluator,route_source):
    proof=u.read(root/'PRUEBA_SERVICIO_APD02.json.gz');bound=u.read(root/'PROTOCOLO_LIGADO.json');index=u.read(root/'ARTEFACTOS.json');quality=load('private_quality',evaluator);origin=r4.origin_from_source(route_source);settings=bound['service_protocol'];issues=[];checks=0;receipts={};seen={};raw_count=0;readers=[];numbers=[];results={};transports={}
    def check(label,ok):
        nonlocal checks
        checks+=1
        if not ok:issues.append(label)
    check('prospective_material_unchanged',proof['protocol']==settings and hashlib.sha256(json.dumps(settings,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==bound['material_settings_sha256'])
    for label,value in proof['results'].items():
        transport=value.get('request')or value;identifier=transport['id'];check(label+':literal_payload_sha',hashlib.sha256(transport['payload'].encode()).hexdigest()==transport['payload_sha']);transports.setdefault(identifier,transport)
        if not transport.get('result'):continue
        body=json.loads(transport['result']);check(label+':result_id',body['id']==identifier);result=body['result'];results[label]=result
        guard=result.get('INSTRUMENTO_FENCE',{});check(label+':truthful_guard',not guard.get('denied')and guard.get('operational_history_reads_universally_blocked')is False and guard.get('no_undeclared_external_lab_or_evidence_reads_allowed')is True)
        for path,node in u.walk(body):
            if not isinstance(node,dict):continue
            tag=label+path
            if {'site','raw','tick'}<=node.keys():
                raw_count+=1;d=u.decoded(node)
                for key,v in d.items():
                    if key in node:check(tag+':'+key,node[key]==v)
                key=(tuple(node['site']),node['tick']);stamp=(str(node['raw']),str(node.get('clock')))
                if key in seen:check(tag+':same_site_tick',seen[key]==stamp)
                else:seen[key]=stamp
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                rc=node['receipt'];rid=str(rc['id']);old=receipts.get(rid);current={k:rc.get(k)for k in('id','kind','channels','requested_tick','status','effective_tick','reason')}
                if old:
                    check(tag+':receipt_identity',all(old[k]==current[k]for k in('id','kind','channels','requested_tick')))
                    if old['status']not in('scheduled','pending')and current['status']not in('scheduled','pending'):check(tag+':receipt_terminal',old==current)
                if old is None or current['status']not in('scheduled','pending'):receipts[rid]=current
            if 'formed_native_command'in node and'panel'in node:
                codec={f:(u.I,v)for f,v in u.CONTEXTS.items()}if len(node['panel'])==12 else u.FORM_CODEC;choice,cs=u.pure_z(node,codec);check(tag+':fixed_z_reader',choice==node['formed_native_command']and cs==node['candidates']);readers.append({'label':label,'path':path,'gates':len(node['panel']),'choice':choice})
            if 'choice'in node and'observations'in node:
                choice,cs=r4.choice3(node,origin)if len(node['observations'])==3 else u.selector(node,(15,15,15));check(tag+':fixed_selector',choice==node['choice']and cs==[v.get('choice')if isinstance(v,dict)else v for v in node['candidates']]);readers.append({'label':label,'path':path,'gates':len(node['observations']),'choice':choice})
            if node.get('kind')=='APD01_candidate_numeric_operation':
                value=u.numeric(node);check(tag+':numeric_raw',value==node['numeric_reader']['numeric_result']);numbers.append({'label':label,'path':path,'value':value,'operation':node['operation']})
    def first(label):return results[label]['rows'][0]
    panels={}
    for label in('old6_before','old5_plus_new_beta_after_lesson','old5_plus_new_beta_after_reload'):
        rows=results[label]['rows'];expected=[v['contexto']for v in settings['old_panel']];entries=[v['result']['rows'][0]for v in rows];contexts=[v['context_signal']for v in entries];check(label+':exact_context_set',len(contexts)==6 and len(set(contexts))==6 and set(contexts)==set(expected));panels[label]={v['context_signal']:u.pure_z(v['reader'],{f:(u.I,d)for f,d in u.CONTEXTS.items()})[0]for v in entries}
    teacher=first('explicit_beta_minus_lesson')['result']['rows'][0];tr=teacher['requests'];teacher_applied=sum(v['receipt']['status']=='applied'for v in tr);baseline=panels['old6_before'];after=panels['old5_plus_new_beta_after_lesson'];reload=panels['old5_plus_new_beta_after_reload'];new_revision=baseline.get('beta')==settings['required_actual_baseline_for_new_revision']and after.get('beta')==settings['declared_teaching']['senal']and teacher_applied==len(tr)
    old5=[{'context':c,'before':v,'expected_from_declared_older_history':u.HISTORY[c],'before_matches_declared_history':v==u.HISTORY[c],'after_lesson':after.get(c),'after_reload':reload.get(c),'observed_before_content_retained':v in(-1,1)and after.get(c)==v and reload.get(c)==v,'historical_function_retained':v==u.HISTORY[c]and after.get(c)==v and reload.get(c)==v}for c,v in baseline.items()if c!='beta']
    check('explicit_beta_three_material_contacts',len(tr)==3)
    functions=[]
    for i,request in enumerate(settings['new_functions']):
        row=first('new_function_'+str(i));word=u.pure_z(row['word']['reader'],u.FORM_CODEC)[0];interaction=row['interaction'];answer=None
        if interaction is not None:answer=u.selector(interaction['reader'],(15,15,15))[0]if word==1 else u.pure_z(interaction['reader'],{f:(u.I,v)for f,v in u.CONTEXTS.items()})[0]
        functions.append({'literal':request['texto'],'physical_word_choice':word,'actual_interaction_choice':answer,'matches_declared_function_history':word==(1 if request['texto']=='compara'else-1),'historical_content_if_accessed':baseline.get(request['contexto'])if word==-1 else None,'matches_preceding_actual_memory_if_accessed':answer==baseline.get(request['contexto'])if word==-1 else None,'context_addressing_remains_operator_P0':True})
    effects=[];goals=[]
    def audit_one(row,form,operands,label):
        receipt=row['committed_effect'];binding=index['by_node'][label];folder=root/binding['directory']if receipt.get('artifact')else root
        if receipt.get('state')=='uncertain':
            check(label+':uncertain_not_evaluated',row.get('quality')is None and row.get('feedback_to_participant')is None);item={'node':label,'state':'uncertain'}
        else:
            checked=effect.audit_effect(row,{'task_id':receipt['task_id'],'text':form,'operands':operands},folder,quality=quality,raw_util=u,route_util=r4,origin=origin)
            for name,ok in checked['checks'].items():check(label+':'+name,ok)
            item={k:v for k,v in checked.items()if k not in('checks','issues')};item['node']=label
        effects.append(item);return item
    for i,request in enumerate(settings['new_apd']):audit_one(first('new_apd_'+str(i)),request['texto'],request['operandos'],'new_apd_'+str(i))
    composition=first('new_composition');request=settings['composition'];current=request['datos'][0]
    for j,row in enumerate(composition['rows']):
        audit_one(row,request['formas'][j],[current,request['datos'][j+1]],'new_composition:stage:'+str(j))
        if not(row.get('quality')or{}).get('task_success'):check('composition_no_fallback',j==len(composition['rows'])-1);current=None;break
        current=row['committed_effect'].get('used_value')
    complete=len(composition['rows'])==len(request['formas'])and current is not None and all((v.get('quality')or{}).get('task_success')for v in composition['rows']);check('composition_uses_actual_last_value',composition['result']==(current if complete else None))
    for label in('goal_first_one','goal_continue'):
        row=first(label);items=[]
        for j,op in enumerate(row['result']['opportunities']):
            binding=index['by_node'][label+':goal:'+str(j)];receipt=op['environment_effect'].get('committed_effect');folder=(root/binding['directory']if receipt.get('artifact')else root)if receipt else None;checked=goal.audit_goal_opportunity(op,artifact_directory=folder,quality_module=quality,expected_second=settings['goal_initialization']['operandos'][1])
            for issue in checked['issues']:check(label+':'+str(j)+':'+issue,False)
            items.append(checked)
        goals.append({'label':label,'opportunities':items,'progress':row['operational_environment_state']['progress']})
    delta=[]
    for label in('delta_before','queued_delta_zero_after_reload'):
        row=first(label);values=[]
        for frame in row['frames']:
            value,cs=u.delta_read(frame);check(label+':delta_raw',value==frame['reader']['value']and cs==frame['reader']['candidates']);values.append({'tick':frame['tick'],'value':value})
        check(label+':delta_actual',values[-1]['value']==row['numeric_result']);delta.append({'label':label,'value':row['numeric_result'],'increment':row['increment'],'frames':values})
    rawrow=first('raw128');check('raw128_literal_components',rawrow['raw_components']==settings['new_raw']['componentes']);mapping={'MU.raw.L128.'+side+'.root.'+str(a)+'.'+str(b)+'.raw.'+str(c):2*(16*a+4*b+c)+parity for parity,side in enumerate(('left','right'))for a in range(4)for b in range(4)for c in range(4)};leaves=[v for v in rawrow['requests']if v['port']in mapping];check('raw128_actual_independent_leaf_codec',len(leaves)==128 and{v['port']for v in leaves}==set(mapping)and all(v['payload']==settings['new_raw']['componentes'][mapping[v['port']]]and v['tick']==rawrow['input_tick']for v in leaves));cframes=[f for f in rawrow['frames']if f['tick']==rawrow['datum_tick']-2];check('raw128_single_C',len(cframes)==1);c=cframes[0]['fields']['C'];d=u.decoded(c);aggregate=d['s_reg']if c['site']==[12,17,18]and d['active']and d['semantic']==1 and d['direction']==[1,-1,-1]else None
    before=proof['saved_pending']['committed_snapshot'];loaded=proof['loaded_pending']['committed_snapshot'];keys=('N','tick','RAW_sha256','clocks_sha256');check('same_native_before_next_process_input',all(before['physical'][k]==loaded['physical'][k]for k in keys));check('same_complete_external_dependencies',before['operational_dependencies']==loaded['operational_dependencies']);qb=proof['actual_pending_transport_before'];qa=proof['actual_pending_transport_after'];check('same_queued_literal_id_once',all(qb[k]==qa[k]for k in('id','status','payload','payload_sha'))and qb['status']=='queued');check('queued_continuation_is_same_id',transports[settings['prefix']+'queued_delta_zero']['id']==qb['id']);check('one_life_two_owners',len(proof['owned_starts'])==2 and proof['continued_state']['world_id']==proof['exact_import']['world_id']and proof['continued_state']['life_id']==proof['exact_import']['life_id'])
    return {'schema':'DEE.APD02.extracted_full_archived_audit.R01','issues':issues,'checks':checks,'primary_sha256':u.sha(root/'PRUEBA_SERVICIO_APD02.json.gz'),'RAW_serialized_observations':raw_count,'unique_site_ticks':len(seen),'native_inputs':{'unique_requested':len(receipts),'terminal_status_counts':dict(collections.Counter(v['status']for v in receipts.values()))},'fixed_readers':readers,'numeric_RAW':numbers,'memory_panels':panels,'old5_retention':old5,'new_function_uses':functions,'explicit_beta_minus':{'requested':len(tr),'applied':teacher_applied,'baseline_actual':baseline.get('beta'),'actual_after':after.get('beta'),'actual_after_reload':reload.get('beta'),'verified_new_revision':new_revision,'revision_retained_after_reload':new_revision and reload.get('beta')==settings['declared_teaching']['senal'],'not_retargeted':True},'effects':effects,'assisted_composition':{'complete':complete,'actual_result':composition['result'],'not_learned_planner':True},'goals':goals,'delta':{'uses':delta,'value_retained_across_processes':type(delta[0]['value'])is int and delta[0]['value']==delta[1]['value']},'raw128':{'native_aggregate':aggregate,'auditor_sum_only':sum(settings['new_raw']['componentes']),'matches':aggregate==sum(settings['new_raw']['componentes']),'choice':u.selector(rawrow['reader'],(15,15,15))[0]},'recorded_functional_issues':proof['functional_issues'],'exact_import_record':proof['exact_import'],'continued_state_record':proof['continued_state'],'scope':'Archived RAW, selected real effects, receipts and paired-continuation records only. No Runtime, new provider call, replay, snapshot checksum revalidation, ZIP extraction, OS sandbox claim or new learned ability. The separate exact-Full verifier records extraction/import/Python/PYD provenance. Functional negatives do not become data-integrity errors.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--evaluador',type=Path,required=True);p.add_argument('--fuente-ruta',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();result=calculate(a.evidencia,a.evaluador,a.fuente_ruta)
    partial=load('preserved_R01',Path(__file__).with_name('auditar_intento_full_r01_apd02.py'));first=partial.calculate(a.evidencia/'INTENTO_R01',raw=u,route=r4,effect=effect,goal=goal,quality=load('private_quality_R01',a.evaluador),origin=r4.origin_from_source(a.fuente_ruta));result['preserved_incomplete_technical_attempt_R01']=first
    result['worlds_separate']=result['exact_import_record']['world_id']!=first['world_id'];result['technical_attempts_are_not_independent_learning_replicates']=True
    if not result['worlds_separate']:result['issues'].append('R01_R02_world_identity_not_separate')
    if first['protocol_material_sha256']!=u.read(a.evidencia/'PROTOCOLO_LIGADO.json')['material_settings_sha256']:result['issues'].append('R01_R02_material_settings_differ')
    result['issues'].extend('R01:'+v for v in first['issues'])
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':result['issues'],'checks':result['checks'],'RAW':result['RAW_serialized_observations'],'new_native_ticks':0}));return bool(result['issues'])
if __name__=='__main__':raise SystemExit(main())

