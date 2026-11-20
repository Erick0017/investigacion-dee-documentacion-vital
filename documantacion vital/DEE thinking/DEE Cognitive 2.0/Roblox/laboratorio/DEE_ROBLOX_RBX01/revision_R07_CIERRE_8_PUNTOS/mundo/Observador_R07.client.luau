-- Passive Studio viewer only. No participant input, request or action is sent.
local Players=game:GetService("Players")
local RunService=game:GetService("RunService")
local ReplicatedStorage=game:GetService("ReplicatedStorage")
local H=game:GetService("HttpService")
local player=Players.LocalPlayer
local gui=Instance.new("ScreenGui");gui.Name="R07Observador";gui.ResetOnSpawn=false
gui.Parent=player:WaitForChild("PlayerGui")
local panel=Instance.new("TextLabel");panel.Name="Datos";panel.BackgroundColor3=Color3.fromRGB(15,22,32)
panel.BackgroundTransparency=.12;panel.BorderSizePixel=0;panel.Position=UDim2.fromOffset(12,12)
panel.Size=UDim2.new(0,420,0,135);panel.TextColor3=Color3.fromRGB(235,245,250)
panel.TextXAlignment=Enum.TextXAlignment.Left;panel.TextYAlignment=Enum.TextYAlignment.Top
panel.Font=Enum.Font.GothamMedium;panel.TextSize=18;panel.TextWrapped=true;panel.Parent=gui
local padding=Instance.new("UIPadding");padding.PaddingLeft=UDim.new(0,12);padding.PaddingTop=UDim.new(0,8);padding.Parent=panel
local labels={LIVE_NATIVE="DEE",PROGRAMMED="PROGRAMADO",CONVENTIONAL_AI="IA CONVENCIONAL"}
local actions={ASK_STATION="Consultar",SKIP_STATION="Omitir consulta",SAFE_WAIT="Esperar",EXIT_0="Puerto 0",EXIT_1="Puerto 1"}
local camera=workspace.CurrentCamera
RunService.RenderStepped:Connect(function(dt)
    local status=ReplicatedStorage:FindFirstChild("RBX01Status")
    if status then
        local ok,s=pcall(H.JSONDecode,H,status.Value)
        if ok then
            local a=s.numberAPresent and tostring(s.numberA)or"ausente"
            local b=s.codeBPresent and tostring(s.finalCode)or"ausente"
            panel.Text=(labels[s.participant]or"PREPARACIÓN").." · Destinos propios\n"..
                "Acción: "..(actions[s.action]or"Preparación").."   Permisos: "..tostring(s.permissionStock or"—").."\n"..
                "Producto A: "..a.."   Código B: "..b.."\n"..
                "Recursos acumulados: "..tostring(s.resourceCount or0).."   Entregas: "..tostring(s.delivered or0).."\n"..
                "Los contadores incluyen la historia conservada."
        end
    end
    local world=workspace:FindFirstChild("RBX01");local body=world and world:FindFirstChild("DEE_Body")
    local root=body and body.PrimaryPart
    if root and camera then
        camera.CameraType=Enum.CameraType.Scriptable
        local focus=root.Position+Vector3.new(0,1,0)
        camera.CFrame=camera.CFrame:Lerp(CFrame.lookAt(focus+Vector3.new(22,25,34),focus),math.clamp(dt*5,0,1))
    end
end)
