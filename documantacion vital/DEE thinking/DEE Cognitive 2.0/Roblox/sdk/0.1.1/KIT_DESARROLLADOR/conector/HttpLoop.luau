-- Plomería de fases: jamás selecciona un puerto ni corrige una salidaNative.
local H=game:GetService("HttpService")
local Transport=require(script.Parent.HttpTransport)
local Bootstrap=require(script.Parent.SDKBootstrap)
local Persistence=require(script.Parent.PersistenceChecks_R06)
local Evidence=require(script.Parent.Evidence_R06)
local M={};local running={}
local allowed={ASK_STATION=true,SKIP_STATION=true,EXIT_0=true,EXIT_1=true,SAFE_WAIT=true}
local function copy(v)return H:JSONDecode(H:JSONEncode(v))end
local function setStatus(handle,value)handle.phase=value;handle.prepared.status.Value=value end
local function executeChoice(handle,kind,observation)
 local client=handle.client;local agent=handle.prepared.agent;local contract=handle.contract
 local op=client:newOperation(kind)
 setStatus(handle,"WAITING_NATIVE_"..string.upper(kind))
 local value=client:postOperation("/v1/native/"..kind,{instanceId=client.instanceId,operationId=op,sessionId=contract.sessionId,payload={observation=copy(observation)}})
 assert(type(value)=="table"and allowed[value.action]and type(value.nativeTick)=="number","SDK_UNSUPPORTED_NATIVE_RESULT_PRESERVED")
 assert(value.operation_id==nil or value.operation_id==op,"SDK_NATIVE_OPERATION_ID")
 local raw={protocol="DEE.RBX.Connector.R01",namespace=agent.namespace,sessionId=contract.sessionId,seq=observation.seq,observationId=observation.observationId,actionId=op,operationId=op,sourceKind="DEE_NATIVE",action={name=value.action,nativeTick=value.nativeTick,null=value.null,actionId=op}}
 setStatus(handle,"EXECUTING_NATIVE_"..value.action)
 local ack=agent:deliverAction(H:JSONEncode(raw))
 assert(ack.actionId==op and ack.operationId==op and ack.observationId==observation.observationId,"SDK_BODY_ACK_ID")
 local ackOp=client:newOperation("action_ack")
 local registered=client:postRecorded("/v1/action-ack",{instanceId=client.instanceId,operationId=ackOp,sessionId=contract.sessionId,actionId=op,observationId=observation.observationId,localSequence=observation.seq,ack=copy(ack)},"ACKNOWLEDGED")
 assert(registered.status=="ACKNOWLEDGED"and registered.actionId==op,"SDK_RUNTIME_ACK_REQUIRED")
 agent:confirmActionAck(op,op);client:mark(op,"ACKNOWLEDGED");handle:publishState("ACTION_ACKNOWLEDGED")
 return value,ack,op
end
local function cycle(handle)
 local agent=handle.prepared.agent;local client=handle.client;local contract=handle.contract
 assert(agent:status().phase=="BOUNDARY","SDK_BOUNDARY_BEFORE_CYCLE")
 local obs=agent:observe("QUERY_CHOICE");local choice,ack,actionId=executeChoice(handle,"decision",obs)
 local spent=assert(ack.result.permissionSpent,"SDK_COST_MEASUREMENT")
 if choice.action~="SAFE_WAIT"then
  obs=agent:observe("ROUTE_CHOICE");choice,ack,actionId=executeChoice(handle,"query_sensor",obs);spent+=assert(ack.result.permissionSpent)
 end
 assert(agent:toolRequest()==nil,"SDK_DEFAULT_MAP_TOOL_UNSUPPORTED_PRESERVED")
 local result=ack.result
 local payload={actionId=actionId,seq=obs.seq,observationId=obs.observationId,worldTimeMs=result.worldTimeMs,durationMs=result.durationMs,outcome=result.outcome,collision=result.collision,resourceCollected=result.resourceCollected,resourceDelivered=result.resourceDelivered,permissionSpent=spent,materialConsequence=result.materialConsequence,lastObservation=copy(obs)}
 local op=client:newOperation("feedback");setStatus(handle,"WAITING_NATIVE_FEEDBACK")
 local returned=client:postOperation("/v1/native/feedback",{instanceId=client.instanceId,operationId=op,sessionId=contract.sessionId,payload=payload})
 assert(type(returned)=="table"and returned.accepted==true,"SDK_FEEDBACK_NOT_ACCEPTED_PRESERVED")
 agent:completeFeedback({actionId=actionId,feedbackOperationId=op,nativeTick=returned.nativeTick});client:mark(op,"COMMITTED")
 setStatus(handle,"CYCLE_BOUNDARY_"..agent:status().completedOpportunities);handle:publishState("FEEDBACK_BOUNDARY")
