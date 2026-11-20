"""Portable EO02 primary-record recalculation. Standard library, zero DEE ticks.

Rebuilds native output decoding from RAW observations, admission denominators,
post-action feedback causation, real local-worker byte results, transfer and
same-life continuity. Independent references never control an evaluated life.
"""
from pathlib import Path
import argparse,base64,csv,gzip,hashlib,json,re,statistics,sys,zlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from referencias_eo02 import Policy,Environment,policy_specs,REVISION as REFERENCE_REVISION

class ExactTaskEnvironment(Environment):
    """Instrument adapter to the published four-channel task, not a policy.
    Policy and seeds stay byte-frozen. Only the hidden task evaluator combines
    its own workloads, just as the actual worker does; the policy sees raw4.
    """
    def execute(self,action,observations,**kwargs):
        work=[sum(observations[::2]),sum(observations[1::2])]
        return super().execute(action,work,**kwargs)

def evaluate(events):
    output=[]
    for name,seed in policy_specs():
        policy=Policy(name,seed);environments={};rows=[]
        for event in events:
            domain=event['domain'];identity=event['environment_identity'];old=environments.get(domain)
            if old is None or old[0]!=identity:
                environment=ExactTaskEnvironment(domain,event['external_credit'],phase_visible=event.get('phase_visible',False))
                environments[domain]=(identity,environment)
            else:environment=old[1]
            environment.phase_visible=bool(event.get('phase_visible',False))
            obs=environment.observations(event['observations']);action=policy.choose(obs,phase_visible=environment.phase_visible)
            task_observations=event.get('task_observations',obs)
            before=policy.estimate;result=environment.execute(action,task_observations,actuator=event['actuator'],feedback=event['feedback']);policy.observe(result)
            rows.append({'case':event['case'],'ordinal':event['ordinal'],'domain':domain,'observations':obs,'action':action,
                'origin_life':event['origin_life'],'inherited_reference_prefix':event['origin_life']!=event['evaluation_life'],
                'completed_step':result.completed_step,'completed_transaction':result.completed_transaction,'contact':result.contact,
                'feedback_received':result.received,'estimate_before':before,'estimate_after':policy.estimate,
                'independent_environment_phase_after':int(environment.prepared_by is not None)})
        current=[x for x in rows if not x['inherited_reference_prefix']]
        output.append({'policy':name,'seed':seed,'prefix_attempts':len(rows)-len(current),'attempts':len(current),
            'completed_steps':sum(x['completed_step']for x in current),
            'completed_transactions':sum(x['completed_transaction']for x in current),'rows':rows})
    return{'revision':REFERENCE_REVISION,'task_model_adapter':'Actual alternating workload sums in evaluator only; frozen policy still receives all raw components.',
        'policy_count':len(output),'results':output,'scope':'Independent task-model arithmetic, never native DEE or external worker execution.'}

def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def read(p):
    if p.suffix=='.gz':
        with gzip.open(p,'rt',encoding='utf8')as f:return json.load(f)
    return json.loads(p.read_bytes())
def native_rows(v):
    if isinstance(v,dict):
        if isinstance(v.get('native'),dict)and all(k in v['native']for k in('before','after','row','reader','requests','environment_before')):
            native=dict(v['native'])
            for key in('raw_components','sensory_extra','sensory_extra_receipts','local_service','external_gate','phase_visibility'):
                if key in v:native[key]=v[key]
            if native.get('domain')is None:
                provider=native.get('local_service')or native.get('external_gate')or{}
                native['domain']=provider.get('before',{}).get('domain')
            yield native;return
        if all(k in v for k in('before','after','row','reader','requests','environment_before')):
            yield v;return
        for k,value in v.items():
            if k not in('stdout','stderr','operations','service','parent_record_at_fork'):yield from native_rows(value)
    elif isinstance(v,list):
        for value in v:yield from native_rows(value)
