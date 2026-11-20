-- Sólo anatomía+sensores/consecuencias ambientales. Elección proviene de Native.
local H=game:GetService("HttpService")
local Motor=require(script.Parent.MotorPathfinding_R07)
local Availability=require(script.Parent.DisponibilidadLocal)
local A={}
local function clone(x)return H:JSONDecode(H:JSONEncode(x))end
local function pose(actor)return{actor:GetPivot():GetComponents()}end
function A.new(actor,o)
 local source=assert(o.inherited);local cfg=H:JSONDecode(assert(o.worldRoot:GetAttribute("FocalConfig")))
 assert(type(source.permissionStock)=="number"and source.permissionStock>=cfg.minimumPermissionStock and source.permissionStock<=200,"FOCAL_REAL_STOCK_AT_LEAST18_REQUIRED")
 local state={stock=source.permissionStock,worldTimeMs=0,signal=-1,station=cfg.startStation,epoch=0,
  inventoryKey=source.inventoryKey,inventoryResource=source.inventoryResource,numberAPresent=source.numberAPresent,
  codeBPresent=source.codeBPresent,codeBCurrent=source.codeBCurrent,numberAVersion=source.numberAVersion,
  lastFailure=false,queries=0,skips=0,moves=0,waits=0,tollSpent=0,freePassesUsed=0,
  sourceEnvironment=o.sourceEnvironment,contactCertain=true,motorEvents={},environmentEvents={}}
 local function emit(kind,data)table.insert(state.environmentEvents,{kind=kind,data=data})end
 local motor=Motor.new(actor,o.motor,function(kind,data)table.insert(state.motorEvents,{kind=kind,data=data})end,
  function(dt)state.worldTimeMs+=math.floor(dt*1000)end)
 local gates={};for s=0,5 do gates[s]={};for p=0,1 do gates[s][p]=assert(o.worldRoot.Gates:FindFirstChild("Gate_"..s.."_"..p))end end
 local law=Availability.new(gates,o.panels,cfg,emit)
 local function contactCode(required)
  local params=OverlapParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances={o.worldRoot.Markers}
  local found=nil
  for _,p in ipairs(workspace:GetPartsInPart(motor.root,params))do
   local tag=p:GetAttribute("ContactCode")
   if tag~=nil then assert(type(tag)=="number"and tag%1==0 and tag>=0 and tag<=5 and(found==nil or found==tag),"FOCAL_AMBIGUOUS_CONTACT");found=tag end
  end
  if required then assert(found~=nil,"FOCAL_NO_PHYSICAL_CONTACT_PRESERVED")end
  return found
 end
 local world={}
 function world:capture()
  assert(not motor.active,"FOCAL_NO_CAPTURE_DURING_ACTION")
  return{schema="DEE.Focal.World.R02",state=clone(state),availability=law:capture(),motor=motor:export(),
   device={value=o.device:GetAttribute("ActuatorValue"),canCollide=o.device.CanCollide,color={o.device.Color.R,o.device.Color.G,o.device.Color.B},transparency=o.device.Transparency},
   scope="Focal six-zone apparatus only; paired full Native required separately"}
 end
 function world:restore(saved)
  assert(saved.schema=="DEE.Focal.World.R02"and not motor.active,"FOCAL_WORLD_RESTORE")
  state=clone(saved.state);law:restore(saved.availability)
  o.device:SetAttribute("ActuatorValue",saved.device.value);o.device.CanCollide=saved.device.canCollide
  o.device.Color=Color3.new(table.unpack(saved.device.color));o.device.Transparency=saved.device.transparency
 end
 local body={}
 function body:execute(action)
  local started=os.clock();local r={before=pose(actor),collision=false,invalidAction=false,resourceCollected=false,resourceDelivered=false,
   permissionSpent=0,querySpent=0,tollSpent=0,outcome="WAITED",deviceBefore=o.device:GetAttribute("ActuatorValue")}
  local station=contactCode(true);assert(station==state.station,"FOCAL_STATION_PHYSICAL_MISMATCH")
  if action.name=="ASK_STATION"then
   if state.stock<1 then r.invalidAction=true;r.outcome="QUERY_UNAVAILABLE"
   else
    local sample=law:quoteLocal(station,motor.root);state.stock-=1;state.signal=sample.signal;state.queries+=1
    r.permissionSpent=1;r.querySpent=1;r.outcome="PANEL_OBSERVED";r.panelAudit=sample
    emit("PAID_LOCAL_PANEL",{actionId=action.actionId,station=station,epoch=state.epoch,sample=sample})
   end
   task.wait(.1);state.worldTimeMs+=100
  elseif action.name=="SKIP_STATION"then state.signal=-1;state.skips+=1;r.outcome="QUERY_OMITTED"
  elseif action.name=="SAFE_WAIT"then state.waits+=1;task.wait(.1);state.worldTimeMs+=100
  elseif action.name=="EXIT_0"or action.name=="EXIT_1"then
   local port=action.name=="EXIT_0"and 0 or 1;local target=assert(cfg.edges[tostring(station)][tostring(port)])
   local price=gates[station][port]:GetAttribute("TollCost_C02");assert(price==0 or price==2,"FOCAL_PHYSICAL_PRICE")
   assert((gates[station][port].Position-motor.root.Position).Magnitude<=12,"FOCAL_SELECTED_GATE_NOT_LOCAL")
   r.selectedPort=port;r.originStation=station;r.selectedTarget=target
   if state.stock<price then r.invalidAction=true;r.outcome="DEVICE_BLOCKED"
   else
    state.stock-=price;state.tollSpent+=price;r.permissionSpent=price;r.tollSpent=price
    emit("PORT_ATTEMPT_TOLL",{actionId=action.actionId,station=station,port=port,target=target,price=price})
    local moved=motor:moveTo(o.points[target],action.actionId);r.motor=moved
    if moved.status=="ARRIVED"then
     assert(contactCode(true)==target,"FOCAL_ARRIVAL_CONTACT_MISMATCH_PRESERVED")
     local passage=law:recordVerifiedPassage(station,port,action.actionId,true)
     if passage.freePassUsed then state.freePassesUsed+=1 end
     state.station=target;state.moves+=1;state.contactCertain=true;r.outcome="MOVED";r.passage=passage
     o.device:SetAttribute("ActuatorValue",port);o.device.CanCollide=port==0
     o.device.Color=port==0 and Color3.fromRGB(220,150,70)or Color3.fromRGB(60,210,175)
    else
     r.invalidAction=true;r.outcome="MOTOR_NO_PATH";state.contactCertain=contactCode(false)==station
    end
   end
   state.signal=-1
  else r.invalidAction=true;r.outcome="UNSUPPORTED_ACTION"end
  state.lastFailure=r.invalidAction or r.collision;r.materialConsequence=state.lastFailure
  r.after=pose(actor);r.durationMs=math.floor((os.clock()-started)*1000);r.worldTimeMs=state.worldTimeMs
  r.deviceAfter=o.device:GetAttribute("ActuatorValue");emit("ACTION_EXECUTED",{actionId=action.actionId,name=action.name,result=r})
  return r
 end
 function body:capture()assert(not motor.active);return{schema="DEE.Focal.Body.R02",pose=pose(actor)}end
 function body:restore(saved)assert(saved.schema=="DEE.Focal.Body.R02"and not motor.active);actor:PivotTo(CFrame.new(table.unpack(saved.pose)))end
 local sensors={}
 function sensors:observe(phase)
  assert(state.contactCertain,"FOCAL_UNCERTAIN_CONTACT_NO_NEW_OBSERVATION")
  local station=contactCode(true);assert(station==state.station,"FOCAL_ACTUAL_STATION_ONLY")
  if phase=="QUERY_CHOICE"then state.epoch+=1;law:beginEpoch(state.epoch);state.signal=-1 end
  return{phase=phase,worldTimeMs=state.worldTimeMs,sampleTimeMs=state.worldTimeMs,
   sensors={station=station,stage=state.inventoryResource and 2 or 1,contact=0,
    inventoryKey=state.inventoryKey,inventoryResource=state.inventoryResource,queryAvailable=state.stock>=1,
    stationSignal=state.signal,permissionStock=state.stock,publicContactCode=station,lastFailure=state.lastFailure,
    numberAPresent=state.numberAPresent,codeBPresent=state.codeBPresent,numberAVersion=state.numberAVersion,
    codeBCurrent=state.codeBCurrent,goalDelivery=true}}
 end
 return{body=body,sensors=sensors,world=world}
end
return A
