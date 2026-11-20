-- Aparato geométrico únicamente. No elige rutas ni abre Native.
local M={}
local function v(a) assert(type(a)=="table"and #a==3,"SDK_VECTOR3");return Vector3.new(a[1],a[2],a[3])end
function M.build(cfg)
 local c=cfg.Map;assert(not workspace:FindFirstChild(c.RootName),"SDK_SCENE_EXISTS_PRESERVED")
 local world=Instance.new("Folder");world.Name=c.RootName;world:SetAttribute("DEE_SDK_Version",cfg.Version);world:SetAttribute("ScenarioFingerprint",cfg.ScenarioFingerprint);world.Parent=workspace
 local function part(name,pos,size,parent,collide)
  local p=Instance.new("Part");p.Name=name;p.Anchored=true;p.CanCollide=collide;p.CanQuery=true;p.Size=v(size);p.Position=v(pos);p.Parent=parent or world;return p
 end
 local points={[0]=v(c.Start),[1]=v(c.Port0),[2]=v(c.Port1)}
 local floor=part("Suelo",c.FloorCenter,c.FloorSize,world,true);floor.Color=Color3.fromRGB(45,55,70)
 local obstacles=Instance.new("Folder");obstacles.Name="Obstaculos";obstacles.Parent=world
 for i,o in ipairs(c.Obstacles)do local p=part("Obstaculo"..i,o.Position,o.Size,obstacles,true);p.Color=Color3.fromRGB(105,115,130)end
 local panels={}
 for code,p in pairs(points)do
  local panel=part("PanelLocal"..code,{p.X,p.Y+2,p.Z},{3,1,1},world,false);panel:SetAttribute("Signal",c.Panel.Signal);panel:SetAttribute("Price0",c.Panel.Price0);panel:SetAttribute("Price1",c.Panel.Price1);panel.Color=Color3.fromRGB(80,170,240);panels[code]=panel
  local mark=part("PuertoFijo"..code,{p.X,p.Y-2.8,p.Z},{7,.2,7},world,false);mark.Color=Color3.fromRGB(80,205,190)
 end
 local device=part("Dispositivo",c.Device,{5,6,1},world,false);device:SetAttribute("ActuatorValue",-1);device.Color=Color3.fromRGB(150,160,175)
 local actor=Instance.new("Model");actor.Name="DEE_Demo";actor.Parent=world
 local root=part("CoreInicial",c.Start,{2,2,1},actor,false);actor.PrimaryPart=root;actor:SetAttribute("DEE_AgentId",cfg.AgentId);game:GetService("CollectionService"):AddTag(actor,"DEE_Agent")
 return{world=world,actor=actor,points=points,panels=panels,device=device}
end
return M
