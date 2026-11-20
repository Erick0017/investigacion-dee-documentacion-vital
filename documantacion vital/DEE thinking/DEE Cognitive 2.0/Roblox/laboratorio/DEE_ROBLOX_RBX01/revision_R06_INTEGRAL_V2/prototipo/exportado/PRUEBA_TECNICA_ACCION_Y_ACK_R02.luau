-- Technical connector control only, NOT a DEE-selected action or experiment.
local package=game:GetService("ServerScriptService").DEEConnector_R06
local API=require(package.Main);local H=game:GetService("HttpService")
local a=API.lookupRuntime("R06_CLEAN","scene_01"):get("agent_01")
local s=a:status();assert(s.phase=="AWAIT_ACTION","TEST_EXPECTS_ORIGINAL_FRESH_OBSERVATION")
local raw=H:JSONEncode({protocol=API.Schema,namespace=a.namespace,sessionId=s.sessionId,
    seq=s.sequence,observationId=s.observation.observationId,actionId="MCP_TEST_ACTION_01",
    operationId="MCP_TEST_OPERATION_01",action={name="EXIT_0"},sourceKind="MCP_TECHNICAL_CONTROL"})
local ack=a:deliverAction(raw);local beforeDuplicate=a.adapters.body:capture()
local duplicate=a:deliverAction(raw);local afterDuplicate=a.adapters.body:capture()
assert(beforeDuplicate.schema==afterDuplicate.schema and #beforeDuplicate.pose==12 and #afterDuplicate.pose==12,"DUPLICATE_POSE_SHAPE")
for i=1,12 do assert(beforeDuplicate.pose[i]==afterDuplicate.pose[i],"DUPLICATE_ACTION_REPLAYED_COMPONENT_"..i)end
a:confirmActionAck(ack.actionId,ack.operationId)
local closed=a:completeFeedback({actionId=ack.actionId,feedbackOperationId="MCP_TEST_FEEDBACK_01",nativeTick=0})
local checkpoint=a:capture({backendWriterClosed=true,bridgeQuiescent=true,sessionId=s.sessionId,
    lifeId=s.lifeId,nativeTick=0,proofKind="NO_BACKEND_CREATED_TECHNICAL_ONLY"})
return{ack=ack,duplicateWasSameAction=duplicate.actionId==ack.actionId,cursor=closed.actionCursor,
    completedOpportunities=closed.completedOpportunities,folderCursor=a.node.ActionCursor.Value,
    checkpoint=checkpoint,NativeTicks=0,scope="MCP_TECHNICAL_CONTROL_NOT_DEE_DECISION"}
