-- ASSISTED Native client: developer inputs and literal Native outputs. No host answers.
local H=game:GetService("HttpService");local SS=game:GetService("ServerStorage")
local M={};local C={};C.__index=C
local terminal={COMPLETED=true,FAILED_KNOWN=true,UNCERTAIN=true}
local function identifier(v)assert(type(v)=="string"and #v>0 and #v<=90 and not string.find(v,"[^%w_%-]"),"EXT_IDENTIFIER");return v end
local function exact(t,keys)
 assert(type(t)=="table","EXT_REQUEST_OBJECT");local wanted={};for _,k in ipairs(keys)do wanted[k]=true;assert(t[k]~=nil,"EXT_REQUIRED_"..k)end
 for k in pairs(t)do assert(wanted[k],"EXT_UNEXPECTED_FIELD_"..tostring(k))end
end
local function array(t,n)
 assert(type(t)=="table"and #t==n,"EXT_ARRAY_LENGTH")
 for k in pairs(t)do assert(type(k)=="number"and k%1==0 and k>=1 and k<=n,"EXT_ARRAY_KEYS")end
end
local function form(v)assert(v=="luma"or v=="nara","EXT_FORM")end
local function integer(v,low,high)assert(type(v)=="number"and v%1==0 and v>=low and v<=high,"EXT_INTEGER_RANGE")end
function M.validateRequest(r)
 assert(type(r)=="table"and type(r.kind)=="string","EXT_REQUEST_KIND")
 if r.kind=="RECALL"then exact(r,{"kind","form"});form(r.form)
 elseif r.kind=="LESSON"then exact(r,{"kind","form","observedSign","revision","teacherMode"});form(r.form);assert(r.observedSign==1 or r.observedSign==-1,"EXT_SIGN");assert(type(r.revision)=="boolean","EXT_REVISION_BOOL");assert(r.teacherMode=="paired"or r.teacherMode=="omitted"or r.teacherMode=="desync","EXT_TEACHER_MODE")
 elseif r.kind=="NUMERIC"then exact(r,{"kind","operation","left","right"});assert(r.operation=="suma"or r.operation=="diferencia","EXT_OPERATION");integer(r.left,0,32);integer(r.right,0,32)
 elseif r.kind=="SOLVE"then exact(r,{"kind","form","left","right"});form(r.form);integer(r.left,0,32);integer(r.right,0,32)
 elseif r.kind=="COMPOSE"then exact(r,{"kind","forms","data"});array(r.forms,2);array(r.data,3);for _,v in ipairs(r.forms)do form(v)end;for _,v in ipairs(r.data)do integer(v,0,32)end
 elseif r.kind=="COMPARE"then exact(r,{"kind","left","right"});integer(r.left,0,20);integer(r.right,0,20)
 else error("EXT_KIND_NOT_IMPLEMENTED",0)end
 return r
end
local function text(parent,name)local v=parent:FindFirstChild(name);if v then assert(v:IsA("StringValue"),"EXT_STORAGE_CONFLICT");return v end;v=Instance.new("StringValue");v.Name=name;v.Parent=parent;return v end
function M.new(cfg,node,onEvent)
 assert(cfg.NoAutomaticMaterial==true and cfg.Enabled==true,"EXT_EXPLICIT_ENABLE_REQUIRED")
 local p=assert(SS:FindFirstChild(cfg.PrivateConnectionFolder),"EXT_PRIVATE_CONNECTION_REQUIRED")
 local function read(k)local v=p:FindFirstChild(k);assert(v and v:IsA("StringValue")and #v.Value>0,"EXT_CONNECTION_"..k);return v.Value end
 local base=read("BaseUrl");assert(string.match(base,"^http://127%.0%.0%.1:%d+$"),"EXT_AUTHORIZED_LOOPBACK_ONLY")
 local id=identifier(read("InstanceId"));local token=read("Token");assert(#token>=32,"EXT_TOKEN_REQUIRED")
 local ops=node:FindFirstChild("Operations");if ops then assert(ops:IsA("Folder"),"EXT_OPERATION_STORAGE")else ops=Instance.new("Folder");ops.Name="Operations";ops.Parent=node end
 for _,v in ipairs(ops:GetChildren())do local header=v:FindFirstChild("Header");assert(v:IsA("Folder")and header,"EXT_OPERATION_LAYOUT");local row=H:JSONDecode(header.Value);assert(row.status=="COMPLETED"or row.status=="FAILED_KNOWN","EXT_PRESERVED_OPERATION_NO_REOPEN")end
 return setmetatable({cfg=cfg,node=node,ops=ops,instanceId=id,base=base,token=token,onEvent=onEvent,busy=false,records={}},C)
end
function C:_request(method,path,body)
 local opts={Url=self.base..path,Method=method,Headers={Authorization="Bearer "..self.token,["Content-Type"]="application/json"}}
 if body~=nil then opts.Body=H:JSONEncode(body)end
 local reply=H:RequestAsync(opts);local ok,decoded=pcall(function()return H:JSONDecode(reply.Body)end)
 assert(ok and type(decoded)=="table","EXT_HTTP_NON_JSON")
 if not reply.Success or decoded.ok~=true then local code=type(decoded.error)=="table"and decoded.error.code or tostring(reply.StatusCode);error("EXT_HTTP_"..tostring(code),0)end
 assert(decoded.result~=nil,"EXT_HTTP_RESULT");return decoded.result,reply.Body
end
function C:_save(id,row)
 id=identifier(id);self.records[id]=row
 local op=self.ops:FindFirstChild(id)
 if op then assert(op:IsA("Folder"),"EXT_OPERATION_FOLDER")else op=Instance.new("Folder");op.Name=id;op.Parent=self.ops end
 if not op:FindFirstChild("POST_INTENT")then local intent=H:JSONEncode(row.body);assert(#intent<=8192,"EXT_INTENT_BYTE_BOUND");text(op,"POST_INTENT").Value=intent end
 local encoded=H:JSONEncode(row);local first=1;local count=0
 while first<=#encoded do
  local last=math.min(first+15999,#encoded)
  while last<#encoded do local b=string.byte(encoded,last+1);if b>=128 and b<=191 then last-=1 else break end end
  assert(last>=first,"EXT_UTF8_CHUNK_BOUNDARY");count+=1
  text(op,string.format("Chunk_%05d",count)).Value=string.sub(encoded,first,last);first=last+1
 end
 -- Header is written last. Read callbacks run in thisnormalVM and see onecompletecurrentrecord.
 text(op,"Header").Value=H:JSONEncode({operationId=id,status=row.status,kind=row.kind,chunkCount=count,byteCount=#encoded,chunkBytesMaximum=16000,originalTruncated=false})
 if self.onEvent then pcall(self.onEvent,row)end
end
function C:localInfo(id)
 local op=self.ops:FindFirstChild(identifier(id));if not op then return nil end
 return H:JSONDecode(assert(op:FindFirstChild("Header")).Value)
end
function C:readChunk(id,index)
 local info=assert(self:localInfo(id),"EXT_LOCAL_OPERATION_NOT_FOUND");integer(index,1,info.chunkCount)
 return assert(self.ops:FindFirstChild(id):FindFirstChild(string.format("Chunk_%05d",index))).Value
end
function C:readLocal(id)
 id=identifier(id);if self.records[id]then return self.records[id]end
 local info=self:localInfo(id);if not info then return nil end
 local chunks={};for i=1,info.chunkCount do chunks[i]=self:readChunk(id,i)end
 local encoded=table.concat(chunks);assert(#encoded==info.byteCount,"EXT_LOCAL_CHUNK_LENGTH");return H:JSONDecode(encoded)
end
function C:getCapabilities()
 local h,raw=self:_request("GET","/v1/capabilities/handshake")
 assert(h.instanceId==self.instanceId and h.extensionVersion==self.cfg.ExtensionVersion,"EXT_WRONG_INSTANCE_OR_VERSION")
 assert(type(h.sessionId)=="string"and type(h.lifeId)=="string"and type(h.limits)=="table","EXT_HANDSHAKE_CONTEXT")
 assert(h.postK4Guard==true and h.worldBinding=="PRE_CAP_SDK_PAIR_NOT_CURRENT_AFTER_NATIVE_ADVANCE","EXT_POST_K4_PRE_CAP_REQUIRED")
 assert(type(h.capabilities)=="table"and type(h.limits.hardFinishUtcEpoch)=="number"and type(h.limits.lastNewUtcEpoch)=="number","EXT_LIMITS_REQUIRED")
 assert(h.limits.maxTicksPerEvent==4096 and h.limits.globalNativeTicks==40000 and type(h.limits.maxEvents)=="number"and h.limits.maxEvents%1==0 and h.limits.maxEvents>=1 and h.limits.maxEvents<=12,"EXT_FIXED_LIMITS")
 self.contract=h;return h,raw
end
function C:getOperation(id)
 return self:_request("GET","/v1/capability-operations/"..identifier(id).."?instanceId="..identifier(self.instanceId))
end
function C:reconcileOperation(id)
 local answer,raw=self:getOperation(id);assert(answer.operationId==id,"EXT_RECONCILE_ID")
 local row=self:readLocal(id)
 if row then
  row.status=answer.status;row.responseRaw=raw;row.value=answer.value;row.error=answer.error;self:_save(id,row)
  if self.activeId==id and terminal[answer.status]then self.busy=answer.status=="UNCERTAIN";if not self.busy then self.activeId=nil end end
 end
 return answer,raw
end
function C:_start(path,request,close)
 assert(not self.busy,"EXT_ONE_OPERATION_AT_A_TIME")
 self.busy=true -- reserve before the handshake yields; no concurrent submit can pass.
 local prepared,packet=pcall(function()
 if not close then M.validateRequest(request);request=H:JSONDecode(H:JSONEncode(request))end
 local h=self:getCapabilities();assert(h.status=="READY","EXT_BACKEND_NOT_READY_NO_POST")
 assert(os.time()<h.limits.hardFinishUtcEpoch and(close or os.time()<h.limits.lastNewUtcEpoch),"EXT_ADMISSION_DEADLINE_NO_POST")
 if not close then assert(type(h.capabilitySequence)=="number"and h.capabilitySequence<h.limits.maxEvents,"EXT_EVENT_LIMIT_NO_POST");local found=false;for _,kind in ipairs(h.capabilities)do if kind==request.kind then found=true end end;assert(found,"EXT_KIND_NOT_ADVERTISED")end
 assert(#self.ops:GetChildren()<self.cfg.MaxLocalOperations,"EXT_LOCAL_LEDGER_LIMIT")
 local id=identifier("ext_"..(close and"close_"or"cap_")..H:GenerateGUID(false))
 local body={instanceId=self.instanceId,sessionId=h.sessionId,operationId=id};if not close then body.request=request end
 local row={operationId=id,status="POST_INTENT",kind=close and"CLOSE"or request.kind,body=body,assisted=true,source="DEVELOPER_INITIATED",material=true}
 self.activeId=id;self:_save(id,row) -- ID+literalbody existbefore firstPOST; noheader/tokenstored.
 return{h=h,id=id,body=body,row=row}
 end)
 if not prepared then self.busy=false;self.activeId=nil;error(packet,0)end
 local h,id,body,row=packet.h,packet.id,packet.body,packet.row
 task.spawn(function()
  local flowOK,flowError=xpcall(function()
  local posted,result=pcall(function()return self:_request("POST",path,body)end)
  if posted then assert(result.operationId==id,"EXT_SUBMIT_ID")else row.status="SUBMIT_UNKNOWN_PRESERVED";self:_save(id,row)end
  local began=os.clock();local limit=self.cfg.PollDeadlineSeconds;assert(type(limit)=="number"and limit>0 and limit<=3600,"EXT_FINITE_POLL")
  while os.clock()-began<limit and os.time()<h.limits.hardFinishUtcEpoch do
   local ok,answer,raw=pcall(function()return self:getOperation(id)end)
   if ok then
    assert(answer.operationId==id,"EXT_OPERATION_ID_MISMATCH")
    row.status=answer.status;row.responseRaw=raw;row.value=answer.value;row.error=answer.error
    row.preNativeAdmissionGuaranteed=answer.preNativeAdmissionGuaranteed;self:_save(id,row)
    if terminal[answer.status]then self.busy=answer.status=="UNCERTAIN";if not self.busy then self.activeId=nil end;return end
    assert(answer.status=="PENDING"or answer.status=="PENDING_RESOURCE"or answer.status=="RUNNING","EXT_UNKNOWN_STATUS_PRESERVED")
   else row.lastReadError="STATUS_GET_FAILED";self:_save(id,row)end
   task.wait(self.cfg.PollIntervalSeconds)
  end
  row.status="POLL_DEADLINE_UNKNOWN_PRESERVED";self:_save(id,row) -- busy stays true, noautomaticnewID/rePOST
  end,function(e)return tostring(e)end)
  if not flowOK then row.status="CLIENT_ERROR_PRESERVED";row.errorCode=tostring(flowError);self:_save(id,row)end
 end)
 return{operationId=id,status="POST_INTENT",assisted=true,material=true,source="DEVELOPER_INITIATED"}
end
function C:submit(request)return self:_start("/v1/capabilities/submit",request,false)end
function C:close()return self:_start("/v1/capabilities/close",nil,true)end
return M
