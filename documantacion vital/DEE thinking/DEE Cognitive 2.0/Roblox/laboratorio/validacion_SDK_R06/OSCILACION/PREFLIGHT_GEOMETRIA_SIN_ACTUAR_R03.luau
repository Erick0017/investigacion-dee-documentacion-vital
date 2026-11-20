-- RO técnico: calcula viabilidad de los12puertos ya fijados. No mueve el cuerpo ni envía datos aNative.
local Run=game:GetService("RunService")
assert(Run:IsStudio()and Run:IsServer()and Run:IsRunning(),"FOCAL_SERVER_PLAY_REQUIRED")
local pkg=assert(game:GetService("ServerScriptService"):FindFirstChild("DEEConnector_R07"))
local cfg=require(pkg.SDKConfig);assert(cfg.Mode=="PREVIEW","FOCAL_PREFLIGHT_PREVIEW_ONLY")
assert(cfg.MaxOpportunities==6 and cfg.RunCycles==6 and cfg.MaxActions==12,"FOCAL_FIXED_HORIZON")
assert(cfg.Focal.rechargeEpochs==3 and cfg.Focal.tagModeBothArms=="local_tag","FOCAL_FIXED_RULE")
local world=assert(workspace:FindFirstChild(cfg.Map.RootName));local actor=assert(world:FindFirstChild("DEE_Focal"))
local before=actor:GetPivot();local Pathfinding=game:GetService("PathfindingService")
local function v(t)return Vector3.new(t[1],t[2],t[3])end
local rows={};local allReachable=true
for station=0,5 do for port=0,1 do
 local target=cfg.Focal.edges[tostring(station)][tostring(port)];assert(target~=station,"FOCAL_NO_SELF_EDGE")
 local gate=assert(world.Gates:FindFirstChild("Gate_"..station.."_"..port))
 assert(gate.CanCollide==false and gate:GetAttribute("FocalPassAvailable")==true,"FOCAL_INITIAL_PORT_OPEN")
 local motor=cfg.Map.Motor
 local path=Pathfinding:CreatePath({AgentRadius=motor.AgentRadius,AgentHeight=motor.AgentHeight,
  AgentCanJump=motor.AgentCanJump,AgentCanClimb=false,WaypointSpacing=motor.WaypointSpacing})
 local ok,err=pcall(function()path:ComputeAsync(v(cfg.Map.Positions[tostring(station)]),v(cfg.Map.Positions[tostring(target)]))end)
 local reachable=ok and path.Status==Enum.PathStatus.Success;allReachable=allReachable and reachable
 table.insert(rows,{station=station,port=port,fixedTarget=target,reachable=reachable,
  status=ok and tostring(path.Status)or"COMPUTE_ERROR",waypoints=reachable and #path:GetWaypoints()or 0,error=not ok and tostring(err)or nil})
end end
assert(actor:GetPivot()==before,"FOCAL_PREFLIGHT_BODY_CHANGED")
return{schema="DEE.Focal.GeometryPreflight.R03",kind="TECHNICAL_REFERENCE_NOT_POLICY_INPUT",native=false,http=false,
 avatarActuation=false,bodyPoseUnchanged=true,allTwelvePortsReachable=allReachable,ports=rows,
 epoch=0,developmentOpportunities={1,2,3,4},sealedReserveOpportunities={5,6},
 note="No ruta óptima/objetivo calculado; no copiar estas filas aNative. Si falla, preservar y consultarantesde admisión."}
