-- Presentación solamente: nunca calcula respuestas ni manda solicitudes.
local H=game:GetService("HttpService")
local M={}
local NL=string.char(10)
function M.create(cfg)
 local view={}
 function view:state(text)end;function view:operation(row)end;function view:capabilities(h)end
 if not cfg.View.Enabled then return view end
 local name="DEE_SDK_EXT_R06_PANEL";assert(not workspace:FindFirstChild(name),"EXT_VIEW_EXISTS_PRESERVE")
 local p=Instance.new("Part");p.Name=name;p.Anchored=true;p.CanCollide=false;p.CanQuery=false;p.CanTouch=false
 p.Size=Vector3.new(table.unpack(cfg.View.Size));p.Position=Vector3.new(table.unpack(cfg.View.Position));p.Color=Color3.fromRGB(13,22,38);p.Parent=workspace
 local gui=Instance.new("SurfaceGui");gui.Name="VistaCapacidadesES";gui.Face=Enum.NormalId.Front;gui.CanvasSize=Vector2.new(table.unpack(cfg.View.CanvasSize));gui.Parent=p
 local frame=Instance.new("Frame");frame.Size=UDim2.fromScale(1,1);frame.BackgroundColor3=Color3.fromRGB(13,22,38);frame.BorderSizePixel=0;frame.Parent=gui
 local function label(name,y,height,size,color)
  local t=Instance.new("TextLabel");t.Name=name;t.Position=UDim2.new(0,24,0,y);t.Size=UDim2.new(1,-48,0,height)
  t.BackgroundTransparency=1;t.Font=Enum.Font.Code;t.TextSize=size;t.TextColor3=color or Color3.fromRGB(225,234,245)
  t.TextXAlignment=Enum.TextXAlignment.Left;t.TextYAlignment=Enum.TextYAlignment.Top;t.TextWrapped=true;t.RichText=false;t.Parent=frame;return t
 end
 label("Titulo",20,40,29).Text="Capacidades Native · invocación asistida"
 label("Modo",66,44,18,Color3.fromRGB(245,197,85)).Text="El desarrollador inicia el experimento; DEE produce el resultado. Sin respuestas del host."
 local status=label("Estado",120,52,19);local request=label("Entrada",180,120,16)
 local identity=label("Identidad",306,80,16,Color3.fromRGB(150,207,239));local result=label("Resultado",392,258,15)
 label("Limite",662,42,15,Color3.fromRGB(245,197,85)).Text="Tras avance Native: la pareja SDK anterior queda PRE_CAP, no representa un World actual."
 function view:state(text)status.Text="Estado: "..tostring(text)end
 function view:capabilities(h)
  status.Text="Estado del servicio: "..tostring(h.status)
  identity.Text="Instancia: "..tostring(h.instanceId)..NL.."Vida: "..tostring(h.lifeId).." · tick del último handshake: "..tostring(h.nativeTick)
  request.Text="Capacidades anunciadas: "..table.concat(h.capabilities,", ")..NL.."Sólo entradas explícitas suministradas por el desarrollador."
 end
 function view:operation(row)
  status.Text="Estado: "..tostring(row.status).." · ID: "..tostring(row.operationId)
  request.Text="Entrada suministrada (ASSISTED):"..NL..H:JSONEncode(row.body and row.body.request or{kind="CIERRE_EXPLICITO"})
  local raw=row.responseRaw or"Sin respuesta Native todavía. PENDING no es resultado."
  if #raw>cfg.View.MaxDisplayCharacters then local last=cfg.View.MaxDisplayCharacters;while last<#raw do local b=string.byte(raw,last+1);if b>=128 and b<=191 then last-=1 else break end end;raw=string.sub(raw,1,last)..NL.."[VISTA RECORTADA; la respuesta original está en Operations y en el primario privado.]"end
  result.Text="Respuesta literal del servicio (incluye valor Native / NULL):"..NL..raw
 end
 view:state("Extensión instalada; deshabilitada por defecto. No Native.");return view
end
return M
