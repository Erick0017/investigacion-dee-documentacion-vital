"""Auditor-only checkpoint transportR02: Folder of bounded ASCII-hex StringValues.

Replaces R01 single StringValue, which exceeded Roblox's200000 byte limit on
DEV2. No world advancement, action, Native query or policy is implemented here.
Calling capture_world performs exactly one explicitly requested passive capture.
"""
import json,re
CHUNK_BYTES=16000
MAX_BYTES=16000000
PROTOCOL='DEE.RBX01.C02.CHECKPOINT_TRANSPORT.R02'
def need(x,message):
    if not x:raise ValueError(message)
def long_string(text):
    for n in range(20):
        eq='='*n
        if ']'+eq+']'not in text:return'(['+eq+'[!'+text+']'+eq+']):sub(2)'
    raise ValueError('Cannot delimit bounded transport JSON')
def slot_name(label):
    need(isinstance(label,str)and re.fullmatch('[A-Za-z0-9_]{1,100}',label),'Exact simple capture label required')
    return 'C02CheckpointTransportR02_'+label
def capture_code(context,label):
    slot=slot_name(label);raw=json.dumps(context,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    return '''
assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"RUNNING_STUDIO_REQUIRED")
local s=game:GetService("ServerStorage");assert(not s:FindFirstChild("SLOT"),"CAPTURE_ALREADY_ATTEMPTED_PRESERVED")
local capture=assert(s:FindFirstChild("RBX01Checkpoint_C02"),"C02_BOUNDARY_CAPTURE_REQUIRED")
local h=game:GetService("HttpService");local state=capture:Invoke(h:JSONDecode(CONTEXT))
local raw=h:JSONEncode(state);assert(#raw>0 and #raw<=16000000,"C02_CHECKPOINT_SIZE_BOUND")
local f=Instance.new("Folder");f.Name="SLOT";f:SetAttribute("Protocol","DEE.RBX01.C02.CHECKPOINT_TRANSPORT.R02")
f:SetAttribute("Complete",false);f:SetAttribute("TotalBytes",#raw);f.Parent=s
local count=0
for first=1,#raw,16000 do
 count+=1;local t={};for i=first,math.min(first+15999,#raw)do table.insert(t,string.format("%02x",string.byte(raw,i)))end
 local value=Instance.new("StringValue");value.Name=string.format("chunk_%05d",count);value.Value=table.concat(t)
 assert(#value.Value<=32000,"C02_CHUNK_BOUND");value.Parent=f
end
f:SetAttribute("Count",count);f:SetAttribute("CheckpointId",state.checkpoint_id);f:SetAttribute("NativeTick",state.native_tick)
f:SetAttribute("Complete",true)
return {protocol="DEE.RBX01.C02.CHECKPOINT_TRANSPORT.R02",bytes=#raw,count=count,chunkBytes=16000,
 checkpointId=state.checkpoint_id,nativeTick=state.native_tick,NativeQuerySubmitted=false,newActionExecuted=false}
'''.replace('SLOT',slot).replace('CONTEXT',long_string(raw))
def read_code(label,index):
    need(type(index)is int and 1<=index<=1000,'Exact bounded chunk index required')
    slot=slot_name(label)
    return '''
local f=assert(game:GetService("ServerStorage"):FindFirstChild("SLOT"),"C02_CHECKPOINT_FOLDER_REQUIRED")
assert(f:IsA("Folder")and f:GetAttribute("Protocol")=="DEE.RBX01.C02.CHECKPOINT_TRANSPORT.R02"and f:GetAttribute("Complete")==true,"C02_INCOMPLETE_TRANSPORT_PRESERVED")
local v=assert(f:FindFirstChild(string.format("chunk_%05d",INDEX)),"C02_EXACT_CHUNK_REQUIRED")
assert(v:IsA("StringValue")and #v.Value<=32000,"C02_STRINGVALUE_BOUND")
return {protocol="DEE.RBX01.C02.CHECKPOINT_TRANSPORT.R02",index=INDEX,hex=v.Value,
 bytes=f:GetAttribute("TotalBytes"),count=f:GetAttribute("Count"),checkpointId=f:GetAttribute("CheckpointId")}
'''.replace('SLOT',slot).replace('INDEX',str(index))
def capture_world(mcp,context,label,path,validator):
    need(not path.exists(),'Preserve existing world file')
    meta=mcp('execute_luau',{'datamodel_type':'Server','code':capture_code(context,label)},label+'_capture_once_R02',120)
    need(meta.get('protocol')==PROTOCOL and meta.get('checkpointId')==context['checkpoint_id']and
         meta.get('nativeTick')==context['native_tick'],'Checkpoint capture identity/protocol mismatch')
    total,count=meta.get('bytes'),meta.get('count')
    need(type(total)is int and 0<total<=MAX_BYTES and type(count)is int and count==(total+CHUNK_BYTES-1)//CHUNK_BYTES,'Bounded complete transport manifest required')
    chunks=[]
    for index in range(1,count+1):
        value=mcp('execute_luau',{'datamodel_type':'Server','code':read_code(label,index)},label+'_chunk_%05d_R02'%index,120)
        need(value.get('protocol')==PROTOCOL and value.get('checkpointId')==context['checkpoint_id']and
             value.get('index')==index and value.get('count')==count and value.get('bytes')==total,'Checkpoint chunk correlation mismatch')
        hextext=value.get('hex');need(isinstance(hextext,str)and len(hextext)<=CHUNK_BYTES*2,'Checkpoint chunk exceeds limit')
        chunk=bytes.fromhex(hextext)
        need(len(chunk)==min(CHUNK_BYTES,total-(index-1)*CHUNK_BYTES),'Checkpoint chunk length mismatch')
        chunks.append(chunk)
    raw=b''.join(chunks);need(len(raw)==total,'Incomplete checkpoint bytes')
    world=json.loads(raw.decode('utf8'));validator(world)
    with path.open('xb')as stream:stream.write(raw)
    return world,path,total
