-- R06 keeps literal unreservedIDs and adds boundedresourcewait.
-- Revision TRANSPORT_R02: IDs already validated URL-unreserved; preserve literalpath/query.
-- HTTP local privado; sólo transporte/idempotencia. Nunca decide ni rePOSTea material.
local H=game:GetService("HttpService")
local Storage=game:GetService("ServerStorage")
local M={};local Client={};Client.__index=Client
local function id(v)assert(type(v)=="string"and #v>0 and #v<=160 and not string.find(v,"[^%w_%-%.]"),"SDK_IDENTIFIER");return v end
local function folder(parent,name)local n=parent:FindFirstChild(name);if n then assert(n:IsA("Folder"),"SDK_STORAGE_CONFLICT");return n end;n=Instance.new("Folder");n.Name=name;n.Parent=parent;return n end
local function text(parent,name)local n=parent:FindFirstChild(name);if n then assert(n:IsA("StringValue"),"SDK_STORAGE_CONFLICT");return n end;n=Instance.new("StringValue");n.Name=name;n.Value="";n.Parent=parent;return n end
local function childValue(parent,name)local v=parent and parent:FindFirstChild(name);assert(v and v:IsA("StringValue")and #v.Value>0,"SDK_PRIVATE_CONNECTION_REQUIRED_"..name);return v.Value end
function M.readPrivateConnection(cfg)
 local p=Storage:FindFirstChild(cfg.PrivateConnectionFolder or"DEE_SDK_PrivateConnection")
 return{BaseUrl=childValue(p,"BaseUrl"),InstanceId=childValue(p,"InstanceId"),Token=childValue(p,"Token")}
end
function M.new(connection,cfg)
 local base=assert(connection.BaseUrl);assert(type(base)=="string"and not string.find(base,"@"),"SDK_ENDPOINT_NO_EMBEDDED_CREDENTIALS")
 assert(string.match(base,"^http://127%.0%.0%.1:%d+$")or string.match(base,"^http://localhost:%d+$"),"SDK_LOCAL_ENDPOINT_ONLY_0_1_0")
 local instance=id(connection.InstanceId);assert(type(connection.Token)=="string"and #connection.Token>0,"SDK_PRIVATE_TOKEN_REQUIRED")
 local root=folder(Storage,"DEE_SDK_Transport");local node=folder(root,instance)
 local self=setmetatable({base=base,instanceId=instance,token=connection.Token,cfg=cfg,node=node,ledger=folder(node,"Operations"),status=text(node,"Status")},Client)
 self.status.Value="CLIENT_PREPARED_NO_NATIVE_REQUEST";return self
end
function Client:_request(method,path,body)
 local options={Url=self.base..path,Method=method,Headers={Authorization="Bearer "..self.token,["Content-Type"]="application/json"}}
 if body~=nil then options.Body=H:JSONEncode(body)end
 local reply=H:RequestAsync(options)
 local ok,decoded=pcall(function()return H:JSONDecode(reply.Body)end)
 assert(ok and type(decoded)=="table","SDK_HTTP_NON_JSON_PRESERVED")
 if not reply.Success or decoded.ok~=true then
  local code=type(decoded.error)=="table"and decoded.error.code or tostring(reply.StatusCode)
  error("SDK_HTTP_"..tostring(code),0)
 end
 assert(decoded.result~=nil,"SDK_HTTP_RESULT_REQUIRED");return decoded.result
end
function Client:setWindow(contract)
 assert(type(contract.lastNewUtcEpoch)=="number"and type(contract.hardFinishUtcEpoch)=="number"and contract.lastNewUtcEpoch<contract.hardFinishUtcEpoch,"R06_FINITE_BACKEND_WINDOW_REQUIRED")
 self.lastNewUtcEpoch=contract.lastNewUtcEpoch;self.hardFinishUtcEpoch=contract.hardFinishUtcEpoch
end
function Client:pastHardDeadline()return self.hardFinishUtcEpoch~=nil and os.time()>=self.hardFinishUtcEpoch end
function Client:handshake()return self:_request("GET","/v1/instances/"..id(self.instanceId).."/handshake")end
function Client:waitReadyHandshake()
 local started=os.clock();local limit=self.cfg.StartupWaitSeconds or 900
 assert(type(limit)=="number"and limit>=1 and limit<=3600,"SDK_FINITE_STARTUP_DEADLINE")
 while os.clock()-started<limit do
  local contract=self:handshake();self:setWindow(contract)
  assert(not self:pastHardDeadline(),"R06_BACKEND_HARD_DEADLINE")
  if contract.status=="READY"then self.status.Value="BACKEND_READY_NO_NATIVE_REQUEST";return contract end
  assert(contract.status=="STARTING"or contract.status=="PENDING_RESOURCE","SDK_BACKEND_HANDSHAKE_STATE")
  self.status.Value="WAITING_BACKEND_READY_NO_NATIVE_REQUEST";task.wait(self.cfg.PollIntervalSeconds or 2)
 end
 error("SDK_BACKEND_STARTUP_DEADLINE_NO_NATIVE_REQUEST",0)
end
function Client:getStatus()return self:_request("GET","/v1/instances/"..id(self.instanceId).."/status")end
function Client:operationStatus(operationId)return self:_request("GET","/v1/operations/"..id(operationId).."?instanceId="..id(self.instanceId))end
function Client:newOperation(kind)return id("sdk_"..kind.."_"..H:GenerateGUID(false))end
function Client:_save(operationId,value)text(self.ledger,id(operationId)).Value=H:JSONEncode(value)end
function Client:_read(operationId)local n=self.ledger:FindFirstChild(operationId);return n and H:JSONDecode(n.Value)or nil end
function Client:assertQuiescent()
 for _,entry in ipairs(self.ledger:GetChildren())do
  local r=H:JSONDecode(entry.Value)
  assert(r.status=="ACKNOWLEDGED"or r.status=="COMMITTED"or r.status=="SEALED","SDK_EXISTING_OPERATION_REQUIRES_RECONCILIATION_"..entry.Name)
 end
end
function Client:waitOperation(operationId)
 local started=os.clock();local limit=self.cfg.OperationPollSeconds or 900;assert(type(limit)=="number"and limit>=1 and limit<=3600,"SDK_FINITE_POLL_DEADLINE")
 while os.clock()-started<limit and not self:pastHardDeadline()do
  local ok,r=pcall(function()return self:operationStatus(operationId)end)
  if ok then
   assert(r.operationId==operationId,"SDK_OPERATION_ID_MISMATCH")
   local saved=self:_read(operationId)or{operationId=operationId};saved.status=r.status;saved.value=r.value;saved.error=r.error;saved.preNativeAdmissionGuaranteed=r.preNativeAdmissionGuaranteed;saved.nativeAdmissionStarted=r.nativeAdmissionStarted;self:_save(operationId,saved)
   if r.status=="COMPLETED"then assert(r.value~=nil,"SDK_COMPLETED_WITHOUT_VALUE");self.status.Value="COMPLETED_"..operationId;return r.value end
   if r.status=="FAILED_KNOWN"or r.status=="UNCERTAIN"then self.status.Value=r.status.."_PRESERVED_"..operationId;error("SDK_OPERATION_"..r.status.."_PRESERVED",0)end
   assert(r.status=="PENDING"or r.status=="RUNNING"or r.status=="PENDING_RESOURCE","SDK_UNKNOWN_OPERATION_STATE")
  else self.status.Value="STATUS_READ_FAILED_PRESERVED_"..operationId end
  task.wait(self.cfg.PollIntervalSeconds or 2)
 end
 self.status.Value="POLL_DEADLINE_PRESERVED_"..operationId;error("SDK_OPERATION_DEADLINE_UNKNOWN_PRESERVED_"..operationId,0)
end
function Client:postOperation(path,body)
 local op=id(body.operationId);assert(self:_read(op)==nil,"SDK_OPERATION_ALREADY_RECORDED_NO_REPOST")
 assert(#self.ledger:GetChildren()<(self.cfg.MaxOperationRecords or 128),"SDK_FINITE_OPERATION_LEDGER")
 self:_save(op,{operationId=op,status="POST_INTENT",path=path,body=body}) -- headers/token never stored
 self.status.Value="POST_INTENT_"..op
 local ok,r=pcall(function()return self:_request("POST",path,body)end)
 if ok then assert(r.operationId==op,"SDK_SUBMIT_OPERATION_ID")
 else self.status.Value="POST_UNKNOWN_PRESERVED_"..op end
 -- Even after a network/HTTP error only GET reconciliation is allowed here.
 return self:waitOperation(op)
end
function Client:postRecorded(path,body,finalStatus)
 local op=id(body.operationId);assert(self:_read(op)==nil,"SDK_OPERATION_ALREADY_RECORDED_NO_REPOST")
 self:_save(op,{operationId=op,status="POST_INTENT",path=path,body=body})
 local ok,r=pcall(function()return self:_request("POST",path,body)end)
 if not ok then self.status.Value="SYNC_POST_UNKNOWN_PRESERVED_"..op;error("SDK_SYNC_POST_UNKNOWN_PRESERVED_"..op,0)end
 self:_save(op,{operationId=op,status=finalStatus or"ACKNOWLEDGED",path=path,result=r});return r
end
function Client:mark(operationId,status)local r=assert(self:_read(operationId));r.status=status;self:_save(operationId,r)end
M.Client=Client;return M
