"""Prospective R04 ABAB archived audit: exact RAW, effects, quality and receipts.

This module never imports DEE, calls a provider, retries an action or chooses
a route. Fixed geometry is obtained from the captured pre-response source,
not fitted to the output. All correctness arithmetic is external auditing.
"""
import argparse,ast,collections,hashlib,importlib.util,json
from pathlib import Path

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
u=load('RAW_archive_utilities',Path(__file__).with_name('recalcular_cadena_main_apd02.py'))
def origin_from_source(path):
    for node in ast.parse(path.read_text(encoding='utf8')).body:
        if isinstance(node,ast.Assign)and any(isinstance(target,ast.Name)and target.id=='O'for target in node.targets):
            origin=ast.literal_eval(node.value)
            if not isinstance(origin,tuple)or len(origin)!=3 or any(type(v)is not int or not 0<=v<67 for v in origin):raise ValueError('Bounded exact frozen origin required')
            return origin
    raise ValueError('No literal prepared origin in captured R04 source')
def choice3(reader,origin):
    expected={tuple((origin[j]+off[j])%67 for j in range(3)):sign for sign in(-1,0,1)for off in[(2*sign,2,0)]};obs=reader['observations']
    if len(obs)!=3 or{tuple(o['site'])for o in obs}!=set(expected):raise ValueError('All three fixed gates required; no output-dependent reader')
    cs=[]
    for o in obs:
        d=u.decoded(o);sg=expected[tuple(o['site'])]
        if d['state']and d['semantic']==1 and d['direction']==[sg,1,0]:cs.append(sg)
    return cs[0]if len(cs)==1 else None,cs
def ports(origin):
    at=lambda delta:tuple((origin[j]+delta[j])%67 for j in range(3));prefix='APD02.trace.R04'
    out={prefix+'.experience.A':(at((-1,-1,-4)),(0,0,1)),prefix+'.experience.B':(at((1,-1,-4)),(0,0,1)),prefix+'.query':(at((0,0,-3)),(0,0,1)),prefix+'.support.plus':(at((-2,1,-2)),(1,0,1)),prefix+'.support.minus':(at((2,4,0)),(-1,-1,0))}
    for x in(-1,0,1):
        for kind,p,d in(('divert',(4*x,4,1),(0,0,-1)),('flatten',(6*x,6,-3),(0,0,1)),('clear',(10*x,10,-3),(0,0,1))):out[prefix+'.'+kind+'.'+str(x)]=(at(p),d)
        target=(2*x,-2,-2);d=(0,0,1)if x else(-1,0,1);p=tuple(target[j]-d[j]for j in range(3));out[prefix+'.failure.'+str(x)]=(at(p),d);out[prefix+'.sham.'+str(x)]=(at((p[0],p[1],p[2]+8)),d)
    return out
def refs(values,origin):
    expected={tuple((origin[j]+delta[j])%67 for j in range(3))for delta in((-1,-1,0),(1,-1,0))}
    if len(values)!=2 or{tuple(o['site'])for o in values}!=expected:raise ValueError('Both acquired reference positions required')
    return[{'site':o['site'],'raw':o['raw'],'clock':o['clock'],'s_reg':u.decoded(o)['s_reg']}for o in values]
