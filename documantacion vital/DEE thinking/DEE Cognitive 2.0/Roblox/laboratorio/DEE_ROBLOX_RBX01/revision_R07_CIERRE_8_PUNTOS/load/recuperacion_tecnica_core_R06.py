"""Pure known-no-admission recovery; no Native import or file writes."""
import copy,hashlib,json
KEY='DEE.Cognitive.RBX01.async_native.INTEGRAL.V3.R01'
CODE='DEE.Cognitive.RBX01.CODE_SCOPE_INTEGRAL_V3'
SYSTEM='DEE.Cognitive.System.1.1.life.v1'
def need(v,m):
    if not v:raise ValueError(m)
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def repaired_entries(entries,original_m,current_code_scope):
    need(KEY in entries and CODE in entries,'EXISTING_NATIVE_EPISODE_REQUIRED')
    m=json.loads(entries[KEY]);expected=copy.deepcopy(original_m);expected['code_scope']=current_code_scope
    need(m==expected and entries[CODE]==canonical(current_code_scope),'EXACT_POST_LEASE_PENDING_STATE')
    need(m['phase']=='AWAIT_ROUTE_SENSOR'and m['uncertain']is True and m['cycles']==0 and m['last_sequence']==56,'ONLY_THREE_ORIGINAL_FAILED_Q2_GUARDS')
    need(m['failure']=={'type':'ValueError','tick':991543,'no_automatic_retry':True},'EXACT_TECHNICAL_FAILURE_FLAG')
    need('q2_reader'not in m['pending']and m['pending']['question_released']is True,'Q2_NOT_MATERIALLY_EXECUTED')
    new=copy.deepcopy(entries);after=copy.deepcopy(m);after['uncertain']=False
    # Keep failure as historical evidence; only the technical uncertainty bit
    # changes after the external receipt and static dominance proof.
    need({k:v for k,v in m.items()if k!='uncertain'}=={k:v for k,v in after.items()if k!='uncertain'},'NO_POLICY_PHASE_PENDING_RECEIPT_SEQUENCE_OR_HISTORY_CHANGE')
    new[KEY]=canonical(after)
    need({k:v for k,v in entries.items()if k!=KEY}=={k:v for k,v in new.items()if k!=KEY},'CODE_AND_ALL_ANCESTORS_LITERAL')
    return new,{'only_changed_own_field':'uncertain True -> False','failure_preserved':True,'phase_pending_receipts_sequence_cycles_policy_literal':True,
      'own_metadata_before_sha256':digest(m),'own_metadata_after_sha256':digest(after),'no_autonomous_repair_or_learning_claim':True}
def environment(proof):
    q1=proof['q1'];failed=proof['failed_q2_intent'];m=proof['own_metadata_preserved_from_failed_snapshot']
    need(q1['kind']=='decision'and q1['result']['action']=='ASK_STATION'and q1['result']['null']is False and q1['result']['nativeTick']==991543,'ACTUAL_ORIGINAL_ASK_ONLY')
    need(failed['kind']=='query_sensor'and failed['context']['session_id']==q1['context']['session_id'],'SAME_ORIGINAL_SESSION')
    original=failed['payload']['observation'];need(original['sensors']['permissionStock']==164 and m['pending']['initial_observation']['sensors']['permissionStock']==164,'EXACT_OMITTED_HOST_EFFECT')
    corrected=copy.deepcopy(original);corrected['sensors']['permissionStock']=163
    need({k:v for k,v in original['sensors'].items()if k!='permissionStock'}=={k:v for k,v in corrected['sensors'].items()if k!='permissionStock'},'ONLY_STOCK_CORRECTED')
    new_id=failed['context']['operation_id']+'_stockR06';need(len(new_id)<=96 and new_id!=failed['context']['operation_id'],'NEW_DECLARED_ID_FOR_CHANGED_PAYLOAD')
    return {'life':proof['life'],'profile':proof['profile'],'session_id':q1['context']['session_id'],'original_Q1':copy.deepcopy(q1),
      'failed_Q2_id':failed['context']['operation_id'],'failed_Q2_receipt_sha256':proof['failed_official_sha256'],
      'corrected_Q2_id':new_id,'corrected_Q2_observation':corrected,'sequence':58,'completed_new':0,'permission_stock':163,
      'transaction':{'from':164,'to':163,'cause':'Actual prior Native ASK omitted by host stock accounting','retrospective_timing_not_learning':True},
      'no_Q1_replay':True,'first_new_phase':'query_sensor','Native_requests_by_environment_correction':0}
def archive_ledger(old,proofs,utc):
    need(old['limit']==160000 and old['consumed']==10452,'EXACT_SHARED_DOSE')
    expected={p['life']:p['failed_q2_id']for p in proofs};need(set(old['intents'])==set(expected),'EXACT_THREE_FAILED_Q2_INTENTS')
    new=copy.deepcopy(old);records=[]
    for proof in proofs:
        life=proof['life'];identifier=expected[life];w=new['worlds'][life]
        need(new['intents'][life]['id']==identifier and w['consumed']==356 and w['reserved']==3740 and w['cycles']==0,'NO_OTHER_ADMISSION_OR_RESERVATION')
        records.append({'life':life,'id':identifier,'mode':'eci01-rbx01-query-sensor','status':'FAILED_PRESERVED_KNOWN_ZERO_ADMISSION',
          'before_tick':991543,'after_tick':991543,'actual_ticks':0,'external_execution_may_be_uncertain':False,
          'official_receipt_sha256':proof['failed_official_sha256'],'utc':utc,'original_intent':new['intents'].pop(life)})
    new['reconciled_failed_admissions']=[*old.get('reconciled_failed_admissions',[]),*records]
    need(new['worlds']==old['worlds']and new['consumed']==old['consumed']and new.get('last_completed')==old.get('last_completed'),'PRESERVE_CONSUMED_RESERVATIONS_CYCLES_AND_LAST_REAL_COMPLETION')
    for key in set(old)-{'intents','reconciled_failed_admissions'}:need(new[key]==old[key],'OTHER_LEDGER_FIELDS_LITERAL')
    return new,records