def fields(w,key):return [q['s_reg']for q in w[key]]
def decoded_word(raw):
    n=int(raw)
    if not 0<=n<2**64:raise ValueError('RAW outside uint64')
    def signed(n):return n-16 if n>=8 else n
    return{'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,
        'direction':[signed((n>>p)&15)for p in(48,52,56)]}
def verify_observation_fields(value,label,discrepancies):
    count=0
    if isinstance(value,dict):
        if all(k in value for k in('raw','clock','state','s_reg','semantic','direction')):
            count+=1;decoded=decoded_word(value['raw'])
            if any(value[k]!=v for k,v in decoded.items()):discrepancies.append({'kind':'raw_view_mismatch','case':label,'site':value.get('site')})
            clock=value['clock']
            if type(clock)not in(int,str)or not 0<=int(clock)<2**64:discrepancies.append({'kind':'clock_not_exact_uint64','case':label,'site':value.get('site')})
        for k,v in value.items():
            if k not in('stdout','stderr'):count+=verify_observation_fields(v,label,discrepancies)
    elif isinstance(value,list):
        for v in value:count+=verify_observation_fields(v,label,discrepancies)
    return count
def decode(r):
    critical=r['row']['critical_tick'];samples=[]
    for tick in(critical-16,critical-15):
        frame=next(q for q in r['frames']if q['tick']==tick);roles=[]
        for role in(-1,0,1):
            q=decoded_word(frame['contacts'][str(role)]['raw'])
            if q['state']>0 and q['semantic']==1 and q['direction']in([role,-1,-1],[role,-1,0]):roles.append(role)
        samples.append({'tick':tick,'material_roles':roles,'command':(1 if roles[0]>=0 else-1)if len(roles)==1 else None,'simultaneous_conflict':len(roles)>1})
    chosen=None if samples[-1]['simultaneous_conflict']else next((q for q in reversed(samples)if q['command']is not None),None)
    return{'samples':samples,'command':None if chosen is None else chosen['command'],'source_tick':None if chosen is None else chosen['tick'],'posture':None if chosen is None else chosen['material_roles'][0]}

def verify_archive(folder,identity,discrepancies):
    base=folder/identity;index=base/'INDICE.json'
    if not index.exists():
        discrepancies.append({'kind':'missing_code_archive','sha256':identity});return {'identity':identity,'present':False}
    signatures=read(index);computed=hashlib.sha256(json.dumps(signatures,sort_keys=True).encode()).hexdigest()
    if computed!=identity:discrepancies.append({'kind':'code_index_hash','expected':identity,'actual':computed})
    mismatches=[]
    for name,expected in signatures.items():
        p=base/name
        if not p.is_file()or sha(p)!=expected:mismatches.append(name)
    if mismatches:discrepancies.append({'kind':'code_members','identity':identity,'files':mismatches})
    return{'identity':identity,'files':len(signatures),'present':True,'index_matches':computed==identity,'member_mismatches':mismatches}