def calculate(root,evaluator,route_source):
    x=u.read(root/'REGISTROS_VENTANA.json.gz');proto=u.read(root/'PROTOCOLO.json');artifacts=u.read(root/'ARTEFACTOS.json');history=u.read(root/'HISTORIA_R03.json.gz');origin=origin_from_source(route_source);quality=load('frozen_private_post_action_verifier',evaluator)
    issues=[];checks=0;RAW=0;seen={};receipts={};statuses=collections.defaultdict(set);readers=[];numbers=[]
    def check(name,ok):
        nonlocal checks
        checks+=1
        if not ok:issues.append(name)
    terminal=lambda status:status not in('pending','scheduled')
    transports={k:v for k,v in x['records'].items()if not k.endswith('_parsed')}
    for identifier,transport in transports.items():
        parsed=json.loads(transport['result']);check(identifier+':completed',transport['status']=='completed');check(identifier+':ID',parsed['id']==identifier);check(identifier+':payloadSHA',hashlib.sha256(transport['payload'].encode()).hexdigest()==transport['payload_sha'])
        if identifier+'_parsed'in x['records']:check(identifier+':parsed_mirror',parsed==x['records'][identifier+'_parsed'])
        fence=parsed.get('result',{}).get('INSTRUMENTO_FENCE')
        if fence:check(identifier+':truthful_guard',not fence['denied']and fence.get('operational_history_reads_universally_blocked')is False)
        for path,node in u.walk(parsed):
            if not isinstance(node,dict):continue
            label=identifier+path
            if'raw'in node and'site'in node and'tick'in node:
                RAW+=1;d=u.decoded(node)
                for k,v in d.items():
                    if k in node:check(label+':'+k,node[k]==v)
                key=(tuple(node['site']),int(node['tick']));stamp=(str(node['raw']),str(node.get('clock')))
                if key in seen:check(label+':same_site_tick',seen[key]==stamp)
                else:seen[key]=stamp
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                r=node['receipt'];rid=str(r['id']);entry={k:r.get(k)for k in('id','kind','channels','requested_tick','status','effective_tick','reason')};statuses[rid].add(r['status'])
                if rid in receipts:
                    old=receipts[rid];check(label+':receipt_identity',all(old[k]==entry[k]for k in('id','kind','channels','requested_tick')))
                    if terminal(old['status'])and terminal(entry['status']):check(label+':same_terminal_outcome',old==entry)
                    elif terminal(entry['status']):receipts[rid]=entry
                else:receipts[rid]=entry
                if'id'in node:check(label+':requestID',node['id']==r['id'])
                if'tick'in node:check(label+':requestTick',node['tick']==r['requested_tick'])
            if'formed_native_command'in node and'panel'in node:
                codec={f:(u.I,v)for f,v in u.CONTEXTS.items()}if len(node['panel'])==12 else u.FORM_CODEC;answer,cs=u.pure_z(node,codec);check(label+':pureZ',answer==node['formed_native_command']and cs==node['candidates']);readers.append({'id':identifier,'path':path,'gates':len(node['panel']),'choice':answer})
            if'choice'in node and'observations'in node:
                answer,cs=choice3(node,origin)if len(node['observations'])==3 else u.selector(node,(15,15,15));recorded=[c.get('choice')if isinstance(c,dict)else c for c in node['candidates']];check(label+':fixed_selector',answer==node['choice']and cs==recorded);readers.append({'id':identifier,'path':path,'gates':len(node['observations']),'choice':answer})
            if node.get('kind')=='APD01_candidate_numeric_operation':number=u.numeric(node);check(label+':numeric_RAW',number==node['numeric_reader']['numeric_result']);numbers.append({'id':identifier,'path':path,'value':number,'operation':node['operation']})
    logs=[json.loads(line)for line in(root/'ADMISIONES.jsonl').read_text(encoding='utf8').splitlines()if line];check('unique_transportIDs',len(logs)==len({l['id']for l in logs}));check('all_transports',{l['id']for l in logs}==set(transports))
    for log in logs:check(log['id']+':queued',log['admission']['admission']=='queued'and log['payload']==json.loads(transports[log['id']]['payload']))
    for previous,nxt in zip(logs,logs[1:]):check(previous['id']+':FIFO',transports[previous['id']]['finished_utc']<=transports[nxt['id']]['started_utc'])
    env=None;apd=[];memory={};language=[];delta=[];preflight=None
    for event in proto['events']:
        identifier=proto['prefix']+event['id'];parsed=json.loads(transports[identifier]['result']);situations=event['payload']['situaciones'];rows=parsed['result']['rows'];check(identifier+':rowcount',len(rows)==len(situations));check(identifier+':frozen_payload',json.loads(transports[identifier]['payload'])==event['payload'])
        for slot,(s,row)in enumerate(zip(situations,rows)):
            label=identifier+':'+str(slot);mode=s['modo']
            if mode=='apd02-ruta04-admitir':
                preflight=row['preparation']['preflight'];check(label+':origin_from_frozen_source',preflight['origin']==list(origin));check(label+':all_preflightRAW0',all(int(o['raw'])==0 for o in preflight['pre_geometry']+preflight['pre_loop']+[r['observation']for r in preflight['pre_ALL_injection_ports']]));actual={r['name']:(tuple(r['site']),tuple(r['direction']))for r in preflight['pre_ALL_injection_ports']};check(label+':all20ports_exact',len(actual)==20 and actual==ports(origin));own={tuple(r['site']):int(r['raw'])for r in preflight['geometry']};conflicts=[name for name,(site,di)in actual.items()if own.get(site,0)];check(label+':self_recipe_no_port_conflicts',not conflicts and preflight['self_recipe_port_conflicts']==[]and preflight['admissible']is True);check(label+':no_seed_or_transplant',row['seed_experience']is None and row['prior_body_and_adverse_future_preserved']is True)
            elif mode=='apd02-ambiente':env=row['after'];check(label+':environment',env==s['configuracion'])
            elif mode=='memoria':
                trial=row['result']['rows'][0];sign,_=u.pure_z(trial['reader'],{f:(u.I,v)for f,v in u.CONTEXTS.items()});memory.setdefault(event['id'],[]).append({'context':s['contexto'],'choice':sign,'expected_declared_history':u.HISTORY[s['contexto']],'match':sign==u.HISTORY[s['contexto']]})
            elif mode=='apd02-lenguaje':
                sign,_=u.pure_z(row['word']['reader'],u.FORM_CODEC);interaction=row['interaction'];check(label+':native_function',sign==row['native_function_choice']and interaction['kind']==('native_current_selection'if sign==1 else'query'));choice=u.selector(interaction['reader'],(15,15,15))[0]if sign==1 else u.pure_z(interaction['reader'],{f:(u.I,v)for f,v in u.CONTEXTS.items()})[0];language.append({'literal':s['texto'],'datum':s['valor'],'operator_context_P0':s['contexto'],'native_function_choice':sign,'native_interaction_choice':choice})
            elif mode=='apd02-acumular':
                value=None
                for frame in row['frames']:value,cs=u.delta_read(frame);check(label+':deltaRAW',value==frame['reader']['value']and cs==frame['reader']['candidates'])
                check(label+':delta_final',value==row['numeric_result']);delta.append({'increment':row['increment'],'result':value,'uses_before':row['legacy_uses_before'],'uses_after':row['legacy_uses_after'],'read_tick':row['read_tick']})
            elif mode=='apd02':
                word,_=u.pure_z(row['word']['reader'],u.FORM_CODEC);route,_=choice3(row['route']['reader'],origin)if row['route']else(None,[]);operation='add'if word==1 else'sub'if word==-1 else None;procedure='native'if route==-1 else'external'if route in(0,1)else None;receipt=row['committed_effect'];check(label+':physical_operation_route',operation==row['selected_operation']==receipt['selected_operation']and procedure==row['selected_procedure']==receipt['selected_procedure']);check(label+':public_original',row['literal_form']==s['texto']and row['raw_operands']==s['operandos']);check(label+':actual_environment',env==row['environment'])
                calls=receipt['provider_calls'];selected_available=bool(procedure is not None and env['disponibilidad'][0 if procedure=='native'else 1]);expected_calls={'native':int(procedure=='native'and selected_available),'external':int(procedure=='external'and selected_available)};check(label+':sole_selected_callback',calls==expected_calls)
                if procedure is None:check(label+':no_substitution',receipt['state']=='no_output'and receipt['artifact']is None and row['native_numeric']is None and row['external_tool']is None)
                else:
                    check(label+':real_callback_scope',receipt['fixture_does_not_advance_DEE']is False)
                    if selected_available:
                        if procedure=='native':check(label+':native_value_RAW',row['native_numeric']is not None and row['external_tool']is None and u.numeric(row['native_numeric'])==receipt['raw_provider_response']['value'])
                        else:check(label+':external_only',row['native_numeric']is None and row['external_tool']is not None and row['external_tool']['value']==receipt['raw_provider_response']['value'])
                    else:check(label+':unavailable_no_fallback',row['native_numeric']is None and row['external_tool']is None and receipt['state']=='failed'and receipt['failure_class']=='selected_provider_unavailable')
                    index=0 if procedure=='native'else 1;check(label+':chosen_actual_cost_delay',receipt['price']==env['precios'][index]and receipt['delay_ticks']==env['demora'][index])
                    if'used_value'in receipt:check(label+':provider_payload_not_corrected',receipt['used_value']==receipt['raw_provider_response']['value']+(1 if env['fallos'][index]=='wrong_value'else 0))
                policy={'max_operand':32,'max_artifact_bytes':4096,'max_price':env['presupuesto'],'max_delay_ticks':env['demora_maxima'],'resource_limits_required_for_success':True};public={'task_id':receipt['task_id'],'text':s['texto'],'operands':s['operandos']};item=artifacts['by_slot'][label];folder=root/item['directory']if receipt['artifact']else root;verified=quality.evaluate_literal_committed(public,receipt,sandbox_root=folder,policy=policy);check(label+':post_committed_quality_reread',u.content(verified)==u.content(row['quality']));check(label+':class_only_to_DEE',quality.actor_feedback(verified,binary=True)==row['feedback_to_participant']);check(label+':feedback_mode',row['feedback_mode']==event['payload'].get('retorno','real'))
                returned=row['native_consequence'];before=after=None
                if returned:
                    check(label+':category_no_action',returned['category']==row['feedback_to_participant']['category']and returned['no_action_or_correct_route_argument']is True);check(label+':common_return_ports',all(r['payload']==0 for r in returned['requests']));required={-1,0,1}if returned['category']=='FAILURE'and returned['mode']=='real'else set();actual={int(r['port'].rsplit('.',1)[1])for r in returned['requests']};check(label+':all_or_no_failure_ports_not_selected',actual==required);check(label+':generic_trace_source_not_reinjected',row['route']['trace_not_reinjected_from_reader']is True);before=refs(returned['before'],origin);after=refs(returned['after'],origin)
                apd.append({'id':identifier,'literal':s['texto'],'operands':s['operandos'],'word_sign':word,'route_choice':route,'procedure':procedure,'provider_calls':calls,'native_value_before_fault':(receipt.get('raw_provider_response')or{}).get('value'),'artifact_value':verified['private_audit']['observed_artifact']['value']if verified['private_audit']['observed_artifact']else None,'semantic_correct':verified['axes']['operation_corresponds_to_original_request'],'numeric_correct_original_request':verified['axes']['numeric_correct_for_original_request'],'category':verified['feedback']['category'],'valid_completed_task':verified['completed_task'],'within_resources':verified['resource_acceptable'],'task_success':verified['task_success'],'environment':env,'feedback_mode':row['feedback_mode'],'references_before_consequence':before,'references_after_consequence':after,'artifact':item})
    previous=[n for _,n in u.walk(history)if isinstance(n,dict)and n.get('kind')=='native_recirculating_accumulation_candidate'];prior=max(previous,key=lambda r:r['read_tick']);prior_value,_=u.delta_read(prior['frames'][-1]);check('exact_same_descendant_snapshot',x['initial']['snapshot_sha256']==history['final']['snapshot_sha256']==proto['snapshot_sha256'])
    if delta:check('delta_retained_after_route_changes',delta[0]['result']==prior_value+delta[0]['increment']and delta[0]['uses_before']==prior['legacy_uses_after'])
    check('all_archived_requests_resolved',all(terminal(r['status'])for r in receipts.values()));check('owner_stopped_without_forced_close',not x['owner_final']['running']and x['pending']==[]and not x.get('forced_own_job_close',False)and x['job_before_cleanup']['job_active_processes']==0)
    return{'schema':'DEE.APD02.R04_route_main_archived.candidate.R01','issues':issues,'checks':checks,'RAW_serialized_observations':RAW,'unique_observed_site_ticks':len(seen),'readers':readers,'native_numeric_readers':numbers,'frozen_route_origin':list(origin),'frozen_route_source_sha256':u.sha(route_source),'quality_source_sha256':u.sha(evaluator),'primary_sha256':u.sha(root/'REGISTROS_VENTANA.json.gz'),'transport':{'requested':len(logs),'admitted':sum(l['admission']['admission']=='queued'for l in logs),'completed':sum(r['status']=='completed'for r in transports.values()),'material':sum(not r['is_control']for r in transports.values()),'controls':sum(bool(r['is_control'])for r in transports.values())},'native_inputs':{'unique_requested':len(receipts),'status_counts':dict(collections.Counter(r['status']for r in receipts.values())),'status_sets_same_ids':dict(collections.Counter(','.join(sorted(values))for values in statuses.values())),'receipts':sorted(receipts.values(),key=lambda r:r['id'])},'preflight':{'performed':preflight is not None,'all20ports_checked':preflight is not None,'own_recipe_compatible':preflight['self_recipe_port_conflicts']==[]if preflight else None},'APD':{'requested':len(apd),'operator_emissions':sum(r['word_sign']in(-1,1)for r in apd),'route_emissions':sum(r['route_choice']is not None for r in apd),'provider_invocations':sum(sum(r['provider_calls'].values())for r in apd),'semantic_correct':sum(r['semantic_correct']for r in apd),'numeric_correct_original_request':sum(r['numeric_correct_original_request']is True for r in apd),'valid_completed_task':sum(r['valid_completed_task']for r in apd),'task_success_under_limits':sum(r['task_success']for r in apd),'category_counts':dict(collections.Counter(r['category']for r in apd)),'cases':apd},'memory':memory,'new_language_function_uses':language,'accumulator':{'prior_RAW_value':prior_value,'continuations':delta},'continuity':{'initial':x['initial'],'final':x['final'],'enabled_seconds':x['enabled_seconds'],'not_a60minute_test':True,'idle_delta':x['owner_final']['idle_ticks']-x['owner_initial']['idle_ticks'],'material_calls_delta':x['owner_final']['material_calls']-x['owner_initial']['material_calls'],'owner_stopped':not x['owner_final']['running']},'scope':'Archived computation only. Every fixed reader is reconstructed from RAW, and every committed artifact is reread from this exact exported event directory. Quality uses the original frozen public request only after a terminal effect; its private arithmetic and categories are audit, not native cognition. Response/operator/numeric/file/resource outcomes are distinct. Main ABAB history alone is not an age-matched causal control or policy-generalization proof. Prepared origin/ports/codec/schedule, operator teaching and preceding R03 adverse state remain separate and preserved. No Runtime, provider invocation, new native tick, action correction, repair, or promotion is executed.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--evaluador',type=Path,required=True);p.add_argument('--fuente-ruta',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia,a.evaluador,a.fuente_ruta)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':r['issues'],'checks':r['checks'],'RAW':r['RAW_serialized_observations'],'APD':r['APD']['category_counts'],'native_ticks':0}));raise SystemExit(bool(r['issues']))
