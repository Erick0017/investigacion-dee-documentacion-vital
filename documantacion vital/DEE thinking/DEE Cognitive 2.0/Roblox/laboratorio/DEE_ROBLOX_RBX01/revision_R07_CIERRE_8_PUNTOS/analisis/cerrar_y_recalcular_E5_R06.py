"""Passive closure/recalculation of actual PROGRAMMED and prestart-rejected AI."""
from pathlib import Path
import hashlib
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RECALCULO_CIERRE8_R07_R02 import Sources,run,save_outputs

ROOT=Path(__file__).resolve().parents[1];A=ROOT/'analisis'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def metadata(p):
    p=Path(p);raw=p.read_bytes();return {'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
program=ROOT/'evidencia/PROGRAMMED_R06_BLOQUE_01'
result=read(program/'RESULTADO.json');world=read(program/'WORLD_CHECKPOINT.json')
policy=read(ROOT/'comparadores/PROGRAMMED_R06/POLICY_STATE_V3.json')
policy_events=[json.loads(x)for x in(ROOT/'comparadores/PROGRAMMED_R06/POLICY_EVENTS_V3.jsonl').read_text('utf-8').splitlines()if x.strip()]
assert result['owner_closed']is True and world['boundary']['phase']=='BOUNDARY'
assert result['new_opportunities_completed']==18 and world['S']['completedCycles']==46
assert policy['pending']is None and policy_events[-1]['kind']=='CLOSED'
assert not(ROOT/'comparadores/PROGRAMMED_R06/POLICY_OWNER_V3.lock').exists()
reject_path=ROOT/'evidencia/CONVENTIONAL_AI_R06_BLOQUE_01/PREFLIGHT_RAM_REJECTED.json'
reject=read(reject_path)
assert reject['status']=='PRESTART_RESOURCE_REJECTED_NO_WORLD_OR_POLICY_OPENED'
assert reject['Native_calls']==reject['model_calls']==reject['MCP_calls']==0
assert not(ROOT/'comparadores/CONVENTIONAL_AI_R06').exists()
assert not(ROOT/'comparadores/CUOTA_LLM_V3.json').exists()
daemon_path=ROOT/'comparadores/SERVIDOR_MODELO_V3_R05.jsonl'
daemon=[json.loads(x)for x in daemon_path.read_text('utf-8').splitlines()if x.strip()]
closed=[x for x in daemon if x.get('kind')=='CLOSED'];assert len(closed)==1 and closed[0]['server_exit_code']==0
scene=ROOT/'mundo/DEE_RBX01_R07_NATIVE.rbxlx'
assert metadata(scene)['sha256']=='724cb84eec14d9b6fa3b4d4eede22743f7030c1be4ad21ffb4f7d4b2acf33ab8'
spec=read(A/'RECALCULO_MAIN6_INPUTS_R02.json')
spec['arms'].append({'name':'PROGRAMMED_R06_18','participant':'PROGRAMMED','sensor_arm':'local_tag',
    'blocks':[{'result':str(program/'RESULTADO.json'),'world':str(program/'WORLD_CHECKPOINT.json'),
        'events':str(program/'EVENTS.jsonl')}]})
inputs=A/'INPUTS_E5_MAIN6_PROGRAMMED18_R06.json'
assert not inputs.exists();inputs.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n','utf-8')
facts=run(spec,Sources(ROOT.parent))
output=A/'E5_MAIN6_PROGRAMMED18_RECALCULO_R01'
save_outputs(output,facts)
arm=next(x for x in facts['arms']if x['participant']=='PROGRAMMED')
summary={'schema':'DEE.R07.E5.ActualReferencesAndPrestartRejection.R06',
    'PROGRAMMED':{'session':result['identity']['session'],'actual_new_opportunities':18,
        'global_completed':46,'closed':True,'pending':None,'backend_operations':len(policy['cache']),
        'world':metadata(program/'WORLD_CHECKPOINT.json'),'result':metadata(program/'RESULTADO.json'),
        'counter_delta':arm['delta'],'numeric_invocations':arm['calculation_opportunities'],
        'integers_formed':arm['formed_integer_outputs'],'correct_given_actual_opcode':arm['correct_given_actual_opcode'],
        'numeric_no_integer':arm['numeric_no_integer'],'lesson_calls':arm['lesson_calls'],
        'assistance':'Prepared Python strategy, own experienced graph, symbolic associations and Python arithmetic; not DEE'},
    'CONVENTIONAL_AI':{'status':'PRESTART_HOST_RAM_REJECTED_NOT_A_COGNITIVE_TRIAL',
        'prospective_session':'R07_CONVENTIONAL_AI_R06_01','actual_new_opportunities':0,
        'inference_requests_by_campaign':0,'quota_file_created':False,'policy_or_World_opened':False,
        'rejection':metadata(reject_path),'available_physical_bytes':reject['measurement']['available_physical_bytes'],
        'required_physical_bytes':reject['minimum_start_free_bytes'],
        'not_scored_as_18_failures':True,'model_ability_not_evaluated':True},
    'daemon':{'lifecycle':metadata(daemon_path),'owned_pid':next(x['pid']for x in daemon if x.get('kind')=='STARTED'),
        'closed':closed[0],'stop_reason':'STOP_FILE_AFTER_NO_POLICY_OR_PENDING_REQUEST',
        'quota_reset':False,'downloads':0,'model_manifest_sha256':'a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72'},
    'world_control_returned':'Studio522 stopped to Edit, stop receipt control/E5_PREFLIGHT_R06/10_AI_REJECTED_STOP_PLAY.json',
    'scene_file':metadata(scene),'Native_executions_by_references':0,
    'comparison':{'actual_common_prefix':facts['common_observed_cycles'],
        'all_three_executed':False,'Native6_vs_PROGRAMMED18_full_and_common6_separate':True,
        'not_equal_innate_prior':'References receive symbolic public preparation; Native physical history and scalar inputs do not prove equal semantic decoding',
        'host_confound':'Root reported bounded window/capture host probes during this interval; not a universal efficiency ranking'},
    'recalculation_issues':facts['issues_total'],'passive_recalculation_not_Native_reproduction':True}
target=output/'E5_CIERRE_REAL_R06.json';target.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'summary':metadata(target),'program_numeric':arm['numeric'],
    'program_delta':arm['delta'],'comparison':facts['comparison'],'issues':facts['issues_total']},ensure_ascii=False))
