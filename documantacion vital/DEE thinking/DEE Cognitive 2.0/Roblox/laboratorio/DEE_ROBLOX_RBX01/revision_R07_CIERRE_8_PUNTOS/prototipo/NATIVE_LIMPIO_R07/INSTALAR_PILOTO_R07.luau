-- Apparatus preparation only. No owner, Native call, action or model is opened.
local package=assert(game.ServerScriptService:FindFirstChild("DEEConnector_R07"))
local API=require(package.Main);local adapters=require(package.LiveAdapters_R07)
assert(not workspace:FindFirstChild("DEE_PILOT_MAP_B_R07"),"R07_PILOT_EXISTING_SCENE_PRESERVED")
local world=Instance.new("Folder");world.Name="DEE_PILOT_MAP_B_R07";world.Parent=workspace
local function part(name,pos,size,collide)
 local p=Instance.new("Part");p.Name=name;p.Anchored=true;p.CanCollide=collide;p.CanQuery=true
 p.Position=pos;p.Size=size;p.Parent=world;return p
end
local points={[0]=Vector3.new(20,3,20),[1]=Vector3.new(-12,3,48),[2]=Vector3.new(55,3,-12)}
local floor=part("SueloOtroMapa",Vector3.new(20,-.5,20),Vector3.new(130,1,130),true)
floor.Color=Color3.fromRGB(45,55,70)
local obstacles=Instance.new("Folder");obstacles.Name="ObstaculosFijos";obstacles.Parent=world
for i,row in ipairs({{34,3,4,8,6,12},{0,3,35,6,6,8}})do
 local p=part("Obstacle"..i,Vector3.new(row[1],row[2],row[3]),Vector3.new(row[4],row[5],row[6]),true)
 p.Parent=obstacles;p.Color=Color3.fromRGB(105,115,130)
end
local panels={}
for code,p in pairs(points)do
 local panel=part("PanelLocal"..code,p+Vector3.new(0,2,0),Vector3.new(3,1,1),false)
 panel:SetAttribute("Signal",1);panel:SetAttribute("Price0",0);panel:SetAttribute("Price1",0)
 panel.Color=Color3.fromRGB(80,170,240);panels[code]=panel
 local marker=part("PuertoFijo"..code,p-Vector3.new(0,2.8,0),Vector3.new(7,.2,7),false)
 marker.Color=Color3.fromRGB(80,205,190)
end
local device=part("DispositivoFijo",Vector3.new(20,3,-28),Vector3.new(5,6,1),false)
device:SetAttribute("ActuatorValue",-1);device.Color=Color3.fromRGB(150,160,175)
local actor=Instance.new("Model");actor.Name="NativeAgent_PILOT";actor.Parent=world
local root=part("CoreInicial",points[0],Vector3.new(2,2,1),false);root.Parent=actor;actor.PrimaryPart=root
actor:SetAttribute("DEE_AgentId","PILOT");game:GetService("CollectionService"):AddTag(actor,"DEE_Agent")
local H=game:GetService("HttpService")
local inherited=H:JSONDecode("{\"permissionStock\":164,\"inventoryKey\":true,\"inventoryResource\":false,\"numberAPresent\":true,\"codeBPresent\":false,\"numberAVersion\":5,\"codeBCurrent\":false}")
local runtime=API.mount({ExperienceId="R07_NATIVE_PILOT",SceneId="map_b",ScenarioFingerprint="4af62518f7288b1b7bc97a575b690b53d502d518ed1c29a3424812856d0dcee4",
 RegistryRoot=world,Agents={PILOT={Participant="DEE",MaxOpportunities=3,MaxActions=6,AllowTechnicalTest=false}},
 MakeAdapters=function(model)return adapters.new(model,{worldRoot=world,panels=panels,device=device,
  points=points,inherited=inherited,sourceEnvironment="48544f655382bdf97b4930200158e35371d878c29d17c1ce918077aa27cf6930",
  motor={WalkSpeed=16,AgentRadius=2,AgentHeight=5,AgentCanJump=false,WaypointSpacing=4,
   ArrivalRadius=2,WaypointTimeout=8,MaxRecomputes=2,MaxWallSeconds=45}})end})
runtime:scanTagged()
return{installed=true,namespace=runtime:get("PILOT").namespace,NativeBackendOpened=false,
 NativeTicks=0,newMap=true,initialPublicState=inherited,independentExternalValidation=false}
