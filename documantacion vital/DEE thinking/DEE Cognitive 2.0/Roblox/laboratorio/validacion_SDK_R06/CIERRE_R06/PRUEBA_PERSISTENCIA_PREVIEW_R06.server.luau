-- Root sólo: prueba técnica enScriptNORMAL/Preview. No observa ni llamaNative.
local H=game:GetService("HttpService");local Run=game:GetService("RunService")
assert(Run:IsStudio()and Run:IsServer(),"R06_PREVIEW_SERVER")
local pkg=assert(game:GetService("ServerScriptService"):FindFirstChild("DEEConnector_R06"))
local cfg=require(pkg.SDKConfig);assert(cfg.Mode=="PREVIEW","R06_PREVIEW_ONLY")
local a=require(pkg.Main).lookupRuntime(cfg.ExperienceId,cfg.SceneId):get(cfg.AgentId)
local stateBefore=a:status();local body=a.adapters.body:capture();local world=a.adapters.world:capture()
a.adapters.world:restore(world);a.adapters.body:restore(body)
local actual={state=a:status(),body=a.adapters.body:capture(),world=a.adapters.world:capture()}
local comparison=require(pkg.PersistenceChecks_R06).compare({state=stateBefore,body=body,world=world},actual)
local report={schema="DEE.SDK.PreviewRoundTrip.R06",kind="TECHNICAL_NON_NATIVE_NOT_K4",passed=comparison.passed,
 differenceCount=comparison.differenceCount,differences=comparison.differences,poseTolerance=1e-5,
 stateBefore=stateBefore,stateAfter=actual.state,bodyExpected=body,bodyActual=actual.body,worldExpected=world,worldActual=actual.world,
 nativeExecuted=false,observationsCreated=0,agentPhase=actual.state.phase}
local folder=Instance.new("Folder");folder.Name="DEE_SDK_PREVIEW_R06";folder.Parent=game:GetService("ServerStorage")
local value=Instance.new("StringValue");value.Name="ROUNDTRIP_JSON";value.Value=H:JSONEncode(report);value.Parent=folder
local args=game:GetService("StudioTestService"):GetTestArgs()
if type(args)=="table"and args.EndPreviewAfterCheck==true then game:GetService("StudioTestService"):EndTest(report)end