end
local function saveClose(handle)
 local agent=handle.prepared.agent;local client=handle.client;local contract=handle.contract
 assert(agent:status().phase=="BOUNDARY","SDK_CLOSE_BOUNDARY_ONLY");agent:requestClose();setStatus(handle,"WAITING_NATIVE_SAVE_CLOSE")
 local closeId=client:newOperation("close")
 local result=client:postOperation("/v1/session/close",{instanceId=client.instanceId,operationId=closeId,sessionId=contract.sessionId})
 local proof=assert(result.backendProof,"SDK_NATIVE_CLOSED_PROOF_REQUIRED")
 assert(proof.backendWriterClosed==true and proof.bridgeQuiescent==true,"SDK_NATIVE_NOT_CLOSED")
 local snapshot=agent:capture(proof);handle:publish("CLOSED_CAPTURE",{snapshot=snapshot,backendProof=proof});client:mark(closeId,"COMMITTED")
 local checkpointId=client:newOperation("checkpoint")
 local sealed=client:postRecorded("/v1/checkpoint",{instanceId=client.instanceId,operationId=checkpointId,sessionId=contract.sessionId,snapshot=snapshot},"SEALED")
 assert(sealed.status=="SEALED"and sealed.nativeTick==proof.nativeTick and type(sealed.checkpointSha256)=="string","SDK_CHECKPOINT_NOT_SEALED")
 handle.checkpoint=sealed;handle.closed=true;setStatus(handle,"CLOSED_SEALED_"..sealed.checkpointId);handle:publish("PAIR_SEALED",sealed)
 if handle.cfg.AutoEndStudioTest==true then
  local s=agent:status()
  local meta={schema="DEE.SDK.RunCompletion.R06",status="CLOSED_SEALED",instanceId=client.instanceId,sessionId=contract.sessionId,lifeId=contract.lifeId,
   nativeTick=s.nativeTick,localSequence=s.sequence,completedOpportunities=s.completedOpportunities,checkpoint=sealed,restorationProof=handle.restorationProof,
   scope="Diagnostic completion metadata only; no Native answers or future choices supplied"}
  handle:publish("AUTO_END_REQUESTED_AFTER_SEAL",meta)
  local ended,endError=pcall(function()game:GetService("StudioTestService"):EndTest(meta)end)
  if not ended then handle:publish("AUTO_END_REFUSED",{error=tostring(endError)});warn("DEE_SDK_AUTO_END_REFUSED:"..tostring(endError))end
 end
