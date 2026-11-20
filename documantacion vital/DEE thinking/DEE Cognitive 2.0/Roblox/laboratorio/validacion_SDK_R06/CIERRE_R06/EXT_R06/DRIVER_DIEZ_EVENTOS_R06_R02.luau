-- R02 technical GET-only recovery; no Native POST replay or answer evaluation.
local H=game:GetService("HttpService");local SS=game:GetService("ServerStorage")
local f=assert(SS:FindFirstChild("R06_CAP_DRIVER"));local api=assert(SS:FindFirstChild("DEE_SDK_EXT_R06"))
assert(string.sub(f.Status.Value,1,15)=="ERROR_PRESERVED","Exact stopped driver required")
assert(not f:FindFirstChild("RESUME4_R02_STARTED"),"Resume already exists")
local initial=H:JSONDecode(assert(f:FindFirstChild("E04_SUBMITTED")).Value)
assert(initial.operationId=="ext_cap_c2847f26-47db-4cd8-9974-35ad02ce9004","Same original in-flight ID")
local function note(name,value)local v=Instance.new("StringValue");v.Name=name;v.Value=H:JSONEncode(value);v.Parent=f end
note("R01_ERROR_PRESERVED",{status=f.Status.Value,retained=true})
note("RESUME4_R02_STARTED",{operationId=initial.operationId,getOnlyForExisting=true,newNativePostReplay=false})
local requests=H:JSONDecode([=[[{"kind":"RECALL","form":"luma"},{"kind":"COMPARE","left":5,"right":4},{"kind":"COMPARE","left":4,"right":5},{"kind":"COMPARE","left":5,"right":5},{"kind":"NUMERIC","operation":"suma","left":4,"right":5},{"kind":"COMPOSE","forms":["luma","nara"],"data":[4,5,2]},{"kind":"LESSON","form":"luma","observedSign":-1,"revision":true,"teacherMode":"paired"},{"kind":"RECALL","form":"luma"},{"kind":"LESSON","form":"luma","observedSign":1,"revision":true,"teacherMode":"paired"},{"kind":"RECALL","form":"luma"}]]=])
local function poll(id,index)
 local errors=0
 while os.time()<1795028441 do
  local r=api.GetOperationRO:Invoke(id)
  if not(r.ok and r.result and r.result.operation)then
   errors+=1;note("R02_GET_ERROR_"..index.."_"..errors,{operationId=id,error=r,materialResubmitted=false})
   assert(errors<=5,"Repeated transport read failure; preserve original ID")
   task.wait(2)
  else
   errors=0;local row=r.result.operation
   f.Status.Value="R02_EVENT_"..index.."_"..row.status.."_"..id
   if row.status=="COMPLETED"then return row end
   assert(row.status~="UNCERTAIN"and row.status~="FAILED_KNOWN","Material failure preserved; no replay")
   task.wait(2)
  end
 end
 error("Finite CAP deadline")
end
task.spawn(function()
 local ok,err=xpcall(function()
  for index=4,10 do
   local id
   if index==4 then id=initial.operationId
   else
    assert(not f:FindFirstChild(string.format("E%02d_SUBMITTED",index)),"No repeated submission")
    assert(os.time()<1795026641,"Last new admission cutoff")
    local r=api.SubmitCapability:Invoke(requests[index]);assert(r.ok and r.result and r.result.operationId,"New submit refused")
    id=r.result.operationId;note(string.format("E%02d_SUBMITTED",index),{index=index,request=requests[index],operationId=id,operatorInitiated=true,answerComputedByDriver=false})
   end
   local result=poll(id,index);note(string.format("E%02d_COMPLETED",index),{index=index,operationId=id,status=result.status})
  end
  local c=api.CloseCapabilities:Invoke();assert(c.ok and c.result and c.result.operationId,"Close refused")
  note("CLOSE_SUBMITTED",{operationId=c.result.operationId});poll(c.result.operationId,11);f.Status.Value="CLOSED_ALL_TEN"
 end,function(e)return tostring(e)end)
 if not ok then f.Status.Value="ERROR_PRESERVED_R02: "..err;note("ERROR_R02",{message=err,automaticMaterialRetry=false})end
end)
return {resumed=true,existingOperationId=initial.operationId,repeatedNativePosts=0}