def worker_model(r,discrepancies,label):
    local=r.get('local_service')
    if local is None:return None
    before=local['before'];domain=before['domain'];command=r['executed_external_command'];receipt=local['worker_receipt']
    if command is None:
        if receipt is not None:discrepancies.append({'kind':'worker_called_without_action','case':label})
        return{'domain':domain,'expected_accepted':False,'expected_transaction':False,'executed':False}
    sensory=r.get('raw_components',r['row']['public_raw'])
    # A stage/context channel may be a physical stimulus but not task workload.
    # Preserve both byte-recorded domains; never add a false stage bit to the
    # worker's admission law merely because it entered the native comparator.
    pair=receipt.get('raw_observations',sensory)if receipt else sensory
    if not isinstance(pair,list)or not all(type(x)is int for x in pair):
        raise ValueError('Worker input observations must be exact integers')
    pending=before.get('pending_transaction');verify=domain.startswith('transaccion')and pending is not None
    if verify:
        payload=base64.b64decode(pending['payload_base64']);digest=hashlib.sha256(payload).hexdigest()
        accepted=command!=pending['prepared_by']and digest==pending['payload_sha256'];operation='verify_commit'
        if receipt and receipt.get('schema')=='EO02.local_worker.receipt.v2':
            embedded=base64.b64decode(pending['prepared_output_base64']);artifact_digest=hashlib.sha256(embedded).hexdigest()
            expected_artifact_ok=artifact_digest==pending['prepared_output_sha256']
            content_ok=zlib.decompress(embedded)==payload if pending['prepared_by']==1 else embedded==hashlib.sha256(payload).digest()
            check=receipt.get('prepared_artifact_check')or{}
            reported_actual_ok=bool(check.get('actual_file_read')and check.get('sha256')==artifact_digest and check.get('bytes')==len(embedded))
            if check.get('valid')!=bool(expected_artifact_ok and content_ok and reported_actual_ok):discrepancies.append({'kind':'artifact_chain_check','case':label})
            accepted=accepted and expected_artifact_ok and content_ok and reported_actual_ok
    else:
        left,right=sum(pair[::2]),sum(pair[1::2])
        payload=bytes(pair)*max(1,32+left);digest=hashlib.sha256(payload).hexdigest()
        eligible=1 if left+before['reference']>=right else-1
        accepted=command==eligible;operation='prepare'if domain.startswith('transaccion')else'execute_service'
    out=zlib.compress(payload,9)if command==1 else hashlib.sha256(payload).digest()
    expected={'worker':command,'operation':operation,'accepted':accepted,'transaction_completed':bool(verify and accepted),
        'input_bytes':len(payload),'input_sha256':digest,'output_bytes':len(out),'output_sha256':hashlib.sha256(out).hexdigest()}
    if receipt is None:discrepancies.append({'kind':'missing_worker_receipt','case':label})
    else:
        for key,value in expected.items():
            if receipt.get(key)!=value:discrepancies.append({'kind':'worker_byte_or_law_mismatch','case':label,'field':key,'expected':value,'actual':receipt.get(key)})
        for key in('host_started_ns','host_finished_ns','native_tick'):
            if type(receipt.get(key))is not int:discrepancies.append({'kind':'non_exact_integer','case':label,'field':key})
    return{**expected,'domain':domain,'executed':True,'real_operation_bytes_regenerated':True,
        'input_observations':pair,'sensory_observations':sensory,
        'separate_task_and_sensor_channels':pair!=sensory,
        'chained_file_check':None if receipt is None else receipt.get('prepared_artifact_check'),
        'worker_revision':None if receipt is None else receipt.get('schema')}

