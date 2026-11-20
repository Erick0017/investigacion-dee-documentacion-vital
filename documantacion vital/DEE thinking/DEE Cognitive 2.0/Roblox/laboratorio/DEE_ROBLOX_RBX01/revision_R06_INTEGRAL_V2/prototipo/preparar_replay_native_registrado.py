"""Prepare one technical replay of a recorded Native action in the clean module.

Reads a closed R06 result only. No Native callback/MCP/owner. The replay has a
new technical transport ID, carries original provenance, and counts0Native ticks.
It is not a continuation, new learned action or new mission result.
"""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):
    source=a.source.resolve(strict=True);value=json.loads(source.read_text(encoding='utf-8-sig'))
    if value.get('schema')!='DEE.RBX01.R06.integrated.result.R01'or value.get('owner_closed')is not True:raise ValueError('Actual closed R06 result required')
    candidates=[r for r in value['rows']if isinstance(r.get('Native_Q2'),dict)and r['Native_Q2'].get('action')in('EXIT_0','EXIT_1')and not r['Native_Q2'].get('null',True)and r.get('executed_route')==r['Native_Q2']['action']]
    if not candidates:raise ValueError('No recorded Native movement matching the original executed route; do not invent a successful action')
    row=candidates[0];decision=row['Native_Q2'];operation=decision['evidence']['native_request_id']
    provenance=dict(source=str(source),source_sha256=sha(source),life=value['identity']['life'],session=value['identity']['session'],
        cycle=row['cycle'],Native_action=decision['action'],Native_tick=decision['nativeTick'],original_operation_id=operation,
        original_executed_route=row['executed_route'],original_result=row['world_result'],
        selection_rule='First closed non-NULL Native Q2 movement that equals its actual registered route; no best-result selection.')
    output=a.output.resolve();
    if output.exists()or not output.is_relative_to(ROOT/'prototipo'):raise ValueError('Fresh prototype replay output only')
    output.mkdir(parents=True)
    action_id='REPLAY_'+sha(source)[:16]+'_C'+str(row['cycle']);transport_id='REPLAY_TRANSPORT_'+sha(source)[:16]
    metadata=dict(schema='DEE.RBX.Prototype.RecordedOutputReplay.R01',provenance=provenance,new_transport_action_id=action_id,
        new_transport_operation_id=transport_id,scope='RECORDED_NATIVE_OUTPUT_IN_DIFFERENT_TECHNICAL_BODY_NOT_NEW_NATIVE_OR_LEARNING',
        generated_only=True,MCP_executed=False,new_Native_ticks=0,mission_score_increment=0,
        target='Already installed clean DEEConnector_R06 in Studio. Optional after the prior clean technical test; no backend started.')
    (output/'PROCEDENCIA_REPLAY.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    literal=json.dumps(json.dumps(provenance,ensure_ascii=True,separators=(',',':')))
    code='''-- RECORDED OUTPUT REPLAY ONLY; no new DEE callback or learning.
local package=game:GetService("ServerScriptService").DEEConnector_R06
local API=require(package.Main);local H=game:GetService("HttpService")
local a=API.lookupRuntime("R06_CLEAN","scene_01"):get("agent_01")
assert(not a.node.Actions:FindFirstChild(ACTION_ID),"EXISTING_REPLAY_PRESERVED_INSPECT_RECEIPT_NO_REPLAY")
local state=a:status();local observation
if state.phase=="BOUNDARY"then observation=a:observe("ROUTE_CHOICE")
else assert(state.phase=="AWAIT_ACTION"and state.completedOpportunities==0,"ONLY_CLEAN_TECHNICAL_START_OR_BOUNDARY");observation=state.observation end
local provenance=H:JSONDecode(PROVENANCE)
local raw=H:JSONEncode({protocol=API.Schema,namespace=a.namespace,sessionId=state.sessionId,
    seq=observation.seq,observationId=observation.observationId,actionId=ACTION_ID,
    operationId=OPERATION_ID,action={name=ACTION_NAME},sourceKind="MCP_TECHNICAL_CONTROL",
    recordedNativeProvenance=provenance,replayNotNewNative=true})
local ack=a:deliverAction(raw);a:confirmActionAck(ack.actionId,ack.operationId)
local closed=a:completeFeedback({actionId=ack.actionId,feedbackOperationId=FEEDBACK_ID,nativeTick=0})
return{scope="RECORDED_NATIVE_OUTPUT_REPLAY_DIFFERENT_BODY",original=provenance,ack=ack,
    cursor=closed.actionCursor,folderCursor=a.node.ActionCursor.Value,newNativeTicks=0,
    newLearning=false,newMissionScore=0,noNativeBackendOpened=true}
'''.replace('ACTION_ID',json.dumps(action_id)).replace('OPERATION_ID',json.dumps(transport_id)).replace('ACTION_NAME',json.dumps(decision['action'])).replace('FEEDBACK_ID',json.dumps('REPLAY_FEEDBACK_'+sha(source)[:16])).replace('PROVENANCE',literal)
    target=output/'REPLAY_SALIDA_REGISTRADA.luau';target.write_text(code,encoding='utf8')
    return dict(script=str(target),script_sha256=sha(target),source_cycle=row['cycle'],Native_action=decision['action'],Native_executed=False,MCP_executed=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(run(p.parse_args()),ensure_ascii=False,indent=2))
