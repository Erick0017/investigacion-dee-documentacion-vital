assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"RUNNING_STUDIO_REQUIRED")
local s=game:GetService("ServerStorage");assert(not s:FindFirstChild("C02CheckpointTransportR02_AI02_ROOT_B05"),"CAPTURE_ALREADY_ATTEMPTED_PRESERVED")
local h=game:GetService("HttpService");local state=s.RBX01Checkpoint_C02:Invoke(h:JSONDecode("{\"checkpoint_id\":\"C02CMP_AI02_ROOT_B05_20261115T1821\",\"native_life_id\":\"COMPARATOR_CONVENTIONAL_AI_C02_CONVENTIONAL_AI_R06_02\",\"native_tick\":0,\"bridge\":{\"session_id\":\"dff2980509d448be9315e75b98fad02f\",\"server_id\":\"studio_5e97dc96-2743-4d27-9010-2675e3efd57a\",\"phase\":\"READY_QUERY\",\"pending_count\":0,\"uncertain_count\":0,\"native_ticks_in_session\":0}}"))
local raw=h:JSONEncode(state);assert(#raw>0 and #raw<=16000000,"C02_CHECKPOINT_SIZE_BOUND")
local f=Instance.new("Folder");f.Name="C02CheckpointTransportR02_AI02_ROOT_B05";f:SetAttribute("Protocol","DEE.RBX01.C02.CHECKPOINT_TRANSPORT.R02");f:SetAttribute("Complete",false);f:SetAttribute("TotalBytes",#raw);f.Parent=s
local count=0
for first=1,#raw,16000 do count+=1;local t={};for i=first,math.min(first+15999,#raw)do table.insert(t,string.format("%02x",string.byte(raw,i)))end;local value=Instance.new("StringValue");value.Name=string.format("chunk_%05d",count);value.Value=table.concat(t);assert(#value.Value<=32000,"C02_CHUNK_BOUND");value.Parent=f end
f:SetAttribute("Count",count);f:SetAttribute("CheckpointId",state.checkpoint_id);f:SetAttribute("NativeTick",state.native_tick);f:SetAttribute("Complete",true)
return {protocol="DEE.RBX01.C02.CHECKPOINT_TRANSPORT.R02",bytes=#raw,count=count,checkpointId=state.checkpoint_id,nativeTick=state.native_tick,NativeQuerySubmitted=false,newActionExecuted=false}
