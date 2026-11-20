"""Read-only science evaluator of four CLOSED PI09 arms, stdlib only.

No Native/DEE/network/database access, no deployment or approval. Supply the
pure portable recalculation plus all four closed Root proofs explicitly.
The output may only be a NEW file in this PI09/fuentes directory.
"""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json

P=Path(__file__).resolve().parents[1]
ROLES=('native_real','always_real','never','always_desacoplado')
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(data):return hashlib.sha256(data).hexdigest()
def canon(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def load(path):
    path=Path(path).resolve(strict=True);require(not path.is_symlink(),'Literal frozen JSON only');data=path.read_bytes();return json.loads(data),{'path':str(path),'bytes':len(data),'sha256':sha(data)}
def raw_fields(obj):
    raw=int(obj['raw']);require(0<=raw<2**64,'Literal uint64 RAW');ds=[(raw>>s)&15 for s in(48,52,56)]
    fields={'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':raw>>60,'direction':[v-16 if v&8 else v for v in ds]}
    require(all(obj[k]==v for k,v in fields.items()),'RAW declaration mismatch')
    return {**fields,'raw':str(raw),'clock':int(obj['clock']),'tick':int(obj['tick']),'site':obj['site']}
def bank_fields(observations):
    require(len(observations)==2,'Two actually observed bank references required')
    a,b=(raw_fields(v)for v in observations)
    return {'A':a,'B':b,'A_minus_B':a['s_reg']-b['s_reg']}
def direct_requests(rows):
    unique={}
    for row in rows:
        for request in row['requests']:
            i=request['id'];receipt=request['receipt'];require(i==receipt['id'],'Request/receipt ID differs')
            if i in unique:require(unique[i]==request,'Cross-row Native request alias differs')
            unique[i]=request
    return sorted(unique.values(),key=lambda r:r['id'])
def request_value(request):
    # Keep Native argument order and boundary/receipt facts. Omit documentary
    # descriptions and transport IDs. Literal Native IDs are compared separately.
    physical={k:request[k]for k in('channel','port','payload','site','direction','state','semantic','declared_state','declared_semantic')if k in request}
    tick=request.get('requested_tick',request.get('tick'));require(type(tick)is int,'Actual Native boundary required')
    receipt=request['receipt'];return {'tick':tick,'physical':physical,'status':receipt['status'],'effective_tick':receipt.get('effective_tick')}
def prefix_before_second_datum(allrows,row):
    q=row['second_stage']['calendar']['query_tick'];end=q+3
    datum=[r for r in row['second_stage']['requests']if r.get('channel')=='PI07.TC.R01.datum'and r.get('requested_tick')==end]
    require(len(datum)==1,'Exactly one second Native datum at frozen q2+3')
    selected=[r for r in direct_requests(allrows)if r.get('requested_tick',r.get('tick'))<end]
    return {'boundary':end,'datum':datum[0],'physical_input_prefix':[request_value(r)for r in selected],'literal_Native_ids':[r['id']for r in selected],'attempts':len(selected)}
def first_content_disagreement(leftrows,rightrows):
    """Prospective first differing payload, never choose a favourable episode."""
    left={r['ordinal']:r for r in leftrows};right={r['ordinal']:r for r in rightrows}
    for i in range(12):
        if i not in left or i not in right:return {'status':'PENDING_MISSING_ORDINAL','ordinal':i,'causal_useful_witness':False}
        a,b=left[i],right[i];sa,sb=a['second_stage'],b['second_stage']
        da,db=sa['sensor']['submitted_state_datum'],sb['sensor']['submitted_state_datum']
        if da==db:continue
        pa,pb=prefix_before_second_datum(leftrows,a),prefix_before_second_datum(rightrows,b)
        qa,qb=a['first_stage']['query_tick'],b['first_stage']['query_tick'];q2a,q2b=sa['calendar']['query_tick'],sb['calendar']['query_tick']
        banksa,banksb=bank_fields(sa['reference_before']),bank_fields(sb['reference_before'])
        same_times=(a.get('before_prepared_wait',a['before_tick']),a['after_tick'],qa,q2a)==(b.get('before_prepared_wait',b['before_tick']),b['after_tick'],qb,q2b)
        same_prefix=pa['physical_input_prefix']==pb['physical_input_prefix']
        same_banks=banksa==banksb
        same_env=sa['environment_spec']==sb['environment_spec']
        same_questions=a['first_stage']['sample_register']['question_applied_and_signature']and b['first_stage']['sample_register']['question_applied_and_signature']
        changed_choice=sa['reader']['choice']!=sb['reader']['choice']
        changed_action=sa['actual_motor']!=sb['actual_motor']
        changed_use=sa['actual_failed']!=sb['actual_failed']
        return {'status':'FIRST_DIFFERENT_SUBMITTED_CONTENT','ordinal':i,'left_bit':da,'right_bit':db,'same_actual_calendars_and_age':same_times,'same_material_input_prefix_until_second_datum':same_prefix,'Native_input_attempts_before_difference':{'left':pa['attempts'],'right':pb['attempts']},'literal_Native_ids_equal':pa['literal_Native_ids']==pb['literal_Native_ids'],'same_observed_banks_before_second_query':same_banks,'same_public_environment':same_env,'both_material_queries_applied':bool(same_questions),'left_banks_before_second':banksa,'right_banks_before_second':banksb,'second_Native_choice_changed':changed_choice,'second_actual_action_changed':changed_action,'joint_actual_outcome_changed':changed_use,'left_useful':not sa['actual_failed'],'right_useful':not sb['actual_failed'],'causal_useful_witness':bool(same_times and same_prefix and same_banks and same_env and same_questions and changed_choice and changed_action and changed_use),'scope':'Local first-content contrast under declared equal physical input history. Native IDs retained for audit. No new reader, no retrospective favourable-case selection; later divergent histories are not treated as identical.'}
    return {'status':'NO_DIFFERENT_SUBMITTED_BIT_IN12','causal_useful_witness':False,'scope':'The fixed permutation did not separate received content; do not optimize it afterward.'}
def content_history_contrast(leftrows,rightrows,first,initial_physical_equal):
    """Whole fixed content intervention; later feedback is a mediator, not reset."""
    require(len(leftrows)==len(rightrows)==12,'Two complete material content histories required')
    schedules=[];beneficial=[];adverse=[]
    for a,b in zip(leftrows,rightrows):
        require(a['ordinal']==b['ordinal'],'Same declared environmental ordinal')
        sa,sb=a['second_stage'],b['second_stage'];qa,qb=a['first_stage']['question_request'],b['first_stage']['question_request']
        qschedule=lambda v:None if v is None else {k:v[k]for k in('site','direction','payload','requested_tick')}
        same=(a['first_stage']['query_tick']==b['first_stage']['query_tick']and sa['calendar']['query_tick']==sb['calendar']['query_tick']and sa['environment_spec']==sb['environment_spec']and qschedule(qa)==qschedule(qb)and a['query_control']==b['query_control']=='always'and a['information_control']=='real'and b['information_control']=='desynchronized')
        schedules.append(same)
        valid=sa['reader']['choice']is not None and sb['reader']['choice']is not None
        changed=valid and sa['actual_motor']!=sb['actual_motor']
        if changed and not sa['actual_failed']and sb['actual_failed']:beneficial.append(a['ordinal'])
        if changed and sa['actual_failed']and not sb['actual_failed']:adverse.append(a['ordinal'])
    matched_start=bool(initial_physical_equal and first.get('same_material_input_prefix_until_second_datum')and first.get('same_observed_banks_before_second_query')and first.get('same_actual_calendars_and_age'))
    return {'matched_initial_physical_state':bool(initial_physical_equal),'same_all12_declared_question_and_environment_schedules':all(schedules),'first_content_change_starts_from_matched_input_history':matched_start,'actual_real_content_benefit_ordinals':beneficial,'actual_real_content_adverse_ordinals':adverse,'causal_useful_history_witness':bool(matched_start and all(schedules)and beneficial),'negative_returns_equal':sum(r['second_stage']['returned_failed']for r in leftrows)==sum(r['second_stage']['returned_failed']for r in rightrows),'scope':'Prespecified material sequence intervention, including consequences and later shared-bank changes. A later benefit is not labelled an isolated instantaneous bit effect; every beneficial/adverse ordinal is listed. Does not establish superiority over Always, query-specific credit, or true-feedback advantage.'}
def actual_rows(proof):
    out=[]
    for record in proof['records']:
        for row in record.get('rows',[]):
            if 'first_stage'in row and'second_stage'in row:out.append((record,row))
    return out
def evaluate(criteria,recalculation,proofs,refs):
    require(criteria.get('schema')=='DEE.PI09.prospective.functional_criteria.R01','Prospective Root criteria required')
    require(recalculation.get('schema')=='DEE.PI09.consultation.recalculated_controlled_flow.R01'and recalculation.get('integrity_passed')is True and not recalculation.get('fixture_MOCK_ONLY_NOT_NATIVE',False)and recalculation.get('Native_executed')is False,'Actual nonmock documentary recalculation required')
    groups={};rawrows={};closures={};tables=[];initial_states={}
    for role in ROLES:
        proof=proofs[role]
        require(proof.get('schema')=='DEE.PI09.actual.finite_owner_plan.R01'and proof.get('status')=='CLOSED_FINITE_PHASE'and proof.get('closed')is True and proof.get('error')is None and proof.get('protected_before')==proof.get('protected_after'),'All four actual closed owner phases with protected principal required: '+role)
        rr=actual_rows(proof);require(len(rr)==12 and [r['ordinal']for _,r in rr]==list(range(12)),'Exactly12 consecutive actual opportunities per closed arm')
        group=[g for g in recalculation['groups']if g['arm']==role and g['life_id']==proof['life_id']and g['completed']==12]
        require(len(group)==1,'Unique recalculated arm/life group');group=group[0];version=group['version']
        recalculated={r['ordinal']:r for r in recalculation['rows']if r['arm']==role and r['life_id']==proof['life_id']and r['version']==version}
        for record,row in rr:require(recalculated[row['ordinal']]['primary_sha256']==record['sha256']and row['life_id']==proof['life_id']and row['version']==version,'Closed summary must match the hashed literal primary used by recalc')
        state=[row for record in proof['records']for row in record.get('rows',[])if record.get('label')=='STATE_AFTER'and row.get('present')]
        require(len(state)==1 and state[0]['progress']['ordinal']==12 and state[0]['progress']['ready']and not state[0]['progress']['uncertain']and not state[0]['progress']['pending'],'Final state must preserve closed actual progress12')
        require(state[0]['progress']['control']['arm']==role,'Actual admitted control role must match its closed proof')
        initial=[row for record in proof['records']for row in record.get('rows',[])if record.get('label')=='STATE_BEFORE']
        require(len(initial)==1 and proof['initial_tick']==884835,'Exact inherited C884835 initial boundary')
        initial_states[role]=initial[0]['physical']
        rawrows[role]=[row for _,row in rr];groups[role]=group;closures[role]={'closed':True,'life_id':proof['life_id'],'version':version,'initial_tick':proof['initial_tick'],'final_tick':proof['final_tick'],'Native_ticks':proof['new_Native_ticks'],'summary_sha256':refs[role]['sha256']}
        detailed=[]
        for row in rawrows[role]:
            s=row['second_stage'];before=bank_fields(s['reference_before']);last=s['return_frames'][-1];after=bank_fields([last['A'],last['B']])
            detailed.append({'ordinal':row['ordinal'],'before_second':before,'after_second_return':after,'observed_bank_difference_change':after['A_minus_B']-before['A_minus_B'],'actual_failed':s['actual_failed'],'returned_failed':s['returned_failed'],'first_native_choice':row['first_stage']['reader']['choice'],'first_actual_query_motor':row['first_stage']['actual_query_motor'],'q1':row['first_stage']['query_tick'],'q2':s['calendar']['query_tick'],'q2_minus_q1':s['calendar']['query_tick']-row['first_stage']['query_tick'],'q1_phase67_391_782':[row['first_stage']['query_tick']%n for n in(67,391,782)],'q2_phase67_391_782':[s['calendar']['query_tick']%n for n in(67,391,782)]})
            reg=row['first_stage']['sample_register'];queried=reg['question_applied_and_signature'];q1=row['first_stage']['query_tick'];q2=s['calendar']['query_tick']
            detailed[-1]['technical_register']={'sample_tick':reg['sample_tick'],'release_tick':reg['release_tick']if queried else None,'second_datum_tick':q2+3,'sample_age_at_release':reg['release_tick']-reg['sample_tick']if queried else None,'sample_age_at_second_input':q2+3-reg['sample_tick']if queried else None,'released_from_technical_memory_not_fresh_observation':bool(queried),'no_query_material0_not_observation':not queried}
        tables.append({'arm':role,'life_id':proof['life_id'],'useful':group['useful'],'opportunities':12,'reserved_useful':group['reserved_useful'],'reserved_opportunities':6,'Native_first_valid':group['Native_first_valid'],'questions_scheduled':group['questions_scheduled'],'questions_applied':group['questions_applied'],'no_query_actual_motors':sum(r['first_stage']['actual_query_motor']in(-1,0)for r in rawrows[role]),'first_NULL_not_abstention':sum(r['first_stage']['reader']['choice']is None for r in rawrows[role]),'extra_bits_released':group['extra_bits_released'],'Native_ticks_complete_phase':proof['new_Native_ticks'],'Native_inputs_unique':group['Native_inputs_unique'],'Native_status_counts':group['Native_status_counts'],'marginal_material_query_births':group['questions_scheduled'],'actual_failed_count':sum(r['second_stage']['actual_failed']for r in rawrows[role]),'returned_failed_count':sum(r['second_stage']['returned_failed']for r in rawrows[role]),'messages_offered':sum(r['second_stage']['message']['required_payload']is not None for r in rawrows[role]),'messages_delivered':sum(r['second_stage']['message']['delivered_exact']for r in rawrows[role]),'FI_q4_choices':[r['second_stage']['FI']['early_physical_choice']for r in rawrows[role]],'FI_q6_choices':[r['second_stage']['FI']['old_q6_choice']for r in rawrows[role]],'bank_and_phase_trace':detailed})
    native_rows=[r for r in recalculation['rows']if r['arm']=='native_real'and r['life_id']==proofs['native_real']['life_id']]
    informed=[r for r in native_rows if r['first']['question_applied']and r['first']['extra_released']]
    useful_informed=[r for r in informed if r['second']['Native_selection_valid']and r['joint_useful']]
    codes={tuple(r['first']['actual_direction'])for r in informed};actions={r['second']['actual_motor']for r in informed if r['second']['Native_selection_valid']}
    floor=groups['native_real']['useful']>=8 and groups['native_real']['reserved_useful']>=4
    bounded=len(informed)>=2 and bool(useful_informed)and {(0,0,1),(1,0,0)}<=codes and {-1,1}<=actions
    content=first_content_disagreement(rawrows['always_real'],rawrows['always_desacoplado'])
    history=content_history_contrast(rawrows['always_real'],rawrows['always_desacoplado'],content,initial_states['always_real']==initial_states['always_desacoplado'])
    gates={'four_closed_arms':{'result':True,'criterion':'Four complete isolated material histories,12 each, finalprogress12 and primary hashes verified'},'candidate_floor':{'result':floor,'criterion':'At least8/12 jointly useful and4/6 reserved','actual':{'useful':groups['native_real']['useful'],'reserved':groups['native_real']['reserved_useful']}},'bounded_Native_access':{'result':bounded,'criterion':'At least2applied questions, both actual physical direction codes, distinct valid second actions and actual useful informed use','actual':{'applied_informed_uses':len(informed),'useful_informed_uses':len(useful_informed),'physical_codes':[list(v)for v in sorted(codes)],'actual_second_actions':sorted(actions)}},'causal_content_witness':{'result':bool(content['causal_useful_witness']or history['causal_useful_history_witness']),'criterion':'Prespecified material content contrast changes a Native action and actual useful outcome, separating instantaneous local effect from mediated history','actual':{'first_content_local':content,'fixed_content_history':history}},'conservation_panel':{'result':None,'status':'PENDING_SEPARATE_ACTUAL_PANEL','criterion':criteria['core']['minimum_previous_function']},'save_reopen':{'result':None,'status':'PENDING_ACTUAL_ZERO_ADVANCE_REOPEN','criterion':'Complete coherent state and actual save/reopen without false history'},'decisive_material_reproduction':{'result':None,'status':'PENDING_NEW_ACTUAL_RP_REPLAY','criterion':'Reproduction of decisive new adopted mechanism from complete isolated prefix'}}
    return {'schema':'DEE.PI09.consultation.compact_actual_criteria_evaluation.R01','Native_executed_by_evaluation':False,'DEE_imported':False,'approval':False,'adoption_not_performed':True,'source_evidence':refs,'closures':closures,'initial_physical_states_equal':all(v==initial_states['native_real']for v in initial_states.values()),'gates':gates,'new_access_evidence_sufficient_for_root_review':all(gates[k]['result']is True for k in('four_closed_arms','candidate_floor','bounded_Native_access','causal_content_witness')),'all_adoption_gates_met':False,'material_comparison_table':tables,'first_content_disagreement':content,'fixed_content_history_contrast':history,'learned_query_value':{'isolated':False,'reason':'One shared bank; established generic return is second stage only. Changed query1 may follow shared-bank history; no separate query credit.'},'interpretive_limits':['Always may be optimal in this finite domain; no superiority condition is imposed.','Ticks, births, useful FI/messages and input statuses remain separate quantities, not an invented energy score.','Nominal waits are not effective phase differences; actual clocks/calendars are reported.','The first content comparison is chosen by ordinal/payload disagreement, not by favourable outcome.','Later histories can diverge after different consequences. Aggregate score differences do not isolate instantaneous content or true-contingency advantage.','No counterfactual utility is computed from unexecuted actions; all utility counts refer to material branches.']}
def main(a):
    criteria,cref=load(a.criterios);recalc,rref=load(a.recalculo);proofs={};refs={'criteria':cref,'recalculation':rref}
    for role in ROLES:proofs[role],refs[role]=load(getattr(a,role))
    result=evaluate(criteria,recalc,proofs,refs);out=Path(a.salida).absolute();require(out.parent==Path(__file__).resolve().parent and not out.exists(),'New output in PI09/fuentes only')
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(out),'sha256':sha(out.read_bytes()),'new_access_evidence_sufficient_for_root_review':result['new_access_evidence_sufficient_for_root_review'],'adoption_gates_pending':True,'approval':False}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--criterios',default=str(P/'codigo/CRITERIOS_PI09_R01.json'));ap.add_argument('--recalculo',required=True)
    for flag in ROLES:ap.add_argument('--'+flag.replace('_','-'),dest=flag,required=True)
    ap.add_argument('--salida',required=True);main(ap.parse_args())
