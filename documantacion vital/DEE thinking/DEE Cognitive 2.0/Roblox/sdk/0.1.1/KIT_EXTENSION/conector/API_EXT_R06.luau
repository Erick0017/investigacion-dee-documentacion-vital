-- Normal serverVM/Bindable API. RO yMATERIAL separados; noCoreMain/actor/motor dependencies.
local H=game:GetService("HttpService");local SS=game:GetService("ServerStorage");local Run=game:GetService("RunService")
local Client=require(script.Parent.CapabilitiesClient_EXT_R06);local View=require(script.Parent.VistaES_EXT_R06)
local M={}
function M.mount(cfg)
 assert(Run:IsServer()and Run:IsStudio(),"EXT_NORMAL_STUDIO_SERVER_REQUIRED")
 assert(cfg.ExtensionVersion=="DEE.Roblox.SDK.assisted_capabilities.R06"and cfg.NoAutomaticMaterial==true,"EXT_CONFIG_VERSION")
 assert(not SS:FindFirstChild(cfg.RuntimeFolder),"EXT_RUNTIME_EXISTS_PRESERVE")
 local node=Instance.new("Folder");node.Name=cfg.RuntimeFolder;node:SetAttribute("ExtensionVersion",cfg.ExtensionVersion);node:SetAttribute("AssistedOnly",true);node.Parent=SS
 local view=View.create(cfg);local client=nil
 local function getClient()
  assert(cfg.Enabled==true,"EXT_DISABLED_NO_NATIVE")
  if not client then client=Client.new(cfg,node,function(row)view:operation(row)end)end;return client
 end
 local function bind(name,material,fn)
  local b=Instance.new("BindableFunction");b.Name=name;b:SetAttribute("MaterialNativeAdmissionPossible",material)
  b.OnInvoke=function(...)
   local ok,result=pcall(fn,...)
   if not ok then view:state("Bloqueado / conservado: "..tostring(result));return{ok=false,error={code="PRESERVED_NO_AUTOMATIC_RETRY",message=tostring(result)},materialNativeAdmissionPossible=material}end
   return{ok=true,result=result,materialNativeAdmissionPossible=material}
  end;b.Parent=node
 end
 bind("GetCapabilitiesRO",false,function()
  if not cfg.Enabled then return{status="DISABLED",extensionVersion=cfg.ExtensionVersion,native=false,help="Configurar endpoint privado y habilitar explícitamente; no hay fallback."}end
  local h=getClient():getCapabilities();view:capabilities(h);return h
 end)
 bind("SubmitCapability",true,function(request)return getClient():submit(request)end)
 bind("GetOperationRO",false,function(id)local value,raw=getClient():reconcileOperation(id);return{operation=value,responseRaw=raw}end)
 bind("ReadResultRO",false,function(id)return assert(getClient():readLocal(id),"EXT_LOCAL_OPERATION_NOT_FOUND")end)
 bind("GetLocalRecordInfoRO",false,function(id)return assert(getClient():localInfo(id),"EXT_LOCAL_OPERATION_NOT_FOUND")end)
 bind("ReadRawChunkRO",false,function(id,index)return getClient():readChunk(id,index)end)
 bind("CloseCapabilities",true,function()return getClient():close()end)
 local status=Instance.new("StringValue");status.Name="ALCANCE";status.Value="ASSISTED developer initiated; no autonomous tool choice; GET is readonly; Submit/Close explicit. Core unchanged.";status.Parent=node
 return node
end
return M
