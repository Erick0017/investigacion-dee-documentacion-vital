-- Motor geometry only. The caller supplies ONE already selected destination.
-- No graph search for goals, inventory policy, novelty, anti-loop or target swap.
local PathfindingService=game:GetService("PathfindingService")
local RunService=game:GetService("RunService")
local Motor={};Motor.__index=Motor

local function part(parent,name,size,frame,color,collide)
    local p=parent:FindFirstChild(name)
    if p then assert(p:IsA("Part"),"R07_RIG_PART_CLASS");return p end
    p=Instance.new("Part");p.Name=name;p.Size=size;p.CFrame=frame;p.Color=color
    p.Anchored=false;p.CanCollide=collide;p.CanTouch=true;p.CanQuery=true
    p:SetAttribute("R07PreparedBody",true);p.Parent=parent;return p
end
local function joint(parent,name,a,b,c0,c1)
    local old=parent:FindFirstChild(name)
    if old then assert(old:IsA("Motor6D"),"R07_JOINT_CLASS");return old end
    local m=Instance.new("Motor6D");m.Name=name;m.Part0=a;m.Part1=b
    m.C0=c0;m.C1=c1;m.Parent=parent;return m
end
function Motor.new(body,config,emit,onFrame)
    local self=setmetatable({},Motor)
    self.body=body;self.C=config;self.emit=emit;self.onFrame=onFrame;self.active=false
    local before=body:GetPivot();local existing={}
    for _,p in ipairs(body:GetDescendants())do if p:IsA("BasePart")then table.insert(existing,p)end end
    local root=part(body,"HumanoidRootPart",Vector3.new(2,2,1),before,Color3.fromRGB(70,205,230),false)
    root.Transparency=1;root.Anchored=true
    local torso=part(body,"Torso",Vector3.new(2,2,1),before,Color3.fromRGB(55,150,190),true)
    local head=part(body,"Head",Vector3.new(2,1,1),before*CFrame.new(0,1.5,0),Color3.fromRGB(130,225,225),false)
    local ll=part(body,"Left Leg",Vector3.new(1,2,1),before*CFrame.new(-.5,-2,0),Color3.fromRGB(55,90,130),true)
    local rl=part(body,"Right Leg",Vector3.new(1,2,1),before*CFrame.new(.5,-2,0),Color3.fromRGB(55,90,130),true)
    local la=part(body,"Left Arm",Vector3.new(1,2,1),before*CFrame.new(-1.5,0,0),Color3.fromRGB(75,175,200),false)
    local ra=part(body,"Right Arm",Vector3.new(1,2,1),before*CFrame.new(1.5,0,0),Color3.fromRGB(75,175,200),false)
    joint(root,"RootJoint",root,torso,CFrame.identity,CFrame.identity)
    joint(torso,"Neck",torso,head,CFrame.new(0,1,0),CFrame.new(0,-.5,0))
    joint(torso,"Left Hip",torso,ll,CFrame.new(-.5,-1,0),CFrame.new(0,1,0))
    joint(torso,"Right Hip",torso,rl,CFrame.new(.5,-1,0),CFrame.new(0,1,0))
    joint(torso,"Left Shoulder",torso,la,CFrame.new(-1.5,0,0),CFrame.identity)
    joint(torso,"Right Shoulder",torso,ra,CFrame.new(1.5,0,0),CFrame.identity)
    for _,p in ipairs(existing)do
        if p~=root and not p:GetAttribute("R07PreparedBody")then
            p.CanCollide=false;p.Massless=true
            if not p:FindFirstChild("R07OldVisualWeld")then
                local w=Instance.new("Weld");w.Name="R07OldVisualWeld";w.Part0=root;w.Part1=p
                w.C0=root.CFrame:ToObjectSpace(p.CFrame);w.C1=CFrame.identity;w.Parent=p
            end
        end
    end
    for _,p in ipairs(body:GetDescendants())do if p:IsA("BasePart")and p~=root then p.Anchored=false end end
    local h=body:FindFirstChildOfClass("Humanoid")or Instance.new("Humanoid")
    h.Name="Humanoid";h.RequiresNeck=false;h.BreakJointsOnDeath=false
    h.WalkSpeed=config.WalkSpeed;h.HipHeight=0;h.AutoRotate=true
    h.DisplayDistanceType=Enum.HumanoidDisplayDistanceType.None;h.Parent=body
    body.PrimaryPart=root;self.root=root;self.humanoid=h
    root.AssemblyLinearVelocity=Vector3.zero;root.AssemblyAngularVelocity=Vector3.zero
    self.emit("MOTOR_PREPARED",{kind="HUMANOID_PATHFINDING",preservedPivot={before:GetComponents()},
        semantic_destination_selected_by_motor=false})
    return self
