-- Root-only environmental replay. Requires a fresh isolated DEV Play with
-- Controller disabled. It NEVER requires Bridge, invokes Native, learns or
-- completes Native feedback. Recorded Native output is replayed explicitly.
local HttpService=game:GetService("HttpService")
local ServerStorage=game:GetService("ServerStorage")
local RunService=game:GetService("RunService")
assert(RunService:IsStudio()and RunService:IsRunning(),"REPLAY_STUDIO_PLAY_ONLY")
assert(game:GetService("StudioService"):GetUserId()==11981994305,"REPLAY_OWNER_ACCOUNT")
local package=game:GetService("ServerScriptService"):WaitForChild("RBX01Server")
assert(package.Controller.Disabled==true,"REPLAY_CONTROLLER_MUST_BE_DISABLED")
assert(not ServerStorage:FindFirstChild("RBX01Mailbox_C02"),"REPLAY_NO_BRIDGE_MAILBOX")
assert(not ServerStorage:FindFirstChild("RBX01Checkpoint_C02")and not ServerStorage:FindFirstChild("RBX01Restore_C02"),"REPLAY_NO_ACTIVE_CONTROLLER")
assert(not ServerStorage:FindFirstChild("C02NumericReplayResult"),"REPLAY_ALREADY_EXECUTED_PRESERVED")
local folder=assert(ServerStorage:FindFirstChild("C02NumericReplayPayload"),"REPLAY_PREPARED_PAYLOAD_REQUIRED")
assert(folder:GetAttribute("Protocol")=="DEE.C02.ENV_REPLAY.NUMERIC_LINK.R02"and folder:GetAttribute("Complete")==true,"REPLAY_PAYLOAD_PROTOCOL")
local condition=folder:GetAttribute("Condition")
assert(condition=="INTACT"or condition=="CUT_B","REPLAY_FIXED_CONDITION_ONLY")
local parts={}
for index=1,folder:GetAttribute("Count")do
 local hex=assert(folder:FindFirstChild(string.format("chunk_%05d",index))).Value
 assert(#hex<=32000 and #hex%2==0,"REPLAY_CHUNK_BOUND")
 table.insert(parts,(hex:gsub("..",function(pair)return string.char(tonumber(pair,16))end)))
end
local payload=HttpService:JSONDecode(table.concat(parts))
assert(payload.schema=="DEE.C02.ENV_REPLAY.NUMERIC_LINK.R02","REPLAY_PAYLOAD_SCHEMA")
local C=require(package.Config)
assert(C.WorldId==payload.world.world_id and C.WorldId=="RBX01_R05_C02_DEV4","REPLAY_DEV_WORLD_ONLY")
assert(C.ScenarioFingerprint==payload.world.scenario_sha256 and C.MaxCycles==4,"REPLAY_SAME_FROZEN_WORLD")
assert(not ServerStorage:FindFirstChild(C.EventLogName),"REPLAY_FRESH_BODY_REQUIRED")
local Body=require(package.Body_C02)
local State=require(package.EstadoPareja_C02)
local B=Body.new("ENVIRONMENTAL_REPLAY_"..condition)
local restored=State.apply(B,payload.world,payload.restore_expected)
assert(restored.restored==true and B.S.nativeTick==950523 and B.S.station==2 and B.S.cycle==2,
 "REPLAY_EXACT_HISTORICAL_BOUNDARY")
assert(B.S.numberAPresent==true and B.S.numberA==payload.toolResult.inputs[1]and B.S.codeBPresent==false,"REPLAY_ACTUAL_A_PRESENT")
local initial=HttpService:JSONDecode(HttpService:JSONEncode(B.S))
B:emit("ENV_REPLAY_BEGIN",{condition=condition,scope="WORLD_ONLY_NO_NATIVE_EXECUTION",
 sourceWorldSha256=payload.provenance.world_sha256,sourceFunctionId=payload.provenance.operation_id,
 sourceFunctionSha256=payload.provenance.primary_sha256,actionsExternallyReplayed=true})
local controls={};local functionResults={}
for cycle=3,4 do
 B:beginCycle(cycle)
 local i=(cycle-3)*2
 local q1=B:observe("QUERY_CHOICE")
 local a1=payload.actions[i+1]
 assert(a1.name=="ASK_STATION"and a1.nativeTick==nil,"REPLAY_RECORDED_QUERY_NO_FAKE_NATIVE_TICK")
 local r1,err1=B:execute(a1);assert(r1,err1)
 local q2=B:observe("ROUTE_CHOICE")
 local a2=payload.actions[i+2]
 assert(a2.name=="EXIT_0"and a2.nativeTick==nil,"REPLAY_RECORDED_ROUTE_NO_FAKE_NATIVE_TICK")
 local r2,err2=B:execute(a2);assert(r2,err2)
 if cycle==3 then
  assert(B.pendingTool and B.pendingTool.kind=="CALCULATE"and B.pendingTool.slot=="B"and B.pendingTool.form==payload.toolResult.form,
   "REPLAY_RECORDED_FUNCTION_INTERFACE_REQUIRED")
  assert(B.pendingTool.left==payload.toolResult.inputs[1]and B.pendingTool.right==payload.toolResult.inputs[2],"REPLAY_INPUTS_MATCH_ARCHIVED_NATIVE")
  local value=HttpService:JSONDecode(HttpService:JSONEncode(payload.toolResult))
  value.replayedFromArchivedNative=true;value.capability_execution_admitted=false
  if condition=="CUT_B"then value.numeric_result=nil;value.formed=false end
  B:emit("ENV_REPLAY_TOOL_VALUE",{condition=condition,NativeExecuted=false,sourceFunctionId=payload.provenance.operation_id,
      actualRecordedValue=payload.toolResult.numeric_result,valuePresent=condition=="INTACT"})
  local status=B:applyTool(value,r2)
  table.insert(functionResults,{cycle=cycle,status=status,codePresent=B.S.codeBPresent,
      actualCode=B.S.finalCode,NativeExecuted=false})
 else assert(B.pendingTool==nil,"REPLAY_UNEXPECTED_NEW_FUNCTION")end
 -- This updates environmental lastFailure/consequence as the original controller
 -- did. No feedback RPC, Native admission, counter increment or learning occurs.
 local consequence=B:feedbackFields(r2,a2,q2,r1)
 -- Body's completedCycles is the environmental loop cursor in this replay.
 -- Advance it explicitly so cycle4 is legal; Native is NOT advanced or called.
 B.S.completedCycles=cycle
 B:emit("ENV_REPLAY_WORLD_CYCLE_CLOSED",{environmentCompletedCycle=cycle,
     archivedNativeCompletedCycles=initial.completedCycles,NativeExecuted=false,NativeTicksExecuted=0})
 table.insert(controls,{cycle=cycle,queryResult=r1,routeResult=r2,environmentalConsequence=consequence,
     observationQ1=q1,observationQ2=q2,NativeFeedbackSent=false})
end
assert(B.S.nativeTick==initial.nativeTick and B.S.completedCycles==4,"REPLAY_FIXED_WORLD_CURSOR_AND_NATIVE_TICK")
local final=HttpService:JSONDecode(HttpService:JSONEncode(B.S))
local result={schema="DEE.C02.ENV_REPLAY.NUMERIC_LINK.RESULT.R02",condition=condition,
 scope="ENVIRONMENT_ONLY_REPLAY_NOT_NATIVE_REPRODUCTION_OR_LEARNING",NativeExecuted=false,NativeTicksExecuted=0,
 sourceNativeLifeId=payload.world.native_life_id,sourceNativeTick=payload.world.native_tick,
 archivedNativeCompletedCycles=initial.completedCycles,environmentReplayCompletedCycles=B.S.completedCycles,
 initial=initial,final=final,controls=controls,functionResults=functionResults,
 bodyPose={B.body:GetPivot():GetComponents()},events=B.events,poseTrace=B.poseTrace,
 physical=State.capturePhysical(B.world),sourceProvenance=payload.provenance,
 NativeContinuationCheckpoint=false,hostSelectedAllActions=true}
local raw=HttpService:JSONEncode(result)
local out=Instance.new("Folder");out.Name="C02NumericReplayResult";out:SetAttribute("Protocol",result.schema)
out:SetAttribute("TotalBytes",#raw);out:SetAttribute("Complete",false);out.Parent=ServerStorage
local count=0
for first=1,#raw,16000 do
 count+=1;local t={};for j=first,math.min(first+15999,#raw)do table.insert(t,string.format("%02x",string.byte(raw,j)))end
 local v=Instance.new("StringValue");v.Name=string.format("chunk_%05d",count);v.Value=table.concat(t);v.Parent=out
end
out:SetAttribute("Count",count);out:SetAttribute("Complete",true)
return {schema=result.schema,condition=condition,bytes=#raw,count=count,
 resourceDelta=final.resourceCount-initial.resourceCount,codeRejectedDelta=final.codeRejected-initial.codeRejected,
 stockDelta=final.permissionStock-initial.permissionStock,worldTimeDelta=final.worldTime-initial.worldTime,
 NativeTicksExecuted=0,NativeExecuted=false,hostSelectedAllActions=true}
