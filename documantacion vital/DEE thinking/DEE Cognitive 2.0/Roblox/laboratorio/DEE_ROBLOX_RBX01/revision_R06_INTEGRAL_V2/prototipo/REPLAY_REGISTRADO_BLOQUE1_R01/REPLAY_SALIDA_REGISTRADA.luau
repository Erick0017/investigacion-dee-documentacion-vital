-- RECORDED OUTPUT REPLAY ONLY; no new DEE callback or learning.
local package=game:GetService("ServerScriptService").DEEConnector_R06
local API=require(package.Main);local H=game:GetService("HttpService")
local a=API.lookupRuntime("R06_CLEAN","scene_01"):get("agent_01")
assert(not a.node.Actions:FindFirstChild("REPLAY_46ecea6eb451d1ef_C5"),"EXISTING_REPLAY_PRESERVED_INSPECT_RECEIPT_NO_REPLAY")
local state=a:status();local observation
if state.phase=="BOUNDARY"then observation=a:observe("ROUTE_CHOICE")
else assert(state.phase=="AWAIT_ACTION"and state.completedOpportunities==0,"ONLY_CLEAN_TECHNICAL_START_OR_BOUNDARY");observation=state.observation end
local provenance=H:JSONDecode("{\"source\":\"D:\\\\GENESIS AI\\\\GENESIS 5.0\\\\simulador de universo ab-initio\\\\dee_libreria\\\\VERSION_27\\\\tests\\\\documantacion vital\\\\DEE thinking\\\\DEE Cognitive 2.0\\\\laboratorio\\\\DEE_ROBLOX_RBX01\\\\revision_R06_INTEGRAL_V2\\\\evidencia\\\\NATIVE_BLOQUE_01\\\\RESULTADO.json\",\"source_sha256\":\"46ecea6eb451d1ef8a82af59b3c3add251e401ac58a5fefdeb51f60c43231d45\",\"life\":\"ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V2_MAIN\",\"session\":\"R06_MAIN_bb7e2b08e4ab445ca8bd\",\"cycle\":5,\"Native_action\":\"EXIT_0\",\"Native_tick\":954029,\"original_operation_id\":\"R06_R06_MAIN_bb7e2b08e4ab445ca8bd_05_QUERY_SENSOR\",\"original_executed_route\":\"EXIT_0\",\"original_result\":{\"resourceCollected\":false,\"durationMs\":8000,\"keyCollected\":false,\"querySpent\":0,\"permissionSpent\":0,\"tollSpent\":0,\"materialConsequence\":false,\"outcome\":\"DELIVERED\",\"resourceDelivered\":true,\"codeRejected\":false,\"queryDenied\":false,\"collision\":false,\"invalidAction\":false},\"selection_rule\":\"First closed non-NULL Native Q2 movement that equals its actual registered route; no best-result selection.\"}")
local raw=H:JSONEncode({protocol=API.Schema,namespace=a.namespace,sessionId=state.sessionId,
    seq=observation.seq,observationId=observation.observationId,actionId="REPLAY_46ecea6eb451d1ef_C5",
    operationId="REPLAY_TRANSPORT_46ecea6eb451d1ef",action={name="EXIT_0"},sourceKind="MCP_TECHNICAL_CONTROL",
    recordedNativeProvenance=provenance,replayNotNewNative=true})
local ack=a:deliverAction(raw);a:confirmActionAck(ack.actionId,ack.operationId)
local closed=a:completeFeedback({actionId=ack.actionId,feedbackOperationId="REPLAY_FEEDBACK_46ecea6eb451d1ef",nativeTick=0})
return{scope="RECORDED_NATIVE_OUTPUT_REPLAY_DIFFERENT_BODY",original=provenance,ack=ack,
    cursor=closed.actionCursor,folderCursor=a.node.ActionCursor.Value,newNativeTicks=0,
    newLearning=false,newMissionScore=0,noNativeBackendOpened=true}
