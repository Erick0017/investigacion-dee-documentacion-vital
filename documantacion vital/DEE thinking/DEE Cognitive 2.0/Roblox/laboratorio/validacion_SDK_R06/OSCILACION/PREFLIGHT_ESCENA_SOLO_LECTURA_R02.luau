-- Preflight RO de escena ya preparada en Preview. No decide, no HTTP, no Native, no movimiento.
local H=game:GetService("HttpService")
local Run=game:GetService("RunService")
assert(Run:IsStudio()and Run:IsServer()and Run:IsRunning(),"FOCAL_SERVER_PLAY_REQUIRED")
assert(game:GetService("StudioService"):GetUserId()==11981994305,"FOCAL_OWNER_MISMATCH")
local p=assert(game:GetService("ServerScriptService"):FindFirstChild("DEEConnector_R07"),"FOCAL_PACKAGE")
local cfg=require(p.SDKConfig);assert(cfg.Mode=="PREVIEW"and cfg.MaxOpportunities==6 and cfg.RunCycles==6,"FOCAL_PREFLIGHT_ONLY_PREVIEW")
local w=assert(workspace:FindFirstChild(cfg.Map.RootName),"FOCAL_WORLD")
local actor=assert(w:FindFirstChild("DEE_Focal"));local root=assert(actor.PrimaryPart)
assert(actor:FindFirstChildOfClass("Humanoid"),"FOCAL_RIG_NOT_PREPARED")
local markers=w.Markers:GetChildren();local gates=w.Gates:GetChildren();assert(#markers==6 and #gates==12,"FOCAL_ANATOMY_COUNT")
local panels={};for s=0,5 do
 local q=assert(w:FindFirstChild("Panel_"..s));assert(q:GetAttribute("EncodedSignal_C02")==1 and q:GetAttribute("Price0_C02")==0 and q:GetAttribute("Price1_C02")==0,"FOCAL_INITIAL_PANEL")
 panels[tostring(s)]={signal=q:GetAttribute("EncodedSignal_C02"),price0=q:GetAttribute("Price0_C02"),price1=q:GetAttribute("Price1_C02")}
end
for _,gate in ipairs(gates)do assert(gate:GetAttribute("FocalPassAvailable")==true and gate.CanCollide==false,"FOCAL_INITIAL_GATE")end
return {kind="READ_ONLY_PREVIEW_ANATOMY_NOT_NATIVE_ADMISSION",native=false,http=false,movement=false,arm=cfg.Focal.Arm,
 fingerprint=cfg.ScenarioFingerprint,markers=#markers,gates=#gates,panels=panels,bodyPose={actor:GetPivot():GetComponents()},
 status=w.SDK_STATUS.Value,httpEnabled=H.HttpEnabled,privateConnectionFolderPresent=game:GetService("ServerStorage"):FindFirstChild(cfg.PrivateConnectionFolder)~=nil,
 requiredNext="Root separate focal6 instances/lease/global40000budget; controlled actual Native preflight before6cycles"}
