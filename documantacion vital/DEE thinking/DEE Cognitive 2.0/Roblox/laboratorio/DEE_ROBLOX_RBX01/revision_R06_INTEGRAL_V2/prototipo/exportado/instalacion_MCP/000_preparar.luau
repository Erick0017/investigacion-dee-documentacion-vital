assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"STUDIO_PLAY_ONLY")
local ss=game:GetService("ServerStorage");assert(not ss:FindFirstChild("DEE_Install_R06_V1"),"INSTALL_ALREADY_PRESENT_PRESERVED")
assert(not game:GetService("ServerScriptService"):FindFirstChild("DEEConnector_R06"),"PACKAGE_ALREADY_PRESENT_PRESERVED")
local f=Instance.new("Folder");f.Name="DEE_Install_R06_V1";f:SetAttribute("Protocol","DEE.SourceInstall.R01");f.Parent=ss
local c=Instance.new("Folder");c.Name="Main";c.Parent=f
local c=Instance.new("Folder");c.Name="BackendBinding";c.Parent=f
local c=Instance.new("Folder");c.Name="MinimalAdapters";c.Parent=f
local c=Instance.new("Folder");c.Name="ExampleConfig";c.Parent=f
return{prepared=true,NativeTicks=0,packageNotYetInstalled=true}
