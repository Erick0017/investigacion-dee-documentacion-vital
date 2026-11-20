-- Same finite opportunity controller for all declared participants. This
-- sequences prepared interfaces; it never selects a route, operation or value.
local Players=game:GetService("Players")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local ServerStorage=game:GetService("ServerStorage")
local RunService=game:GetService("RunService")
local C=require(script.Parent.Config)
local Body=require(script.Parent.Body_C02)
local State=require(script.Parent.EstadoPareja_C02)
local Bridge=require(script.Parent.Bridge)
Players.CharacterAutoLoads=false
local B=Body.new(C.Participant)
local bridge=nil;local running=false;local activeOwner=nil
local cursor=1;local checkpointSerial=0;local restoredBridge=nil
local lastActionId=nil;local lastFeedbackOperationId=nil;local acknowledgedActionId=nil
local phase="PREPARED"
local function fail(reason)
    B.S.mode="WAIT";B.S.reason=reason;running=false;phase="FAILED_PRESERVED"
    B:emit("STOP",{reason=reason,noMaterialRetry=true});B:publish()
end
local function decide(observation)
    B.S.mode="WAIT";B.S.reason="PROCESAMIENTO / RELOJ AMBIENTAL PAUSADO";B:publish()
    local started=os.clock()
    local action,err=bridge:decide(observation,function()B:publish()end)
    B.S.latency=os.clock()-started
    if action then B.S.mode=C.Participant;B.S.reason="ACTUACIÓN FORMADA"end
    return action,err
end
local function ack(action)
    local value,err=bridge:post("/v1/ack",{actionId=action.actionId,
        worldTimeMs=math.floor(B.S.worldTime*1000),executionStatus="EXECUTED"})
    if value then B.S.previousActionId=action.actionId;acknowledgedActionId=action.actionId end
    return value,err
end
local function useTool(result,action,observation)
    local fields=B:toolRequest(action,observation)
    if not fields then return true end
    phase="FUNCTION";B.S.mode="WAIT";B.S.reason="FUNCIÓN / RELOJ AMBIENTAL PAUSADO";B:publish()
    B:emit("FUNCTION_SUBMITTED",fields)
    local returned,err=bridge:tool(fields,function()B:publish()end)
    if not returned then return nil,err end
    if returned.accepted~=true or type(returned.toolResult)~="table"then return nil,"FUNCTION_RESULT_PROTOCOL"end
    B.S.nativeTick=returned.nativeTick or B.S.nativeTick
    if type(returned.operationId)~="string"or returned.operationId==""then return nil,"FUNCTION_OPERATION_ID_MISSING"end
    local appliedStatus=B:applyTool(returned.toolResult,result)
    local acked,ackError=bridge:toolAck({operationId=returned.operationId,
        worldTimeMs=math.floor(B.S.worldTime*1000),executionStatus=appliedStatus})
    if not acked then return nil,ackError or"FUNCTION_ACK_UNKNOWN"end
    B:emit("FUNCTION_ACKNOWLEDGED",{operationId=returned.operationId,executionStatus=appliedStatus})
    B:emit("FUNCTION_COMPLETED",{actionId=action.actionId,nativeTick=B.S.nativeTick,
        participantResult=returned.toolResult,hostChoseFunctionOrder=true})
    return true
end
local function feedback(result,action,observation,queryResult)
    phase="FEEDBACK";B.S.mode="WAIT";B.S.reason="CONSECUENCIA / RELOJ AMBIENTAL PAUSADO";B:publish()
    local fields=B:feedbackFields(result,action,observation,queryResult)
    B:emit("FEEDBACK_SUBMITTED",fields)
    local returned,err=bridge:feedback(fields,function()B:publish()end)
    if returned then
        B.S.nativeTick=returned.nativeTick or B.S.nativeTick
        B.S.completedCycles+=1
        if observation.phase=="ROUTE_CHOICE"then B.S.completedRouteOpportunities+=1 end
        lastActionId=action.actionId
        lastFeedbackOperationId=returned.operationId or returned.feedbackOperationId
        -- A missing feedback ID blocks a joint checkpoint, never creates one.
        B:emit("FEEDBACK_COMPLETED",{cycle=B.S.cycle,nativeTick=B.S.nativeTick,
            phase=observation.phase,feedbackOperationId=lastFeedbackOperationId,
            completeRouteOpportunity=observation.phase=="ROUTE_CHOICE"})
        cursor=B.S.completedCycles+1;phase="BOUNDARY"
    end
    return returned,err
