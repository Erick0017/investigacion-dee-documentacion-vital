-- Operator transport, not a decision policy. All actions carry explicit provenance.
local H=game:GetService('HttpService')
local SS=game:GetService('ServerStorage')
local C=require(script.Parent.Config)
local Body=require(script.Parent.Body_C02)
local State=require(script.Parent.EstadoPareja_C02)
local API={}; local B=nil;local phase='UNINITIALIZED';local commands={};local diagnosticAllowed=false
local lastAction=nil;local lastFeedback=nil;local lastObs=nil;local lastResult=nil;local queryResult=nil
local function deep(t)return H:JSONDecode(H:JSONEncode(t))end
local function initialized()assert(B,'R06_NOT_INITIALIZED')end
local function boundary()
 return {phase='BOUNDARY',native_phase='IDLE',completed_opportunities=B.S.completedCycles,
 next_opportunity=B.S.completedCycles+1,uncertain=false,last_action_id=lastAction,
 acknowledged_action_id=lastAction,last_feedback_operation_id=lastFeedback}
end
local function sensor(obs)
 local s=obs.sensors
 s.numberAPresent=B.S.numberAPresent;s.codeBPresent=B.S.codeBPresent
 s.codeBCurrent=B.S.codeBPresent and B.S.codeBFromAVersion==B.S.numberAVersion
 s.numberAVersion=B.S.numberAVersion;s.goalDelivery=true
 return obs
