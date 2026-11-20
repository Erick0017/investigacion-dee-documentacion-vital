"""Pure portable C verifier: two Native queries plus a declared host register.

Never aliases the outer C operation to one PI07 episode. Only frozen RAW,
reader and receipt primitives are reused; intervals/IDs are counted once.
Closed failures may retain a first-stage witness without a completed stage2.
"""
from pathlib import Path,PurePosixPath
from collections import Counter
import argparse,hashlib,importlib.util,json

VERSION='DEE.PI08.conditional_sensor_register_access.C.R02'
LITERAL_SHA='bbc81b6c01ca455ed961ae3cb53f29a6650374676ddc31df5f55af9a8a8b3470'
def require(ok,message):
    if not ok:raise ValueError(message)
def digest(data):return hashlib.sha256(data).hexdigest()
def local(root,name):
    require(isinstance(name,str)and name and'\\'not in name and':'not in name,'Portable relative file only')
    rel=PurePosixPath(name);require(not rel.is_absolute()and all(p not in('.','..')for p in rel.parts),'Escaping path')
    path=root.joinpath(*rel.parts).resolve(strict=True);require(path.is_relative_to(root),'File outside extraction')
    return path
def checked(root,entry):
    data=local(root,entry['file']).read_bytes();require(len(data)==entry['bytes']and digest(data)==entry['sha256'],'Indexed C bytes/hash changed');return data
