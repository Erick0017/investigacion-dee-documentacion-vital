-- Joint-state codec only. No action policy, Native query, reward or target solver.
-- Root uses capture/apply only at a fully acknowledged opportunity boundary.
-- Private full state returned here is NEVER a participant observation.
local HttpService=game:GetService("HttpService")
local E={}
E.Schema="DEE.RBX01.C02.world_checkpoint.v1"

local function deep(value)
    return HttpService:JSONDecode(HttpService:JSONEncode(value))
end
local function components(frame)
    return {frame:GetComponents()}
end
local function vector(v) return {v.X,v.Y,v.Z} end
local function color(v) return {v.R,v.G,v.B} end
local function pack(v)
    local t=typeof(v)
    if t=="nil" or t=="boolean" or t=="string" then return v end
    if t=="number" then assert(v==v and math.abs(v)<math.huge,"C02_NONFINITE");return v end
    if t=="Vector3" then return {_type="Vector3",v=vector(v)} end
    if t=="Color3" then return {_type="Color3",v=color(v)} end
    if t=="CFrame" then return {_type="CFrame",v=components(v)} end
    if t=="BrickColor" then return {_type="BrickColor",v=v.Number} end
    if t=="UDim" then return {_type="UDim",v={v.Scale,v.Offset}} end
    if t=="UDim2" then return {_type="UDim2",v={v.X.Scale,v.X.Offset,v.Y.Scale,v.Y.Offset}} end
    if t=="NumberRange" then return {_type="NumberRange",v={v.Min,v.Max}} end
    error("C02_UNSUPPORTED_STATE_TYPE:"..t)
end
local function unpackValue(v)
    if type(v)~="table" or not v._type then return v end
    local a=v.v
    if v._type=="Vector3" then return Vector3.new(table.unpack(a)) end
    if v._type=="Color3" then return Color3.new(table.unpack(a)) end
    if v._type=="CFrame" then return CFrame.new(table.unpack(a)) end
    if v._type=="BrickColor" then return BrickColor.new(a) end
    if v._type=="UDim" then return UDim.new(table.unpack(a)) end
    if v._type=="UDim2" then return UDim2.new(table.unpack(a)) end
    if v._type=="NumberRange" then return NumberRange.new(table.unpack(a)) end
    error("C02_UNSUPPORTED_PACKED_TYPE")
end
local function pathOf(root,obj)
    assert(obj==root or obj:IsDescendantOf(root),"C02_OUTSIDE_WORLD")
    local parts={}
    while obj~=root do
        assert(obj.Name~="" and obj.Name~="." and obj.Name~=".." and not string.find(obj.Name,"/",1,true),"C02_UNSAFE_INSTANCE_NAME")
        table.insert(parts,1,obj.Name);obj=obj.Parent
    end
    return table.concat(parts,"/")
