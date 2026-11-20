"""Standalone stdlib B primary/causal comparator. Native0 and no originals.

Paths are resolved ONLY below --raiz. Recorded source-reference paths are never
opened. Includes partial closed episodes without declaring an arm completed.
The preserved PI07 parser is reused through one explicit geometry alias; actual
B roles, selection/reference action, returns and protocol are checked here.
"""
from pathlib import Path, PurePosixPath
from collections import Counter, defaultdict
import argparse, copy, hashlib, importlib.util, json

VERSION='DEE.PI08.successive_contextual_regulation.B.R01'
R03='DEE.PI07.acquired_regulation.perpendicular_environment.R03'
LITERAL_SHA='bbc81b6c01ca455ed961ae3cb53f29a6650374676ddc31df5f55af9a8a8b3470'
ROLES=('real','none','yoked','reference')

def require(ok,message):
    if not ok:raise ValueError(message)
def digest(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def local(root,value):
    require(isinstance(value,str)and value and'\\'not in value and':'not in value,'Portable relative path only')
    rel=PurePosixPath(value);require(not rel.is_absolute()and all(p not in('.','..')for p in rel.parts),'Escaping relative path')
    path=root.joinpath(*rel.parts).resolve(strict=True);require(path.is_relative_to(root),'Source outside extraction')
    for node in(path,*path.parents):
        if node==root.parent:break
        require(not node.is_symlink()and not(getattr(node.lstat(),'st_file_attributes',0)&1024),'No linked member')
    return path
def checked(root,entry):
    path=local(root,entry['file']);data=path.read_bytes()
    require(len(data)==entry['bytes']and digest(data)==entry['sha256'],'Indexed bytes/hash changed: '+entry['file'])
    return data
def legacy():
    here=Path(__file__).resolve().parent
    choices=[here/'RECALCULAR_PRIMARIOS_PI07_LITERAL.py',here/'heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py']
    file=next((p for p in choices if p.is_file()),None);require(file is not None,'Preserved stdlib PI07 parser must travel beside this tool')
    require(digest(file.read_bytes())==LITERAL_SHA,'Exact preserved parser changed')
    spec=importlib.util.spec_from_file_location('PI08_B_literal_primary_codec',file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
def one_primary(data):
    primary=json.loads(data);require(primary.get('status')=='completed'and not primary.get('error'),'Only actual completed material primary rows')
    value=primary['result'];value=json.loads(value)if isinstance(value,str)else value
    rows=value['result']['rows'];require(len(rows)==1,'One material B episode per indexed primary')
    row=rows[0];require(row.get('version')==VERSION,'No administrative, inherited or other-version row aliased as B')
    return row
def state_signature(observation):
    if int(observation['raw'])==0:return'exact_RAW0'
    if int(observation['state'])==0:return'state0_nonzero_RAW'
    if int(observation['semantic'])==1 and list(observation['direction'])==[0,0,1]:return'active_SEM1_plusZ'
    if int(observation['semantic'])==1 and list(observation['direction'])==[1,0,0]:return'active_SEM1_plusX'
    return'other_actual_RAW_signature'

def inspect(row,role,source,products,parser,p,checks):
    require(row['feedback_arm']==role and row['B_ordinal']==row['ordinal']-12==row['global_regulatory_ordinal']-12,'Actual role/global/new ordinal differs')
    i=row['B_ordinal'];require(type(i)is int and 0<=i<18,'Only the eighteen prospectively evaluated B opportunities')
    require(row['environment_spec']==p['schedule'][12+i],'Environmental fixture differs from frozen schedule')
    aliased=copy.deepcopy(row);aliased['version']=R03
    # Sole alias is fixed geometry selection in the original pure parser. It
    # does not alter RAW, choice, actuator, result, timing, receipt or utility.
    out=parser.inspect_episode(aliased,source,products,checks)
    out['version']=VERSION;out['B_ordinal']=i;out['global_regulatory_ordinal']=row['ordinal']
    out['geometry_alias_only']=R03
    native=out['selection'];canonical=None if native is None else 1 if native==1 else -1
    require(row['native_motor']==canonical and row['Native_selection_valid']is(native is not None),'Native0/NULL or canonical motor conflated')
    require(row['operator_forced_action']is None and not row['actuator_ablation']and not row['sensor_ablation'],'No force/cut belongs to this four-arm B series')
    before=row['reference_policy_before'];after=row['reference_policy_after']
    if role=='reference':
        require(row['executed_action_source']=='external_contextual_WSLS'and isinstance(before,dict)and isinstance(after,dict),'Declared external material reference missing')
        require(set(before)==set(after)=={'0','1','2','3'}and all(type(v)is int and v in(-1,1)for v in before.values()),'Only four actualSTATE actions in external benchmark')
        require(row['actual_motor']==before[str(out['sensor_actual_state'])],'Reference used more than its actual visitedSTATE')
        expected=dict(before)
        if out['actual_failed']:expected[str(out['sensor_actual_state'])]=-row['actual_motor']
        require(after==expected,'Reference did not stay/switch only after its own actual consequence')
    else:
        require(row['executed_action_source']=='Native_TC'and row['actual_motor']==canonical and before is None and after is None,'Candidate/control action chosen outside Native or external policy table present')
    copies=[r for r in row['requests']if r.get('channel')in('PI07.TC.R01.copy.minus','PI07.TC.R01.copy.plus')]
    require(len(copies)==(row['actual_motor']is not None),'Exactly actual executed motor must have action-time efference')
    if copies:
        cp=copies[0];require(cp['actual_motor_choice']==row['actual_motor']and cp['requested_tick']==row['calendar']['query_tick']+7,'Efference does not copy executed action at fixed action boundary')
    returns=[r for r in row['requests']if r.get('channel')in('PI07.TC.R01.outcome.failure','PI07.TC.R01.outcome.nonfailure')]
    require(len(returns)==1,'One material generic return in every arm, including constantFalse')
    ret=returns[0];require(type(ret['actual_environment_failed'])is bool and ret['actual_environment_failed']is row['returned_failed'],'Actual generic return bit differs')
    require(ret['requested_tick']==row['calendar']['query_tick']+408 and not any(k in ret for k in('actual_motor_choice','action','bank','route','target')),'Outcome contains no prior-action/bank dispatch')
    if role in('real','reference'):require(row['returned_failed']is row['actual_failed'],'Real/reference return differs from actual result')
    if role=='none':require(row['returned_failed']is False,'No-failure control is a realFalse return, not missing stimulus')
    direct,aliases=parser.receipts(row['requests'])
    out.update(Native_selection_valid=row['Native_selection_valid'],native_motor=canonical,
       executed_action_source=row['executed_action_source'],reference_policy_before=before,reference_policy_after=after,
       sensor_actual_RAW=row['sensor']['observation']['raw'],sensor_actual_direction=row['sensor']['observation']['direction'],
       sensor_local_signature=state_signature(row['sensor']['observation']),
       cue_native_inputs=[{'id':r['id'],'channel':r['channel'],'status':r['receipt']['status'],'requested_tick':r['requested_tick']}for r in row['requests']if r.get('channel','').startswith('PI07.environment.')and'.useful_'not in r.get('channel','')],
       datum_native_inputs=[{'id':r['id'],'payload':r['payload'],'status':r['receipt']['status'],'requested_tick':r['requested_tick']}for r in row['requests']if r.get('channel')=='PI07.TC.R01.datum'],
       return_channel=ret['channel'],return_receipt_status=ret['receipt']['status'],return_requested_tick=ret['requested_tick'],
       q_mod67=row['calendar']['query_tick']%67,FI_q_mod67=row['FI']['calendar']['query_tick']%67,
       sensor_input_not_private_cue=row['sensor']['submitted_state_datum']==row['sensor']['actual_state_datum'],
       message_artifact_sha256=row['message']['artifact']['sha256']if row['message']['artifact']else None)
    return out,direct

def revisions(rows):
    """Observed same-STATE changes. No nominalcue-implied correct action."""
    bystate=defaultdict(list)
    for row in rows:
        if row['Native_selection_valid']and row['actual_motor']in(-1,1):bystate[row['sensor_actual_state']].append(row)
    pairs=[];triples=[]
    for state,items in sorted(bystate.items()):
        for n in range(len(items)-1):
            a,b=items[n:n+2]
            if not(a['actual_failed']and a['actual_motor']!=b['actual_motor']and b['complete_opportunity']):continue
            between=[r for r in rows if a['B_ordinal']<r['B_ordinal']<b['B_ordinal']]
            event={'actual_STATE':state,'cost_case':a['B_ordinal'],'later_useful_case':b['B_ordinal'],
               'old_executed_motor':a['actual_motor'],'new_executed_motor':b['actual_motor'],
               'direction':'NoPulse_to_Pulse'if b['actual_motor']==1 else'Pulse_to_NoPulse',
               'cost_returned_failed':a['returned_failed'],'cost_delta_before':a['reference_delta_before'],'cost_delta_after':a['reference_delta_after'],
               'later_delta_before':b['reference_delta_before'],'later_pulse_applied':b['pulse_applied'],
               'later_FI_q6':b['FI_q6'],'later_message_delivered':b['message_delivered'],
               'intervening_cases':[r['B_ordinal']for r in between],
               'bank_change_at_cost_matches_inherited_credit_contract':a['credit_increment_contract_matched'],
               'delta_reached_later_use_unchanged':a['reference_delta_after']==b['reference_delta_before']and all(r['observed_credit_increment']==0 for r in between),
               'not_unique_microcausal_lineage_or_independent_replicate':True}
            pairs.append(event)
            if n>0:
                previous=items[n-1]
                if previous['complete_opportunity']and previous['actual_motor']==a['actual_motor']:
                    triples.append({**event,'earlier_same_STATE_same_action_useful_case':previous['B_ordinal'],
                       'interpretation':'Observed useful action became costly, then a different action became useful at the same actualSTATE. Nominal cue labels do not establish this.'})
    return{'same_STATE_cost_then_changed_action_useful':pairs,'observed_useful_to_costly_to_revised_useful':triples,
           'directions_with_useful_later_STATE1':sorted({r['direction']for r in pairs if r['actual_STATE']==1}),
           'both_directions_observed_STATE1':{'NoPulse_to_Pulse','Pulse_to_NoPulse'}<={r['direction']for r in pairs if r['actual_STATE']==1}}

def calculate(root,index_path):
    index=read(local(root,index_path));require(index['schema']=='DEE.PI08.B.portable_primary_index.R01','Exact B portable index required')
    p=json.loads(checked(root,index['protocol']));require(p['schema']=='DEE.PI08.successive_contextual_regulation.protocol.B.R01'and p['status']=='SEALED_BEFORE_B_NATIVE','Frozen B protocol required')
    require(len(p['schedule'])==32 and p['start_ordinal']==12 and p['evaluated_opportunities']==18,'Do not score12copied inherited rows as B opportunities')
    parser=legacy();checks=[];arms={};denominators={};all_lives=set()
    for role,arm in index['arms'].items():
        require(role in ROLES,'Unexpected role')
        products={entry['sha256']:checked(root,entry)for entry in arm.get('products',[])}
        rows=[];ids=set();totals=Counter();life=None
        for entry in arm['primaries']:
            row=one_primary(checked(root,entry));require(life in(None,row['life_id']),'Mixed Native worlds inside an arm');life=row['life_id']
            observed,direct=inspect(row,role,entry['file'],products,parser,p,checks)
            require(not ids.intersection(direct),'Historical/current Native receipt counted twice in one life');ids.update(direct);totals.update(r['status']for r in direct.values());rows.append(observed)
        rows.sort(key=lambda r:r['B_ordinal']);require([r['B_ordinal']for r in rows]==list(range(len(rows))),'Missing, repeated or reordered B episode')
        require(life not in all_lives,'Two arms cannot use the same current identity');all_lives.add(life)
        for a,b in zip(rows,rows[1:]):require(a['after_tick']==b['before_tick'],'Noncontinuous arm exposure')
        summary=None
        if arm.get('summary'):
            summary=json.loads(checked(root,arm['summary']));require(summary['role']==role and summary['life_id']==life,'Wrong closed arm summary')
            require(summary['Native_inputs']['unique_requested']==len(ids)and summary['opportunities_completed']==len(rows),'Summary direct dose/opportunities differ')
        complete=bool(summary and summary['closed']and summary['error']is None and summary['status']=='CLOSED_18_OPPORTUNITIES'and len(rows)==18)
        if role=='yoked':
            plan=json.loads(checked(root,arm['yoked_plan']));perm=p['controls']['yoke_permutation']
            require(plan['permutation']==perm and plan['values']==[plan['source_failed'][i]for i in perm],'Frozen noncyclic permutation changed')
            require(all(type(v)is bool for v in plan['values'])and len(plan['values'])==18,'Exact18boolean control')
            require([r['returned_failed']for r in rows]==plan['values'][:len(rows)],'Material yoked return differs from fixed plan')
        stats={'life_id':life,'complete_closed_18':complete,'opportunities':len(rows),'valid_Native_selections':sum(r['Native_selection_valid']for r in rows),
            'joint_useful':sum(r['complete_opportunity']for r in rows),'FI_q6_correct':sum(r['FI_q6']==1 for r in rows),'FI_q4_correct':sum(r['FI_q4']==1 for r in rows),
            'messages_offered':sum(r['message_required']for r in rows),'messages_delivered':sum(r['message_required']and r['message_delivered']for r in rows),
            'pulse_requested':sum(r['pulse_scheduled']for r in rows),'pulse_applied':sum(r['pulse_applied']for r in rows),
            'actual_failures':sum(r['actual_failed']for r in rows),'returned_failures':sum(r['returned_failed']for r in rows),'return_mismatches':sum(r['actual_failed']!=r['returned_failed']for r in rows),
            'actual_STATE_counts':dict(Counter(str(r['sensor_actual_state'])for r in rows)),
            'local_signature_counts':dict(Counter(r['sensor_local_signature']for r in rows)),
            'Native_inputs':{'unique_requested':len(ids),'status_counts':dict(totals)},
            'new_Native_ticks':sum(r['after_tick']-r['before_tick']for r in rows),
            'block_counts':{stage:{'opportunities':len(group),'joint_useful':sum(r['complete_opportunity']for r in group),'STATE1_exposures':sum(r['sensor_actual_state']==1 for r in group)}for stage,group in((stage,[r for r in rows if r['stage']==stage])for stage in('T1','F1','T2','F2'))}}
        arms[role]={'stats':stats,'rows':rows,'revisions':revisions(rows),
                    'perception_aliases':[{'B_ordinal':r['B_ordinal'],'nominal_cue':r['cue_fixture_not_actor_input'],'actual_STATE':r['sensor_actual_state'],'local_signature':r['sensor_local_signature'],'FI_q6':r['FI_q6'],'pulse_applied':r['pulse_applied'],'interpretation':'Prepared cue is not actual perception or demonstrated harm; do not count success by nominal label.'}for r in rows if(r['cue_fixture_not_actor_input']!='none'and r['sensor_actual_state']==0)or(r['cue_fixture_not_actor_input']=='none'and r['sensor_actual_state']!=0)]}
        denominators[role]=stats
    comparisons={}
    if'real'in arms:
        real=arms['real']['rows']
        for role,arm in arms.items():
            if role=='real':continue
            paired=[]
            for a,b in zip(real,arm['rows']):
                require(a['B_ordinal']==b['B_ordinal'],'Paired ordinal mismatch')
                paired.append({'B_ordinal':a['B_ordinal'],'same_query_tick':a['query_tick']==b['query_tick'],'same_FI_query_tick':a['FI_query_tick']==b['FI_query_tick'],
                  'same_return_tick':a['return_requested_tick']==b['return_requested_tick'],'same_duration':a['after_tick']-a['before_tick']==b['after_tick']-b['before_tick'],
                  'same_actual_STATE':a['sensor_actual_state']==b['sensor_actual_state'],'same_local_signature':a['sensor_local_signature']==b['sensor_local_signature'],
                  'real_motor':a['actual_motor'],'control_motor':b['actual_motor'],'real_joint_useful':a['complete_opportunity'],'control_joint_useful':b['complete_opportunity'],
                  'real_Native_requests':a['unique_current_requests'],'control_Native_requests':b['unique_current_requests'],
                  'real_returned_failed':a['returned_failed'],'control_returned_failed':b['returned_failed']})
            comparisons[role]={'paired_source_not_independent_lives':True,'pairs':paired,'calendars_all_equal':all(r['same_query_tick']and r['same_FI_query_tick']and r['same_return_tick']and r['same_duration']for r in paired),
               'actual_exposure_equal_all':all(r['same_actual_STATE']and r['same_local_signature']for r in paired),
               'request_count_difference_can_include_the_selected_pulse_not_only_feedback':True,
               'real_joint_useful_on_paired':sum(r['real_joint_useful']for r in paired),'control_joint_useful_on_paired':sum(r['control_joint_useful']for r in paired)}
        if'yoked'in arms:
            yp=json.loads(checked(root,index['arms']['yoked']['yoked_plan']))
            require(len(real)==18 and yp['source_failed']==[r['actual_failed']for r in real],'Yoke source must be actual closed18real consequences')
            comparisons['yoked']['same_true_false_return_dose']=sum(yp['values'])==sum(r['returned_failed']for r in real)
            comparisons['yoked']['actual_manipulation_mismatches']=arms['yoked']['stats']['return_mismatches']
            comparisons['yoked']['warning_information_not_ruled_out_by_dose_matching']=True
    require(all(check['passed']for check in checks),'Inherited parser integrity/calendar check failed')
    return{'schema':'DEE.PI08.B.recalculated_primary_comparison.R01','Native_executed':False,'DEE_imported':False,'integrity_passed':True,
       'evidence_status':'ALL_FOUR_ARMS_CLOSED18'if set(arms)==set(ROLES)and all(a['stats']['complete_closed_18']for a in arms.values())else'PARTIAL_CLOSED_EPISODES_NOT_ALL_ARMS_COMPLETE',
       'index_sha256':digest(local(root,index_path).read_bytes()),'protocol_sha256':index['protocol']['sha256'],'legacy_parser_sha256':LITERAL_SHA,
       'mechanical_geometry_alias':{'from':VERSION,'to':R03,'scope':'Geometry/readers/RAW/FI/message/receipt validation only; originalBversion restored in output. Native/reference action and actual returns independently checked.'},
       'denominators':denominators,'arms':arms,'comparisons':comparisons,'integrity_checks':checks,
       'interpretation_limits':['STATE0 is not NULL; a nominal threat with exactRAW0/STATE0 is not treated as a perceived harmful episode.','Observed same-STATE revisions and bank increments support local history dependence; pair/triple labels do not isolate a unique microcausal lineage.','Returns matched in total dose can remain accidentally informative; no automatic true-contingency advantage is inferred.','Nativeinputs, ticks and copied metadata rows are not new concepts or independent individuals.','Material externalWSLS utility is reported from its own clone only; no offline counterfactual scores.','No adoption, current principal modification or universal agency claim is performed by this recálculo.']}

def main(args):
    root=Path(args.raiz).resolve(strict=True);output=Path(args.salida).absolute();require(not output.exists(),'New output only; preserve prior recálculo')
    result=calculate(root,args.indice)
    with output.open('x',encoding='utf8')as out:json.dump(result,out,ensure_ascii=False,indent=2);out.write('\n')
    print(json.dumps({'passed':True,'status':result['evidence_status'],'output':str(output),'sha256':digest(output.read_bytes()),'denominators':result['denominators']},ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--raiz',required=True);parser.add_argument('--indice',default='INDICE_B_PI08_R01.json');parser.add_argument('--salida',required=True);main(parser.parse_args())
