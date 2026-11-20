-- Fixed minimal sensor/body anatomy. NO decision policy, arithmetic or teacher.
local A={}
local function pose(model)return {model:GetPivot():GetComponents()}end
function A.new(actor,options)
    local root=assert(options.worldRoot);local panel=assert(options.panel)
    local resource=assert(options.resource);local base=assert(options.base)
    assert(actor:IsA("Model")and actor.PrimaryPart and actor:IsDescendantOf(root),"LIVE_ACTOR_SCOPE")
    local state={stock=200,worldTimeMs=0,signal=-1,inventoryResource=false,resourceCount=0,delivered=0,lastFailure=false,
        queries=0,skips=0,moves=0,waits=0,resourceAvailable=true,rng={algorithm="NONE"}}
    local function code()
        local x=actor.PrimaryPart.Position.X
        if math.abs(x)<.05 then return 0 elseif math.abs(x-6)<.05 then return 1 elseif math.abs(x+6)<.05 then return 2 else return 3 end
    end
    local function contact(part)
        local p=OverlapParams.new();p.FilterType=Enum.RaycastFilterType.Include;p.FilterDescendantsInstances={part}
        return #workspace:GetPartsInPart(actor.PrimaryPart,p)>0
    end
    local world={}
    function world:capture()
        return {schema="DEE.NativeCleanWorld.R01",state=table.clone(state),panel={price0=panel:GetAttribute("Price0"),price1=panel:GetAttribute("Price1"),signal=panel:GetAttribute("Signal")},
            resource={available=resource:GetAttribute("Available"),pose={resource.CFrame:GetComponents()}},base={pose={base.CFrame:GetComponents()}},
            task="PREPARED_DELIVERY_GOAL",preparedPorts={0,1},noTargetCodeOrFutureInSensor=true}
    end
    function world:restore(saved)
        assert(saved.schema=="DEE.NativeCleanWorld.R01"and saved.state.rng.algorithm=="NONE","LIVE_WORLD_SCHEMA")
        state=table.clone(saved.state);panel:SetAttribute("Price0",saved.panel.price0);panel:SetAttribute("Price1",saved.panel.price1);panel:SetAttribute("Signal",saved.panel.signal)
        resource:SetAttribute("Available",saved.resource.available);resource.CFrame=CFrame.new(table.unpack(saved.resource.pose));resource.CanQuery=saved.resource.available
        resource.Transparency=saved.resource.available and 0 or 1;base.CFrame=CFrame.new(table.unpack(saved.base.pose))
    end
    local body={}
    function body:execute(action)
        local r={before=pose(actor),collision=false,invalidAction=false,resourceCollected=false,resourceDelivered=false,permissionSpent=0,querySpent=0,tollSpent=0,durationMs=1000,outcome="WAITED"}
        if action.name=="ASK_STATION"then
            if state.stock<1 or(panel.Position-actor.PrimaryPart.Position).Magnitude>8 then r.invalidAction=true;r.queryDenied=true;r.outcome="QUERY_UNAVAILABLE"
            else
                assert(panel:GetAttribute("Price0")==0 and panel:GetAttribute("Price1")==0 and panel:GetAttribute("Signal")==1,"PREDECLARED_REAL_FREE_PANEL")
                state.stock-=1;state.signal=panel:GetAttribute("Signal");state.queries+=1;r.permissionSpent=1;r.querySpent=1;r.durationMs=2000;r.outcome="PANEL_OBSERVED"
            end
        elseif action.name=="SKIP_STATION"then state.skips+=1;state.signal=-1;r.outcome="QUERY_OMITTED"
        elseif action.name=="SAFE_WAIT"then state.waits+=1
        elseif action.name=="EXIT_0"or action.name=="EXIT_1"then
            local delta=Vector3.new(action.name=="EXIT_0"and 6 or -6,0,0)
            local ray=RaycastParams.new();ray.FilterType=Enum.RaycastFilterType.Include;ray.FilterDescendantsInstances={options.obstacles}
            r.collision=workspace:Blockcast(actor.PrimaryPart.CFrame,actor.PrimaryPart.Size*.9,delta,ray)~=nil
            if not r.collision then actor:PivotTo(actor:GetPivot()+delta);state.moves+=1;r.outcome="MOVED"end
            r.durationMs=1000
            if not r.collision and state.resourceAvailable and contact(resource)then
                state.inventoryResource=true;state.resourceAvailable=false;state.resourceCount+=1
                resource:SetAttribute("Available",false);resource.CanQuery=false;resource.Transparency=1
                r.resourceCollected=true;r.outcome="RESOURCE_COLLECTED"
            end
            if state.inventoryResource and contact(base)then
                state.inventoryResource=false;state.delivered+=1;r.resourceDelivered=true;r.outcome="DELIVERED"
            end
        else r.invalidAction=true;r.outcome="UNSUPPORTED_ACTION"end
        state.worldTimeMs+=r.durationMs;state.lastFailure=r.collision or r.invalidAction
        r.after=pose(actor);r.worldTimeMs=state.worldTimeMs;r.materialConsequence=state.lastFailure
        r.preparedKinematicActuator=true;return r
    end
    function body:capture()return {schema="DEE.NativeCleanBody.R01",pose=pose(actor)}end
    function body:restore(saved)assert(saved.schema=="DEE.NativeCleanBody.R01");actor:PivotTo(CFrame.new(table.unpack(saved.pose)))end
    local sensors={}
    function sensors:observe(phase)
        if phase=="QUERY_CHOICE"then state.signal=-1 end
        local localCode=code()
        return {phase=phase,worldTimeMs=state.worldTimeMs,sampleTimeMs=state.worldTimeMs,
            sensors={station=localCode,stage=state.inventoryResource and 2 or 0,contact=contact(base)and 0 or contact(resource)and 2 or 0,
                inventoryKey=false,inventoryResource=state.inventoryResource,queryAvailable=state.stock>=1,
                stationSignal=state.signal,permissionStock=state.stock,publicContactCode=localCode,lastFailure=state.lastFailure,
                numberAPresent=false,codeBPresent=false,numberAVersion=0,codeBCurrent=false,goalDelivery=true}}
    end
    return {body=body,sensors=sensors,world=world}
end
return A