def summarize_file(path,payload,discrepancies):
    manager=payload.get('result',payload);rows=list(native_rows(manager.get('result',{})))if isinstance(manager,dict)else[]
    life=(manager.get('INSTRUMENTO',{}).get('life_id')or manager.get('life_id'))if isinstance(manager,dict)else None
    case={'file':path.name,'sha256':sha(path),'compressed_bytes':path.stat().st_size,'case':payload.get('case',path.stem),
        'returncode':payload.get('returncode'),'timed_out':payload.get('timed_out',False),'life':life,
        'code_revision_sha256':payload.get('code_revision_sha256'),'elapsed_host_seconds':payload.get('elapsed_seconds'),
        'experimental_source_sha256':payload.get('code_sha256'),
        'failure_type':payload.get('failure_type'),
        'instrumental_error':payload.get('detail',payload.get('stderr'))if payload.get('returncode')not in(None,0)else None,
        'declared_primary_native_ticks':payload.get('native_ticks'),
        'episodes':[],'incomplete_or_non_episode_primary':not rows}
    if isinstance(manager,dict)and manager.get('schema')=='DCS1.1.life.v1':case['fork_parent']=manager.get('parent')
    fence=manager.get('INSTRUMENTO_FENCE',{})if isinstance(manager,dict)else{}
    case['fence']={'denied':fence.get('denied',[]),'exact_environment_processes':len(fence.get('exact_environment_processes',[])),
        'scope':fence.get('scope')}
    for i,r in enumerate(rows):
        label=path.name+':'+str(i);d=decode(r);row=r['row'];before=r['before'];after=r['after'];mismatches=[]
        observation_checks=verify_observation_fields(r,label,discrepancies)
        for key in('samples','command','source_tick'):
            if r['reader'].get(key)!=d[key]:mismatches.append('reader.'+key)
        if r['formed_native_command']!=d['command']:mismatches.append('formed_command')
        expected_executed=d['command']if row['actuator']=='closed'else None
        if r['executed_external_command']!=expected_executed:mismatches.append('executed_command')
        if row['native_posture']!=d['posture']:mismatches.append('native_posture')
        worker=worker_model(r,discrepancies,label)
        raw_components=r.get('raw_components',row['public_raw'])
        if worker is None:
            reference=r['environment_before'].get('reference_not_injected',r['environment_before'].get('reference'))
            if reference is None:reference=r['environment_after'].get('reference_not_injected')
            expected_success=bool(expected_executed is not None and expected_executed==(1 if sum(raw_components[::2])+reference>=sum(raw_components[1::2])else-1))
            domain=r.get('domain')or'puertas'
        else:
            reference=r['local_service']['before']['reference'];expected_success=bool(worker['expected_accepted']if 'expected_accepted'in worker else worker['accepted']);domain=worker['domain']
        expected_contact=bool(expected_executed is not None and not expected_success)
        if r['job_completed']!=expected_success:mismatches.append('success')
        if r['observed_result']['contact']!=expected_contact:mismatches.append('contact')
        returned=d['posture']if expected_contact else None
        if row['feedback']=='omit':returned=None
        elif row['feedback']=='decoupled'and returned is not None:returned=-returned if returned else 1
        if row['returned_posture']!=returned:mismatches.append('returned_posture')
        tactile=[q for q in r['requests']if q['port'].startswith('EO01.post.tactile.')]
        if len(tactile)!=int(returned is not None):mismatches.append('tactile_count')
        if tactile:
            q=tactile[0];expected_tick=row['critical_tick']-15+(3 if returned==0 else 4)
            if q['payload']!=0 or q['tick']!=expected_tick or q['tick']<=r['observed_result']['tick']:mismatches.append('tactile_information_or_order')
            if q['direction']!=[returned,-1,0]:mismatches.append('tactile_posture')
        if not r['plan'].get('all_j0_sources_omitted'):mismatches.append('legacy_preconsequence_not_excluded')
        statuses={}
        extra=r.get('sensory_extra_receipts',(r.get('sensory_extra')or{}).get('request_receipts',[]))
        for q in r['requests']+extra:
            status=q['receipt']['status'];statuses[status]=statuses.get(status,0)+1
        counts={'requested_inputs':len(r['requests'])+len(extra),'applied_inputs':statuses.get('applied',0),
            'rejected_inputs':sum(n for s,n in statuses.items()if s.startswith('rejected')),'pending_inputs':sum(n for s,n in statuses.items()if s in('pending','accepted','queued')),'statuses':statuses}
        episode={'ordinal':i,'domain':domain,'start_tick':before['tick'],'critical_tick':row['critical_tick'],'end_tick':after['tick'],
            'native_tick_latency':row['critical_tick']-15-before['tick'],'raw_observations':raw_components,
            'task_observations':raw_components if worker is None else worker.get('input_observations',raw_components),
            'core_public_pair':row['public_raw'],'phase_visible':bool((r.get('phase_visibility')or{}).get('enabled',False)and not(r.get('phase_visibility')or{}).get('dose_matched_zero_control',False)),
            'phase_apparatus':r.get('phase_visibility'),
            'sensory_extra':r.get('sensory_extra'),
            'formed_native_command':d['command'],'posture':d['posture'],'executed_command':expected_executed,
            'valid_response':d['command']is not None,'useful':expected_success,'incorrect_executed':bool(expected_executed is not None and not expected_success),
            'abstention':d['command']is None,'actuator_annulled':d['command']is not None and expected_executed is None,
            'feedback':row['feedback'],'actuator_mode':row['actuator'],'contact':expected_contact,'tactile_return':returned,'external_credit_auditor_only':reference,
            'own_before':fields(before,'own'),'own_after':fields(after,'own'),'context_before':fields(before,'context_A'),'context_after':fields(after,'context_A'),
            'B_private_before':fields(before,'private_B'),'B_private_after':fields(after,'private_B'),
            'counts':counts,'reader_source_tick':d['source_tick'],'worker':worker,'mismatches':mismatches,
            'raw_clock_observation_checks':observation_checks,
            'trace_frames':len(r['frames']),'deep_trace':len(r['frames'])>30,
            'environment_before':r['environment_before'],'environment_after':r['environment_after']}
        frame=next((f for f in r['frames']if f['tick']==row['critical_tick']-17),None)
        targets=None if frame is None else frame.get('sensory_fanin_targets')
        if targets is not None and r.get('sensory_extra'):
            target_sums=[sum(raw_components[::2]),sum(raw_components[1::2])]
            actual_sums=[decoded_word(x['raw'])['s_reg']for x in targets]
            episode['sensory_sum_witness']={'tick':frame['tick'],'target_sums_auditor_only':target_sums,'physical_sums':actual_sums,'exact':target_sums==actual_sums}
            if target_sums!=actual_sums:mismatches.append('sensory_sum_witness')
        if i and case['episodes'][-1]['end_tick']!=before['tick']:mismatches.append('same_case_tick_gap')
        case['episodes'].append(episode)
        if mismatches:discrepancies.append({'kind':'episode_mismatch','case':label,'fields':mismatches})
    case['totals']={'attempts':len(rows),'valid':sum(r['valid_response']for r in case['episodes']),
        'executed':sum(r['executed_command']is not None for r in case['episodes']),'useful':sum(r['useful']for r in case['episodes']),
        'incorrect_executed':sum(r['incorrect_executed']for r in case['episodes']),'abstentions':sum(r['abstention']for r in case['episodes']),
        'actuator_annulled':sum(r['actuator_annulled']for r in case['episodes']),
        'completed_transactions':sum(bool((r['worker']or{}).get('transaction_completed'))for r in case['episodes']),
        'requested_inputs':sum(r['counts']['requested_inputs']for r in case['episodes']),
        'applied_inputs':sum(r['counts']['applied_inputs']for r in case['episodes']),
        'rejected_inputs':sum(r['counts']['rejected_inputs']for r in case['episodes'])}
    return case

