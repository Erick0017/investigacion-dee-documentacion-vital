"""Portable passive FI/admission recálculo B_R02 with completed SHAM2, no DEE, no ticks, stdlib only.

Reads completed/failed captures, not summaries as the primary evidence. Shares
the exact pure RAW/receipt parser from RECALCULAR_PI02.py. Global Native snapshot
equivalence is identified as a previously executed passive control unless the
immutable snapshots are separately exported; local paths never become inputs
to the portable mode. A prepared closed valve is never scored as learned.
"""
from pathlib import Path
import argparse, collections, datetime, hashlib, importlib.util, json, shutil, sys

def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def descriptor(path):
    b=path.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
def base_library():
    path=Path(__file__).with_name('RECALCULAR_PI02.py')
    if not path.is_file(): raise ValueError('Required shared stdlib verifier is absent')
    spec=importlib.util.spec_from_file_location('pi02_pure_documentary_library',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    if any(name.startswith('dee_thinking') for name in sys.modules):raise RuntimeError('Unexpected DEE import')
    return module,path

def local_index(root):
    captures=[]
    for arm in ('SYNC','ASYNC','ACTIVE','GUARDED','SHAM2'):
        for case in range(3):
            path=root/'ensayos'/f'PI02_R03_FI_{arm}_{case:02d}.json'
            if not path.is_file():raise FileNotFoundError(path)
            captures.append({'file':path.relative_to(root).as_posix(),'kind':'FI_R03','arm':arm,'case':case,**descriptor(path)})
    for case in range(3):
        path=root/'ensayos'/f'PI02_R03_MAIN_ACCESS_{case:02d}.json'
        if not path.is_file():raise FileNotFoundError(path)
        captures.append({'file':path.relative_to(root).as_posix(),'kind':'FI_R03','arm':'MAIN_RECOVERY','case':case,**descriptor(path)})
    failed=root/'ensayos/PI02_R03_FI_SHAM_00.json'
    if failed.is_file():captures.append({'file':failed.relative_to(root).as_posix(),'kind':'FI_R03_FAILED','arm':'SHAM_FAILED','case':0,**descriptor(failed)})
    result={'schema':'PI02.B.portable.index.R02','captures':captures}
    proof=root/'control/COMPARACION_FI_ASYNC_R03.json'
    if proof.is_file():result['prior_equivalence']={'file':proof.relative_to(root).as_posix(),**descriptor(proof)}
    return result

def captured(meta,outer,base):
    errors=[]
    if outer.get('status')=='failed_preserved':
        error=json.loads(outer['error'])if isinstance(outer['error'],str)else outer['error']
        state=error.get('failed_native_future_preserved',{})
        return {'arm':meta['arm'],'case':meta['case'],'id':outer['id'],'status':'failed_preserved','scored':False,
                'error_type':error.get('type'),'error_detail':error.get('detail'),'tick_after_attempt':error.get('native_tick_after_attempt'),
                'preserved_physical':state.get('physical'),'preserved_snapshot_localizer':state.get('snapshot'),
                'preserved_snapshot_sha256':state.get('snapshot_sha256'),'no_retry_or_rollback':error.get('no_retry_or_rollback'),
                'interpretation':'Technical interface contract failure before Native advancement; not a biological/cognitive failure and not a performed sham.'},errors,[]
    payload,result,value=base.unwrap(outer)
    literal=payload['situaciones'][0]
    if value['condition']!=literal:errors.append('Literal/result condition mismatch')
    if set(literal)!={'modo','izquierda','derecha','asincrono','ruido'}:errors.append('Unexpected semantic input fields')
    if literal['modo']!='eci01-pi02-fi-prueba':errors.append('Unexpected FI operation')
    left,right=literal['izquierda'],literal['derecha']
    if any(type(x)is not int or not 0<=x<=20 for x in (left,right)):errors.append('Invalid independent public loads')
    trial=value['native_trial']
    frame=trial if 'raw_components'in trial else trial['original_result']['native_trial']
    components=[0]*128;components[0]=left;components[1]=20-right
    if frame['raw_components']!=components:errors.append('Fixed independent-operand codec differs')
    observation=value['early_observation'];fields,observation_errors=base.observation(observation);errors+=observation_errors
    decoded=base.fi_sign(observation['raw'])
    if decoded!=value['early_physical_choice'] or (decoded is not None and type(value['early_physical_choice'])is not int):errors.append('Fixed q4 decoder differs')
    if tuple(observation['site'])!=(15,15,15):errors.append('Different FI physical reader')
    q=frame['query_tick']
    if value['early_tick']!=q+4 or frame['read_tick']!=q+6 or value['after']['tick']!=q+8+2*67:errors.append('Fixed FI horizons differ')
    if frame['reader']['choice']!=value['legacy_q6_choice']:errors.append('q6 alias differs')
    canonical=list(value['all_FI_receipts'])+list(value['noise_requests'])
    unique,counts=base.canonical_receipts(canonical)
    if counts['aliases_not_counted']!=0:errors.append('Duplicated alias in canonical FI material list')
    expected_counts=value.get('denominators')
    if expected_counts is not None:
        for key,real in (('requested',counts['requested_unique']),('applied',counts['applied']),('rejected',counts['rejected'])):
            if expected_counts[key]!=real:errors.append('Reported denominator differs:'+key)
        if expected_counts['other_statuses']or counts['pending_or_other']:errors.append('Pending/other FI receipts at terminal horizon')
    rejected=[]
    for item in canonical:
        receipt=item['receipt']
        if str(receipt['status']).startswith('rejected'):
            rejected.append({'id':receipt['id'],'port':item.get('port'),'payload':item.get('payload'),'status':receipt['status'],'requested_tick':receipt['requested_tick'],'effective_tick':receipt.get('effective_tick'),'reason':receipt.get('reason')})
    noise=value.get('noise_admission');noise_receipts=[]
    if noise is not None:
        if noise['condition']!=literal['ruido']:errors.append('Noise condition differs')
        prepared={item['name']:item['state']for item in noise.get('apparatus',[])}
        if prepared!={'PI02.R03.FI.noise.raw0':1,'PI02.R03.FI.noise.sham':600001}:errors.append('Frozen active/sham prepared state fields differ from protocol')
        for apparatus in noise.get('apparatus',[]):
            _,problems=base.observation(apparatus['pre_observation']);errors+=problems
        if meta['arm']=='SHAM2' and literal['ruido']!='sham':errors.append('SHAM2 must be an actually requested sham condition')
        for item in noise['final_receipts']:
            receipt=item['receipt']
            canonical_item=unique.get(base.exact(receipt['id']))
            if canonical_item is None or canonical_item['receipt']!=receipt:errors.append('Noise receipt differs from canonical material list')
            noise_receipts.append({'id':receipt['id'],'port':item.get('port'),'payload':item.get('payload'),'status':receipt['status'],'requested_tick':receipt['requested_tick'],'effective_tick':receipt.get('effective_tick'),'reason':receipt.get('reason')})
        if noise['request']is not None:
            if noise['request']['tick']!=noise['scheduled_submit_tick']:errors.append('Noise request phase differs')
            original=next((x for x in value['all_FI_receipts']if x['id']==noise['raw0_frame_request_id']),None)
            if original is None or original['tick']!=noise['scheduled_submit_tick']:errors.append('Interference not simultaneous with recorded raw0')
    # This evaluator calculation is not passed to the Native reader or bridge.
    expected=(left>right)-(left<right)
    before=value['before'];after=value['after']
    if before['N']!=67 or after['N']!=67:errors.append('Changed Native dimension')
    if result['after_tick']!=after['tick']:errors.append('Outer Native endpoint differs')
    if sha(outer['payload'].encode('utf-8'))!=outer['payload_sha']:errors.append('Captured literal payload hash differs')
    row={'arm':meta['arm'],'case':meta['case'],'id':outer['id'],'status':outer['status'],'scored':True,'public_loads':[left,right],
         'condition':literal,'before':before,'after':after,
         'noise_prepared_states':{item['name']:item['state']for item in noise.get('apparatus',[])}if noise is not None else {},
         'noise_requested_events':noise.get('requested_noise_events')if noise is not None else 0,
         'noise_load_per_requested_event':noise.get('load_per_requested_event')if noise is not None else None,
         'noise_dose_limit':noise.get('dose_limit')if noise is not None else None,
         'decoded_q4':decoded,'q4_tick':q+4,'observation_q4':observation,
         'legacy_q6':value['legacy_q6_choice'],'reference_sign_auditor_only':expected,'correct_sign':decoded is not None and decoded==expected,
         'denominators':counts,'rejected_material_requests':rejected,'noise_receipts':noise_receipts,'frame':frame,
         'prepared_closed_valve':noise is not None and noise.get('guarded_is_prepared_closed_valve',False),
         'source_witness':value['source'],'no_resource_actuation_in_this_diagnostic':value['no_resource_actuation_or_target_evaluation'],
         'clock_raw_zero_NULL_are_distinct':True}
    return row,errors,list(unique)

def run(root,out,export_to=None):
    root=root.resolve();out=out.resolve();base,base_path=base_library()
    index_path=root/'EVIDENCIA/INDICE_PI02_B_R02.json'
    index=read(index_path)if index_path.is_file()else local_index(root)
    if index.get('schema')!='PI02.B.portable.index.R02':raise ValueError('B_R02 index schema required')
    expected={(arm,case)for arm in ('SYNC','ASYNC','ACTIVE','GUARDED','SHAM2','MAIN_RECOVERY')for case in range(3)}|{('SHAM_FAILED',0)}
    actual=[(meta['arm'],meta['case'])for meta in index['captures']]
    if set(actual)!=expected or len(actual)!=len(expected):raise ValueError('B_R02 requires all18completed captures and preserved failed SHAM exactly once')
    rows=[];provenance=[];errors=[];ids=collections.defaultdict(list)
    for meta in index['captures']:
        path=base.safe_file(root,meta['file']);before=descriptor(path)
        if any(before[k]!=meta[k]for k in ('bytes','sha256')):raise ValueError('Indexed primary differs:'+meta['file'])
        outer=read(path);row,problems,native_ids=captured(meta,outer,base)
        row['primary_file']=meta['file'];row['primary_sha256']=before['sha256'];rows.append(row)
        errors.extend(row['id']+': '+error for error in problems);ids[meta['arm']]+=native_ids
        if descriptor(path)!=before:raise ValueError('Concurrent primary change detected')
        provenance.append({'file':meta['file'],**before})
    for arm,identifiers in ids.items():
        if len(identifiers)!=len(set(identifiers)):errors.append('Canonical Native IDs reused across same-arm operations:'+arm)
    byarm={arm:[row for row in rows if row['arm']==arm and row['scored']]for arm in ids if any(row["arm"]==arm and row["scored"]for row in rows)}
    pairs=[]
    keys=('kind','version','level','raw_components','input_tick','all_components_same_tick','datum_tick','query_tick','read_tick','timing','reader','before','after','datum_pre','datum_after','references_pre','references_after','requests','frames','minimum_passive_horizon_ticks')
    for case in range(3):
        a=next(row for row in byarm['SYNC']if row['case']==case);b=next(row for row in byarm['ASYNC']if row['case']==case)
        equality={key:a['frame'].get(key)==b['frame'].get(key)for key in keys}
        current={'case':case,'public_loads':a['public_loads'],'same_before_physical':a['before']==b['before'],'same_after_physical':a['after']==b['after'],'same_q4_RAW_clock':a['observation_q4']==b['observation_q4'],'frame_equalities':equality}
        pairs.append(current)
        if not all(equality.values())or not all(current[k]for k in ('same_before_physical','same_after_physical','same_q4_RAW_clock')):errors.append('Captured synchronous/asynchronous mismatch:'+str(case))
    totals={}
    for arm,group in byarm.items():
        for i in range(1,len(group)):
            if group[i]['before']!=group[i-1]['after']:errors.append('Sequential physical history interrupted:'+arm)
        totals[arm]={'operations':len(group),'valid_q4':sum(row['decoded_q4']is not None for row in group),'correct_sign':sum(row['correct_sign']for row in group),'q4':[row['decoded_q4']for row in group],
                     **{key:sum(row['denominators'][key]for row in group)for key in ('requested_unique','applied','rejected','pending_or_other')},
                     'initial_tick':group[0]['before']['tick'],'final_tick':group[-1]['after']['tick']}
    global_proof=None
    if 'prior_equivalence'in index:
        meta=index['prior_equivalence'];path=base.safe_file(root,meta['file']);info=descriptor(path)
        if any(info[k]!=meta[k]for k in ('bytes','sha256')):raise ValueError('Prior global proof changed')
        prior=read(path)
        if prior['inconsistencies']or not prior['bounded_technical_equivalence_supported']:errors.append('Prior global equivalence not supported')
        global_proof={'file':meta['file'],**info,'previous_local_snapshot_recalculation_report':True,'snapshot_bytes_newly_recalculated_by_this_portable_run':False,'local_snapshot_final_comparison':prior['final_closed_comparison'],'limit':'Snapshot files are local locators, not silently accessed by the portable calculation. Captured port/frame/receipts are independently recalculated above.'}
    # Avoid claiming that a rejected perturbing pulse entered the physical world.
    active=[row for row in rows if row['scored']and row['condition']['ruido']=='active']
    active_noise_statuses=collections.Counter(receipt['status']for row in active for receipt in row['noise_receipts'])
    sham=[row for row in rows if row['scored']and row['condition']['ruido']=='sham']
    sham_noise_statuses=collections.Counter(receipt['status']for row in sham for receipt in row['noise_receipts'])
    noise_contrast={'active_prepared_state':1,'sham_prepared_state':600001,
                    'active_requested_noise_events':sum(row['noise_requested_events']for row in active),
                    'sham_requested_noise_events':sum(row['noise_requested_events']for row in sham),
                    'active_noise_statuses':dict(active_noise_statuses),'sham_noise_statuses':dict(sham_noise_statuses),
                    'limit':'Same requested payload7 and scheduling convention do not equal material dose: prepared state1 versus600001, different sites/directions and admitted/rejected receipts differ. No fully dose-matched sham is claimed.'}
    for row in rows:row.pop('frame',None)
    result={'schema':'PI02.B.passive_recalculation.R02','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_imports':0,'new_ticks':0,
            'code':descriptor(Path(__file__)),'shared_stdlib_verifier':descriptor(base_path),'primaries':provenance,'rows':rows,'totals':totals,'SYNC_ASYNC_captured_equivalence':pairs,'prior_global_snapshot_proof':global_proof,
            'active_noise_receipt_statuses_across_independent_arm_and_MAIN':dict(active_noise_statuses),
            'sham_noise_receipt_statuses':dict(sham_noise_statuses),'noise_contrast_and_dose_limit':noise_contrast,'inconsistencies':errors,
            'interpretation':['FI q4 material zero is a valid answer; q6 NULL is a different observation.','Asynchronous extraction equality is an instrument result for these three sequential cases, not newly acquired cognition.','ACTIVE tests simultaneous admission competition. Rejected noise is not a physically admitted load7 carrier.','GUARDED is an externally prepared closed valve and does not demonstrate learned regulation.','MAIN removal of the external interference and later valid FI readings is access recovery without re-teaching, not autonomous protection.','Failed original SHAM is a preserved technical failure, not an executed sham. Completed SHAM2 is a separate later branch, never a replacement or retry of that failed future.','SHAM2 requests payload7 through its separately prepared state600001 interface; ACTIVE uses state1. This is not a fully dose-matched control.','Shared-prefix branches and sequential queries are not independent acquisitions.'],
            'not_certified':['Acquired regulation, anticipatory usefulness, warning learning, final retention/adoption, independent replication, new Native reproduction.']}
    if any(name.startswith('dee_thinking')for name in sys.modules):raise RuntimeError('DEE import in passive verifier')
    out.mkdir(parents=True,exist_ok=True);target=out/'RECALCULO_PI02_B_R02.json'
    if target.exists():raise ValueError('Existing output protected; select a new output directory')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if export_to is not None:
        destination=export_to.resolve();destindex={'schema':'PI02.B.portable.index.R02','captures':[]}
        for meta in index['captures']:
            source=base.safe_file(root,meta['file']);name='EVIDENCIA/PRIMARIOS_B/'+source.name;dest=destination/name;dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists()and descriptor(dest)!=descriptor(source):raise ValueError('Different archived primary protected')
            if not dest.exists():shutil.copyfile(source,dest)
            destindex['captures'].append({**meta,'file':name,'source_localizer_at_export':str(source)})
        if 'prior_equivalence'in index:
            meta=index['prior_equivalence'];source=base.safe_file(root,meta['file']);name='EVIDENCIA/CONTROL_B/'+source.name;dest=destination/name;dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():shutil.copyfile(source,dest)
            elif descriptor(dest)!=descriptor(source):raise ValueError('Different equivalence proof protected')
            destindex['prior_equivalence']={**meta,'file':name}
        dest=destination/'EVIDENCIA/INDICE_PI02_B_R02.json';dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():raise ValueError('Prior B_R02 index protected')
        dest.write_text(json.dumps(destindex,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        codepath=destination/'RECALCULO/RECALCULAR_PI02_B_R02.py';codepath.parent.mkdir(parents=True,exist_ok=True)
        if codepath.exists():raise ValueError('Prior B_R02 exported code protected')
        shutil.copyfile(Path(__file__),codepath)
        shared=destination/'RECALCULO/RECALCULAR_PI02.py'
        if not shared.exists():shutil.copyfile(base_path,shared)
        elif descriptor(shared)!=descriptor(base_path):raise ValueError('Exported shared verifier differs')
    print(json.dumps({'out':str(target),'totals':totals,'active_noise_statuses':dict(active_noise_statuses),'sham_noise_statuses':dict(sham_noise_statuses),'inconsistencies':errors,'new_ticks':0},ensure_ascii=False,indent=2))
    return 0 if not errors else 2

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--out-dir',type=Path,required=True);parser.add_argument('--export-to',type=Path)
    args=parser.parse_args();raise SystemExit(run(args.root,args.out_dir,args.export_to))