def parser():
    here=Path(__file__).resolve().parent;choices=[here/'RECALCULAR_PRIMARIOS_PI07_LITERAL.py',here/'heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py']
    file=next((p for p in choices if p.is_file()),None);require(file is not None and digest(file.read_bytes())==LITERAL_SHA,'Frozen pure RAW/parser dependency required')
    spec=importlib.util.spec_from_file_location('PI08_C_literal_RAW_primitives',file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def result(primary):
    value=primary.get('result');value=json.loads(value)if isinstance(value,str)else value
    if value is None:return None
    rows=value.get('result',value).get('rows',[]);require(len(rows)==1,'One explicit C operation per primary');return rows[0]
def motor(choice):return None if choice is None else 1 if choice==1 else -1
def extra(obj):
    if int(obj['raw'])==0:return 0
    if int(obj['state'])>0 and int(obj['semantic'])==1:
        if list(obj['direction'])==[0,0,1]:return 1
        if list(obj['direction'])==[1,0,0]:return 0
    return None
def summary(requests,recorded,m):
    direct,aliases=m.receipts(requests);counts=Counter(r['status']for r in direct.values());rejected=sum(n for k,n in counts.items()if k.startswith('rejected'))
    require(recorded['unique_requested']==len(direct)and recorded['applied']==counts['applied'],'C direct receipt summary mismatch')
    # C outer/first rows use `rejected`; the unchanged inherited FI wrapper
    # uses `rejected_or_other`. Verify their actual declared contracts rather
    # than inventing an alias Native input or dropping the176 inner receipts.
    if 'rejected'in recorded:require(recorded['rejected']==rejected,'C rejected count differs')
    elif 'rejected_or_other'in recorded:require(recorded['rejected_or_other']==len(direct)-counts['applied'],'Inherited FI rejected_or_other count differs')
    else:raise ValueError('Unknown explicit Native receipt summary shape')
    return direct,counts,aliases
def reader(value,m):
    require(value['site']==[8,40,50],'Fixed inherited TC reader only');decoded=m.early_choice(value['observation']);require(decoded==value['choice'],'RAW TCchoice differs');return decoded
def witness(data,m):
    w=json.loads(data);require(w['schema']=='DEE.PI08.C.immediate_first_stage_witness.R03'and w['instrumentation_revision']=='R03','Immediate actual R03 witness required')
    require(w['new_Native_calls_for_witness']==0 and w['uses_existing_observations_and_receipts_only'],'Witness scope changed')
    q=w['query_tick'];require(w['observation_tick']==q+8 and w['reader']['tick']==q+4,'First-stage frozen windows changed')
    physical=m.observation(w['actual_preview_observation']);state=physical['state'];require(w['first_submitted_STATE']==state,'First Native input is actual STATE, not hidden direction/fixture')
    require(w['actual_preview_observation']['site']==[30,40,30]and int(w['actual_preview_observation']['tick'])==q-1,'First actual preview location/window changed')
    choice=reader(w['reader'],m);canonical=motor(choice);require(w['native_motor']==canonical,'FirstNative0/NULL/motor conflated')
    direct,counts,aliases=summary(w['requests'],w['Native_inputs'],m)
    query=w['question_request_before_final_receipt_lookup'];require((query is not None)==(canonical==1),'Question was not selected by Native+1')
    applied=False;status=None
    if query is not None:
        require(query['site']==[33,40,30]and query['direction']==[1,0,0]and query['payload']==0 and query['requested_tick']==q+7,'Fixed question port mapping changed')
        status=direct[query['id']]['status'];applied=status=='applied'
    observed=m.observation(w['question_observation']);signature=observed['state']>0 and observed['semantic']==1 and observed['direction']==[1,0,0]
    require(w['question_observation']['site']==[34,40,30]and int(w['question_observation']['tick'])==q+8,'Physical question-reader location/window changed')
    for channel in('PI07.TC.R01.query','PI07.TC.R01.support.plus','PI07.TC.R01.support.minus'):
        query_inputs=[r for r in w['requests']if r.get('channel')==channel]
        require(len(query_inputs)==1 and query_inputs[0]['requested_tick']==q and query_inputs[0]['payload']==0,'Three original material question1 inputs required')
    for item in w['requests']:
        if item.get('channel')=='PI07.TC.R01.datum':require(item['payload']==state and item['requested_tick']==q+3,'Question1 datum codec/tick changed')
    copies=[r for r in w['requests']if r.get('channel')in('PI07.TC.R01.copy.minus','PI07.TC.R01.copy.plus')]
    require(len(copies)==(canonical is not None),'First action-time efference missing/extra')
    if copies:require(copies[0]['actual_motor_choice']==canonical and copies[0]['requested_tick']==q+7,'First efference does not carry actual motor')
    require(not any(r.get('channel','').startswith('PI07.TC.R01.outcome.')for r in w['requests']),'No first generic reward/assignment was prepared')
    released=applied and signature;bit=extra(w['actual_preview_observation'])if released else 0
    valid_link=not(applied and not signature)and(not released or bit is not None)
    return{'ordinal':w['ordinal'],'query_tick':q,'observation_tick':w['observation_tick'],'before_tick':w['before_tick'],
       'actual_preview_STATE':state,'actual_preview_RAW':w['actual_preview_observation']['raw'],'actual_preview_direction':physical['direction'],
       'Native_choice':choice,'Native_selection_valid':choice is not None,'actual_motor':canonical,'question_scheduled':query is not None,
       'question_status':status,'question_applied':applied,'question_reader_signature':signature,'extra_released':released,'actual_extra_bit':bit,
       'physical_access_link_valid':valid_link,'Native_inputs':{'unique_requested':len(direct),'status_counts':dict(counts),'aliases_not_events':aliases}},direct
def stage2(row,expected_bit,protocol,ordinal,m,products):
    require(row['version']==VERSION and row['ordinal']==ordinal and row['environment_spec']==protocol['schedule'][ordinal],'Second-stage identity/environment differs')
    q=row['calendar']['query_tick'];cal=row['calendar']
    require(cal['seed_tick']==q+7 and cal['outcome_injection_tick']==q+408 and cal['collision_tick']==q+409 and cal['contact_tick']==q+410 and row['after_tick']==q+412,'Unchanged second6lapcalendar required')
    require(row['sensor']['site']==[52,48,47]and row['sensor']['tick']==q-1 and row['reader']['tick']==q+4,'Fixed actual secondsensor/reader windows changed')
    actual_sensor=m.observation(row['sensor']['observation']);require(row['sensor']['actual_state_datum']==actual_sensor['state'],'Actualsecondsensor incorrectly reported')
    require(row['sensor']['submitted_state_datum']==expected_bit,'Registered extra bit did not enter Nativequery2')
    choice=reader(row['reader'],m);canonical=motor(choice);require(row['native_motor']==row['actual_motor']==canonical and row['Native_selection_valid']is(choice is not None),'Secondaction chosen outside measuredNative')
    copies=[r for r in row['requests']if r.get('channel')in('PI07.TC.R01.copy.minus','PI07.TC.R01.copy.plus')]
    require(len(copies)==(canonical is not None),'Second efference count differs')
    if copies:require(copies[0]['actual_motor_choice']==canonical and copies[0]['requested_tick']==q+7,'Second action-time efference differs')
    datum=[r for r in row['requests']if r.get('channel')=='PI07.TC.R01.datum']
    require(len(datum)==1 and datum[0]['payload']==expected_bit and datum[0]['requested_tick']==q+3,'Registered actual bit did not enter fixed second Native datum port')
    require(row['operator_forced_action']is None and not row['actuator_ablation']and not row['sensor_ablation'],'No forced/cut response in prepared C')
    fi=row['FI'];early=m.early_choice(fi['legacy_result']['early_observation']);late=m.late_FI_choice(fi['legacy_result']['original_result']['native_trial']['reader'])
    require(early==fi['early_physical_choice']and late==fi['old_q6_choice']and fi['calendar']['query_tick']==q+192,'Fixed FI q+4/q+6 cannot be exchanged')
    fd,fc,fa=summary(fi['requests'],fi['Native_inputs'],m);require(len(fd)==176,'Historical internal FI176inputs required')
    message=row['message'];observed=m.observation(message['observation']);valid=observed['state']>0 and observed['semantic']==1 and observed['direction']==[1,0,0]
    payload=observed['s_reg']if valid else None;required=protocol['schedule'][ordinal]['message_payload'];status=m.request_status(message['request'])
    delivered=required is not None and status=='applied'and valid and payload==required
    require(message['site']==[54,48,56]and message['read_tick']==q+8 and message['actual_payload']==payload and message['delivered_exact']is delivered,'Actual message transport differs')
    pulse=row['actuator_request'];applied=m.request_status(pulse)=='applied'
    require(row['pulse_scheduled']is(pulse is not None)and row['pulse_applied']is applied,'Pulse request/admission conflated')
    for item,direction,wanted in[(pulse,[-1,0,0],0),(message['request'],[1,0,0],required)]:
        if item is not None:require(item['site']==[53,48,56]and item['direction']==direction and item['payload']==wanted and item['requested_tick']==q+7,'Fixed secondaction/message ports only')
    if message['artifact']:
        artifact=message['artifact'];require(artifact['bytes']==64 and artifact['sha256']in products and products[artifact['sha256']]==int(payload).to_bytes(8,'little')*8,'Actual Native64Bmessage content missing/different')
    failed=late!=1 or(required is not None and not delivered);require(row['actual_failed']is failed and row['returned_failed']is failed,'Outcome must use actual function, no expectedaction')
    direct,counts,aliases=summary(row['requests'],row['Native_inputs'],m)
    ret=[r for r in row['requests']if r.get('channel','').startswith('PI07.TC.R01.outcome.')]
    require(len(ret)==1 and ret[0]['actual_environment_failed']is failed and ret[0]['requested_tick']==q+408,'One generic actualoutcome only atsecondboundary')
    require(not any(k in ret[0]for k in('actual_motor_choice','route','bank','target')),'No hostassignment toearlieraction')
    for frame in row['return_frames']:
        for name in('A','B','hub'):m.observation(frame[name])
    return{'ordinal':ordinal,'before_tick':row['before_tick'],'after_tick':row['after_tick'],'query_tick':q,'Native_choice':choice,'Native_selection_valid':choice is not None,
       'actual_motor':canonical,'actual_second_sensor_STATE':actual_sensor['state'],'actually_submitted_extra_bit':expected_bit,
       'pulse_scheduled':pulse is not None,'pulse_applied':applied,'FI_q4':early,'FI_q6':late,'message_offered':required is not None,'message_delivered':delivered,
       'actual_failed':failed,'returned_failed':failed,'Native_inputs':{'unique_requested':len(direct),'status_counts':dict(counts),'aliases_not_events':aliases}},direct

def calculate(root,name):
    index=json.loads(local(root,name).read_bytes());require(index['schema']=='DEE.PI08.C.portable_primary_index.R03','Exact two-stage C index required')
    # Verify every declared member, including the seal and adverse/partial
    # phase summaries, even if a phase stopped before a complete C episode.
    verified={}
    def members(value):
        if isinstance(value,dict):
            if {'file','bytes','sha256'}<=set(value):
                data=checked(root,value);require(value['file']not in verified or verified[value['file']]==value['sha256'],'Conflicting indexed C alias')
                verified[value['file']]=value['sha256']
            for child in value.values():members(child)
        elif isinstance(value,list):
            for child in value:members(child)
    members(index)
    protocol=json.loads(checked(root,index['protocol']));require(protocol['schema']=='DEE.PI08.conditional_sensor_register_access.protocol.C.R02'and len(protocol['schedule'])==6,'Frozen scientific C6protocol required')
    if not index.get('fixture_MOCK_ONLY_NOT_NATIVE',False):
        require(index.get('seal')is not None,'Actual Native C bundle must include its original prospective source seal')
        seal=json.loads(checked(root,index['seal']));require(seal['protocol_sha256']==index['protocol']['sha256']and seal['life_id']==index['life_id'],'C prospective seal/protocol/life binding differs')
    m=parser();products={entry['sha256']:checked(root,entry)for entry in index.get('products',[])}
    witnesses={};witness_data={};witness_ids={}
    for entry in index.get('immediate_witnesses',[]):
        data=checked(root,entry);row,ids=witness(data,m);key=(row['ordinal'],row['query_tick']);require(key not in witnesses,'Duplicate immediate witness')
        witnesses[key]={**row,'file':entry['file'],'sha256':entry['sha256'],'bytes':entry['bytes']};witness_data[key]=json.loads(data);witness_ids[key]=ids
    preparation=None;allids={};intervals=[]
    if index.get('preparation_primary'):
        primary=json.loads(checked(root,index['preparation_primary']));row=result(primary)
        if row is not None:
            require(primary['status']=='completed'and row['version']==VERSION and row['new_native_ticks']==3,'Actual declared fixeddevicepreparation attempt differs')
            direct,counts,aliases=summary(row['requests'],row['Native_inputs'],m);require(len(direct)==1,'One declared legal sink birth attempt only')
            require(bool(row['ready'])is(counts['applied']==1 and row['Native_inputs']['all_terminal']),'Preparation readiness differs from actual Nativeadmission')
            request=row['requests'][0];require(request['site']==[36,40,30]and request['direction']==[0,0,0]and request['payload']==0 and request['requested_tick']==row['before_tick']+2,'No newTC/clock/inputoutsideprepareddevice')
            preparation={'attempt_completed':True,'ready':bool(row['ready']),'before_tick':row['before_tick'],'after_tick':row['after_tick'],'Native_inputs':len(direct),'status_counts':dict(counts)};allids.update(direct);intervals.append((row['before_tick'],row['after_tick']))
        else:preparation={'completed':False,'primary_status':primary['status'],'error':primary.get('error'),'no_preparation_result_claimed':True}
    completed=[];failed_primaries=[];used_witnesses=set()
    for entry in index.get('episode_primaries',[]):
        primary=json.loads(checked(root,entry));row=result(primary)
        if row is None:
            failed_primaries.append({'file':entry['file'],'status':primary['status'],'error':primary.get('error'),'complete_stage2_not_claimed':True});continue
        require(primary['status']=='completed'and row['version']==VERSION,'Only real C completed operation')
        ordinal=row['ordinal'];first=row['first_stage'];key=(ordinal,first['query_tick']);require(key in witnesses,'Immediate witness musttravelwithCprimary')
        w=witnesses[key];literal=witness_data[key];reg=first['sample_register'];pointer=row['external_immediate_first_stage_witness']
        require(pointer['sha256']==w['sha256']and pointer['bytes']==w['bytes']and first['external_immediate_witness']==pointer,'Immediate witness pointer differs')
        require(reg['actual_preview_observation']==literal['actual_preview_observation']and reg['first_submitted_STATE']==w['actual_preview_STATE'],'Actual register rewritten or expectedbit supplied')
        require(reg['question_applied_and_signature']is w['extra_released']and reg['question_applied']is w['question_applied'],'Question admission/signature altered')
        require(w['physical_access_link_valid']and w['actual_extra_bit']is not None,'A completed secondstage cannot hide NULL access/bit')
        require(reg['released_bit']==row['extra_bit_entered_second_TC']==w['actual_extra_bit'],'Conditional release bit differs')
        second,second_ids=stage2(row['second_stage'],w['actual_extra_bit'],protocol,ordinal,m,products)
        require(second['query_tick']>=w['query_tick']+782 and second['before_tick']==w['query_tick']+412,'Prepared normalized twostage order changed')
        require(row['before_tick']==w['before_tick']and row['after_tick']==second['after_tick']and row['after_tick']-row['before_tick']<=2099,'No overlappingintervaldoublecount or alteredfinitehorizon')
        union=dict(witness_ids[key]);require(not set(union).intersection(second_ids),'First/secondNativeID reused');union.update(second_ids)
        direct,counts,aliases=summary(row['requests'],row['Native_inputs'],m);require(direct==union,'Outer requestset must beexactfirst+second,deduplicated')
        require(not set(allids).intersection(direct),'PriorCinputs countedagain');allids.update(direct);used_witnesses.add(key)
        require(row['actual_failed']is second['actual_failed']and row['old_metadata_literal_unchanged']and row['no_first_trace_credit_claim'],'Actual consequence/parenthistory/attribution differs')
        completed.append({'ordinal':ordinal,'first':w,'second':second,'before_tick':row['before_tick'],'after_tick':row['after_tick'],
          'new_Native_ticks':row['after_tick']-row['before_tick'],'Native_inputs':{'unique_requested':len(direct),'status_counts':dict(counts)},
          'technical_register_is_external_not_Native_memory':True,'isolated_first_question_credit_proved':False})
        intervals.append((row['before_tick'],row['after_tick']))
    uncompleted=[]
    for key,w in witnesses.items():
        if key in used_witnesses:continue
        direct=witness_ids[key];require(not set(allids).intersection(direct),'Uncompleted witness IDs duplicated');allids.update(direct)
        uncompleted.append({**w,'second_stage_complete':False,'no_useful_outcome_or_full_horizon_claimed':True})
    completed.sort(key=lambda r:r['ordinal']);require([r['ordinal']for r in completed]==list(range(len(completed))),'Missing/repeatedcompleteCstage')
    for a,b in zip(sorted(intervals),sorted(intervals)[1:]):require(a[1]==b[0],'Unexplained age/exposure gap betweenCmaterialoperations')
    counts=Counter(r['status']for r in allids.values())
    return{'schema':'DEE.PI08.C.recalculated_two_stage_flow.R03','Native_executed':False,'DEE_imported':False,'integrity_passed':True,
       'fixture_MOCK_ONLY_NOT_NATIVE':bool(index.get('fixture_MOCK_ONLY_NOT_NATIVE',False)),
       'status':'SIX_COMPLETED_WITH_IMMEDIATE_WITNESSES'if len(completed)==6 else'PARTIAL_OR_BLOCKED_C_PRESERVED',
       'preparation':preparation,'opportunities_planned':6,'opportunities_completed':len(completed),'failed_primary_count':len(failed_primaries),
       'immediate_witnesses':len(witnesses),'uncompleted_first_stage_witnesses':uncompleted,'failed_primaries':failed_primaries,
       'questions_scheduled_completed':sum(r['first']['question_scheduled']for r in completed),'questions_applied_completed':sum(r['first']['question_applied']for r in completed),
       'extra_bits_released_completed':sum(r['first']['extra_released']for r in completed),'joint_useful_completed':sum(not r['second']['actual_failed']for r in completed),
       'first_Native_valid_completed':sum(r['first']['Native_selection_valid']for r in completed),'second_Native_valid_completed':sum(r['second']['Native_selection_valid']for r in completed),
       'completed_rows':completed,'Native_inputs_unique_observed':{'unique_requested':len(allids),'status_counts':dict(counts)},
       'completed_material_intervals':sorted(intervals),'observed_complete_interval_ticks':sum(b-a for a,b in intervals),
       'index_sha256':digest(local(root,name).read_bytes()),'protocol_sha256':index['protocol']['sha256'],'legacy_RAW_parser_sha256':LITERAL_SHA,
       'all_indexed_members_verified':len(verified),'indexed_member_sha256':verified,
       'limits':['One actual C world, no controlforcausalvalueofinformation.','Hostselects/serializes twostages and their distinctfixedactuators; Nativechooseswithinsteps, notanacquiredplan.','Extra dataisconditionalaccess toanactualregisteredRAWsample, notfreshoriginalworldmeasurementatrelease or Native memory.','Only secondtracehas theestablished6lapoutcome matching; firstquestioncreditnotisolated.','NoQuerymaterial0, measuredRAW0 and NULLremain distinct; aNULLaccesscannotbeclassifiedascompletedsecondNativeuse.','Partialwitness receiptsdonotbythemselvesaccountforpossiblelaterincompleteNativeadvancement; useRootcampaignledgerforsuchticks.']}

def main(args):
    root=Path(args.raiz).resolve(strict=True);out=Path(args.salida).absolute();require(not out.exists(),'New outputonly;preserveoldrecálculos')
    value=calculate(root,args.indice)
    with out.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'passed':True,'status':value['status'],'output':str(out),'sha256':digest(out.read_bytes()),'completed':value['opportunities_completed'],'immediate_witnesses':value['immediate_witnesses']},ensure_ascii=False))
if __name__=='__main__':
    parser_cli=argparse.ArgumentParser();parser_cli.add_argument('--raiz',required=True);parser_cli.add_argument('--indice',default='INDICE_C_PI08_R03.json');parser_cli.add_argument('--salida',required=True);main(parser_cli.parse_args())