def events_for(cases):
    trajectories={};parents={}
    for case in cases:
        if case.get('fork_parent')and case['life']:parents[case['life']]=case['fork_parent']
        if not case['life']or not case['episodes']:continue
        rows=trajectories.setdefault(case['life'],[])
        for episode in case['episodes']:
            env=episode['environment_before'];credit=episode['external_credit_auditor_only']
            identity=[env.get('law',env.get('domain')),env.get('created_at_tick',env.get('created_at_native_tick')),credit]
            if identity[1]is None:identity[1]='common_fixed_environment_no_explicit_reset'
            rows.append({'case':case['file'],'ordinal':episode['ordinal'],'tick':episode['start_tick'],'end_tick':episode['end_tick'],'origin_life':case['life'],
                'domain':episode['domain'],'environment_identity':identity,'external_credit':credit,
                'observations':episode['raw_observations'],'actuator':episode['actuator_mode'],
                'task_observations':episode['core_public_pair'] if episode['domain'].startswith('transaccion') and episode.get('phase_apparatus') else episode.get('task_observations',episode['raw_observations']),
                'feedback':episode['feedback'],'phase_visible':episode['phase_visible']})
    def collect(life,limit=None,seen=()):
        if life in seen:raise ValueError('Reference genealogy cycle')
        parent=parents.get(life);prefix=[]
        if parent and parent.get('life_id'):
            prefix=collect(parent['life_id'],parent['tick'],seen+(life,))
        own=[q for q in trajectories.get(life,[])if limit is None or q['end_tick']<=limit]
        return prefix+sorted(own,key=lambda r:r['tick'])
    return{life:[{**event,'evaluation_life':life}for event in collect(life)]for life in trajectories}

