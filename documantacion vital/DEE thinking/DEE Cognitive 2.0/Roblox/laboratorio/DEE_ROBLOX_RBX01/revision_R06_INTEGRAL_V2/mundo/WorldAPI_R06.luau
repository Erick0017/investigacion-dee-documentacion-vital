-- Operator transport, not a decision policy. All actions carry explicit provenance.
local H=game:GetService('HttpService')
local SS=game:GetService('ServerStorage')
local C=require(script.Parent.Config)
local Body=require(script.Parent.Body_C02)
local State=require(script.Parent.EstadoPareja_C02)
local API={}; local B=nil;local phase='UNINITIALIZED';local commands={}
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
 local restored=State.apply(B,state,expected)
 -- Technical clone identity only. Contents, products, counters, pose and history survive.
 local old={world_id=state.world_id,life=B.S.lifeId,session=B.S.sessionId,tick=B.S.nativeTick}
 B.S.lifeId=identity.life;B.S.sessionId=identity.session
 B.participant=identity.participant
 lastAction=state.boundary.last_action_id;lastFeedback=state.boundary.last_feedback_operation_id
 commands=deep((state.controller or {}).r06_commands or {})
 phase='BOUNDARY'
 B:emit('R06_TECHNICAL_IDENTITY',{parent=old,current=identity,
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
  if phase=='Q2' and B.S.cycle<=22 and actualName~='SAFE_WAIT' then
   -- Frozen prepared logistics. Never call this a Native route choice.
   action=deep(action);action.name='EXIT_0'
   B:emit('ASSISTED_ORDER',{native_action=actualName,executed_action=action.name,
    actionId=action.actionId,host_prepared_order=true,Native_number_unmodified=true})
  end
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
 r06_commands=deep(commands)}
 return State.capture(B,{checkpoint_id=id,world_id=C.WorldId,scenario_sha256=C.ScenarioFingerprint,
 native_life_id=B.S.lifeId,native_tick=B.S.nativeTick,boundary=boundary(),controller=controller,
 bridge={session_id=B.S.sessionId,server_id='R06_DIRECT_MCP',phase='READY_QUERY',pending_count=0,uncertain_count=0},
 rng={algorithm='PREDECLARED_EVENT_TABLE_V1',cycle=B.S.cycle,scenario_sha256=C.ScenarioFingerprint},
 managed_roots={'Gates','Pickups','ContactMarkers_C02','LocalPricePanels_C02','Devices_C02'}})
end
function API.status()initialized();return {S=deep(B.S),phase=phase,events=#B.events,poses=#B.poseTrace}end
return API
