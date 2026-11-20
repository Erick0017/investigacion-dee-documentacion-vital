-- Persistencia de propiedades capturadas. Sin sensores, decisiones ni avanceNative.
local H=game:GetService("HttpService")
local M={}
function M.copy(v)return H:JSONDecode(H:JSONEncode(v))end
function M.frame(f)return{f:GetComponents()}end
function M.vec(v)return{v.X,v.Y,v.Z}end
function M.part(p)
 return{name=p.Name,className=p.ClassName,cframe=M.frame(p.CFrame),size=M.vec(p.Size),anchored=p.Anchored,
  canCollide=p.CanCollide,canQuery=p.CanQuery,canTouch=p.CanTouch,massless=p.Massless,
  transparency=p.Transparency,color={p.Color.R,p.Color.G,p.Color.B},material=p.Material.Name,
  collisionGroup=p.CollisionGroup,linearVelocity=M.vec(p.AssemblyLinearVelocity),angularVelocity=M.vec(p.AssemblyAngularVelocity),attributes=p:GetAttributes()}
end
function M.applyPart(p,s)
 assert(p.Name==s.name and p.ClassName==s.className,"R06_PART_BINDING")
 p.Anchored=true;p.Size=Vector3.new(table.unpack(s.size));p.CFrame=CFrame.new(table.unpack(s.cframe))
 p.CanCollide=s.canCollide;p.CanQuery=s.canQuery;p.CanTouch=s.canTouch;p.Massless=s.massless
 p.Transparency=s.transparency;p.Color=Color3.new(table.unpack(s.color));p.Material=assert(Enum.Material[s.material],"R06_PART_MATERIAL")
 p.CollisionGroup=s.collisionGroup
 for k in pairs(p:GetAttributes())do if s.attributes[k]==nil then p:SetAttribute(k,nil)end end
 for k,v in pairs(s.attributes)do p:SetAttribute(k,v)end
 p.AssemblyLinearVelocity=Vector3.new(table.unpack(s.linearVelocity));p.AssemblyAngularVelocity=Vector3.new(table.unpack(s.angularVelocity))
 p.Anchored=s.anchored
end
function M.body(actor,root)
 assert(root.Anchored,"R06_CAPTURE_BODY_ANCHORED")
 local parts,joints={},{}
 for _,p in ipairs(actor:GetDescendants())do
  if p:IsA("BasePart")then table.insert(parts,M.part(p))
  elseif p:IsA("JointInstance")then table.insert(joints,{name=p.Name,className=p.ClassName,parent=p.Parent.Name,part0=p.Part0 and p.Part0.Name,part1=p.Part1 and p.Part1.Name,c0=M.frame(p.C0),c1=M.frame(p.C1),transform=p:IsA("Motor6D")and M.frame(p.Transform)or nil})end
 end
 table.sort(parts,function(a,b)return a.name<b.name end);table.sort(joints,function(a,b)return(a.parent.."/"..a.name)<(b.parent.."/"..b.name)end)
 return{schema="DEE.SDK.Body.R06",pose=M.frame(actor:GetPivot()),rootName=root.Name,rootAnchored=root.Anchored,parts=parts,joints=joints}
end
function M.restoreBody(actor,root,s)
 assert(s.schema=="DEE.SDK.Body.R06"and s.rootName==root.Name and s.rootAnchored==true,"R06_BODY_BINDING")
 local found={};for _,p in ipairs(actor:GetDescendants())do if p:IsA("BasePart")then assert(not found[p.Name],"R06_BODY_PART_NAME_DUPLICATE");found[p.Name]=p;p.Anchored=true end end
 local n=0;for _ in pairs(found)do n+=1 end;assert(n==#s.parts,"R06_BODY_PART_SET")
 actor:PivotTo(CFrame.new(table.unpack(s.pose))) -- explicit paired restore only
 for _,j in ipairs(s.joints)do
  local parent=actor:FindFirstChild(j.parent,true);local live=parent and parent:FindFirstChild(j.name)
  assert(live and live:IsA("JointInstance")and live.ClassName==j.className and live.Part0 and live.Part1 and live.Part0.Name==j.part0 and live.Part1.Name==j.part1,"R06_JOINT_BINDING")
  live.C0=CFrame.new(table.unpack(j.c0));live.C1=CFrame.new(table.unpack(j.c1));if j.transform then assert(live:IsA("Motor6D"),"R06_JOINT_TRANSFORM");live.Transform=CFrame.new(table.unpack(j.transform))end
 end
 for _,p in ipairs(s.parts)do M.applyPart(assert(found[p.name],"R06_BODY_PART_MISSING"),p)end
 assert(root.Anchored,"R06_RESTORE_ROOT_MUST_STAY_ANCHORED")
end
return M