def main():
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--codigos',type=Path);p.add_argument('--salida',type=Path,required=True);p.add_argument('--sin-referencias',action='store_true');p.add_argument('--artefactos',type=Path);p.add_argument('--indice-artefactos',type=Path);args=p.parse_args()
    codigos=args.codigos or args.primarios/'codigo_ejecutado';args.salida.mkdir(parents=True,exist_ok=True)
    discrepancies=[];cases=[];identities=set();sources=[]
    paths=sorted(list(args.primarios.glob('*.json.gz'))+list(args.primarios.glob('*.json')))
    experimental_sources=[]
    for path in paths:
        if not re.match(r'^\d+[A-Za-z]*_',path.name):continue
        if path.name.startswith('00_'):continue # independently checked protected-state inventory, not an episode
        payload=read(path);case=summarize_file(path,payload,discrepancies);cases.append(case)
        if case['code_revision_sha256']:identities.add(case['code_revision_sha256'])
        sources.append({'file':path.name,'sha256':case['sha256'],'bytes':case['compressed_bytes']})
        if case['experimental_source_sha256']:
            digest=case['experimental_source_sha256'];basename=Path(payload['code_exact_path']).name
            source=args.primarios/'codigo_experimento'/digest/basename
            good=source.is_file()and sha(source)==digest
            experimental_sources.append({'primary':path.name,'source_member':'codigo_experimento/'+digest+'/'+basename,'sha256':digest,'byte_verified':good,
                'imported_system_bundle_link':'Experimental primary does not store imported system revision; use independent frozen-bundle execution record, not a retroactive edit.'})
            if not good:discrepancies.append({'kind':'experimental_source_missing_or_changed','primary':path.name})
    archives=[verify_archive(codigos,identity,discrepancies)for identity in sorted(identities)]
    continuity=[]
    for life in sorted({c['life']for c in cases if c['life']}):
        rows=sorted([(e,c['file'])for c in cases if c['life']==life for e in c['episodes']],key=lambda x:x[0]['start_tick'])
        edges=[]
        for(left,lf),(right,rf)in zip(rows,rows[1:]):
            edges.append({'from':lf+':'+str(left['ordinal']),'to':rf+':'+str(right['ordinal']),
                'same_tick':left['end_tick']==right['start_tick'],'own_equal':left['own_after']==right['own_before'],
                'context_equal':left['context_after']==right['context_before'],'B_private_equal':left['B_private_after']==right['B_private_before']})
        continuity.append({'life':life,'episodes':len(rows),'first_tick':None if not rows else rows[0][0]['start_tick'],'last_tick':None if not rows else rows[-1][0]['end_tick'],'edges':edges,
            'scope':'Witness-level continuity across recorded episodes; complete snapshot identity remains independently indexed, not inferred from equal loads.'})
    references={}
    if not args.sin_referencias:
        for life,events in events_for(cases).items():
            references[life]=evaluate(events)
            references[life]['initial_prior_scope']='UNMATCHED_LEGACY_PRIOR_12_FOR_DISTINCT_R10_T0_DO_NOT_INFER_FAIR_HISTORY_MATCHED_SUPERIORITY'if'R10'in life else'Frozen initial threshold12 at the common EO01 effective reference; campaign histories and exact branch prefixes then evolve independently.'
    artifacts={'status':'NOT_REQUESTED_RECEIPTS_AND_DETERMINISTIC_BYTES_ONLY'}
    if args.artefactos or args.indice_artefactos:
        if not(args.artefactos and args.indice_artefactos):raise ValueError('Both artifact directory and its index are required')
        index=read(args.indice_artefactos);checks=[]
        for row in index['rows']:
            member=row.get('export_member');check={'primary':row['primary'],'ordinal':row['ordinal'],'member':member}
            if member is None:check['status']='NOT_EXPORTED';discrepancies.append({'kind':'actual_artifact_missing_export',**check})
            else:
                path=(args.artefactos/member).resolve()
                if not path.is_relative_to(args.artefactos.resolve()):raise ValueError('Artifact outside package')
                good=path.is_file()and sha(path)==row['expected_sha256']and path.stat().st_size==row['expected_bytes']
                check['status']='BYTE_IDENTICAL'if good else'MISMATCH'
                if not good:discrepancies.append({'kind':'actual_artifact_mismatch',**check})
            checks.append(check)
        artifacts={'status':'EXPORTED_ACTUAL_BYTES_CHECKED','index_sha256':sha(args.indice_artefactos),'checks':checks}
    output={'schema':'EO02.archived_recalculation.v1','sources':sources,'code_archives':archives,'experimental_sources':experimental_sources,'cases':cases,
        'continuity':continuity,'discrepancies':discrepancies,'references':references,
        'units':'Episodes are repeated uses within one life; forks share an exact prefix. Neither ticks nor queries are independent learned organisms.',
        'new_native_ticks':0,'new_local_service_executions':0,'reference_revision':REFERENCE_REVISION,'actual_worker_artifacts':artifacts,
        'recalculation_source_sha256':sha(Path(__file__)),'frozen_policy_source_sha256':sha(Path(__file__).with_name('referencias_eo02.py')),
        'scope':'Primary-record output/arithmetic and deterministic worker-byte regeneration. Not native DEE replay or new local worker execution.'}
    target=args.salida/'RECALCULO_EO02.json';target.write_text(json.dumps(output,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    with(args.salida/'RESUMEN_CASOS.csv').open('w',newline='',encoding='utf8')as f:
        fields_=['file','life','attempts','valid','executed','useful','incorrect_executed','abstentions','actuator_annulled','completed_transactions','requested_inputs','applied_inputs','rejected_inputs']
        writer=csv.DictWriter(f,fieldnames=fields_);writer.writeheader()
        for case in cases:writer.writerow({'file':case['file'],'life':case['life'],**case['totals']})
    with(args.salida/'REFERENCIAS_POR_CASO.csv').open('w',newline='',encoding='utf8')as f:
        cols=['life','policy','seed','case','attempts','completed_steps','completed_transactions','first_action','first_completed_step']
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for life,group in references.items():
            for policy in group['results']:
                bycase={}
                for row in policy['rows']:
                    if not row['inherited_reference_prefix']:bycase.setdefault(row['case'],[]).append(row)
                for case,rows in bycase.items():writer.writerow({'life':life,'policy':policy['policy'],'seed':policy['seed'],'case':case,
                    'attempts':len(rows),'completed_steps':sum(r['completed_step']for r in rows),'completed_transactions':sum(r['completed_transaction']for r in rows),
                    'first_action':rows[0]['action'],'first_completed_step':rows[0]['completed_step']})
    with(args.salida/'PRIMER_USO_Y_RETENCION.csv').open('w',newline='',encoding='utf8')as f:
        cols=['file','life','domain','first_tick','first_action','first_useful','first_own','first_context','last_tick','last_own','last_context','attempts','useful','transactions']
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for case in cases:
            if not case['episodes']:continue
            first,last=case['episodes'][0],case['episodes'][-1]
            writer.writerow({'file':case['file'],'life':case['life'],'domain':first['domain'],'first_tick':first['start_tick'],
                'first_action':first['formed_native_command'],'first_useful':first['useful'],'first_own':json.dumps(first['own_before']),
                'first_context':json.dumps(first['context_before']),'last_tick':last['end_tick'],'last_own':json.dumps(last['own_after']),
                'last_context':json.dumps(last['context_after']),'attempts':case['totals']['attempts'],'useful':case['totals']['useful'],'transactions':case['totals']['completed_transactions']})
    print(json.dumps({'cases':len(cases),'episodes':sum(c['totals']['attempts']for c in cases),'code_archives':len(archives),'discrepancies':discrepancies,'output':str(target),'sha256':sha(target),'summary':[{'file':c['file'],'life':c['life'],**c['totals']}for c in cases if c['episodes']]},ensure_ascii=False))
    return bool(discrepancies)
if __name__=='__main__':raise SystemExit(main())
