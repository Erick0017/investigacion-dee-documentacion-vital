-- Anatomía fija de seis zonas R07. No selecciona puertos ni resuelve objetivos.
local H=game:GetService("HttpService")
local M={}
local function v(a)return Vector3.new(a[1],a[2],a[3])end
function M.build(cfg)
 local c=cfg.Map;assert(not workspace:FindFirstChild(c.RootName),"FOCAL_WORLD_EXISTS_PRESERVED")
 local w=Instance.new("Folder");w.Name=c.RootName;w:SetAttribute("FocalConfig",H:JSONEncode(cfg.Focal));w:SetAttribute("ScenarioFingerprint",cfg.ScenarioFingerprint);w.Parent=workspace
 local function part(parent,name,pos,size,collide)
  local p=Instance.new("Part");p.Name=name;p.Anchored=true;p.CanCollide=collide;p.CanQuery=true;p.Size=v(size);p.Position=pos;p.Parent=parent;return p
 end
 local floor=part(w,"Suelo",Vector3.new(0,4.5,10),{220,1,220},true);floor.Color=Color3.fromRGB(45,55,70)
 for i,o in ipairs(c.Obstacles)do local p=part(w,"Obstaculo"..i,v(o.Position),o.Size,true);p.Color=Color3.fromRGB(100,115,130)end
 local markers=Instance.new("Folder");markers.Name="Markers";markers.Parent=w
 local gatesFolder=Instance.new("Folder");gatesFolder.Name="Gates";gatesFolder.Parent=w
 local points,panels={},{}
 for s=0,5 do
  local p=v(c.Positions[tostring(s)]);points[s]=p
  local marker=part(markers,"Contacto"..s,p,{9,8,9},false);marker.Transparency=.9;marker:SetAttribute("ContactCode",s)
  local panel=part(w,"Panel_"..s,p+Vector3.new(0,2,0),{3,1,1},false);panel.Color=Color3.fromRGB(90,180,240);panels[s]=panel
  for port=0,1 do
   local gate=part(gatesFolder,"Gate_"..s.."_"..port,p+Vector3.new(port==0 and -3 or 3,0,0),{2,3,1},false)
   gate:SetAttribute("Station",s);gate:SetAttribute("Port",port);gate:SetAttribute("FocalCapacity",1);gate.Color=Color3.fromRGB(80,210,170)
  end
 end
 local actor=Instance.new("Model");actor.Name="DEE_Focal";actor.Parent=w
 local root=part(actor,"CoreInicial",points[cfg.Focal.startStation],{2,2,1},false);actor.PrimaryPart=root
 actor:SetAttribute("DEE_AgentId",cfg.AgentId);game:GetService("CollectionService"):AddTag(actor,"DEE_Agent")
 local device=part(w,"UltimoPuertoObservado",Vector3.new(0,10,10),{2,2,2},false);device:SetAttribute("ActuatorValue",-1)
 return{world=w,actor=actor,points=points,panels=panels,device=device}
end
return M