end
function M.start(cfg)
 assert(cfg.Mode=="NATIVE","SDK_NATIVE_MODE_EXPLICIT_REQUIRED")
 local client=Transport.new(Transport.readPrivateConnection(cfg),cfg.Transport or{})
 assert(not running[client.instanceId],"SDK_INSTANCE_LOOP_ALREADY_EXISTS");client:assertQuiescent()
 local contract=client:waitReadyHandshake()
 assert(contract.instanceId==client.instanceId and contract.protocolVersion=="DEE.RBX.Connector.R01"and contract.runtimeVersion=="0.1.1","SDK_RUNTIME_CONTRACT_VERSION")
 assert(contract.backendKind=="NATIVE_REAL"and contract.technicalControl==false,"SDK_REAL_NATIVE_BACKEND_REQUIRED")
 local prepared=Bootstrap.prepare(cfg,contract);local agent=prepared.agent
 local handle={client=client,contract=contract,prepared=prepared,cfg=cfg,closed=false};running[client.instanceId]=handle
 function handle:requestClose()self.requestedClose=true;return self.prepared.agent:status()end
 function handle:status()return{phase=self.phase,closed=self.closed,error=self.error,checkpoint=self.checkpoint,agent=self.prepared.agent:status()}end
 Evidence.attach(handle)
 local initialized,initialError=xpcall(function()
  if contract.snapshot~=nil then
   assert(contract.backendProof~=nil and type(contract.checkpointSha256)=="string","SDK_PAIRED_RESTORE_PROOF_REQUIRED")
   local expected=copy(contract.backendProof);expected.checkpointSha256=contract.checkpointSha256
   agent:restore(contract.snapshot,expected)
   local comparison=Persistence.verifyRestore(agent,contract.snapshot)
   handle:publish("RESTORE_COMPARISON_BEFORE_OBSERVE",comparison)
   assert(comparison.passed,"R06_RESTORE_EQUALITY_FAILED_BEFORE_OBSERVE")
   local ledger=Persistence.verifyBackendLedger(client,contract,contract.snapshot)
   handle:publish("RESTORE_LEDGER_BEFORE_OBSERVE",ledger)
   local proofId=client:newOperation("restoration_proof")
   local proof={schema="DEE.RBX.RestorationProof.R06",ok=comparison.passed,differences=comparison.differences,differenceCount=comparison.differenceCount,
    poseTolerance=1e-5,actual=comparison.actual,expected=comparison.expected,backendLedgerCheck=ledger}
   local persisted=client:postRecorded("/v1/restoration-proof",{instanceId=client.instanceId,operationId=proofId,sessionId=contract.sessionId,
    checkpointSha256=contract.checkpointSha256,pairSha256=assert(contract.pairSha256,"R06_PAIR_FILE_ANCHOR_REQUIRED"),proof=proof},"COMMITTED")
   assert(persisted.operationId==proofId and persisted.status=="RECORDED"and type(persisted.restorationProofSha256)=="string","R06_RESTORATION_PROOF_NOT_DURABLE")
   handle.restorationProof=persisted;handle:publish("RESTORATION_PROOF_PERSISTED_BEFORE_OBSERVE",persisted)
  else
   assert(contract.localSequence==0 and contract.completedCycles==0,"SDK_NEW_WITH_NONZERO_CURSOR_REJECTED")
   agent:bindSession({sessionId=contract.sessionId,lifeId=contract.lifeId,nativeTick=contract.nativeTick})
   handle:publishState("NEW_BOUNDARY_BEFORE_OBSERVE")
  end
  assert(agent:status().sequence==contract.localSequence and agent:status().completedOpportunities==contract.completedCycles,"SDK_LOCAL_CURSOR_MISMATCH")
 end,function(e)return tostring(e)end)
 if not initialized then
  handle.error=initialError;setStatus(handle,"ERROR_PRESERVED_BEFORE_OBSERVE");handle:publishState("START_ERROR_PRESERVED");error(initialError,0)
 end
 task.spawn(function()
  local ok,err=xpcall(function()
   local count=cfg.RunCycles or 1;assert(type(count)=="number"and count%1==0 and count>=1 and count<=cfg.MaxOpportunities,"SDK_FINITE_RUN_CYCLES")
   for _=1,count do
    local s=agent:status();if handle.requestedClose or s.closeRequested or s.completedOpportunities>=cfg.MaxOpportunities then break end
    assert(not client:pastHardDeadline(),"R06_HARD_DEADLINE_NO_NEW_OBSERVE")
    assert(os.time()<client.lastNewUtcEpoch,"R06_LAST_NEW_DEADLINE_NO_OBSERVE")
    cycle(handle)
   end
   saveClose(handle)
  end,function(e)return tostring(e)end)
  if not ok then handle.error=err;setStatus(handle,"ERROR_PRESERVED_OWNER_RECONCILIATION_REQUIRED");handle:publishState("ERROR_PRESERVED");warn("DEE_SDK: "..err)end
 end)
 return handle
end
function M.get(instanceId)return running[instanceId]end
return M