end
local function boundary()
    return {phase="BOUNDARY",native_phase="IDLE",completed_opportunities=B.S.completedCycles,
        next_opportunity=cursor,pending_action=nil,pending_operation=nil,uncertain=false,
        last_action_id=lastActionId,acknowledged_action_id=acknowledgedActionId,
        last_feedback_operation_id=lastFeedbackOperationId}
end
local function finishSession(suspend)
    local endpoint=suspend and"/v1/suspend"or"/v1/stop"
    local payload={reason=suspend and"CHECKPOINT_BOUNDARY"or"HORIZON_COMPLETE"}
    if suspend then
        payload.completedCycles=B.S.completedCycles;payload.nextOpportunity=cursor
        payload.lastActionId=lastActionId;payload.feedbackOperationId=lastFeedbackOperationId
    end
    local value,err=bridge:post(endpoint,payload)
    if not value then fail(err or"SESSION_CLOSE_UNKNOWN");return end
    running=false;B.S.mode="WAIT";B.S.reason=suspend and"FRONTERA GUARDADA / REAPERTURA PENDIENTE"or"HORIZONTE CERRADO"
    phase="BOUNDARY";B:publish()
    B:emit(suspend and"SESSION_SUSPENDED"or"SESSION_CLOSED",{completedCycles=B.S.completedCycles,nextOpportunity=cursor,
        delivered=B.S.delivered,queries=B.S.queries,tollSpent=B.S.tollSpent,collisions=B.S.collisions,moves=B.S.moves,
        resources=B.S.resourceCount,numberAPresent=B.S.numberAPresent,codeBPresent=B.S.codeBPresent})
end
local function start()
    if running or bridge or C.OwnerUserId<=0 then return end
    assert(C.ScenarioFingerprint~=string.rep("0",64),"C02_UNSEALED_SCENARIO")
    running=true;phase="STARTING";B.closeRequested=false;B.S.reason="CONECTANDO";B:publish()
    bridge=Bridge.new()
    local started,err
    if restoredBridge then
        assert(type(bridge.resumeCheckpoint)=="function","C02_EXPLICIT_RESUME_METHOD_REQUIRED")
        started,err=bridge:resumeCheckpoint(restoredBridge)
    else started,err=bridge:start(C.Participant)end
    if not started then fail(err or"START_FAILED");return end
    B.S.sessionId=bridge.sessionId
    B.S.lifeId=started.lifeId or B.S.lifeId
    B.S.nativeTick=started.nativeTick or B.S.nativeTick
    B:emit(restoredBridge and"SESSION_RESUMED"or"SESSION_START",{sessionId=bridge.sessionId,
        participant=C.Participant,startOpportunity=cursor,scenarioFingerprint=C.ScenarioFingerprint,
        body="PREPARED_KINEMATIC_AND_CONTACT_TOOLS",functionOrder="PREPARED_BY_LOCATION",
        returnLaw="ACTUAL_COLLISION_INVALID_ACTION_OR_CODE_REJECTION"})
    for cycle=cursor,C.MaxCycles do
        if B.closeRequested then break end
        B:beginCycle(cycle);phase="Q1"
        local q1=B:observe("QUERY_CHOICE");local a1,e1=decide(q1)
        if not a1 then fail(e1);return end
        if a1.name~="ASK_STATION"and a1.name~="SKIP_STATION"and a1.name~="SAFE_WAIT"then fail("Q1_ACTION_REJECTED");return end
        local r1,x1=B:execute(a1);if not r1 then fail(x1);return end
        local ok1,k1=ack(a1);if not ok1 then fail(k1);return end
        if a1.name=="SAFE_WAIT"then
            local done,why=feedback(r1,a1,q1,nil);if not done then fail(why);return end
        else
            phase="Q2";local q2=B:observe("ROUTE_CHOICE");local a2,e2=decide(q2)
            if not a2 then fail(e2);return end
            if a2.name~="EXIT_0"and a2.name~="EXIT_1"and a2.name~="SAFE_WAIT"then fail("Q2_ACTION_REJECTED");return end
            local r2,x2=B:execute(a2);if not r2 then fail(x2);return end
            local ok2,k2=ack(a2);if not ok2 then fail(k2);return end
            local used,toolErr=useTool(r2,a2,q2);if not used then fail(toolErr);return end
            local done,why=feedback(r2,a2,q2,r1);if not done then fail(why);return end
        end
        if B.closeRequested or(C.SuspendAfter and B.S.completedCycles==C.SuspendAfter)then
            finishSession(true);return
        end
    end
    finishSession(B.closeRequested==true)
