-- DEE reusable server connector. Backend decisions remain outside this module.
-- No HTTP, secret, Native query, target solver, player kick or auto-start.
local Http=game:GetService("HttpService")
local Storage=game:GetService("ServerStorage")
local Tags=game:GetService("CollectionService")
local Run=game:GetService("RunService")
local Binding=require(script.Parent.BackendBinding)
local function sameBinding(a,b)
 if type(a)~=type(b)then return false end;if type(a)~="table"then return a==b end
 for k,v in pairs(a)do if not sameBinding(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end;return true
end
local M={Schema="DEE.RBX.Connector.R01"}
local runtimes={}
local Agent={};Agent.__index=Agent
local Runtime={};Runtime.__index=Runtime
local function copy(v)return Http:JSONDecode(Http:JSONEncode(v))end
local function id(v)
    assert(type(v)=="string"and #v>0 and #v<=96 and not string.find(v,"[^%w_%-]"),"DEE_SAFE_ID_REQUIRED")
    return v
end
local function integer(v)return type(v)=="number"and v%1==0 and v>=0 end
local function guid(prefix)return prefix.."_"..Http:GenerateGUID(false)end
local function value(parent,class,name,initial)
    local v=Instance.new(class);v.Name=name;v.Value=initial;v.Parent=parent;return v
end
local function folder(parent,name)
    local f=Instance.new("Folder");f.Name=name;f.Parent=parent;return f
end
local function decode(raw)
    assert(type(raw)=="string"and #raw<=65536,"DEE_MESSAGE_BOUND")
    local ok,v=pcall(Http.JSONDecode,Http,raw);assert(ok and type(v)=="table","DEE_JSON_OBJECT_REQUIRED");return v
end
function Agent:_save()
    self.node.State.Value=Http:JSONEncode(self.s)
    self.node.ActionCursor.Value=self.s.actionCursor
    self.node.OpportunityCursor.Value=self.s.completedOpportunities
    self.node.Sequence.Value=self.s.sequence
    self.node:SetAttribute("Phase",self.s.phase)
end
function Agent:_exclusive(fn)
    assert(not self.busy,"DEE_CONCURRENT_ENTITY_CALL")
    self.busy=true;local ok,result=pcall(fn);self.busy=false
    if not ok then error(result,0)end;return result
end
function Agent:_identity(message)
    assert(message.protocol==M.Schema and message.namespace==self.namespace,"DEE_TRANSPORT_NAMESPACE")
    assert(message.sessionId==self.s.sessionId,"DEE_TRANSPORT_SESSION")
end
function Agent:bindSession(context)
    return self:_exclusive(function()
        assert(self.s.phase=="PREPARED"and self.s.sessionId=="","DEE_NO_SESSION_OVERWRITE")
        self.s.sessionId=id(context.sessionId);self.s.lifeId=id(context.lifeId)
        assert(integer(context.nativeTick),"DEE_TICK_REQUIRED")
        self.s.nativeTick=context.nativeTick;self.s.phase="BOUNDARY";self:_save()
        return self:status()
    end)
end
function Agent:observe(phase)
    return self:_exclusive(function()
        local continuation=self.s.phase=="ACTION_ACKNOWLEDGED"and self.s.observation.phase=="QUERY_CHOICE"
            and self.s.lastActionName~="SAFE_WAIT"and phase=="ROUTE_CHOICE"
        assert(self.s.phase=="BOUNDARY"or continuation,"DEE_OBSERVE_PHASE")
        assert(not self.s.closeRequested,"DEE_CLOSE_REQUESTED")
        assert(phase=="QUERY_CHOICE"or phase=="ROUTE_CHOICE","DEE_OBSERVATION_PHASE")
        assert(self.s.completedOpportunities<self.config.MaxOpportunities,"DEE_HORIZON_CLOSED")
        local observation=self.adapters.sensors:observe(phase)
        assert(type(observation)=="table"and type(observation.sensors)=="table","DEE_SENSOR_CONTRACT")
        self.s.sequence+=1
        observation.protocol=M.Schema;observation.namespace=self.namespace;observation.sessionId=self.s.sessionId
        observation.observationId=guid("obs");observation.seq=self.s.sequence
        observation.opportunity=self.s.completedOpportunities+1;observation.phase=phase
        observation.previousActionId=self.s.lastActionId
        self.s.observation=copy(observation);self.s.phase="AWAIT_ACTION"
        self.node.Observation.Value=Http:JSONEncode(observation);self:_save();return copy(observation)
    end)
end
function Agent:deliverAction(raw)
    return self:_exclusive(function()
        local message=decode(raw);self:_identity(message)
        local actionId=id(message.actionId);local operationId=id(message.operationId)
        local prior=self.node.Actions:FindFirstChild(actionId)
        if prior then
            local receipt=decode(prior.Value)
            assert(receipt.rawRequest==raw,"DEE_ACTION_ID_CONFLICT")
            assert(receipt.status=="EXECUTED"or receipt.status=="ACKNOWLEDGED"or receipt.status=="COMMITTED","DEE_PARTIAL_ACTION_PRESERVED")
            return copy(receipt.ack) -- no physical replay, no new ACK fabricated
        end
        assert(self.s.phase=="AWAIT_ACTION","DEE_ACTION_PHASE")
        assert(message.observationId==self.s.observation.observationId and message.seq==self.s.sequence,"DEE_OBSERVATION_CORRELATION")
        assert(type(message.action)=="table"and type(message.action.name)=="string","DEE_ACTION_CONTRACT")
        local technical=message.sourceKind=="MCP_TECHNICAL_CONTROL"
        assert(message.sourceKind==self.binding.sourceKind or(technical and self.config.AllowTechnicalTest==true),"DEE_DECISION_SOURCE")
        assert(#self.node.Actions:GetChildren()<self.config.MaxActions,"DEE_ACTION_LEDGER_BOUND")
        local receipt={status="PREPARED",rawRequest=raw,operationId=operationId,technical=technical}
        local entry=value(self.node.Actions,"StringValue",actionId,Http:JSONEncode(receipt))
        self.s.phase="EXECUTING";self.s.pendingActionId=actionId;self.s.pendingOperationId=operationId;self:_save()
        local ok,result=pcall(self.adapters.body.execute,self.adapters.body,copy(message.action))
        if not ok then
            receipt.status="UNCERTAIN";receipt.error=tostring(result);entry.Value=Http:JSONEncode(receipt)
            self.s.phase="FAILED_PRESERVED";self.s.lastError=tostring(result);self:_save()
            error("DEE_BODY_EXECUTION_PRESERVED:"..tostring(result),0)
        end
        assert(type(result)=="table","DEE_BODY_RESULT_REQUIRED")
        local ack={protocol=M.Schema,namespace=self.namespace,sessionId=self.s.sessionId,
            actionId=actionId,operationId=operationId,observationId=message.observationId,seq=message.seq,
            executionStatus="EXECUTED",result=copy(result),technicalControl=technical}
        receipt.status="EXECUTED";receipt.ack=ack;entry.Value=Http:JSONEncode(receipt)
        self.node.ActionInbox.Value=raw;self.node.ActionAck.Value=Http:JSONEncode(ack)
        self.s.result=copy(result);self.s.lastActionName=message.action.name
        self.s.phase="AWAIT_ACTION_ACK";self:_save();return copy(ack)
    end)
end
function Agent:confirmActionAck(actionId,operationId)
    return self:_exclusive(function()
        assert(self.s.phase=="AWAIT_ACTION_ACK"and actionId==self.s.pendingActionId and operationId==self.s.pendingOperationId,"DEE_EXACT_ACTION_ACK")
        local entry=assert(self.node.Actions:FindFirstChild(actionId));local receipt=decode(entry.Value)
        receipt.status="ACKNOWLEDGED";entry.Value=Http:JSONEncode(receipt)
        self.s.lastActionId=actionId;self.s.actionCursor+=1
        self.s.phase="ACTION_ACKNOWLEDGED";self.node.ActionAck.Value="";self.node.ActionInbox.Value="";self:_save()
        return self:status()
    end)
end
function Agent:toolRequest()
    assert(self.s.phase=="ACTION_ACKNOWLEDGED","DEE_TOOL_ORDER")
    if type(self.adapters.body.toolRequest)~="function"then return nil end
    local tool=self.adapters.body:toolRequest(copy(self.s.result),copy(self.s.observation))
    return tool and copy(tool)or nil
end
function Agent:deliverTool(raw)
    return self:_exclusive(function()
        local message=decode(raw);self:_identity(message);local operationId=id(message.operationId)
        assert(message.actionId==self.s.lastActionId,"DEE_TOOL_ACTION_CORRELATION")
        local old=self.node.Tools:FindFirstChild(operationId)
        if old then local item=decode(old.Value);assert(item.rawRequest==raw and item.status=="APPLIED","DEE_TOOL_ID_CONFLICT_OR_PARTIAL");return copy(item.ack)end
        assert(self.s.phase=="ACTION_ACKNOWLEDGED"and type(self.adapters.body.applyTool)=="function","DEE_TOOL_NOT_AVAILABLE")
        assert(type(message.toolResult)=="table","DEE_TOOL_RESULT_REQUIRED")
        local record={status="PREPARED",rawRequest=raw};local entry=value(self.node.Tools,"StringValue",operationId,Http:JSONEncode(record))
        self.s.phase="APPLYING_TOOL";self:_save()
        local ok,result=pcall(self.adapters.body.applyTool,self.adapters.body,copy(message.toolResult),self.s.result)
        if not ok then self.s.phase="FAILED_PRESERVED";record.status="UNCERTAIN";record.error=tostring(result);entry.Value=Http:JSONEncode(record);self:_save();error(result,0)end
        assert(result=="APPLIED"or result=="NO_RESULT","DEE_TOOL_APPLICATION_STATUS")
        record.ack={protocol=M.Schema,namespace=self.namespace,sessionId=self.s.sessionId,operationId=operationId,actionId=message.actionId,executionStatus=result}
        record.status="APPLIED";entry.Value=Http:JSONEncode(record)
        self.s.toolOperationId=operationId;self.s.phase="AWAIT_TOOL_ACK";self.node.ToolAck.Value=Http:JSONEncode(record.ack);self:_save();return copy(record.ack)
    end)
end
function Agent:confirmToolAck(operationId)
    return self:_exclusive(function()
        assert(self.s.phase=="AWAIT_TOOL_ACK"and self.s.toolOperationId==operationId,"DEE_EXACT_TOOL_ACK")
        self.node.ToolAck.Value="";self.s.phase="TOOL_ACKNOWLEDGED";self:_save();return self:status()
    end)
end
function Agent:completeFeedback(context)
    return self:_exclusive(function()
        assert(self.s.phase=="ACTION_ACKNOWLEDGED"or self.s.phase=="TOOL_ACKNOWLEDGED","DEE_FEEDBACK_PHASE")
        assert(context.actionId==self.s.lastActionId,"DEE_FEEDBACK_ACTION")
        if self.s.observation.phase=="QUERY_CHOICE"then assert(self.s.lastActionName=="SAFE_WAIT","DEE_QUERY_NEEDS_ROUTE_OR_WAIT")end
        self.s.lastFeedbackOperationId=id(context.feedbackOperationId)
        assert(integer(context.nativeTick),"DEE_FEEDBACK_TICK")
        self.s.nativeTick=context.nativeTick;self.s.completedOpportunities+=1
        local entry=assert(self.node.Actions:FindFirstChild(context.actionId));local r=decode(entry.Value);r.status="COMMITTED";entry.Value=Http:JSONEncode(r)
        self.s.pendingActionId=nil;self.s.pendingOperationId=nil;self.s.toolOperationId=nil
        self.s.phase="BOUNDARY";self.s.result=nil;self.node.Observation.Value="";self:_save();return self:status()
    end)
end
function Agent:requestClose()
    self.s.closeRequested=true;self:_save();return self:status()
end
function Agent:status()return copy(self.s)end
function Agent:capture(context)
    assert(self.s.phase=="BOUNDARY"and self.node.ActionAck.Value==""and self.node.ToolAck.Value=="","DEE_CHECKPOINT_BOUNDARY_ONLY")
    assert(context.backendWriterClosed==true and context.bridgeQuiescent==true,"DEE_CLOSED_PAIR_PROOF_REQUIRED")
    assert(context.sessionId==self.s.sessionId and context.lifeId==self.s.lifeId and context.nativeTick==self.s.nativeTick,"DEE_PAIR_CONTEXT")
    local actions,tools={},{}
    for _,entry in ipairs(self.node.Actions:GetChildren())do
        local item=decode(entry.Value);assert(item.status=="ACKNOWLEDGED"or item.status=="COMMITTED","DEE_PENDING_RECEIPT_PRESERVED")
        actions[entry.Name]=item
    end
    for _,entry in ipairs(self.node.Tools:GetChildren())do tools[entry.Name]=decode(entry.Value)end
    return {schema="DEE.RBX.AgentWorldCheckpoint.R01",namespace=self.namespace,scenarioFingerprint=self.runtime.config.ScenarioFingerprint,
        bindings=copy(assert(self.runtime.config.PersistenceBinding,"R06_BINDINGS_REQUIRED")),
        state=copy(self.s),actions=actions,tools=tools,body=self.adapters.body:capture(),world=self.adapters.world:capture(),
        scope="WORLD_AND_TRANSPORT_ONLY_REQUIRES_COMPLETE_MATCHING_NATIVE_SERVICE",backend=copy(context)}
end
function Agent:restore(state,expected)
    return self:_exclusive(function()
        assert(self.s.phase=="PREPARED"and self.s.actionCursor==0 and #self.node.Actions:GetChildren()==0,"DEE_FRESH_RESTORE_ONLY")
        assert(state.schema=="DEE.RBX.AgentWorldCheckpoint.R01"and state.namespace==self.namespace and state.scenarioFingerprint==self.runtime.config.ScenarioFingerprint,"DEE_CHECKPOINT_IDENTITY")
        assert(expected.backendWriterClosed==true and expected.bridgeQuiescent==true and type(expected.checkpointSha256)=="string"and #expected.checkpointSha256==64 and not string.find(expected.checkpointSha256,"[^0-9a-f]"),"DEE_EXTERNAL_PAIR_ANCHOR")
        assert(expected.sessionId==state.state.sessionId and expected.lifeId==state.state.lifeId and expected.nativeTick==state.state.nativeTick,"DEE_RESTORE_PAIR_CONTEXT")
        assert(state.state.phase=="BOUNDARY"and state.state.pendingActionId==nil,"DEE_RESTORE_BOUNDARY")
        assert(sameBinding(state.bindings,self.runtime.config.PersistenceBinding),"R06_RESTORE_BINDINGS")
        self.adapters.world:restore(copy(state.world));self.adapters.body:restore(copy(state.body))
        for key,item in pairs(state.actions)do id(key);value(self.node.Actions,"StringValue",key,Http:JSONEncode(item))end
        for key,item in pairs(state.tools)do id(key);value(self.node.Tools,"StringValue",key,Http:JSONEncode(item))end
        self.s=copy(state.state);self.s.closeRequested=false;self:_save();return self:status()
    end)
end
function Runtime:register(model)
    assert(model:IsA("Model")and model.PrimaryPart and model:IsDescendantOf(self.config.RegistryRoot),"DEE_REGISTERED_MODEL_SCOPE")
    assert(Tags:HasTag(model,"DEE_Agent"),"DEE_AGENT_TAG_REQUIRED")
    local agentId=id(model:GetAttribute("DEE_AgentId"));assert(not self.agents[agentId],"DEE_DUPLICATE_AGENT_ID")
    local cfg=assert(self.config.Agents[agentId],"DEE_UNCONFIGURED_AGENT")
    local binding=Binding.resolve(cfg.Participant)
    assert(integer(cfg.MaxOpportunities)and cfg.MaxOpportunities>0 and cfg.MaxOpportunities<=1000,"DEE_FINITE_HORIZON")
    cfg=copy(cfg);cfg.MaxActions=cfg.MaxActions or cfg.MaxOpportunities*2
    assert(integer(cfg.MaxActions)and cfg.MaxActions>0 and cfg.MaxActions<=2000,"DEE_FINITE_ACTION_LEDGER")
    assert(not self.node:FindFirstChild(agentId),"DEE_EXISTING_RUNTIME_PRESERVED")
    local adapters=self.config.MakeAdapters(model,cfg)
    for _,name in ipairs({"body","sensors","world"})do assert(type(adapters[name])=="table","DEE_INJECTED_ADAPTER_REQUIRED")end
    local node=folder(self.node,agentId);node:SetAttribute("Protocol",M.Schema)
    local namespace=self.config.ExperienceId.."/"..self.config.SceneId.."/"..agentId
    node:SetAttribute("Namespace",namespace);node:SetAttribute("Participant",binding.mode)
    for _,name in ipairs({"State","Observation","ActionInbox","ActionAck","ToolAck"})do value(node,"StringValue",name,"")end
    for _,name in ipairs({"ActionCursor","OpportunityCursor","Sequence"})do value(node,"IntValue",name,0)end
    folder(node,"Actions");folder(node,"Tools")
    local a=setmetatable({runtime=self,namespace=namespace,node=node,config=cfg,binding=binding,adapters=adapters,busy=false,
        s={phase="PREPARED",sessionId="",lifeId="",nativeTick=0,sequence=0,actionCursor=0,completedOpportunities=0,closeRequested=false}},Agent)
    self.agents[agentId]=a;a:_save();return a
end
function Runtime:scanTagged()
    local candidates={}
    for _,model in ipairs(Tags:GetTagged("DEE_Agent"))do if model:IsDescendantOf(self.config.RegistryRoot)then table.insert(candidates,model)end end
    table.sort(candidates,function(a,b)return tostring(a:GetAttribute("DEE_AgentId"))<tostring(b:GetAttribute("DEE_AgentId"))end)
    for _,model in ipairs(candidates)do if not self.agents[model:GetAttribute("DEE_AgentId")]then self:register(model)end end
    return self.agents
end
function Runtime:get(agentId)return assert(self.agents[agentId],"DEE_AGENT_NOT_REGISTERED")end
function Runtime:watchTagged()
    assert(not self.connections,"DEE_REGISTRY_ALREADY_WATCHING")
    self.connections={
        Tags:GetInstanceAddedSignal("DEE_Agent"):Connect(function(model)
            if model:IsDescendantOf(self.config.RegistryRoot)then
                local ok,err=pcall(self.register,self,model)
                if not ok then self.node:SetAttribute("RegistrationError",tostring(err))end
            end
        end),
        Tags:GetInstanceRemovedSignal("DEE_Agent"):Connect(function(model)
            local a=self.agents[model:GetAttribute("DEE_AgentId")]
            if a then a:requestClose()end -- preserve receipts, no cancellation/replay
        end),
    }
end
function Runtime:stopWatching()
    for _,connection in ipairs(self.connections or{})do connection:Disconnect()end
    self.connections=nil
end
function M.lookupRuntime(experienceId,sceneId)
    return assert(runtimes[id(experienceId).."/"..id(sceneId)],"DEE_RUNTIME_NOT_MOUNTED")
end
function M.mount(config)
    assert(Run:IsServer()and Run:IsStudio(),"DEE_LOCAL_STUDIO_SERVER_ONLY")
    id(config.ExperienceId);id(config.SceneId)
    assert(type(config.ScenarioFingerprint)=="string"and #config.ScenarioFingerprint==64,"DEE_SCENARIO_FINGERPRINT")
    assert(typeof(config.RegistryRoot)=="Instance"and type(config.MakeAdapters)=="function"and type(config.Agents)=="table","DEE_INJECTED_CONFIGURATION")
    local root=Storage:FindFirstChild("DEE_Runtime")
    if root then assert(root:IsA("Folder")and root:GetAttribute("Protocol")==M.Schema,"DEE_RUNTIME_CONFLICT")
    else root=folder(Storage,"DEE_Runtime");root:SetAttribute("Protocol",M.Schema)end
    local exp=root:FindFirstChild(config.ExperienceId)or folder(root,config.ExperienceId)
    assert(not exp:FindFirstChild(config.SceneId),"DEE_EXISTING_SCENE_RUNTIME_PRESERVED")
    local key=config.ExperienceId.."/"..config.SceneId
    assert(not runtimes[key],"DEE_RUNTIME_ALREADY_MOUNTED")
    local runtime=setmetatable({config=config,node=folder(exp,config.SceneId),agents={}},Runtime)
    runtimes[key]=runtime;return runtime
end
return M
