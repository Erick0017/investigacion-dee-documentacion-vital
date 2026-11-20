-- Ejecutar como Script normal en ServerScriptService, NO como require enVMdelplugin.
-- Sólo capturaRO y salida forense; NO observe/acción/completeFeedback/_save/HTTP/Native.
local H=game:GetService("HttpService")
local SS=game:GetService("ServerStorage")
local SSS=game:GetService("ServerScriptService")
local Run=game:GetService("RunService")
assert(Run:IsServer()and Run:IsStudio()and Run:IsRunning(),"FORENSIC_NORMAL_SERVER_PLAY_REQUIRED")
local folder=SS:FindFirstChild("DEE_SDK_FORENSIC_CAPTURE")
if folder then assert(folder:IsA("Folder"),"FORENSIC_OUTPUT_CONFLICT")
else folder=Instance.new("Folder");folder.Name="DEE_SDK_FORENSIC_CAPTURE";folder.Parent=SS end
local function output(name,value)
 assert(not folder:FindFirstChild(name),"FORENSIC_OUTPUT_EXISTS_PRESERVE")
 local v=Instance.new("StringValue");v.Name=name;v.Value=value;v.Parent=folder
end
output("STATUS","CAPTURE_STARTED_READ_ONLY")
local function rawValues(node)
 local rows={};if not node then return rows end
 for _,v in ipairs(node:GetDescendants())do
  if v:IsA("StringValue")or v:IsA("IntValue")or v:IsA("BoolValue")or v:IsA("NumberValue")then
   table.insert(rows,{path=v:GetFullName(),class=v.ClassName,value=v.Value})
  end
 end
 return rows
end
local out={schema="DEE.SDK.SAME_SERVER_VM_FORENSIC.R01",kind="PARTIAL_FORENSIC_NOT_BOUNDARY_CHECKPOINT",
 checkpoint=false,restoreCertified=false,nativeExecuted=false,httpRequested=false,observationsCreated=0,
 completedFeedbackCalls=0,stateWrites=0,credentialPrinted=false,
 scope="Agent/body/worldliteral if original normal-server ModuleScript cache is accessible; no fakephase/tick/pair."}
local ok,err=xpcall(function()
 local pkg=assert(SSS:FindFirstChild("DEEConnector_R07"),"FORENSIC_PACKAGE_MISSING")
 local cfg=require(pkg.SDKConfig)
 out.experienceId=cfg.ExperienceId;out.sceneId=cfg.SceneId;out.agentId=cfg.AgentId
 out.scenarioFingerprint=cfg.ScenarioFingerprint
 local api=require(pkg.Main)
 local lookupOK,agent=pcall(function()return api.lookupRuntime(cfg.ExperienceId,cfg.SceneId):get(cfg.AgentId)end)
 out.originalAgentObjectAvailable=lookupOK
 if lookupOK then
  local before=agent:status();out.agentStatusBefore=before
  local bodyOK,body=pcall(function()return agent.adapters.body:capture()end)
  out.bodyLiteralCaptureOK=bodyOK
  if bodyOK then out.bodyLiteral=body else out.bodyLiteralError=tostring(body)end
  local worldOK,world=pcall(function()return agent.adapters.world:capture()end)
  out.worldLiteralCaptureOK=worldOK
  if worldOK then out.worldLiteral=world else out.worldLiteralError=tostring(world)end
  out.agentNodeValues=rawValues(agent.node)
  local after=agent:status();out.agentStatusAfter=after
  out.agentStatusSameAcrossCapture=H:JSONEncode(before)==H:JSONEncode(after)
  out.agentTickIsOnlyLastCompletedFeedbackTick=true
  out.requiresActualNativeProofSeparately=true
 else out.lookupError=tostring(agent)end
 out.registryValues=rawValues(SS:FindFirstChild("DEE_Runtime"))
 out.transportValues=rawValues(SS:FindFirstChild("DEE_SDK_Transport")) -- never PrivateConnection
 local w=workspace:FindFirstChild(cfg.Map.RootName)
 if w then
  local actor=w:FindFirstChild("DEE_Demo")or w:FindFirstChild("DEE_Focal")
  if actor then out.bodyDirectPose={actor:GetPivot():GetComponents()}end
 end
end,function(e)return tostring(e)end)
if not ok then out.captureError=err end
local encodedOK,encoded=pcall(function()return H:JSONEncode(out)end)
if not encodedOK then
 encoded=H:JSONEncode({schema=out.schema,checkpoint=false,nativeExecuted=false,
 error="FORENSIC_JSON_ENCODE_FAILED",details=tostring(encoded)})
end
output("RESULT_JSON",encoded)
-- Duplicate component values permit compact retrieval without truncating thefull packet.
if out.bodyLiteralCaptureOK then output("BODY_LITERAL_JSON",H:JSONEncode(out.bodyLiteral))end
if out.worldLiteralCaptureOK then output("WORLD_LITERAL_JSON",H:JSONEncode(out.worldLiteral))end
local status=folder:FindFirstChild("STATUS")
status.Value=out.originalAgentObjectAvailable and out.bodyLiteralCaptureOK and out.worldLiteralCaptureOK and"CAPTURED_LITERAL_PARTIAL_NOT_CHECKPOINT"or"FORENSIC_PARTIAL_LOOKUP_OR_CAPTURE_FAILED"
