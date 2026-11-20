-- Auditor-only bounded export. No action, time advance, Native query or policy.
local RunService=game:GetService("RunService")
local HttpService=game:GetService("HttpService")
local ServerStorage=game:GetService("ServerStorage")
local C=require(script.Parent.Config)
local State=require(script.Parent.EstadoPareja_C02)
local E={}
local schema="DEE.C02.JSON_CHUNKS.R02"
local function selected(kind,serial)
    assert(RunService:IsStudio(),"C02_STUDIO_EXPORT_ONLY")
    assert(kind=="events"or kind=="poses","C02_KNOWN_EXPORT_ONLY")
    local name=kind=="events"and C.EventLogName or C.PoseTraceName
    local source=assert(ServerStorage:FindFirstChild(name),"C02_EXPORT_SOURCE_MISSING")
    if source:IsA("StringValue")then
        assert(#source.Value<=200000,"C02_LEGACY_STRING_LOG_TOO_LARGE")
        return source,nil,{scope="AUDITOR_ONLY_NOT_PARTICIPANT_INPUT",source=name,kind=kind,legacy=true,
            totalBytes=#source.Value,serial=0,newActionExecuted=false,NativeQuerySubmitted=false}
    end
    assert(source:IsA("Folder")and source:GetAttribute("Schema")==schema,"C02_EXPORT_FOLDER_SCHEMA")
    serial=serial or source:GetAttribute("LatestSerial")
    assert(type(serial)=="number"and serial>=1 and serial%1==0,"C02_EXACT_LOG_SERIAL")
    local generation=assert(source:FindFirstChild(string.format("g%06d",serial)),"C02_LOG_GENERATION_EXPIRED")
    assert(generation:IsA("Folder")and generation:GetAttribute("complete")==true and generation:GetAttribute("serial")==serial,"C02_LOG_GENERATION_INCOMPLETE")
    return source,generation,{scope="AUDITOR_ONLY_NOT_PARTICIPANT_INPUT",source=name,kind=kind,schema=schema,
        serial=serial,total=generation:GetAttribute("totalRows"),totalBytes=generation:GetAttribute("totalBytes"),
        chunkCount=generation:GetAttribute("chunkCount"),tailFirst=generation:GetAttribute("tailFirst"),tailRows=generation:GetAttribute("tailRows"),
        tailProjected=generation:GetAttribute("tailProjected"),newActionExecuted=false,NativeQuerySubmitted=false}
end
local function rowsOf(source,generation,metadata)
    local text=nil
    if generation then
        local chunks={}
        for index=1,metadata.chunkCount do
            local chunk=assert(generation:FindFirstChild(string.format("Chunk%06d",index)),"C02_LOG_CHUNK_MISSING")
            assert(chunk:IsA("StringValue")and #chunk.Value<=16000,"C02_LOG_CHUNK_BOUND")
            table.insert(chunks,chunk.Value)
        end
        text=table.concat(chunks);assert(#text==metadata.totalBytes,"C02_LOG_TOTAL_BYTES_MISMATCH")
    else text=source.Value end
    local rows=HttpService:JSONDecode(text)
    if generation then assert(#rows==metadata.total,"C02_LOG_TOTAL_ROWS_MISMATCH")else metadata.total=#rows end
    return rows
end
function E.metadata(kind,serial)
    local _,_,metadata=selected(kind,serial);return metadata
end
function E.textChunk(kind,serial,index)
    local source,generation,metadata=selected(kind,serial)
    assert(type(index)=="number"and index>=1 and index%1==0,"C02_EXACT_TEXT_CHUNK")
    assert(generation,"C02_TEXT_CHUNK_REQUIRES_R02_FOLDER")
    assert(index<=metadata.chunkCount,"C02_TEXT_CHUNK_OUT_OF_RANGE")
    local value=assert(generation:FindFirstChild(string.format("Chunk%06d",index)),"C02_LOG_CHUNK_MISSING")
    assert(value:IsA("StringValue")and #value.Value<=16000,"C02_LOG_CHUNK_BOUND")
    metadata.index=index;metadata.text=value.Value;metadata.chunkBytes=#value.Value
    return metadata
end
function E.chunk(kind,first,count,serial)
    assert(type(first)=="number"and first>=1 and first%1==0,"C02_EXACT_EXPORT_CURSOR")
    assert(type(count)=="number"and count>=1 and count<=100 and count%1==0,"C02_EXPORT_MAX100")
    local source,generation,metadata=selected(kind,serial);local rows=rowsOf(source,generation,metadata)
    metadata.first=first;metadata.last=first-1;metadata.items={};metadata.geometryInterpolated=false
    for index=first,math.min(first+count-1,#rows)do
        table.insert(metadata.items,rows[index]);metadata.last=index
        if #HttpService:JSONEncode(metadata)>15000 then
            table.remove(metadata.items);metadata.last=index-1
            metadata.byteLimitReached=true
            if metadata.last<first then metadata.status="ROW_TOO_LARGE_USE_TEXT_CHUNK"end
            break
        end
    end
    metadata.complete=metadata.last>=#rows
    assert(#HttpService:JSONEncode(metadata)<=16000,"C02_AUDITOR_RESPONSE_BOUND")
    return metadata
end
function E.geometry()
    assert(RunService:IsStudio(),"C02_STUDIO_EXPORT_ONLY")
    return {scope="AUDITOR_ONLY_NOT_PARTICIPANT_INPUT",worldId=C.WorldId,
        scenarioFingerprint=C.ScenarioFingerprint,physical=State.capturePhysical(workspace:WaitForChild("RBX01")),
        newActionExecuted=false,NativeQuerySubmitted=false}
end
return E
