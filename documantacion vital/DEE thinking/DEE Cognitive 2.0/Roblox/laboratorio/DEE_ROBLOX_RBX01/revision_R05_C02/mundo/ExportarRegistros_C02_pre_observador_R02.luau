-- Auditor-only bounded export. No action, time advance, Native query or policy.
local RunService=game:GetService("RunService")
local HttpService=game:GetService("HttpService")
local ServerStorage=game:GetService("ServerStorage")
local C=require(script.Parent.Config)
local State=require(script.Parent.EstadoPareja_C02)
local E={}
function E.chunk(kind,first,count)
    assert(RunService:IsStudio(),"C02_STUDIO_EXPORT_ONLY")
    assert(kind=="events"or kind=="poses","C02_KNOWN_EXPORT_ONLY")
    assert(type(first)=="number"and first>=1 and first%1==0,"C02_EXACT_EXPORT_CURSOR")
    assert(type(count)=="number"and count>=1 and count<=100 and count%1==0,"C02_EXPORT_MAX100")
    local name=kind=="events"and C.EventLogName or C.PoseTraceName
    local value=assert(ServerStorage:FindFirstChild(name),"C02_EXPORT_SOURCE_MISSING")
    local rows=HttpService:JSONDecode(value.Value)
    local items={};local last=math.min(first+count-1,#rows)
    for index=first,last do table.insert(items,rows[index])end
    return {scope="AUDITOR_ONLY_NOT_PARTICIPANT_INPUT",source=name,kind=kind,
        total=#rows,first=first,last=last,items=items,
        geometryInterpolated=false,newActionExecuted=false,NativeQuerySubmitted=false}
end
function E.geometry()
    assert(RunService:IsStudio(),"C02_STUDIO_EXPORT_ONLY")
    return {scope="AUDITOR_ONLY_NOT_PARTICIPANT_INPUT",worldId=C.WorldId,
        scenarioFingerprint=C.ScenarioFingerprint,physical=State.capturePhysical(workspace:WaitForChild("RBX01")),
        newActionExecuted=false,NativeQuerySubmitted=false}
end
return E
