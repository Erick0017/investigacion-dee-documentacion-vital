-- Predeclared API exercise. Operator chooses request/order; no answer is computed or inspected.
local H=game:GetService("HttpService")
local SS=game:GetService("ServerStorage")
local api=assert(SS:FindFirstChild("DEE_SDK_EXT_R06"))
assert(not SS:FindFirstChild("R06_CAP_DRIVER"),"Driver already exists; reconcile")
local f=Instance.new("Folder");f.Name="R06_CAP_DRIVER";f.Parent=SS
local state=Instance.new("StringValue");state.Name="Status";state.Value="STARTING";state.Parent=f
local planned=Instance.new("StringValue");planned.Name="PredeclaredRequests";planned.Value=[=[[{"kind":"RECALL","form":"luma"},{"kind":"COMPARE","left":5,"right":4},{"kind":"COMPARE","left":4,"right":5},{"kind":"COMPARE","left":5,"right":5},{"kind":"NUMERIC","operation":"suma","left":4,"right":5},{"kind":"COMPOSE","forms":["luma","nara"],"data":[4,5,2]},{"kind":"LESSON","form":"luma","observedSign":-1,"revision":true,"teacherMode":"paired"},{"kind":"RECALL","form":"luma"},{"kind":"LESSON","form":"luma","observedSign":1,"revision":true,"teacherMode":"paired"},{"kind":"RECALL","form":"luma"}]]=];planned.Parent=f
local requests=H:JSONDecode(planned.Value)
local function note(name,value)
 local v=Instance.new("StringValue");v.Name=name;v.Value=H:JSONEncode(value);v.Parent=f
end
local function poll(id,index)
 while os.time()<1795028441 do
  local r=api.GetOperationRO:Invoke(id)
  assert(r.ok and r.result and r.result.operation,"Transport read failed; preserve original ID")
  local row=r.result.operation
  state.Value="EVENT_"..index.."_"..row.status.."_"..id
  if row.status=="COMPLETED" then return row end
  assert(row.status~="UNCERTAIN" and row.status~="FAILED_KNOWN","Preserved event failure; no replay")
  task.wait(1)
 end
 error("Finite CAP deadline; preserve original ID")
end
task.spawn(function()
 local ok,err=xpcall(function()
  for index,request in ipairs(requests)do
   local id
   if index==1 then id="ext_cap_cc6b5511-721a-4842-846f-d5d4eec7eb1d"
   else
    assert(os.time()<1795026641,"Last new CAP admission cutoff")
    local r=api.SubmitCapability:Invoke(request)
    assert(r.ok and r.result and r.result.operationId,"Submit refused; preserve local intent")
    id=r.result.operationId
   end
   note(string.format("E%02d_SUBMITTED",index),{index=index,request=request,operationId=id,operatorInitiated=true,answerComputedByDriver=false})
   local result=poll(id,index)
   note(string.format("E%02d_COMPLETED",index),{index=index,operationId=id,status=result.status})
  end
  local c=api.CloseCapabilities:Invoke()
  assert(c.ok and c.result and c.result.operationId,"Close refused; preserve intent")
  note("CLOSE_SUBMITTED",{operationId=c.result.operationId})
  poll(c.result.operationId,11)
  state.Value="CLOSED_ALL_TEN"
 end,function(e)return tostring(e)end)
 if not ok then state.Value="ERROR_PRESERVED: "..err;note("ERROR",{message=err,automaticRetry=false})end
end)
return {started=true,adoptedFirstOperation=true,newSubmitsAtMost=9,hostOrdered=true,noAnswerEvaluation=true}
