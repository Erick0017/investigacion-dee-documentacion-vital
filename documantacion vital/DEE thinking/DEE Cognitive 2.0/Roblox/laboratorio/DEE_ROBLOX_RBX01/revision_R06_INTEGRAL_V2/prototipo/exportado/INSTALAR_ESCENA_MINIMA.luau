assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"STUDIO_PLAY_ONLY")
local package=assert(game:GetService("ServerScriptService"):FindFirstChild("DEEConnector_R06"));local API=require(package.Main);local adapters=require(package.MinimalAdapters)
assert(not workspace:FindFirstChild("DEE_Minimal_R06"),"EXISTING_TEST_SCENE_PRESERVED")
local world=Instance.new("Folder");world.Name="DEE_Minimal_R06";world.Parent=workspace
local actor=Instance.new("Model");actor.Name="Agent_01";local part=Instance.new("Part");part.Name="Core";part.Size=Vector3.new(2,2,2);part.Anchored=true;part.CanCollide=false;part.Position=Vector3.new(0,3,0);part.Parent=actor;actor.PrimaryPart=part;actor.Parent=world
actor:SetAttribute("DEE_AgentId","agent_01");game:GetService("CollectionService"):AddTag(actor,"DEE_Agent")
local runtime=API.mount({ExperienceId="R06_CLEAN",SceneId="scene_01",ScenarioFingerprint="79173686537dbad241d37283d9fe0c68f0eb9170a5c3660424328af40fea2335",RegistryRoot=world,
Agents={agent_01={Participant="DEE",MaxOpportunities=2,MaxActions=4,AllowTechnicalTest=true}},
MakeAdapters=function(model)return adapters.new(model,{worldRoot=world})end})
runtime:scanTagged();local a=runtime:get("agent_01")
a:bindSession({sessionId="MCP_TECH_SESSION",lifeId="MCP_TECHNICAL_CONTROL",nativeTick=0})
return{observation=a:observe("ROUTE_CHOICE"),scope="TECHNICAL_CONNECTOR_INSTALL_NOT_NATIVE",NativeTicks=0}
