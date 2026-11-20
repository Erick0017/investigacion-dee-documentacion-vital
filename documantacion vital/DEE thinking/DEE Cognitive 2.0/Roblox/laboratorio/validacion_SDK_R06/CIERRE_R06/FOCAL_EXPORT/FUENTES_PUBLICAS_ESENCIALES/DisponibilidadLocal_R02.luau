-- Candidato focal aislado. Sólo disponibilidad física local; no Native ni selección de salida.
-- No se instala en KIT_DESARROLLADOR ni modifica el adapter aprobado.
local M={};local Law={};Law.__index=Law
local function checkPort(station,port)assert(type(station)=="number"and station%1==0 and station>=0 and station<=5 and(port==0 or port==1),"FOCAL_PORT")end
function M.new(gates,panels,cfg,emit)
 assert(cfg.rechargeEpochs==3 and cfg.capacityPerPort==1 and cfg.emptyPortToll==2 and cfg.maxCyclesPerArm==6,"FOCAL_FROZEN_LAW")
 assert(cfg.Arm=="CONSUME_RECHARGE"or cfg.Arm=="NONCONSUMING_CONTROL","FOCAL_ARM")
 local self=setmetatable({gates=gates,panels=panels,cfg=cfg,epoch=0,ports={},actions={},emit=emit or function()end},Law)
 for s=0,5 do
  assert(panels[s]and panels[s]:IsA("BasePart"),"FOCAL_PHYSICAL_PANEL_REQUIRED")
  self.ports[s]={}
  for p=0,1 do assert(gates[s]and gates[s][p]and gates[s][p]:IsA("BasePart"),"FOCAL_PHYSICAL_GATE_REQUIRED");self.ports[s][p]={available=true,rechargeAt=nil}end
 end
 self:_publish();return self
end
function Law:_publish()
 for s=0,5 do
  local costs={}
  for p=0,1 do
   local token=self.ports[s][p];local gate=self.gates[s][p]
   costs[p]=token.available and 0 or self.cfg.emptyPortToll
   gate:SetAttribute("FocalPassAvailable",token.available);gate:SetAttribute("FocalRechargeAt",token.rechargeAt)
   gate:SetAttribute("TollCost_C02",costs[p])
  end
  local panel=self.panels[s];local signal=nil
  if costs[0]==0 then signal=costs[1]==0 and 1 or 0 elseif costs[1]==0 then signal=2 end
  panel:SetAttribute("Price0_C02",costs[0]);panel:SetAttribute("Price1_C02",costs[1]);panel:SetAttribute("EncodedSignal_C02",signal)
  panel:SetAttribute("FocalPanelReadable",signal~=nil)
 end
end
function Law:beginEpoch(epoch)
 assert(epoch==self.epoch+1 and epoch<=6,"FOCAL_EXACT_FINITE_EPOCH");self.epoch=epoch
 for s=0,5 do for p=0,1 do local v=self.ports[s][p]
  if not v.available and epoch>=v.rechargeAt then v.available=true;v.rechargeAt=nil;self.emit("FOCAL_PASS_REPLENISHED",{station=s,port=p,epoch=epoch})end
 end end
 self:_publish()
end
function Law:quoteLocal(station,root)
 checkPort(station,0);assert(root and root:IsA("BasePart"),"FOCAL_REAL_BODY_REQUIRED")
 local panel=self.panels[station]
 assert((panel.Position-root.Position).Magnitude<=12,"FOCAL_PANEL_NOT_LOCAL")
 assert(panel:GetAttribute("FocalPanelReadable")==true,"FOCAL_BOTH_PAID_UNENCODABLE_STOP_BEFORE_NATIVE")
 return {signal=panel:GetAttribute("EncodedSignal_C02"),price0=panel:GetAttribute("Price0_C02"),price1=panel:GetAttribute("Price1_C02"),epoch=self.epoch}
end
function Law:recordVerifiedPassage(station,port,actionId,arrivalVerified)
 checkPort(station,port);assert(arrivalVerified==true and type(actionId)=="string"and #actionId>0,"FOCAL_ACTUAL_PASSAGE_ONLY")
 assert(self.actions[actionId]==nil,"FOCAL_ACTION_ALREADY_RECORDED_NO_REPLAY");self.actions[actionId]=true
 local v=self.ports[station][port];local used=v.available
 if used and self.cfg.Arm=="CONSUME_RECHARGE"then v.available=false;v.rechargeAt=self.epoch+3 end
 self.emit("FOCAL_PASSAGE",{actionId=actionId,station=station,port=port,epoch=self.epoch,freePassUsed=used,arm=self.cfg.Arm,rechargeAt=v.rechargeAt})
 self:_publish();return {freePassUsed=used,rechargeAt=v.rechargeAt}
end
function Law:capture()
 local rows={}
 for s=0,5 do for p=0,1 do local v=self.ports[s][p];table.insert(rows,{station=s,port=p,available=v.available,rechargeAt=v.rechargeAt})end end
 return{schema="DEE.Focal.LocalAvailability.R02",arm=self.cfg.Arm,epoch=self.epoch,ports=rows,actions=table.clone(self.actions)}
end
function Law:restore(saved)
 assert(saved.schema=="DEE.Focal.LocalAvailability.R02"and saved.arm==self.cfg.Arm and type(saved.epoch)=="number"and saved.epoch%1==0 and saved.epoch>=0 and saved.epoch<=6,"FOCAL_RESTORE_IDENTITY")
 assert(type(saved.ports)=="table"and #saved.ports==12 and type(saved.actions)=="table","FOCAL_RESTORE_COMPLETE")
 local ports={};for s=0,5 do ports[s]={}end
 for _,row in ipairs(saved.ports)do
  checkPort(row.station,row.port);assert(ports[row.station][row.port]==nil and type(row.available)=="boolean","FOCAL_RESTORE_PORT")
  if row.available then assert(row.rechargeAt==nil,"FOCAL_RESTORE_READY")else assert(type(row.rechargeAt)=="number"and row.rechargeAt>saved.epoch,"FOCAL_RESTORE_DEADLINE")end
  ports[row.station][row.port]={available=row.available,rechargeAt=row.rechargeAt}
 end
 for id,value in pairs(saved.actions)do assert(type(id)=="string"and value==true,"FOCAL_RESTORE_RECEIPT")end
 self.ports=ports;self.epoch=saved.epoch;self.actions=table.clone(saved.actions);self:_publish()
end
return M
