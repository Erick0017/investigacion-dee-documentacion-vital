"""Passive P08 closed-file accounting; no Native/SDK/DB/model execution."""
from __future__ import annotations
import argparse, csv, importlib.util, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('passive_sources',Path(__file__).with_name('RECALCULO_CIERRE8_R07_R02.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def calculate(spec,source):
    if spec.get('schema')!='DEE.R07.P08.closed_inputs.R09.v1':raise ValueError('Explicit P08 inputs required')
    result=source.json(spec['result']);world=source.json(spec['world']);conciliation=source.json(spec['conciliation']);ledger=source.json(spec['ledger'])
    lease=source.json(spec['lease_result']);loc=source.json(spec['localizers']);manifest=source.raw(spec['source_manifest'])
    kit=source.raw(spec['kit']);connector=source.raw(spec['exported_connector']);events=source.jsonl(spec['events']);adapter=source.raw(spec['source_adapter']).decode('utf-8-sig')
    if result.get('owner_closed')is not True or result.get('status')!='ONE_LIVE_EPISODE_CLOSED' or result.get('failure')is not None:raise ValueError('Closed successful P08 result required')
    state=world['state'];backend=world['backend'];ws=world['world']['state'];issues=[]
    def check(ok,code):
        if not ok:issues.append(code)
    check(backend.get('backendWriterClosed')is True and backend.get('bridgeQuiescent')is True,'BACKEND_NOT_QUIESCENT_CLOSED')
    check(state['phase']=='BOUNDARY'and state['completedOpportunities']==1,'EXACT_ONE_BOUNDARY')
    check(state['sessionId']==result['session_id']==backend['sessionId'],'SESSION_MISMATCH')
    check(state['lifeId']==result['basis']['life']==backend['lifeId'],'LIFE_MISMATCH')
    check(m.digest(manifest)==result['basis']['source_manifest'],'SOURCE_MANIFEST_MISMATCH')
    for key,spec_key in [('result','result'),('world','world'),('ledger','ledger')]:
        check(source.records[spec[spec_key]]['sha256']==conciliation[key]['sha256'],'CLOSURE_PIN_'+key)
    check(conciliation['global_intents']=={} and ledger.get('intents')=={},'PENDING_LEDGER_INTENT')
    check(conciliation['pilot_ledger']['reserved']==0 and conciliation['pilot_ledger']['cycles']==1,'PILOT_LEDGER_BOUNDARY')
    ops={};aliases=0;intents={}
    for line,event in events:
        if event.get('kind')=='NATIVE_INTENT':intents[event['context']['operation_id']]=event
        if event.get('kind')!='NATIVE_COMPLETED':continue
        op=event['operation_id'];record={'phase':event['phase'],'result':event['result']}
        if op in ops:
            check(ops[op]['record']==record,'CONFLICTING_OPERATION_ID');aliases+=1
        else:ops[op]={'record':record,'line':line}
    expected=result['native_outputs'];check(len(ops)==len(expected)==3,'THREE_UNIQUE_NATIVE_PHASES_REQUIRED')
    phases=[];tick=result['basis']['source_tick']
    for item in expected:
        op=item['operation_id'];out=item['result'];kind=item['kind']
        check(op in ops and ops[op]['record']=={'phase':kind,'result':out},'EVENT_RESULT_PHASE_MISMATCH')
        check(op in intents,'MISSING_NATIVE_INTENT')
        check(out['nativeTick']-out['nativeTicks']==tick,'NONCONTIGUOUS_TICKS');tick=out['nativeTick']
        phases.append({'phase':kind,'operation_id':op,'ticks':out['nativeTicks'],'after_tick':tick,'action':out.get('action'),'null':out['null'],'source_line':ops.get(op,{}).get('line')})
    check([x['phase']for x in phases]==['decision','query_sensor','feedback'],'PHASE_ORDER')
    check(tick==result['final_tick']==state['nativeTick']==backend['nativeTick']==992751,'FINAL_TICK')
    check(sum(x['ticks']for x in phases)==result['new_native_ticks']==1564,'TICK_TOTAL')
    check(phases[0]['action']=='ASK_STATION'and phases[1]['action']=='EXIT_1','ACTUAL_NATIVE_CHOICES')
    check(all(x['null']is False for x in phases),'NULL_PHASE')
    actions=[];seen=set()
    for ack in result['body_acks']:
        op=ack['operationId'];check(op not in seen,'REPEATED_ACTION_ALIAS');seen.add(op)
        persisted=world['actions'][op];request=json.loads(persisted['rawRequest']);native=ops[op]['record']['result']
        check(ack==persisted['ack'],'WORLD_ACK_RESULT_MISMATCH')
        check(ack['technicalControl']is False and persisted['technical']is False and request['sourceKind']=='DEE_NATIVE','TECHNICAL_OR_NON_NATIVE_ACTION')
        check(ack['executionStatus']=='EXECUTED','ACTION_NOT_EXECUTED')
        check(request['action']['name']==native['action']and request['action']['nativeTick']==native['nativeTick'],'BODY_ACTION_NOT_NATIVE_CHOICE')
        check(request['actionId']==request['operationId']==ack['actionId']==op,'ACTION_ID_CORRELATION')
        check(request['sessionId']==ack['sessionId']==result['session_id']and request['observationId']==ack['observationId'],'OBSERVATION_CORRELATION')
        ir=intents[op];check(ir['context']['sequence']==ack['seq']+56 and ir['context']['observation_id']==ack['observationId'],'DECLARED_SEQUENCE_OFFSET')
        ar=ack['result'];before=ar['before'][:3];after=ar['after'][:3]
        actions.append({'operation_id':op,'action':native['action'],'module_seq':ack['seq'],'Native_seq':ir['context']['sequence'],'query_spent':ar['querySpent'],'toll_spent':ar['tollSpent'],'permission_spent':ar['permissionSpent'],'outcome':ar['outcome'],'before_position':before,'after_position':after,'euclidean_displacement':math.dist(before,after),'device_before':ar['deviceBefore'],'device_after':ar['deviceAfter'],'collision':ar['collision'],'resource_collected':ar['resourceCollected'],'resource_delivered':ar['resourceDelivered']})
    check(len(actions)==2,'EXACT_TWO_BODY_ACTIONS')
    route=result['body_acks'][1]['result'];motor=route['motor'];feedback=intents[expected[2]['operation_id']]['payload']
    check(motor['status']=='ARRIVED','MOTOR_NOT_ARRIVED')
    motor_label=motor['actionId'];declared_fallback='R07_PILOT_TRANSPORT'
    fallback_declared=('action.actionId or\"'+declared_fallback+'\"')in adapter
    check(motor_label==expected[1]['operation_id']or(motor_label==declared_fallback and fallback_declared),'UNDECLARED_MOTOR_LABEL')
    check(route['preparedHumanoidPathfinding']is True and route['preparedKinematicActuator']is False,'PREPARED_MOTOR_SCOPE')
    check(feedback['actionId']==expected[1]['operation_id']and feedback['observationId']==result['body_acks'][1]['observationId'],'FEEDBACK_ACTION_CORRELATION')
    check(feedback['permissionSpent']==sum(x['permission_spent']for x in actions),'COST_ALIAS_OR_DOUBLE_COUNT')
    check(route['deviceBefore']==-1 and route['deviceAfter']==world['world']['device']['value']==1,'ACTUAL_DEVICE_CHANGE')
    check(lease['Native_calls']==lease['new_ticks']==0 and lease['other_roles_bytes_unchanged']is True,'LEASE_WAS_NOT_FS_ONLY')
    check(loc['native_tick']==1019339 and all(loc[k]is False for k in ['all_current_files_newly_enumerated','new_whole_root_manifest_created','immutable_full_backup','independent_rollback','material_reopen_at46_tested']),'LOCATOR_SCOPE_OVERCLAIM')
    source.verify_unchanged()
    return {'schema':'DEE.R07.P08.passive_recalculation.R09.v1','mode':'CLOSED_FILES_NOT_NATIVE_REPRODUCTION','episodes':1,'new_native_ticks':sum(x['ticks']for x in phases),'source_tick':result['basis']['source_tick'],'final_tick':tick,'phases':phases,'unique_operations':len(ops),'operation_aliases':aliases,'actions':actions,'unique_body_actions':len(actions),'queries':sum(x['query_spent']for x in actions),'toll_spent':sum(x['toll_spent']for x in actions),'permission_spent':sum(x['permission_spent']for x in actions),'stock_after':ws['stock'],'motor':{'status':motor['status'],'waypoints':len(motor['waypoints']),'wall_seconds':motor['wallSeconds'],'no_alternate_goal':motor['no_alternate_goal'],'raw_motor_action_label':motor_label,'nested_label_equals_Native_operation_id':motor_label==expected[1]['operation_id'],'fallback_declared_in_source':fallback_declared,'binding_scope':'Native operationId is correlated in raw request, outer ACK and World action record. Nested motor uses declared technical fallback label, not an independent Native operationId.','prepared_pathfinding_not_cognitive_route_planning':True},'device':{'before':route['deviceBefore'],'after':route['deviceAfter'],'fixed_actuator':route['deviceActuation']['prepared_fixed_actuator'],'semantic_choice_in_motor':route['deviceActuation']['semantic_choice_in_motor']},'resource_collections':sum(x['resource_collected']is True for x in actions),'resource_deliveries':sum(x['resource_delivered']is True for x in actions),'feedback_material_consequence':feedback['materialConsequence'],'paid_panel':world['world']['panels'],'assistance':result['assistance'],'ledger_capture':{'global_consumed':conciliation['global_consumed'],'global_intents':conciliation['global_intents'],'pilot_consumed':conciliation['pilot_ledger']['consumed']},'kit':{'bytes':len(kit),'sha256':m.digest(kit)},'exported_connector':{'bytes':len(connector),'sha256':m.digest(connector)},'MAIN46_locator':{'sha256':source.records[spec['localizers']]['sha256'],'full_manifest':False,'immutable_backup':False,'rollback':False,'material_reopen46':False},'issues':issues,'Native_MCP_Studio_model_SQLite_executions':0,'sources':list(source.records.values()),'limits':['Single internally operated prepared-map transfer episode; external evaluation not provided.','No new teacher, arithmetic invocation, learned route, general agency or necessity of paid information established.','Three Native phases and two correlated body actions form one episode; aliases are not extra experiences.','Runtime/service, snapshots and DB remain local; module World and narrow locators are not complete independent rollback.','Captured ledger53176 must not be replaced by earlier MAIN51612; this analysis reads neither live ledger nor DB.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inputs',type=Path,required=True);ap.add_argument('--source-root',type=Path,default=ROOT);ap.add_argument('--package-root',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists()or not a.output.parent.is_dir():raise ValueError('Fresh output with existing parent required')
    facts=calculate(json.loads(a.inputs.read_text('utf-8-sig')),m.Sources(a.source_root,a.package_root));a.output.mkdir()
    (a.output/'HECHOS_P08_R09.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name,rows in [('FASES_P08_R09.csv',facts['phases']),('ACCIONES_P08_R09.csv',facts['actions'])]:
        with(a.output/name).open('w',encoding='utf-8',newline='')as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:m.canonical(v)if isinstance(v,(dict,list))else v for k,v in row.items()}for row in rows)
    print(json.dumps({'output':str(a.output),'episodes':1,'issues':facts['issues'],'Native_executed':False},ensure_ascii=False))
    return 0 if not facts['issues']else 1
if __name__=='__main__':raise SystemExit(main())
