-- Another-map pilot: fixed sensors/ports and a geometry-only Humanoid motor.
-- No target selection, anti-loop, arithmetic, teacher or Native memory edit.
local Motor=require(script.Parent.MotorPathfinding_R07)
local A={}
local function pose(actor)return{actor:GetPivot():GetComponents()}end
function A.new(actor,o)
 local source=assert(o.inherited);local points=assert(o.points);local device=assert(o.device)
 local state={stock=source.permissionStock,worldTimeMs=0,signal=-1,
  inventoryKey=source.inventoryKey,inventoryResource=source.inventoryResource,
  numberAPresent=source.numberAPresent,codeBPresent=source.codeBPresent,codeBCurrent=source.codeBCurrent,
  numberAVersion=source.numberAVersion,lastFailure=false,queries=0,skips=0,moves=0,waits=0,
  sourceEnvironment=o.sourceEnvironment,rng={algorithm="NONE"},motorEvents={},contactCertain=true}
 local motor=Motor.new(actor,o.motor,function(kind,data)table.insert(state.motorEvents,{kind=kind,data=data})end,
  function(dt)state.worldTimeMs+=math.floor(dt*1000)end)
 local function contactCode()
  for code,p in pairs(points)do
   local d=motor.root.Position-p
   if Vector3.new(d.X,0,d.Z).Magnitude<=o.motor.ArrivalRadius then return code end
  end
  error("R07_PILOT_PHYSICAL_CONTACT_UNKNOWN_NO_SENSOR_FABRICATED")
 end
 local world={}
 function world:capture()
  assert(not motor.active,"R07_PILOT_CAPTURE_NOT_MOVING")
  return{schema="DEE.R07.PilotWorld.R01",state=table.clone(state),
   device={value=device:GetAttribute("ActuatorValue"),canCollide=device.CanCollide,
    color={device.Color.R,device.Color.G,device.Color.B},transparency=device.Transparency},
   panels={price0=0,price1=0,signal=1},motor=motor:export(),
   declaredTask="TRANSFER_OF_CONNECTOR_TO_ANOTHER_MAP_NOT_FREE_MISSION_OR_NEW_LEARNING"}
 end
 function world:restore(saved)
  assert(saved.schema=="DEE.R07.PilotWorld.R01"and saved.state.rng.algorithm=="NONE","R07_PILOT_WORLD_SCHEMA")
  state=table.clone(saved.state);device:SetAttribute("ActuatorValue",saved.device.value)
  device.CanCollide=saved.device.canCollide;device.Transparency=saved.device.transparency
  device.Color=Color3.new(table.unpack(saved.device.color))
 end
 local body={}
 function body:execute(action)
  local started=os.clock();local r={before=pose(actor),collision=false,invalidAction=false,
   resourceCollected=false,resourceDelivered=false,permissionSpent=0,querySpent=0,tollSpent=0,
   outcome="WAITED",deviceBefore=device:GetAttribute("ActuatorValue")}
  if action.name=="ASK_STATION"then
   local code=contactCode();local panel=assert(o.panels[code])
   if state.stock<1 or(panel.Position-motor.root.Position).Magnitude>8 then
    r.invalidAction=true;r.outcome="QUERY_UNAVAILABLE"
   else
    assert(panel:GetAttribute("Signal")==1 and panel:GetAttribute("Price0")==0 and panel:GetAttribute("Price1")==0,"R07_PILOT_FIXED_PANEL")
    state.stock-=1;state.signal=1;state.queries+=1;r.permissionSpent=1;r.querySpent=1;r.outcome="PANEL_OBSERVED"
    task.wait(.1);state.worldTimeMs+=100
   end
  elseif action.name=="SKIP_STATION"then state.signal=-1;state.skips+=1;r.outcome="QUERY_OMITTED"
  elseif action.name=="SAFE_WAIT"then state.waits+=1;task.wait(.1);state.worldTimeMs+=100
  elseif action.name=="EXIT_0"or action.name=="EXIT_1"then
   local port=action.name=="EXIT_0"and 0 or 1
   -- Absolute endpoints are fixed actuator anatomy. The motor cannot substitute one.
   local result=motor:moveTo(points[port+1],action.actionId or"R07_PILOT_TRANSPORT")
   r.motor=result
   if result.status=="ARRIVED"then
    state.moves+=1;state.contactCertain=true;r.outcome="MOVED"
    device:SetAttribute("ActuatorValue",port);device.CanCollide=port==0
    device.Transparency=port==0 and .15 or .8
    device.Color=port==0 and Color3.fromRGB(220,150,70)or Color3.fromRGB(60,210,175)
    r.deviceActuation={port=port,value=device:GetAttribute("ActuatorValue"),actualCanCollide=device.CanCollide,
     semantic_choice_in_motor=false,prepared_fixed_actuator=true}
   else state.contactCertain=false;r.invalidAction=true;r.outcome="MOTOR_NO_PATH"end
   state.signal=-1
  else r.invalidAction=true;r.outcome="UNSUPPORTED_ACTION"end
  state.lastFailure=r.invalidAction or r.collision
  r.after=pose(actor);r.durationMs=math.floor((os.clock()-started)*1000);r.worldTimeMs=state.worldTimeMs
  r.deviceAfter=device:GetAttribute("ActuatorValue");r.materialConsequence=state.lastFailure
  r.preparedKinematicActuator=false;r.preparedHumanoidPathfinding=true
  return r
 end
 function body:capture()assert(not motor.active);return{schema="DEE.R07.PilotBody.R01",pose=pose(actor)}end
 function body:restore(saved)
  assert(saved.schema=="DEE.R07.PilotBody.R01"and not motor.active)
  actor:PivotTo(CFrame.new(table.unpack(saved.pose))) -- coherent restore only, never a motor waypoint.
 end
 local sensors={}
 function sensors:observe(phase)
  assert(state.contactCertain,"R07_PILOT_NO_NEW_EPISODE_AFTER_UNCERTAIN_PATH")
  if phase=="QUERY_CHOICE"then state.signal=-1 end
  local code=contactCode()
  return{phase=phase,worldTimeMs=state.worldTimeMs,sampleTimeMs=state.worldTimeMs,
   sensors={station=code,stage=state.inventoryResource and 2 or 1,contact=0,
    inventoryKey=state.inventoryKey,inventoryResource=state.inventoryResource,queryAvailable=state.stock>=1,
    stationSignal=state.signal,permissionStock=state.stock,publicContactCode=code,lastFailure=state.lastFailure,
    numberAPresent=state.numberAPresent,codeBPresent=state.codeBPresent,numberAVersion=state.numberAVersion,
    codeBCurrent=state.codeBCurrent,goalDelivery=true}}
 end
 return{body=body,sensors=sensors,world=world}
end
return A