end
function API.initialize(state,expected,identity)
 assert(not B and phase=='UNINITIALIZED','R06_INITIALIZE_ONCE')
 assert(game:GetService('RunService'):IsStudio() and game:GetService('RunService'):IsRunning(),'STUDIO_SERVER_REQUIRED')
 assert(game:GetService('StudioService'):GetUserId()==11981994305,'AUTHORIZED_STUDIO_REQUIRED')
 B=Body.new(identity.participant)
 if state.world_id==C.WorldId then
  -- Future R07 restores recreate only declared motor geometry from the captured
  -- full World. The untouched R06 parent first restores without this extra root.
  local folder=workspace.RBX01:FindFirstChild("R07MotorGeometry")
  if not folder then folder=Instance.new("Folder");folder.Name="R07MotorGeometry";folder.Parent=workspace.RBX01 end
 else
  assert(state.world_id==C.SourceWorldId and state.native_tick==C.ParentNativeTick and
   state.S.completedCycles==C.ParentCompletedCycles,"R07_EXACT_PARENT_OR_SAME_REVISION")
 end
 local restored=State.apply(B,state,expected)
 B:enablePathMotor()
 diagnosticAllowed=identity.diagnostic==true
 -- Technical clone identity only. Contents, products, counters, pose and history survive.
 local old={world_id=state.world_id,life=B.S.lifeId,session=B.S.sessionId,tick=B.S.nativeTick}
 B.S.lifeId=identity.life;B.S.sessionId=identity.session
 B.participant=identity.participant
 lastAction=state.boundary.last_action_id;lastFeedback=state.boundary.last_feedback_operation_id
 commands=deep((state.controller or {}).r07_commands or (state.controller or {}).r06_commands or {})
 phase='BOUNDARY'
 B:emit('R07_TECHNICAL_IDENTITY',{parent=old,current=identity,
 Native_memory_edited=false,products_preserved=true,preparation_external=true})
 B:publish()
 return {restored=restored,S=deep(B.S),phase=phase,
 original_events=#state.events,current_events=#B.events,new_Native_ticks=0}
end
function API.call(id,kind,data)
 initialized();assert(type(id)=='string' and #id<180,'R06_COMMAND_ID')
 if commands[id] then
  assert(commands[id].kind==kind and commands[id].payload==H:JSONEncode(data),'R06_CORRELATION_CONFLICT')
  assert(commands[id].status=='COMPLETED','R06_UNCERTAIN_COMMAND_PRESERVED')
  return deep(commands[id].result)
 end
 local row={kind=kind,payload=H:JSONEncode(data),status='RUNNING'};commands[id]=row
 local out=nil
 if kind=='begin' then
  assert(phase=='BOUNDARY','R06_BEGIN_BOUNDARY_ONLY');B:beginCycle(data.cycle)
  phase='Q1';lastObs=sensor(B:observe('QUERY_CHOICE'));queryResult=nil
  out={observation=lastObs,S=deep(B.S)}
 elseif kind=='action' then
  assert(phase=='Q1' or phase=='Q2','R06_ACTION_PHASE')
  local action=data.action;assert(type(action.actionId)=='string','R06_ACTION_ID')
  local actualName=action.name
  -- Execute the actual chosen port unchanged in EVERY evaluative opportunity.
  -- Pathfinding geometry belongs to Body; no route or goal is selected here.
  local result,err=B:execute(action);assert(result,err)
  B.S.previousActionId=action.actionId;lastAction=action.actionId;lastResult=result
  if phase=='Q1' and action.name~='SAFE_WAIT' then
   queryResult=result;phase='Q2';lastObs=sensor(B:observe('ROUTE_CHOICE'))
   out={result=result,observation=lastObs,executed_name=action.name,selected_name=actualName,S=deep(B.S)}
  else
   phase='TOOL';out={result=result,tool=B.pendingTool and deep(B.pendingTool) or nil,
    executed_name=action.name,selected_name=actualName,S=deep(B.S)}
  end
  B:emit('R06_ACTION_ACK',{actionId=action.actionId,executed_name=action.name,
   selected_name=actualName,executionStatus='EXECUTED'})
 elseif kind=='offer_diagnostic' then
  assert(diagnosticAllowed and C.AllowDiagnosticTools and phase=='TOOL'and not B.pendingTool,
   "R07_DIAGNOSTIC_ROLE_AND_BOUNDARY_ONLY")
  assert(data.kind=="CALCULATE"and data.slot=="B"and data.form=="nara","R07_DECLARED_NARA_DIAGNOSTIC_ONLY")
  assert(B.S.numberAPresent and type(B.S.numberA)=="number"and B.S.numberA%1==0 and B.S.numberA>=0 and B.S.numberA<=32,
   "R07_NO_DIAGNOSTIC_EXPECTED_INTERMEDIATE")
  local tuple=assert(B.S.roundOperands,"R07_DIAGNOSTIC_REAL_TUPLE_REQUIRED")
  B.pendingTool={kind="CALCULATE",slot="B",form="nara",left=B.S.numberA,right=tuple.bRight}
  B:emit("OPERATOR_DIAGNOSTIC_INTERFACE",{tool=deep(B.pendingTool),mission_credit=false,
   preparation="Explicit operator probe on diagnostic clone; not a selected destination or contact"})
  out={tool=deep(B.pendingTool),mission_credit=false,operator_initiated=true,S=deep(B.S)}
 elseif kind=='tool' then
  assert(phase=='TOOL' and B.pendingTool,'R06_TOOL_PHASE')
  B.S.nativeTick=data.nativeTick or B.S.nativeTick
  local status=B:applyTool(data.output,lastResult)
  out={executionStatus=status,result=lastResult,S=deep(B.S)}
 elseif kind=='feedback_fields' then
  assert(phase=='TOOL' and not B.pendingTool,'R06_FEEDBACK_PHASE')
  phase='FEEDBACK'
  local fields=B:feedbackFields(lastResult,{actionId=lastAction},lastObs,queryResult)
  fields.lastObservation=deep(lastObs)
  out={feedback=fields,observation=lastObs,S=deep(B.S)}
 elseif kind=='complete' then
  assert(phase=='FEEDBACK' and type(data.operationId)=='string','R06_COMPLETE_PHASE')
  B.S.nativeTick=data.nativeTick or B.S.nativeTick
  B.S.completedCycles+=1
  if lastObs.phase=='ROUTE_CHOICE' then B.S.completedRouteOpportunities+=1 end
  lastFeedback=data.operationId;phase='BOUNDARY';B.S.reason='FRONTERA COMPLETA';B:publish()
  B:emit('FEEDBACK_COMPLETED',{cycle=B.S.cycle,nativeTick=B.S.nativeTick,
   feedbackOperationId=lastFeedback,completeRouteOpportunity=lastObs.phase=='ROUTE_CHOICE'})
  out={S=deep(B.S),boundary=boundary()}
 else error('R06_COMMAND_NOT_ALLOWED') end
 row.status='COMPLETED';row.result=deep(out)
 return out
end
function API.checkpoint(id)
 initialized();assert(phase=='BOUNDARY' and not B.pendingTool,'R06_NO_CHECKPOINT_DURING_ACTION')
 local controller={phase='BOUNDARY',next_opportunity=B.S.completedCycles+1,
 completed_opportunities=B.S.completedCycles,participant=B.participant,
 last_action_id=lastAction,acknowledged_action_id=lastAction,last_feedback_operation_id=lastFeedback,
 r07_commands=deep(commands)}
 local checkpoint=State.capture(B,{checkpoint_id=id,world_id=C.WorldId,scenario_sha256=C.ScenarioFingerprint,
 native_life_id=B.S.lifeId,native_tick=B.S.nativeTick,boundary=boundary(),controller=controller,
 bridge={session_id=B.S.sessionId,server_id='R06_DIRECT_MCP',phase='READY_QUERY',pending_count=0,uncertain_count=0},
 rng={algorithm='PREDECLARED_EVENT_TABLE_V1',cycle=B.S.cycle,scenario_sha256=C.ScenarioFingerprint},
 managed_roots={'Gates','Pickups','ContactMarkers_C02','LocalPricePanels_C02','Devices_C02','DEE_Body','R07MotorGeometry'}})
 checkpoint.motor=B.motor:export();return checkpoint
end
function API.status()initialized();return {S=deep(B.S),phase=phase,events=#B.events,poses=#B.poseTrace,
 motorContactCertain=not B.motorContactUncertain,motorActive=B.motor and B.motor.active or false,diagnosticAllowed=diagnosticAllowed}end
return API
