-- LOCAL R03 transport revision. Same RBX01 HTTP contract and Native codec.
-- Studio only: MCP relays exact request/response blobs via ServerStorage.
-- No HttpService request, secret, navigation, action selection or client remote.
local HttpService = game:GetService("HttpService")
local ServerStorage = game:GetService("ServerStorage")
local RunService = game:GetService("RunService")
local C = require(script.Parent.Config)
local Bridge = {}
Bridge.__index = Bridge
local MAILBOX_PROTOCOL = "RBX01.MAILBOX.C02"
local MAILBOX_NAME = "RBX01Mailbox_C02"
local MAX_REQUEST_BYTES = 16384
local MAX_RESPONSE_BYTES = 65536
local REQUEST_TIMEOUT_SECONDS = 120
local BOOTSTRAP_TIMEOUT_SECONDS = 600
local ROUTES = {
    ["/v1/session/start"]=true, ["/v1/observation"]=true,
    ["/v1/decision"]=true, ["/v1/query_sensor"]=true,
    ["/v1/function"]=true, ["/v1/tool_ack"]=true, ["/v1/suspend"]=true, ["/v1/feedback"]=true, ["/v1/ack"]=true, ["/v1/state"]=true,
    ["/v1/pause"]=true, ["/v1/resume"]=true, ["/v1/stop"]=true,
}
local function mailbox()
    assert(RunService:IsStudio(), "LOCAL_C02_IS_STUDIO_ONLY")
    assert(C.OwnerUserId == 11981994305, "LOCAL_C02_OWNER_MISMATCH")
    local folder = ServerStorage:FindFirstChild(MAILBOX_NAME)
    if not folder then
        folder = Instance.new("Folder")
        folder.Name = MAILBOX_NAME
        folder:SetAttribute("Protocol", MAILBOX_PROTOCOL)
        folder:SetAttribute("OwnerUserId", C.OwnerUserId)
        folder:SetAttribute("NativePolicyInRelay", false)
        for _, name in ipairs({"Request", "Response"}) do
            local value = Instance.new("StringValue")
            value.Name = name
            value.Value = ""
            value.Parent = folder
        end
        folder.Parent = ServerStorage
    end
    assert(folder:IsA("Folder") and folder:GetAttribute("Protocol") == MAILBOX_PROTOCOL,
        "LOCAL_C02_MAILBOX_PROTOCOL_MISMATCH")
    assert(folder:GetAttribute("OwnerUserId") == C.OwnerUserId, "LOCAL_C02_MAILBOX_OWNER_MISMATCH")
    assert(folder:FindFirstChild("Request") and folder.Request:IsA("StringValue"),
        "LOCAL_C02_REQUEST_SLOT_MISSING")
    assert(folder:FindFirstChild("Response") and folder.Response:IsA("StringValue"),
        "LOCAL_C02_RESPONSE_SLOT_MISSING")
    return folder
end
function Bridge.new()
    return setmetatable({sessionId=nil, serverInstanceId="studio_"..HttpService:GenerateGUID(false),
        lastRequest=0, mailbox=mailbox(), postInProgress=false}, Bridge)
end
local function uuid(prefix)
    return prefix.."_"..HttpService:GenerateGUID(false)
end
local function exchange(self, path, body, requestId, attempt)
    local folder = self.mailbox
    local requestSlot, responseSlot = folder.Request, folder.Response
    local envelope = HttpService:JSONEncode({
        mailboxProtocol=MAILBOX_PROTOCOL, requestId=requestId,
        path=path, body=body, attempt=attempt,
    })
    -- Never overwrite a pending transaction or a late, unconsumed response.
    if requestSlot.Value ~= "" or responseSlot.Value ~= "" then
        return nil, "MAILBOX_PENDING_PRESERVED"
    end
    requestSlot.Value = envelope
    local started = os.clock()
    local timeoutSeconds = path == "/v1/session/start" and BOOTSTRAP_TIMEOUT_SECONDS or REQUEST_TIMEOUT_SECONDS
    while os.clock()-started < timeoutSeconds do
        if requestSlot.Value ~= envelope then return nil, "MAILBOX_REQUEST_CHANGED_PRESERVED" end
        local raw = responseSlot.Value
        if raw ~= "" then
            if #raw > MAX_RESPONSE_BYTES + 32768 then return nil, "MAILBOX_RESPONSE_OVERSIZE_PRESERVED" end
            local ok, response = pcall(function() return HttpService:JSONDecode(raw) end)
            if not ok or type(response) ~= "table"
                or response.mailboxProtocol ~= MAILBOX_PROTOCOL
                or response.requestId ~= requestId or response.path ~= path
                or response.requestBody ~= body or response.attempt ~= attempt
                or type(response.success) ~= "boolean" or type(response.statusCode) ~= "number"
                or response.statusCode%1 ~= 0 or response.statusCode < 100 or response.statusCode > 599
                or type(response.body) ~= "string" or #response.body > MAX_RESPONSE_BYTES then
                return nil, "MAILBOX_RESPONSE_CONFLICT_PRESERVED"
            end
            -- Consumption is technical receipt only. Action execution and ACK
            -- remain in the unchanged Controller, after Bridge:decide returns.
            requestSlot.Value = ""
            responseSlot.Value = ""
            return response
        end
        task.wait(.05)
    end
    -- A response may still arrive. Keep both slots for reconciliation; do not
    -- create a fresh ID or enact a late action after Controller has stopped.
    return nil, "MAILBOX_TIMEOUT_PRESERVED"
