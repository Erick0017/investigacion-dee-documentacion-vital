-- R02: declared NO_RESULT on incomplete lesson, actual generic failure.
-- Uniform prepared body/environment, not a policy or a Native arithmetic solver.
local RunService=game:GetService("RunService")
local HttpService=game:GetService("HttpService")
local ServerStorage=game:GetService("ServerStorage")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local C=require(script.Parent.Config)
local Body={};Body.__index=Body
local function copy(value)return HttpService:JSONDecode(HttpService:JSONEncode(value))end
local function integer(v)return type(v)=="number" and v%1==0 and v>=0 and v<=32 end
local function formedInteger(v)return type(v)=="number"and v==v and math.abs(v)<=9007199254740991 and v%1==0 end
local function evaluate(left,right,sign)return sign==1 and left+right or left-right end

-- Observer transport R02 only. Internal complete events/poses, physical rules,
-- participant inputs and action laws below are unchanged. StringValue has a
-- platform size cap, so publish immutable bounded generations outside RBX01.
local observerSchema="DEE.C02.JSON_CHUNKS.R02"
local observerChunkBytes=16000
local function utf8Chunks(text)
    local chunks={};local first=1
    while first<=#text do
        local last=math.min(first+observerChunkBytes-1,#text)
        while last<#text do
            local following=string.byte(text,last+1)
            if following and following>=128 and following<=191 then last-=1 else break end
        end
        assert(last>=first,"C02_OBSERVER_UTF8_BOUNDARY")
        table.insert(chunks,string.sub(text,first,last));first=last+1
    end
    return chunks
end
local function observerTail(rows)
    if #rows==0 then return "[]",1,0,false end
    local first=math.max(1,#rows-63);local tail={}
    for index=first,#rows do table.insert(tail,rows[index])end
    local text=HttpService:JSONEncode(tail)
    while #text>observerChunkBytes and #tail>1 do
        table.remove(tail,1);first+=1;text=HttpService:JSONEncode(tail)
    end
    local projected=false
    if #text>observerChunkBytes then
        local last=rows[#rows];projected=true
        tail={{kind=last.kind,seq=last.seq,wallSeconds=last.wallSeconds,worldTime=last.worldTime,
            observerTailProjection=true,fullLogRowIndex=#rows,originalRowBytes=#HttpService:JSONEncode(last),
            data={observerPayloadOmitted=true,reason="FULL_ROW_IN_AUDITOR_CHUNKS"}}}
        first=#rows;text=HttpService:JSONEncode(tail)
    end
    assert(#text<=observerChunkBytes,"C02_OBSERVER_TAIL_BOUND")
    return text,first,#tail,projected
end
local function newObserverLog(name)
    local folder=Instance.new("Folder");folder.Name=name
    folder:SetAttribute("Schema",observerSchema);folder:SetAttribute("LatestSerial",0)
    folder.Parent=ServerStorage;return folder
end
local function publishObserverLog(folder,rows)
    assert(folder:IsA("Folder")and folder:GetAttribute("Schema")==observerSchema,"C02_OBSERVER_LOG_SCHEMA")
    local serial=folder:GetAttribute("LatestSerial")+1
    local encoded=#rows==0 and"[]"or HttpService:JSONEncode(rows);local chunks=utf8Chunks(encoded)
    local generation=Instance.new("Folder");generation.Name=string.format("g%06d",serial)
    generation:SetAttribute("Schema",observerSchema);generation:SetAttribute("serial",serial)
    generation:SetAttribute("totalRows",#rows);generation:SetAttribute("totalBytes",#encoded)
    generation:SetAttribute("chunkCount",#chunks);generation:SetAttribute("complete",false)
    generation.Parent=folder
    for index,part in ipairs(chunks)do
        assert(#part<=observerChunkBytes,"C02_OBSERVER_CHUNK_BOUND")
        local value=Instance.new("StringValue");value.Name=string.format("Chunk%06d",index)
        value.Value=part;value.Parent=generation
    end
    local tailText,tailFirst,tailRows,projected=observerTail(rows)
    local tail=Instance.new("StringValue");tail.Name="Tail";tail.Value=tailText;tail.Parent=generation
    generation:SetAttribute("tailFirst",tailFirst);generation:SetAttribute("tailRows",tailRows)
    generation:SetAttribute("tailProjected",projected)
    generation:SetAttribute("complete",true)
    -- Publish pointer last. A reader pins serial before/after reading its Tail.
    folder:SetAttribute("LatestSerial",serial)
    for _,old in ipairs(folder:GetChildren())do
        if old:IsA("Folder")and type(old:GetAttribute("serial"))=="number"and old:GetAttribute("serial")<serial-1 then old:Destroy()end
    end
end

function Body.new(participant)
    assert(C.OwnerUserId==11981994305 and C.AutoStart=="NONE","C02_PREPARED_ACCOUNT")
    local self=setmetatable({},Body)
    self.world=workspace:WaitForChild("RBX01");self.body=self.world:WaitForChild("DEE_Body")
    self.root=assert(self.body.PrimaryPart,"C02_BODY_PRIMARY_PART")
    self.gates=self.world:WaitForChild("Gates");self.pickups=self.world:WaitForChild("Pickups")
    self.status=ReplicatedStorage:WaitForChild("RBX01Status")
    self.executed={};self.events={};self.poseTrace={};self.paused=false;self.closeRequested=false
    self.participant=participant;self.pendingTool=nil;self.lastActionId=nil
    self.wallStartUnixMs=DateTime.now().UnixTimestampMillis;self.lastPoseWall=-math.huge;self.segmentSerial=1
    self.S={station=0,stage=0,contact=0,inventoryKey=false,inventoryResource=false,
        permissionStock=C.PermissionStock,stationSignal=-1,worldTime=0,phase=0,seq=0,cycle=0,
        nativeTick=0,action="—",consequence="SIN SESIÓN",observation="—",delivered=0,
        resourceUnits=C.ResourceUnits,queries=0,collisions=0,moves=0,tollSpent=0,
        lifeId="PENDIENTE",latency=0,reason="LISTO",publicContactCode=0,reserveActive=false,
        mode="WAIT",completedCycles=0,completedRouteOpportunities=0,sessionId="",
        lastFailure=false,numberAPresent=false,codeBPresent=false,keyCount=0,
        resourceCount=0,codeRejected=0,functionCalls=0,functionNoResult=0,round=0,
        numberAVersion=0,codeBFromAVersion=nil}
    assert(not ServerStorage:FindFirstChild(C.EventLogName),"C02_EXISTING_EVENT_LOG_PRESERVED")
    self.log=newObserverLog(C.EventLogName);self:publishEventLog()
    self.traceLog=newObserverLog(C.PoseTraceName);self:publishPoseLog()
    self.markers=Instance.new("Folder");self.markers.Name="ContactMarkers_C02";self.markers.Parent=self.world
    self.panels=Instance.new("Folder");self.panels.Name="LocalPricePanels_C02";self.panels.Parent=self.world
    self.devices=Instance.new("Folder");self.devices.Name="Devices_C02";self.devices.Parent=self.world
    for station,pos in pairs(C.Positions) do
        local marker=Instance.new("Part");marker.Name="LocalTag_"..station;marker.Anchored=true
        marker.CanCollide=false;marker.CanQuery=true;marker.Size=Vector3.new(3,3,3);marker.Position=pos
        marker.Transparency=.75;marker.Color=Color3.fromRGB(70+station*25,210,180)
        marker:SetAttribute("ContactCode",station);marker.Parent=self.markers
        local panel=Instance.new("Part");panel.Name="Panel_"..station;panel.Anchored=true
        panel.CanCollide=false;panel.Size=Vector3.new(2,3,.5);panel.Position=pos+Vector3.new(5,1,0);panel.Parent=self.panels
        for port=0,1 do
            local gate=assert(self.gates:FindFirstChild("Gate_"..station.."_"..port),"C02_GATE_MISSING")
            local direction=(C.Positions[C.Edges[station][port]]-pos).Unit
            local lateral=Vector3.new(-direction.Z,0,direction.X)*5
            local point=pos+direction*26+lateral+Vector3.new(0,1.1,0)
            gate.CFrame=CFrame.lookAt(point,point+direction);gate.CanQuery=true
        end
        local device=Instance.new("Part");device.Name="Device_"..station;device.Anchored=true
        device.CanCollide=false;device.CanQuery=true;device.Size=Vector3.new(5,5,5);device.Position=pos
        device.Transparency=.8;device.Color=Color3.fromRGB(120,175,230)
        device:SetAttribute("Station",station);device.Parent=self.devices
    end
    for _,part in ipairs(self.pickups:GetChildren()) do
        if part:IsA("BasePart") and part:FindFirstChild("Kind") then
            local station=part.Kind.Value=="KEY" and 1 or part.Kind.Value=="RESOURCE" and 5 or 0
            part.CFrame=CFrame.new(C.Positions[station]);part.CanQuery=true
        end
    end
    self.body:PivotTo(CFrame.new(C.Positions[0]));self:updateGates();self:publish();self:samplePose(true)
    return self
end
function Body:publishEventLog()publishObserverLog(self.log,self.events)end
function Body:publishPoseLog()publishObserverLog(self.traceLog,self.poseTrace)end
function Body:emit(kind,data)
    local wallMs=DateTime.now().UnixTimestampMillis
    local event={kind=kind,worldTimeMs=math.floor(self.S.worldTime*1000),wallUnixMs=wallMs,
        wallSeconds=(wallMs-self.wallStartUnixMs)/1000,segment=self.segmentSerial,seq=self.S.seq,
        sessionId=self.S.sessionId,participant=self.participant,data=copy(data)}
    assert(#self.events<6000,"C02_EVENT_CAP_PRESERVE")
    table.insert(self.events,event);self:publishEventLog()
end
function Body:samplePose(force)
    local wallMs=DateTime.now().UnixTimestampMillis
    local wall=(wallMs-self.wallStartUnixMs)/1000
    if not force and wall-self.lastPoseWall<1/C.PoseSamplesPerWallSecond then return end
    assert(#self.poseTrace<C.MaxPoseSamples,"C02_POSE_CAP_PRESERVE")
    self.lastPoseWall=wall
    table.insert(self.poseTrace,{source="HEARTBEAT_OBSERVED",wallSeconds=wall,wallUnixMs=wallMs,
        segment=self.segmentSerial,worldTime=self.S.worldTime,
        cycle=self.S.cycle,seq=self.S.seq,actionId=self.lastActionId,pose={self.body:GetPivot():GetComponents()}})
end
function Body:publish()
    -- This status is an auditor/HUD view. Only observe/toolRequest are policy inputs.
    local status=copy(self.S);status.level="C02";status.maxCycles=C.MaxCycles
    status.timeScale=C.RenderTimeScale;status.paused=self.paused;status.participant=self.participant
    self.status.Value=HttpService:JSONEncode(status)
end
function Body:updateGates()
    for _,gate in ipairs(self.gates:GetChildren()) do
        if gate:IsA("BasePart") and gate:FindFirstChild("Station") and gate:FindFirstChild("Port") then
            local free=C.FreePorts[self.S.phase][gate.Station.Value]
            local price=(free==-1 or free==gate.Port.Value) and 0 or C.TollCost
            gate:SetAttribute("TollCost_C02",price);gate.CanCollide=price>self.S.permissionStock
            gate.Transparency=price==0 and .8 or .25
            gate.Color=price==0 and Color3.fromRGB(65,230,180) or Color3.fromRGB(245,175,55)
        end
    end
    for station in pairs(C.Positions) do
        local p0=self.gates["Gate_"..station.."_0"]:GetAttribute("TollCost_C02")
        local p1=self.gates["Gate_"..station.."_1"]:GetAttribute("TollCost_C02")
        local signal=p0==0 and(p1==0 and 1 or 0)or 2
        local panel=self.panels["Panel_"..station]
        panel:SetAttribute("Price0_C02",p0);panel:SetAttribute("Price1_C02",p1)
        panel:SetAttribute("EncodedSignal_C02",signal)
        panel.Color=signal==0 and Color3.fromRGB(70,225,170)or signal==2 and Color3.fromRGB(235,175,80)or Color3.fromRGB(170,200,230)
    end
end
function Body:beginCycle(cycle)
    assert(not self.pendingTool,"C02_PREVIOUS_TOOL_NOT_CONSUMED")
    assert(cycle==self.S.completedCycles+1 and cycle<=C.MaxCycles,"C02_EXACT_CURSOR")
    self.S.cycle=cycle;self.S.stationSignal=-1;self.S.contact=0
    local phase=C.PhaseAtCycle(cycle)
    if phase~=self.S.phase then self.S.phase=phase;self:emit("PRICE_CONTINGENCY",{cycle=cycle,phase=phase})end
    if cycle==14 or cycle==27 then self:emit("CUE_CONTINGENCY",{cycle=cycle,observableAt="ARCHIVE_ONLY"})end
    self.S.reserveActive=cycle>=C.ReserveStartsAtCycle;self:updateGates()
end
function Body:advanceTime(seconds,onProgress)
    local elapsed=0
    while elapsed<seconds do
        if self.paused then self:publish();task.wait(.1)
        else
            local dt=math.min(RunService.Heartbeat:Wait()*C.RenderTimeScale,seconds-elapsed)
            elapsed+=dt;self.S.worldTime+=dt
            if onProgress then onProgress(elapsed/seconds,dt)end
            self:samplePose(false);self:publish()
        end
    end
end
function Body:physicalContactCode()
    local params=OverlapParams.new();params.FilterType=Enum.RaycastFilterType.Include;params.FilterDescendantsInstances={self.markers}
    local code=nil
    for _,part in ipairs(workspace:GetPartsInPart(self.root,params))do
        local v=part:GetAttribute("ContactCode")
        if type(v)=="number"then assert(code==nil or code==v,"C02_AMBIGUOUS_TAG");code=v end
    end
    assert(code~=nil,"C02_NO_PHYSICAL_TAG");return code
end
function Body:readLocalPanel()
    local panel=assert(self.panels:FindFirstChild("Panel_"..self.S.station),"C02_PANEL_MISSING")
    assert((panel.Position-self.root.Position).Magnitude<=12,"C02_PANEL_NOT_LOCAL")
    local signal=panel:GetAttribute("EncodedSignal_C02")
    assert(signal==0 or signal==1 or signal==2,"C02_PANEL_INVALID")
    return signal,{part=panel.Name,port0=panel:GetAttribute("Price0_C02"),port1=panel:GetAttribute("Price1_C02")}
end
function Body:observe(phase)
    self.S.seq+=1;self.S.publicContactCode=self:physicalContactCode()
    local obs={observationId="obs_"..HttpService:GenerateGUID(false),seq=self.S.seq,phase=phase,
        worldTimeMs=math.floor(self.S.worldTime*1000),sampleTimeMs=math.floor(self.S.worldTime*1000),
        previousActionId=self.S.previousActionId,sensors={station=self.S.station,stage=self.S.stage,
            contact=self.S.contact,inventoryKey=self.S.inventoryKey,inventoryResource=self.S.inventoryResource,
            queryAvailable=self.S.permissionStock>=C.QueryCost,stationSignal=self.S.stationSignal,
            permissionStock=self.S.permissionStock,publicContactCode=self.S.publicContactCode,lastFailure=self.S.lastFailure}}
    self.S.observation=phase.." / zona "..self.S.publicContactCode.." / panel "..self.S.stationSignal
    self:emit("OBSERVATION",obs);self:publish();return obs
end
function Body:contactAtArrival(result)
    local p=OverlapParams.new();p.FilterType=Enum.RaycastFilterType.Include;p.FilterDescendantsInstances={self.devices}
    local touched=false
    for _,part in ipairs(workspace:GetPartsInPart(self.root,p))do
        if part:GetAttribute("Station")==self.S.station then touched=true end
    end
    assert(touched,"C02_DEVICE_CONTACT_NOT_OBSERVED")
    if self.S.station==1 then
        if not self.S.inventoryKey and not self.S.inventoryResource then
            self.S.inventoryKey=true;self.S.keyCount+=1;self.S.stage=1;self.S.round+=1
            self.S.roundOperands=C.OperandsAtCycle(self.S.cycle)
            self.S.numberA=nil;self.S.finalCode=nil;self.S.numberAPresent=false;self.S.codeBPresent=false
            self.S.numberAVersion=0;self.S.codeBFromAVersion=nil;self.S.codeBInputA=nil
            result.keyCollected=true;self.S.contact=1;result.outcome="KEY_COLLECTED"
            self:emit("PHYSICAL_CONTACT",{kind="KEY",station=1,round=self.S.round})
        end
        local signs=C.SignsAtCycle(self.S.cycle)
        self.pendingTool={kind="LESSON",items={{form="luma",observedSign=signs.luma},{form="nara",observedSign=signs.nara}}}
    elseif self.S.station==2 and self.S.inventoryKey then
        local q=assert(self.S.roundOperands,"C02_KEY_WITHOUT_TUPLE")
        self.pendingTool={kind="CALCULATE",slot="A",form="luma",left=q.aLeft,right=q.aRight}
    elseif self.S.station==4 and self.S.inventoryKey then
        local q=assert(self.S.roundOperands,"C02_KEY_WITHOUT_TUPLE")
        if self.S.numberAPresent and integer(self.S.numberA)then
            self.pendingTool={kind="CALCULATE",slot="B",form="nara",left=self.S.numberA,right=q.bRight}
        elseif self.S.numberAPresent then
            -- The actual out-of-domain A remains visible in S/events. It is
            -- never clamped or replaced with a convenient legal operand.
            self.S.finalCode=nil;self.S.codeBPresent=false;self.S.codeBFromAVersion=nil
            result.invalidAction=true;result.outcome="NUMERIC_OUT_OF_DOMAIN"
            self:emit("TOOL_NOT_INVOKED",{kind="CALCULATE",slot="B",form="nara",leftPresent=true,
                actualLeft=self.S.numberA,reason="NUMERIC_OUT_OF_DOMAIN",Native_function_executed=false})
        else
            self.S.finalCode=nil;self.S.codeBPresent=false;result.invalidAction=true
            result.outcome="NUMERIC_INPUT_MISSING"
            self:emit("TOOL_NOT_INVOKED",{kind="CALCULATE",slot="B",form="nara",leftPresent=false,
                missingLeft=true,reason="NO_ACTUAL_A_OUTPUT",Native_function_executed=false})
        end
    elseif self.S.station==5 and not self.S.inventoryResource then
        local q=self.S.roundOperands;local expected=nil
        if self.S.inventoryKey and q then
            local signs=C.SignsAtCycle(self.S.cycle)
            expected=evaluate(evaluate(q.aLeft,q.aRight,signs.luma),q.bRight,signs.nara)
        end
        local valid=self.S.inventoryKey and self.S.codeBPresent and expected~=nil and self.S.finalCode==expected
        -- This is an environmental lock check, never an observation/Native input.
        self:emit("EVALUATOR_LOCK_CHECK",{actualCode=self.S.finalCode,codePresent=self.S.codeBPresent,
            expectedCode=expected,keyPresent=self.S.inventoryKey,accepted=valid,scope="PRIVATE_EVALUATOR_NOT_POLICY_INPUT"})
        if valid and self.S.resourceUnits>0 then
            local overlap=OverlapParams.new();overlap.FilterType=Enum.RaycastFilterType.Include;overlap.FilterDescendantsInstances={self.pickups}
            local resource=false
            for _,part in ipairs(workspace:GetPartsInPart(self.root,overlap))do if part:FindFirstChild("Kind")and part.Kind.Value=="RESOURCE"then resource=true end end
            assert(resource,"C02_RESOURCE_CONTACT_MISSING")
            self.S.inventoryKey=false;self.S.inventoryResource=true;self.S.resourceUnits-=1;self.S.resourceCount+=1
            self.S.stage=2;self.S.contact=2;result.resourceCollected=true;result.outcome="RESOURCE_COLLECTED"
            self:emit("PHYSICAL_CONTACT",{kind="RESOURCE",unitsRemaining=self.S.resourceUnits})
        else
            self.S.codeRejected+=1;self.S.contact=5;result.codeRejected=true;result.outcome="CODE_REJECTED"
        end
    elseif self.S.station==0 and self.S.inventoryResource then
        local overlap=OverlapParams.new();overlap.FilterType=Enum.RaycastFilterType.Include;overlap.FilterDescendantsInstances={self.pickups}
        local delivery=false
        for _,part in ipairs(workspace:GetPartsInPart(self.root,overlap))do if part:FindFirstChild("Kind")and part.Kind.Value=="DELIVERY"then delivery=true end end
        assert(delivery,"C02_DELIVERY_CONTACT_MISSING")
        self.S.inventoryResource=false;self.S.inventoryKey=false;self.S.delivered+=1;self.S.stage=0;self.S.contact=3
        self.S.numberA=nil;self.S.finalCode=nil;self.S.numberAPresent=false;self.S.codeBPresent=false;self.S.roundOperands=nil
        self.S.numberAVersion=0;self.S.codeBFromAVersion=nil;self.S.codeBInputA=nil
        result.resourceDelivered=true;result.outcome="DELIVERED";self:emit("PHYSICAL_CONTACT",{kind="DELIVERY",delivered=self.S.delivered})
    end
end
function Body:execute(action)
    if self.executed[action.actionId]then return nil,"DUPLICATE_ACTION_NOT_REEXECUTED"end
    self.executed[action.actionId]="EXECUTING";self.lastActionId=action.actionId
    self.S.action=action.name;self.S.nativeTick=action.nativeTick or self.S.nativeTick
    local result={outcome="WAITED",collision=false,resourceCollected=false,resourceDelivered=false,keyCollected=false,
        invalidAction=false,codeRejected=false,permissionSpent=0,materialConsequence=false,durationMs=0,tollSpent=0,querySpent=0,queryDenied=false}
    local before=self.S.worldTime
    if action.name=="ASK_STATION"then
        if self.S.permissionStock>=C.QueryCost then
            self.S.permissionStock-=C.QueryCost;self.S.queries+=1;result.permissionSpent=C.QueryCost;result.querySpent=C.QueryCost
            self:advanceTime(C.QuerySeconds);local signal,audit=self:readLocalPanel();self.S.stationSignal=signal
            self:emit("PAID_LOCAL_PANEL",{actionId=action.actionId,emittedSignal=signal,physicalPanelAudit=audit})
        else self.S.stationSignal=-1;result.queryDenied=true;result.invalidAction=true;self:advanceTime(C.WaitSeconds)end
    elseif action.name=="SKIP_STATION"then self.S.stationSignal=-1;self:advanceTime(C.SkipSeconds)
    elseif action.name=="EXIT_0"or action.name=="EXIT_1"then
        local port=action.name=="EXIT_0"and 0 or 1;local targetStation=C.Edges[self.S.station][port]
        local gate=assert(self.gates:FindFirstChild("Gate_"..self.S.station.."_"..port),"C02_GATE_MISSING")
        local start=self.root.Position;local finish=C.Positions[targetStation];local direction=(finish-start).Unit
        local lateral=Vector3.new(-direction.Z,0,direction.X)*5
        local points={start,start+lateral,finish+lateral,finish};local lengths={5,(finish-start).Magnitude,5}
        local total=lengths[1]+lengths[2]+lengths[3]
        local function pointAt(alpha)
            local remaining=math.clamp(alpha,0,1)*total
            for i,length in ipairs(lengths)do if remaining<=length then return points[i]:Lerp(points[i+1],remaining/length)end;remaining-=length end
            return finish
        end
        local ray=RaycastParams.new();ray.FilterType=Enum.RaycastFilterType.Include;ray.FilterDescendantsInstances={self.gates};ray.RespectCanCollide=true
        local overlap=OverlapParams.new();overlap.FilterType=Enum.RaycastFilterType.Include;overlap.FilterDescendantsInstances={gate}
        local collision=false;local charged=false;local reached=0
        self:advanceTime(C.MoveSeconds,function(alpha)
            if collision then return end
            local target=pointAt(alpha);local from=self.root.Position;local steps=math.max(1,math.ceil((target-from).Magnitude/.5))
            for step=1,steps do
                local point=from:Lerp(target,step/steps);local displacement=point-self.root.Position
                if displacement.Magnitude>.0001 and workspace:Blockcast(self.root.CFrame,self.root.Size*.9,displacement,ray)then collision=true;return end
                self.body:PivotTo(CFrame.lookAt(point,point+direction))
                if not charged and #workspace:GetPartsInPart(self.root,overlap)>0 then
                    local price=gate:GetAttribute("TollCost_C02");assert(price==0 or price==C.TollCost,"C02_TOLL_INVALID")
                    assert(self.S.permissionStock>=price,"C02_TOLL_STOCK_CONFLICT")
                    charged=true;self.S.permissionStock-=price;self.S.tollSpent+=price;result.tollSpent=price;result.permissionSpent+=price
                    self:emit("PHYSICAL_TOLL_CONTACT",{actionId=action.actionId,part=gate.Name,tollSpent=price})
                end
            end
            reached=alpha
        end)
        if collision then
            self.S.collisions+=1;self.S.contact=4;result.collision=true;result.outcome="BLOCKED"
            self:advanceTime(C.BlockSeconds,function(alpha)self.body:PivotTo(CFrame.new(pointAt(reached*(1-alpha))))end)
        else
            assert(charged,"C02_EXIT_WITHOUT_TURNSTILE_CONTACT")
            self.S.station=targetStation;self.S.moves+=1;result.outcome="MOVED";self:contactAtArrival(result)
        end
        self.S.stationSignal=-1;self:updateGates()
    elseif action.name=="SAFE_WAIT"then self.S.reason=action.null and"NULL / PAUSA SEGURA"or"SAFE_WAIT";self:advanceTime(C.WaitSeconds)
    else self.executed[action.actionId]="FAILED";return nil,"ACTION_ENUM_REJECTED"end
    result.materialConsequence=result.collision or result.invalidAction or result.codeRejected
    result.durationMs=math.floor((self.S.worldTime-before)*1000)
    self.executed[action.actionId]="EXECUTED";self:emit("ACTION_EXECUTED",{action=action,result=result})
    self:samplePose(true);self:publishPoseLog();self:publish();return result
end
function Body:toolRequest(action,observation)
    if not self.pendingTool then return nil end
    return {actionId=action.actionId,seq=observation.seq,observationId=observation.observationId,
        worldTimeMs=math.floor(self.S.worldTime*1000),tool=copy(self.pendingTool)}
end
function Body:applyTool(output,result)
    local pending=assert(self.pendingTool,"C02_NO_PENDING_TOOL")
    assert(type(output)=="table"and output.kind==pending.kind,"C02_TOOL_KIND_MISMATCH")
    self.S.functionCalls+=1
    local executionStatus="APPLIED"
    if pending.kind=="CALCULATE"then
        assert(output.slot==pending.slot and output.form==pending.form,"C02_TOOL_IDENTITY_MISMATCH")
        local actual=output.numeric_result;local present=output.formed~=false and formedInteger(actual)
        if pending.slot=="A"then
            local priorCode=self.S.finalCode;local priorVersion=self.S.numberAVersion
            self.S.numberAVersion+=1
            self.S.numberAPresent=present;self.S.numberA=present and actual or nil
            self.S.codeBPresent=false;self.S.finalCode=nil;self.S.codeBFromAVersion=nil;self.S.codeBInputA=nil
            self:emit("NUMERIC_OBJECT_REPLACED",{slot="A",actualValue=actual,present=present,
                oldVersion=priorVersion,newVersion=self.S.numberAVersion,invalidatedCodeB=priorCode,
                reason="NEW_A_REQUIRES_NEW_B_COMPOSITION"})
        else
            self.S.codeBPresent=present;self.S.finalCode=present and actual or nil
            self.S.codeBFromAVersion=present and self.S.numberAVersion or nil
            self.S.codeBInputA=pending.left
        end
        if not present then self.S.functionNoResult+=1;result.invalidAction=true;result.outcome="TOOL_NO_RESULT";executionStatus="NO_RESULT"end
    elseif pending.kind=="LESSON"and(output.reason=="NATIVE_PARTIAL_ADMISSION"or output.capability_execution_admitted==false)then
        -- Partial/rejected admission remains an actual failure; never fill a
        -- word or pretend the whole lesson was acquired. Native partial physics
        -- is preserved by its owner; only transport continues after NO_RESULT.
        self.S.functionNoResult+=1;result.invalidAction=true
        result.outcome="TOOL_NO_RESULT";executionStatus="NO_RESULT"
    end
    self:emit("FUNCTION_APPLIED",{request=copy(pending),output=copy(output),
        numericResultFromParticipantOnly=true,preparedOperationCodec="memory+1=sum;memory-1=difference"})
    self.pendingTool=nil;self:advanceTime(C.ToolSeconds)
    result.materialConsequence=result.collision or result.invalidAction or result.codeRejected
    self:samplePose(true);self:publishPoseLog();self:publish();return executionStatus
end
function Body:feedbackFields(result,action,observation,queryResult)
    local failed=result.collision or result.invalidAction or result.codeRejected or(queryResult and queryResult.invalidAction)or false
    self.S.lastFailure=failed;self.S.consequence=result.outcome.." / consulta -"..result.querySpent.." / peaje -"..result.tollSpent
    return {actionId=action.actionId,seq=observation.seq,observationId=observation.observationId,
        worldTimeMs=math.floor(self.S.worldTime*1000),durationMs=result.durationMs,outcome=result.outcome,
        collision=result.collision,resourceCollected=result.resourceCollected,resourceDelivered=result.resourceDelivered,
        permissionSpent=result.permissionSpent+(queryResult and queryResult.permissionSpent or 0),materialConsequence=failed}
end
return Body
