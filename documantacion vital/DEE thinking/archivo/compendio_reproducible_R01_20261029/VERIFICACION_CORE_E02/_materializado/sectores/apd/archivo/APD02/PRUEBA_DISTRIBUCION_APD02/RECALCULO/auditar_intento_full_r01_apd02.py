"""Audit the preserved, incomplete R01 proof separately from the R02 world."""
import hashlib,json
from pathlib import Path

def calculate(root,*,raw,route,effect,goal,quality,origin):
    proof=raw.read(root/'PRUEBA_SERVICIO_APD02.json.gz');diag=raw.read(root/'DIAGNOSTICO_N0.json');index=raw.read(root/'ARTEFACTOS.json');issues=[];checks=0;seen={};receipts={};readers=[];results={};count=0
    def check(label,ok):
        nonlocal checks
        checks+=1
        if not ok:issues.append(label)
    import gzip
    check('original_primary_exact_bytes',hashlib.sha256(gzip.decompress((root/'PRUEBA_SERVICIO_APD02.json.gz').read_bytes())).hexdigest()==diag['primary']['sha256'])
    check('separate_R01_world',proof['exact_import']['life_id']==index['life_id'] and proof['exact_import']['world_id']==index['world_id'])
    for label,value in proof['results'].items():
        transport=value.get('request')or value
        if not transport.get('payload'):continue
        check(label+':payload_sha',hashlib.sha256(transport['payload'].encode()).hexdigest()==transport['payload_sha'])
        if not transport.get('result'):continue
        body=json.loads(transport['result']);check(label+':result_id',body['id']==transport['id']);results[label]=body['result']
        for path,node in raw.walk(body):
            if not isinstance(node,dict):continue
            tag=label+path
            if {'site','raw','tick'}<=node.keys():
                count+=1;decoded=raw.decoded(node)
                for k,v in decoded.items():
                    if k in node:check(tag+':'+k,node[k]==v)
                key=(tuple(node['site']),node['tick']);stamp=(str(node['raw']),str(node.get('clock')))
                if key in seen:check(tag+':same_site_tick',seen[key]==stamp)
                else:seen[key]=stamp
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                r=node['receipt'];rid=str(r['id']);old=receipts.get(rid);current={k:r.get(k)for k in('id','kind','channels','requested_tick','status','effective_tick','reason')}
                if old:
                    check(tag+':receipt_identity',all(old[k]==current[k]for k in('id','kind','channels','requested_tick')))
                    if old['status']not in('scheduled','pending')and current['status']not in('scheduled','pending'):check(tag+':terminal',old==current)
                if old is None or current['status']not in('scheduled','pending'):receipts[rid]=current
            if 'formed_native_command'in node and'panel'in node:
                codec={f:(raw.I,v)for f,v in raw.CONTEXTS.items()}if len(node['panel'])==12 else raw.FORM_CODEC;value,cs=raw.pure_z(node,codec);check(tag+':reader',value==node['formed_native_command']and cs==node['candidates']);readers.append({'label':label,'choice':value,'gates':len(node['panel'])})
            if 'choice'in node and'observations'in node:
                value,cs=route.choice3(node,origin)if len(node['observations'])==3 else raw.selector(node,(15,15,15));check(tag+':selector',value==node['choice']and cs==[v.get('choice')if isinstance(v,dict)else v for v in node['candidates']])
            if node.get('kind')=='APD01_candidate_numeric_operation':check(tag+':number',raw.numeric(node)==node['numeric_reader']['numeric_result'])
    settings=proof['protocol'];queue=diag['same_ID_actual_closed_journal_row'];summary=diag['first_zero_wait_response'];out=diag['outstanding']
    expected={'modo':'apd02-acumular','valor':0,'demora_periodos':2}
    check('real_admission_not_full_row',summary['admission']=='queued'and summary['status']=='waiting_or_processing'and 'payload'not in summary)
    check('exact_pending_same_ID',queue['id']==settings['prefix']+'queued_delta_zero'and queue['status']=='queued'and summary['id']==queue['id']and len(out)==1 and out[0]['id']==queue['id'])
    check('exact_pending_literal',json.loads(queue['payload'])['situaciones']==[expected]and hashlib.sha256(queue['payload'].encode()).hexdigest()==queue['payload_sha'])
    check('journal_N0_unchanged',diag['journal_byte_unchanged']and diag['journal_SHA_after']==diag['journal_SHA_before']and diag['journal_integrity']=='ok'and diag['new_native_ticks']==0 and diag['requeued_actions']==0)
    check('no_resume_imputed','continued_state'not in proof and not diag['owner']['running']and not diag['owner']['uncertain_external_result'])
    check('owned_close_actual',len(proof['owned_close'])==1 and proof['owned_close'][0]['resources']['job_active_processes']==0 and not proof.get('forced_owned_job_cleanup'))
    effects=[]
    def audit(row,label,text,operands):
        receipt=row['committed_effect'];binding=index['by_node'][label];folder=root/binding['directory']if receipt.get('artifact')else root
        answer=effect.audit_effect(row,{'task_id':receipt['task_id'],'text':text,'operands':operands},folder,quality=quality,raw_util=raw,route_util=route,origin=origin)
        for name,ok in answer['checks'].items():check(label+':'+name,ok)
        effects.append({'label':label,**{k:v for k,v in answer.items()if k not in('checks','issues')}})
    for i,request in enumerate(settings['new_apd']):audit(results['new_apd_'+str(i)]['rows'][0],'new_apd_'+str(i),request['texto'],request['operandos'])
    composed=results['new_composition']['rows'][0];request=settings['composition'];current=request['datos'][0]
    for i,row in enumerate(composed['rows']):
        audit(row,'new_composition:stage:'+str(i),request['formas'][i],[current,request['datos'][i+1]])
        if not(row.get('quality')or{}).get('task_success'):break
        current=row['committed_effect'].get('used_value')
    panels={}
    for label in('old6_before','old5_plus_new_beta_after_lesson'):
        entries=[r['result']['rows'][0]for r in results[label]['rows']];check(label+':six_unique',len(entries)==6 and len({r['context_signal']for r in entries})==6);panels[label]={r['context_signal']:raw.pure_z(r['reader'],{f:(raw.I,v)for f,v in raw.CONTEXTS.items()})[0]for r in entries}
    check('beta_incomplete_attempt_real_change',panels['old6_before']['beta']==1 and panels['old5_plus_new_beta_after_lesson']['beta']==-1)
    for label in('delta_before',):
        row=results[label]['rows'][0]
        for frame in row['frames']:
            value,cs=raw.delta_read(frame);check(label+':delta_raw',value==frame['reader']['value']and cs==frame['reader']['candidates'])
    goalrow=results['goal_first_one']['rows'][0];ops=goalrow['result']['opportunities'];goals=[]
    for op in ops:
        checked=goal.audit_goal_opportunity(op,artifact_directory=None,quality_module=quality,expected_second=settings['goal_initialization']['operandos'][1]);goals.append(checked)
        for issue in checked['issues']:check('first_goal:'+issue,False)
    check('incomplete_goal_kept_incomplete',len(ops)==1 and diag['goal_before_reload']['progress']['verified_file_goal_completed']is False)
    return {'schema':'APD02.Full.incomplete_R01.archived_audit.N0','issues':issues,'checks':checks,'world_id':proof['exact_import']['world_id'],'life_id':proof['exact_import']['life_id'],'protocol_material_sha256':hashlib.sha256(json.dumps(proof['protocol'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),'RAW_serialized_observations':count,'unique_site_ticks':len(seen),'native_inputs_unique_within_this_world':len(receipts),'fixed_readers':readers,'memory_panels':panels,'real_effects_before_instrument_failure':effects,'first_goal_only':goals,'queued_literal_id':queue['id'],'queued_literal_sha256':queue['payload_sha'],'not_consumed_or_requeued_by_diagnosis':True,'instrumental_failure':diag['external_failure'],'complete_continuation':False,'source_or_cognitive_failure_inferred':False,'scope':'R01 is a separate personal world. Its incomplete goal and queued transport are retained. The zero-wait response-shape failure is not a Native failure. No IDs/RAW are merged with R02 and no technical reproduction is counted as independent learned replication. Uses archived observations and files only; no journal/snapshot/ZIP reopen or new provider call.'}