end
function Bridge:post(path, fields)
    if not RunService:IsStudio() then return nil, "LOCAL_C02_IS_STUDIO_ONLY" end
    if not ROUTES[path] or type(fields) ~= "table" then return nil, "MAILBOX_ROUTE_OR_BODY_REJECTED" end
    if self.postInProgress then return nil, "MAILBOX_CONCURRENT_POST_PRESERVED" end
    fields.apiVersion = C.Protocol
    fields.requestId = fields.requestId or uuid("req")
    fields.serverInstanceId = self.serverInstanceId
    if self.sessionId then fields.sessionId = self.sessionId end
    -- Exact request ID and serialized bytes survive all bounded retries.
    local body = HttpService:JSONEncode(fields)
    if #body > MAX_REQUEST_BYTES then return nil, "MAILBOX_REQUEST_OVERSIZE" end
    self.postInProgress = true
    local function finish(value, reason)
        self.postInProgress = false
        return value, reason
    end
    for attempt=1,4 do
        local remaining = 1.05 - (os.clock()-self.lastRequest)
        if remaining>0 then task.wait(remaining) end
        self.lastRequest = os.clock()
        local response, exchangeError = exchange(self, path, body, fields.requestId, attempt)
        if not response then return finish(nil, exchangeError) end
        if response.success then
            local decodedOK, decoded = pcall(function() return HttpService:JSONDecode(response.body) end)
            if decodedOK then return finish(decoded) end
            return finish(nil, "INVALID_RESPONSE_JSON")
        end
        if response.statusCode~=429 and response.statusCode<500 then
            return finish(nil, "HTTP_"..tostring(response.statusCode))
        end
        if attempt<4 then task.wait(math.min(2^(attempt-1),8)) end
    end
    return finish(nil, "INFRASTRUCTURE_RECONCILIATION_REQUIRED")
end
function Bridge:start(mode)
    local result,err=self:post("/v1/session/start",{ownerUserId=C.OwnerUserId,worldId=C.WorldId,mode=mode,level="L4"})
    if result then self.sessionId=result.sessionId or (result.session and result.session.sessionId) end
    if not self.sessionId then return nil,err or "NO_SESSION_ID" end
    return result
end
function Bridge:waitOperation(result,onPoll,wantsAction)
    local operationId=result.operationId or (result.operation and result.operation.operationId)
    for poll=1,480 do
        -- A completed operation can outlive a stopped/expired/paused session.
        -- Reconcile its receipt, but never enact its action after the session ceased being ACTIVE.
        if result.operation and result.status~="ACTIVE" then
            return nil,"SESSION_"..tostring(result.status)
        end
        local operation=result.operation or result
        local completion=operation.result or result.result or operation
        if wantsAction and completion.action then return completion.action end
        local status=operation.status or result.status
        if not wantsAction and status=="COMPLETED" and completion.accepted then completion.operationId=operationId; return completion end
        if status=="FAILED" or status=="STOPPED" or status=="HOST_SAFETY_STOP" or status=="UNCERTAIN" or status=="CANCELLED" then return nil,status end
        if not operationId then return nil,"NO_OPERATION_ID" end
        onPoll(operation)
        task.wait(C.PollSeconds)
        local err
        result,err=self:post("/v1/state",{operationId=operationId})
        if not result then return nil,err end
    end
    return nil,"OPERATION_TIMEOUT_PRESERVED"
end
function Bridge:decide(observation,onPoll)
    local admitted,err=self:post("/v1/observation",observation)
    if not admitted then return nil,err end
    local endpoint=observation.phase=="QUERY_CHOICE" and "/v1/decision" or "/v1/query_sensor"
    local result,decisionError=self:post(endpoint,{observationId=observation.observationId,seq=observation.seq})
    if not result then return nil,decisionError end
    return self:waitOperation(result,onPoll,true)
end
function Bridge:feedback(fields,onPoll)
    local result,err=self:post("/v1/feedback",fields)
    if not result then return nil,err end
    return self:waitOperation(result,onPoll,false)
end
function Bridge:tool(fields,onPoll)
    local result,err=self:post("/v1/function",fields)
    if not result then return nil,err end
    return self:waitOperation(result,onPoll,false)
end
function Bridge:toolAck(fields)
    return self:post("/v1/tool_ack",fields)
end
function Bridge:resumeCheckpoint(context)
    assert(type(context)=="table" and type(context.session_id)=="string" and type(context.server_instance_id)=="string","C02_RESUME_CONTEXT_REQUIRED")
    assert(type(context.resumeTransport)=="table" and type(context.resumeTransport.checkpointId)=="string" and type(context.resumeTransport.checkpointSha256)=="string","C02_EXTERNAL_BOUND_CHECKPOINT_REQUIRED")
    self.sessionId=context.session_id;self.serverInstanceId=context.server_instance_id
    return self:post("/v1/resume",{checkpointId=context.resumeTransport.checkpointId,checkpointSha256=context.resumeTransport.checkpointSha256})
end
return Bridge

