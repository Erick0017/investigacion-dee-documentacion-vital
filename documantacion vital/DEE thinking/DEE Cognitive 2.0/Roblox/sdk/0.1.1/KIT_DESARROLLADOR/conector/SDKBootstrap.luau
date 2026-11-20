-- Construcción+registro. Este módulo nunca abre un backend ni emite una decisión.
local M={}
local H=game:GetService("HttpService")
local API=require(script.Parent.Main)
local Adapters=require(script.Parent.LiveAdapters_R06)
local DefaultMap=require(script.Parent.MapaEjemplo)
local function clone(v)return H:JSONDecode(H:JSONEncode(v))end
function M.prepare(cfg,contract)
 assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsServer(),"SDK_STUDIO_SERVER_REQUIRED")
 assert(cfg.Version=="0.1.1"and(cfg.Mode=="PREVIEW"or cfg.Mode=="NATIVE"),"SDK_CONFIG_VERSION_MODE")
 local initial,participant,source
 if cfg.Mode=="NATIVE"then
  assert(type(contract)=="table"and type(contract.initialPublicState)=="table","SDK_NATIVE_CONTRACT_REQUIRED")
  initial=clone(contract.initialPublicState);source=assert(contract.sourceWorldSha256,"SDK_SOURCE_WORLD_REQUIRED");participant="DEE"
 else initial=clone(cfg.PreviewPublicState);source="PREVIEW_NOT_NATIVE_STATE";participant="PROGRAMMED"end
 local Map=cfg.MapModule and require(assert(script.Parent:FindFirstChild(cfg.MapModule),"SDK_MAP_MODULE_REQUIRED"))or DefaultMap
 local AdapterFactory=cfg.AdapterModule and require(assert(script.Parent:FindFirstChild(cfg.AdapterModule),"SDK_ADAPTER_MODULE_REQUIRED"))or Adapters
 local scene=Map.build(cfg)
 local runtime=API.mount({ExperienceId=cfg.ExperienceId,SceneId=cfg.SceneId,ScenarioFingerprint=cfg.ScenarioFingerprint,PersistenceBinding=clone(assert(cfg.PersistenceBinding,"R06_BINDING_CONFIG_REQUIRED")),RegistryRoot=scene.world,Agents={[cfg.AgentId]={Participant=participant,MaxOpportunities=cfg.MaxOpportunities,MaxActions=cfg.MaxActions,AllowTechnicalTest=false}},MakeAdapters=function(model)
  return AdapterFactory.new(model,{worldRoot=scene.world,panels=scene.panels,device=scene.device,points=scene.points,inherited=initial,sourceEnvironment=source,motor=clone(cfg.Map.Motor)})
 end})
 runtime:scanTagged();local agent=runtime:get(cfg.AgentId)
 local state=Instance.new("StringValue");state.Name="SDK_STATUS";state.Value=cfg.Mode=="PREVIEW"and"PREVIEW_PREPARED_NO_NATIVE_K2_K3_PENDING"or"NATIVE_CONTRACT_PREPARED_NOT_YET_BOUND";state.Parent=scene.world
 scene.world:SetAttribute("Mode",cfg.Mode);scene.world:SetAttribute("NativeBackendOpenedByBootstrap",false)
 return{runtime=runtime,agent=agent,scene=scene,status=state}
end
return M