end
local function safeSegments(path)
    assert(type(path)=="string" and #path>0 and not string.find(path,"\\",1,true),"C02_UNSAFE_PATH")
    local parts=string.split(path,"/")
    for _,p in ipairs(parts) do assert(p~="" and p~="." and p~="..","C02_UNSAFE_PATH") end
    return parts
end
local function find(root,path)
    local obj=root
    for _,name in ipairs(safeSegments(path)) do
        local matches={}
        for _,child in ipairs(obj:GetChildren()) do if child.Name==name then table.insert(matches,child) end end
        assert(#matches<=1,"C02_AMBIGUOUS_INSTANCE_PATH")
        if #matches==0 then return nil end
        obj=matches[1]
    end
    return obj
end
local function managed(path,roots)
    for _,root in ipairs(roots) do
        if path==root or string.sub(path,1,#root+1)==root.."/" then return true end
    end
    return false
end
local function attrs(obj)
    local result={}
    for key,value in pairs(obj:GetAttributes()) do result[key]=pack(value) end
    return result
end
local function setAttrs(obj,values)
    for key in pairs(obj:GetAttributes()) do if values[key]==nil then obj:SetAttribute(key,nil) end end
    for key,value in pairs(values) do obj:SetAttribute(key,unpackValue(value)) end
end
local valueClasses={BoolValue=true,IntValue=true,NumberValue=true,StringValue=true,
    Vector3Value=true,CFrameValue=true,Color3Value=true,BrickColorValue=true}
local constructibleParts={Part=true,WedgePart=true,CornerWedgePart=true}

function E.capturePhysical(root)
    local parts,values,containers={}, {}, {}
    local seen={}
    local all=root:GetDescendants()
    assert(#all<=16000,"C02_WORLD_OBJECT_BOUND")
    for _,obj in ipairs(all) do
        local path=pathOf(root,obj)
        if obj:IsA("BasePart") or valueClasses[obj.ClassName] or obj:IsA("Folder") or obj:IsA("Model") then
            assert(not seen[path],"C02_AMBIGUOUS_INSTANCE_PATH");seen[path]=true
        end
        if obj:IsA("BasePart") then
            local physical=obj.CustomPhysicalProperties
            local row={path=path,className=obj.ClassName,cframe=components(obj.CFrame),size=vector(obj.Size),
                color=color(obj.Color),transparency=obj.Transparency,anchored=obj.Anchored,
                canCollide=obj.CanCollide,canQuery=obj.CanQuery,canTouch=obj.CanTouch,
                collisionGroup=obj.CollisionGroup,massless=obj.Massless,
                linearVelocity=vector(obj.AssemblyLinearVelocity),angularVelocity=vector(obj.AssemblyAngularVelocity),
                pivotOffset=components(obj.PivotOffset),material=obj.Material.Name,
                attributes=attrs(obj)}
            if obj:IsA("Part") then row.shape=obj.Shape.Name end
            if physical then row.customPhysicalProperties={physical.Density,physical.Friction,physical.Elasticity,
                physical.FrictionWeight,physical.ElasticityWeight} end
            table.insert(parts,row)
        elseif valueClasses[obj.ClassName] then
            table.insert(values,{path=path,className=obj.ClassName,value=pack(obj.Value),attributes=attrs(obj)})
        elseif obj:IsA("Folder") or obj:IsA("Model") then
            local row={path=path,className=obj.ClassName,attributes=attrs(obj)}
            if obj:IsA("Model") and obj.PrimaryPart then row.primaryPart=pathOf(root,obj.PrimaryPart) end
            table.insert(containers,row)
        end
    end
    table.sort(parts,function(a,b)return a.path<b.path end)
    table.sort(values,function(a,b)return a.path<b.path end)
    table.sort(containers,function(a,b)return a.path<b.path end)
    return {parts=parts,values=values,containers=containers}
end

local function requireBoundary(body,c)
    assert(type(c)=="table" and c.phase=="BOUNDARY" and c.native_phase=="IDLE","C02_SETTLED_BOUNDARY_ONLY")
    assert(c.pending_action==nil and c.pending_operation==nil and c.uncertain==false,"C02_PENDING_ACTION_PRESERVED")
    assert(type(c.completed_opportunities)=="number" and c.completed_opportunities%1==0,"C02_CURSOR")
    assert(c.next_opportunity==c.completed_opportunities+1,"C02_CURSOR_RESTART_REFUSED")
    assert(body.S.completedCycles==c.completed_opportunities and body.S.cycle==c.completed_opportunities,"C02_BODY_CURSOR")
    if c.completed_opportunities>0 then
        assert(type(c.last_action_id)=="string" and c.acknowledged_action_id==c.last_action_id,"C02_EXACT_ACK_REQUIRED")
        assert(body.executed[c.last_action_id]=="EXECUTED" or body.executed[c.last_action_id]=="ACKNOWLEDGED","C02_DEDUP_REQUIRED")
        assert(type(c.last_feedback_operation_id)=="string","C02_FEEDBACK_REQUIRED")
    end
    for _,status in pairs(body.executed) do
        assert(status=="EXECUTED" or status=="ACKNOWLEDGED","C02_INFLIGHT_ACTION_REFUSED")
    end
end

function E.capture(body,context)
    requireBoundary(body,context.boundary)
    assert(context.native_tick==body.S.nativeTick,"C02_NATIVE_TICK_MISMATCH")
    assert(context.native_life_id==body.S.lifeId,"C02_NATIVE_IDENTITY_MISMATCH")
    assert(type(context.scenario_sha256)=="string" and #context.scenario_sha256==64,"C02_SCENARIO_PIN")
    assert(context.bridge.pending_count==0 and context.bridge.uncertain_count==0,"C02_BRIDGE_NOT_QUIET")
    assert(context.rng.algorithm=="NONE" or context.rng.algorithm=="C02_LCG32_V1" or
        context.rng.algorithm=="PREDECLARED_EVENT_TABLE_V1","C02_RESTORABLE_RNG_REQUIRED")
    local state={schema=E.Schema,checkpoint_id=context.checkpoint_id,world_id=context.world_id,
        scenario_sha256=context.scenario_sha256,native_life_id=context.native_life_id,native_tick=context.native_tick,
        boundary=deep(context.boundary),S=deep(body.S),body_pose=components(body.body:GetPivot()),
        executed_actions=deep(body.executed),events=deep(body.events),pose_trace=deep(body.poseTrace or {}),physical=E.capturePhysical(body.world),
        controller=deep(context.controller),bridge=deep(context.bridge),rng=deep(context.rng),
        observer={wall_start_unix_ms=body.wallStartUnixMs,segment=body.segmentSerial},
        managed_roots=deep(context.managed_roots or {}),close_requested=body.closeRequested==true,
        observer_scope="FULL_PRIVATE_CHECKPOINT_NOT_PARTICIPANT_PERCEPTION"}
    return deep(state)
end

local function parentFor(root,path,roots)
    local parts=safeSegments(path);local obj=root;local prefix=""
    for i=1,#parts-1 do
        prefix=prefix=="" and parts[i] or prefix.."/"..parts[i]
        local child=obj:FindFirstChild(parts[i])
        if not child then
            assert(managed(prefix,roots),"C02_MISSING_STATIC_PARENT")
            child=Instance.new("Folder");child.Name=parts[i];child.Parent=obj
        end
        obj=child
    end
    return obj,parts[#parts]
end

function E.apply(body,state,expected)
    assert(state.schema==E.Schema,"C02_CHECKPOINT_SCHEMA")
    assert(state.world_id==expected.world_id and state.scenario_sha256==expected.scenario_sha256,"C02_SCENARIO_IDENTITY")
    assert(state.native_life_id==expected.native_life_id and state.native_tick==expected.native_tick,"C02_NATIVE_PAIR_IDENTITY")
    assert(expected.checkpoint_id==state.checkpoint_id and type(expected.checkpoint_sha256)=="string" and
        #expected.checkpoint_sha256==64 and not string.find(expected.checkpoint_sha256,"[^0-9a-f]"),"C02_EXTERNAL_CHECKPOINT_HASH_REQUIRED")
    assert(expected.owner_closed==true and expected.bridge_quiescent==true,"C02_NO_RESTORE_OVER_LIVE_WRITER")
    assert(body.S.completedCycles==0 and #body.events==0 and next(body.executed)==nil,"C02_FRESH_WORLD_RESTORE_ONLY")
    local roots=state.managed_roots or {}
    for _,root in ipairs(roots) do safeSegments(root);assert(find(body.world,root),"C02_MANAGED_ROOT_MISSING") end
    local wanted={}
    for _,group in ipairs({state.physical.parts,state.physical.values,state.physical.containers}) do
        for _,row in ipairs(group or {}) do assert(not wanted[row.path],"C02_DUPLICATE_CHECKPOINT_PATH");wanted[row.path]=row end
    end
    -- Only mutable roots explicitly frozen in the checkpoint can lose objects.
    -- No code, service, player, external tree or Native state is ever destroyed.
    local extras={}
    for _,obj in ipairs(body.world:GetDescendants()) do
        if obj:IsA("BasePart") or valueClasses[obj.ClassName] or obj:IsA("Model") or obj:IsA("Folder") then
            local path=pathOf(body.world,obj)
            if not wanted[path] then assert(managed(path,roots),"C02_STATIC_WORLD_SHAPE_CHANGED");table.insert(extras,obj) end
        end
    end
    table.sort(extras,function(a,b)return #pathOf(body.world,a)>#pathOf(body.world,b) end)
    for _,obj in ipairs(extras) do if obj.Parent then obj:Destroy() end end
    local function getOrCreate(row,allow)
        local obj=find(body.world,row.path)
        if obj then assert(obj.ClassName==row.className,"C02_CLASS_CHANGED");return obj end
        assert(managed(row.path,roots) and allow[row.className],"C02_NONRECREATABLE_PART_OR_STATIC_OBJECT")
        local parent,name=parentFor(body.world,row.path,roots)
        obj=Instance.new(row.className);obj.Name=name;obj.Parent=parent;return obj
    end
    for _,row in ipairs(state.physical.containers or {}) do
        local obj=getOrCreate(row,{Folder=true,Model=true});setAttrs(obj,row.attributes)
    end
    for _,row in ipairs(state.physical.parts) do
        local obj=getOrCreate(row,constructibleParts)
        obj.Anchored=true;obj.CFrame=CFrame.new(table.unpack(row.cframe));obj.Size=Vector3.new(table.unpack(row.size))
        obj.Color=Color3.new(table.unpack(row.color));obj.Transparency=row.transparency
        obj.CanCollide=row.canCollide;obj.CanQuery=row.canQuery;obj.CanTouch=row.canTouch
        obj.CollisionGroup=row.collisionGroup;obj.Massless=row.massless;obj.Material=Enum.Material[row.material]
        obj.PivotOffset=CFrame.new(table.unpack(row.pivotOffset))
        if row.shape then obj.Shape=Enum.PartType[row.shape] end
        obj.CustomPhysicalProperties=row.customPhysicalProperties and PhysicalProperties.new(table.unpack(row.customPhysicalProperties)) or nil
        setAttrs(obj,row.attributes)
        obj.Anchored=row.anchored
        obj.AssemblyLinearVelocity=Vector3.new(table.unpack(row.linearVelocity))
        obj.AssemblyAngularVelocity=Vector3.new(table.unpack(row.angularVelocity))
    end
    for _,row in ipairs(state.physical.values or {}) do
        local obj=getOrCreate(row,valueClasses);obj.Value=unpackValue(row.value);setAttrs(obj,row.attributes)
    end
    for _,row in ipairs(state.physical.containers or {}) do
        if row.className=="Model" and row.primaryPart then find(body.world,row.path).PrimaryPart=assert(find(body.world,row.primaryPart),"C02_PRIMARY_PART_MISSING") end
    end
    body.S=deep(state.S);body.executed=deep(state.executed_actions);body.events=deep(state.events);body.poseTrace=deep(state.pose_trace or {})
    if state.observer then
        body.wallStartUnixMs=state.observer.wall_start_unix_ms
        body.segmentSerial=(state.observer.segment or 1)+1
    end
    body.lastPoseWall=-math.huge
    body.closeRequested=false;body.paused=false -- Operator pause is a host transport condition, not an acquired choice.
    body.body:PivotTo(CFrame.new(table.unpack(state.body_pose)))
    -- Observer transportR02: preserve complete internal arrays; publish bounded
    -- chunks rather than exceed Roblox StringValue200000 during restoration.
    body:publishEventLog()
    body:publishPoseLog()
    requireBoundary(body,state.boundary)
    body:publish()
    -- Root restores these explicit technical cursors; no action is chosen here.
    local resumeBridge=deep(state.bridge)
    assert(type(state.bridge.session_id)=="string" and type(state.bridge.server_id)=="string","C02_SAVED_LOGICAL_TRANSPORT_ID_REQUIRED")
    resumeBridge.resumeTransport={checkpointId=expected.checkpoint_id,checkpointSha256=expected.checkpoint_sha256,
        sessionId=state.bridge.session_id,serverInstanceId=state.bridge.server_id}
    return {restored=true,native_tick=state.native_tick,checkpoint_id=state.checkpoint_id,
        next_opportunity=state.boundary.next_opportunity,controller=deep(state.controller),
        bridge=resumeBridge,rng=deep(state.rng),new_action_executed=false,Native_query_submitted=false}
end

function E.lcg32(seed,counter)
    -- Numerical Recipes32-bit LCG uses exact integer arithmetic in Luau doubles.
    -- The environment's RNG must be separate from every participant policy RNG.
    assert(type(seed)=="number" and seed>=0 and seed<4294967296 and seed%1==0,"C02_RNG_STATE")
    assert(type(counter)=="number" and counter>=0 and counter%1==0,"C02_RNG_COUNTER")
    local state={algorithm="C02_LCG32_V1",state=seed,counter=counter}
    local function nextNumber()
        state.state=(1664525*state.state+1013904223)%4294967296
        state.counter+=1;return state.state/4294967296
    end
    return {nextNumber=nextNumber,export=function()return deep(state)end}
end
return E