end

function Motor:moveTo(destination,actionId)
    assert(not self.active and typeof(destination)=="Vector3","R07_SINGLE_FIXED_MOTOR_TARGET")
    self.active=true
    local selected=destination;local started=os.clock();local totalDistance=0;local old=self.root.Position
    local recomputes=0;local status="NO_PATH";local reason="NOT_COMPUTED";local pathRows={}
    self.emit("MOTOR_TARGET_ADMITTED",{actionId=actionId,selectedDestination={selected.X,selected.Y,selected.Z},
        walkSpeed=self.C.WalkSpeed,no_goal_substitution=true})
    while recomputes<=self.C.MaxRecomputes and os.clock()-started<self.C.MaxWallSeconds do
        local path=PathfindingService:CreatePath({AgentRadius=self.C.AgentRadius,AgentHeight=self.C.AgentHeight,
            AgentCanJump=self.C.AgentCanJump,AgentCanClimb=false,WaypointSpacing=self.C.WaypointSpacing})
        -- No semantic Costs/modifiers or desired goal can enter this service.
        local ok,err=pcall(function()path:ComputeAsync(self.root.Position,selected)end)
        if not ok or path.Status~=Enum.PathStatus.Success then reason=ok and"PATH_STATUS_NO_PATH"or tostring(err);break end
        local waypoints=path:GetWaypoints();local blocked=nil;local waypointIndex=1
        local connection=path.Blocked:Connect(function(index)if index>=waypointIndex then blocked=index end end)
        self.root.Anchored=false;pcall(function()self.root:SetNetworkOwner(nil)end)
        local completed=true
        for index,waypoint in ipairs(waypoints)do
            waypointIndex=index
            if blocked or os.clock()-started>=self.C.MaxWallSeconds then completed=false;reason="BLOCKED_OR_MOTOR_TIMEOUT";break end
            if waypoint.Action==Enum.PathWaypointAction.Jump then self.humanoid:ChangeState(Enum.HumanoidStateType.Jumping)end
            self.humanoid:MoveTo(waypoint.Position)
            local stepStart=os.clock();local reached=false
            while os.clock()-stepStart<self.C.WaypointTimeout and os.clock()-started<self.C.MaxWallSeconds do
                local dt=RunService.Heartbeat:Wait()
                totalDistance+=(self.root.Position-old).Magnitude;old=self.root.Position
                self.onFrame(dt)
                local delta=self.root.Position-waypoint.Position
                if Vector3.new(delta.X,0,delta.Z).Magnitude<=self.C.ArrivalRadius then reached=true;break end
                if blocked then break end
            end
            table.insert(pathRows,{attempt=recomputes,waypoint=index,reached=reached,
                position={waypoint.Position.X,waypoint.Position.Y,waypoint.Position.Z}})
            if not reached then completed=false;reason=blocked and"PATH_BLOCKED"or"WAYPOINT_TIMEOUT";break end
        end
        connection:Disconnect()
        local delta=self.root.Position-selected
        if completed and Vector3.new(delta.X,0,delta.Z).Magnitude<=self.C.ArrivalRadius then status="ARRIVED";reason="SELECTED_TARGET_REACHED";break end
        recomputes+=1
        -- Recompute only to selected, never a different station or useful tool.
    end
    self.humanoid:Move(Vector3.zero);self.root.Anchored=true
    self.root.AssemblyLinearVelocity=Vector3.zero;self.root.AssemblyAngularVelocity=Vector3.zero
    self.active=false
    local result={status=status,reason=reason,actionId=actionId,selectedDestination={selected.X,selected.Y,selected.Z},
        finalPosition={self.root.Position.X,self.root.Position.Y,self.root.Position.Z},recomputes=recomputes,
        wallSeconds=os.clock()-started,distance=totalDistance,waypoints=pathRows,no_alternate_goal=true}
    self.emit("MOTOR_RESULT",result);return result
end

function Motor:export()
    assert(not self.active and self.root.Anchored,"R07_NO_CAPTURE_DURING_MOTOR")
    return {schema="DEE.R07.prepared_motor.R01",active=false,rootAnchored=true,
        walkSpeed=self.humanoid.WalkSpeed,hipHeight=self.humanoid.HipHeight,
        autoRotate=self.humanoid.AutoRotate,parameters=self.C}
end
return Motor
