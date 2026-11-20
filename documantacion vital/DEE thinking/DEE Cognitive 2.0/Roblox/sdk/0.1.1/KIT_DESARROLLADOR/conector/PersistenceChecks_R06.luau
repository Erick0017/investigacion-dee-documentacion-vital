-- ComparaciónRO completa antes de nuevaobserve. Sólo pose/CFrame admite1e-5.
local H=game:GetService("HttpService")
local M={}
local function copy(v)return H:JSONDecode(H:JSONEncode(v))end
local function records(folder)local r={};for _,v in ipairs(folder:GetChildren())do r[v.Name]=H:JSONDecode(v.Value)end;return r end
function M.inspect(agent)
 return{namespace=agent.namespace,scenarioFingerprint=agent.runtime.config.ScenarioFingerprint,
  bindings=copy(agent.runtime.config.PersistenceBinding),state=agent:status(),actions=records(agent.node.Actions),tools=records(agent.node.Tools),
  body=agent.adapters.body:capture(),world=agent.adapters.world:capture()}
end
local banned={actions=true,tools=true,bindings=true,state=true,namespace=true,scenariofingerprint=true}
local function poseField(k)
 if type(k)~="string"then return false end;k=string.lower(k)
 return k=="c0"or k=="c1"or string.match(k,"pose$")~=nil or string.match(k,"cframe$")~=nil or string.match(k,"transform$")~=nil
end
function M.compare(expected,actual)
 local differences={};local checked=0;local total=0
 local function diff(path,reason,a,b)total+=1;if #differences<64 then table.insert(differences,{path=path,reason=reason,expected=a,actual=b})end end
 local function visit(a,b,path,tolerant,allowPose)
  checked+=1
  if type(a)~=type(b)then diff(path,"TYPE",type(a),type(b));return end
  if type(a)~="table"then
   if type(a)=="number"and tolerant then if math.abs(a-b)>1e-5 then diff(path,"POSE_TOLERANCE",a,b)end
   elseif a~=b then diff(path,"VALUE",a,b)end;return
  end
  for k,v in pairs(a)do
   local p=path.."/"..tostring(k)
   local allowed=allowPose;if path==""then allowed=k=="body"or k=="world"end
   if type(k)=="string"and banned[string.lower(k)]then allowed=false end
   if b[k]==nil then diff(p,"MISSING_ACTUAL",type(v),nil)else visit(v,b[k],p,allowed and(tolerant or poseField(k)),allowed)end
  end
  for k,v in pairs(b)do if a[k]==nil then diff(path.."/"..tostring(k),"UNEXPECTED_ACTUAL",nil,type(v))end end
 end
 visit(expected,actual,"",false,false)
 return{passed=total==0,checkedValues=checked,differenceCount=total,differences=differences,poseTolerance=1e-5}
end
function M.verifyRestore(agent,snapshot)
 local expected={namespace=snapshot.namespace,scenarioFingerprint=snapshot.scenarioFingerprint,bindings=copy(snapshot.bindings),
  state=copy(snapshot.state),actions=copy(snapshot.actions),tools=copy(snapshot.tools),body=copy(snapshot.body),world=copy(snapshot.world)}
 assert(expected.state.phase=="BOUNDARY","R06_RESTORE_EXPECTED_BOUNDARY")
 expected.state.closeRequested=false -- único cambio explícito de habilitación; sin resetearotro campo.
 local actual=M.inspect(agent);local result=M.compare(expected,actual)
 result.schema="DEE.SDK.RestoreEquality.R06";result.kind="BEFORE_FIRST_NEW_OBSERVE_READ_ONLY";result.nativeExecuted=false
 result.allowedTransition="state.closeRequested true->false only";result.expected=expected;result.actual=actual
 return result
end
function M.verifyBackendLedger(client,contract,snapshot)
 local acknowledged={};for _,v in ipairs(assert(contract.acknowledgedActionIds,"R06_ACK_LEDGER_METADATA_REQUIRED"))do acknowledged[v]=true end
 local checked={}
 for id,receipt in pairs(snapshot.actions)do
  assert(acknowledged[id],"R06_BACKEND_ACTION_ACK_MISSING")
  local wire=H:JSONDecode(receipt.rawRequest);local row=client:operationStatus(id)
  assert(row.operationId==id and row.status=="COMPLETED"and type(row.value)=="table","R06_BACKEND_ACTION_NOT_COMPLETED")
  assert(row.value.action==wire.action.name and row.value.nativeTick==wire.action.nativeTick and row.value.null==wire.action.null,"R06_BACKEND_ACTION_BINDING")
  table.insert(checked,{operationId=id,kind=row.kind,action=row.value.action,nativeTick=row.value.nativeTick,acknowledged=true})
 end
 local feedbackId=assert(snapshot.state.lastFeedbackOperationId,"R06_FEEDBACK_ID_REQUIRED")
 local feedback=client:operationStatus(feedbackId)
 assert(feedback.operationId==feedbackId and feedback.status=="COMPLETED"and feedback.value.accepted==true and feedback.value.nativeTick==snapshot.state.nativeTick,"R06_BACKEND_FEEDBACK_BINDING")
 assert(contract.completedCycles==snapshot.state.completedOpportunities,"R06_BACKEND_CYCLE_CURSOR")
 return{passed=true,actionOperations=checked,feedbackOperationId=feedbackId,completedCycles=contract.completedCycles,kind="GET_ONLY_DURABLE_LEDGER_CHECK"}
end
return M
