-- SalidaRO enVMnormal; no requierelookupdelcacheMCP. Nunca observa, actúa o llamaNative.
local H=game:GetService("HttpService");local SS=game:GetService("ServerStorage")
local M={}
local function folder(parent,name)local f=parent:FindFirstChild(name);if f then assert(f:IsA("Folder"),"R06_EVIDENCE_CONFLICT");return f end;f=Instance.new("Folder");f.Name=name;f.Parent=parent;return f end
function M.attach(handle)
 local root=folder(SS,"DEE_SDK_R06_EVIDENCE");local f=folder(root,handle.client.instanceId)
 assert(not f:FindFirstChild("ReadOnlyExport"),"R06_EVIDENCE_ALREADY_BOUND")
 local counter=0
 local function inspect()
  local agent=handle.prepared.agent;local o={schema="DEE.SDK.ReadOnlyState.R06",checkpoint=false,agent=agent:status(),phase=handle.phase,native=false}
  local bOk,b=pcall(function()return agent.adapters.body:capture()end);o.bodyCaptureOK=bOk;if bOk then o.body=b else o.bodyError=tostring(b)end
  local wOk,w=pcall(function()return agent.adapters.world:capture()end);o.worldCaptureOK=wOk;if wOk then o.world=w else o.worldError=tostring(w)end
  return o
 end
 local bridge=Instance.new("BindableFunction");bridge.Name="ReadOnlyExport";bridge.OnInvoke=function()return H:JSONEncode(inspect())end;bridge.Parent=f
 function handle:publish(kind,data)
  counter+=1;local v=Instance.new("StringValue");v.Name=string.format("E%04d_%s",counter,kind)
  v.Value=H:JSONEncode({schema="DEE.SDK.Event.R06",kind=kind,instanceId=self.client.instanceId,sessionId=self.contract.sessionId,data=data});v.Parent=f
 end
 function handle:publishState(kind)self:publish(kind,inspect())end
 return f
end
return M