end

local capture=Instance.new("BindableFunction");capture.Name="RBX01Checkpoint_C02"
capture.OnInvoke=function(context)
    assert(not running and phase=="BOUNDARY"and not B.pendingTool,"C02_NO_CHECKPOINT_DURING_ACTION")
    context.boundary=boundary()
    context.controller={phase="BOUNDARY",next_opportunity=cursor,completed_opportunities=B.S.completedCycles,
        participant=C.Participant,last_action_id=lastActionId,acknowledged_action_id=acknowledgedActionId,
        last_feedback_operation_id=lastFeedbackOperationId}
    context.rng={algorithm="PREDECLARED_EVENT_TABLE_V1",cycle=B.S.cycle,scenario_sha256=C.ScenarioFingerprint}
    context.managed_roots={"Gates","Pickups","ContactMarkers_C02","LocalPricePanels_C02","Devices_C02"}
    context.world_id=C.WorldId;context.scenario_sha256=C.ScenarioFingerprint
    context.native_life_id=B.S.lifeId;context.native_tick=B.S.nativeTick
    return State.capture(B,context)
end
capture.Parent=ServerStorage
local restore=Instance.new("BindableFunction");restore.Name="RBX01Restore_C02"
restore.OnInvoke=function(state,expected)
    assert(not running and bridge==nil and phase=="PREPARED","C02_RESTORE_ONLY_FRESH_PREPARED_CONTROLLER")
    local returned=State.apply(B,state,expected)
    cursor=returned.next_opportunity;phase="BOUNDARY";restoredBridge=returned.bridge
    lastActionId=returned.controller.last_action_id;acknowledgedActionId=returned.controller.acknowledged_action_id
    lastFeedbackOperationId=returned.controller.last_feedback_operation_id
    B.closeRequested=false;return returned
end
restore.Parent=ServerStorage

ReplicatedStorage:WaitForChild("RBX01Control").OnServerEvent:Connect(function(player,command)
    if player.UserId~=C.OwnerUserId or(activeOwner and activeOwner~=player)or type(command)~="string"then return end
    if command=="START_NATIVE"then task.spawn(start)
    elseif command=="PAUSE"then B.paused=not B.paused;B:publish()
    elseif command=="SAVE_CLOSE_BOUNDARY"or command=="SAVE_CLOSE"then
        B.closeRequested=true;B.paused=false;B.S.reason="CIERRE EN PRÓXIMA FRONTERA";B:publish()
    end
end)
Players.PlayerAdded:Connect(function(player)
    if player.UserId~=C.OwnerUserId or activeOwner then player:Kick("RBX01 propietario requerido");return end
    activeOwner=player;B:publish()
end)
Players.PlayerRemoving:Connect(function(player)if activeOwner==player then B.closeRequested=true;B.paused=false end end)
game:BindToClose(function()
    B.closeRequested=true;B.paused=false
    -- No blind stop/replay if a material operation may still be in flight.
    if running then B:emit("PLATFORM_CLOSE_REQUESTED",{phase=phase,uncertainUntilReceipts=true})end
end)
assert(C.AutoStart=="NONE","C02_CONTROLLED_START_ONLY")
