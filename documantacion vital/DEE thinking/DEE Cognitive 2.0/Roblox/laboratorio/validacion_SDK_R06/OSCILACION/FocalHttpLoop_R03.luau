-- Guarda de enlaceFOCAL antes de cualquierPOST; no decide acciones ni cambiaDTOs.
local Transport=require(script.Parent.HttpTransport)
local OriginalLoop=require(script.Parent.HttpLoop)
local M={}
function M.start(cfg)
 assert(cfg.Mode=="NATIVE"and cfg.MaxOpportunities==6 and cfg.RunCycles==6 and cfg.MaxActions==12,"FOCAL_FIXED_6_12_HORIZON")
 local expected={CONSUME_RECHARGE="OSCILANTE",NONCONSUMING_CONTROL="CONTROL"}
 local condition=assert(expected[cfg.Focal.Arm],"FOCAL_SCENE_ARM")
 local client=Transport.new(Transport.readPrivateConnection(cfg),cfg.Transport or{})
 client:assertQuiescent()
 local contract=client:waitReadyHandshake() -- GET only, no Native request/phase advancement
 assert(contract.profile=="FOCAL","FOCAL_PROFILE_REQUIRED_NOT_DEMO3")
 assert(contract.focalCondition==condition,"FOCAL_BACKEND_SCENE_CONDITION_MISMATCH")
 assert(contract.sequenceOffset==56 and type(contract.localSequence)=="number"and contract.localSequence>=0 and contract.localSequence<=12,"FOCAL_CURSOR_CONTRACT")
 -- OriginalLoop does exact pairedNEW/CONTINUE checks and retains every original ID.
 return OriginalLoop.start(cfg)
end
return M
