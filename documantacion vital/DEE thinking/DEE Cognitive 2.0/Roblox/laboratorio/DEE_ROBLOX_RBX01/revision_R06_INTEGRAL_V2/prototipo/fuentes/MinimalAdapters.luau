-- An explicit small scene adapter. Prepared kinematic offsets are actuators,
-- never choices or learned routes. No private goal or expected answer is read.
local A={}
local function pose(model)return {model:GetPivot():GetComponents()}end
function A.new(actor,options)
    assert(actor:IsA("Model")and actor.PrimaryPart,"DEE_MINIMAL_ACTOR")
    local root=assert(options.worldRoot,"DEE_WORLD_ROOT_REQUIRED")
    assert(actor:IsDescendantOf(root),"DEE_ACTOR_OUTSIDE_DECLARED_WORLD")
    local offsets=options.portOffsets or {[0]=Vector3.new(6,0,0),[1]=Vector3.new(-6,0,0)}
    local world={logicalTimeMs=0,contactCount=0}
    function world:capture()
        return {schema="DEE.MinimalWorld.v1",logicalTimeMs=self.logicalTimeMs,
            contactCount=self.contactCount,rng={algorithm="NONE"}}
    end
    function world:restore(state)
        assert(state.schema=="DEE.MinimalWorld.v1"and state.rng.algorithm=="NONE","DEE_MINIMAL_WORLD_SCHEMA")
        self.logicalTimeMs=state.logicalTimeMs;self.contactCount=state.contactCount
    end
    local body={}
    function body:execute(action)
        local before=pose(actor);local moved=false;local collision=false
        if action.name=="EXIT_0"or action.name=="EXIT_1"then
            local port=action.name=="EXIT_0"and 0 or 1
            local delta=assert(offsets[port],"DEE_UNAVAILABLE_PORT")
            if options.obstacleRoot then
                local ray=RaycastParams.new();ray.FilterType=Enum.RaycastFilterType.Include
                ray.FilterDescendantsInstances={options.obstacleRoot}
                collision=workspace:Blockcast(actor.PrimaryPart.CFrame,actor.PrimaryPart.Size*.9,delta,ray)~=nil
            end
            if not collision then actor:PivotTo(actor:GetPivot()+delta);moved=true end
        else
            assert(action.name=="ASK_STATION"or action.name=="SKIP_STATION"or action.name=="SAFE_WAIT","DEE_ACTION_NOT_SUPPORTED")
        end
        world.logicalTimeMs+=1
        return {outcome=collision and"BLOCKED"or moved and"MOVED"or"WAITED",moved=moved,
            collision=collision,before=before,after=pose(actor),worldTimeMs=world.logicalTimeMs,
            preparedKinematicActuator=true,noNativeExecutedByAdapter=true}
    end
    function body:capture()return {schema="DEE.MinimalBody.v1",pose=pose(actor)}end
    function body:restore(state)
        assert(state.schema=="DEE.MinimalBody.v1"and #state.pose==12,"DEE_BODY_STATE")
        actor:PivotTo(CFrame.new(table.unpack(state.pose)))
    end
    local sensors={}
    function sensors:observe(phase)
        local p=actor.PrimaryPart.Position
        return {phase=phase,sampleTimeMs=world.logicalTimeMs,
            sensors={position={p.X,p.Y,p.Z},contact=world.contactCount,
                availablePorts={0,1},source="LOCAL_MINIMAL_SCENE"}}
    end
    return {body=body,sensors=sensors,world=world}
end
return A
