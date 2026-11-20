-- Pure scene/configuration installation, no Native callback or action.
local package=assert(game:GetService("ServerScriptService"):FindFirstChild("DEEConnector_R06"))
local API=require(package.Main);local adapters=require(package.LiveAdapters_R01)
assert(not workspace:FindFirstChild("DEE_NATIVE_MINIMAL_R01"),"EXISTING_LIVE_SCENE_PRESERVED")
local world=Instance.new("Folder");world.Name="DEE_NATIVE_MINIMAL_R01";world.Parent=workspace
local function part(name,pos,size)
    local p=Instance.new("Part");p.Name=name;p.Anchored=true;p.CanCollide=false;p.CanQuery=true;p.Position=pos;p.Size=size;p.Parent=world;return p
end
local panel=part("LocalPanel",Vector3.new(0,4.5,0),Vector3.new(2,1,1))
panel:SetAttribute("Price0",0);panel:SetAttribute("Price1",0);panel:SetAttribute("Signal",1)
local resource=part("Resource",Vector3.new(6,3,0),Vector3.new(3,3,3));resource:SetAttribute("Available",true)
local base=part("Base",Vector3.new(0,3,0),Vector3.new(3,3,3))
base.Transparency=.8;resource.Color=Color3.fromRGB(70,220,160);panel.Color=Color3.fromRGB(80,160,240)
local obstacles=Instance.new("Folder");obstacles.Name="Obstacles";obstacles.Parent=world
local actor=Instance.new("Model");actor.Name="NativeAgent_CTRL1"
local core=Instance.new("Part");core.Name="Core";core.Anchored=true;core.CanCollide=false;core.CanQuery=true;core.Size=Vector3.new(2,2,2);core.Position=Vector3.new(0,3,0);core.Parent=actor;actor.PrimaryPart=core;actor.Parent=world
actor:SetAttribute("DEE_AgentId","CTRL1");game:GetService("CollectionService"):AddTag(actor,"DEE_Agent")
local runtime=API.mount({ExperienceId="R06_NATIVE_CLEAN",SceneId="scene_01",ScenarioFingerprint="SCENARIO_SHA_PLACEHOLDER",RegistryRoot=world,
    Agents={CTRL1={Participant="DEE",MaxOpportunities=1,MaxActions=2,AllowTechnicalTest=false}},
    MakeAdapters=function(model)return adapters.new(model,{worldRoot=world,panel=panel,resource=resource,base=base,obstacles=obstacles})end})
runtime:scanTagged()
return {installed=true,namespace=runtime:get("CTRL1").namespace,NativeBackendOpened=false,NativeTicks=0,preparedPanel="BOTH_FREE_SIGNAL1",newWorldStock=200}
